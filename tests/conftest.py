"""Shared pytest fixtures for ai-mem tests."""
from __future__ import annotations

import atexit
import json
import os
import shutil
import tempfile

import pytest

# A throwaway AI_MEM_PATH before any test module imports ai_mem, so a test that forgets to point at a
# temp dir cannot write into the real ~/.local/share/ai-mem.
_TEST_DB_PATH = tempfile.mkdtemp(prefix="ai-mem-test-")
atexit.register(shutil.rmtree, _TEST_DB_PATH, ignore_errors=True)
os.environ["AI_MEM_PATH"] = _TEST_DB_PATH
# Never search the real workspace from a test run.
os.environ.pop("AI_MEM_WORKSPACE_ROOT", None)

from ai_mem.domain.memory import CollectionInfo, MemoryEdge, MemoryEntry


class InMemoryRepository:
    """A MemoryRepository held in a dict, for use-case tests that do not care about files.

    Only what the use cases call is implemented; edges live in the `edges` metadata JSON, as in
    FileMemoryRepository.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, MemoryEntry]] = {}

    def upsert(self, collection: str, entries: list[MemoryEntry]) -> None:
        col = self._store.setdefault(collection, {})
        for entry in entries:
            col[entry.id] = MemoryEntry(id=entry.id, text=entry.text, metadata=dict(entry.metadata))

    def get_by_ids(self, collection: str, ids: list[str]) -> list[MemoryEntry]:
        col = self._store.get(collection, {})
        return [MemoryEntry(id=i, text=col[i].text, metadata=dict(col[i].metadata)) for i in ids if i in col]

    def get_all(self, collection: str) -> list[MemoryEntry]:
        return self.get_by_ids(collection, list(self._store.get(collection, {})))

    def list_collections(self) -> list[CollectionInfo]:
        return [CollectionInfo(name=name, count=len(col)) for name, col in self._store.items()]

    def delete(self, collection: str, ids: list[str] | None) -> int:
        col = self._store.get(collection, {})
        targets = list(col) if ids is None else [i for i in ids if i in col]
        for i in targets:
            del col[i]
        return len(targets)

    def add_edge(self, collection: str, source_id: str, edge: MemoryEdge) -> None:
        source = self._store[collection][source_id]
        edges = json.loads(source.metadata.get("edges") or "[]")
        pair = {"target_id": edge.target_id, "edge_type": edge.edge_type}
        if pair not in edges:
            edges.append(pair)
        source.metadata["edges"] = json.dumps(edges)

    def get_edges(self, collection: str, entry_id: str) -> list[MemoryEdge]:
        entry = self._store.get(collection, {}).get(entry_id)
        raw = json.loads(entry.metadata.get("edges") or "[]") if entry else []
        return [MemoryEdge(target_id=e["target_id"], edge_type=e["edge_type"]) for e in raw]


@pytest.fixture
def tmp_repo() -> InMemoryRepository:
    return InMemoryRepository()
