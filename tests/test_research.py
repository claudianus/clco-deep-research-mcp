"""Tests for deep research pipeline functions."""

from __future__ import annotations

import pytest

from maru_deep_pro_search.research.deep import _probe_network, _filter_slow_domains
from maru_deep_pro_search.engines.duckduckgo import DuckDuckGoEngine


class TestProbeNetwork:
    @pytest.mark.asyncio
    async def test_probe_returns_dict(self):
        engine = DuckDuckGoEngine()
        result = await _probe_network(engine)
        assert isinstance(result, dict)
        assert "ok" in result
        assert "latency_ms" in result
        assert "slow" in result
        assert isinstance(result["slow"], bool)


class TestFilterSlowDomains:
    def test_no_store_returns_all(self):
        urls = ["https://github.com/repo", "https://example.com/page"]
        result = _filter_slow_domains(urls, store=None)
        assert result == urls

    def test_empty_list(self):
        assert _filter_slow_domains([], store=None) == []
