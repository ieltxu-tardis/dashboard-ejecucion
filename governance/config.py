from __future__ import annotations

import os
import yaml
from pathlib import Path
from dataclasses import dataclass


@dataclass
class GovernanceConfig:
    safe_mode_tools_disabled: bool
    safe_mode_jobs_disabled: bool
    safe_mode_finance_write_disabled: bool
    req_max_tool_calls: int
    req_max_jobs_enqueued: int
    req_max_total_runtime_ms: int
    queue_depth_high: int
    queue_lag_high_seconds: int


def load_yaml(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text())


def load_config() -> GovernanceConfig:
    return GovernanceConfig(
        safe_mode_tools_disabled=os.getenv("SAFE_MODE_DISABLE_TOOLS", "0") == "1",
        safe_mode_jobs_disabled=os.getenv("SAFE_MODE_DISABLE_JOB_ENQUEUE", "0") == "1",
        safe_mode_finance_write_disabled=os.getenv("SAFE_MODE_DISABLE_FINANCE_WRITE", "0") == "1",
        req_max_tool_calls=int(os.getenv("REQ_MAX_TOOL_CALLS", "12")),
        req_max_jobs_enqueued=int(os.getenv("REQ_MAX_JOBS_ENQUEUED", "5")),
        req_max_total_runtime_ms=int(os.getenv("REQ_MAX_TOTAL_RUNTIME_MS", "120000")),
        queue_depth_high=int(os.getenv("QUEUE_DEPTH_HIGH", "50")),
        queue_lag_high_seconds=int(os.getenv("QUEUE_LAG_HIGH_SECONDS", "120")),
    )
