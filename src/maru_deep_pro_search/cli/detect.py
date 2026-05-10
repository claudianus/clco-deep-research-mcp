"""Auto-detect installed AI agents on the user's machine."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Callable


AgentDetector = Callable[[], bool]


# ── Claude Code ──────────────────────────────────────────────
def _detect_claude_code() -> bool:
    return (
        shutil.which("claude") is not None
        or Path.home().joinpath(".claude.json").exists()
        or Path.home().joinpath(".claude").exists()
    )


# ── Cursor ───────────────────────────────────────────────────
def _detect_cursor() -> bool:
    return (
        Path.home().joinpath(".cursor").exists()
        or Path(".cursor").exists()
        or shutil.which("cursor") is not None
    )


# ── Kimi Code CLI ────────────────────────────────────────────
def _detect_kimi() -> bool:
    return (
        shutil.which("kimi") is not None
        or Path.home().joinpath(".kimi").exists()
    )


# ── AntiGravity ──────────────────────────────────────────────
def _detect_antigravity() -> bool:
    return Path.home().joinpath(".gemini", "antigravity").exists()


# ── Kilo Code ────────────────────────────────────────────────
def _detect_kilo() -> bool:
    return (
        Path.home().joinpath(".config", "kilo").exists()
        or shutil.which("kilo") is not None
    )


# ── OpenCode ─────────────────────────────────────────────────
def _detect_opencode() -> bool:
    return (
        shutil.which("opencode") is not None
        or Path.home().joinpath(".config", "opencode").exists()
    )


# ── Windsurf ─────────────────────────────────────────────────
def _detect_windsurf() -> bool:
    return (
        Path(".windsurf").exists()
        or Path.home().joinpath(".windsurf").exists()
        or shutil.which("windsurf") is not None
    )


# ── Registry ─────────────────────────────────────────────────
AGENT_DETECTORS: dict[str, AgentDetector] = {
    "claude": _detect_claude_code,
    "cursor": _detect_cursor,
    "kimi": _detect_kimi,
    "antigravity": _detect_antigravity,
    "kilo": _detect_kilo,
    "opencode": _detect_opencode,
    "windsurf": _detect_windsurf,
}


def detect_agents() -> dict[str, bool]:
    """Return a map of agent_name -> installed for all known agents."""
    return {name: fn() for name, fn in AGENT_DETECTORS.items()}


def installed_agents() -> list[str]:
    """Return only the names of agents that are installed."""
    return [name for name, detected in detect_agents().items() if detected]
