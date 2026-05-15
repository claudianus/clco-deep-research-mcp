"""Configuration management for maru-search.

Supports environment variables and sensible defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class SearchConfig:
    """Runtime search configuration."""

    default_engine: str = "duckduckgo_lite"
    max_results_per_query: int = 10
    max_concurrent_fetches: int = 5
    # --- HTTP timeouts (seconds) — read by MCP tools -----------------------------
    serp_timeout_seconds: float = 30.0
    """Timeout for search-engine HTML scrape (``web_search``, ``search_with_citations``)."""

    http_fetch_timeout_seconds: float = 20.0
    """Timeout for ``fetch_page`` / each URL in ``fetch_bulk``."""

    deep_research_timeout_seconds: float = 45.0
    """Timeout for ``deep_research(...)`` orchestration."""

    answer_timeout_seconds: float = 30.0
    """Timeout for ``tool_answer`` (deep pipeline)."""

    auto_fetch_nested_timeout_seconds: float = 8.0
    """Budget for each nested ``fetch_page`` during ``deep_research`` ``auto_fetch``."""

    retry_attempts: int = 3
    # Auto-update settings
    auto_check_updates: bool = True
    # Quality weights for ranking
    authority_weight: float = 2.0
    freshness_weight: float = 1.0
    snippet_weight: float = 1.0
    position_weight: float = 0.5

    @classmethod
    def from_env(cls) -> SearchConfig:
        """Load configuration from environment variables."""
        return cls(
            default_engine=os.getenv("MARU_SEARCH_ENGINE", "duckduckgo_lite"),
            max_results_per_query=int(os.getenv("MARU_SEARCH_MAX_RESULTS", "10")),
            max_concurrent_fetches=int(os.getenv("MARU_SEARCH_MAX_CONCURRENT", "5")),
            serp_timeout_seconds=float(os.getenv("MARU_SEARCH_TIMEOUT", "30.0")),
            http_fetch_timeout_seconds=float(os.getenv("MARU_FETCH_HTTP_TIMEOUT", "20.0")),
            deep_research_timeout_seconds=float(os.getenv("MARU_DEEP_RESEARCH_TIMEOUT", "45.0")),
            answer_timeout_seconds=float(os.getenv("MARU_ANSWER_TIMEOUT", "30.0")),
            auto_fetch_nested_timeout_seconds=float(os.getenv("MARU_AUTO_FETCH_TIMEOUT", "8.0")),
            retry_attempts=int(os.getenv("MARU_SEARCH_RETRIES", "3")),
            auto_check_updates=os.getenv("MARU_SKIP_UPDATE_CHECK", "").lower()
            not in ("1", "true", "yes"),
        )


# Global default instance
DEFAULT_CONFIG = SearchConfig.from_env()
