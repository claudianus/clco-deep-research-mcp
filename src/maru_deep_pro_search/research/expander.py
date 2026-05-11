"""Query expansion for deep research.

Generates orthogonal subqueries to cover multiple angles of a research topic
without requiring LLM calls."""

from __future__ import annotations

import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

_CURRENT_YEAR = datetime.now().year

# Template-based query expansion angles
_QUERY_TEMPLATES = {
    "recent_versioned": [
        f"{{query}} latest {_CURRENT_YEAR} {_CURRENT_YEAR + 1}",
        "{query} new features updates",
        "{query} recent developments",
    ],
    "recent_general": [
        "{query} recent developments",
        "{query} overview explained",
    ],
    "tutorial": [
        "{query} tutorial getting started",
        "{query} beginner guide examples",
        "{query} how to use",
    ],
    "api": [
        "{query} API reference documentation",
        "{query} function methods parameters",
        "{query} SDK docs",
    ],
    "troubleshooting": [
        "{query} common errors solutions",
        "{query} fix problem troubleshooting",
        "{query} error handling",
    ],
    "comparison": [
        "{query} vs alternative comparison",
        "{query} best practices",
        "{query} benchmark performance",
    ],
    "github": [
        "{query} github repository examples",
        "{query} open source implementation",
        "{query} code samples",
    ],
    "community": [
        "{query} stackoverflow discussion",
        "{query} reddit community",
        "{query} forum discussion",
    ],
    "korean_community": [
        "{query} 한국 개발자 커뮤니티",
        "{query} 국내 개발 블로그",
        "{query} 한국어 튜토리얼",
        "{query} 네이버 블로그",
        "{query} 티스토리",
    ],
    "korean_docs": [
        "{query} 한국어 문서",
        "{query} 한글 설명서",
        "{query} 국내 번역",
    ],
}

# Concepts that are stable enough that "latest YYYY" is usually noise
_STABLE_CONCEPTS = {
    "list comprehension", "dictionary", "tuple", "set", "string",
    "for loop", "while loop", "if statement", "function", "class",
    "inheritance", "polymorphism", "encapsulation", "recursion",
    "ownership", "borrowing", "lifetime", "trait", "struct", "enum",
    "closure", "iterator", "generics", "macro",
    "variable", "constant", "scope", "namespace", "module",
    "http", "tcp", "udp", "rest", "json", "xml", "yaml",
    "algorithm", "data structure", "big o", "complexity",
    "sort", "search", "tree", "graph", "queue", "stack", "heap",
}


def expand_query(query: str, max_subqueries: int = 5) -> list[str]:
    """Expand a query into multiple orthogonal subqueries.

    Args:
        query: Original search query.
        max_subqueries: Maximum number of subqueries to generate.

    Returns:
        List of subqueries including the original.
    """
    subqueries = [query]  # Always include original

    # Select angles based on query characteristics
    angles = _select_angles(query)

    for angle in angles:
        templates = _QUERY_TEMPLATES.get(angle, [])
        for template in templates:
            subquery = template.format(query=query)
            if subquery not in subqueries:
                subqueries.append(subquery)
            if len(subqueries) >= max_subqueries:
                break
        if len(subqueries) >= max_subqueries:
            break

    logger.debug("Expanded query '%s' into %d subqueries", query, len(subqueries))
    return subqueries[:max_subqueries]


def _select_angles(query: str) -> list[str]:
    """Select relevant expansion angles based on query content."""
    lower = query.lower()
    angles = []

    # Check for Korean language indicators
    has_korean = any('\uac00' <= char <= '\ud7a3' for char in query)
    korean_keywords = ["한국", "국내", "korean", "한글", "한국어"]
    is_korean_query = has_korean or any(kw in lower for kw in korean_keywords)

    if is_korean_query:
        angles.extend(["korean_community", "korean_docs", "recent"])
        return angles

    # Determine if query needs versioned "latest" expansion
    has_version = bool(re.search(r'\d+\.\d+|v\d+\.|\b\d{4}\b', query))
    is_stable = any(concept in lower for concept in _STABLE_CONCEPTS)
    needs_freshness = any(kw in lower for kw in [
        "deprecated", "removed", "latest", "new ", "update", "release",
        "version", "v2", "v3", "migrate", "migration", "upgrade",
    ])

    if has_version or needs_freshness or not is_stable:
        angles.append("recent_versioned")
    else:
        angles.append("recent_general")

    # Code-related queries
    if any(kw in lower for kw in ["python", "javascript", "typescript", "go", "rust", "java", "code", "programming", "api", "library", "framework"]):
        angles.extend(["tutorial", "api", "github"])

    # Error/problem queries
    if any(kw in lower for kw in ["error", "fix", "problem", "issue", "bug", "troubleshoot"]):
        angles.extend(["troubleshooting", "community"])

    # Comparison queries
    if any(kw in lower for kw in ["vs", "versus", "compare", "alternative", "best", "difference between", "diff between"]):
        angles.append("comparison")

    # General tech queries
    if len(angles) <= 2:
        angles.extend(["tutorial", "github"])

    return angles


def extract_keywords(query: str) -> list[str]:
    """Extract key terms from a query for relevance scoring."""
    # Remove common stop words
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "shall",
        "can", "need", "dare", "ought", "used", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into",
        "through", "during", "before", "after", "above", "below",
        "between", "under", "again", "further", "then", "once",
        "here", "there", "when", "where", "why", "how", "all",
        "each", "few", "more", "most", "other", "some", "such",
        "no", "nor", "not", "only", "own", "same", "so", "than",
        "too", "very", "just", "and", "but", "if", "or", "because",
        "until", "while", "what", "which", "who", "whom", "this",
        "that", "these", "those", "am", "it", "its", "about",
        "against", "down", "out", "off", "over", "i", "me", "my", "myself", "we",
        "our", "ours", "ourselves", "you", "your", "yours", "yourself",
        "yourselves", "he", "him", "his", "himself", "she", "her",
        "hers", "herself", "they", "them", "their", "theirs",
        "themselves", "get", "using", "use", "tutorial",
        "guide", "example", "sample", "documentation", "docs",
    }

    words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 2]

    return keywords
