# Finance Intake v0

Minimal, append-only expense capture optimized for short text messages.

## Goal
Capture expenses quickly from free text, while preserving:
- original amount + original currency
- FX used at capture time
- normalized ARS value
- normalized USD value

## Storage
- File: `finance/expenses.jsonl`
- Format: one JSON object per line (JSONL)
- Rule: never rewrite historical lines; append corrections as new entries

## Data model (expense event)

```json
{
  "id": "exp_20260214_0001",
  "timestamp": "2026-02-14T03:10:00Z",
  "source_text": "gasté 25 usd en hosting",
  "kind": "expense",
  "category": "hosting",
  "description": "hosting",

  "amount_original": 25,
  "currency_original": "USD",

  "fx": {
    "ars_per_usd": 1200,
    "usd_per_ars": 0.0008333333,
    "source": "manual",
    "as_of": "2026-02-14"
  },

  "amount_ars": 30000,
  "amount_usd": 25,

  "payment_method": "card",
  "notes": "",
  "created_at": "2026-02-14T03:10:02Z"
}
```

## Normalization rules
- If original currency = `USD`:
  - `amount_usd = amount_original`
  - `amount_ars = amount_usd * fx.ars_per_usd`
- If original currency = `ARS`:
  - `amount_ars = amount_original`
  - `amount_usd = amount_ars * fx.usd_per_ars`
- Keep both normalized values even when one is derived.

## Suggested enums
- `kind`: `expense` (v0)
- `currency_original`: `ARS`, `USD`
- `payment_method`: `cash`, `debit`, `credit`, `transfer`, `wallet`, `card`, `other`

## Why JSONL
- frictionless append
- easy git diff/history
- easy import to scripts/SQL later
