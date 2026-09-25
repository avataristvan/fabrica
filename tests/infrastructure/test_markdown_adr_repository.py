"""Tests for MarkdownAdrRepository: the Chroma-decorator that projects domain/pattern/
anti-pattern entries onto ADR Markdown files under docs/decisions/.

Uses a minimal in-memory fake for the inner MemoryRepository (not ChromaMemoryRepository)
so these tests exercise the decorator's own logic -- the diff-before-write confidence-
lifecycle boundary, the file-lifecycle on delete, and the add_edge resync -- in isolation.
"""
from __future__ import annotations

import json

import pytest

from ai_mem.domain.memory import MemoryEdge, MemoryEntry
from ai_mem.infrastructure import adr_paths
from ai_mem.infrastructure.markdown_adr_repository import MarkdownAdrRepository

COLLECTION = "repo.testproj"


class FakeMemoryRepository:
    """In-memory MemoryRepository fake. Only the methods MarkdownAdrRepository actually
    calls (upsert, get_by_ids, delete, add_edge) have real behavior; the rest raise so an
    accidental new call path is caught rather than silently returning nonsense."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, MemoryEntry]] = {}

    def upsert(self, collection: str, entries: list[MemoryEntry]) -> None:
        col = self._store.setdefault(collection, {})
        for entry in entries:
            col[entry.id] = MemoryEntry(id=entry.id, text=entry.text, metadata=dict(entry.metadata))

    def get_by_ids(self, collection: str, ids: list[str]) -> list[MemoryEntry]:
        col = self._store.get(collection, {})
        return [col[id_] for id_ in ids if id_ in col]

    def delete(self, collection: str, ids: list[str] | None) -> int:
        col = self._store.setdefault(collection, {})
        if ids is None:
            col.clear()
            return -1
        removed = 0
        for id_ in ids:
            if col.pop(id_, None) is not None:
                removed += 1
        return removed

    def add_edge(self, collection: str, source_id: str, edge: MemoryEdge) -> None:
        col = self._store.setdefault(collection, {})
        entry = col.get(source_id)
        if entry is None:
            return
        raw_edges = entry.metadata.get("edges")
        edges = json.loads(raw_edges) if raw_edges else []
        if any(e["target_id"] == edge.target_id and e["edge_type"] == edge.edge_type for e in edges):
            return
        edges.append({"target_id": edge.target_id, "edge_type": edge.edge_type})
        entry.metadata["edges"] = json.dumps(edges)

    def query(self, *args, **kwargs):
        raise NotImplementedError

    def list_collections(self):
        raise NotImplementedError

    def delete_expired(self, collection):
        raise NotImplementedError

    def record_access(self, collection, ids):
        raise NotImplementedError

    def delete_stale(self, collection, stale_after_days):
        raise NotImplementedError

    def get_all(self, collection):
        raise NotImplementedError

    def get_edges(self, collection, entry_id):
        raise NotImplementedError


@pytest.fixture
def repo_root(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    return root


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "db"


@pytest.fixture
def adr_repo(db_path, repo_root):
    adr_paths.record_collection_root(db_path, COLLECTION, repo_root)
    return MarkdownAdrRepository(FakeMemoryRepository(), db_path)


def _adr_file(repo_root, entry_id: str):
    return repo_root / "docs" / "decisions" / f"{entry_id}.md"


def test_upsert_domain_type_writes_file(adr_repo, repo_root):
    entry = MemoryEntry(
        id="domain_x",
        text="Decision: keep it simple\n\nWhy: ...\n\nScope: ...",
        metadata={"type": "domain", "created_at": 123.0, "confidence": 0.7, "access_count": 0},
    )

    adr_repo.upsert(COLLECTION, [entry])

    content = _adr_file(repo_root, "domain_x").read_text()
    assert "id: domain_x" in content
    assert "type: domain" in content
    assert "created: 123.0" in content
    assert "Decision: keep it simple" in content
    assert "confidence" not in content
    assert "access_count" not in content


def test_upsert_non_adr_type_writes_no_file(adr_repo, repo_root):
    entry = MemoryEntry(id="feedback_x", text="Rule: ...\nWhen: ...\nWhy: ...", metadata={"type": "feedback"})

    adr_repo.upsert(COLLECTION, [entry])

    assert not _adr_file(repo_root, "feedback_x").exists()


def test_confidence_only_change_does_not_rewrite_file(adr_repo, repo_root):
    original = MemoryEntry(
        id="domain_x",
        text="Decision: ...",
        metadata={"type": "domain", "created_at": 123.0, "confidence": 0.7, "access_count": 0},
    )
    adr_repo.upsert(COLLECTION, [original])

    file_path = _adr_file(repo_root, "domain_x")
    original_content = file_path.read_text()
    original_mtime_ns = file_path.stat().st_mtime_ns

    boosted = MemoryEntry(
        id="domain_x",
        text="Decision: ...",
        metadata={"type": "domain", "created_at": 123.0, "confidence": 0.95, "access_count": 3},
    )
    adr_repo.upsert(COLLECTION, [boosted])

    assert file_path.read_text() == original_content
    assert file_path.stat().st_mtime_ns == original_mtime_ns


def test_delete_with_ids_removes_file(adr_repo, repo_root):
    entry = MemoryEntry(id="domain_x", text="Decision: ...", metadata={"type": "domain"})
    adr_repo.upsert(COLLECTION, [entry])
    assert _adr_file(repo_root, "domain_x").exists()

    affected = adr_repo.delete(COLLECTION, ["domain_x"])

    assert affected == 1
    assert not _adr_file(repo_root, "domain_x").exists()


def test_delete_with_none_ids_leaves_files_untouched(adr_repo, repo_root):
    entry = MemoryEntry(id="domain_x", text="Decision: ...", metadata={"type": "domain"})
    adr_repo.upsert(COLLECTION, [entry])

    affected = adr_repo.delete(COLLECTION, None)

    assert affected == -1
    assert _adr_file(repo_root, "domain_x").exists()


def test_add_edge_supersedes_updates_source_file_and_target_upsert_follows(adr_repo, repo_root):
    source = MemoryEntry(id="domain_new", text="Decision: new", metadata={"type": "domain"})
    target = MemoryEntry(id="domain_old", text="Decision: old", metadata={"type": "domain"})
    adr_repo.upsert(COLLECTION, [source, target])

    adr_repo.add_edge(COLLECTION, "domain_new", MemoryEdge(target_id="domain_old", edge_type="supersedes"))

    source_content = _adr_file(repo_root, "domain_new").read_text()
    assert '"target_id": "domain_old"' in source_content
    assert '"edge_type": "supersedes"' in source_content

    # add_edge() only resyncs the source file -- AddEdgeUseCase separately upserts the
    # target with superseded_by set (ai_mem/application/add_edge.py:43-51); simulate that
    # follow-up upsert here since this test operates below the use-case layer.
    updated_target = MemoryEntry(id="domain_old", text="Decision: old", metadata={"type": "domain", "superseded_by": "domain_new"})
    adr_repo.upsert(COLLECTION, [updated_target])

    target_content = _adr_file(repo_root, "domain_old").read_text()
    assert "superseded_by: domain_new" in target_content


def test_upsert_no_resolvable_root_is_a_noop(tmp_path):
    # No record_collection_root() call, no detectable repo context: adr_file_path()
    # returns None, so _sync_file() must no-op rather than crash.
    repo = MarkdownAdrRepository(FakeMemoryRepository(), tmp_path / "db")
    entry = MemoryEntry(id="domain_x", text="Decision: ...", metadata={"type": "domain"})

    repo.upsert("workspace", [entry])  # "workspace" never resolves to a root

    assert repo.get_by_ids("workspace", ["domain_x"])[0].text == "Decision: ..."
