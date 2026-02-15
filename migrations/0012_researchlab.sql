CREATE TABLE IF NOT EXISTS research_collections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_research_collections_tenant_name_lower
  ON research_collections(tenant_id, lower(name));

CREATE INDEX IF NOT EXISTS idx_research_collections_tenant_created
  ON research_collections(tenant_id, created_at DESC);

CREATE TABLE IF NOT EXISTS research_collection_documents (
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  collection_id UUID NOT NULL REFERENCES research_collections(id) ON DELETE CASCADE,
  doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (tenant_id, collection_id, doc_id)
);

CREATE INDEX IF NOT EXISTS idx_research_collection_docs_collection
  ON research_collection_documents(tenant_id, collection_id);

CREATE INDEX IF NOT EXISTS idx_research_collection_docs_doc
  ON research_collection_documents(tenant_id, doc_id);
