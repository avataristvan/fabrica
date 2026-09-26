"""Record a /reflect citation on existing memory entries.

Confidence was dropped as a trust signal (see domain_drop_confidence_for_evidence_and_
librarian_2026_09_26): a numeric score converged to popularity, not relevance, and hid
its own "why". A 'confirms' edge (mem_link), 'supersedes'/'contradicts', and this cue
are the replacement -- traceable evidence a reader can check, instead of a number to
trust blindly. This use case no longer reads or writes confidence at all: every call is
itself the citation signal, so it increments boost_count and, optionally, sets the
entry's experience-index cue.
"""
from __future__ import annotations

from ai_mem.application.experience_index import normalize_cue
from ai_mem.application.track_access import TrackAccessUseCase
from ai_mem.domain.memory import MemoryEntry, MemoryRepository


class BoostConfidenceUseCase:
    def __init__(self, repo: MemoryRepository, track_access: TrackAccessUseCase | None = None) -> None:
        self._repo = repo
        self._track_access = track_access

    def execute(self, collection: str, ids: list[str], cue: str | None = None) -> int:
        """Record a /reflect citation: increments boost_count and, when `cue` is given, sets
        (or, when empty, clears) the entry's experience-index cue. Returns count of updated
        entries; entries not found in the collection are silently skipped.
        """
        cue_text = normalize_cue(cue) if cue is not None else None
        existing = self._repo.get_by_ids(collection, ids)
        if not existing:
            return 0

        updated: list[MemoryEntry] = []
        for entry in existing:
            entry.metadata["boost_count"] = int(entry.metadata.get("boost_count", 0)) + 1
            if cue_text is not None:
                # "" clears: Chroma's upsert merges metadata keys, so a popped key would survive
                # (same convention as superseded_by / valid_until).
                entry.metadata["cue"] = cue_text
            updated.append(entry)

        self._repo.upsert(collection, updated)

        # Every call is itself the /reflect citation signal -- the agent deliberately cited this
        # entry, which is stronger evidence of use than a passive query hit.
        if self._track_access is not None:
            self._track_access.execute(collection, [entry.id for entry in updated])

        return len(updated)
