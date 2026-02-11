# Agent Improvement Lab

## Goal
Build a local, measurable system to improve agent reliability, context awareness, and workflow quality across Codex/Claude Code/OpenCode using repeatable experiments.

## Status
Active.

## Project Paths
- /Users/ieltxualganaras/IDEAS/labctl.py
- /Users/ieltxualganaras/IDEAS/config/rubric.json
- /Users/ieltxualganaras/IDEAS/config/strategies.json
- /Users/ieltxualganaras/IDEAS/config/executors.json
- /Users/ieltxualganaras/IDEAS/data/reports/
- /Users/ieltxualganaras/IDEAS/data/runs/
- /Users/ieltxualganaras/IDEAS/data/snapshots/

## Core Commands
- `./labctl.py sessions-summary --hours 24`
- `./labctl.py score`
- `./labctl.py next`
- `./labctl.py run --executor cli --command "echo lab-ready" --expect-substring lab-ready`
- `./labctl.py metrics --days 7`

## Current Priorities
- Validate adapter parity across `cli`, `server`, `mcp`, `skill`.
- Add recall-quality metrics to memory/context experiments.
- Convert recurring checks into weekly automation.

## Links
- [[Active-Projects]]
- [[Worklog]]
- [[Decisions]]
- [[Tasks]]

## Eval Pack (2026-02-06)
- Added `/Users/ieltxualganaras/IDEAS/config/evals.json` with 15 recurring evals across memory/context, skills/automation, OpenAI docs, UI/perf, Obsidian sync, and AGENTS policy change control.
- Command: `./labctl.py evals --show summary`
- Validation result: `Validation: OK`.

## Latest Eval Cycle (P0)
- Command: `./labctl.py eval-cycle --priority P0`
- Score: `64.3`
- Result split: `pass=3`, `fail=1`, `inconclusive=3`
- Report: `/Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-p0-20260206-141754.md`
- Snapshot: `/Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-p0-20260206-141754.json`

## P0 Eval Gate Cleared (2026-02-06)
- Added typed metrics support to run logger (`--metric KEY=VALUE`) and write-gate policy doc (`docs/MEMORY_WRITE_GATES.md`).
- Executed instrumented runs for recall, pruning, and memory write-gates.
- `./labctl.py eval-cycle --priority P0` => `pass=7`, `fail=0`, `inconclusive=0`, `cycle_score=100.0`.
- Report: `/Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-p0-20260206-142953.md`
- Snapshot: `/Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-p0-20260206-142953.json`

## Full Eval Baseline (ALL) - 2026-02-06
- Command: `./labctl.py eval-cycle --priority ALL`
- Result: `pass=15`, `fail=0`, `inconclusive=0`, `cycle_score=100.0`
- Report: `/Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-all-20260206-144645.md`
- Snapshot: `/Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-all-20260206-144645.json`

## Manual Gold Baseline (2026-02-06)
- Commands run: `sessions-summary`, `score`, `eval-cycle --priority ALL`, `metrics`
- Outcome: `pass=15`, `fail=0`, `inconclusive=0`, `cycle_score=100.0`
- Brief: `/Users/ieltxualganaras/IDEAS/data/reports/baseline-brief-20260206-150226.md`
- Eval report: `/Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-all-20260206-150226.md`
- Snapshot: `/Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-all-20260206-150226.json`

## Phone Notifications (2026-02-06)
- Installed launchd notifier: com.codex.phone-notifier
- Topic: codex-ieltxualganaras-bf6dec32905938ce
- Source DB: ~/.codex/sqlite/codex-dev.db (automation_runs)
- Triggers:
  - PENDING_REVIEW + unread -> needs input push
  - ARCHIVED -> task finished push
- Docs: /Users/ieltxualganaras/IDEAS/docs/PHONE_NOTIFICATIONS.md
- Debug logs: ~/.codex/tmp/phone-notifier.log and ~/.codex/tmp/phone-notifier.err.log

- 2026-02-07: Ran labctl sessions-summary (24h), score, eval-cycle ALL, and metrics (7d). Eval: pass=13 fail=2 inconclusive=0. Reports: /Users/ieltxualganaras/IDEAS/data/reports/sessions-summary-20260207-090033.md; /Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-all-20260207-090038.md. Snapshots: /Users/ieltxualganaras/IDEAS/data/snapshots/strategy-scores-20260207-090035.json; /Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-all-20260207-090038.json. Failures: OpenAI docs citation freshness + primary sourcing; tasks added in AI/Tasks.md.

- 2026-02-07: Ran labctl sessions-summary (24h), score, eval-cycle ALL, and metrics (7d). Eval: pass=13 fail=2 inconclusive=0. Reports: /Users/ieltxualganaras/IDEAS/data/reports/sessions-summary-20260207-090033.md; /Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-all-20260207-090038.md. Snapshots: /Users/ieltxualganaras/IDEAS/data/snapshots/strategy-scores-20260207-090035.json; /Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-all-20260207-090038.json. Failures: OpenAI docs citation freshness + primary sourcing; tasks added in AI/Tasks.md.

## 2026-02-08
- Weekly run: eval-cycle ALL: pass=14 fail=0 inconclusive=1 (cycle_score=96.7).
- Reports: /Users/ieltxualganaras/IDEAS/data/reports/sessions-summary-20260208-090101.md; /Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-all-20260208-090106.md
- Snapshots: /Users/ieltxualganaras/IDEAS/data/snapshots/strategy-scores-20260208-090103.json; /Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-all-20260208-090106.json

- 2026-02-09: Ran labctl sessions-summary/score/eval-cycle/metrics. Eval pass=10 fail=4 inconclusive=1. Reports: /Users/ieltxualganaras/IDEAS/data/reports/sessions-summary-20260209-090026.md; /Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-all-20260209-090026.md. Snapshots: /Users/ieltxualganaras/IDEAS/data/snapshots/strategy-scores-20260209-090026.json; /Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-all-20260209-090026.json. Failures: policy-change control, OpenAI docs citation freshness, OpenAI docs primary sourcing, UI regression checks. Inconclusive: Obsidian fallback reliability. Added remediation tasks in AI/Tasks.

- 2026-02-09: Ran labctl sessions-summary/score/eval-cycle/metrics. Eval pass=10 fail=4 inconclusive=1. Reports: /Users/ieltxualganaras/IDEAS/data/reports/sessions-summary-20260209-090026.md; /Users/ieltxualganaras/IDEAS/data/reports/eval-cycle-all-20260209-090026.md. Snapshots: /Users/ieltxualganaras/IDEAS/data/snapshots/strategy-scores-20260209-090026.json; /Users/ieltxualganaras/IDEAS/data/snapshots/eval-cycle-all-20260209-090026.json. Failures: policy-change control, OpenAI docs citation freshness, OpenAI docs primary sourcing, UI regression checks. Inconclusive: Obsidian fallback reliability. Added remediation tasks in AI/Tasks.
