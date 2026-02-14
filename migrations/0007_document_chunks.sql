CREATE TABLE IF NOT EXISTS document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_id TEXT NOT NULL,
  chunk_text TEXT NOT NULL,
  chunk_index INT NOT NULL,
  token_estimate INT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, doc_id, chunk_id)
);

CREATE INDEX IF NOT EXISTS idx_document_chunks_doc ON document_chunks(tenant_id, doc_id, chunk_index);
