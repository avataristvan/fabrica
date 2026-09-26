"""BoostConfidenceUseCase: a /reflect citation -- boost_count, cue, unknown-id skipping."""
from __future__ import annotations

from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.boost_confidence import BoostConfidenceUseCase
from ai_mem.application.get_memory import GetMemoryUseCase


def test_boost_increments_boost_count(tmp_repo):
    AddMemoryUseCase(tmp_repo).execute(collection="col", documents=["x"], ids=["a"])
    n = BoostConfidenceUseCase(tmp_repo).execute("col", ["a"])
    assert n == 1
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["boost_count"] == 1


def test_repeated_boosts_accumulate(tmp_repo):
    AddMemoryUseCase(tmp_repo).execute(collection="col", documents=["x"], ids=["a"])
    boost = BoostConfidenceUseCase(tmp_repo)
    boost.execute("col", ["a"])
    boost.execute("col", ["a"])
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["boost_count"] == 2


def test_boost_does_not_touch_confidence(tmp_repo):
    """Confidence was dropped as a trust signal -- boost never reads or writes it, even when
    an older entry still carries a legacy value."""
    AddMemoryUseCase(tmp_repo).execute(
        collection="col", documents=["x"], ids=["a"], metadatas=[{"confidence": 0.5}]
    )
    BoostConfidenceUseCase(tmp_repo).execute("col", ["a"])
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["confidence"] == 0.5


def test_unknown_ids_silently_skipped(tmp_repo):
    n = BoostConfidenceUseCase(tmp_repo).execute("col", ["does-not-exist"])
    assert n == 0


def test_return_count_matches_found_entries(tmp_repo):
    add = AddMemoryUseCase(tmp_repo)
    add.execute(collection="col", documents=["x", "y"], ids=["a", "b"])
    n = BoostConfidenceUseCase(tmp_repo).execute("col", ["a", "b", "missing"])
    assert n == 2


def test_cue_is_set_alongside_boost(tmp_repo):
    AddMemoryUseCase(tmp_repo).execute(collection="col", documents=["x"], ids=["a"])
    BoostConfidenceUseCase(tmp_repo).execute("col", ["a"], cue="when X happens")
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["cue"] == "when X happens"
    assert meta["boost_count"] == 1


# ---------------------------------------------------------------------------
# track_access wiring: every boost call is the /reflect citation signal.
# ---------------------------------------------------------------------------

def test_without_track_access_does_not_error(tmp_repo):
    """Default (no track_access injected) -- existing callers that don't care about
    access tracking keep working unchanged."""
    AddMemoryUseCase(tmp_repo).execute(collection="col", documents=["x"], ids=["a"])
    n = BoostConfidenceUseCase(tmp_repo).execute("col", ["a"])
    assert n == 1


def test_boost_bumps_last_accessed_at(tmp_repo, track_access):
    AddMemoryUseCase(tmp_repo).execute(collection="col", documents=["x"], ids=["a"])
    created_at = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata["created_at"]
    BoostConfidenceUseCase(tmp_repo, track_access).execute("col", ["a"])
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["last_accessed_at"] >= created_at
