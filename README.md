# Technical Documentation Knowledge Graph

> An LLM-powered knowledge graph that transforms unstructured developer documentation into a queryable, interconnected knowledge base using Neo4j, GraphDB, and SPARQL.

## 📋 Summary

**Technical Documentation Knowledge Graph** | *Python, Neo4j, GraphDB, SPARQL, Docker, OpenRouter, Pydantic*

- Builting a document intelligence pipeline that extracts structured entities and relationships from official developer documentation into Neo4j and GraphDB using LLMs.
- Designing an ontology-driven validation and query system with Cypher and SPARQL, enabling visualization and exploration of API dependencies in NeoDash.

---

## 🎯 Project Overview

Developer documentation is fragmented and difficult to navigate. This project solves that by:

1. **Extracting** structured entities (Functions, APIs, Parameters, Commands) from raw documentation using LLMs
2. **Validating** extractions against a strict ontology to ensure data quality
3. **Storing** the knowledge graph in Neo4j (property graph) and GraphDB (RDF triplestore)
4. **Querying** with both Cypher and SPARQL to answer complex questions
5. **Visualizing** dependencies and relationships in NeoDash

---

## 📁 Project Structure

```
technical-documentation-knowledge-graph/
├── README.md
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── data/
│   ├── raw/                 # Place your .txt documentation files here
│   └── processed/           # Extracted triples and RDF exports
├── src/
│   ├── ontology.py          # Defines allowed nodes and relationships
│   ├── extract.py           # LLM extraction pipeline
│   ├── validate.py          # Ontology compliance checker
│   ├── load_neo4j.py        # Cypher loader for Neo4j
│   └── load_graphdb.py      # RDF converter for GraphDB
├── queries/
│   ├── cypher/              # Sample Cypher queries
│   └── sparql/              # Sample SPARQL queries
├── docker/
│   └── neo4j/               # Neo4j data and plugins
└── dashboard/
    └── neodash_export.json  # NeoDash dashboard configuration
```

---
<!-- 
## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- `uv` (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Setup

```bash
# Install dependencies with uv
uv sync

# Start databases
docker-compose up -d

# Run extraction
uv run python src/extract.py
```

---

## 📊 Example Queries

### Cypher (Neo4j)

**Find all dependencies of FastAPI:**
```cypher
MATCH path = (api:Entity {name: "FastAPI"})-[:RELATES*1..3 {type: "DEPENDS_ON"}]->(dep)
RETURN path
LIMIT 25
```

### SPARQL (GraphDB)

**Find all APIs and their parameters:**
```sparql
PREFIX ex: <http://example.org/devdoc/>
SELECT ?api ?param WHERE {
  ?api ex:TAKES ?param .
  ?api rdf:type ex:API .
}
```

---

## 📄 License

MIT License

## References
https://learnxinyminutes.com/cypher/
