"""Load validated triples into Neo4j as a property graph."""

import json
import logging
from pathlib import Path

from neo4j import GraphDatabase
from tqdm import tqdm

from .ontology import Triple
from .settings import settings

logger = logging.getLogger(__name__)


def load_triples(triples: list[Triple]) -> None:
    """Insert validated triples into Neo4j.

    For each triple, creates or merges two Entity nodes and a
    relationship between them. The relationship type is the predicate,
    and each node stores its name and entity type as properties.

    Args:
        triples: Validated triples to load.

    Raises:
        ConnectionError: If the Neo4j connection fails.
    """
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )

    try:
        driver.verify_connectivity()
        logger.info("Connected to Neo4j at %s", settings.neo4j_uri)
    except Exception as e:
        raise ConnectionError(f"Neo4j connection failed: {e}") from e

    with driver.session() as session:
        for triple in tqdm(triples, desc="Loading into Neo4j", unit="triple"):
            session.run(
                (
                    "MERGE (s:Entity {name: $subject, type: $subject_type}) "
                    "MERGE (o:Entity {name: $object, type: $object_type}) "
                    f"MERGE (s)-[:{triple.predicate}]->(o)"
                ),
                subject=triple.subject,
                subject_type=triple.subject_type,
                object=triple.object,
                object_type=triple.object_type,
            )

    driver.close()
    logger.info("Loaded %d triples into Neo4j", len(triples))


def load_from_file(file_path: str | Path) -> None:
    """Read validated triples from a JSON file and load into Neo4j.

    Args:
        file_path: Path to the JSON file with validated triples.
    """
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    triples = [Triple.model_validate(item) for item in data]
    load_triples(triples)
