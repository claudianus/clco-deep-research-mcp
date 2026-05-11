"""Aider adapter — terminal-first AI coding agent with deep git integration."""

from __future__ import annotations

import shutil
from pathlib import Path

from .base import AgentAdapter
from ..backup import backup_file, read_text_safe, restore_file, write_text_safe
from ..prompts import get_protocol_for_agent


class AiderAdapter(AgentAdapter):
    name = "aider"
    display_name = "Aider"

    def detect(self) -> bool:
        return shutil.which("aider") is not None

    # ── paths ────────────────────────────────────────────────────
    def _conventions_path(self, scope: str) -> Path:
        if scope == "project":
            return Path("CONVENTIONS.md")
        return Path.home() / ".aider" / "CONVENTIONS.md"

    def _config_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".aider.conf.yml")
        return Path.home() / ".aider.conf.yml"

    def _ignore_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".aiderignore")
        return Path.home() / ".aiderignore"

    # ── backup ───────────────────────────────────────────────────
    def backup(self) -> list[Path]:
        paths = [
            self._conventions_path("user"),
            self._config_path("user"),
        ]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [
            self._conventions_path("user"),
            self._config_path("user"),
        ]:
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    # ── install MCP (Aider doesn't use MCP natively, but we register via conventions) ──
    def install_mcp(self, scope: str = "user") -> bool:
        # Aider uses CONVENTIONS.md for tool guidance, not MCP.
        # We inject research protocol as conventions.
        return self.inject_rules(scope)

    # ── inject rules ─────────────────────────────────────────────
    def inject_rules(self, scope: str = "user") -> bool:
        # 1. CONVENTIONS.md
        conv_path = self._conventions_path(scope)
        protocol = get_protocol_for_agent(self.name)

        content = read_text_safe(conv_path)
        if protocol in content:
            return True

        header = "# maru-deep-pro-search Research Protocol\n\n"
        new_content = content + "\n\n" + header + protocol + "\n"
        write_text_safe(conv_path, new_content)

        # 2. .aider.conf.yml
        config_path = self._config_path(scope)
        config_lines = read_text_safe(config_path).splitlines()

        # Ensure read: CONVENTIONS.md is present
        has_read = any("CONVENTIONS.md" in line for line in config_lines)
        if not has_read:
            config_lines.append('read: CONVENTIONS.md')

        # Ensure auto-lint and auto-test hooks (lightweight defaults)
        has_lint = any("auto-lint" in line for line in config_lines)
        if not has_lint:
            config_lines.append("auto-lint: true")

        write_text_safe(config_path, "\n".join(config_lines) + "\n")

        # 3. .aiderignore — exclude harness artifacts
        ignore_path = self._ignore_path(scope)
        ignore_content = read_text_safe(ignore_path)
        maru_ignore = "# maru harness\n.maru/knowledge.db\n.maru/knowledge.db-journal\n.maru/*.bak\n"
        if ".maru/" not in ignore_content:
            write_text_safe(ignore_path, ignore_content + "\n" + maru_ignore)

        return True
