CREATE TABLE IF NOT EXISTS approval_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  actor_ref TEXT NOT NULL,
  action TEXT NOT NULL,
  scope TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  reason_code TEXT,
  request_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  decided_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_approval_requests_tenant_status ON approval_requests(tenant_id, status, created_at DESC);
