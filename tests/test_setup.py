"""Tests for the setup CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from maru_deep_pro_search.cli.setup import (
    ADAPTER_REGISTRY,
    cmd_check,
    cmd_list,
    cmd_restore,
    cmd_setup,
    main,
)


@pytest.fixture(autouse=True)
def _mock_python_compat(monkeypatch: Any) -> None:
    """Always pass Python version check."""
    monkeypatch.setattr(
        "maru_deep_pro_search.cli.setup.ensure_compatible_python",
        lambda: 0,
    )


@pytest.fixture
def mock_adapter(monkeypatch: Any) -> MagicMock:
    """Return a reusable mock adapter class."""
    cls = MagicMock()
    inst = cls.return_value
    inst.display_name = "MockAgent"
    inst.configure.return_value = {
        "backups": [],
        "mcp_installed": True,
        "rules_injected": True,
    }
    inst.detect.return_value = True
    inst.restore.return_value = True
    inst.install_mcp.return_value = True
    monkeypatch.setitem(ADAPTER_REGISTRY, "mock", cls)
    return cls


class TestCmdList:
    def test_lists_detected_and_missing(self, monkeypatch: Any, capsys: Any) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"claude": True, "cursor": False},
        )
        args = MagicMock()
        assert cmd_list(args) == 0
        captured = capsys.readouterr()
        assert "Claude" in captured.out
        assert "Cursor" in captured.out


class TestCmdSetup:
    def test_no_agents_found(self, monkeypatch: Any, capsys: Any) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"claude": False},
        )
        args = MagicMock()
        args.agents = None
        args.scope = "user"
        assert cmd_setup(args) == 1
        captured = capsys.readouterr()
        assert "찾을 수 없습니다" in captured.out

    def test_selected_not_installed(self, monkeypatch: Any, capsys: Any) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"claude": False},
        )
        args = MagicMock()
        args.agents = ["claude"]
        args.scope = "user"
        assert cmd_setup(args) == 1
        captured = capsys.readouterr()
        # When no agents are installed at all, early return happens before filtering
        assert "찾을 수 없습니다" in captured.out

    def test_setup_success(self, monkeypatch: Any, capsys: Any, mock_adapter: MagicMock) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        args = MagicMock()
        args.agents = None
        args.scope = "user"
        assert cmd_setup(args) == 0
        captured = capsys.readouterr()
        assert "완료" in captured.out
        mock_adapter.return_value.configure.assert_called_once_with(scope="user")

    def test_setup_with_skills(
        self, monkeypatch: Any, capsys: Any, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.return_value.configure.return_value = {
            "backups": [Path("/tmp/bak")],
            "mcp_installed": True,
            "rules_injected": True,
            "skills_installed": True,
            "skills_supported": True,
        }
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        args = MagicMock()
        args.agents = None
        args.scope = "user"
        assert cmd_setup(args) == 0
        captured = capsys.readouterr()
        assert "SKILL.md" in captured.out


class TestCmdRestore:
    def test_restore_success(self, monkeypatch: Any, capsys: Any, mock_adapter: MagicMock) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        args = MagicMock()
        assert cmd_restore(args) == 0
        captured = capsys.readouterr()
        assert "복원 완료" in captured.out
        mock_adapter.return_value.restore.assert_called_once()

    def test_restore_no_backups(
        self, monkeypatch: Any, capsys: Any, mock_adapter: MagicMock
    ) -> None:
        mock_adapter.return_value.restore.return_value = False
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        args = MagicMock()
        assert cmd_restore(args) == 0
        captured = capsys.readouterr()
        assert "복원할 백업" in captured.out or "복원 완료" in captured.out


class TestCmdCheck:
    def test_check_all_ok(self, monkeypatch: Any, capsys: Any, mock_adapter: MagicMock) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        args = MagicMock()
        assert cmd_check(args) == 0
        captured = capsys.readouterr()
        assert "MockAgent" in captured.out

    def test_check_some_fail(self, monkeypatch: Any, capsys: Any, mock_adapter: MagicMock) -> None:
        mock_adapter.return_value.install_mcp.return_value = False
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        args = MagicMock()
        assert cmd_check(args) == 1
        captured = capsys.readouterr()
        assert "MockAgent" in captured.out


class TestMain:
    def test_list_subcommand(self, monkeypatch: Any, capsys: Any) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"claude": True},
        )
        assert main(["setup", "--list"]) == 0
        captured = capsys.readouterr()
        assert "Claude" in captured.out

    def test_restore_subcommand(self, monkeypatch: Any, capsys: Any) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        assert main(["setup", "--restore"]) == 0

    def test_check_subcommand(self, monkeypatch: Any, capsys: Any) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        assert main(["setup", "--check"]) == 0

    def test_default_setup(self, monkeypatch: Any, capsys: Any, mock_adapter: MagicMock) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.detect_agents",
            lambda: {"mock": True},
        )
        assert main(["setup"]) == 0

    def test_python_incompatible(self, monkeypatch: Any) -> None:
        monkeypatch.setattr(
            "maru_deep_pro_search.cli.setup.ensure_compatible_python",
            lambda: 1,
        )
        assert main([]) == 1
