CREATE TABLE IF NOT EXISTS finance_transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  ts TIMESTAMPTZ NOT NULL,
  amount NUMERIC(14,2) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD',
  category TEXT,
  merchant TEXT,
  note TEXT,
  external_id_or_hash TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, external_id_or_hash)
);

CREATE INDEX IF NOT EXISTS idx_finance_transactions_tenant_ts
  ON finance_transactions(tenant_id, ts DESC);

CREATE INDEX IF NOT EXISTS idx_finance_transactions_tenant_category
  ON finance_transactions(tenant_id, category);

CREATE TABLE IF NOT EXISTS finance_imports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  source_doc_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  status TEXT NOT NULL,
  payload_hash TEXT NOT NULL,
  summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_finance_imports_tenant_status
  ON finance_imports(tenant_id, status, created_at DESC);
