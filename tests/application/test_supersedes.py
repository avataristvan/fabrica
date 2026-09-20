"""Tests for the 'supersedes' edge: flagging the target and surfacing the successor in queries."""
from __future__ import annotations

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.get_memory import GetMemoryUseCase
from ai_mem.application.query_memory import QueryMemoryUseCase
from ai_mem.application.track_access import TrackAccessUseCase


def _seed(repo, docs: dict[str, str], **shared_meta) -> None:
    AddMemoryUseCase(repo).execute(
        collection="col",
        documents=list(docs.values()),
        ids=list(docs.keys()),
        metadatas=[dict(shared_meta) for _ in docs] if shared_meta else None,
    )


def _query(repo, text: str, n_results: int):
    return QueryMemoryUseCase(repo, TrackAccessUseCase(repo)).execute("col", text, n_results=n_results)


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


# ---------------------------------------------------------------------------
# QueryMemoryUseCase
# ---------------------------------------------------------------------------

def test_query_returns_superseded_entry_flagged_and_appends_successor(tmp_repo):
    # 'new' shares no vocabulary with the query, so only the supersession can surface it.
    _seed(tmp_repo, {
        "old": "skip validation because it slows things down",
        "new": "ZZZQQQXXX completely unrelated boilerplate content here",
    })
    AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")

    results = _query(tmp_repo, "skip validation", n_results=1)

    assert results[0].id == "old"
    assert results[0].metadata["superseded_by"] == "new"
    appended = [r for r in results if r.metadata.get("via_edge") == "superseded_by"]
    assert [r.id for r in appended] == ["new"]
    assert appended[0].metadata["via_source"] == "old"


def test_query_does_not_append_successor_twice_when_already_in_results(tmp_repo):
    _seed(tmp_repo, {
        "old": "validate user input before processing (old wording)",
        "new": "validate user input before processing (new wording)",
    })
    AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")

    results = _query(tmp_repo, "validate user input", n_results=5)

    assert [r.id for r in results].count("new") == 1


def test_query_follows_chain_to_newest_successor(tmp_repo):
    _seed(tmp_repo, {
        "v1": "skip validation because it slows things down",
        "v2": "ZZZ second revision unrelated wording",
        "v3": "QQQ third revision unrelated wording",
    })
    add_edge = AddEdgeUseCase(tmp_repo)
    add_edge.execute("col", "v2", "v1", "supersedes")
    add_edge.execute("col", "v3", "v2", "supersedes")

    results = _query(tmp_repo, "skip validation", n_results=1)

    appended = [r.id for r in results if r.metadata.get("via_edge") == "superseded_by"]
    assert appended == ["v3"]


def test_query_survives_deleted_successor(tmp_repo):
    _seed(tmp_repo, {"old": "skip validation because it slows things down", "new": "ZZZ unrelated"})
    AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")
    tmp_repo.delete("col", ["new"])

    results = _query(tmp_repo, "skip validation", n_results=1)

    assert [r.id for r in results] == ["old"]
    assert results[0].metadata["superseded_by"] == "new"


def test_query_survives_cyclic_superseded_by_metadata(tmp_repo):
    """Hand-edited metadata must not make the successor lookup loop."""
    AddMemoryUseCase(tmp_repo).execute(
        "col", ["skip validation because it is slow", "ZZZ other"], ["a", "b"],
        metadatas=[{"superseded_by": "b"}, {"superseded_by": "a"}],
    )
    results = _query(tmp_repo, "skip validation", n_results=1)
    assert results[0].id == "a"


def test_superseded_successor_takes_edge_budget_before_ordinary_edges(tmp_repo):
    _seed(tmp_repo, {
        "old": "alpha topic rule, old version",
        "src": "alpha topic rule, other note",
        "new": "ZZZ replacement entry unrelated wording",
        "t1": "QQQ linked target one",
        "t2": "XXX linked target two",
    })
    add_edge = AddEdgeUseCase(tmp_repo)
    add_edge.execute("col", "new", "old", "supersedes")
    add_edge.execute("col", "src", "t1", "related")
    add_edge.execute("col", "src", "t2", "related")

    results = _query(tmp_repo, "alpha topic rule", n_results=2)

    appended = [(r.id, r.metadata["via_edge"]) for r in results if r.metadata.get("via_edge")]
    assert appended[0] == ("new", "superseded_by")
    assert len(appended) == 2  # budget of 2 is shared


def test_clearing_superseded_by_undoes_the_flag(tmp_repo):
    _seed(tmp_repo, {"old": "skip validation because it slows things down", "new": "ZZZ unrelated"})
    AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")

    AddMemoryUseCase(tmp_repo).execute(
        "col", ["skip validation because it slows things down"], ["old"],
        metadatas=[{"superseded_by": "", "valid_until": ""}],
    )
    results = _query(tmp_repo, "skip validation", n_results=1)

    assert not any(r.metadata.get("via_edge") == "superseded_by" for r in results)
    assert GetMemoryUseCase(tmp_repo).execute("col", ["old"])[0].metadata["superseded_by"] == ""
