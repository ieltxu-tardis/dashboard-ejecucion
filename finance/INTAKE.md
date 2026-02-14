# Intake rules (v0)

Purpose: convert short Spanish text into one expense JSONL row.

## Accepted patterns (examples)
- `gasté 25 usd en hosting`
- `pagué 18000 ars de supermercado`
- `uber 12 usd`
- `12 usd taxi`

## Parsing steps
1. **Amount**: first numeric token (`25`, `18000`, `12`).
2. **Currency**: detect `usd` or `ars` (case-insensitive). Default = `ARS` if omitted.
3. **Description/category**:
   - text after `en` / `de`, else remaining words.
   - normalize to lowercase.
4. **Kind**: always `expense` (v0).
5. **Timestamp**: ingestion time in UTC ISO-8601.
6. **FX**: use configured rate for the day (`ars_per_usd`, `usd_per_ars`).
7. **Normalized values**:
   - USD input → `amount_usd = original`, `amount_ars = original * ars_per_usd`
   - ARS input → `amount_ars = original`, `amount_usd = original * usd_per_ars`
8. **Append** one JSON object line to `expenses.jsonl`.

## Minimal defaults
- `payment_method`: `other`
- `notes`: `""`
- `source_text`: raw original message

## Validation
- reject if no numeric amount
- reject if currency token not recognized (`ars|usd`) and not omitted
- store amounts as numbers (not strings)
