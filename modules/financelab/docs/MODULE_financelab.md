# MODULE_financelab.md

FinanceLab MVP provides CSV import preview and approval-gated commits.

## Tools
- `financelab.import_preview_csv` (`docs:ingest`)
- `financelab.list_transactions` (`finance:read`)
- `financelab.spend_summary` (`finance:read`)
- `financelab.commit_import` (`finance:write`, approval required)
- `financelab.write_transaction` (`finance:write`, approval required)

## Safety
- No external account connections.
- Preview never writes final transactions.
- Commit/write require approval via 6.1 flow.
- Dedupe enforced with `external_id_or_hash` unique key.
- Logs/audit store counts/hashes/summary only.
