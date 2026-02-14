# EMBEDDINGS.md

## Embedding pipeline (Phase 4)

## Flow
1. `write_document()` (MemoryService) persists document
2. enqueue `embed_document` async job
3. worker loads document content
4. chunking (`chunk_text`)
5. embed each chunk with provider
6. upsert into:
   - `document_chunks`
   - `embeddings`

## Provider interface
- `EmbeddingProvider` protocol
- default: `LocalHashEmbeddingProvider`
  - deterministic
  - local CPU-friendly
  - no external API keys

## Dimension
- current dimension: `1536`
- must match `embeddings.embedding VECTOR(1536)`
- change requires migration + provider config update

## Semantic search output
`semantic_search()` returns:
- `doc_id`
- `chunk_id`
- `distance` (score proxy)
- `snippet` (from `document_chunks`)

## Reindex strategy (later)
- planned Phase 4+/5 helper:
  - enqueue `embed_document` for target docs/model
- safe because upsert key is `(tenant_id, doc_id, chunk_id, model)`
