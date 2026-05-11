"""Academic search engine — ArXiv + Semantic Scholar, no API keys required.

ArXiv API is fully open. Semantic Scholar base API requires no key
(optional key raises rate limits). Falls back to DuckDuckGo site-search
if both APIs fail.
"""

from __future__ import annotations

import asyncio
import json
import logging
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, urljoin

from .base import SearchEngine, SearchResult, PageContent, ContentType, ExtractionQuality
from ..exceptions import NetworkError, ParseError
from ..utils.url import get_domain, should_skip_url

logger = logging.getLogger(__name__)

_ARXIV_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


class AcademicEngine(SearchEngine):
    """Search academic papers via ArXiv and Semantic Scholar."""

    name = "academic"
    supports_stealth = False
    quality_tier = 1
    typical_latency_ms = 1500
    reliability_score = 0.92

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search ArXiv + Semantic Scholar concurrently."""
        tasks = [
            asyncio.create_task(self._search_arxiv(query, max_results)),
            asyncio.create_task(self._search_semantic_scholar(query, max_results)),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_results: list[SearchResult] = []
        for res in results:
            if isinstance(res, list):
                all_results.extend(res)
            elif isinstance(res, Exception):
                logger.warning("Academic search sub-engine failed: %s", res)

        if not all_results:
            logger.warning("All academic APIs failed for: %s", query)
            raise ParseError(
                "Academic search failed. Try a different engine.",
                retryable=True,
                suggested_engine="duckduckgo_lite",
            )

        # Deduplicate by URL and sort by year (desc)
        seen: set[str] = set()
        unique: list[SearchResult] = []
        for r in sorted(all_results, key=lambda x: x.position, reverse=False):
            norm = r.url.rstrip("/")
            if norm not in seen:
                seen.add(norm)
                unique.append(r)

        return unique[:max_results]

    async def _search_arxiv(self, query: str, max_results: int) -> list[SearchResult]:
        """Query ArXiv API (Atom feed)."""
        url = (
            f"http://export.arxiv.org/api/query?"
            f"search_query=all:{quote_plus(query)}&"
            f"start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
        )
        try:
            import aiohttp
        except ImportError:
            logger.debug("aiohttp not available, skipping ArXiv search")
            return []

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(url) as resp:
                    text = await resp.text()
        except Exception as exc:
            logger.debug("ArXiv request failed: %s", exc)
            return []

        try:
            root = ET.fromstring(text)
        except ET.ParseError as exc:
            logger.debug("ArXiv XML parse failed: %s", exc)
            return []

        results: list[SearchResult] = []
        for i, entry in enumerate(root.findall("atom:entry", _ARXIV_NS), 1):
            title_el = entry.find("atom:title", _ARXIV_NS)
            url_el = entry.find("atom:id", _ARXIV_NS)
            summary_el = entry.find("atom:summary", _ARXIV_NS)
            published_el = entry.find("atom:published", _ARXIV_NS)

            title = (title_el.text or "").replace("\n", " ").strip()
            arxiv_url = (url_el.text or "").strip()
            summary = (summary_el.text or "").replace("\n", " ").strip()[:400]
            published = (published_el.text or "")[:4]  # year only

            if not arxiv_url:
                continue

            # Prefer abstract URL, fallback to PDF
            pdf_url = arxiv_url.replace("/abs/", "/pdf/") + ".pdf"

            results.append(SearchResult(
                title=f"[arXiv] {title}",
                url=arxiv_url,
                snippet=f"{summary} (Published: {published})",
                position=i,
                likely_content_type=ContentType.ARTICLE,
                domain="arxiv.org",
                url_suggests_docs=True,
                engine="academic",
            ))

        logger.debug("ArXiv returned %d results", len(results))
        return results

    async def _search_semantic_scholar(self, query: str, max_results: int) -> list[SearchResult]:
        """Query Semantic Scholar public API."""
        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/search?"
            f"query={quote_plus(query)}&"
            f"fields=title,url,year,abstract,authors&"
            f"limit={max_results}"
        )
        try:
            import aiohttp
        except ImportError:
            logger.debug("aiohttp not available, skipping Semantic Scholar search")
            return []

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(url) as resp:
                    if resp.status == 429:
                        logger.debug("Semantic Scholar rate limited")
                        return []
                    data = await resp.json()
        except Exception as exc:
            logger.debug("Semantic Scholar request failed: %s", exc)
            return []

        papers = data.get("data", [])
        results: list[SearchResult] = []
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "")
            year = paper.get("year", "")
            abstract = (paper.get("abstract") or "")[:400]
            authors = ", ".join(a.get("name", "") for a in paper.get("authors", [])[:3])
            paper_url = paper.get("url", "")
            if not paper_url:
                # Build URL from paperId
                pid = paper.get("paperId", "")
                if pid:
                    paper_url = f"https://www.semanticscholar.org/paper/{pid}"

            snippet = f"{abstract} (Authors: {authors}, Year: {year})"
            results.append(SearchResult(
                title=f"[S2] {title}",
                url=paper_url,
                snippet=snippet,
                position=i,
                likely_content_type=ContentType.ARTICLE,
                domain="semanticscholar.org",
                url_suggests_docs=True,
                engine="academic",
            ))

        logger.debug("Semantic Scholar returned %d results", len(results))
        return results

    async def fetch(self, url: str, stealth: bool = False, timeout: float = 15.0) -> PageContent:
        """Fetch academic page — arxiv abstracts or PDF metadata."""
        # For arXiv, convert abs URL to HTML if needed
        if "arxiv.org/abs/" in url:
            html_url = url.replace("/abs/", "/html/")
            try:
                import aiohttp
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=int(timeout))) as session:
                    async with session.get(html_url) as resp:
                        text = await resp.text()
                        return PageContent(
                            url=url,
                            final_url=str(resp.url),
                            title="arXiv Paper",
                            text=text,
                            markdown=text,
                            quality=ExtractionQuality.HIGH if len(text) > 500 else ExtractionQuality.MEDIUM,
                            content_type=ContentType.ARTICLE,
                            content_length=len(text),
                        )
            except Exception as exc:
                logger.debug("arXiv fetch failed: %s", exc)

        # Fallback to generic fetch via DuckDuckGo engine
        from .registry import SearchEngineRegistry
        ddg = SearchEngineRegistry.create("duckduckgo")
        return await ddg.fetch(url, stealth=stealth, timeout=timeout)
