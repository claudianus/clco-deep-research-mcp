"""Shared helpers for idempotent agent config writes."""

from __future__ import annotations

from .prompts import text_has_research_protocol


def lines_contain(lines: list[str], needle: str) -> bool:
    """Return True if any line contains *needle*."""
    return any(needle in line for line in lines)


def lines_have_key_prefix(lines: list[str], key: str) -> bool:
    """Return True if any line starts with *key* (after strip), e.g. ``lint-cmd:``."""
    prefix = f"{key}:"
    return any(line.strip().startswith(prefix) for line in lines)


def yaml_rule_has_protocol(rule: object) -> bool:
    """True if a Continue-style YAML ``rules`` list entry carries our protocol."""
    return isinstance(rule, str) and text_has_research_protocol(rule)
