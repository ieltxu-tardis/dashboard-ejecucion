# MODULE_digesthub.md

DigestHub handles digest subscriptions, previews, and DM delivery orchestration.

## Tools
- `digesthub.subscribe_daily` (`digest:write`)
- `digesthub.subscribe_weekly` (`digest:write`)
- `digesthub.unsubscribe` (`digest:write`)
- `digesthub.preview_daily` (`digest:read`)
- `digesthub.send_now` (`digest:write`)

## Safety
- delivery mode forced to `dm` in MVP
- no finance writes
- no external account connections
- audited sends with content hash only
