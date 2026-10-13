"""Remove a typed edge between two memory entries (the inverse of AddEdgeUseCase)."""
from __future__ import annotations

import json

from ai_mem.domain.memory import EdgeType, MemoryRepository, is_area_qualified, parse_edges


class RemoveEdgeUseCase:
    def __init__(self, repo: MemoryRepository) -> None:
        self._repo = repo

    def execute(
        self,
        collection: str,
        source_id: str,
        target_id: str,
        edge_type: EdgeType | None = None,
    ) -> list[str]:
        """Remove the edges source_id → target_id (only those of edge_type, if given) and return
        the removed edge types.

        The target is matched as stored (bare id or `<rel-area-path>:<id>`) and need not exist, so
        an edge to a deleted record can be removed. Removing a 'supersedes' edge also clears
        `superseded_by` and `valid_until` on a bare target the source flagged; a target in another
        area was never flagged (AddEdgeUseCase refuses 'supersedes' across areas).

        Raises ValueError when the source does not exist, its edges are malformed, or it has no
        matching edge.
        """
        entries = self._repo.get_by_ids(collection, [source_id])
        if not entries:
            raise ValueError(f"Entry ID(s) not found in '{collection}': {[source_id]}")
        source = entries[0]
        edges = parse_edges(source.metadata.get("edges"))
        removed = [
            edge["edge_type"] for edge in edges
            if edge["target_id"] == target_id and edge_type in (None, edge["edge_type"])
        ]
        if not removed:
            wanted = f" of type '{edge_type}'" if edge_type else ""
            raise ValueError(f"'{source_id}' has no edge{wanted} to '{target_id}'")

        source.metadata["edges"] = json.dumps([
            edge for edge in edges
            if not (edge["target_id"] == target_id and edge["edge_type"] in removed)
        ])
        self._repo.upsert(collection, [source])

        if "supersedes" in removed and not is_area_qualified(target_id):
            targets = self._repo.get_by_ids(collection, [target_id])
            if targets and targets[0].metadata.get("superseded_by") == source_id:
                target = targets[0]
                target.metadata.pop("superseded_by", None)
                target.metadata.pop("valid_until", None)
                self._repo.upsert(collection, [target])
        return removed
