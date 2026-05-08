"""Structured exception hierarchy for clco-deep-research-mcp.

All errors are categorized so the host LLM can decide whether to retry,
switch engines, or report failure."""

from __future__ import annotations


class ResearchError(Exception):
    """Base exception for all research-related errors."""

    default_retryable: bool = False
    default_suggested_engine: str | None = None

    def __init__(self, message: str, *, retryable: bool | None = None, suggested_engine: str | None = None):
        super().__init__(message)
        # Use explicit parameter if provided, otherwise fall back to class default
        self.retryable = retryable if retryable is not None else self.default_retryable
        self.suggested_engine = suggested_engine if suggested_engine is not None else self.default_suggested_engine


class NetworkError(ResearchError):
    """Network-level failure (timeout, DNS, connection reset)."""

    default_retryable = True


class RateLimitError(ResearchError):
    """Rate limit or temporary block from search engine."""

    default_retryable = True


class BlockedError(ResearchError):
    """Anti-bot wall (CAPTCHA, Cloudflare challenge, etc)."""

    default_retryable = True
    default_suggested_engine = "duckduckgo_lite"


class ParseError(ResearchError):
    """HTML/SERP parsing failure (selectors outdated, unexpected structure)."""

    default_retryable = True
    default_suggested_engine = "duckduckgo_lite"


class NoResultsError(ResearchError):
    """Query returned zero usable results."""

    default_retryable = False


class ExtractionError(ResearchError):
    """Content extraction failed (trafilatura error, empty page, etc)."""

    default_retryable = True
