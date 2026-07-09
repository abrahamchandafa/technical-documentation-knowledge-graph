"""Ontology definitions for the developer documentation knowledge graph.

Defines the entity types, relationship types, and validation rules
that govern what can be extracted and stored in the graph.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel


class EntityType(str, Enum):
    """Allowed entity types for nodes in the knowledge graph."""

    FUNCTION = "Function"
    CLASS = "Class"
    MODULE = "Module"
    PARAMETER = "Parameter"
    DATA_TYPE = "DataType"
    RESPONSE_TYPE = "ResponseType"
    URL = "URL"
    API = "API"
    LIBRARY = "Library"


class RelationshipType(str, Enum):
    """Allowed relationship types for edges in the knowledge graph."""

    CALLS = "CALLS"
    BELONGS_TO = "BELONGS_TO"
    TAKES = "TAKES"
    RETURNS = "RETURNS"
    HAS_PARAMETER = "HAS_PARAMETER"
    DEPENDS_ON = "DEPENDS_ON"
    EXTENDS = "EXTENDS"


class Triple(BaseModel):
    """A single extracted fact from a document.

    Attributes:
        subject: Name of the source entity.
        predicate: Relationship connecting subject to object.
        object: Name of the target entity.
        subject_type: Entity type of the subject.
        object_type: Entity type of the object.
        source_document: File path or identifier of the source document.
        confidence: LLM confidence score for this extraction (0-1).
    """

    subject: str
    predicate: RelationshipType
    object: str
    subject_type: EntityType
    object_type: EntityType
    source_document: Optional[str] = None
    confidence: Optional[float] = None


# Whitelist of valid (subject_type, predicate, object_type) combinations.
# Only triples matching these rules pass validation. Everything else is
# rejected to prevent LLM hallucinations from polluting the graph.
VALID_RELATIONSHIPS: dict[RelationshipType, list[tuple[EntityType, EntityType]]] = {
    RelationshipType.CALLS: [
        (EntityType.FUNCTION, EntityType.FUNCTION),
    ],
    RelationshipType.BELONGS_TO: [
        (EntityType.FUNCTION, EntityType.MODULE),
        (EntityType.FUNCTION, EntityType.CLASS),
        (EntityType.CLASS, EntityType.MODULE),
    ],
    RelationshipType.TAKES: [
        (EntityType.FUNCTION, EntityType.DATA_TYPE),
        (EntityType.API, EntityType.DATA_TYPE),
    ],
    RelationshipType.RETURNS: [
        (EntityType.FUNCTION, EntityType.RESPONSE_TYPE),
        (EntityType.API, EntityType.RESPONSE_TYPE),
    ],
    RelationshipType.HAS_PARAMETER: [
        (EntityType.URL, EntityType.PARAMETER),
        (EntityType.FUNCTION, EntityType.PARAMETER),
    ],
    RelationshipType.DEPENDS_ON: [
        (EntityType.LIBRARY, EntityType.LIBRARY),
        (EntityType.MODULE, EntityType.MODULE),
        (EntityType.FUNCTION, EntityType.LIBRARY),
    ],
    RelationshipType.EXTENDS: [
        (EntityType.CLASS, EntityType.CLASS),
    ],
}
