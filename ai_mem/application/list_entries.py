"""List all entries in a collection as id + title pairs."""
from __future__ import annotations

from ai_mem.domain.memory import MemoryRepository, title_of

__all__ = ["ListEntriesUseCase", "title_of"]  # title_of re-exported for the hooks


class ListEntriesUseCase:
    def __init__(self, repo: MemoryRepository) -> None:
        self._repo = repo

    def execute(self, collection: str) -> list[dict]:
        entries = self._repo.get_all(collection)
        return [{"id": entry.id, "title": title_of(entry.text)} for entry in entries]
