"""Tests for exception hierarchy."""

import pytest
from clco_deep_research.exceptions import (
    ResearchError,
    NetworkError,
    RateLimitError,
    BlockedError,
    ParseError,
    NoResultsError,
    ExtractionError,
)


class TestResearchError:
    def test_base_error(self):
        err = ResearchError("test error")
        assert str(err) == "test error"
        assert err.retryable is False

    def test_retryable_error(self):
        err = ResearchError("retry me", retryable=True)
        assert err.retryable is True

    def test_suggested_engine(self):
        err = ResearchError("failed", suggested_engine="duckduckgo_lite")
        assert err.suggested_engine == "duckduckgo_lite"


class TestNetworkError:
    def test_is_retryable(self):
        err = NetworkError("connection failed")
        assert err.retryable is True


class TestBlockedError:
    def test_is_retryable(self):
        err = BlockedError("captcha")
        assert err.retryable is True

    def test_has_fallback(self):
        err = BlockedError("blocked")
        assert err.suggested_engine == "duckduckgo_lite"


class TestNoResultsError:
    def test_not_retryable(self):
        err = NoResultsError("nothing found")
        assert err.retryable is False
