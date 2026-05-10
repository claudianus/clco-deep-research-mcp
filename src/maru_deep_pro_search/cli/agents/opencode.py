"""OpenCode adapter."""

from __future__ import annotations

import shutil
from pathlib import Path

from .base import AgentAdapter
from ..backup import backup_file, read_json_safe, read_text_safe, restore_file, write_json_safe, write_text_safe
from ..prompts import get_protocol_for_agent


class OpenCodeAdapter(AgentAdapter):
    name = "opencode"
    display_name = "OpenCode"

    def detect(self) -> bool:
        return (
            shutil.which("opencode") is not None
            or Path.home().joinpath(".config", "opencode").exists()
        )

    def _config_path(self, scope: str) -> Path:
        if scope == "project":
            return Path("opencode.json")
        return Path.home() / ".config" / "opencode" / "opencode.json"

    def _agents_md_path(self, scope: str) -> Path:
        if scope == "project":
            return Path("AGENTS.md")
        return Path.home() / ".config" / "opencode" / "AGENTS.md"

    def backup(self) -> list[Path]:
        paths = [self._config_path("user"), self._agents_md_path("user")]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [self._config_path("user"), self._agents_md_path("user")]:
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    def install_mcp(self, scope: str = "user") -> bool:
        path = self._config_path(scope)
        config = read_json_safe(path)
        if "mcp" not in config:
            config["mcp"] = {}

        config["mcp"]["maru-deep-pro-search"] = {
            "type": "local",
            "command": ["python3", "-m", "maru_deep_pro_search.server"],
            "enabled": True,
        }
        write_json_safe(path, config)
        return True

    def inject_rules(self, scope: str = "user") -> bool:
        path = self._agents_md_path(scope)
        content = read_text_safe(path)
        protocol = get_protocol_for_agent(self.name)

        if protocol in content:
            return True

        content += f"\n\n# maru-deep-pro-search Research Protocol\n\n{protocol}\n"
        write_text_safe(path, content)
        return True
