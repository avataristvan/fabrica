"""Add a typed causal edge between two memory entries."""
from __future__ import annotations

from datetime import datetime, timezone

from ai_mem.domain.memory import EdgeType, MemoryEdge, MemoryRepository


class AddEdgeUseCase:
    def __init__(self, repo: MemoryRepository) -> None:
        self._repo = repo

    def execute(
        self,
        collection: str,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
    ) -> None:
        """Link source_id → target_id with the given edge_type.

        Raises ValueError if either entry does not exist in the collection.
        Silently deduplicates if the same (target_id, edge_type) already exists.

        A 'supersedes' edge (source is the newer entry replacing target) additionally flags the
        target with `superseded_by` and `valid_until` metadata, so a query that retrieves the
        target can warn and point at the successor -- edges are only stored on the source, so
        the edge alone would never surface from the target's side. Raises ValueError when the
        source is the target itself or is already superseded (which would allow cycles).

        A 'confirms' edge (source is the later entry bearing out the earlier target) is evidence,
        not a score: it only stores the edge. Raises ValueError when the source is the target.
        """
        # Checked before the fetch: get_by_ids([x, x]) makes ChromaDB raise DuplicateIDError.
        if edge_type == "supersedes" and source_id == target_id:
            raise ValueError(f"An entry cannot supersede itself: '{source_id}'")
        if edge_type == "confirms" and source_id == target_id:
            raise ValueError(f"An entry cannot confirm itself: '{source_id}'")

        entries = {entry.id: entry for entry in self._repo.get_by_ids(collection, [source_id, target_id])}
        missing = [id_ for id_ in (source_id, target_id) if id_ not in entries]
        if missing:
            raise ValueError(f"Entry ID(s) not found in '{collection}': {missing}")

        if edge_type == "supersedes" and (successor := entries[source_id].metadata.get("superseded_by")):
            raise ValueError(f"'{source_id}' is itself superseded by '{successor}'; link '{successor}' instead")

        self._repo.add_edge(collection, source_id, MemoryEdge(target_id=target_id, edge_type=edge_type))

        if edge_type == "supersedes":
            # add_edge only rewrote the source, so the target fetched above is still current.
            # Metadata is round-tripped whole, as BoostConfidence does.
            target = entries[target_id]
            target.metadata["superseded_by"] = source_id
            target.metadata["valid_until"] = datetime.now(tz=timezone.utc).timestamp()
            self._repo.upsert(collection, [target])
