ALTER TABLE approval_requests
  ADD COLUMN IF NOT EXISTS decided_by TEXT,
  ADD COLUMN IF NOT EXISTS decision_reason TEXT,
  ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS payload_hash TEXT,
  ADD COLUMN IF NOT EXISTS payload_summary TEXT;

UPDATE approval_requests
SET expires_at = COALESCE(expires_at, created_at + INTERVAL '15 minutes')
WHERE expires_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_approval_requests_status_created_at ON approval_requests(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_approval_requests_tenant_id ON approval_requests(tenant_id);
