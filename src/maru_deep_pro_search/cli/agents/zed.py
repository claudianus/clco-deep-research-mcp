"""Zed editor adapter — supports .zed/settings.json and assistant rules."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

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


class ZedAdapter(AgentAdapter):
    name = "zed"
    display_name = "Zed"

    def detect(self) -> bool:
        return (
            shutil.which("zed") is not None
            or Path.home().joinpath(".config", "zed").exists()
            or Path.home().joinpath(".zed").exists()
        )

    def _settings_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".zed") / "settings.json"
        return Path.home() / ".config" / "zed" / "settings.json"

    def _assistant_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".zed") / "assistant.md"
        return Path.home() / ".config" / "zed" / "assistant.md"

    def backup(self) -> list[Path]:
        paths = [self._settings_path("user"), self._assistant_path("user")]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [self._settings_path("user"), self._assistant_path("user")]:
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    def install_mcp(self, scope: str = "user") -> bool:
        path = self._settings_path(scope)
        config: dict[str, Any] = read_json_safe(path)

        if "assistant" not in config:
            config["assistant"] = {}
        if "default_model" not in config["assistant"]:
            config["assistant"]["default_model"] = {
                "provider": "zed",
                "model": "claude-3-7-sonnet-latest",
            }

        # Zed does not natively support MCP servers yet (as of 2025-01),
        # but we can document the intent in settings for when it does.
        if "lsp" not in config:
            config["lsp"] = {}

        write_json_safe(path, config)
        return True

    def inject_rules(self, scope: str = "user") -> bool:
        # Zed uses assistant.md for system prompt injection
        md_path = self._assistant_path(scope)
        protocol = get_protocol_for_agent(self.name)
        content = read_text_safe(md_path)

        if protocol not in content:
            header = "# maru-deep-pro-search Research Protocol\n\n"
            write_text_safe(md_path, content + "\n\n" + header + protocol + "\n")
        return True
