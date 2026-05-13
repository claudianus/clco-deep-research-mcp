"""GitHub Copilot adapter — VS Code / GitHub Copilot custom instructions."""

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
from .base import AgentAdapter


class CopilotAdapter(AgentAdapter):
    name = "copilot"
    display_name = "GitHub Copilot"

    def detect(self) -> bool:
        # VS Code with Copilot extension, or Copilot CLI
        return (
            shutil.which("code") is not None
            or shutil.which("gh") is not None
            or Path.home().joinpath(".vscode", "extensions").exists()
        )

    def _instructions_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".github") / "copilot-instructions.md"
        return Path.home() / ".github" / "copilot-instructions.md"

    def _settings_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".github") / "copilot-settings.json"
        return Path.home() / ".github" / "copilot-settings.json"

    def backup(self) -> list[Path]:
        path = self._instructions_path("user")
        b = backup_file(path)
        return [b] if b else []

    def restore(self) -> bool:
        path = self._instructions_path("user")
        backups = sorted(path.parent.glob(f"{path.name}.bak.*"), reverse=True)
        if backups:
            return restore_file(path, backups[0])
        return False

    def install_mcp(self, scope: str = "user") -> bool:
        # Copilot doesn't support MCP yet (as of 2025).
        # We inject rules only.
        return self.inject_rules(scope)

    def inject_rules(self, scope: str = "user") -> bool:
        # 1. copilot-instructions.md
        path = self._instructions_path(scope)
        protocol = get_protocol_for_agent(self.name)

        content = read_text_safe(path)
        new_content = inject_protocol(content, protocol)
        if new_content != content:
            write_text_safe(path, new_content)

        # 2. copilot-settings.json — hint for future Copilot versions
        settings_path = self._settings_path(scope)
        settings = read_json_safe(settings_path)
        if "instructions" not in settings:
            settings["instructions"] = {}
        settings["instructions"]["research_first"] = (
            "You MUST call deep_research before any code generation or file edits. "
            "This is enforced by the maru-deep-pro-search MCP server."
        )
        write_json_safe(settings_path, settings)

        return True
