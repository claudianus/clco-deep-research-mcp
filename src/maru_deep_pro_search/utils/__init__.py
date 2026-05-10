"""Utility modules for maru-search."""

from .retry import with_retry
from .url import (
    normalize_url,
    should_skip_url,
    is_authority_domain,
    deduplicate_urls,
    resolve_redirect,
    get_domain,
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
