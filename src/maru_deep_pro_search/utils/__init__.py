"""Utility modules for maru-search."""

from .retry import with_retry
from .url import (
    deduplicate_urls,
    get_domain,
    is_authority_domain,
    normalize_url,
    resolve_redirect,
    should_skip_url,
)

__all__ = [
    "with_retry",
    "normalize_url",
    "should_skip_url",
    "is_authority_domain",
    "deduplicate_urls",
    "resolve_redirect",
    "get_domain",
]
