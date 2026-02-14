from __future__ import annotations

import os
from pathlib import Path
import yaml


class ModuleRegistry:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.cfg = yaml.safe_load((self.repo_root / "modules/modules.yaml").read_text())

    def enabled_modules(self) -> set[str]:
        env = os.getenv("MODULES_ENABLED", "")
        if env.strip():
            return {x.strip() for x in env.split(",") if x.strip()}
        return {m["name"] for m in self.cfg.get("modules", []) if m.get("enabled", False)}

    def is_enabled(self, module_name: str) -> bool:
        return module_name in self.enabled_modules()
