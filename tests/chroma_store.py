"""A tiny writer for real ChromaDB stores, used only as a fixture for the records_v1 migration tests.

ai-mem itself no longer writes Chroma (the backend was removed; see tag v0-last-mcp). The migration
and its stdlib reader still have to read what chromadb really wrote, so these tests build real stores
with chromadb when it is installed (the `dev` extra) and skip when it is not.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_mem.domain.memory import CollectionInfo, MemoryEdge, MemoryEntry


class ChromaStore:
    def __init__(self, db_path: Path) -> None:
        chromadb = pytest.importorskip("chromadb")
        db_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(db_path))

    def _col(self, name: str):
        return self._client.get_or_create_collection(name)

    def _existing(self, name: str):
        try:
            return self._client.get_collection(name)
        except Exception:
            return None

    def upsert(self, collection: str, entries: list[MemoryEntry]) -> None:
        self._col(collection).upsert(
            documents=[e.text for e in entries], ids=[e.id for e in entries], metadatas=[e.metadata for e in entries]
        )

    def get_by_ids(self, collection: str, ids: list[str]) -> list[MemoryEntry]:
        col = self._existing(collection)
        if col is None:
            return []
        result = col.get(ids=ids)
        return [MemoryEntry(id=i, text=d, metadata=m or {})
                for i, d, m in zip(result["ids"], result["documents"], result["metadatas"])]

    def get_all(self, collection: str) -> list[MemoryEntry]:
        col = self._existing(collection)
        if col is None:
            return []
        result = col.get()
        return [MemoryEntry(id=i, text=d, metadata=m or {})
                for i, d, m in zip(result["ids"], result["documents"], result["metadatas"])]

    def list_collections(self) -> list[CollectionInfo]:
        return [CollectionInfo(name=c.name, count=c.count()) for c in self._client.list_collections()]

    def delete(self, collection: str, ids: list[str]) -> None:
        self._col(collection).delete(ids=ids)

    def add_edge(self, collection: str, source_id: str, edge: MemoryEdge) -> None:
        col = self._existing(collection)
        meta = dict(col.get(ids=[source_id])["metadatas"][0])
        edges = json.loads(meta.get("edges", "[]"))
        edges.append({"target_id": edge.target_id, "edge_type": edge.edge_type})
        meta["edges"] = json.dumps(edges)
        col.update(ids=[source_id], metadatas=[meta])
