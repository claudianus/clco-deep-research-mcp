"""OpenCode adapter."""

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
from ..prompts import get_protocol_for_agent, inject_protocol
from .base import AgentAdapter, get_mcp_server_command_list


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
            "command": get_mcp_server_command_list(),
            "enabled": True,
        }
        write_json_safe(path, config)
        return True

    def inject_rules(self, scope: str = "user") -> bool:
        # 1. AGENTS.md
        path = self._agents_md_path(scope)
        content = read_text_safe(path)
        protocol = get_protocol_for_agent(self.name)

        new_content = inject_protocol(content, protocol)
        if new_content != content:
            write_text_safe(path, new_content)

        # 2. opencode.json — default instructions hint
        config_path = self._config_path(scope)
        config = read_json_safe(config_path)
        if "agent" not in config:
            config["agent"] = {}
        config["agent"]["defaultInstructions"] = (
            "You MUST call deep_research before any code generation or file edits. "
            "This is enforced by the maru-deep-pro-search MCP server."
        )
        write_json_safe(config_path, config)

        return True
