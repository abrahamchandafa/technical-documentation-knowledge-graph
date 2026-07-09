"""LLM-based entity and relationship extraction from documentation.

Calls OpenRouter to extract structured triples from raw text,
then parses the response into validated Triple objects.
"""

import json
import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from tqdm import tqdm

from .ontology import EntityType, RelationshipType, Triple

load_dotenv()

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = "\n".join(
    [
        "You are an expert at extracting structured information from developer documentation.",
        "",
        "Entity types you can use:",
        "- Function — a named function or method",
        "- Class — a class definition",
        "- Module — a file or module containing code",
        "- Parameter — a function or URL parameter",
        "- DataType — a data type (int, str, list, etc.)",
        "- ResponseType — the type of a response or return value",
        "- URL — a URL endpoint or route pattern",
        "- API — a named API or web service",
        "- Library — a library, package, or framework dependency",
        "",
        "Relationship types you can use:",
        "- CALLS — one function calls another",
        "- BELONGS_TO — an entity belongs to a module, class, or library",
        "- TAKES — a function or API accepts a data type",
        "- RETURNS — a function or API returns a response type",
        "- HAS_PARAMETER — a URL or function has a parameter",
        "- DEPENDS_ON — a library/module depends on another",
        "- EXTENDS — a class extends another class",
        "",
        "Rules:",
        "1. Only extract facts explicitly stated or strongly implied in the text.",
        "2. Use exact entity names as they appear in the documentation.",
        "3. Each triple must have a subject, predicate, object, subject_type, and object_type.",
        '4. Return a JSON object with a single key "triples" containing an array of triples.',
        "5. Do not include any text outside the JSON object.",
    ]
)


def extract_triples(
    text: str,
    source_document: str | None = None,
) -> list[Triple]:
    """Extract triples from document text via OpenRouter.

    Args:
        text: Raw document text to extract from.
        source_document: Optional file path or identifier for provenance.

    Returns:
        A list of validated Triple objects.

    Raises:
        ConnectionError: If the API call fails.
        ValueError: If the response cannot be parsed.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not set. Add it to your .env file or environment variables."
        )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Extract all triples from this documentation:\n\n{text}",
            },
        ],
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info("Sending %d characters to %s", len(text), OPENROUTER_MODEL)
    with httpx.Client(timeout=120.0) as client:
        with tqdm(total=1, desc="Calling OpenRouter", unit="req") as pbar:
            response = client.post(
                f"{OPENROUTER_BASE}/chat/completions",
                json=payload,
                headers=headers,
            )
            pbar.update(1)

    if response.status_code != 200:
        raise ConnectionError(
            f"OpenRouter API returned {response.status_code}: {response.text}"
        )

    body = response.json()
    content = body["choices"][0]["message"]["content"]
    logger.info("Received response with %d characters", len(content))
    return _parse_response(content, source_document)


def _parse_response(
    content: str,
    source_document: str | None = None,
) -> list[Triple]:
    """Parse the LLM JSON response into Triple objects.

    Args:
        content: The raw JSON string from the LLM.
        source_document: Optional source identifier to attach to each triple.

    Returns:
        A list of validated Triple objects.

    Raises:
        ValueError: If JSON parsing fails or required fields are missing.
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e

    raw_triples = data.get("triples", [])
    triples: list[Triple] = []

    for item in tqdm(raw_triples, desc="Parsing triples", unit="triple"):
        try:
            triple = Triple(
                subject=item["subject"],
                predicate=RelationshipType(item["predicate"]),
                object=item["object"],
                subject_type=EntityType(item["subject_type"]),
                object_type=EntityType(item["object_type"]),
                source_document=source_document,
            )
            triples.append(triple)
        except (KeyError, ValueError) as e:
            logger.warning("Skipping invalid triple: %s — %s", item, e)

    return triples


def extract_from_file(file_path: str | Path) -> list[Triple]:
    """Read a documentation file and extract triples from it.

    Args:
        file_path: Path to the .txt documentation file.

    Returns:
        A list of validated Triple objects.
    """
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")
    logger.info("Read %d characters from %s", len(text), path)
    return extract_triples(text, source_document=path.name)



