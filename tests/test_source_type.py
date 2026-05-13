"""Tests for source type classification in search engines and research pipeline."""

from __future__ import annotations

from maru_deep_pro_search.engines.base import (
    SearchResult,
    SourceType,
    guess_source_type_and_primary,
)
from maru_deep_pro_search.research.ranker import merge_results


class TestGuessSourceTypeAndPrimary:
    def test_github(self):
        st, prim = guess_source_type_and_primary("https://github.com/openai/gpt-4")
        assert st == SourceType.GITHUB_REPO
        assert prim is True

    def test_official_docs(self):
        st, prim = guess_source_type_and_primary("https://react.dev/learn/thinking-in-react")
        assert st == SourceType.OFFICIAL_DOCS
        assert prim is True

    def test_blog_not_primary(self):
        st, prim = guess_source_type_and_primary("https://medium.com/@user/article")
        assert st == SourceType.BLOG_REVIEW
        assert prim is False

    def test_stackoverflow_primary(self):
        st, prim = guess_source_type_and_primary("https://stackoverflow.com/questions/123")
        assert st == SourceType.FORUM
        assert prim is True


class TestMergeResultsSourceType:
    def test_auto_classifies_missing_source_type(self):
        results = {
            "duckduckgo": [
                SearchResult(
                    title="Python Docs",
                    url="https://docs.python.org/3/",
                    snippet="Python documentation",
                    source_type=SourceType.UNKNOWN,
                    is_primary=False,
                ),
            ]
        }
        ranked = merge_results(results, "python docs")
        assert len(ranked) == 1
        assert ranked[0].result.source_type == SourceType.OFFICIAL_DOCS
        assert ranked[0].result.is_primary is True

    def test_preserves_existing_source_type(self):
        results = {
            "duckduckgo": [
                SearchResult(
                    title="My Blog",
                    url="https://medium.com/article",
                    snippet="blog post",
                    source_type=SourceType.BLOG_REVIEW,
                    is_primary=False,
                ),
            ]
        }
        ranked = merge_results(results, "blog")
        assert ranked[0].result.source_type == SourceType.BLOG_REVIEW
        assert ranked[0].result.is_primary is False
