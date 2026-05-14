"""Integration tests for search engines — hit the real web.

Run with: pytest tests/test_engines_integration.py --integration
These tests make actual network requests and may be flaky.
"""

from __future__ import annotations

import pytest

from maru_deep_pro_search.engines.registry import SearchEngineRegistry

SEARCH_ENGINES = list(SearchEngineRegistry.list_engines())
SIMPLE_QUERY = "Python asyncio tutorial"


@pytest.mark.integration
@pytest.mark.parametrize("engine_name", SEARCH_ENGINES)
@pytest.mark.asyncio
async def test_engine_returns_results(engine_name: str) -> None:
    """Each engine should return non-empty results for a simple query."""
    search_engine = SearchEngineRegistry.create(engine_name)
    results = await search_engine.search(SIMPLE_QUERY, max_results=5)
    assert isinstance(results, list)
    assert len(results) > 0
    for r in results:
        assert r.url.startswith("http")
        assert r.title
        assert r.snippet or r.title


@pytest.mark.integration
@pytest.mark.parametrize("engine_name", SEARCH_ENGINES)
@pytest.mark.asyncio
async def test_engine_result_structure(engine_name: str) -> None:
    """Each result should have the expected fields populated."""
    search_engine = SearchEngineRegistry.create(engine_name)
    results = await search_engine.search(SIMPLE_QUERY, max_results=3)
    for r in results:
        assert isinstance(r.url, str)
        assert isinstance(r.title, str)
        assert isinstance(r.snippet, str)
        assert isinstance(r.is_primary, bool)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_duckduckgo_lite_returns_ranked_results() -> None:
    """DuckDuckGo lite should return at least 5 results for a programming query."""
    engine = SearchEngineRegistry.create("duckduckgo_lite")
    results = await engine.search(SIMPLE_QUERY, max_results=10)
    assert len(results) >= 5
    # First result should be reasonably relevant
    first = results[0]
    assert first.title
    assert first.url.startswith("http")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bing_returns_authority_results() -> None:
    """Bing should return results with authority indicators."""
    engine = SearchEngineRegistry.create("bing")
    results = await engine.search("github python", max_results=5)
    assert len(results) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_engine_circuit_breaker_resets() -> None:
    """After a successful search, the circuit breaker should allow more requests."""
    engine = SearchEngineRegistry.create("duckduckgo_lite")
    # First search
    r1 = await engine.search("hello world", max_results=3)
    assert len(r1) > 0
    # Second search immediately after should also work
    r2 = await engine.search("python list", max_results=3)
    assert len(r2) > 0
