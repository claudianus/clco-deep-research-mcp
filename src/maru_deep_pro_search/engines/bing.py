"""Bing search engine implementation."""

from __future__ import annotations

import logging
from urllib.parse import quote_plus

from scrapling import AsyncFetcher, StealthyFetcher

from .base import SearchEngine, SearchResult, PageContent, ContentType, ExtractionQuality
from ..exceptions import NetworkError, ParseError
from ..utils.url import get_domain, should_skip_url, resolve_redirect, is_authority_domain
from ..utils.retry import with_retry

logger = logging.getLogger(__name__)

_SERP_SELECTORS = {
    "containers": ["li.b_algo", ".b_algo"],
    "title": ["h2 a", "h2", ".b_title"],
    "url": ["h2 a", "a[href]", ".b_attribution"],
    "snippet": [".b_caption p", ".b_snippet", ".b_paractl p", "p"],
}

_DOCS_DOMAINS = {
    "docs.python.org", "python.org", "developer.mozilla.org", "mdn.io",
    "react.dev", "nextjs.org", "nodejs.org", "deno.com",
    "go.dev", "pkg.go.dev", "doc.rust-lang.org", "docs.rs",
    "api.rubyonrails.org", "guides.rubyonrails.org",
    "learn.microsoft.com", "docs.microsoft.com",
    "postgresql.org/docs", "dev.mysql.com/doc",
    "kubernetes.io/docs", "helm.sh/docs", "terraform.io/docs",
    "fastapi.tiangolo.com", "flask.palletsprojects.com",
    "docs.djangoproject.com", "vuejs.org", "svelte.dev",
}


class BingEngine(SearchEngine):
    """Bing search engine with direct HTML scraping."""

    name = "bing"
    supports_stealth = True
    quality_tier = 2
    typical_latency_ms = 1200
    reliability_score = 0.90

    def __init__(self):
        self._fetcher = AsyncFetcher()

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search Bing with retry and fallback selectors."""
        search_url = f"https://www.bing.com/search?q={quote_plus(query)}&count={max_results}"

        try:
            page = await with_retry(
                self._fetcher.async_fetch,
                search_url,
                max_attempts=3,
                retryable_exceptions=(Exception,),
            )
        except Exception as exc:
            logger.error("Bing SERP scrape failed: %s", exc)
            raise NetworkError(f"Failed to fetch Bing SERP: {exc}", retryable=True)

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
                    url_suggests_docs=any(d in domain for d in _DOCS_DOMAINS),
                    engine=self.name,
                )
            )
            if len(results) >= max_results:
                break

        if not results:
            raise ParseError("No results found on Bing", retryable=True, suggested_engine="duckduckgo_lite")

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
    if any(k in lower for k in ["github.com", "gitlab.com", "bitbucket.org"]):
        return ContentType.CODE
    if any(k in lower for k in ["stackoverflow.com", "stackexchange.com", "discourse", "forum"]):
        return ContentType.FORUM
    if any(k in lower for k in ["docs.", "/docs/", "documentation", "reference", "api.", "/api/"]):
        return ContentType.DOCUMENTATION
    if any(k in lower for k in ["medium.com", "dev.to", "blog.", "/blog/"]):
        return ContentType.ARTICLE
    return ContentType.UNKNOWN
