"""Tests for configuration system."""

import os

from maru_deep_pro_search.config import DEFAULT_CONFIG, SearchConfig


class TestSearchConfig:
    def test_default_values(self):
        cfg = SearchConfig()
        assert cfg.default_engine == "duckduckgo_lite"
        assert cfg.max_results_per_query == 10
        assert cfg.max_concurrent_fetches == 5

    def test_from_env(self):
        os.environ["MARU_SEARCH_ENGINE"] = "duckduckgo"
        os.environ["MARU_SEARCH_MAX_RESULTS"] = "20"
        cfg = SearchConfig.from_env()
        assert cfg.default_engine == "duckduckgo"
        assert cfg.max_results_per_query == 20
        # Clean up
        del os.environ["MARU_SEARCH_ENGINE"]
        del os.environ["MARU_SEARCH_MAX_RESULTS"]

    def test_global_default_exists(self):
        assert DEFAULT_CONFIG is not None
        assert isinstance(DEFAULT_CONFIG, SearchConfig)
