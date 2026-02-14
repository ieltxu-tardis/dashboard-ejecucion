# MODULE_timelab.md

TimeLab MVP manages tasks, goals, and weekly review summaries.

## Tools
- `timelab.capture_task` (`time:write`)
- `timelab.list_tasks` (`time:read`)
- `timelab.update_task` (`time:write`)
- `timelab.capture_goal` (`time:write`)
- `timelab.list_goals` (`time:read`)
- `timelab.weekly_review` (`time:read`; when `persist=true` it writes with `time:write` scope inside memory write payload)

## Data model
- Tasks -> `tasks` table
- Goals -> `entities(type='goal')`
- Weekly review persisted -> `documents(source_type='weekly_review')`

## Safety
- tenant-safe queries only
- no approvals required
- governance budgets/rate-limit still apply
