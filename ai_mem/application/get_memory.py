"""Fetch memory entries by id."""
from __future__ import annotations

from ai_mem.application.track_access import TrackAccessUseCase
from ai_mem.domain.memory import MemoryEntry, MemoryRepository


class GetMemoryUseCase:
    def __init__(self, repo: MemoryRepository, track_access: TrackAccessUseCase | None = None) -> None:
        self._repo = repo
        self._track_access = track_access

    def execute(self, collection: str, ids: list[str]) -> list[MemoryEntry]:
        entries = self._repo.get_by_ids(collection, ids)
        # Fetching by explicit id is a deliberate-use signal, recorded as last_accessed_at --
        # only found entries are tracked, missing ids leave no trace. track_access is optional:
        # callers that fetch entries as internal plumbing rather than an agent's deliberate choice
        # (e.g. hook.py's SessionStart current_focus lookup) omit it so that automatic reads
        # don't count as deliberate use.
        if self._track_access is not None and entries:
            self._track_access.execute(collection, [entry.id for entry in entries])
        return entries
