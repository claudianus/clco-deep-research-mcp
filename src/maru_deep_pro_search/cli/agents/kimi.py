"""Kimi Code CLI adapter."""

from __future__ import annotations

import shutil
from pathlib import Path

from .base import AgentAdapter
from ..backup import backup_file, read_json_safe, read_text_safe, restore_file, write_json_safe, write_text_safe
from ..prompts import get_protocol_for_agent


class KimiAdapter(AgentAdapter):
    name = "kimi"
    display_name = "Kimi Code CLI"

    def detect(self) -> bool:
        return (
            shutil.which("kimi") is not None
            or Path.home().joinpath(".kimi").exists()
        )

    def _mcp_path(self, scope: str) -> Path:
        return Path.home() / ".kimi" / "mcp.json"

    def _settings_path(self, scope: str) -> Path:
        return Path.home() / ".kimi" / "settings.json"

    def backup(self) -> list[Path]:
        paths = [self._mcp_path("user"), self._settings_path("user")]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [self._mcp_path("user"), self._settings_path("user")]:
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    def install_mcp(self, scope: str = "user") -> bool:
        path = self._mcp_path(scope)
        config = read_json_safe(path)
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"]["maru-deep-pro-search"] = {
            "command": "python3",
            "args": ["-m", "maru_deep_pro_search.server"],
        }
        write_json_safe(path, config)
        return True

    def inject_rules(self, scope: str = "user") -> bool:
        path = self._settings_path(scope)
        config = read_json_safe(path)
        if "systemPrompt" not in config:
            config["systemPrompt"] = ""

        protocol = get_protocol_for_agent(self.name)
        if protocol in config.get("systemPrompt", ""):
            return True

        config["systemPrompt"] = config.get("systemPrompt", "") + f"\n\n{protocol}"
        write_json_safe(path, config)
        return True
