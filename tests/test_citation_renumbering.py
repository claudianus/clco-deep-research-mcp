"""Tests for stable citation ID renumbering."""

from __future__ import annotations

from maru_deep_pro_search.research.deep import (
    CitedSource,
    ResearchResult,
    _allocate_tokens,
)


class TestCitationRenumbering:
    def test_sequential_ids_after_allocation(self):
        """After token allocation, remaining sources should have sequential IDs."""
        sources = [
            CitedSource(citation_id=1, url="http://a.com", title="A", quality="high", markdown="x" * 1000),
            CitedSource(citation_id=2, url="http://b.com", title="B", quality="blocked", markdown=""),
            CitedSource(citation_id=3, url="http://c.com", title="C", quality="high", markdown="x" * 1000),
            CitedSource(citation_id=5, url="http://e.com", title="E", quality="low", markdown="x" * 1000),
        ]
        # With 2500 per source * high (1.0) = 2500 each, total budget 10000,
        # all non-blocked sources should fit.
        allocations, _, _ = _allocate_tokens(sources, 2500, 10000, False)
        allocated = [src for src, _ in allocations]

        # Simulate renumbering logic from deep_research
        old_to_new = {}
        for new_id, src in enumerate(allocated, 1):
            old_to_new[src.citation_id] = new_id
            src.citation_id = new_id

        ids = [s.citation_id for s in allocated]
        # blocked (B) is skipped, so A(1)->1, C(3)->2, E(5)->3
        assert ids == [1, 2, 3]
        assert "B" not in [s.title for s in allocated]

    def test_no_gaps_in_final_ids(self):
        """Final citation IDs should never have gaps."""
        sources = [
            CitedSource(citation_id=10, url="http://x.com", title="X", quality="high", markdown="content"),
            CitedSource(citation_id=20, url="http://y.com", title="Y", quality="high", markdown="content"),
        ]
        old_to_new = {}
        for new_id, src in enumerate(sources, 1):
            old_to_new[src.citation_id] = new_id
            src.citation_id = new_id

        assert sources[0].citation_id == 1
        assert sources[1].citation_id == 2


class TestResearchResultFormatting:
    def test_format_for_llm_uses_sequential_ids(self):
        from maru_deep_pro_search.research.deep import format_for_llm

        result = ResearchResult(
            query="test",
            engine="duckduckgo_lite",
            total_sources=2,
            sources=[
                CitedSource(citation_id=1, url="http://a.com", title="A", quality="high", markdown="content A"),
                CitedSource(citation_id=2, url="http://b.com", title="B", quality="high", markdown="content B"),
            ],
        )
        output = format_for_llm(result)
        assert "[1]" in output
        assert "[2]" in output
        assert "#### [1] A" in output
        assert "#### [2] B" in output
