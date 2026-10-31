"""MemoryRepository over the git-native record files -- no database.

- record types (domain/pattern/anti-pattern/learning/todo/user) -> docs/records/<area>/<kind>/<id>.md
- the `current_focus` entry, whatever its type -> docs/records/FOCUS.md
- `reference` entries -> docs/reference/<id>.md (plain text)
Any other type is rejected at write time: the type taxonomy is the quality gate
(pattern_taxonomy_as_quality_gate), and there is no file to hold an untyped entry.

Counters and access tracking (`boost_count`, `last_accessed_at`) and TTL deletion do not
exist here; those protocol methods are no-ops. `query` is lexical (term overlap), not
semantic: retrieval is INDEX.md, grep and the librarian agent's judgment.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from ai_mem.domain.memory import CollectionInfo, MemoryEdge, MemoryEntry, QueryResult, title_of
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import regenerate_index
from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    DEFAULT_AREA,
    FOCUS_ID,
    FOCUS_TYPE,
    REFERENCE_TYPE,
    find_adr_files,
    focus_path,
    is_safe_area,
    is_safe_entry_id,
    iter_record_files,
    plain_file_content,
    record_file_path,
    reference_dir,
    remove_files,
    write_atomic,
)
from ai_mem.infrastructure.areas import find_area

STORED_TYPES = ADR_TYPES | {REFERENCE_TYPE}
_TERM = re.compile(r"[\wäöüß-]{3,}", re.IGNORECASE)


def _terms(text: str) -> set[str]:
    return {term.casefold() for term in _TERM.findall(text)}


def _read_or_none(path: Path) -> str | None:
    try:
        return path.read_text()
    except (FileNotFoundError, IsADirectoryError):
        return None


class FileMemoryRepository:
    """`collection` is an area key (the area root as an absolute path string); `records_dir_for` maps it to a records directory."""

    def __init__(self, records_dir_for: Callable[[str], Path | None]) -> None:
        self._records_dir_for = records_dir_for

    def _records_dir(self, collection: str) -> Path | None:
        return self._records_dir_for(collection)

    def _require_records_dir(self, collection: str) -> Path:
        records_dir = self._records_dir(collection)
        if records_dir is None:
            raise ValueError(f"no records directory for area {collection!r}")
        return records_dir

    @staticmethod
    def _reference_file(records_dir: Path, entry_id: str) -> Path | None:
        return reference_dir(records_dir) / f"{entry_id}.md" if is_safe_entry_id(entry_id) else None

    @staticmethod
    def _record_entry(path: Path) -> MemoryEntry | None:
        try:
            parsed = adr_markdown.parse(path.read_text())
        except (OSError, ValueError):
            return None
        metadata: dict = {"type": parsed.type, "area": parsed.area}
        if parsed.created_at is not None:
            metadata["created_at"] = parsed.created_at
        if parsed.superseded_by:
            metadata["superseded_by"] = parsed.superseded_by
        if parsed.valid_until is not None:
            metadata["valid_until"] = parsed.valid_until
        if parsed.edges:
            metadata["edges"] = json.dumps(parsed.edges)
        if parsed.cue:
            metadata["cue"] = parsed.cue
        if parsed.perspective:
            metadata["perspective"] = parsed.perspective
        if parsed.extra:
            metadata[adr_markdown.EXTRA_FRONTMATTER] = dict(parsed.extra)
        return MemoryEntry(id=parsed.id, text=parsed.text, metadata=metadata)

    @staticmethod
    def _plain_entry(entry_id: str, path: Path, entry_type: str) -> MemoryEntry | None:
        text = _read_or_none(path)
        return MemoryEntry(id=entry_id, text=text.rstrip("\n"), metadata={"type": entry_type}) if text is not None else None

    def _get_one(self, records_dir: Path, entry_id: str) -> MemoryEntry | None:
        if entry_id == FOCUS_ID:
            return self._plain_entry(FOCUS_ID, focus_path(records_dir), FOCUS_TYPE)
        for path in find_adr_files(records_dir, entry_id):
            entry = self._record_entry(path)
            if entry is not None:
                return entry
        reference = self._reference_file(records_dir, entry_id)
        return self._plain_entry(entry_id, reference, REFERENCE_TYPE) if reference is not None else None

    def get_by_ids(self, collection: str, ids: list[str]) -> list[MemoryEntry]:
        records_dir = self._records_dir(collection)
        if records_dir is None:
            return []
        found = (self._get_one(records_dir, entry_id) for entry_id in dict.fromkeys(ids))
        return [entry for entry in found if entry is not None]

    @staticmethod
    def _reference_files(records_dir: Path) -> list[Path]:
        directory = reference_dir(records_dir)
        return sorted(directory.glob("*.md")) if directory.is_dir() else []

    def get_all(self, collection: str) -> list[MemoryEntry]:
        records_dir = self._records_dir(collection)
        if records_dir is None:
            return []
        entries = [self._record_entry(path) for path in iter_record_files(records_dir)]
        entries.append(self._plain_entry(FOCUS_ID, focus_path(records_dir), FOCUS_TYPE))
        entries += [self._plain_entry(path.stem, path, REFERENCE_TYPE) for path in self._reference_files(records_dir)]
        return [entry for entry in entries if entry is not None]

    def _collection_names(self) -> set[str]:
        area = find_area(Path.cwd())
        return {str(area.root)} if area is not None else set()

    def list_collections(self) -> list[CollectionInfo]:
        """The area of the cwd, named by its root."""
        names = self._collection_names()
        infos = []
        for name in sorted(names):
            records_dir = self._records_dir(name)
            if records_dir is None:
                continue
            # Counted from the file listing, not by parsing every file: callers only need names and sizes.
            count = (len(iter_record_files(records_dir)) + focus_path(records_dir).is_file()
                     + len(self._reference_files(records_dir)))
            if count:
                infos.append(CollectionInfo(name=name, count=count))
        return infos

    def query(
        self,
        collection: str,
        text: str,
        n_results: int,
        max_age_days: float | None,
        type_filter: str | None = None,
    ) -> list[QueryResult]:
        """Lexical relevance: the share of the query's terms found in the entry (title counts double)."""
        wanted = _terms(text)
        if not wanted:
            return []
        cutoff = None
        if max_age_days is not None:
            cutoff = datetime.now(tz=timezone.utc).timestamp() - max_age_days * 86400
        scored = []
        for entry in self.get_all(collection):
            if type_filter and entry.metadata.get("type") != type_filter:
                continue
            created = entry.metadata.get("created_at")
            if cutoff is not None and created is not None and float(created) < cutoff:
                continue
            body, title = _terms(entry.text), _terms(f"{entry.id.replace('_', ' ')} {title_of(entry.text)}")
            score = (len(wanted & body) + len(wanted & title)) / (2 * len(wanted))
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda item: (-item[0], item[1].id))
        return [
            QueryResult(rank=rank, id=entry.id, score=round(score, 4), text=entry.text, metadata=entry.metadata)
            for rank, (score, entry) in enumerate(scored[:n_results], start=1)
        ]

    def get_edges(self, collection: str, entry_id: str) -> list[MemoryEdge]:
        entries = self.get_by_ids(collection, [entry_id])
        if not entries:
            return []
        raw = json.loads(entries[0].metadata.get("edges") or "[]")
        return [MemoryEdge(target_id=edge["target_id"], edge_type=edge["edge_type"]) for edge in raw]

    def upsert(self, collection: str, entries: list[MemoryEntry]) -> None:
        # Validate everything before writing anything, so a rejected batch leaves no partial state.
        for entry in entries:
            if entry.id == FOCUS_ID:
                continue
            entry_type = entry.metadata.get("type")
            if entry_type not in STORED_TYPES:
                raise ValueError(
                    f"type {entry_type!r} of {entry.id!r} is not stored; use one of "
                    f"{', '.join(sorted(STORED_TYPES))} (or the id 'current_focus')"
                )
            if not is_safe_entry_id(entry.id):
                raise ValueError(f"id {entry.id!r} cannot be used as a filename")
            if entry_type == REFERENCE_TYPE:
                continue
            area = entry.metadata.get("area") or DEFAULT_AREA
            if not is_safe_area(area):
                raise ValueError(f"area {area!r} cannot be used as a folder name")
            perspective = entry.metadata.get("perspective")
            if perspective and not is_safe_area(perspective):
                raise ValueError(f"perspective {perspective!r} must match the topic pattern ^[a-z0-9][a-z0-9_-]*$")
            if adr_markdown.EXTRA_FRONTMATTER in entry.metadata:
                adr_markdown.check_extra_frontmatter(entry.metadata[adr_markdown.EXTRA_FRONTMATTER])
        records_dir = self._require_records_dir(collection)

        index_stale = False
        for entry in entries:
            if entry.id == FOCUS_ID:
                self._write_if_changed(focus_path(records_dir), plain_file_content(entry.text))
            elif entry.metadata["type"] == REFERENCE_TYPE:
                index_stale |= self._remove_records(records_dir, entry.id)
                self._write_if_changed(self._reference_file(records_dir, entry.id), plain_file_content(entry.text))
            else:
                index_stale |= self._write_record(records_dir, entry)
        if index_stale:
            regenerate_index(records_dir)

    @staticmethod
    def _write_if_changed(path: Path, content: str) -> bool:
        if _read_or_none(path) == content:
            return False
        write_atomic(path, content)
        return True

    @staticmethod
    def _remove_records(records_dir: Path, entry_id: str) -> bool:
        stale = find_adr_files(records_dir, entry_id)
        remove_files(records_dir, stale)
        return bool(stale)

    def _drop_reference(self, records_dir: Path, entry_id: str) -> bool:
        reference = self._reference_file(records_dir, entry_id)
        if reference is None:
            return False
        try:
            reference.unlink()
        except FileNotFoundError:
            return False
        return True

    def _write_record(self, records_dir: Path, entry: MemoryEntry) -> bool:
        """Write the record and drop any other file for its id (retype, re-area, reference).
        Returns whether INDEX.md needs a refresh -- any content change can change its row."""
        entry_type = entry.metadata["type"]
        area = entry.metadata.get("area") or DEFAULT_AREA
        target = record_file_path(records_dir, entry.id, entry_type, area)
        content = adr_markdown.serialize(entry.id, entry_type, entry.text, {**entry.metadata, "area": area})
        changed = self._write_if_changed(target, content)
        others = [path for path in find_adr_files(records_dir, entry.id) if path != target]
        remove_files(records_dir, others)
        self._drop_reference(records_dir, entry.id)
        return changed or bool(others)

    def add_edge(self, collection: str, source_id: str, edge: MemoryEdge) -> None:
        entries = self.get_by_ids(collection, [source_id])
        if not entries or entries[0].metadata.get("type") not in ADR_TYPES:
            return
        source = entries[0]
        edges = json.loads(source.metadata.get("edges") or "[]")
        if any(e["target_id"] == edge.target_id and e["edge_type"] == edge.edge_type for e in edges):
            return
        edges.append({"target_id": edge.target_id, "edge_type": edge.edge_type})
        source.metadata["edges"] = json.dumps(edges)
        self.upsert(collection, [source])

    def delete(self, collection: str, ids: list[str] | None) -> int:
        if ids is None:
            raise ValueError("deleting a whole collection is not supported for record files; pass ids")
        records_dir = self._records_dir(collection)
        if records_dir is None:
            return 0
        deleted, index_stale = 0, False
        for entry_id in dict.fromkeys(ids):
            if entry_id == FOCUS_ID:
                try:
                    focus_path(records_dir).unlink()
                    deleted += 1
                except FileNotFoundError:
                    pass
                continue
            removed_record = self._remove_records(records_dir, entry_id)
            removed_reference = self._drop_reference(records_dir, entry_id)
            index_stale |= removed_record
            deleted += int(removed_record or removed_reference)
        if index_stale:
            regenerate_index(records_dir)
        return deleted

    # Database-only concepts: no-ops for record files.

    def delete_expired(self, collection: str) -> int:
        return 0

    def delete_stale(self, collection: str, stale_after_days: float) -> int:
        return 0

    def record_access(self, collection: str, ids: list[str]) -> None:
        return None
