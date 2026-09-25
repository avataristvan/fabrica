"""Decorator that projects domain/pattern/anti-pattern entries onto ADR Markdown files.

Sits between `ChromaMemoryRepository` and the optional BM25 wrapper (server.py's
wiring, a later chunk) so its `upsert()`/`delete()`/`add_edge()` see the actual
write operations before BM25 reformats them for read-only ranking. Same thin-
decorator style as `bm25_repository.py`: only the three methods below get real
logic, every other Protocol method is a one-line passthrough with no file I/O.
"""
from __future__ import annotations

from pathlib import Path

from ai_mem.domain.memory import CollectionInfo, MemoryEdge, MemoryEntry, MemoryRepository, QueryResult
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_paths import ADR_TYPES, adr_file_path


class MarkdownAdrRepository:
    def __init__(self, inner: MemoryRepository, db_path: Path) -> None:
        self._inner = inner
        self._db_path = db_path

    def _sync_file(self, collection: str, entry: MemoryEntry) -> None:
        file_path = adr_file_path(self._db_path, collection, entry.id)
        if file_path is None:
            return

        new_content = adr_markdown.serialize(entry.id, entry.metadata.get("type"), entry.text, entry.metadata)

        # Confidence-lifecycle boundary: a mem_boost-only upsert (confidence/access_count
        # changed, structural fields unchanged) must not touch the file, or every boost
        # would generate a spurious git diff. serialize()'s fixed field order (Chunk 1)
        # is what makes this a reliable content comparison rather than key-order churn.
        if file_path.exists() and file_path.read_text() == new_content:
            return

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(new_content)

    def upsert(self, collection: str, entries: list[MemoryEntry]) -> None:
        self._inner.upsert(collection, entries)
        for entry in entries:
            if entry.metadata.get("type") in ADR_TYPES:
                self._sync_file(collection, entry)

    def query(
        self,
        collection: str,
        text: str,
        n_results: int,
        max_age_days: float | None,
        type_filter: str | None = None,
    ) -> list[QueryResult]:
        return self._inner.query(collection, text, n_results, max_age_days, type_filter)

    def get_by_ids(self, collection: str, ids: list[str]) -> list[MemoryEntry]:
        return self._inner.get_by_ids(collection, ids)

    def list_collections(self) -> list[CollectionInfo]:
        return self._inner.list_collections()

    def delete(self, collection: str, ids: list[str] | None) -> int:
        if ids is None:
            # Deliberate safety decision: a whole-collection delete never touches files.
            return self._inner.delete(collection, None)

        adr_entries = [entry for entry in self._inner.get_by_ids(collection, ids) if entry.metadata.get("type") in ADR_TYPES]
        affected = self._inner.delete(collection, ids)
        for entry in adr_entries:
            file_path = adr_file_path(self._db_path, collection, entry.id)
            if file_path is not None:
                file_path.unlink(missing_ok=True)
        return affected

    def delete_expired(self, collection: str) -> int:
        return self._inner.delete_expired(collection)

    def record_access(self, collection: str, ids: list[str]) -> None:
        self._inner.record_access(collection, ids)

    def delete_stale(self, collection: str, stale_after_days: float) -> int:
        return self._inner.delete_stale(collection, stale_after_days)

    def get_all(self, collection: str) -> list[MemoryEntry]:
        return self._inner.get_all(collection)

    def add_edge(self, collection: str, source_id: str, edge: MemoryEdge) -> None:
        self._inner.add_edge(collection, source_id, edge)
        entries = self._inner.get_by_ids(collection, [source_id])
        if entries and entries[0].metadata.get("type") in ADR_TYPES:
            self._sync_file(collection, entries[0])

    def get_edges(self, collection: str, entry_id: str) -> list[MemoryEdge]:
        return self._inner.get_edges(collection, entry_id)
