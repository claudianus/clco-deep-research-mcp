"""Naver search engine implementation for Korean queries."""

from __future__ import annotations

import logging
from urllib.parse import quote_plus

from scrapling import AsyncFetcher

from .base import SearchEngine, SearchResult, PageContent, ContentType, ExtractionQuality
from ..exceptions import NetworkError, ParseError
from ..utils.url import get_domain, should_skip_url, resolve_redirect
from ..utils.retry import with_retry

logger = logging.getLogger(__name__)

_SERP_SELECTORS = {
    "containers": ["li.bx", ".total_wrap", ".lst_total"],
    "title": [".total_tit", "a.title_link", "a[href]"],
    "url": ["a[href]", ".total_source"],
    "snippet": [".total_dsc", ".dsc_wrap", ".total_group"],
}

_KOREAN_DOMAINS = {
    "velog.io", "tistory.com", "naver.com", "blog.naver.com",
    "brunch.co.kr", "okky.kr", "hashnode.dev", "dev.to",
}


class NaverEngine(SearchEngine):
    """Naver search engine for Korean-language search."""

    name = "naver"
    supports_stealth = True
    quality_tier = 2
    typical_latency_ms = 1200
    reliability_score = 0.85

    def __init__(self):
        self._fetcher = AsyncFetcher()

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search Naver with Korean query support."""
        search_url = f"https://search.naver.com/search.naver?query={quote_plus(query)}"

        try:
            page = await with_retry(
                self._fetcher.async_fetch,
                search_url,
                max_attempts=3,
                retryable_exceptions=(Exception,),
            )
        except Exception as exc:
            logger.error("Naver SERP scrape failed: %s", exc)
            raise NetworkError(f"Failed to fetch Naver SERP: {exc}", retryable=True)

        results: list[SearchResult] = []
        seen: set[str] = set()

        containers = []
        for sel in _SERP_SELECTORS["containers"]:
            containers = page.css(sel)
            if containers:
                break

        for el in containers[:max_results * 2]:
            title_el = _first(el, _SERP_SELECTORS["title"])
            url_el = _first(el, _SERP_SELECTORS["url"])
            snippet_el = _first(el, _SERP_SELECTORS["snippet"])

            title = title_el.text.strip() if title_el else ""
            href = url_el.attrib.get("href", "") if url_el else ""
            snippet = snippet_el.text.strip() if snippet_el else ""

            href = resolve_redirect(href, search_url)
            if not href or not title:
                continue
            if should_skip_url(href):
                continue

            norm = href.rstrip("/")
            if norm in seen:
                continue
            seen.add(norm)

            domain = get_domain(href)
            results.append(
                SearchResult(
                    title=title,
                    url=href,
                    snippet=snippet,
                    position=len(results) + 1,
                    likely_content_type=_guess_content_type(href, snippet),
                    domain=domain,
                    url_suggests_docs=any(d in domain for d in _KOREAN_DOMAINS),
                    engine=self.name,
                )
            )
            if len(results) >= max_results:
                break

        if not results:
            raise ParseError("No results found on Naver", retryable=True, suggested_engine="duckduckgo_lite")

        return results

    async def fetch(self, url: str, stealth: bool = False, timeout: float = 15.0) -> PageContent:
        """Fetch a page with content extraction."""
        from .registry import SearchEngineRegistry

        engine = SearchEngineRegistry.create("duckduckgo")
        return await engine.fetch(url, stealth=stealth, timeout=timeout)


def _first(el, selectors: list[str]):
    for sel in selectors:
        results = el.css(sel)
        if results:
            return results[0]
    return None


def _guess_content_type(url: str, snippet: str = "") -> ContentType:
    lower = (url + " " + snippet).lower()
    if any(k in lower for k in ["github.com", "gitlab.com"]):
        return ContentType.CODE
    if any(k in lower for k in ["stackoverflow.com", "okky.kr", "forum"]):
        return ContentType.FORUM
    if any(k in lower for k in ["docs.", "/docs/", "documentation", "reference", "api."]):
        return ContentType.DOCUMENTATION
    if any(k in lower for k in ["tistory.com", "velog.io", "brunch.co.kr", "blog.", "/blog/", "medium.com"]):
        return ContentType.ARTICLE
    return ContentType.UNKNOWN
