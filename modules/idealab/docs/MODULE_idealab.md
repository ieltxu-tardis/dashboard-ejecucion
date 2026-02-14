# MODULE_idealab.md

IdeaLab module provides lightweight idea capture, evaluation, and experiment tracking.

## Tools
- `idealab.capture_idea` (`ideas:write`)
- `idealab.list_ideas` (`ideas:read`)
- `idealab.evaluate_idea` (`ideas:read`)
- `idealab.plan_experiment` (`ideas:write`)
- `idealab.log_experiment_result` (`ideas:write`)

## Enable/Disable
Controlled by module registry (`modules/modules.yaml`) or env override:
- `MODULES_ENABLED=idealab`

## Persistence model
- Ideas -> `entities(type='idea')`
- Experiments -> `entities(type='experiment')`
- Evaluations -> `facts(key='idealab.evaluation')`
- Lifecycle markers -> `events(event_type='idealab.*')`

## Safety
- Multi-tenant through `tenant_id` at MemoryService boundary.
- No sensitive external side effects.
- Governance scopes enforced pre-tool execution.
