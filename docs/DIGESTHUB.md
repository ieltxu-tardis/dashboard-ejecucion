# DIGESTHUB.md

## Overview
DigestHub MVP generates daily/weekly review digests and sends DM-only by default.

Sections:
1. TimeLab (due soon/overdue/recent done)
2. FinanceLab (weekly spend summary by category, read-only)
3. IdeaLab (recent ideas + top evaluated)
4. ResearchLab (recent docs + suggested searches)

## Delivery
- DM-only default
- no arbitrary channel ids accepted
- simulated send mode in MVP tests

## Scheduler
Use `scripts/digest-tick.sh` from cron/systemd.

## Validation
```bash
./docs_check 11
./scripts/test-digesthub.sh
```
