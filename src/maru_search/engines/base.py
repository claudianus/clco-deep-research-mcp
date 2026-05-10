"""Abstract base classes and data models for search engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ContentType(str, Enum):
    ARTICLE = "article"
    DOCUMENTATION = "docs"
    FORUM = "forum"
    CODE = "code"
    SPAM = "spam"
    UNKNOWN = "unknown"


class ExtractionQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EMPTY = "empty"
    BLOCKED = "blocked"


@dataclass
class SearchResult:
    """A single search result from any engine."""

    title: str
    url: str
    snippet: str = ""
    position: int = 0
    likely_content_type: ContentType = ContentType.UNKNOWN
    domain: str = ""
    url_suggests_docs: bool = False
    engine: str = ""
    # Citation support
    citation_id: int = 0
    # Cross-engine metadata
    engines_found: list[str] = field(default_factory=list)
    cross_engine_score: float = 0.0


@dataclass
class PageContent:
    """Extracted content from a fetched page."""

    url: str
    final_url: str = ""
    title: str = ""
    text: str = ""
    markdown: str = ""
    html: str = ""

    quality: ExtractionQuality = ExtractionQuality.EMPTY
    content_type: ContentType = ContentType.UNKNOWN
    content_length: int = 0
    heading_count: int = 0
    code_block_count: int = 0

    internal_links: list[dict] = field(default_factory=list)
    external_links: list[dict] = field(default_factory=list)
    needs_stealth: bool = False
    fetch_duration_ms: float = 0.0
    error_message: str = ""

    published_date: str = ""
    code_languages: list[str] = field(default_factory=list)
    api_signatures: list[dict] = field(default_factory=list)
    package_refs: list[dict] = field(default_factory=list)
    code_to_text_ratio: float = 0.0
    freshness_days: Optional[int] = None
    is_api_reference: bool = False
    is_tutorial: bool = False
    is_error_solution: bool = False

    # Citation support for answer synthesis
    citation_id: int = 0


class SearchEngine(ABC):
    """Abstract base for all search engines.

    Subclasses should set quality metadata to help the registry
    recommend optimal engine combinations.
    """

    name: str = ""
    supports_stealth: bool = False

    # Quality metadata (used by SearchEngineRegistry.recommend_engines)
    quality_tier: int = 2  # 1=best, 2=good, 3=fallback/last-resort
    typical_latency_ms: int = 1200
    reliability_score: float = 0.9  # 0.0-1.0, higher is more reliable

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Search and return results."""
        ...

    @abstractmethod
    async def fetch(self, url: str, stealth: bool = False) -> PageContent:
        """Fetch and extract content from a URL."""
        ...
