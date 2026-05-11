"""GitHub Copilot adapter — VS Code / GitHub Copilot custom instructions."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..backup import backup_file, read_text_safe, restore_file, write_text_safe
from ..prompts import get_protocol_for_agent
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
        path = self._instructions_path(scope)
        protocol = get_protocol_for_agent(self.name)

        content = read_text_safe(path)
        if protocol in content:
            return True

        write_text_safe(path, content + "\n\n# maru-deep-pro-search Research Protocol\n\n" + protocol + "\n")
        return True
