# TIMELAB.md

## Overview
TimeLab MVP adds lightweight productivity workflows:
- capture/list/update tasks
- capture/list goals
- weekly review summary (preview + optional persist)

## Required scopes
- `time:read`
- `time:write`

## Example flow
1. `timelab.capture_task`
2. `timelab.list_tasks`
3. `timelab.update_task` (done or reschedule)
4. `timelab.capture_goal`
5. `timelab.weekly_review` (`persist=false` preview)
6. `timelab.weekly_review` (`persist=true` stores weekly document)

## Validation
```bash
./docs_check 8
./scripts/test-timelab.sh
```
