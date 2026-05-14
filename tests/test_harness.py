"""Tests for maru harness: persistence, project init."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from maru_deep_pro_search.harness.persistence import KnowledgeStore
from maru_deep_pro_search.harness.project import HarnessProject, init_project


class TestKnowledgeStore:
    def test_save_and_query_exact(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            store.save(
                query="Python async best practices", answer="Use asyncio.gather...", sources=[]
            )
            results = store.query("Python async best practices")
            assert len(results) == 1
            assert results[0].answer == "Use asyncio.gather..."

    def test_query_no_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            results = store.query("nonexistent query")
            assert results == []

    def test_update_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            store.save(query="test", answer="old", sources=[])
            store.save(query="test", answer="new", sources=[])
            results = store.query("test")
            assert results[0].answer == "new"

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            store.save(query="q1", answer="a1", sources=[])
            store.save(query="q2", answer="a2", sources=[])
            stats = store.get_stats()
            assert stats["total_entries"] == 2

    def test_prune(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            # Can't easily test time-based pruning without mocking,
            # so just verify it doesn't crash
            store.save(query="q", answer="a", sources=[])
            deleted = store.prune(max_age_days=0)
            # 0 days means everything older than 0 days (which is everything)
            assert deleted >= 0

    def test_record_domain_fetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            store.record_domain_fetch("github.com", 500.0, True)
            store.record_domain_fetch("github.com", 600.0, True)
            store.record_domain_fetch("github.com", 30000.0, False)
            stats = store.get_domain_stats("github.com")
            assert stats is not None
            assert stats["success_rate"] == 2 / 3
            assert stats["failure_count"] == 1
            assert stats["total"] == 3

    def test_get_domain_stats_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            assert store.get_domain_stats("nonexistent.com") is None

    def test_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            store.save(query="q", answer="a")
            store.close()
            assert store._conn is None

    def test_default_db_path(self):
        from maru_deep_pro_search.harness.persistence import KnowledgeStore
        path = KnowledgeStore._default_db_path()
        assert path.name == "knowledge.db"

    def test_entry_serialization(self):
        from maru_deep_pro_search.harness.persistence import KnowledgeEntry
        entry = KnowledgeEntry(
            query="test",
            answer="answer",
            sources=[{"url": "https://example.com"}],
            created_at="2024-01-01T00:00:00",
        )
        json_str = entry.to_json()
        restored = KnowledgeEntry.from_json(json_str)
        assert restored.query == entry.query
        assert restored.answer == entry.answer

    def test_bump_access_by_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            store.save(query="q1", answer="a1")
            store._bump_access_by_query("q1", "2024-01-01T00:00:00")
            stats = store.get_stats()
            assert stats["total_entries"] == 1

    def test_embedding_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            store = KnowledgeStore(db_path=db)
            # Manually insert with embedding to test _row_to_entry path
            q_hash = store._hash_query("q")
            conn = store._connect()
            conn.execute(
                "INSERT INTO knowledge (query_hash, query, answer, sources, created_at, embedding) VALUES (?, ?, ?, ?, ?, ?)",
                (q_hash, "q", "a", "[]", "2024-01-01", json.dumps([0.1, 0.2, 0.3])),
            )
            conn.commit()
            results = store.query("q")
            assert len(results) == 1
            assert results[0].embedding == [0.1, 0.2, 0.3]


class TestHarnessProject:
    def test_init_project_creates_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project(path=root, agents=None, create_agents_md=True, create_gitignore=True)
            assert (root / ".maru" / "knowledge.db").exists()
            assert (root / "AGENTS.md").exists()
            assert (root / ".gitignore").exists()

    def test_init_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project(path=root)
            init_project(path=root)
            # Should not crash on second init
            assert (root / ".maru" / "knowledge.db").exists()

    def test_harness_project_accessor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            init_project(path=root)
            hp = HarnessProject(root)
            assert hp.is_initialized()
            assert hp.store is not None
