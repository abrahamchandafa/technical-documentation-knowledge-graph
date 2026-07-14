"""Convert validated triples to RDF and load into GraphDB.

In RDF, every fact is a triple: subject → predicate → object.
Each part is a URI (not a string like in Neo4j).

Example:
    Neo4j:  (:Entity {name: "FastAPI", type: "Library"})
            -[:DEPENDS_ON]->
            (:Entity {name: "Starlette", type: "Library"})

    RDF:    ex:FastAPI   rdf:type       ex:Library .
            ex:Starlette rdf:type       ex:Library .
            ex:FastAPI   ex:depends_on  ex:Starlette .
"""

import logging
import re

import httpx
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
from tqdm import tqdm

from .ontology import Triple
from .settings import settings

logger = logging.getLogger(__name__)

# Namespace for our developer documentation entities
# Everything gets a URI like http://example.org/devdoc/FastAPI
EX = Namespace("http://example.org/devdoc/")


def _safe_uri_fragment(name: str) -> str:
    """Sanitize an entity name into a valid URI fragment.

    Strips leading slashes and replaces characters that are not
    valid in URI path segments.

    Args:
        name: Raw entity name like "/items/{item_id}".

    Returns:
        URI-safe fragment like "items_item_id".
    """
    cleaned = name.lstrip("/")
    cleaned = cleaned.replace("{", "_").replace("}", "")
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", cleaned)
    return cleaned


def triples_to_rdf(triples: list[Triple]) -> Graph:
    """Convert a list of validated Triple objects into an RDF graph.

    Each entity becomes a URI (e.g. ex:FastAPI) and each entity type
    becomes an RDF class (e.g. ex:Library). Relationships become
    predicates (e.g. ex:depends_on).

    Args:
        triples: Validated triples from the extraction pipeline.

    Returns:
        An rdflib Graph containing the RDF triples.
    """
    g = Graph()

    # Bind prefixes so the Turtle output is readable
    g.bind("ex", EX)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)

    for t in tqdm(triples, desc="Converting to RDF", unit="triple"):
        subj_uri = EX[_safe_uri_fragment(t.subject)]
        obj_uri = EX[_safe_uri_fragment(t.object)]

        # Type triples: subj rdf:type ex:EntityType
        # e.g. ex:FastAPI rdf:type ex:Library
        g.add((subj_uri, RDF.type, EX[t.subject_type]))
        g.add((obj_uri, RDF.type, EX[t.object_type]))

        # Relationship triple: subj ex:predicate obj
        # e.g. ex:FastAPI ex:depends_on ex:Starlette
        g.add((subj_uri, EX[t.predicate.lower()], obj_uri))

    return g


def load_rdf_to_graphdb(rdf_graph: Graph) -> None:
    """Upload an RDF graph to GraphDB via its REST API.

    Uses the SPARQL UPDATE endpoint to insert all triples in a
    single request. GraphDB must be running and the repository
    must already exist.

    Args:
        rdf_graph: The RDF graph to upload.

    Raises:
        ConnectionError: If the upload fails.
    """
    url = f"{settings.graphdb_url}/repositories/{settings.graphdb_repo}/statements"

    headers = {"Content-Type": "application/x-turtle"}
    turtle_data = rdf_graph.serialize(format="turtle")

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, content=turtle_data, headers=headers)

    if response.status_code != 204:
        raise ConnectionError(
            f"GraphDB returned {response.status_code}: {response.text}"
        )

    logger.info("Uploaded RDF to GraphDB repository '%s'", settings.graphdb_repo)


def load_triples_to_graphdb(triples: list[Triple]) -> None:
    """Convert and load validated triples into GraphDB.

    Convenience function that chains triples_to_rdf() and
    load_rdf_to_graphdb().

    Args:
        triples: Validated triples to load.
    """
    rdf_graph = triples_to_rdf(triples)
    triple_count = len(rdf_graph)
    logger.info("Generated %d RDF triples from %d source triples", triple_count, len(triples))
    load_rdf_to_graphdb(rdf_graph)
