"""Intelligent ranking engine for multi-source search results.

Combines BM25 relevance scoring with metadata-based quality signals
to produce Perplexity-level result ranking."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ..engines.base import SearchResult, PageContent, ContentType
from ..utils.url import is_authority_domain, normalize_url
from ..research.expander import extract_keywords

logger = logging.getLogger(__name__)

# Metadata scoring weights
_AUTHORITY_BOOST = 2.0
_FRESHNESS_BOOST = 1.5
_DOCS_TYPE_BOOST = 1.5
_ARTICLE_TYPE_BOOST = 1.0
_CODE_TYPE_BOOST = 0.8
_FORUM_TYPE_BOOST = 0.6
_CROSS_ENGINE_BOOST = 0.5
_SNIPPET_QUALITY_BOOST = 1.0
_POSITION_DECAY = 0.1


@dataclass
class RankedResult:
    """A search result with comprehensive ranking metadata."""

    result: SearchResult
    bm25_score: float = 0.0
    metadata_score: float = 0.0
    final_score: float = 0.0
    citation_id: int = 0


def _compute_bm25_scores(query: str, results: list[SearchResult]) -> dict[str, float]:
    """Compute BM25 scores for results against the query."""
    try:
        from rank_bm25 import BM25Okapi
    except ImportError:
        logger.debug("rank-bm25 not available, skipping BM25 scoring")
        return {normalize_url(r.url): 0.0 for r in results}

    if not results:
        return {}

    # Tokenize query and documents
    query_tokens = extract_keywords(query)
    if not query_tokens:
        query_tokens = query.lower().split()

    corpus = []
    url_map = {}
    for r in results:
        doc = f"{r.title} {r.snippet} {r.domain}".lower()
        tokens = doc.split()
        corpus.append(tokens)
        url_map[normalize_url(r.url)] = len(corpus) - 1

    try:
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(query_tokens)
    except Exception as exc:
        logger.warning("BM25 scoring failed: %s", exc)
        return {normalize_url(r.url): 0.0 for r in results}

    return {
        normalize_url(r.url): scores[url_map.get(normalize_url(r.url), 0)]
        for r in results
    }


def _score_metadata(result: SearchResult) -> float:
    """Score a result based on metadata quality signals."""
    score = 0.0

    # Authority boost
    if is_authority_domain(result.url):
        score += _AUTHORITY_BOOST

    # Content type preference
    if result.likely_content_type == ContentType.DOCUMENTATION:
        score += _DOCS_TYPE_BOOST
    elif result.likely_content_type == ContentType.ARTICLE:
        score += _ARTICLE_TYPE_BOOST
    elif result.likely_content_type == ContentType.CODE:
        score += _CODE_TYPE_BOOST
    elif result.likely_content_type == ContentType.FORUM:
        score += _FORUM_TYPE_BOOST

    # URL suggests docs
    if result.url_suggests_docs:
        score += 1.0

    # Snippet quality (length heuristic)
    if result.snippet:
        score += min(len(result.snippet) / 500, 1.0) * _SNIPPET_QUALITY_BOOST

    # Position bonus with decay
    score += max(0, (10 - result.position) / 10) * (1 - result.position * _POSITION_DECAY)

    # Cross-engine confirmation boost
    if len(result.engines_found) > 1:
        score += _CROSS_ENGINE_BOOST * min(len(result.engines_found), 3)

    return score


def merge_results(
    engine_results: dict[str, list[SearchResult]],
    query: str,
) -> list[RankedResult]:
    """Merge results from multiple engines, deduplicate, and rank.

    Args:
        engine_results: Dict mapping engine name -> list of SearchResult.
        query: Original query for BM25 scoring.

    Returns:
        List of RankedResult sorted by final_score descending.
    """
    # Deduplicate and track which engines found each URL
    url_to_result: dict[str, SearchResult] = {}
    url_to_engines: dict[str, list[str]] = {}

    for engine_name, results in engine_results.items():
        for r in results:
            norm = normalize_url(r.url)
            if norm not in url_to_result:
                url_to_result[norm] = r
                url_to_engines[norm] = []
            url_to_engines[norm].append(engine_name)

    # Update results with cross-engine metadata
    merged: list[SearchResult] = []
    for norm, r in url_to_result.items():
        r.engines_found = url_to_engines.get(norm, [])
        r.cross_engine_score = min(len(r.engines_found) * _CROSS_ENGINE_BOOST, 1.5)
        merged.append(r)

    # Compute BM25 scores
    bm25_scores = _compute_bm25_scores(query, merged)

    # Build ranked results
    ranked: list[RankedResult] = []
    for r in merged:
        bm25 = bm25_scores.get(normalize_url(r.url), 0.0)
        meta = _score_metadata(r)
        # Normalize BM25 to be comparable with metadata score
        # (BM25 scores can be 0-30+, we compress to 0-5 range)
        normalized_bm25 = min(bm25 / 5.0, 5.0) if bm25 > 0 else 0.0
        final = normalized_bm25 + meta + r.cross_engine_score

        ranked.append(RankedResult(
            result=r,
            bm25_score=normalized_bm25,
            metadata_score=meta,
            final_score=final,
        ))

    # Sort by final score descending
    ranked.sort(key=lambda x: x.final_score, reverse=True)

    # Assign citation IDs
    for i, rr in enumerate(ranked, 1):
        rr.citation_id = i
        rr.result.citation_id = i

    logger.debug(
        "Merged %d results from %d engines, top score: %.2f",
        len(ranked),
        len(engine_results),
        ranked[0].final_score if ranked else 0,
    )

    return ranked


def rank_pages(pages: list[PageContent], query: str) -> list[PageContent]:
    """Rank fetched pages by quality and relevance.

    Args:
        pages: List of fetched PageContent.
        query: Original query.

    Returns:
        Pages sorted by combined quality+relevance score.
    """
    query_keywords = set(extract_keywords(query))

    scored_pages: list[tuple[PageContent, float]] = []
    for p in pages:
        score = 0.0

        # Quality score
        if p.quality.value == "high":
            score += 3.0
        elif p.quality.value == "medium":
            score += 1.5
        elif p.quality.value == "low":
            score += 0.5

        # Authority
        if is_authority_domain(p.url):
            score += 2.0

        # Keyword overlap in title/content
        text = f"{p.title} {p.text[:500]}".lower()
        overlap = sum(1 for kw in query_keywords if kw in text)
        score += overlap * 0.5

        # Content type preference
        if p.content_type == ContentType.DOCUMENTATION:
            score += 1.0
        elif p.content_type == ContentType.ARTICLE:
            score += 0.5

        # Freshness
        if p.freshness_days is not None and p.freshness_days < 30:
            score += 1.0
        elif p.freshness_days is not None and p.freshness_days < 90:
            score += 0.5

        # Code richness (for dev queries)
        if p.code_to_text_ratio > 0.2:
            score += 0.5

        scored_pages.append((p, score))

    scored_pages.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in scored_pages]
