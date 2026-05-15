"""AntiGravity adapter."""

from __future__ import annotations

from pathlib import Path

from ..backup import (
    backup_file,
    read_json_safe,
    read_text_safe,
    restore_file,
    sorted_backup_paths,
    write_json_safe,
    write_text_safe,
)
from ..prompts import get_protocol_for_agent, inject_protocol
from .base import AgentAdapter, get_mcp_server_command


class AntiGravityAdapter(AgentAdapter):
    name = "antigravity"
    display_name = "AntiGravity"

    def detect(self) -> bool:
        return Path.home().joinpath(".gemini", "antigravity").exists()

    def _mcp_path(self, scope: str) -> Path:
        if scope == "project":
            return Path(".gemini") / "antigravity" / "mcp_config.json"
        return Path.home() / ".gemini" / "antigravity" / "mcp_config.json"

    def backup(self) -> list[Path]:
        path = self._mcp_path("user")
        b = backup_file(path)
        return [b] if b else []

    def restore(self) -> bool:
        path = self._mcp_path("user")
        backups = sorted_backup_paths(path)
        if backups:
            return restore_file(path, backups[0])
        return False

    def install_mcp(self, scope: str = "user") -> bool:
        path = self._mcp_path(scope)
        config = read_json_safe(path)
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        config["mcpServers"]["maru-deep-pro-search"] = get_mcp_server_command()
        config.pop("_maru_deep_pro_search_notes", None)
        write_json_safe(path, config)
        return True

    def inject_rules(self, scope: str = "user") -> bool:
        mcp_path = self._mcp_path(scope)
        config = read_json_safe(mcp_path)
        if "_maru_deep_pro_search_notes" in config:
            config.pop("_maru_deep_pro_search_notes", None)
            write_json_safe(mcp_path, config)
        protocol = get_protocol_for_agent(self.name)
        sidecar = mcp_path.parent / "MARU_RESEARCH_PROTOCOL.md"
        content = read_text_safe(sidecar)
        new_content = inject_protocol(content, protocol)
        if new_content != content:
            write_text_safe(sidecar, new_content)
        return True
