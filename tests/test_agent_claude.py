"""Tests for Claude Code agent adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from maru_deep_pro_search.cli.agents.claude import ClaudeAdapter


class TestDetect:
    def test_detected_via_binary(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(
            "shutil.which", lambda cmd: "/usr/bin/claude" if cmd == "claude" else None
        )
        assert ClaudeAdapter().detect() is True

    def test_detected_via_home_dir(self, monkeypatch: Any, tmp_path: Path) -> None:
        monkeypatch.setattr("shutil.which", lambda _cmd: None)
        (tmp_path / ".claude").mkdir()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert ClaudeAdapter().detect() is True

    def test_not_detected(self, monkeypatch: Any, tmp_path: Path) -> None:
        monkeypatch.setattr("shutil.which", lambda _cmd: None)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert ClaudeAdapter().detect() is False


class TestPaths:
    def test_mcp_user(self) -> None:
        p = ClaudeAdapter()._mcp_path("user")
        assert p.name == ".mcp.json"

    def test_mcp_project(self) -> None:
        p = ClaudeAdapter()._mcp_path("project")
        assert p == Path(".mcp.json")

    def test_settings_user(self) -> None:
        p = ClaudeAdapter()._settings_path("user")
        assert p.name == "settings.json"

    def test_settings_project(self) -> None:
        p = ClaudeAdapter()._settings_path("project")
        assert p == Path(".claude") / "settings.json"

    def test_claude_md_user(self) -> None:
        p = ClaudeAdapter()._claude_md_path("user")
        assert p.name == "CLAUDE.md"

    def test_claude_md_project(self) -> None:
        p = ClaudeAdapter()._claude_md_path("project")
        assert p == Path("CLAUDE.md")

    def test_commands_dir_user(self) -> None:
        p = ClaudeAdapter()._commands_dir("user")
        assert p.name == "commands"

    def test_commands_dir_project(self) -> None:
        p = ClaudeAdapter()._commands_dir("project")
        assert p == Path(".claude") / "commands"

    def test_skills_dir_user(self) -> None:
        p = ClaudeAdapter()._skills_dir("user")
        assert p is not None
        assert p.name == "skills"

    def test_skills_dir_project(self) -> None:
        p = ClaudeAdapter()._skills_dir("project")
        assert p is not None
        assert p == Path(".claude") / "skills"


class TestBackupRestore:
    def test_backup(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        mcp = tmp_path / ".mcp.json"
        mcp.touch()
        settings = tmp_path / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.touch()
        md = tmp_path / "CLAUDE.md"
        md.touch()

        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.backup_file",
            lambda _p: tmp_path / "bak.0",
        )
        assert len(adapter.backup()) == 3

    def test_backup_skips_none(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.backup_file",
            lambda _p: None,
        )
        assert adapter.backup() == []

    def test_restore_no_backups(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert adapter.restore() is False

    def test_restore_with_backups(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        mcp = tmp_path / ".claude" / ".mcp.json"
        mcp.parent.mkdir(parents=True)
        mcp.touch()
        (mcp.parent / ".mcp.json.bak.0").touch()

        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.restore_file",
            lambda _orig, _bak: True,
        )
        assert adapter.restore() is True


class TestInstallMcp:
    def test_install_mcp_user(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.read_json_safe",
            lambda _p: {},
        )
        written: dict[str, Any] = {}
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.write_json_safe",
            lambda p, data: written.update({str(p): data}),
        )
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.get_mcp_server_command",
            lambda: {"command": "python", "args": ["-m", "maru"]},
        )
        assert adapter.install_mcp("user") is True
        mcp_key = str(tmp_path / ".claude" / ".mcp.json")
        settings_key = str(tmp_path / ".claude" / "settings.json")
        assert mcp_key in written
        assert settings_key in written
        cfg = written[mcp_key]
        assert "maru-deep-pro-search" in cfg["mcpServers"]


class TestInjectRules:
    def test_inject_rules_user(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.read_text_safe",
            lambda _p: "",
        )
        text_written: dict[str, str] = {}
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.write_text_safe",
            lambda p, data: text_written.update({str(p): data}),
        )
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.get_protocol_for_agent",
            lambda _name: "# PROTOCOL",
        )
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.inject_protocol",
            lambda _content, _protocol: "# PROTOCOL\n",
        )
        assert adapter.inject_rules("user") is True
        assert any("CLAUDE.md" in k for k in text_written)
        assert (tmp_path / ".claude" / "hooks" / "maru_research_gate.py").exists()
        assert (tmp_path / ".claude" / "hooks" / "maru_research_revert.py").exists()
        assert (tmp_path / ".claude" / "hooks" / "maru_session_start.py").exists()
        assert (tmp_path / ".claude" / "commands" / "research.md").exists()
        assert (tmp_path / ".claude" / "commands" / "verify.md").exists()

    def test_inject_rules_idempotent(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.read_text_safe",
            lambda _p: "# PROTOCOL\n",
        )
        text_written: dict[str, str] = {}
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.write_text_safe",
            lambda p, data: text_written.update({str(p): data}),
        )
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.get_protocol_for_agent",
            lambda _name: "# PROTOCOL",
        )
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.inject_protocol",
            lambda content, _protocol: content,
        )
        assert adapter.inject_rules("user") is True
        assert len(text_written) == 0

    def test_inject_rules_skips_existing_hooks_and_commands(
        self, monkeypatch: Any, tmp_path: Path
    ) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        hooks = tmp_path / ".claude" / "hooks"
        hooks.mkdir(parents=True)
        (hooks / "maru_research_gate.py").touch()
        (hooks / "maru_research_revert.py").touch()
        (hooks / "maru_session_start.py").touch()
        cmds = tmp_path / ".claude" / "commands"
        cmds.mkdir(parents=True)
        (cmds / "research.md").touch()
        (cmds / "verify.md").touch()

        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.read_text_safe",
            lambda _p: "",
        )
        text_written: dict[str, str] = {}
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.write_text_safe",
            lambda p, data: text_written.update({str(p): data}),
        )
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.get_protocol_for_agent",
            lambda _name: "# PROTOCOL",
        )
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.inject_protocol",
            lambda _content, _protocol: "# PROTOCOL\n",
        )
        assert adapter.inject_rules("user") is True
        assert len(text_written) == 1
        assert "CLAUDE.md" in list(text_written.keys())[0]


class TestWriteSettings:
    def test_write_settings_fresh(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.read_json_safe",
            lambda _p: {},
        )
        written: dict[str, Any] = {}
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.write_json_safe",
            lambda p, data: written.update({str(p): data}),
        )
        adapter._write_settings("user")
        cfg = written[str(tmp_path / ".claude" / "settings.json")]
        assert "hooks" in cfg
        assert "PreToolUse" in cfg["hooks"]
        assert "PostToolUse" in cfg["hooks"]
        assert "SessionStart" in cfg["hooks"]
        assert "UserPromptSubmit" in cfg["hooks"]
        assert "permissions" in cfg
        assert "rm -rf /*" in cfg["permissions"]["deny"]

    def test_write_settings_idempotent(self, monkeypatch: Any, tmp_path: Path) -> None:
        adapter = ClaudeAdapter()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        existing = {
            "hooks": {
                "PreToolUse": [{"matcher": "Edit|Write", "hooks": []}],
                "PostToolUse": [{"matcher": "Write|Edit", "hooks": []}],
                "SessionStart": [{"matcher": "*", "hooks": []}],
                "UserPromptSubmit": [{"matcher": "*", "hooks": []}],
            },
            "permissions": {"deny": ["rm -rf /*"]},
        }
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.read_json_safe",
            lambda _p: existing,
        )
        written: dict[str, Any] = {}
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.agents.claude.write_json_safe",
            lambda p, data: written.update({str(p): data}),
        )
        adapter._write_settings("user")
        cfg = written[str(tmp_path / ".claude" / "settings.json")]
        assert len(cfg["hooks"]["PreToolUse"]) == 1
        assert len(cfg["permissions"]["deny"]) == 4
