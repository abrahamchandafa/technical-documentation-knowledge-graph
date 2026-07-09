"""Central entry point for the documentation knowledge graph pipeline.

Orchestrates extraction, validation, and loading steps.
Run with: uv run python main.py
"""

import logging

from src.extract import extract_from_file
from src.validate import validate_triples

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DOCUMENT = "data/raw/fastapi_intro.txt"


def main() -> None:
    """Run the full pipeline: extract → validate."""
    raw = extract_from_file(DOCUMENT)
    logger.info("Extracted %d raw triples", len(raw))

    valid = validate_triples(raw)
    rejected = len(raw) - len(valid)
    logger.info("Accepted: %d | Rejected: %d", len(valid), rejected)

    logger.info("--- Accepted Triples ---")
    for t in valid:
        logger.info(
            "(%s) %s --[%s]--> (%s) %s",
            t.subject_type, t.subject, t.predicate, t.object_type, t.object,
        )


if __name__ == "__main__":
    main()
