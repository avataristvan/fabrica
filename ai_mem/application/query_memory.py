"""Query memory semantically; records last_accessed_at for deliberate use."""
from __future__ import annotations

from collections import defaultdict

from ai_mem.application.track_access import TrackAccessUseCase
from ai_mem.domain.memory import MemoryRepository, QueryResult

_MAX_SUCCESSOR_HOPS = 5


class QueryMemoryUseCase:
    def __init__(
        self,
        repo: MemoryRepository,
        track_access: TrackAccessUseCase,
    ) -> None:
        self._repo = repo
        self._track_access = track_access
        self._session_hits: dict[str, set[str]] = defaultdict(set)

    def execute(
        self,
        collection: str,
        query: str,
        n_results: int = 5,
        max_age_days: float | None = None,
        type_filter: str | None = None,
        min_score_for_tracking: float | None = None,
    ) -> list[QueryResult]:
        results = self._repo.query(collection, query, n_results, max_age_days, type_filter)
        if not results:
            return []

        for idx, result in enumerate(results):
            result.rank = idx + 1

        returned_ids = {result.id for result in results}
        self._session_hits[collection].update(returned_ids)

        # last_accessed_at means deliberate use, not passive surfacing -- a result merely
        # appearing in a semantic search does not, by itself, count as access. min_score_for_tracking
        # is an explicit opt-in for callers with a real usage signal beyond "it matched":
        # posttool_hook passes a threshold because a strong match to the file just edited is itself
        # evidence of relevance, distinct from a query merely returning a candidate. Without a
        # threshold, no tracking happens here at all -- deliberate retrieval is tracked by
        # GetMemoryUseCase (mem_get by id) and BoostConfidenceUseCase (mem_boost, the /reflect
        # citation signal).
        if min_score_for_tracking is not None:
            tracked_ids = {result.id for result in results if result.score >= min_score_for_tracking}
            self._track_access.execute(collection, list(tracked_ids))

        results = self._append_linked(collection, results, returned_ids)
        return results

    def _append_linked(
        self, collection: str, results: list[QueryResult], result_ids: set[str]
    ) -> list[QueryResult]:
        """Append linked entries (budget: 2): first the live successor of every superseded
        result (so a stale hit always comes with what replaced it), then 1-hop edge targets."""
        linked: list[QueryResult] = []

        def append(entry, via_edge: str, via_source: str) -> None:
            linked_meta = dict(entry.metadata)
            linked_meta["via_edge"] = via_edge
            linked_meta["via_source"] = via_source
            linked.append(
                QueryResult(
                    rank=len(results) + len(linked) + 1,
                    id=entry.id,
                    score=0.0,
                    text=entry.text,
                    metadata=linked_meta,
                )
            )
            result_ids.add(entry.id)

        try:
            for result in results:
                if len(linked) >= 2:
                    break
                successor = self._live_successor(collection, result.metadata)
                if successor is not None and successor.id not in result_ids:
                    append(successor, "superseded_by", result.id)

            for result in results:
                if len(linked) >= 2:
                    break
                edges = self._repo.get_edges(collection, result.id)
                for edge in edges:
                    if len(linked) >= 2:
                        break
                    if edge.target_id in result_ids:
                        continue
                    entries = self._repo.get_by_ids(collection, [edge.target_id])
                    if not entries:
                        continue
                    append(entries[0], edge.edge_type, result.id)
        except Exception:
            pass
        return results + linked

    def _live_successor(self, collection: str, metadata: dict):
        """Follow `superseded_by` links to the newest entry that still exists, or None.

        Stops at a missing entry (deleted successor) and on cycles or after
        _MAX_SUCCESSOR_HOPS, so corrupt metadata cannot loop. The returned entry may itself
        still carry `superseded_by` when the chain ends in a deleted entry.
        """
        successor = None
        seen: set[str] = set()
        next_id = metadata.get("superseded_by")
        for _ in range(_MAX_SUCCESSOR_HOPS):
            if not next_id or next_id in seen:
                break
            seen.add(next_id)
            fetched = self._repo.get_by_ids(collection, [next_id])
            if not fetched:
                break
            successor = fetched[0]
            next_id = successor.metadata.get("superseded_by")
        return successor
