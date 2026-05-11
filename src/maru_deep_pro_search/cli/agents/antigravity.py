"""AntiGravity adapter."""

from __future__ import annotations

from pathlib import Path

from ..backup import backup_file, read_json_safe, restore_file, write_json_safe
from ..prompts import get_protocol_for_agent
from .base import AgentAdapter


class AntiGravityAdapter(AgentAdapter):
    name = "antigravity"
    display_name = "AntiGravity"

    def detect(self) -> bool:
        return Path.home().joinpath(".gemini", "antigravity").exists()

    def _mcp_path(self, scope: str) -> Path:
        return Path.home() / ".gemini" / "antigravity" / "mcp_config.json"

    def backup(self) -> list[Path]:
        path = self._mcp_path("user")
        b = backup_file(path)
        return [b] if b else []

    def restore(self) -> bool:
        path = self._mcp_path("user")
        backups = sorted(path.parent.glob(f"{path.name}.bak.*"), reverse=True)
        if backups:
            return restore_file(path, backups[0])
        return False

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
        # AntiGravity has limited programmatic rule injection.
        # We inject a comment/header in the mcp_config.json as a fallback,
        # and print a manual instruction for the user.
        path = self._mcp_path(scope)
        config = read_json_safe(path)
        protocol = get_protocol_for_agent(self.name)

        # Store protocol in a custom key that won't break MCP
        config.setdefault("_maru_deep_pro_search_notes", {})
        config["_maru_deep_pro_search_notes"]["research_protocol"] = protocol
        write_json_safe(path, config)

        # AntiGravity doesn't have a direct system prompt file we can edit.
        # Return False to signal that manual steps may be needed.
        return False
