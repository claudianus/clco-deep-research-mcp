"""Tests for query expansion module."""

from maru_deep_pro_search.research.expander import expand_query, extract_keywords


class TestExpandQuery:
    def test_expand_basic(self):
        subqueries = expand_query("python asyncio", max_subqueries=3)
        assert len(subqueries) >= 1
        assert "python asyncio" in subqueries

    def test_expand_code_query(self):
        subqueries = expand_query("rust error handling", max_subqueries=5)
        assert len(subqueries) > 1
        # Should include troubleshooting angle
        assert any("error" in sq.lower() or "fix" in sq.lower() for sq in subqueries)

    def test_expand_tutorial_query(self):
        subqueries = expand_query("react hooks tutorial", max_subqueries=5)
        assert len(subqueries) > 1
        # Should include tutorial angle
        assert any("tutorial" in sq.lower() or "guide" in sq.lower() for sq in subqueries)

    def test_expand_respects_max(self):
        subqueries = expand_query("machine learning", max_subqueries=2)
        assert len(subqueries) <= 2

    def test_expand_original_first(self):
        subqueries = expand_query("docker containers", max_subqueries=5)
        assert subqueries[0] == "docker containers"


class TestExtractKeywords:
    def test_basic_keywords(self):
        keywords = extract_keywords("python asyncio tutorial")
        assert "python" in keywords
        assert "asyncio" in keywords

    def test_removes_stop_words(self):
        keywords = extract_keywords("how to use python asyncio")
        assert "how" not in keywords
        assert "to" not in keywords
        assert "use" not in keywords
        assert "python" in keywords
        assert "asyncio" in keywords

    def test_empty_query(self):
        keywords = extract_keywords("")
        assert keywords == []
