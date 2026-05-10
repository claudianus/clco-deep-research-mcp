"""Tests for exception hierarchy."""

import pytest
from maru_search.exceptions import (
    MaruSearchError,
    NetworkError,
    RateLimitError,
    BlockedError,
    ParseError,
    NoResultsError,
    ExtractionError,
)


class TestMaruSearchError:
    def test_base_error(self):
        err = MaruSearchError("test error")
        assert str(err) == "test error"
        assert err.retryable is False

    def test_retryable_error(self):
        err = MaruSearchError("retry me", retryable=True)
        assert err.retryable is True

    def test_suggested_engine(self):
        err = MaruSearchError("failed", suggested_engine="duckduckgo_lite")
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
        assert err.suggested_engine == "duckduckgo"


class TestNoResultsError:
    def test_not_retryable(self):
        err = NoResultsError("nothing found")
        assert err.retryable is False
