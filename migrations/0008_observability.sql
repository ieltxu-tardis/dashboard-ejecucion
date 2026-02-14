CREATE TABLE IF NOT EXISTS observability_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID,
  component TEXT NOT NULL,
  route TEXT,
  event_type TEXT NOT NULL,
  job_type TEXT,
  outcome TEXT,
  error_code TEXT,
  latency_ms INT,
  value_num DOUBLE PRECISION,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_observability_events_component_time
  ON observability_events(component, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_observability_events_job_type
  ON observability_events(job_type, created_at DESC);
