"""JetBrains AI adapter — project rules and optional user marker file.

Official docs:
- https://www.jetbrains.com/help/ai-assistant/configure-project-rules.html
- https://www.jetbrains.com/help/ai-assistant/settings-reference-rules.html

Project rules belong in ``.aiassistant/rules/*.md`` at the project root (JetBrains
2026 docs). We never write free-form Markdown into ``.idea/ai-assistant.xml``,
which is IDE XML and must not be corrupted with protocol text.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..backup import (
    backup_file,
    read_text_safe,
    restore_file,
    sorted_backup_paths,
    write_text_safe,
)
from ..prompts import get_protocol_for_agent, inject_protocol
from .base import AgentAdapter


class JetBrainsAdapter(AgentAdapter):
    name = "jetbrains"
    display_name = "JetBrains AI"

    def detect(self) -> bool:
        home = Path.home()
        jetbrains_dirs = list(home.glob(".jetbrains*")) + list(
            home.glob("Library/Application Support/JetBrains*")
        )
        return bool(
            shutil.which("idea")
            or shutil.which("webstorm")
            or shutil.which("pycharm")
            or jetbrains_dirs
        )

    def _user_marker_path(self) -> Path:
        """Undocumented global marker — Markdown only."""
        return Path.home() / ".jetbrains-ai" / "maru-protocol.md"

    def _rules_dir(self, scope: str) -> Path:
        if scope == "project":
            return Path(".aiassistant") / "rules"
        return Path.home() / ".jetbrains-ai" / "rules"

    def _skills_dir(self, scope: str) -> Path | None:
        return self._rules_dir(scope)

    skills_format = "flat"

    def backup(self) -> list[Path]:
        paths = [self._user_marker_path()]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [self._user_marker_path()]:
            backups = sorted_backup_paths(p)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    def install_mcp(self, scope: str = "user") -> bool:
        # JetBrains AI does not natively support MCP servers yet.
        return self.inject_rules(scope)

    def inject_rules(self, scope: str = "user") -> bool:
        protocol = get_protocol_for_agent(self.name)

        rules_dir = self._rules_dir(scope)
        rules_dir.mkdir(parents=True, exist_ok=True)

        rule_file = rules_dir / "maru-research-protocol.md"
        rule_content = read_text_safe(rule_file)
        new_rule = inject_protocol(rule_content, protocol)
        if new_rule != rule_content:
            write_text_safe(rule_file, new_rule)

        if scope == "user":
            path = self._user_marker_path()
            content = read_text_safe(path)
            new_content = inject_protocol(content, protocol)
            if new_content != content:
                write_text_safe(path, new_content)

        return True
