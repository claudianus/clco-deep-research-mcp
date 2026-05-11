"""Claude Code adapter — supports .claude/settings.json, CLAUDE.md, commands/, hooks."""

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

    # ── detect ──────────────────────────────────────────────────
    def detect(self) -> bool:
        return (
            shutil.which("claude") is not None
            or Path.home().joinpath(".claude").exists()
        )

    # ── paths (2025 layout) ─────────────────────────────────────
    def _mcp_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".mcp.json")
        return Path.home() / ".claude" / ".mcp.json"

    def _settings_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".claude") / "settings.json"
        return Path.home() / ".claude" / "settings.json"

    def _claude_md_path(self, scope: str) -> Path:
        if scope == "project":
            return Path("CLAUDE.md")
        return Path.home() / ".claude" / "CLAUDE.md"

    def _commands_dir(self, scope: str) -> Path:
        if scope == "project":
            return Path(".claude") / "commands"
        return Path.home() / ".claude" / "commands"

    # ── backup ──────────────────────────────────────────────────
    def backup(self) -> list[Path]:
        paths = [
            self._mcp_path("user"),
            self._settings_path("user"),
            self._claude_md_path("user"),
        ]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [
            self._mcp_path("user"),
            self._settings_path("user"),
            self._claude_md_path("user"),
        ]:
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    # ── install MCP ─────────────────────────────────────────────
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

        # Also write .claude/settings.json with hooks
        self._write_settings(scope)
        return True

    # ── inject rules ────────────────────────────────────────────
    def inject_rules(self, scope: str = "user") -> bool:
        # 1. CLAUDE.md
        md_path = self._claude_md_path(scope)
        protocol = get_protocol_for_agent(self.name)
        content = read_text_safe(md_path)

        if protocol in content:
            pass  # Already present
        else:
            write_text_safe(md_path, content + "\n\n" + protocol + "\n")

        # 2. Custom commands
        self._write_commands(scope)
        return True

    # ── helpers ─────────────────────────────────────────────────
    def _write_settings(self, scope: str) -> None:
        path = self._settings_path(scope)
        settings: dict[str, Any] = read_json_safe(path)

        # Ensure hooks structure
        if "hooks" not in settings:
            settings["hooks"] = {}
        if "PostToolUse" not in settings["hooks"]:
            settings["hooks"]["PostToolUse"] = []

        # Add research verification hook (avoid duplicates)
        existing_matchers = [
            h.get("matcher", "") for h in settings["hooks"]["PostToolUse"]
        ]
        if "Write|Edit" not in existing_matchers:
            settings["hooks"]["PostToolUse"].append({
                "matcher": "Write|Edit",
                "hooks": [
                    {
                        "type": "prompt",
                        "prompt": (
                            "You just wrote or edited code. "
                            "Verify that all API references and library versions "
                            "are backed by research citations [1], [2]. "
                            "If not, STOP and call deep_research before continuing."
                        ),
                    }
                ],
            })

        write_json_safe(path, settings)

    def _write_commands(self, scope: str) -> None:
        cmds_dir = self._commands_dir(scope)
        cmds_dir.mkdir(parents=True, exist_ok=True)

        commands = {
            "research.md": (
                "# /research — Deep research with citations\n\n"
                "Call `deep_research` with the user's current technical intent "
                "and return a synthesized answer with inline citations [1], [2]."
            ),
            "verify.md": (
                "# /verify — Verify code against research\n\n"
                "Review the most recent code changes against the knowledge store. "
                "Confirm all API signatures, versions, and security advice match "
                "the research results. Flag any discrepancies."
            ),
        }

        for filename, content in commands.items():
            cmd_path = cmds_dir / filename
            if not cmd_path.exists():
                cmd_path.write_text(content, encoding="utf-8")
