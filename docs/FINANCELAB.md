# FINANCELAB.md

## Overview
FinanceLab MVP supports:
1) CSV import preview (safe summary only)
2) Approval-gated commit to `finance_transactions`
3) Transaction listing and spend summaries

## Core flow
1. write document containing CSV
2. `financelab.import_preview_csv`
3. `financelab.commit_import` -> returns `pending_approval` when missing approval
4. approve via `./scripts/approvals approve <approval_id> --reason "ok" --by "admin-local"`
5. re-run `financelab.commit_import` with `approval_id`

## Required scopes
- `finance:read`
- `finance:write`
- `docs:ingest`

## Validation
```bash
./docs_check 9
./scripts/test-financelab.sh
```
