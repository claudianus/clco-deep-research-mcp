"""Claude Code adapter."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .base import AgentAdapter
from ..backup import (
    backup_file,
    read_json_safe,
    read_text_safe,
    restore_file,
    write_json_safe,
    write_text_safe,
)
from ..prompts import get_protocol_for_agent


class ClaudeAdapter(AgentAdapter):
    name = "claude"
    display_name = "Claude Code"

    # ── detect ──────────────────────────────────────────────
    def detect(self) -> bool:
        return (
            shutil.which("claude") is not None
            or Path.home().joinpath(".claude.json").exists()
            or Path.home().joinpath(".claude").exists()
        )

    # ── paths ───────────────────────────────────────────────
    def _mcp_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".mcp.json")
        return Path.home() / ".claude.json"

    def _settings_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".claude") / "settings.json"
        return Path.home() / ".claude" / "settings.json"

    # ── backup ──────────────────────────────────────────────
    def backup(self) -> list[Path]:
        paths = [self._mcp_path("user"), self._settings_path("user")]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        mcp = self._mcp_path("user")
        settings = self._settings_path("user")
        restored = False
        for p in [mcp, settings]:
            # Find most recent backup
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    # ── install MCP ─────────────────────────────────────────
    def install_mcp(self, scope: str = "user") -> bool:
        path = self._mcp_path(scope)
        config = read_json_safe(path)
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"]["maru-deep-pro-search"] = {
            "command": "python3",
            "args": ["-m", "maru_deep_pro_search.server"],
            "env": {},
        }
        write_json_safe(path, config)
        return True

    # ── inject rules ────────────────────────────────────────
    def inject_rules(self, scope: str = "user") -> bool:
        path = self._settings_path(scope)
        config: dict[str, Any] = read_json_safe(path)
        if "systemPrompt" not in config:
            config["systemPrompt"] = ""

        protocol = get_protocol_for_agent(self.name)
        if protocol in config["systemPrompt"]:
            return True  # Already injected

        config["systemPrompt"] += f"\n\n{protocol}"
        write_json_safe(path, config)
        return True
