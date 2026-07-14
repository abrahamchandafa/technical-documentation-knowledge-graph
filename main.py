"""Central entry point for the documentation knowledge graph pipeline.

Orchestrates the full pipeline:
  1. Extract triples from raw docs via LLM (OpenRouter)
  2. Validate triples against ontology whitelist
  3. Save raw + validated triples to data/processed/
  4. Load validated triples into Neo4j
  5. (optional) Load into GraphDB with --load-graphdb

Run with: uv run python main.py
         uv run python main.py --no-fetch        (skip extraction, load cached triples)
         uv run python main.py --load-graphdb    (also load into GraphDB)
"""

import argparse
import json
import logging
from pathlib import Path

from src.extract import extract_from_file
from src.load_graphdb import load_triples_to_graphdb
from src.load_neo4j import load_triples
from src.settings import settings
from src.validate import validate_triples

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    """Run the full pipeline: extract → validate → load."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--load-graphdb", action="store_true")
    args = parser.parse_args()

    doc_path = Path(settings.data_raw_dir) / "fastapi_intro.txt"
    processed_dir = Path(settings.data_processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    stem = doc_path.stem
    valid_path = processed_dir / f"{stem}_valid.json"

    if args.no_fetch:
        data = json.loads(valid_path.read_text(encoding="utf-8"))
        from src.ontology import Triple

        valid = [Triple.model_validate(item) for item in data]
        logger.info("Loaded %d cached triples from %s", len(valid), valid_path)
        rejected = 0
    else:
        raw = extract_from_file(str(doc_path))
        logger.info("Extracted %d raw triples", len(raw))

        valid = validate_triples(raw)
        rejected = len(raw) - len(valid)
        logger.info("Accepted: %d | Rejected: %d", len(valid), rejected)

        raw_path = processed_dir / f"{stem}_raw.json"
        raw_path.write_text(
            json.dumps([t.model_dump() for t in raw], indent=2),
            encoding="utf-8",
        )
        logger.info("Saved raw triples to %s", raw_path)
        valid_path.write_text(
            json.dumps([t.model_dump() for t in valid], indent=2),
            encoding="utf-8",
        )
        logger.info("Saved valid triples to %s", valid_path)

    load_triples(valid)
    logger.info("Loaded %d triples into Neo4j", len(valid))

    if args.load_graphdb:
        load_triples_to_graphdb(valid)


if __name__ == "__main__":
    main()
