"""Search engine registry — factory and discovery for multi-engine support."""

from __future__ import annotations

import logging
from typing import Type

from .base import SearchEngine

logger = logging.getLogger(__name__)


class SearchEngineRegistry:
    """Registry for search engine implementations."""

    _engines: dict[str, Type[SearchEngine]] = {}
    _instances: dict[str, SearchEngine] = {}

    @classmethod
    def register(cls, name: str, engine_class: Type[SearchEngine]) -> None:
        """Register a search engine class."""
        cls._engines[name] = engine_class
        logger.debug("Registered search engine: %s", name)

    @classmethod
    def get(cls, name: str) -> Type[SearchEngine]:
        """Get engine class by name."""
        if name not in cls._engines:
            available = ", ".join(cls._engines.keys())
            raise ValueError(
                f"Unknown engine '{name}'. Available: {available}"
            )
        return cls._engines[name]

    @classmethod
    def create(cls, name: str, **kwargs) -> SearchEngine:
        """Create or retrieve a cached engine instance by name.

        Instances are cached to reuse expensive resources (e.g. browser sessions).
        """
        if name not in cls._instances:
            engine_class = cls.get(name)
            cls._instances[name] = engine_class(**kwargs)
        return cls._instances[name]

    @classmethod
    def list_engines(cls) -> list[str]:
        """List all registered engine names."""
        return list(cls._engines.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if an engine is registered."""
        return name in cls._engines

    @classmethod
    def recommend_engines(cls, query: str = "", count: int = 3) -> list[str]:
        """Recommend optimal engine combination based on metadata.

        TIER 1 engines are always preferred. TIER 3 (e.g. Google) is only
        included if we need more engines and TIER 1/2 are exhausted.

        Args:
            query: Optional query hint (for future locale-aware selection).
            count: Number of engines to recommend (default: 3).

        Returns:
            List of engine names sorted by quality tier and reliability.
        """
        engines = cls.list_engines()
        scored: list[tuple[str, int, float]] = []

        for name in engines:
            try:
                engine = cls.create(name)
                scored.append((name, engine.quality_tier, engine.reliability_score))
            except Exception:
                continue

        # Sort by tier ascending (1 is best), then reliability descending
        scored.sort(key=lambda x: (x[1], -x[2]))
        return [name for name, _, _ in scored[:count]]


# Auto-register built-in engines
def _register_builtins() -> None:
    try:
        from .duckduckgo import DuckDuckGoEngine
        SearchEngineRegistry.register("duckduckgo", DuckDuckGoEngine)
        SearchEngineRegistry.register("duckduckgo_lite", DuckDuckGoEngine)
    except ImportError as exc:
        logger.warning("Could not register DuckDuckGo engine: %s", exc)

    try:
        from .searxng import SearXNGEngine
        SearchEngineRegistry.register("searxng", SearXNGEngine)
    except ImportError as exc:
        logger.warning("Could not register SearXNG engine: %s", exc)

    try:
        from .bing import BingEngine
        SearchEngineRegistry.register("bing", BingEngine)
    except ImportError as exc:
        logger.warning("Could not register Bing engine: %s", exc)

    try:
        from .naver import NaverEngine
        SearchEngineRegistry.register("naver", NaverEngine)
    except ImportError as exc:
        logger.warning("Could not register Naver engine: %s", exc)

    try:
        from .qwant import QwantEngine
        SearchEngineRegistry.register("qwant", QwantEngine)
    except ImportError as exc:
        logger.warning("Could not register Qwant engine: %s", exc)

    try:
        from .google import GoogleEngine
        SearchEngineRegistry.register("google", GoogleEngine)
    except ImportError as exc:
        logger.warning("Could not register Google engine: %s", exc)

    try:
        from .startpage import StartpageEngine
        SearchEngineRegistry.register("startpage", StartpageEngine)
    except ImportError as exc:
        logger.warning("Could not register Startpage engine: %s", exc)

    try:
        from .academic import AcademicEngine
        SearchEngineRegistry.register("academic", AcademicEngine)
    except ImportError as exc:
        logger.warning("Could not register Academic engine: %s", exc)

    try:
        from .brave import BraveEngine
        SearchEngineRegistry.register("brave", BraveEngine)
    except ImportError as exc:
        logger.warning("Could not register Brave engine: %s", exc)


_register_builtins()
