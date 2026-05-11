"""Project-level harness initialization."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .persistence import KnowledgeStore

logger = logging.getLogger("maru_deep_pro_search.harness.project")

DEFAULT_AGENTS_MD = """# Agent Instructions

> This project uses **maru-deep-pro-search** harness for research-first development.

## Rule Zero

**NEVER write code based solely on training data.**

Your training knowledge has a cutoff date. Libraries evolve. APIs change.
Always call `deep_research(query)` BEFORE making technical decisions.

## Tool Priority

1. `deep_research` — ALWAYS start here
2. `answer` — Quick factual checks
3. `parallel_search` — Multiple angles simultaneously
4. `fetch_page` / `fetch_bulk` — Read specific URLs
5. `stealthy_fetch` — Last resort for blocked sites

## Knowledge Cache

This project has a local knowledge store at `.maru/knowledge.db`.
Previous research results are cached and reused when relevant.

## Research Checklist

Before writing ANY code:
- [ ] Called `deep_research` on the topic
- [ ] Verified library versions are current
- [ ] Checked for known security issues
- [ ] Confirmed API signatures match latest docs
- [ ] Cited sources with [1], [2] in your answer
"""

DEFAULT_GITIGNORE = """# Maru Harness
.maru/knowledge.db
.maru/knowledge.db-journal
.maru/*.bak
"""


def init_project(
    path: Path | str = ".",
    agents: list[str] | None = None,
    create_agents_md: bool = True,
    create_gitignore: bool = True,
) -> dict[str, Any]:
    """Initialize a project with the maru harness.

    Creates:
        .maru/knowledge.db   — local knowledge cache
        AGENTS.md            — project-specific agent instructions (if requested)
        .gitignore additions — exclude harness artifacts

    Args:
        path: Project root directory.
        agents: List of agent names to configure (e.g. ["cursor", "claude"]).
                If None, auto-detect installed agents.
        create_agents_md: Whether to create AGENTS.md.
        create_gitignore: Whether to append harness entries to .gitignore.

    Returns:
        Summary dict with created paths and status.
    """
    root = Path(path).resolve()
    maru_dir = root / ".maru"
    maru_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    # 1. Knowledge store (lazy-created on first access, but we ensure dir)
    store = KnowledgeStore(db_path=maru_dir / "knowledge.db")
    store._connect()  # ensure schema exists
    created.append(str(maru_dir / "knowledge.db"))

    # 2. AGENTS.md
    if create_agents_md:
        agents_md = root / "AGENTS.md"
        if not agents_md.exists():
            agents_md.write_text(DEFAULT_AGENTS_MD, encoding="utf-8")
            created.append(str(agents_md))

    # 3. .gitignore
    if create_gitignore:
        gitignore = root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text(encoding="utf-8")
            if ".maru/knowledge.db" not in content:
                with gitignore.open("a", encoding="utf-8") as f:
                    f.write("\n" + DEFAULT_GITIGNORE + "\n")
                created.append(str(gitignore))
        else:
            gitignore.write_text(DEFAULT_GITIGNORE + "\n", encoding="utf-8")
            created.append(str(gitignore))

    # 4. Agent configs at project scope
    if agents:
        from ..cli.agents.base import AgentAdapter
        from ..cli.setup import ADAPTER_REGISTRY

        for name in agents:
            adapter_cls = ADAPTER_REGISTRY.get(name)
            if adapter_cls:
                adapter = adapter_cls()
                adapter.configure(scope="project")
                logger.info("Configured %s for project scope", name)

    logger.info("Harness initialized at %s", root)
    return {
        "root": str(root),
        "created": created,
        "agents_configured": agents or [],
    }


class HarnessProject:
    """Accessor for a harness-enabled project."""

    def __init__(self, root: Path | str = ".") -> None:
        self.root = Path(root).resolve()
        self.maru_dir = self.root / ".maru"
        self._store: KnowledgeStore | None = None

    @property
    def store(self) -> KnowledgeStore:
        if self._store is None:
            self._store = KnowledgeStore(db_path=self.maru_dir / "knowledge.db")
        return self._store

    def is_initialized(self) -> bool:
        return (self.maru_dir / "knowledge.db").exists()
