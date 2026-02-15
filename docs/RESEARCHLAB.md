# RESEARCHLAB.md

## Overview
ResearchLab MVP provides local research workflows:
- ingest notes/documents into tenant memory
- organize docs in collections
- semantic search returning snippets + citations
- context packs for orchestrator answer synthesis

## Required scopes
- `research:read`
- `research:write`

## Example flow
1. `researchlab.create_collection`
2. `researchlab.ingest_note` (optional `collection_id`)
3. `researchlab.search` (global or collection-filtered)
4. `researchlab.context_pack`

## Validation
```bash
./docs_check 10
./scripts/test-researchlab.sh
```
