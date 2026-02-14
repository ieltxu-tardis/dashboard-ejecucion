# IDEALAB.md

## Overview
IdeaLab MVP is the first capability module delivered in Phase 7.

It supports:
1. Capture ideas
2. List ideas
3. Evaluate idea quality with a simple rubric
4. Plan experiments
5. Log experiment results

## Tool contracts
- `idealab.capture_idea` -> writes `entity(type=idea)`
- `idealab.list_ideas` -> reads idea entities
- `idealab.evaluate_idea` -> writes `fact(idealab.evaluation)` + `event(idealab.idea_evaluated)`
- `idealab.plan_experiment` -> writes `entity(type=experiment)`
- `idealab.log_experiment_result` -> updates experiment + writes `event(idealab.experiment_result)`

## Required scopes
- `ideas:read`
- `ideas:write`

## Example flow
1. capture_idea(title, summary, tags)
2. list_ideas()
3. evaluate_idea(idea_id)
4. plan_experiment(idea_id, hypothesis, metric, plan)
5. log_experiment_result(experiment_id, result)

## Validation
```bash
./docs_check 7
./scripts/test-idealab.sh
```
