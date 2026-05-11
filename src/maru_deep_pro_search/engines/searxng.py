"""SearXNG meta-search engine using JSON API."""

from __future__ import annotations

import asyncio
import json
import logging
import random
from urllib.parse import quote_plus

from scrapling import DynamicFetcher

from .base import SearchEngine, SearchResult, PageContent, ContentType, ExtractionQuality
from ..exceptions import NetworkError, ParseError
from ..utils.url import get_domain, should_skip_url, is_authority_domain
from ..utils.retry import with_retry

logger = logging.getLogger(__name__)

# Popular public SearXNG instances (rotated with fallback)
_DEFAULT_INSTANCES = [
    "https://searx.be",
    "https://search.sapti.me",
    "https://searx.fmac.xyz",
    "https://searx.tiekoetter.com",
    "https://search.bus-hit.me",
    "https://searxng.nicfab.eu",
]


class SearXNGEngine(SearchEngine):
    """SearXNG meta-search engine via JSON API."""

    name = "searxng"
    supports_stealth = False
    quality_tier = 1
    typical_latency_ms = 1500
    reliability_score = 0.85

    def __init__(self, instances: list[str] | None = None):
        self.instances = instances or _DEFAULT_INSTANCES.copy()
        self._fetcher = DynamicFetcher()

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search via SearXNG JSON API with instance rotation."""
        encoded = quote_plus(query)
        shuffled = self.instances.copy()
        random.shuffle(shuffled)

        last_error: Exception | None = None
        for base_url in shuffled:
            search_url = f"{base_url.rstrip('/')}/search?q={encoded}&format=json"
            try:
                page = await with_retry(
                    self._fetcher.async_fetch,
                    search_url,
                    max_attempts=2,
                    retryable_exceptions=(Exception,),
                )
                raw = page.html_content if hasattr(page, "html_content") else ""
                if not raw:
                    raise ParseError("Empty response from SearXNG", retryable=True)

                data = json.loads(raw)
                raw_results = data.get("results", [])

                results: list[SearchResult] = []
                seen: set[str] = set()
                for item in raw_results[: max_results * 2]:
                    title = (item.get("title") or "").strip()
                    url = (item.get("url") or "").strip()
                    snippet = (item.get("content") or item.get("snippet") or "").strip()
                    if not title or not url:
                        continue
                    if should_skip_url(url):
                        continue
                    norm = url.rstrip("/")
                    if norm in seen:
                        continue
                    seen.add(norm)
                    domain = get_domain(url)
                    results.append(
                        SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            position=len(results) + 1,
                            likely_content_type=_guess_content_type(url, snippet),
                            domain=domain,
                            url_suggests_docs=is_authority_domain(domain),
                            engine=self.name,
                        )
                    )
                    if len(results) >= max_results:
                        break

                if results:
                    logger.info("SearXNG (%s) returned %d results", base_url, len(results))
                    return results
                else:
                    raise ParseError("No results from SearXNG", retryable=True)

            except (json.JSONDecodeError, ParseError) as exc:
                last_error = exc
                logger.warning("SearXNG instance %s failed: %s", base_url, exc)
                continue
            except Exception as exc:
                last_error = exc
                logger.warning("SearXNG instance %s error: %s", base_url, exc)
                continue

        raise NetworkError(
            f"All SearXNG instances failed. Last: {last_error}",
            retryable=True,
            suggested_engine="duckduckgo_lite",
        )

    async def fetch(self, url: str, stealth: bool = False, timeout: float = 15.0) -> PageContent:
        """Fetch a page — delegates to DuckDuckGo-style extraction."""
        from .registry import SearchEngineRegistry

        engine = SearchEngineRegistry.create("duckduckgo")
        return await engine.fetch(url, stealth=stealth, timeout=timeout)


def _guess_content_type(url: str, snippet: str = "") -> ContentType:
    """Guess content type from URL and snippet."""
    lower = (url + " " + snippet).lower()
    if any(k in lower for k in ["github.com", "gitlab.com", "bitbucket.org"]):
        return ContentType.CODE
    if any(k in lower for k in ["stackoverflow.com", "stackexchange.com"]):
        return ContentType.FORUM
    if any(k in lower for k in ["docs.", "/docs/", "documentation", "reference", "api.", "/api/"]):
        return ContentType.DOCUMENTATION
    if any(k in lower for k in ["medium.com", "dev.to", "blog.", "/blog/"]):
        return ContentType.ARTICLE
    return ContentType.UNKNOWN
