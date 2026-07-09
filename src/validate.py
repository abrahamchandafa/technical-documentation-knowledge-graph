"""Ontology validation for extracted triples.

Checks each triple against the VALID_RELATIONSHIPS whitelist
and rejects any that violate the schema rules.
"""

import logging

from .ontology import VALID_RELATIONSHIPS, Triple

logger = logging.getLogger(__name__)


def validate_triples(triples: list[Triple]) -> list[Triple]:
    """Filter triples against the ontology whitelist.

    Only triples whose (subject_type, predicate, object_type) combination
    appears in VALID_RELATIONSHIPS are kept. All others are logged and
    rejected.

    Args:
        triples: Raw triples from the extraction step.

    Returns:
        A list of triples that passed validation.
    """
    valid: list[Triple] = []

    for triple in triples:
        allowed_pairs = VALID_RELATIONSHIPS.get(triple.predicate)
        if allowed_pairs is None:
            logger.warning(
                "Unknown relationship %s — rejecting: (%s) %s --[%s]--> (%s) %s",
                triple.predicate,
                triple.subject_type,
                triple.subject,
                triple.predicate,
                triple.object_type,
                triple.object,
            )
            continue

        pair = (triple.subject_type, triple.object_type)
        if pair not in allowed_pairs:
            logger.warning(
                "Invalid combo (%s, %s) for %s — rejecting: (%s) %s --[%s]--> (%s) %s",
                triple.subject_type,
                triple.object_type,
                triple.predicate,
                triple.subject_type,
                triple.subject,
                triple.predicate,
                triple.object_type,
                triple.object,
            )
            continue

        valid.append(triple)

    return valid



