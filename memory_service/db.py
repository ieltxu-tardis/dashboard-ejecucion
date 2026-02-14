import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


_PLACEHOLDER = re.compile(r"%\((?P<key>[a-zA-Z_][a-zA-Z0-9_]*)\)s")


class PostgresExec:
    def __init__(self, repo_root: str | None = None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1])
        self.env = self._load_env(self.repo_root / ".env")

    def _load_env(self, env_path: Path) -> dict[str, str]:
        env = os.environ.copy()
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k] = v
        return env

    def _sql_literal(self, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        s = str(value).replace("'", "''")
        return f"'{s}'"

    def _prepare(self, sql: str, params: dict[str, Any] | None) -> str:
        params = params or {}

        def repl(match: re.Match[str]) -> str:
            key = match.group("key")
            if key not in params:
                raise KeyError(f"missing_sql_param:{key}")
            return self._sql_literal(params[key])

        return _PLACEHOLDER.sub(repl, sql)

    def _psql(self, sql: str, *, params: dict[str, Any] | None = None, fetch: bool = True) -> str:
        rendered_sql = self._prepare(sql, params)
        cmd = [
            "docker",
            "compose",
            "exec",
            "-T",
            "postgres",
            "psql",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            self.env["POSTGRES_USER"],
            "-d",
            self.env["POSTGRES_DB"],
            "-At",
            "-F",
            "|",
            "-c",
            rendered_sql,
        ]
        proc = subprocess.run(
            cmd,
            cwd=self.repo_root,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "psql_failed")
        return proc.stdout.strip() if fetch else ""

    def fetchall_json(self, sql: str, *, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        wrapped = f"SELECT COALESCE(json_agg(t), '[]'::json)::text FROM ({sql}) t;"
        out = self._psql(wrapped, params=params, fetch=True)
        return json.loads(out or "[]")

    def fetchone_value(self, sql: str, *, params: dict[str, Any] | None = None) -> str | None:
        out = self._psql(sql, params=params, fetch=True)
        return out if out else None

    def execute(self, sql: str, *, params: dict[str, Any] | None = None) -> None:
        _ = self._psql(sql, params=params, fetch=False)
