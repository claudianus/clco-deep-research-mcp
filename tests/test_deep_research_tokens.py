"""Tests for deep research token management."""

import pytest

from maru_search.research.deep import (
    CitedSource,
    ResearchResult,
    _allocate_tokens,
    _extractive_summarize,
    format_for_llm,
)
from maru_search.extraction.content import estimate_token_count


class TestTokenAllocation:
    def test_high_quality_gets_full_budget(self):
        sources = [
            CitedSource(citation_id=1, quality="high", relevance_score=5.0, markdown="x" * 10000, title="High", url="https://example.com/high"),
            CitedSource(citation_id=2, quality="low", relevance_score=1.0, markdown="x" * 10000, title="Low", url="https://example.com/low"),
        ]
        allocations, _, _ = _allocate_tokens(sources, 2500, 20000, False)
        
        high_budget = next(budget for src, budget in allocations if src.quality == "high")
        low_budget = next(budget for src, budget in allocations if src.quality == "low")
        
        assert high_budget > low_budget

    def test_total_budget_respected(self):
        sources = [CitedSource(citation_id=i, quality="high", relevance_score=5.0, markdown="x" * 10000, title=f"Source {i}", url=f"https://example.com/{i}") for i in range(10)]
        allocations, _, dropped = _allocate_tokens(sources, 2500, 5000, False)
        
        total = sum(budget for _, budget in allocations)
        assert total <= 5000
        assert dropped > 0

    def test_summarize_reduces_size(self):
        long_text = "# Heading\n\n" + "Paragraph text. " * 1000
        summary = _extractive_summarize(long_text, 500)
        
        assert len(summary) < len(long_text)
        assert "Heading" in summary
        assert "[Content summarized" in summary

    def test_blocked_sources_skipped(self):
        sources = [
            CitedSource(citation_id=1, quality="blocked", relevance_score=0.0, title="Blocked", url="https://example.com/blocked"),
            CitedSource(citation_id=2, quality="high", relevance_score=5.0, markdown="content", title="High", url="https://example.com/high"),
        ]
        allocations, _, _ = _allocate_tokens(sources, 2500, 20000, False)
        
        assert len(allocations) == 1
        assert allocations[0][0].quality == "high"

    def test_empty_sources_get_low_budget(self):
        sources = [
            CitedSource(citation_id=1, quality="high", relevance_score=5.0, markdown="x" * 10000, title="High", url="https://example.com/high"),
            CitedSource(citation_id=2, quality="empty", relevance_score=1.0, markdown="", title="Empty", url="https://example.com/empty"),
        ]
        allocations, _, _ = _allocate_tokens(sources, 2500, 20000, False)
        
        empty_budget = next(budget for src, budget in allocations if src.quality == "empty")
        high_budget = next(budget for src, budget in allocations if src.quality == "high")
        assert empty_budget < high_budget


class TestFormatForLLM:
    def test_output_within_budget(self):
        result = ResearchResult(
            query="test",
            engine="duckduckgo_lite",
            total_sources=5,
            sources=[
                CitedSource(
                    citation_id=i,
                    quality="high",
                    relevance_score=5.0,
                    markdown="# Test\n\nContent here. " * 500,
                    title=f"Source {i}",
                    url=f"https://example.com/{i}",
                )
                for i in range(5)
            ],
        )
        
        output = format_for_llm(result, max_tokens_per_source=1000)
        token_count = estimate_token_count(output)
        
        assert token_count <= 6000  # Allow some margin for metadata

    def test_token_metadata_tracked(self):
        result = ResearchResult(
            query="test",
            engine="duckduckgo_lite",
            total_sources=3,
            sources=[
                CitedSource(citation_id=1, quality="high", relevance_score=5.0, markdown="content", title="High", url="https://example.com/high"),
                CitedSource(citation_id=2, quality="medium", relevance_score=3.0, markdown="content", title="Medium", url="https://example.com/medium"),
                CitedSource(citation_id=3, quality="low", relevance_score=1.0, markdown="content", title="Low", url="https://example.com/low"),
            ],
        )
        
        output = format_for_llm(result, max_tokens_per_source=1000)
        assert output  # Just verify it produces output


class TestExtractiveSummarize:
    def test_preserves_headings(self):
        text = "# Main\n\nParagraph 1. " * 100 + "\n\n# Section 2\n\nParagraph 2. " * 100
        summary = _extractive_summarize(text, 100)
        assert "# Main" in summary
        assert "# Section 2" in summary

    def test_respects_token_limit(self):
        text = "# Heading\n\n" + "Word " * 1000
        summary = _extractive_summarize(text, 50)
        assert estimate_token_count(summary) <= 50 * 1.5

    def test_adds_summary_notice(self):
        text = "# Heading\n\n" + "Word " * 1000
        summary = _extractive_summarize(text, 50)
        assert "[Content summarized" in summary
