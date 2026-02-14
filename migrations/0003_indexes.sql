CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);

CREATE INDEX IF NOT EXISTS idx_documents_tenant_id ON documents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_documents_tenant_created_at ON documents(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_documents_source_ref ON documents(tenant_id, source_ref);

CREATE INDEX IF NOT EXISTS idx_entities_tenant_id ON entities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_entities_tenant_type ON entities(tenant_id, type);
CREATE INDEX IF NOT EXISTS idx_entities_tenant_name ON entities(tenant_id, name);

CREATE INDEX IF NOT EXISTS idx_facts_tenant_id ON facts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_facts_tenant_key ON facts(tenant_id, key);
CREATE INDEX IF NOT EXISTS idx_facts_source_doc_id ON facts(source_doc_id);

CREATE INDEX IF NOT EXISTS idx_events_tenant_id ON events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_events_tenant_event_type_created ON events(tenant_id, event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_embeddings_tenant_id ON embeddings(tenant_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_tenant_doc_id ON embeddings(tenant_id, doc_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(model);

CREATE INDEX IF NOT EXISTS idx_audit_log_tenant_created_at ON audit_log(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_job_runs_tenant_started_at ON job_runs(tenant_id, started_at DESC);

-- NOTE: vector ANN index intentionally deferred until representative data exists.
-- Rationale documented in docs/DATA_MODEL.md to avoid poor ivfflat list sizing early.
