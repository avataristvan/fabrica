"""Boost or decay the confidence score on existing memory entries."""
from __future__ import annotations

from ai_mem.application.experience_index import normalize_cue
from ai_mem.application.track_access import TrackAccessUseCase
from ai_mem.domain.memory import MemoryEntry, MemoryRepository


class BoostConfidenceUseCase:
    def __init__(self, repo: MemoryRepository, track_access: TrackAccessUseCase | None = None) -> None:
        self._repo = repo
        self._track_access = track_access

    def execute(self, collection: str, ids: list[str], delta: float, cue: str | None = None) -> int:
        """Apply delta to confidence on existing entries. Returns count of updated entries.

        Entries not found in the collection are silently skipped.
        Delta is clamped so the result stays in [0.0, 1.0].
        `cue` sets (or, when empty, clears) the entry's experience-index cue; delta=0 records
        the cue alone, without a boost or an access bump.
        """
        cue_text = normalize_cue(cue) if cue is not None else None
        existing = self._repo.get_by_ids(collection, ids)
        if not existing:
            return 0

        updated: list[MemoryEntry] = []
        for entry in existing:
            if delta:
                prior = float(entry.metadata.get("confidence", 1.0))
                entry.metadata["confidence"] = max(0.0, min(1.0, prior + delta))
            prior_boosts = int(entry.metadata.get("boost_count", 0))
            if delta > 0:
                entry.metadata["boost_count"] = prior_boosts + 1
            if cue_text is not None:
                # "" clears: Chroma's upsert merges metadata keys, so a popped key would survive
                # (same convention as superseded_by / valid_until).
                entry.metadata["cue"] = cue_text
            updated.append(entry)

        self._repo.upsert(collection, updated)

        # A positive boost is the /reflect citation signal (access_count
        # means deliberate use): the agent deliberately confirmed this
        # entry mattered, which is stronger evidence of use than a passive query hit. A decay
        # (delta <= 0) is the opposite signal -- the entry was wrong or unhelpful -- and must not
        # inflate access_count.
        if delta > 0 and self._track_access is not None:
            self._track_access.execute(collection, [entry.id for entry in updated])

        return len(updated)
