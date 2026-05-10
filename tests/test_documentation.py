"""Tests for documentation improvements."""

from maru_search.tools import tool_fetch_page, tool_stealthy_fetch


class TestDocumentation:
    def test_fetch_page_docstring_has_stealth_guidance(self):
        assert "stealthy_fetch" in tool_fetch_page.__doc__
        assert "When to use" in tool_fetch_page.__doc__

    def test_stealthy_fetch_docstring_has_tradeoffs(self):
        assert "Trade-offs" in tool_stealthy_fetch.__doc__
        assert "slower" in tool_stealthy_fetch.__doc__.lower()

    def test_fetch_page_has_use_cases(self):
        assert "Use Cases" in tool_fetch_page.__doc__

    def test_stealthy_fetch_has_recommendation(self):
        assert "Recommendation" in tool_stealthy_fetch.__doc__
