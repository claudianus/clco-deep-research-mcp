"""Enhanced deep research pipeline with citations and answer synthesis.

Perplexity-level search: multi-engine crawling, intelligent ranking,
citation-native output, and rule-based answer synthesis."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

from ..engines.base import SearchResult, PageContent, ContentType, ExtractionQuality
from ..engines.registry import SearchEngineRegistry
from ..exceptions import MaruSearchError, NetworkError, ParseError
from ..utils.url import should_skip_url, deduplicate_urls, is_authority_domain
from ..utils.retry import with_retry
from ..extraction.content import truncate_for_llm
from .expander import expand_query
from .ranker import merge_results, rank_pages, RankedResult

logger = logging.getLogger(__name__)


@dataclass
class CitedSource:
    """A source with citation ID for answer synthesis."""

    citation_id: int
    url: str
    title: str
    snippet: str = ""
    content: str = ""
    markdown: str = ""
    content_length: int = 0
    fetch_ms: float = 0.0
    quality: str = ""
    content_type: str = ""
    internal_links: list[dict] = field(default_factory=list)
    external_links: list[dict] = field(default_factory=list)
    code_languages: list[str] = field(default_factory=list)
    api_signatures: list[dict] = field(default_factory=list)
    package_refs: list[dict] = field(default_factory=list)
    code_to_text_ratio: float = 0.0
    published_date: str = ""
    freshness_days: Optional[int] = None
    is_api_reference: bool = False
    is_tutorial: bool = False
    is_error_solution: bool = False
    relevance_score: float = 0.0
    authority_boost: bool = False
    engines_found: list[str] = field(default_factory=list)


@dataclass
class AnswerResult:
    """Synthesized answer with citations."""

    answer: str
    citations: list[CitedSource]
    subqueries: list[str]
    elapsed_ms: float = 0.0


@dataclass
class ResearchResult:
    """Full research result with sources and metadata."""

    query: str
    engine: str
    total_sources: int
    sources: list[CitedSource] = field(default_factory=list)
    elapsed_ms: float = 0.0
    high_quality_count: int = 0
    blocked_count: int = 0
    subqueries: list[str] = field(default_factory=list)
    total_tokens_used: int = 0
    tokens_allocated: int = 0
    sources_summarized: int = 0
    sources_dropped: int = 0
    # Answer synthesis
    synthesized_answer: str = ""
    has_answer: bool = False
    # Follow-up suggestions
    suggested_followups: list[str] = field(default_factory=list)


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
    synthesize_answer: bool = True,
) -> ResearchResult:
    """End-to-end deep research pipeline with query expansion and multi-pass crawling.

    Args:
        query: Search query.
        engine: Search engine variant (registered in SearchEngineRegistry).
        max_sources: Max unique pages to crawl.
        follow_links: If True, follow one level of external links.
        stealth: Use StealthyFetcher for anti-bot bypass.
        expand_queries: If True, generate subqueries for broader coverage.
        max_tokens_per_source: Token budget per source.
        max_total_tokens: Total output token budget.
        summarize: Enable extractive summarization for over-budget scenarios.
        synthesize_answer: Generate a synthesized answer from sources.
    """
    t0 = time.monotonic()

    # Phase 0: Engine selection
    # If default engine, use metadata-based recommendation for multi-engine search
    if not SearchEngineRegistry.is_registered(engine):
        logger.warning("Engine '%s' not registered, falling back to duckduckgo_lite", engine)
        engine = "duckduckgo_lite"

    if engine == "duckduckgo_lite":
        engines = SearchEngineRegistry.recommend_engines(query, count=2)
        logger.info("Auto-selected engines: %s", engines)
    else:
        engines = [engine]

    primary_engine = SearchEngineRegistry.create(engines[0])

    # Phase 1: Query expansion
    subqueries = [query]
    if expand_queries:
        subqueries = expand_query(query, max_subqueries=5)

    # Phase 2: Search across engines
    # Strategy: run ALL subqueries on primary engine (depth)
    #           run ORIGINAL query on secondary engines (breadth/diversification)
    engine_results: dict[str, list[SearchResult]] = {e: [] for e in engines}

    for sq in subqueries:
        # Primary engine gets all subqueries for depth
        try:
            results = await with_retry(
                primary_engine.search,
                sq,
                max_results=max_sources * 2,
                max_attempts=2,
                retryable_exceptions=(NetworkError, ParseError),
            )
            engine_results[engines[0]].extend(results)
            logger.debug("Subquery '%s' on %s returned %d results", sq, engines[0], len(results))
        except Exception as exc:
            logger.warning("Subquery '%s' on %s failed: %s", sq, engines[0], exc)
            continue

    # Secondary engines only search the original query (breadth)
    for eng_name in engines[1:]:
        try:
            secondary = SearchEngineRegistry.create(eng_name)
            results = await with_retry(
                secondary.search,
                query,
                max_results=max_sources * 2,
                max_attempts=2,
                retryable_exceptions=(NetworkError, ParseError),
            )
            engine_results[eng_name].extend(results)
            logger.debug("Original query on %s returned %d results", eng_name, len(results))
        except Exception as exc:
            logger.warning("Engine %s failed for original query: %s", eng_name, exc)
            continue

    # Flatten for empty check
    all_results = [r for results in engine_results.values() for r in results]
    if not all_results:
        return ResearchResult(
            query=query,
            engine=engines[0],
            total_sources=0,
            subqueries=subqueries,
        )

    # Phase 3: Deduplicate, score, and rank (multi-engine merge)
    ranked = merge_results(engine_results, query)

    # Phase 4: Crawl top pages (use primary engine for fetching)
    urls_to_fetch = [rr.result.url for rr in ranked[:max_sources]]
    pages = await _fetch_pages(urls_to_fetch, primary_engine, stealth=stealth)
    pages = rank_pages(pages, query)

    # Build cited sources
    sources: list[CitedSource] = []
    high_quality = 0
    blocked = 0

    for i, rr in enumerate(ranked[:max_sources], 1):
        sr = rr.result
        matched = next(
            (p for p in pages if normalize_url(p.url) == normalize_url(sr.url)),
            None,
        )

        if matched and matched.quality == ExtractionQuality.BLOCKED:
            blocked += 1

        if matched and matched.content_length > 100:
            if matched.quality == ExtractionQuality.HIGH:
                high_quality += 1

            sources.append(CitedSource(
                citation_id=rr.citation_id,
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
                relevance_score=rr.final_score,
                authority_boost=is_authority_domain(matched.url),
                engines_found=sr.engines_found,
            ))
        elif sr.snippet:
            # Fallback to snippet-only source
            sources.append(CitedSource(
                citation_id=rr.citation_id,
                url=sr.url,
                title=sr.title,
                snippet=sr.snippet,
                quality="empty",
                content_type=sr.likely_content_type.value if sr.likely_content_type else "",
                relevance_score=rr.final_score,
                authority_boost=is_authority_domain(sr.url),
                engines_found=sr.engines_found,
            ))

    # Phase 5: Follow links (optional)
    if follow_links and len(sources) < max_sources:
        fetched_urls = {normalize_url(s.url) for s in sources}
        all_external: list[str] = []

        for src in sources:
            for link in src.external_links:
                u = link.get("url", "")
                if u and not should_skip_url(u) and normalize_url(u) not in fetched_urls:
                    all_external.append(u)

        all_external = deduplicate_urls(all_external)
        new_urls = all_external[:max_sources - len(sources)]

        if new_urls:
            linked_pages = await _fetch_pages(new_urls, search_engine, stealth=True)
            linked_pages = rank_pages(linked_pages, query)
            for lp in linked_pages:
                if lp.content_length > 200:
                    if lp.quality == ExtractionQuality.HIGH:
                        high_quality += 1

                    next_id = len(sources) + 1
                    sources.append(CitedSource(
                        citation_id=next_id,
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
                        relevance_score=0.5,
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
        if summarize and len(src.markdown) > budget * 4:
            src.markdown = _extractive_summarize(src.markdown, budget)
        allocated_sources.append(src)

    # Answer synthesis
    synthesized = ""
    if synthesize_answer and allocated_sources:
        synthesized = _synthesize_answer(query, allocated_sources)

    # Gap detection for follow-up research
    suggested_followups = detect_gaps(query, allocated_sources)

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
        synthesized_answer=synthesized,
        has_answer=bool(synthesized),
        suggested_followups=suggested_followups,
    )


def _synthesize_answer(query: str, sources: list[CitedSource]) -> str:
    """Generate a rule-based synthesized answer from sources.

    Uses headings and first paragraphs to build a structured summary
    with inline citations like [1], [2].
    """
    if not sources:
        return ""

    # Collect key insights from each source
    insights: list[str] = []
    for src in sources:
        text = src.markdown or src.content or src.snippet
        if not text:
            continue

        # Extract first meaningful paragraph and any headings
        lines = text.split("\n")
        paragraphs = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
        headings = [l.strip("# ").strip() for l in lines if l.startswith("#")]

        # Use heading + first paragraph as insight
        insight_parts = []
        if headings:
            insight_parts.append(headings[0])
        if paragraphs:
            # Take first paragraph up to 200 chars
            para = paragraphs[0][:200]
            if len(paragraphs[0]) > 200:
                para += "..."
            insight_parts.append(para)

        if insight_parts:
            insights.append(
                f"- {' — '.join(insight_parts)} [{src.citation_id}]"
            )

    if not insights:
        return ""

    # Build synthesized answer
    answer_parts = [
        f"### Quick Answer: {query}",
        "",
        "Based on the search results, here are the key findings:",
        "",
    ]
    answer_parts.extend(insights[:6])  # Max 6 insights
    answer_parts.append("")
    answer_parts.append("---")
    answer_parts.append("")

    return "\n".join(answer_parts)


def _allocate_tokens(
    sources: list[CitedSource],
    max_tokens_per_source: int,
    max_total_tokens: int,
    summarize: bool,
) -> tuple[list[tuple[CitedSource, int]], int, int]:
    """Allocate tokens to sources based on quality scores."""
    if not sources:
        return [], 0, 0

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

        quality_mult = quality_weights.get(src.quality, 0.5)
        budget = int(max_tokens_per_source * quality_mult)

        if total_allocated + budget > max_total_tokens:
            if summarize and src.quality in ("medium", "low"):
                budget = int(budget * 0.5)
                if total_allocated + budget <= max_total_tokens:
                    allocations.append((src, budget))
                    total_allocated += budget
                    sources_summarized += 1
                    continue

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

    headings = extract_headings(markdown)

    summary_parts = []
    lines = markdown.split('\n')
    current_section = []
    in_section = False

    for line in lines:
        if line.startswith('#'):
            if current_section:
                summary_parts.extend(current_section[:2])
                current_section = []
            in_section = True
            current_section.append(line)
        elif in_section and line.strip() and not line.startswith('#'):
            current_section.append(line)
            if len(current_section) >= 3:
                in_section = False

    if current_section:
        summary_parts.extend(current_section[:2])

    summary = '\n\n'.join(summary_parts)

    if estimate_token_count(summary) > max_tokens:
        summary = truncate_for_llm(summary, max_tokens)

    return summary + "\n\n_[Content summarized for brevity]_"


async def _fetch_pages(
    urls: list[str],
    engine,
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


def format_for_llm(
    result: ResearchResult,
    max_tokens_per_source: int = 2500,
    max_total_tokens: int = 20000,
    summarize: bool = False,
) -> str:
    """Format research results into token-efficient markdown with citations.

    Perplexity-style output with inline citations [1], [2] and
    quality metadata for the host LLM."""
    if not result.sources:
        return f"No results found for: '{result.query}' ({result.engine})"

    lines: list[str] = []

    # Header with stats
    quality_summary = ""
    if result.high_quality_count or result.blocked_count:
        parts = []
        if result.high_quality_count:
            parts.append(f"{result.high_quality_count} high-quality")
        if result.blocked_count:
            parts.append(f"{result.blocked_count} blocked")
        quality_summary = f" | {' ,'.join(parts)}"

    lines.append(f"## Research: {result.query}")
    lines.append(
        f"_engine: {result.engine} | sources: {result.total_sources}{quality_summary} | {result.elapsed_ms:.0f}ms_"
    )

    if result.subqueries and len(result.subqueries) > 1:
        lines.append(f"_subqueries: {', '.join(result.subqueries)}_")

    lines.append("")

    # Synthesized answer (Perplexity-style)
    if result.has_answer and result.synthesized_answer:
        lines.append(result.synthesized_answer)

    # Suggested follow-ups
    if result.suggested_followups:
        lines.append("### Suggested Follow-up Research")
        lines.append("")
        for sq in result.suggested_followups:
            lines.append(f"- {sq}")
        lines.append("")

    # Sources with citations
    lines.append("### Sources")
    lines.append("")

    for src in result.sources:
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

        # Freshness
        freshness = ""
        if src.freshness_days is not None and src.freshness_days > 365:
            freshness = f" [STALE: {src.freshness_days // 30}mo old]"
        elif src.freshness_days is not None:
            freshness = f" [{src.freshness_days}d ago]"
        elif src.published_date:
            freshness = f" [{src.published_date}]"

        authority = " [AUTHORITY]" if src.authority_boost else ""
        cross_engine = ""
        if len(src.engines_found) > 1:
            cross_engine = f" [✓ {len(src.engines_found)} engines]"

        lines.append(
            f"#### [{src.citation_id}] {src.title}{badge}{type_hint}{code_badge_str}{freshness}{authority}{cross_engine}"
        )
        lines.append(f"URL: {src.url}")

        if src.relevance_score > 0:
            lines.append(f"_relevance: {src.relevance_score:.1f}_")

        if src.api_signatures:
            sig_preview = "; ".join(
                s["signature"][:80] for s in src.api_signatures[:6]
            )
            lines.append(f"_APIs: {sig_preview}_")

        if src.package_refs:
            pkg_preview = ", ".join(
                f"{p['package']} ({p['language']})" for p in src.package_refs[:5]
            )
            lines.append(f"_Packages: {pkg_preview}_")

        if src.external_links:
            link_preview = ", ".join(
                f"[{l['text'][:40]}]({l['url']})" for l in src.external_links[:5]
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


def normalize_url(url: str) -> str:
    """Simple normalization for deduplication."""
    from ..utils.url import normalize_url as _normalize
    return _normalize(url)
