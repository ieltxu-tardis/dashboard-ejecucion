INSERT INTO tenants (slug, name)
VALUES ('default', 'Default Tenant')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO users (tenant_id, handle, email)
SELECT t.id, 'default-user', 'default@example.local'
FROM tenants t
WHERE t.slug = 'default'
ON CONFLICT DO NOTHING;
