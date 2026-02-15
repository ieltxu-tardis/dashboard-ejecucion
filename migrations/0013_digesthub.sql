CREATE TABLE IF NOT EXISTS digest_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  actor_id TEXT NOT NULL,
  delivery_mode TEXT NOT NULL DEFAULT 'dm',
  timezone TEXT NOT NULL DEFAULT 'UTC',
  period TEXT NOT NULL,
  schedule JSONB NOT NULL DEFAULT '{}'::jsonb,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  last_sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (tenant_id, actor_id, period)
);

CREATE INDEX IF NOT EXISTS idx_digest_subscriptions_due
  ON digest_subscriptions(tenant_id, enabled, period, updated_at);

CREATE TABLE IF NOT EXISTS digest_deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  subscription_id UUID NOT NULL REFERENCES digest_subscriptions(id) ON DELETE CASCADE,
  period TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  status TEXT NOT NULL,
  summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_digest_deliveries_sub_created
  ON digest_deliveries(subscription_id, created_at DESC);
