"""Tests for the read-only stdlib Chroma reader used by the records_v1 migration."""
from __future__ import annotations

import hashlib
import shutil
import sqlite3
from pathlib import Path

import pytest

from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.domain.memory import MemoryEdge
from tests.chroma_store import ChromaStore
from ai_mem.infrastructure.chroma_sqlite_reader import ChromaSchemaError, read_chroma_store


def _tree_digest(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


@pytest.fixture
def chroma_store(tmp_path):
    db_path = tmp_path / "db"
    repo = ChromaStore(db_path)
    add = AddMemoryUseCase(repo)
    add.execute("repo.alpha", ["Decision: keep X"], ["domain_x"],
                metadatas=[{"type": "domain", "area": "arch", "cue": "before X"}])
    add.execute("repo.alpha", ["Fokus"], ["current_focus"], metadatas=[{"type": "project"}])
    add.execute("global", ["Rule: never Y"], ["pattern_y"],
                metadatas=[{"type": "pattern", "boost_count": 3, "confidence": 0.75, "keep_in_ai_mem": True}])
    repo.add_edge("repo.alpha", "domain_x", MemoryEdge(target_id="pattern_y", edge_type="related"))
    repo.upsert("repo.alpha", [*repo.get_by_ids("repo.alpha", ["domain_x"])])  # an update after the insert
    repo._client.get_or_create_collection("empty")
    return db_path, repo


def test_reads_what_chromadb_returns(chroma_store):
    db_path, repo = chroma_store

    snapshot = read_chroma_store(db_path)

    assert [c.name for c in snapshot.list_collections()] == [c.name for c in repo.list_collections()]
    for info in repo.list_collections():
        expected = [(e.id, e.text, e.metadata) for e in repo.get_all(info.name)]
        assert [(e.id, e.text, e.metadata) for e in snapshot.get_all(info.name)] == expected
    [pattern] = snapshot.get_all("global")
    assert pattern.metadata["keep_in_ai_mem"] is True and pattern.metadata["boost_count"] == 3


def test_reading_never_changes_the_store(chroma_store):
    db_path, _ = chroma_store
    before = _tree_digest(db_path)

    read_chroma_store(db_path)

    assert _tree_digest(db_path) == before


def test_missing_store_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_chroma_store(tmp_path)


def _copy(chroma_store, tmp_path) -> Path:
    db_path, _ = chroma_store
    copy = tmp_path / "copy"
    copy.mkdir()
    shutil.copy2(db_path / "chroma.sqlite3", copy / "chroma.sqlite3")
    return copy


def _edit(db_path: Path, sql: str) -> None:
    conn = sqlite3.connect(db_path / "chroma.sqlite3")
    conn.executescript(sql)
    conn.close()


@pytest.mark.parametrize("sql", [
    "DROP TABLE embedding_metadata;",
    "ALTER TABLE embeddings RENAME COLUMN embedding_id TO eid;",
    "DROP TABLE max_seq_id;",
    "INSERT INTO embedding_metadata_array (id, key, string_value) SELECT MIN(id), 'tags', 'a' FROM embeddings;",
    "UPDATE max_seq_id SET seq_id = 0;",  # queued writes chromadb has not applied yet
    "UPDATE segments SET scope = 'VECTOR' WHERE scope = 'METADATA';",
    "INSERT INTO segments (id, type, scope, collection) "
    "SELECT 'extra', type, scope, collection FROM segments WHERE scope = 'METADATA' LIMIT 1;",
    "UPDATE collections SET database_id = 'elsewhere';",
])
def test_unknown_schema_fails_loudly(chroma_store, tmp_path, sql):
    copy = _copy(chroma_store, tmp_path)
    _edit(copy, sql)

    with pytest.raises(ChromaSchemaError):
        read_chroma_store(copy)


def test_not_a_chroma_database(tmp_path):
    _edit(tmp_path, "CREATE TABLE foo (x);")

    with pytest.raises(ChromaSchemaError):
        read_chroma_store(tmp_path)


def test_hostile_ids_and_names_are_returned_verbatim_not_interpreted(chroma_store, tmp_path):
    """The reader joins no paths; ids like ../x reach records_migration, which refuses them."""
    db_path, repo = chroma_store
    AddMemoryUseCase(repo).execute("repo.alpha", ["evil"], ["../../etc/x"], metadatas=[{"type": "domain"}])

    ids = [e.id for e in read_chroma_store(db_path).get_all("repo.alpha")]

    assert "../../etc/x" in ids
