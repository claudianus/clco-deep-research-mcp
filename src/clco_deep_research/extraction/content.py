"""Content extraction utilities with quality assessment."""

from __future__ import annotations

import re


def truncate_for_llm(text: str, max_tokens_approx: int = 2000) -> str:
    """Truncate text to roughly max_tokens_approx (4 chars ≈ 1 token), at a clean boundary."""
    max_chars = max_tokens_approx * 4
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]

    # Try paragraph boundary
    last_para = truncated.rfind("\n\n")
    if last_para > max_chars * 0.5:
        return truncated[:last_para].strip()

    # Try sentence boundary
    last_sent = max(
        truncated.rfind(". "),
        truncated.rfind(".\n"),
        truncated.rfind("! "),
        truncated.rfind("? "),
    )
    if last_sent > max_chars * 0.5:
        return truncated[:last_sent + 1].strip()

    # Word boundary
    return truncated.rsplit(" ", 1)[0].strip() + "..."


def extract_code_blocks(markdown: str) -> list[dict]:
    """Extract all code blocks from markdown with language detection."""
    blocks = []
    pattern = r"```(\w+)?\s*\n(.*?)```"
    for match in re.finditer(pattern, markdown, re.DOTALL):
        lang = match.group(1) or "text"
        code = match.group(2)
        blocks.append({
            "language": lang,
            "code": code,
            "length": len(code),
        })
    return blocks


def extract_headings(markdown: str) -> list[dict]:
    """Extract headings with hierarchy."""
    headings = []
    for match in re.finditer(r"^(#{1,6})\s+(.+)$", markdown, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        headings.append({"level": level, "text": text})
    return headings


def estimate_token_count(text: str) -> int:
    """Rough token count estimation (4 chars ≈ 1 token for English)."""
    return len(text) // 4
