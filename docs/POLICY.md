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

## Scope model (enforced baseline)
- `memory:write`
- `memory:read`
- `docs:ingest`
- `exec:sandbox`
- `finance:read`
- `finance:write`
- `ideas:read`
- `ideas:write`
- `time:read`
- `time:write`

## Enforcement (Phase 6)
- deny-by-default for unregistered tools
- actor scope checks against `governance/scopes.yaml`
- approval gating when tool has `requires_approval=true`
- request budgets for tool calls and jobs enqueued
- rate limiting via Redis keys per actor
- safe-mode switches (tools/jobs/finance write)

## Scope/action sensitivity matrix

| Tool / Action | Scope | Sensitive | Requires approval | Cost class |
|---|---|---:|---:|---|
| memory.semantic_search | memory:read | no | no | low |
| jobs.enqueue_embed | docs:ingest | no | no | med |
| finance.write_transaction | finance:write | yes | yes | high |
| idealab.capture_idea | ideas:write | no | no | low |
| idealab.list_ideas | ideas:read | no | no | low |
| idealab.evaluate_idea | ideas:read | no | no | med |
| idealab.plan_experiment | ideas:write | no | no | med |
| idealab.log_experiment_result | ideas:write | no | no | low |
| timelab.capture_task | time:write | no | no | low |
| timelab.list_tasks | time:read | no | no | low |
| timelab.update_task | time:write | no | no | low |
| timelab.capture_goal | time:write | no | no | low |
| timelab.list_goals | time:read | no | no | low |
| timelab.weekly_review | time:read (time:write when persist) | no | no | med |

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
