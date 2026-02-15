# MODULE_researchlab.md

ResearchLab MVP: local knowledge base with collections and cited semantic search.

## Tools
- `researchlab.ingest_note` (`research:write`)
- `researchlab.create_collection` (`research:write`)
- `researchlab.list_collections` (`research:read`)
- `researchlab.add_to_collection` (`research:write`)
- `researchlab.search` (`research:read`)
- `researchlab.context_pack` (`research:read`)

## Data model
- `research_collections`
- `research_collection_documents`
- documents/chunks/embeddings from core memory pipeline

## Safety
- no web scraping/fetch in MVP
- no external account connections
- tenant-safe filtering on every query
- outputs include citations (doc/chunk/source_ref)
