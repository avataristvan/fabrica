"""Tests for MoveToAreaUseCase (area -> area, used by `mem move`)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.move_memory import MoveToAreaUseCase
from ai_mem.domain.memory import MemoryEdge
from ai_mem.infrastructure.areas import area_records_dir
from ai_mem.infrastructure.file_repository import FileMemoryRepository
from ai_mem.mem_cli import _AreaAddressing


def _seed(repo, collection: str, docs: dict[str, str], metadatas: list[dict] | None = None) -> None:
    """Add entries: {id: text}."""
    AddMemoryUseCase(repo).execute(
        collection=collection,
        documents=list(docs.values()),
        ids=list(docs.keys()),
        metadatas=metadatas,
    )


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
