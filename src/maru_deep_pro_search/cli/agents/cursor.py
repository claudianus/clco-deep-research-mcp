"""Cursor adapter — supports .cursorrules, .cursor/mcp.json, settings, commands."""

from __future__ import annotations

import shutil
from pathlib import Path

from .base import AgentAdapter
from ..backup import backup_file, read_json_safe, read_text_safe, restore_file, write_json_safe, write_text_safe
from ..prompts import get_protocol_for_agent


class CursorAdapter(AgentAdapter):
    name = "cursor"
    display_name = "Cursor"

    def detect(self) -> bool:
        return (
            Path.home().joinpath(".cursor").exists()
            or Path(".cursor").exists()
            or shutil.which("cursor") is not None
        )

    def _mcp_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".cursor") / "mcp.json"
        return Path.home() / ".cursor" / "mcp.json"

    def _rules_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".cursorrules")
        return Path.home() / ".cursorrules"

    def _settings_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".cursor") / "settings.json"
        return Path.home() / ".cursor" / "settings.json"

    def _commands_dir(self, scope: str) -> Path:
        if scope == "project":
            return Path(".cursor") / "commands"
        return Path.home() / ".cursor" / "commands"

    def backup(self) -> list[Path]:
        paths = [self._mcp_path("user"), self._rules_path("user"), self._settings_path("user")]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [self._mcp_path("user"), self._rules_path("user"), self._settings_path("user")]:
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
        # 1. .cursorrules
        rules_path = self._rules_path(scope)
        content = read_text_safe(rules_path)
        protocol = get_protocol_for_agent(self.name)

        if protocol not in content:
            content += f"\n\n# maru-deep-pro-search Research Protocol\n{protocol}\n"
            write_text_safe(rules_path, content)

        # 2. .cursor/settings.json — enable MCP tools by default
        settings_path = self._settings_path(scope)
        settings = read_json_safe(settings_path)
        if "mcp" not in settings:
            settings["mcp"] = {}
        if "autoEnableTools" not in settings["mcp"]:
            settings["mcp"]["autoEnableTools"] = True
        write_json_safe(settings_path, settings)

        # 3. Cursor commands (if supported in future versions)
        cmds_dir = self._commands_dir(scope)
        cmds_dir.mkdir(parents=True, exist_ok=True)
        return True
