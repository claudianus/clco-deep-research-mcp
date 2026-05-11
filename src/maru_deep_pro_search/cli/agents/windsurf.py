"""Windsurf adapter."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..backup import (
    backup_file,
    read_json_safe,
    read_text_safe,
    restore_file,
    write_json_safe,
    write_text_safe,
)
from ..prompts import get_protocol_for_agent
from .base import AgentAdapter


class WindsurfAdapter(AgentAdapter):
    name = "windsurf"
    display_name = "Windsurf"

    def detect(self) -> bool:
        return (
            Path(".windsurf").exists()
            or Path.home().joinpath(".windsurf").exists()
            or shutil.which("windsurf") is not None
        )

    def _mcp_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".windsurf") / "mcp_config.json"
        return Path.home() / ".windsurf" / "mcp_config.json"

    def _rules_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".windsurfrules")
        return Path.home() / ".windsurfrules"

    def backup(self) -> list[Path]:
        paths = [self._mcp_path("user"), self._rules_path("user")]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [self._mcp_path("user"), self._rules_path("user")]:
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
        path = self._rules_path(scope)
        content = read_text_safe(path)
        protocol = get_protocol_for_agent(self.name)

        if protocol in content:
            return True

        content += f"\n\n{protocol}\n"
        write_text_safe(path, content)
        return True
