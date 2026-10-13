"""Tests for the 'supersedes' edge: flagging the target."""
from __future__ import annotations

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase


def _seed(repo, docs: dict[str, str], **shared_meta) -> None:
    AddMemoryUseCase(repo).execute(
        collection="col",
        documents=list(docs.values()),
        ids=list(docs.keys()),
        metadatas=[dict(shared_meta) for _ in docs] if shared_meta else None,
    )


def _meta(repo, entry_id: str) -> dict:
    return repo.get_by_ids("col", [entry_id])[0].metadata


# ---------------------------------------------------------------------------
# AddEdgeUseCase
# ---------------------------------------------------------------------------

def test_supersedes_flags_target_and_keeps_its_other_metadata(tmp_repo):
    _seed(tmp_repo, {"old": "the old rule", "new": "the new rule"})
    AddMemoryUseCase(tmp_repo).execute("col", ["the old rule"], ["old"], metadatas=[{"confidence": 0.9}])

    AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")

    meta = _meta(tmp_repo, "old")
    assert meta["superseded_by"] == "new"
    assert meta["valid_until"] > 0
    assert meta["confidence"] == 0.9
    assert tmp_repo.get_by_ids("col", ["old"])[0].text == "the old rule"
    assert [(e.target_id, e.edge_type) for e in tmp_repo.get_edges("col", "new")] == [("old", "supersedes")]


def test_supersedes_does_not_flag_the_source(tmp_repo):
    _seed(tmp_repo, {"old": "old", "new": "new"})
    AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")
    assert not _meta(tmp_repo, "new").get("superseded_by")


def test_other_edge_types_do_not_flag_target(tmp_repo):
    _seed(tmp_repo, {"a": "a", "b": "b"})
    AddEdgeUseCase(tmp_repo).execute("col", "b", "a", "contradicts")
    assert "superseded_by" not in _meta(tmp_repo, "a")


def test_entry_cannot_supersede_itself(tmp_repo):
    _seed(tmp_repo, {"a": "a"})
    with pytest.raises(ValueError, match="itself"):
        AddEdgeUseCase(tmp_repo).execute("col", "a", "a", "supersedes")
    assert tmp_repo.get_edges("col", "a") == []


def test_superseded_entry_cannot_supersede_another(tmp_repo):
    _seed(tmp_repo, {"a": "a", "b": "b", "c": "c"})
    add_edge = AddEdgeUseCase(tmp_repo)
    add_edge.execute("col", "b", "a", "supersedes")  # a is now superseded by b

    with pytest.raises(ValueError, match="superseded by 'b'"):
        add_edge.execute("col", "a", "c", "supersedes")  # would allow a cycle a -> c -> ... -> a
    assert tmp_repo.get_edges("col", "a") == []
    assert not _meta(tmp_repo, "c").get("superseded_by")


def test_supersedes_raises_on_missing_entry_without_writing(tmp_repo):
    _seed(tmp_repo, {"new": "new"})
    with pytest.raises(ValueError, match="not found"):
        AddEdgeUseCase(tmp_repo).execute("col", "new", "ghost", "supersedes")
    assert tmp_repo.get_edges("col", "new") == []
