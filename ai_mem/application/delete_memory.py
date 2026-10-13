"""Delete entries from memory and name the edges the delete leaves dangling."""
from __future__ import annotations

from dataclasses import dataclass

from ai_mem.domain.memory import MemoryRepository, parse_edges


@dataclass(frozen=True)
class DanglingEdge:
    referrer: str
    edge_type: str
    target: str


class DeleteMemoryUseCase:
    def __init__(self, repo: MemoryRepository) -> None:
        self._repo = repo

    def execute(self, collection: str, ids: list[str]) -> list[DanglingEdge]:
        """Delete `ids` and return the bare edges of the remaining records in the collection that
        pointed at one of them; nothing else is changed. Edges from other areas (and qualified
        references back into this one) are not scanned: `mem doctor` finds those."""
        self._repo.delete(collection, ids)
        deleted = set(ids)
        dangling: list[DanglingEdge] = []
        for entry in self._repo.get_all(collection):
            try:
                edges = parse_edges(entry.metadata.get("edges"))
            except ValueError:
                continue  # malformed edges are `mem lint`'s finding, not the delete's
            dangling.extend(
                DanglingEdge(entry.id, edge["edge_type"], edge["target_id"])
                for edge in edges if edge["target_id"] in deleted
            )
        return dangling
