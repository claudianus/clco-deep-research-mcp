"""Enhanced deep research pipeline: search SERPs → crawl pages → extract content → structure for LLM.

The intelligence lives in the host LLM (Claude). This module provides the
crawling primitives and structures raw content for efficient consumption.
Rich metadata (quality scores, content types, link maps) flows through every
layer so the host LLM can make informed orchestration decisions."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from ..engines.base import SearchResult, PageContent, ContentType, ExtractionQuality
from ..engines.duckduckgo import DuckDuckGoEngine
from ..exceptions import ResearchError, NetworkError, ParseError
from ..utils.url import should_skip_url, deduplicate_urls, is_authority_domain
from ..utils.retry import with_retry
from .expander import expand_query
from ..extraction.content import truncate_for_llm

logger = logging.getLogger(__name__)


@dataclass
class Source:
    url: str
    title: str
    snippet: str = ""
    content: str = ""          # plain text
    markdown: str = ""         # LLM-optimized markdown
    content_length: int = 0
    fetch_ms: float = 0.0
    # Quality metadata for LLM orchestration
    quality: str = ""          # high/medium/low/empty/blocked
    content_type: str = ""     # article/docs/forum/code/spam/unknown
    internal_links: list[dict] = field(default_factory=list)
    external_links: list[dict] = field(default_factory=list)
    # Code-aware metadata for coding agent optimization
    code_languages: list[str] = field(default_factory=list)
    api_signatures: list[dict] = field(default_factory=list)
    package_refs: list[dict] = field(default_factory=list)
    code_to_text_ratio: float = 0.0
    published_date: str = ""
    freshness_days: int | None = None
    is_api_reference: bool = False
    is_tutorial: bool = False
    is_error_solution: bool = False
    # Relevance scoring
    relevance_score: float = 0.0
    authority_boost: bool = False


@dataclass
class ResearchResult:
    query: str
    engine: str
    total_sources: int
    sources: list[Source] = field(default_factory=list)
    elapsed_ms: float = 0.0
    # Aggregate quality signals
    high_quality_count: int = 0
    blocked_count: int = 0
    # Query expansion info
    subqueries: list[str] = field(default_factory=list)
    # Token management metadata
    total_tokens_used: int = 0
    tokens_allocated: int = 0
    sources_summarized: int = 0
    sources_dropped: int = 0


async def deep_research(
    query: str,
    engine: str = "duckduckgo_lite",
    max_sources: int = 8,
    follow_links: bool = False,
    stealth: bool = False,
    expand_queries: bool = True,
    max_tokens_per_source: int = 2500,
    max_total_tokens: int = 20000,
    summarize: bool = False,
) -> ResearchResult:
    """End-to-end deep research pipeline with query expansion and multi-pass crawling.

    1. Expand query into orthogonal subqueries (optional)
    2. Search each subquery and collect results
    3. Deduplicate and score URLs by relevance
    4. Concurrently crawl top pages with quality assessment
    5. Optionally follow external links for deeper coverage
    6. Structure into Source list with quality metadata

    Args:
        query: Search query.
        engine: Search engine variant ("duckduckgo", "duckduckgo_lite").
        max_sources: Max unique pages to crawl.
        follow_links: If True, follow one level of external links.
        stealth: Use StealthyFetcher for anti-bot bypass.
        expand_queries: If True, generate subqueries for broader coverage.
        max_tokens_per_source: Token budget per source.
        max_total_tokens: Total output token budget.
        summarize: Enable extractive summarization for over-budget scenarios.
    """
    t0 = time.monotonic()

    # Initialize engine
    search_engine = DuckDuckGoEngine(variant=engine)

    # Phase 1: Query expansion
    subqueries = [query]
    if expand_queries:
        subqueries = expand_query(query, max_subqueries=5)

    # Phase 2: Search all subqueries
    all_results: list[SearchResult] = []
    for sq in subqueries:
        try:
            results = await with_retry(
                search_engine.search,
                sq,
                max_results=max_sources * 2,
                max_attempts=2,
                retryable_exceptions=(NetworkError, ParseError),
            )
            all_results.extend(results)
            logger.debug("Subquery '%s' returned %d results", sq, len(results))
        except Exception as exc:
            logger.warning("Subquery '%s' failed: %s", sq, exc)
            continue

    if not all_results:
        return ResearchResult(
            query=query,
            engine=engine,
            total_sources=0,
            subqueries=subqueries,
        )

    # Phase 3: Deduplicate and score
    seen_urls: set[str] = set()
    scored_results: list[tuple[SearchResult, float]] = []

    for r in all_results:
        if should_skip_url(r.url):
            continue
        normalized = r.url.rstrip("/")
        if normalized in seen_urls:
            continue
        seen_urls.add(normalized)

        # Score by authority + content type + snippet quality
        score = _score_result(r, query)
        scored_results.append((r, score))

    # Sort by score descending
    scored_results.sort(key=lambda x: x[1], reverse=True)

    # Phase 4: Crawl top pages
    urls_to_fetch = [r.url for r, _ in scored_results[:max_sources]]

    pages = await _fetch_pages(urls_to_fetch, search_engine, stealth=stealth)

    # Build sources
    sources: list[Source] = []
    high_quality = 0
    blocked = 0

    for sr, score in scored_results[:max_sources]:
        matched = next(
            (p for p in pages if p.url == sr.url or p.final_url == sr.url),
            None,
        )

        if matched and matched.quality == ExtractionQuality.BLOCKED:
            blocked += 1

        if matched and matched.content_length > 100:
            if matched.quality == ExtractionQuality.HIGH:
                high_quality += 1

            sources.append(Source(
                url=matched.final_url or matched.url,
                title=matched.title or sr.title,
                snippet=sr.snippet,
                content=matched.text,
                markdown=matched.markdown,
                content_length=matched.content_length,
                fetch_ms=matched.fetch_duration_ms,
                quality=matched.quality.value if matched.quality else "",
                content_type=matched.content_type.value if matched.content_type else "",
                internal_links=matched.internal_links,
                external_links=matched.external_links,
                code_languages=matched.code_languages,
                api_signatures=matched.api_signatures,
                package_refs=getattr(matched, 'package_refs', []),
                code_to_text_ratio=matched.code_to_text_ratio,
                published_date=matched.published_date,
                freshness_days=matched.freshness_days,
                is_api_reference=matched.is_api_reference,
                is_tutorial=matched.is_tutorial,
                is_error_solution=matched.is_error_solution,
                relevance_score=score,
                authority_boost=is_authority_domain(matched.url),
            ))
        elif sr.snippet:
            # Fallback to snippet-only source
            sources.append(Source(
                url=sr.url,
                title=sr.title,
                snippet=sr.snippet,
                quality="empty",
                content_type=sr.likely_content_type.value if sr.likely_content_type else "",
                relevance_score=score,
                authority_boost=is_authority_domain(sr.url),
            ))

    # Phase 5: Follow links (optional)
    if follow_links and len(sources) < max_sources:
        fetched_urls = {s.url.rstrip("/") for s in sources}
        all_external: list[str] = []

        for src in sources:
            for link in src.external_links:
                u = link.get("url", "")
                if u and not should_skip_url(u) and u.rstrip("/") not in fetched_urls:
                    all_external.append(u)

        all_external = deduplicate_urls(all_external)
        new_urls = all_external[:max_sources - len(sources)]

        if new_urls:
            linked_pages = await _fetch_pages(new_urls, search_engine, stealth=True)
            for lp in linked_pages:
                if lp.content_length > 200:
                    if lp.quality == ExtractionQuality.HIGH:
                        high_quality += 1

                    sources.append(Source(
                        url=lp.final_url or lp.url,
                        title=lp.title,
                        content=lp.text,
                        markdown=lp.markdown,
                        content_length=lp.content_length,
                        fetch_ms=lp.fetch_duration_ms,
                        quality=lp.quality.value if lp.quality else "",
                        content_type=lp.content_type.value if lp.content_type else "",
                        internal_links=lp.internal_links,
                        external_links=lp.external_links,
                        code_languages=lp.code_languages,
                        api_signatures=lp.api_signatures,
                        package_refs=getattr(lp, 'package_refs', []),
                        code_to_text_ratio=lp.code_to_text_ratio,
                        published_date=lp.published_date,
                        freshness_days=lp.freshness_days,
                        is_api_reference=lp.is_api_reference,
                        is_tutorial=lp.is_tutorial,
                        is_error_solution=lp.is_error_solution,
                        relevance_score=0.5,  # Lower score for linked pages
                        authority_boost=is_authority_domain(lp.url),
                    ))

    elapsed = (time.monotonic() - t0) * 1000
    
    # Smart token allocation
    allocations, sources_summarized, sources_dropped = _allocate_tokens(
        sources[:max_sources],
        max_tokens_per_source,
        max_total_tokens,
        summarize,
    )
    
    # Apply allocations to sources
    allocated_sources = []
    for src, budget in allocations:
        src.markdown = _extractive_summarize(src.markdown, budget) if summarize and len(src.markdown) > budget * 4 else src.markdown
        allocated_sources.append(src)
    
    return ResearchResult(
        query=query,
        engine=engine,
        total_sources=len(allocated_sources),
        sources=allocated_sources,
        elapsed_ms=elapsed,
        high_quality_count=high_quality,
        blocked_count=blocked,
        subqueries=subqueries,
        tokens_allocated=sum(budget for _, budget in allocations),
        sources_summarized=sources_summarized,
        sources_dropped=sources_dropped,
    )


def _allocate_tokens(
    sources: list[Source],
    max_tokens_per_source: int,
    max_total_tokens: int,
    summarize: bool,
) -> tuple[list[tuple[Source, int]], int, int]:
    """Allocate tokens to sources based on quality scores.
    
    Returns:
        (source_allocation, sources_summarized, sources_dropped)
        where source_allocation is list of (source, token_budget) tuples
    """
    if not sources:
        return [], 0, 0
    
    # Sort by quality and relevance
    quality_weights = {"high": 1.0, "medium": 0.7, "low": 0.4, "empty": 0.2, "blocked": 0.0}
    scored_sources = [
        (src, quality_weights.get(src.quality, 0.5) * (1 + src.relevance_score))
        for src in sources
    ]
    scored_sources.sort(key=lambda x: x[1], reverse=True)
    
    allocations = []
    total_allocated = 0
    sources_summarized = 0
    sources_dropped = 0
    
    for src, score in scored_sources:
        if src.quality == "blocked":
            continue
            
        # Calculate token budget based on quality
        quality_mult = quality_weights.get(src.quality, 0.5)
        budget = int(max_tokens_per_source * quality_mult)
        
        # Check if we'd exceed total budget
        if total_allocated + budget > max_total_tokens:
            # Try with summarization if enabled
            if summarize and src.quality in ("medium", "low"):
                budget = int(budget * 0.5)  # Half for summarized
                if total_allocated + budget <= max_total_tokens:
                    allocations.append((src, budget))
                    total_allocated += budget
                    sources_summarized += 1
                    continue
            
            # Drop source if still over budget
            sources_dropped += 1
            continue
        
        allocations.append((src, budget))
        total_allocated += budget
    
    return allocations, sources_summarized, sources_dropped


def _extractive_summarize(markdown: str, max_tokens: int) -> str:
    """Create extractive summary using headings and key paragraphs."""
    from ..extraction.content import extract_headings, estimate_token_count
    
    if estimate_token_count(markdown) <= max_tokens:
        return markdown
    
    # Extract headings
    headings = extract_headings(markdown)
    
    # Build summary from headings + first paragraph after each heading
    summary_parts = []
    lines = markdown.split('\n')
    current_section = []
    in_section = False
    
    for line in lines:
        if line.startswith('#'):
            # Save previous section
            if current_section:
                summary_parts.extend(current_section[:2])  # Heading + first paragraph
                current_section = []
            in_section = True
            current_section.append(line)
        elif in_section and line.strip() and not line.startswith('#'):
            current_section.append(line)
            if len(current_section) >= 3:  # Heading + 2 paragraphs max
                in_section = False
    
    # Add last section
    if current_section:
        summary_parts.extend(current_section[:2])
    
    summary = '\n\n'.join(summary_parts)
    
    # Ensure we don't exceed token limit
    if estimate_token_count(summary) > max_tokens:
        summary = truncate_for_llm(summary, max_tokens)
    
    return summary + "\n\n_[Content summarized for brevity]_"


def _score_result(result: SearchResult, query: str) -> float:
    """Score a search result by relevance and authority."""
    score = 0.0

    # Authority boost
    if is_authority_domain(result.url):
        score += 2.0

    # Content type preference
    if result.likely_content_type == ContentType.DOCUMENTATION:
        score += 1.5
    elif result.likely_content_type == ContentType.ARTICLE:
        score += 1.0
    elif result.likely_content_type == ContentType.CODE:
        score += 0.8

    # URL suggests docs
    if result.url_suggests_docs:
        score += 1.0

    # Snippet quality (length heuristic)
    if result.snippet:
        score += min(len(result.snippet) / 500, 1.0)

    # Position bonus (earlier results tend to be better)
    score += max(0, (10 - result.position) / 10)

    return score


async def _fetch_pages(
    urls: list[str],
    engine: DuckDuckGoEngine,
    stealth: bool = False,
    max_concurrent: int = 5,
) -> list[PageContent]:
    """Fetch multiple pages concurrently with semaphore control."""
    sem = asyncio.Semaphore(max_concurrent)

    async def _one(u: str) -> PageContent:
        async with sem:
            try:
                return await engine.fetch(u, stealth=stealth)
            except Exception as exc:
                logger.warning("Fetch failed for %s: %s", u, exc)
                return PageContent(
                    url=u,
                    error_message=str(exc),
                    quality=ExtractionQuality.BLOCKED,
                )

    return await asyncio.gather(*(_one(u) for u in urls))


def format_for_llm(result: ResearchResult, max_tokens_per_source: int = 2500) -> str:
    """Format research results into token-efficient markdown for LLM consumption.

    Includes quality metadata so the host LLM can prioritize which sources to
    deep-read vs skim, and which links to pursue for follow-up research."""
    if not result.sources:
        return f"No results found for: '{result.query}' ({result.engine})"

    quality_summary = ""
    if result.high_quality_count or result.blocked_count:
        parts = []
        if result.high_quality_count:
            parts.append(f"{result.high_quality_count} high-quality")
        if result.blocked_count:
            parts.append(f"{result.blocked_count} blocked")
        quality_summary = f" | {' ,'.join(parts)}"

    lines = [
        f"## Research: {result.query}",
        f"_engine: {result.engine} | sources: {result.total_sources}{quality_summary} | {result.elapsed_ms:.0f}ms_",
    ]

    if result.subqueries and len(result.subqueries) > 1:
        lines.append(f"_subqueries: {', '.join(result.subqueries)}_")

    lines.append("")

    for i, src in enumerate(result.sources, 1):
        # Quality badge
        badge = ""
        if src.quality == "high":
            badge = " **[HIGH]**"
        elif src.quality == "medium":
            badge = " *[med]*"
        elif src.quality == "low":
            badge = " *[low]*"
        elif src.quality == "blocked":
            badge = " **[BLOCKED]**"

        type_hint = f" _({src.content_type})_" if src.content_type else ""

        # Code-aware badges
        code_badges: list[str] = []
        if src.is_api_reference:
            code_badges.append("[API-REF]")
        if src.is_tutorial:
            code_badges.append("[TUTORIAL]")
        if src.is_error_solution:
            code_badges.append("[ERROR-FIX]")
        if src.code_languages:
            code_badges.append(f"[{', '.join(src.code_languages[:3])}]")
        if src.code_to_text_ratio > 0.2:
            code_badges.append(f"[code-heavy {src.code_to_text_ratio:.0%}]")
        code_badge_str = " " + " ".join(code_badges) if code_badges else ""

        # Freshness warning
        freshness_warning = ""
        if src.freshness_days is not None and src.freshness_days > 365:
            freshness_warning = f" [STALE: {src.freshness_days // 30}mo old]"
        elif src.freshness_days is not None:
            freshness_warning = f" [{src.freshness_days}d ago]"
        elif src.published_date:
            freshness_warning = f" [{src.published_date}]"

        # Authority badge
        authority_badge = " [AUTHORITY]" if src.authority_boost else ""

        lines.append(f"### [{i}] {src.title}{badge}{type_hint}{code_badge_str}{freshness_warning}{authority_badge}")
        lines.append(f"URL: {src.url}")

        if src.relevance_score > 0:
            lines.append(f"_relevance: {src.relevance_score:.1f}_")

        # API signature preview
        if src.api_signatures:
            sig_preview = "; ".join(
                s["signature"][:80]
                for s in src.api_signatures[:6]
            )
            lines.append(f"_APIs: {sig_preview}_")

        # Package references
        if src.package_refs:
            pkg_preview = ", ".join(
                f"{p['package']} ({p['language']})"
                for p in src.package_refs[:5]
            )
            lines.append(f"_Packages: {pkg_preview}_")

        # Link suggestions
        if src.external_links:
            link_preview = ", ".join(
                f"[{l['text'][:40]}]({l['url']})"
                for l in src.external_links[:5]
            )
            lines.append(f"_Links: {link_preview}_")

        if src.markdown:
            content = truncate_for_llm(src.markdown, max_tokens_per_source)
        elif src.content:
            content = truncate_for_llm(src.content, max_tokens_per_source)
        elif src.snippet:
            content = src.snippet
        else:
            content = "_no content extracted_"

        lines.append(f"\n{content}\n")

    return "\n".join(lines)
