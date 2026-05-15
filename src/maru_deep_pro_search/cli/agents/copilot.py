"""GitHub Copilot adapter — VS Code / GitHub Copilot custom instructions.

Workspace: ``.github/copilot-instructions.md`` (repository-wide).

User profile: ``~/.copilot/instructions/*.instructions.md`` per VS Code docs:
https://code.visualstudio.com/docs/copilot/customization/custom-instructions
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..backup import backup_file, read_text_safe, restore_file, sorted_backup_paths, write_text_safe
from ..prompts import get_protocol_for_agent, inject_protocol
from .base import AgentAdapter


class CopilotAdapter(AgentAdapter):
    name = "copilot"
    display_name = "GitHub Copilot"

    def detect(self) -> bool:
        return (
            shutil.which("code") is not None
            or shutil.which("gh") is not None
            or Path.home().joinpath(".vscode", "extensions").exists()
        )

    def _instructions_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".github") / "copilot-instructions.md"
        inst = Path.home() / ".copilot" / "instructions"
        return inst / "maru-research-protocol.instructions.md"

    def backup(self) -> list[Path]:
        path = self._instructions_path("user")
        b = backup_file(path)
        return [b] if b else []

    def restore(self) -> bool:
        path = self._instructions_path("user")
        backs = sorted_backup_paths(path)
        if backs:
            return restore_file(path, backs[0])
        return False

    def install_mcp(self, scope: str = "user") -> bool:
        return self.inject_rules(scope)

    def inject_rules(self, scope: str = "user") -> bool:
        path = self._instructions_path(scope)
        if scope == "user" or scope == "project":
            path.parent.mkdir(parents=True, exist_ok=True)

        protocol = get_protocol_for_agent(self.name)
        content = read_text_safe(path)
        new_content = inject_protocol(content, protocol)
        if new_content != content:
            write_text_safe(path, new_content)

        return True
