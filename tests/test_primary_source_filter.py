"""Tests for primary_sources_only filtering."""

from __future__ import annotations

from maru_deep_pro_search.engines.base import SearchResult, SourceType
from maru_deep_pro_search.research.ranker import merge_results


class TestPrimarySourceFilter:
    def test_merge_results_respects_primary_flag(self):
        """Results already flagged as primary should stay primary."""
        results = {
            "duckduckgo": [
                SearchResult(
                    title="GitHub Repo",
                    url="https://github.com/user/repo",
                    snippet="code",
                    source_type=SourceType.GITHUB_REPO,
                    is_primary=True,
                ),
                SearchResult(
                    title="Medium Blog",
                    url="https://medium.com/article",
                    snippet="blog",
                    source_type=SourceType.BLOG_REVIEW,
                    is_primary=False,
                ),
            ]
        }
        ranked = merge_results(results, "test")
        primary = [r for r in ranked if r.result.is_primary]
        non_primary = [r for r in ranked if not r.result.is_primary]

        assert len(primary) == 1
        assert primary[0].result.title == "GitHub Repo"
        assert len(non_primary) == 1
        assert non_primary[0].result.title == "Medium Blog"

    def test_auto_classification_sets_primary_correctly(self):
        """Unclassified results should be auto-classified with correct primary status."""
        results = {
            "duckduckgo": [
                SearchResult(
                    title="Python Docs",
                    url="https://docs.python.org/3/library/os.html",
                    snippet="official docs",
                    source_type=SourceType.UNKNOWN,
                    is_primary=False,
                ),
                SearchResult(
                    title="Random Blog",
                    url="https://someblog.com/post",
                    snippet="opinion",
                    source_type=SourceType.UNKNOWN,
                    is_primary=False,
                ),
            ]
        }
        ranked = merge_results(results, "python os")
        docs = next(r for r in ranked if "docs.python.org" in r.result.url)
        blog = next(r for r in ranked if "someblog.com" in r.result.url)

        assert docs.result.source_type == SourceType.OFFICIAL_DOCS
        assert docs.result.is_primary is True
        assert blog.result.is_primary is False
