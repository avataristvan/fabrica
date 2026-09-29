"""Decorator that projects domain/pattern/anti-pattern/learning entries onto ADR Markdown files.

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
from ai_mem.infrastructure.adr_index import regenerate_index
from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    DEFAULT_AREA,
    adr_dir_for,
    adr_file_path,
    find_adr_files,
    is_safe_area,
    is_safe_entry_id,
)


class MarkdownAdrRepository:
    def __init__(self, inner: MemoryRepository, db_path: Path) -> None:
        self._inner = inner
        self._db_path = db_path

    def _adr_dir(self, collection: str) -> Path | None:
        return adr_dir_for(self._db_path, collection)

    @staticmethod
    def _area_of(entry: MemoryEntry) -> str:
        return entry.metadata.get("area") or DEFAULT_AREA

    def _remove_files(self, adr_dir: Path, files: list[Path]) -> None:
        for file_path in files:
            file_path.unlink(missing_ok=True)
            for parent in (file_path.parent, file_path.parent.parent):
                if parent != adr_dir and parent.is_dir() and not any(parent.iterdir()):
                    parent.rmdir()

    def _sync_file(self, collection: str, entry: MemoryEntry) -> bool:
        """Write the entry's ADR file if its content changed and remove every other file for this
        id (retype, re-area, legacy flat leftovers). Returns whether INDEX.md needs a refresh: the
        entry's `superseded_by`, type or area differs from what a previous file recorded (a
        mem_boost-only upsert changes none of these). Cleanup of a same-type/area duplicate alone
        does not count."""
        entry_type = entry.metadata.get("type")
        file_path = adr_file_path(self._db_path, collection, entry.id, entry_type, self._area_of(entry))
        if file_path is None:
            return False
        adr_dir = self._adr_dir(collection)

        others = [path for path in find_adr_files(adr_dir, entry.id) if path != file_path]
        previous = [file_path, *others] if file_path.exists() else others
        new_state = (entry_type, self._area_of(entry), entry.metadata.get("superseded_by") or None)
        index_stale = not previous and new_state[2] is not None
        for path in previous:
            try:
                old = adr_markdown.parse(path.read_text())
            except ValueError:
                index_stale = True  # malformed prior file: treat as a status change
                continue
            index_stale |= (old.type, old.area, old.superseded_by) != new_state

        new_content = adr_markdown.serialize(entry.id, entry_type, entry.text, entry.metadata)
        # Volatile-field boundary: a mem_boost-only upsert (boost_count/cue/last_accessed_at
        # changed, structural fields unchanged) must not touch the file, or every boost would
        # generate a spurious git diff. serialize()'s fixed field order is what makes this a
        # reliable content comparison rather than key-order churn.
        if not file_path.exists() or file_path.read_text() != new_content:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(new_content)
        self._remove_files(adr_dir, others)
        return index_stale

    def _reindex(self, collection: str) -> None:
        adr_dir = self._adr_dir(collection)
        if adr_dir is not None and adr_dir.is_dir():
            regenerate_index(adr_dir)

    def upsert(self, collection: str, entries: list[MemoryEntry]) -> None:
        # Validate before the inner write, so a rejected id/area never lands in Chroma without its file.
        for entry in entries:
            if entry.metadata.get("type") in ADR_TYPES:
                if not is_safe_entry_id(entry.id):
                    raise ValueError(f"id {entry.id!r} cannot be used as an ADR filename")
                if not is_safe_area(self._area_of(entry)):
                    raise ValueError(f"area {self._area_of(entry)!r} cannot be used as an ADR folder name")

        self._inner.upsert(collection, entries)
        status_changed = False
        for entry in entries:
            if entry.metadata.get("type") in ADR_TYPES:
                status_changed |= self._sync_file(collection, entry)
            else:
                status_changed |= self._remove_stale_files(collection, entry.id)
        # Deliberately narrow: INDEX.md regeneration stays off the per-mem_add write path
        # (Chunk 3b -- a read-modify-write race on one shared file) except for events that change
        # a row: a supersede status change (whichever caller produced it -- mem_link, or
        # mem_dream --auto_supersede via AddEdgeUseCase's target upsert), or a file moving/vanishing.
        if status_changed:
            self._reindex(collection)

    def _remove_stale_files(self, collection: str, entry_id: str) -> bool:
        # An entry re-typed away from an ADR type must not leave its old record behind in the repo.
        adr_dir = self._adr_dir(collection)
        if adr_dir is None:
            return False
        stale = find_adr_files(adr_dir, entry_id)
        self._remove_files(adr_dir, stale)
        return bool(stale)

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
        adr_dir = self._adr_dir(collection)
        if adr_dir is not None:
            for entry in adr_entries:
                # Metadata-derived path first, recursive search for anything stale (legacy/misplaced).
                target = adr_file_path(self._db_path, collection, entry.id, entry.metadata["type"], self._area_of(entry))
                self._remove_files(adr_dir, sorted({*find_adr_files(adr_dir, entry.id), *([target] if target else [])}))
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
