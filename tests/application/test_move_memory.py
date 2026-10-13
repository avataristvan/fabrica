"""Tests for MoveMemoryUseCase."""
from __future__ import annotations

from pathlib import Path

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.domain.memory import MemoryEdge
from ai_mem.application.move_memory import MoveMemoryUseCase


def _seed(repo, collection: str, docs: dict[str, str], metadatas: list[dict] | None = None) -> None:
    """Add entries: {id: text}."""
    AddMemoryUseCase(repo).execute(
        collection=collection,
        documents=list(docs.values()),
        ids=list(docs.keys()),
        metadatas=metadatas,
    )


def test_move_basic_preserves_metadata(tmp_repo):
    _seed(tmp_repo, "source", {"a": "some entry text"}, metadatas=[{"confidence": 0.9, "type": "pattern"}])

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["a"])

    assert result.moved_ids == ["a"]
    assert result.not_found_ids == []
    assert result.conflicts == []
    assert tmp_repo.get_by_ids("source", ["a"]) == []

    moved = tmp_repo.get_by_ids("target", ["a"])
    assert len(moved) == 1
    assert moved[0].text == "some entry text"
    assert moved[0].metadata["confidence"] == 0.9
    assert moved[0].metadata["type"] == "pattern"


def test_move_missing_id_in_source(tmp_repo):
    _seed(tmp_repo, "source", {"a": "present entry"})

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["a", "ghost"])

    assert result.moved_ids == ["a"]
    assert result.not_found_ids == ["ghost"]
    assert result.conflicts == []


def test_move_missing_id_only_writes_nothing(tmp_repo):
    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["ghost"])

    assert result.moved_ids == []
    assert result.not_found_ids == ["ghost"]
    assert result.conflicts == []
    assert tmp_repo.get_by_ids("target", ["ghost"]) == []


def test_move_conflict_when_target_has_different_text(tmp_repo):
    _seed(tmp_repo, "source", {"a": "source version of the text"})
    _seed(tmp_repo, "target", {"a": "different target version"})

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["a"])

    assert result.moved_ids == []
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict.id == "a"
    assert conflict.existing_text_preview == "different target version"
    assert conflict.source_text_preview == "source version of the text"

    # untouched on both sides
    assert tmp_repo.get_by_ids("source", ["a"])[0].text == "source version of the text"
    assert tmp_repo.get_by_ids("target", ["a"])[0].text == "different target version"


def test_move_no_conflict_when_target_has_identical_text(tmp_repo):
    _seed(tmp_repo, "source", {"a": "identical text"})
    _seed(tmp_repo, "target", {"a": "identical text"})

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["a"])

    assert result.moved_ids == ["a"]
    assert result.conflicts == []
    assert tmp_repo.get_by_ids("source", ["a"]) == []
    assert tmp_repo.get_by_ids("target", ["a"])[0].text == "identical text"


def test_move_creates_target_collection_implicitly(tmp_repo):
    _seed(tmp_repo, "source", {"a": "entry for a brand new collection"})

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "brand_new_target", ["a"])

    assert result.moved_ids == ["a"]
    assert tmp_repo.get_by_ids("brand_new_target", ["a"])[0].text == "entry for a brand new collection"


def test_move_mixed_batch(tmp_repo):
    _seed(tmp_repo, "source", {
        "clean": "clean move entry",
        "conflicted": "source side of conflict",
        "same_text": "shared text unchanged",
    })
    _seed(tmp_repo, "target", {
        "conflicted": "target side of conflict",
        "same_text": "shared text unchanged",
    })

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["clean", "conflicted", "same_text", "missing"])

    assert set(result.moved_ids) == {"clean", "same_text"}
    assert result.not_found_ids == ["missing"]
    assert len(result.conflicts) == 1
    assert result.conflicts[0].id == "conflicted"

    assert tmp_repo.get_by_ids("source", ["clean"]) == []
    assert tmp_repo.get_by_ids("source", ["same_text"]) == []
    assert tmp_repo.get_by_ids("source", ["conflicted"])[0].text == "source side of conflict"
    assert tmp_repo.get_by_ids("target", ["clean"])[0].text == "clean move entry"


def test_move_same_collection_raises_and_does_not_delete(tmp_repo):
    _seed(tmp_repo, "source", {"a": "entry text"})

    move = MoveMemoryUseCase(tmp_repo)
    with pytest.raises(ValueError):
        move.execute("source", "source", ["a"])

    assert tmp_repo.get_by_ids("source", ["a"])[0].text == "entry text"


def test_move_duplicate_ids_are_deduped(tmp_repo):
    _seed(tmp_repo, "source", {"a": "entry text"})

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["a", "a"])

    assert result.moved_ids == ["a"]
    assert tmp_repo.get_by_ids("target", ["a"])[0].text == "entry text"


def test_move_all_conflicts_does_not_touch_source(tmp_repo):
    _seed(tmp_repo, "source", {"a": "source text", "b": "source text b"})
    _seed(tmp_repo, "target", {"a": "different target text", "b": "different target text b"})

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", ["a", "b"])

    assert result.moved_ids == []
    assert len(result.conflicts) == 2
    assert tmp_repo.get_by_ids("source", ["a", "b"]) != []
    assert len(tmp_repo.get_by_ids("source", ["a", "b"])) == 2


def test_move_empty_ids_does_not_drop_source_collection(tmp_repo):
    _seed(tmp_repo, "source", {"a": "entry text"})

    move = MoveMemoryUseCase(tmp_repo)
    result = move.execute("source", "target", [])

    assert result.moved_ids == []
    assert result.not_found_ids == []
    assert result.conflicts == []
    assert tmp_repo.get_by_ids("source", ["a"])[0].text == "entry text"


# --- MoveToAreaUseCase (area -> area, used by `mem move`) ---------------------------------------

import json  # noqa: E402

from ai_mem.application.move_memory import MoveToAreaUseCase  # noqa: E402
from ai_mem.infrastructure.areas import area_records_dir  # noqa: E402
from ai_mem.infrastructure.file_repository import FileMemoryRepository  # noqa: E402
from ai_mem.mem_cli import _AreaAddressing  # noqa: E402


@pytest.fixture
def two_areas(tmp_path):
    keys = []
    for name in ("src", "dst", "far"):
        (tmp_path / name / "docs" / "records").mkdir(parents=True)
        keys.append(str((tmp_path / name).resolve()))
    repo = FileMemoryRepository(tmp_path, records_dir_for=area_records_dir)
    return repo, MoveToAreaUseCase(repo, _AreaAddressing()), *keys


def _edges(repo, key, entry_id):
    return {(e.target_id, e.edge_type) for e in repo.get_edges(key, entry_id)}


def test_area_move_requalifies_edges_and_resolves_round_trip(two_areas):
    repo, use_case, src, dst, far = two_areas
    _seed(repo, src, {"a": "A.", "b": "B.", "ref": "R."}, [{"type": "learning"}] * 3)
    _seed(repo, dst, {"t": "T."}, [{"type": "learning"}])
    repo.add_edge(src, "a", MemoryEdge("b", "related"))
    repo.add_edge(src, "a", MemoryEdge("../dst:t", "related"))
    repo.add_edge(src, "ref", MemoryEdge("a", "derived_from"))

    plan = use_case.plan(src, dst, ["a"], [src, dst, far])
    assert plan.conflicts == []
    use_case.apply(plan)

    assert repo.get_by_ids(src, ["a"]) == []
    assert _edges(repo, dst, "a") == {("../src:b", "related"), ("t", "related")}
    assert _edges(repo, src, "ref") == {("../dst:a", "derived_from")}
    for target, _ in _edges(repo, dst, "a"):
        assert _AreaAddressing().resolve(dst, target) is not None


def test_area_move_reports_but_never_writes_third_area(two_areas):
    repo, use_case, src, dst, far = two_areas
    _seed(repo, src, {"a": "A."}, [{"type": "learning"}])
    _seed(repo, far, {"f": "F."}, [{"type": "learning"}])
    repo.add_edge(far, "f", MemoryEdge("../src:a", "related"))
    before = [(path, path.read_bytes()) for path in sorted((Path(far) / "docs").rglob("*.md"))]

    plan = use_case.plan(src, dst, ["a"], [src, dst, far])
    use_case.apply(plan)

    assert [(op.kind, op.area, op.id) for op in plan.ops if op.kind == "report"] == [("report", far, "f")]
    assert before == [(path, path.read_bytes()) for path in sorted((Path(far) / "docs").rglob("*.md"))]


def test_area_move_identical_target_is_not_a_conflict_and_differing_is(two_areas):
    repo, use_case, src, dst, _ = two_areas
    _seed(repo, src, {"same": "S.", "diff": "D."}, [{"type": "learning"}] * 2)
    _seed(repo, dst, {"diff": "other"}, [{"type": "learning"}])
    repo.upsert(dst, repo.get_by_ids(src, ["same"]))  # an exact copy, as left by an interrupted move

    plan = use_case.plan(src, dst, ["same", "diff"], [])
    assert [c.id for c in plan.conflicts] == ["diff"]
    with pytest.raises(ValueError):
        use_case.apply(plan)
    assert len(repo.get_by_ids(src, ["same", "diff"])) == 2


def test_area_move_refuses_to_split_a_supersede_pair(two_areas):
    repo, use_case, src, dst, _ = two_areas
    _seed(repo, src, {"old": "O.", "new": "N."}, [{"type": "learning"}] * 2)
    AddEdgeUseCase(repo).execute(src, "new", "old", "supersedes")

    assert use_case.plan(src, dst, ["new"], []).conflicts
    assert use_case.plan(src, dst, ["old"], []).conflicts
    assert not use_case.plan(src, dst, ["old", "new"], []).conflicts


def test_area_move_unknown_id_and_same_area(two_areas):
    _, use_case, src, dst, _ = two_areas
    assert use_case.plan(src, dst, ["nope"], []).not_found_ids == ["nope"]
    with pytest.raises(ValueError):
        use_case.plan(src, src, ["nope"], [])


def test_area_move_qualified_self_reference_to_co_moved_record_becomes_bare(two_areas):
    repo, use_case, src, dst, _ = two_areas
    _seed(repo, src, {"a": "A.", "b": "B."}, [{"type": "learning"}] * 2)
    repo.add_edge(src, "a", MemoryEdge("../src:b", "related"))

    use_case.apply(use_case.plan(src, dst, ["a", "b"], []))

    assert _edges(repo, dst, "a") == {("b", "related")}


def test_area_move_reports_target_referrer_that_could_now_be_bare(two_areas):
    repo, use_case, src, dst, _ = two_areas
    _seed(repo, src, {"x": "X."}, [{"type": "learning"}])
    _seed(repo, dst, {"r": "R."}, [{"type": "learning"}])
    repo.add_edge(dst, "r", MemoryEdge("../src:x", "related"))
    before = _edges(repo, dst, "r")

    plan = use_case.plan(src, dst, ["x"], [])
    use_case.apply(plan)

    assert [(op.kind, op.area, op.id) for op in plan.ops if op.kind == "report"] == [("report", dst, "r")]
    assert _edges(repo, dst, "r") == before


class _CorruptEdges:
    """mock: wraps a repository and hands out one entry whose stored `edges` field is not valid JSON."""

    def __init__(self, repo, bad_id):
        self._repo, self._bad = repo, bad_id

    def __getattr__(self, name):
        return getattr(self._repo, name)

    def _corrupt(self, entries):
        for entry in entries:
            if entry.id == self._bad:
                entry.metadata["edges"] = "{not json"
        return entries

    def get_by_ids(self, collection, ids):
        return self._corrupt(self._repo.get_by_ids(collection, ids))

    def get_all(self, collection):
        return self._corrupt(self._repo.get_all(collection))


@pytest.mark.parametrize("bad_id", ["moved", "bystander"])
def test_area_move_malformed_edges_is_a_conflict_naming_the_record(two_areas, bad_id):
    repo, _, src, dst, _ = two_areas
    _seed(repo, src, {"moved": "M.", "bystander": "B."}, [{"type": "learning"}] * 2)
    use_case = MoveToAreaUseCase(_CorruptEdges(repo, bad_id), _AreaAddressing())

    plan = use_case.plan(src, dst, ["moved"], [src, dst])

    assert [c.id for c in plan.conflicts] == [bad_id]
    assert "malformed edges" in plan.conflicts[0].reason
    with pytest.raises(ValueError):
        use_case.apply(plan)
    assert repo.get_by_ids(dst, ["moved"]) == []
