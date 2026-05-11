"""Brave Search engine — optional API key, graceful fallback when unavailable.

Brave Search API offers a free tier (up to 2,000 queries/month).
If no BRAVE_API_KEY is set, the engine gracefully skips registration.
"""

from __future__ import annotations

import logging
import os
from urllib.parse import quote_plus

from .base import SearchEngine, SearchResult, PageContent, ContentType, ExtractionQuality
from ..exceptions import NetworkError, ParseError
from ..utils.url import get_domain, should_skip_url

logger = logging.getLogger(__name__)


class BraveEngine(SearchEngine):
    """Brave Search via official API (requires BRAVE_API_KEY)."""

    name = "brave"
    supports_stealth = False
    quality_tier = 1
    typical_latency_ms = 600
    reliability_score = 0.95

    def __init__(self):
        self.api_key = os.environ.get("BRAVE_API_KEY", "")
        if not self.api_key:
            logger.debug("BRAVE_API_KEY not set; Brave engine will be unavailable")

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        if not self.api_key:
            raise ParseError(
                "Brave Search requires BRAVE_API_KEY environment variable.",
                retryable=False,
                suggested_engine="duckduckgo_lite",
            )

        url = (
            f"https://api.search.brave.com/res/v1/web/search?"
            f"q={quote_plus(query)}&count={max_results}&offset=0"
        )
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

        try:
            import aiohttp
        except ImportError:
            raise ParseError(
                "aiohttp required for Brave Search.",
                retryable=False,
                suggested_engine="duckduckgo_lite",
            )

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status == 401:
                        raise ParseError(
                            "Invalid Brave API key.",
                            retryable=False,
                        )
                    if resp.status == 429:
                        raise RateLimitError("Brave Search rate limit exceeded.")
                    resp.raise_for_status()
                    data = await resp.json()
        except Exception as exc:
            raise NetworkError(f"Brave Search request failed: {exc}", retryable=True)

        results: list[SearchResult] = []
        web_results = data.get("web", {}).get("results", [])
        for i, item in enumerate(web_results[:max_results], 1):
            href = item.get("url", "")
            title = item.get("title", "")
            snippet = item.get("description", "")

            if not href or not title:
                continue
            if should_skip_url(href):
                continue

            results.append(SearchResult(
                title=title,
                url=href,
                snippet=snippet,
                position=i,
                likely_content_type=ContentType.UNKNOWN,
                domain=get_domain(href),
                url_suggests_docs=False,
                engine="brave",
            ))

        if not results:
            raise ParseError(
                "No results from Brave Search.",
                retryable=True,
                suggested_engine="duckduckgo_lite",
            )

        return results

    async def fetch(self, url: str, stealth: bool = False, timeout: float = 15.0) -> PageContent:
        # Fallback to DuckDuckGo fetcher
        from .registry import SearchEngineRegistry
        ddg = SearchEngineRegistry.create("duckduckgo")
        return await ddg.fetch(url, stealth=stealth, timeout=timeout)
