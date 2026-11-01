"""Add a typed causal edge between two memory entries."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from ai_mem.domain.memory import AreaRefs, EdgeType, MemoryEdge, MemoryRepository, is_area_qualified


class AddEdgeUseCase:
    def __init__(
        self,
        repo: MemoryRepository,
        area_refs: AreaRefs | None = None,
        source_exists: Callable[[str, str], bool] | None = None,
    ) -> None:
        self._repo = repo
        self._area_refs = area_refs
        self._source_exists = source_exists or (lambda _collection, _slug: False)

    def _source_target(self, collection: str, target_id: str, edge_type: EdgeType) -> bool:
        """True when `target_id` names a source of `collection`; raises for 'supersedes', which would write into it."""
        if not self._source_exists(collection, target_id):
            return False
        if edge_type == "supersedes":
            raise ValueError(f"{target_id!r} is a source; a source is frozen and cannot be superseded")
        return True

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

        A 'derived_from' edge (source is the decision, target the learning it is based on) only
        stores the edge; the same self-link rule applies.

        A target may also be a source (`docs/sources/<slug>.md`, checked through `source_exists`), for
        every edge type except 'supersedes'; nothing is written into the source.

        An area-qualified target (`<rel-area-path>:<id>`) must resolve through `area_refs` to an
        existing entry or source in that area. The edge is stored as given, on the source only; the other
        area is never written, so 'supersedes' across areas is refused (it would flag the target).
        """
        if is_area_qualified(target_id):
            self._add_cross_area_edge(collection, source_id, target_id, edge_type)
            return

        # Checked before the fetch: get_by_ids([x, x]) makes ChromaDB raise DuplicateIDError.
        if edge_type == "supersedes" and source_id == target_id:
            raise ValueError(f"An entry cannot supersede itself: '{source_id}'")
        if edge_type == "confirms" and source_id == target_id:
            raise ValueError(f"An entry cannot confirm itself: '{source_id}'")
        if edge_type == "derived_from" and source_id == target_id:
            raise ValueError(f"An entry cannot be derived from itself: '{source_id}'")

        entries = {entry.id: entry for entry in self._repo.get_by_ids(collection, [source_id, target_id])}
        missing = [id_ for id_ in (source_id, target_id) if id_ not in entries]
        if missing == [target_id] and self._source_target(collection, target_id, edge_type):
            self._repo.add_edge(collection, source_id, MemoryEdge(target_id=target_id, edge_type=edge_type))
            return
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

    def _add_cross_area_edge(self, collection: str, source_id: str, target_id: str, edge_type: EdgeType) -> None:
        if edge_type == "supersedes":
            raise ValueError(
                f"'supersedes' across areas is refused ({target_id!r}): it would write into the other area. "
                f"Use 'related' or 'derived_from', and supersede inside the target area itself."
            )
        resolved = self._area_refs.resolve(collection, target_id) if self._area_refs is not None else None
        if resolved is None:
            raise ValueError(f"Area-qualified target {target_id!r} does not resolve to an area from '{collection}'")
        target_collection, bare_target = resolved
        if edge_type in ("confirms", "derived_from") and (target_collection, bare_target) == (collection, source_id):
            raise ValueError(f"'{source_id}' cannot point a '{edge_type}' edge at itself ({target_id!r})")
        if not self._repo.get_by_ids(collection, [source_id]):
            raise ValueError(f"Entry ID(s) not found in '{collection}': {[source_id]}")
        if not self._repo.get_by_ids(target_collection, [bare_target]) and not self._source_target(
            target_collection, bare_target, edge_type
        ):
            raise ValueError(f"Entry ID {bare_target!r} not found in area '{target_collection}'")
        self._repo.add_edge(collection, source_id, MemoryEdge(target_id=target_id, edge_type=edge_type))
