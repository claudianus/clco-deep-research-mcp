"""Shared helpers for classifying MCP tool return strings."""

from __future__ import annotations


def is_successful_tool_result(result: object) -> bool:
    """True when a tool returned non-empty output that is not a gate/query failure."""
    if not isinstance(result, str) or not result.strip():
        return False
    head = result[:500].lower()
    failure_markers = (
        "## [query rejected]",
        "## [blocked]",
        "error executing tool",
        "[maru-research-gate]",
        "research gate not unlocked",
        "gate not unlocked",
    )
    return not any(marker in head for marker in failure_markers)
