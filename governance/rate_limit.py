from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RateLimitDecision:
    allowed: bool
    reason: str


class RedisRateLimiter:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root

    def _redis(self, args: list[str]) -> str:
        proc = subprocess.run(
            ["docker", "compose", "exec", "-T", "redis", "redis-cli", "--raw", *args],
            cwd=Path(self.repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            return "ERR"
        return proc.stdout.strip()

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitDecision:
        n = self._redis(["INCR", key])
        try:
            count = int(n)
        except Exception:
            return RateLimitDecision(True, "rate_limit_backend_unavailable")
        if count == 1:
            self._redis(["EXPIRE", key, str(window_seconds)])
        if count > limit:
            return RateLimitDecision(False, "rate_limit_exceeded")
        return RateLimitDecision(True, "allowed")
