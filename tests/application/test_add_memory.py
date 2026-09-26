"""AddMemoryUseCase: timestamp injection, TTL, history preservation on update."""
from __future__ import annotations

from datetime import datetime, timezone

from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.get_memory import GetMemoryUseCase
from ai_mem.application.track_access import TrackAccessUseCase
from ai_mem.domain.memory import MemoryEntry


def test_created_at_is_injected(tmp_repo):
    use_case = AddMemoryUseCase(tmp_repo)
    before = datetime.now(tz=timezone.utc).timestamp()
    use_case.execute(collection="test_col", documents=["hi"], ids=["a"])
    after = datetime.now(tz=timezone.utc).timestamp()

    fetched = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])
    assert len(fetched) == 1
    meta = fetched[0].metadata
    assert before <= meta["created_at"] <= after
    assert meta["last_accessed_at"] == meta["created_at"]
    assert "access_count" not in meta
    assert "expires_at" not in meta


def test_ttl_sets_expires_at(tmp_repo):
    AddMemoryUseCase(tmp_repo).execute(
        collection="test_col", documents=["hi"], ids=["a"], ttl_days=1.0
    )
    fetched = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])
    delta = fetched[0].metadata["expires_at"] - fetched[0].metadata["created_at"]
    assert abs(delta - 86400) < 1.0


def test_readd_preserves_last_accessed_at(tmp_repo):
    """Re-adding an existing id keeps created_at and last_accessed_at."""
    add = AddMemoryUseCase(tmp_repo)
    track = TrackAccessUseCase(tmp_repo)

    add.execute(collection="test_col", documents=["v1"], ids=["a"])
    track.execute("test_col", ["a"])

    before = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])[0].metadata

    add.execute(collection="test_col", documents=["v2 updated text"], ids=["a"])

    after = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])[0]
    assert after.text == "v2 updated text"
    assert after.metadata["created_at"] == before["created_at"]
    assert after.metadata["last_accessed_at"] == before["last_accessed_at"]


def test_new_entry_has_no_confidence_or_access_count(tmp_repo):
    """confidence/access_count were dropped as trust signals -- mem_add no longer defaults
    or computes either for a brand-new entry."""
    AddMemoryUseCase(tmp_repo).execute(collection="test_col", documents=["x"], ids=["a"])
    meta = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])[0].metadata
    assert "confidence" not in meta
    assert "access_count" not in meta


def test_readd_preserves_legacy_confidence_and_access_count(tmp_repo):
    """Stale data is never migrated or deleted, only no longer produced: a pre-existing
    confidence/access_count from before the drop must survive re-add unchanged."""
    tmp_repo.upsert("test_col", [MemoryEntry(
        id="a", text="v1", metadata={"confidence": 0.9, "access_count": 7, "created_at": 1.0},
    )])
    AddMemoryUseCase(tmp_repo).execute(collection="test_col", documents=["v2"], ids=["a"])
    meta = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])[0].metadata
    assert meta["confidence"] == 0.9
    assert meta["access_count"] == 7


def test_explicit_confidence_in_metadata_is_stored_as_is(tmp_repo):
    """mem_add no longer computes confidence, but does not strip an explicitly-passed key
    either -- it is stored like any other ordinary user-supplied metadata field."""
    AddMemoryUseCase(tmp_repo).execute(
        collection="test_col", documents=["x"], ids=["a"],
        metadatas=[{"confidence": 0.6}],
    )
    meta = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])[0].metadata
    assert meta["confidence"] == 0.6


def test_confidence_delta_metadata_is_no_longer_interpreted(tmp_repo):
    """confidence_delta is dead: mem_add stores it as an inert key rather than computing
    a confidence value from it."""
    AddMemoryUseCase(tmp_repo).execute(
        collection="test_col", documents=["x"], ids=["a"], metadatas=[{"confidence_delta": 0.3}],
    )
    meta = GetMemoryUseCase(tmp_repo).execute("test_col", ["a"])[0].metadata
    assert "confidence" not in meta
    assert meta["confidence_delta"] == 0.3
