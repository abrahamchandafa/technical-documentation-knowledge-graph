"""Central entry point for the documentation knowledge graph pipeline.

Orchestrates extraction, validation, and loading steps.
Run with: uv run python main.py
"""

import json
import logging
from pathlib import Path

from src.extract import extract_from_file
from src.load_neo4j import load_triples
from src.settings import settings
from src.validate import validate_triples

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    """Run the full pipeline: extract → validate → save."""
    doc_path = Path(settings.data_raw_dir) / "fastapi_intro.txt"
    processed_dir = Path(settings.data_processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    raw = extract_from_file(str(doc_path))
    logger.info("Extracted %d raw triples", len(raw))

    valid = validate_triples(raw)
    rejected = len(raw) - len(valid)
    logger.info("Accepted: %d | Rejected: %d", len(valid), rejected)

    stem = doc_path.stem
    raw_path = processed_dir / f"{stem}_raw.json"
    valid_path = processed_dir / f"{stem}_valid.json"

    raw_path.write_text(
        json.dumps([t.model_dump() for t in raw], indent=2),
        encoding="utf-8",
    )
    valid_path.write_text(
        json.dumps([t.model_dump() for t in valid], indent=2),
        encoding="utf-8",
    )
    logger.info("Saved raw triples to %s", raw_path)
    logger.info("Saved valid triples to %s", valid_path)

    logger.info("--- Accepted Triples ---")
    for t in valid:
        logger.info(
            "(%s) %s --[%s]--> (%s) %s",
            t.subject_type,
            t.subject,
            t.predicate,
            t.object_type,
            t.object,
        )

    load_triples(valid)


if __name__ == "__main__":
    main()
