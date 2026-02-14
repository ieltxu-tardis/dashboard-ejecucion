from __future__ import annotations

import json
import time
from typing import Any

SENSITIVE_KEYS = {"password", "token", "secret", "key", "authorization", "cookie", "set-cookie"}


def _redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if any(s in lk for s in SENSITIVE_KEYS):
                out[k] = "***REDACTED***"
            else:
                out[k] = _redact(v)
        return out
    if isinstance(obj, list):
        return [_redact(x) for x in obj]
    if isinstance(obj, str) and len(obj) > 500:
        return obj[:500] + "…[truncated]"
    return obj


def log_event(level: str, component: str, message: str, **fields: Any) -> None:
    payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "component": component,
        "message": message,
    }
    payload.update(_redact(fields))
    print(json.dumps(payload, ensure_ascii=False), flush=True)
