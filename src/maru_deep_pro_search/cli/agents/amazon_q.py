"""Amazon Q Developer adapter — supports AWS IDE integrations."""

from __future__ import annotations

import shutil
from pathlib import Path

from ..backup import backup_file, read_json_safe, read_text_safe, restore_file, write_json_safe, write_text_safe
from ..prompts import get_protocol_for_agent, inject_protocol
from .base import AgentAdapter


class AmazonQAdapter(AgentAdapter):
    name = "amazon_q"
    display_name = "Amazon Q Developer"

    def detect(self) -> bool:
        return (
            shutil.which("q") is not None
            or Path.home().joinpath(".aws", "amazonq").exists()
            or any(
                p.name.startswith("amazon-q")
                for p in Path.home().joinpath(".vscode", "extensions").iterdir()
                if p.is_dir()
            )
            if Path.home().joinpath(".vscode", "extensions").exists()
            else False
        )

    def _prompts_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".amazonq") / "prompts.md"
        return Path.home() / ".amazonq" / "prompts.md"

    def _config_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".amazonq") / "config.json"
        return Path.home() / ".amazonq" / "config.json"

    def backup(self) -> list[Path]:
        paths = [self._prompts_path("user")]
        backups = [backup_file(p) for p in paths]
        return [b for b in backups if b is not None]

    def restore(self) -> bool:
        restored = False
        for p in [self._prompts_path("user")]:
            backups = sorted(p.parent.glob(f"{p.name}.bak.*"), reverse=True)
            if backups:
                restored = restore_file(p, backups[0]) or restored
        return restored

    def install_mcp(self, scope: str = "user") -> bool:
        # Amazon Q does not natively support MCP yet.
        return self.inject_rules(scope)

    def inject_rules(self, scope: str = "user") -> bool:
        # 1. prompts.md
        path = self._prompts_path(scope)
        protocol = get_protocol_for_agent(self.name)
        content = read_text_safe(path)
        new_content = inject_protocol(content, protocol)
        if new_content != content:
            write_text_safe(path, new_content)

        # 2. config.json — hint for future Amazon Q versions
        config_path = self._config_path(scope)
        config = read_json_safe(config_path)
        if "instructions" not in config:
            config["instructions"] = {}
        config["instructions"]["research_first"] = (
            "You MUST call deep_research before any code generation or file edits. "
            "This is enforced by the maru-deep-pro-search MCP server."
        )
        write_json_safe(config_path, config)

        return True
