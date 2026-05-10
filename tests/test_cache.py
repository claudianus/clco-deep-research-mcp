"""Tests for in-memory TTL cache."""

import time

from maru_search.utils.cache import TTLCache, cache_key


class TestTTLCache:
    def test_basic_get_set(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60.0)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_missing_key_returns_none(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60.0)
        assert cache.get("missing") is None

    def test_ttl_expiration(self):
        cache = TTLCache(maxsize=10, ttl_seconds=0.1)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        time.sleep(0.15)
        assert cache.get("key1") is None

    def test_lru_eviction(self):
        cache = TTLCache(maxsize=3, ttl_seconds=60.0)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # Should evict 'a'
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_lru_access_moves_to_end(self):
        cache = TTLCache(maxsize=3, ttl_seconds=60.0)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.get("a")  # Access 'a', move to end
        cache.set("d", 4)  # Should evict 'b' (least recently used)
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3
        assert cache.get("d") == 4

    def test_stats(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60.0)
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key1")  # hit
        cache.get("missing")  # miss
        stats = cache.stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert abs(stats["hit_rate"] - 2 / 3) < 0.001
        assert stats["size"] == 1

    def test_clear(self):
        cache = TTLCache(maxsize=10, ttl_seconds=60.0)
        cache.set("key1", "value1")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.stats()["size"] == 0


class TestCacheKey:
    def test_cache_key_basic(self):
        assert cache_key("a", "b", "c") == "a|b|c"

    def test_cache_key_integers(self):
        assert cache_key("search", 10, "query") == "search|10|query"
