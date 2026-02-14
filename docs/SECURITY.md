# SECURITY.md

## Threat model (concise)

Primary risks:
- Unauthorized tool execution
- Cross-tenant data access
- Unbounded job/tool loops causing degradation
- Sensitive data leakage in logs/audit

## Controls in place (Phase 6)
- Tool registry allowlist (deny unregistered tools)
- Scope-based authorization per actor
- Approval gating for sensitive tools
- Request/job budgets and rate limiting
- Safe mode kill switches
- Audit trail for allow/deny/pending decisions
- Log redaction for sensitive keys

## Sensitive data handling
- Never log passwords/tokens/authorization/cookies.
- Audit payloads store reason/meta only (no raw secrets).

## Multi-tenant safety
- Tenant-scoped DB access in service/repository layer.
- Governance decisions always include tenant context.

## Security verification
```bash
./scripts/test-governance.sh
./scripts/test-observability.sh
```
