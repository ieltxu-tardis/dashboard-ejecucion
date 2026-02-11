# Bridge (OpenClaw side)

## Purpose
Safe import sandbox for files exported from Mac `~/OpenClawBridge/outbox`.

## Expected input
Put archives in:
- `bridge/incoming/latest-export.tgz` (preferred), or
- any `bridge/incoming/*.tgz`

## Run import
```bash
bash bridge/import.sh
# or specific archive
bash bridge/import.sh bridge/incoming/my-export.tgz
```

## Output
- Extracted run: `bridge/imports/import-YYYYmmdd-HHMMSS/`
- Latest link: `bridge/imports/latest`
- Sanitized files for assistant work: `bridge/sandbox/current/`
- Logs: `bridge/logs/import-*.log`

## Notes
- Removes macOS metadata (`._*`, `.DS_Store`)
- Keeps only text-like files (`.md`, `.txt`, `.json`, `.yaml`, `.yml`)
