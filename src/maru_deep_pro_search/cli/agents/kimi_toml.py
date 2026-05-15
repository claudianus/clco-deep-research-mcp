"""Idempotent TOML edits for Kimi ``config.toml``."""

from __future__ import annotations

import re

KIMI_SYSTEM_MARKER = "# MARU-SYSTEM-PROMPT"
KIMI_HOOK_MARKER = "# MARU-KIMI-HOOK"

_SYSTEM_BLOCK_RE = re.compile(
    re.escape(KIMI_SYSTEM_MARKER) + r"\nsystem_prompt = \"\"\".*?\"\"\"",
    re.DOTALL,
)
_HOOK_BLOCK_RE = re.compile(
    re.escape(KIMI_HOOK_MARKER) + r"\n\[\[hooks\]\].*?(?=\n# |\n\[\[hooks\]\]|\Z)",
    re.DOTALL,
)


def upsert_kimi_system_prompt(text: str, protocol: str) -> str:
    """Insert or replace the MARU-managed ``system_prompt`` block."""
    block = f'{KIMI_SYSTEM_MARKER}\nsystem_prompt = """\n{protocol.strip()}\n"""'
    if KIMI_SYSTEM_MARKER in text:
        return _SYSTEM_BLOCK_RE.sub(block, text)
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("system_prompt")]
    base = "\n".join(lines).rstrip()
    return f"{base}\n\n{block}\n" if base else f"{block}\n"


def upsert_kimi_hook_block(text: str, hook_block: str) -> str:
    """Insert or replace the MARU PreToolUse hook (no duplicate ``[[hooks]]``)."""
    if "kimi_research_gate.py" in text and KIMI_HOOK_MARKER not in text:
        return text
    block = f"{KIMI_HOOK_MARKER}\n{hook_block.strip()}"
    if KIMI_HOOK_MARKER in text:
        return _HOOK_BLOCK_RE.sub(block, text)
    return f"{text.rstrip()}\n\n{block}\n"
