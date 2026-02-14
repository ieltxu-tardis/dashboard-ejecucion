# POLICY.md

## Memory write policy (Phase 3)

Default stance: **deny-by-default for inferred writes**.

A memory write is allowed only when intent is one of:
1. `explicit_user_intent`
2. `explicit_command`
3. `validated_structured_extraction`

And always requires:
- `reason`
- `source`
- `scope`
- `confidence` (0..1)

Extra rule for `validated_structured_extraction`:
- schema validation must pass
- confidence must be `>= 0.85`

## Scope model (baseline)
- `memory:write`
- `memory:read`
- `docs:ingest`
- `exec:sandbox`

(Expanded scope/budget engine is planned for later phase.)

## Approvals/budgets (current)
- Budgets are documented but not enforced by runtime gate yet.
- Sensitive external side-effects remain manual approval territory.

## Audit policy
On every successful structured write:
- create `audit_log` event with tenant + actor + action + target
- redact secrets (do not store raw credentials/tokens)

## Structured policy contract (v0)

```yaml
memory_write_policy_v0:
  mode: deny_by_default_for_inference
  allowed_intent_types:
    - explicit_user_intent
    - explicit_command
    - validated_structured_extraction
  required_fields:
    - reason
    - source
    - scope
    - confidence
  extraction_guardrails:
    schema_valid_required: true
    min_confidence: 0.85
  audit_on_write: true
```

## Verification

```bash
python3 -m unittest tests/test_policy.py
```
