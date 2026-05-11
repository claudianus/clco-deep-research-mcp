"""Tests for URL utilities."""

from maru_deep_pro_search.utils.url import (
    deduplicate_urls,
    get_domain,
    is_authority_domain,
    normalize_url,
    resolve_redirect,
    should_skip_url,
)


class TestNormalizeUrl:
    def test_strip_tracking_params(self):
        url = "https://example.com/page?utm_source=google&utm_medium=email"
        assert normalize_url(url) == "https://example.com/page"

    def test_remove_fragment(self):
        url = "https://example.com/page#section"
        assert normalize_url(url) == "https://example.com/page"

    def test_normalize_trailing_slash(self):
        assert normalize_url("https://example.com/") == "https://example.com"

    def test_keep_non_tracking_params(self):
        url = "https://example.com/search?q=python"
        assert normalize_url(url) == "https://example.com/search?q=python"


class TestShouldSkipUrl:
    def test_skip_youtube(self):
        assert should_skip_url("https://youtube.com/watch?v=123")

    def test_skip_twitter(self):
        assert should_skip_url("https://twitter.com/user/status/123")

    def test_skip_login(self):
        assert should_skip_url("https://example.com/login")

    def test_allow_docs(self):
        assert not should_skip_url("https://docs.python.org/3/library/asyncio.html")

    def test_allow_github(self):
        assert not should_skip_url("https://github.com/python/cpython")


class TestIsAuthorityDomain:
    def test_python_docs(self):
        assert is_authority_domain("https://docs.python.org/3/library/asyncio.html")

    def test_github(self):
        assert is_authority_domain("https://github.com/user/repo")

    def test_random_blog(self):
        assert not is_authority_domain("https://random-blog.com/post")


class TestDeduplicateUrls:
    def test_remove_duplicates(self):
        urls = ["https://a.com/", "https://a.com", "https://b.com/"]
        result = deduplicate_urls(urls)
        assert len(result) == 2

    def test_preserve_order(self):
        urls = ["https://c.com", "https://a.com", "https://b.com", "https://a.com/"]
        result = deduplicate_urls(urls)
        assert result == ["https://c.com", "https://a.com", "https://b.com"]


class TestResolveRedirect:
    def test_google_redirect(self):
        url = "/url?q=https://example.com"
        assert resolve_redirect(url, "https://google.com") == "https://example.com"

    def test_relative_url(self):
        url = "/path/to/page"
        assert resolve_redirect(url, "https://example.com") == "https://example.com/path/to/page"

    def test_absolute_url(self):
        url = "https://example.com"
        assert resolve_redirect(url, "https://base.com") == "https://example.com"


class TestGetDomain:
    def test_extract_domain(self):
        assert get_domain("https://docs.python.org/3/library/asyncio.html") == "docs.python.org"
