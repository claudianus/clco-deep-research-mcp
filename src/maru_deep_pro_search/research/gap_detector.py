"""Gap detection for iterative deep research.

Analyzes crawled sources against the original query to identify
uncovered topics and suggest follow-up search queries.
"""

from __future__ import annotations

from .expander import extract_keywords


# Predefined angles that are commonly missing from initial searches
_FOLLOWUP_ANGLES = [
    "benchmark",
    "performance",
    "comparison",
    "vs",
    "tutorial",
    "getting started",
    "API reference",
    "documentation",
    "common errors",
    "troubleshooting",
    "fix",
    "best practices",
    "security",
    "deployment",
    "production",
    "case study",
    "example",
    "github",
    "reddit discussion",
    "latest",
    "2026",
    "new features",
    "update",
]


def detect_gaps(query: str, sources: list) -> list[str]:
    """Analyze sources and suggest follow-up queries.

    Args:
        query: Original search query.
        sources: List of CitedSource objects (or any object with
                 content/markdown/snippet attributes).

    Returns:
        List of suggested follow-up queries (2-3 items max).
    """
    if not sources:
        return []

    # 1. Extract keywords from the original query
    query_keywords = set(extract_keywords(query))

    # 2. Collect all text from sources
    source_texts: list[str] = []
    for src in sources:
        text = ""
        if hasattr(src, "markdown") and src.markdown:
            text += src.markdown + " "
        if hasattr(src, "content") and src.content:
            text += src.content + " "
        if hasattr(src, "snippet") and src.snippet:
            text += src.snippet + " "
        source_texts.append(text.lower())

    # 3. Check which follow-up angles are poorly covered
    covered_scores: dict[str, int] = {}
    for angle in _FOLLOWUP_ANGLES:
        score = 0
        for text in source_texts:
            if angle.lower() in text:
                score += 1
        covered_scores[angle] = score

    # 4. Identify poorly covered angles (appearing in 0 or 1 sources)
    poorly_covered = [
        angle for angle, score in covered_scores.items()
        if score <= 1
    ]

    # 5. Generate follow-up queries by combining the original query
    #    with the poorly covered angles
    suggestions: list[str] = []
    for angle in poorly_covered[:3]:
        # Don't duplicate if the angle is already in the query
        if angle.lower() in query.lower():
            continue
        suggestions.append(f"{query} {angle}")

    # 6. If no angles triggered, fall back to a generic "latest" query
    if not suggestions:
        if "latest" not in query.lower():
            suggestions.append(f"{query} latest")
        if "2026" not in query.lower():
            suggestions.append(f"{query} 2026")

    # Limit to 3 suggestions
    return suggestions[:3]
