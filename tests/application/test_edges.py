"""Tests for AddEdgeUseCase (same-area and cross-area edges)."""
from __future__ import annotations

from pathlib import Path

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.domain.memory import MemoryEntry, TargetNotFound
from ai_mem.infrastructure.areas import AreaRefResolver, area_records_dir
from ai_mem.infrastructure.file_repository import FileMemoryRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed(repo, collection: str, docs: dict[str, str]) -> None:
    """Add entries: {id: text}."""
    add = AddMemoryUseCase(repo)
    add.execute(
        collection=collection,
        documents=list(docs.values()),
        ids=list(docs.keys()),
    )


# ---------------------------------------------------------------------------
# AddEdgeUseCase
# ---------------------------------------------------------------------------

def test_add_edge_happy_path(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"a": "pattern: always do X", "b": "anti-pattern: never do Y"})
    add_edge = AddEdgeUseCase(tmp_repo)
    add_edge.execute("col", "b", "a", "contradicts")

    edges = tmp_repo.get_edges("col", "b")
    assert len(edges) == 1
    assert edges[0].target_id == "a"
    assert edges[0].edge_type == "contradicts"


def test_add_edge_deduplication(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"a": "pattern text", "b": "anti text"})
    add_edge = AddEdgeUseCase(tmp_repo)
    add_edge.execute("col", "b", "a", "contradicts")
    add_edge.execute("col", "b", "a", "contradicts")  # duplicate

    edges = tmp_repo.get_edges("col", "b")
    assert len(edges) == 1


def test_add_edge_different_types_not_deduped(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"a": "target", "b": "source"})
    add_edge = AddEdgeUseCase(tmp_repo)
    add_edge.execute("col", "b", "a", "contradicts")
    add_edge.execute("col", "b", "a", "related")

    edges = tmp_repo.get_edges("col", "b")
    assert len(edges) == 2
    types = {e.edge_type for e in edges}
    assert types == {"contradicts", "related"}


def test_add_edge_confirms_stores_edge_without_flagging_target(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"earlier": "insight X", "later": "X held up again in session Y"})
    AddEdgeUseCase(tmp_repo).execute("col", "later", "earlier", "confirms")

    edges = tmp_repo.get_edges("col", "later")
    assert [(e.target_id, e.edge_type) for e in edges] == [("earlier", "confirms")]
    target = tmp_repo.get_by_ids("col", ["earlier"])[0]
    assert "superseded_by" not in target.metadata


def test_add_edge_confirms_rejects_self_edge(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"a": "insight"})
    with pytest.raises(ValueError, match="cannot confirm itself"):
        AddEdgeUseCase(tmp_repo).execute("col", "a", "a", "confirms")


def test_add_edge_raises_when_source_missing(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"a": "target"})
    add_edge = AddEdgeUseCase(tmp_repo)
    with pytest.raises(ValueError, match="not found"):
        add_edge.execute("col", "nonexistent", "a", "related")


def test_add_edge_raises_when_target_missing(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"b": "source"})
    add_edge = AddEdgeUseCase(tmp_repo)
    with pytest.raises(ValueError, match="not found"):
        add_edge.execute("col", "b", "nonexistent", "related")


def test_add_edge_derived_from_stores_edge_on_decision(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"learning": "Observed: X", "decision": "Decision: Y"})
    AddEdgeUseCase(tmp_repo).execute("col", "decision", "learning", "derived_from")

    edges = tmp_repo.get_edges("col", "decision")
    assert [(e.target_id, e.edge_type) for e in edges] == [("learning", "derived_from")]
    assert tmp_repo.get_edges("col", "learning") == []
    assert "superseded_by" not in tmp_repo.get_by_ids("col", ["learning"])[0].metadata


def test_add_edge_derived_from_rejects_self_link(tmp_repo, tmp_path):
    _seed(tmp_repo, "col", {"a": "entry"})
    with pytest.raises(ValueError, match="derived from itself"):
        AddEdgeUseCase(tmp_repo).execute("col", "a", "a", "derived_from")


# ---------------------------------------------------------------------------
# Cross-area edges (area-qualified targets, file records in resolver mode)
# ---------------------------------------------------------------------------

@pytest.fixture
def two_areas(tmp_path):
    """Areas `proj` (learning_src) and `records/workspace` (pattern_tgt), as area keys."""
    repo = FileMemoryRepository(area_records_dir)
    keys = {}
    for name, rel, entry_id, entry_type in (("proj", "proj", "learning_src", "learning"),
                                            ("ws", "records/workspace", "pattern_tgt", "pattern")):
        (tmp_path / rel / "docs" / "records").mkdir(parents=True)
        keys[name] = str((tmp_path / rel).resolve())
        repo.upsert(keys[name], [MemoryEntry(id=entry_id, text="x", metadata={"type": entry_type})])
    return repo, keys, tmp_path


def _uc(repo):
    return AddEdgeUseCase(repo, area_refs=AreaRefResolver())


def test_cross_area_edge_is_stored_on_the_source_only(two_areas):
    repo, keys, tmp_path = two_areas
    target_file = tmp_path / "records/workspace/docs/records/general/decisions/pattern_tgt.md"
    before = target_file.read_text()

    _uc(repo).execute(keys["proj"], "learning_src", "../records/workspace:pattern_tgt", "related")
    _uc(repo).execute(keys["proj"], "learning_src", "../records/workspace:pattern_tgt", "related")

    edges = repo.get_edges(keys["proj"], "learning_src")
    assert [(e.target_id, e.edge_type) for e in edges] == [("../records/workspace:pattern_tgt", "related")]
    assert target_file.read_text() == before
    assert repo.get_edges(keys["ws"], "pattern_tgt") == []


def test_cross_area_supersede_is_refused_before_anything_is_written(two_areas):
    repo, keys, tmp_path = two_areas
    files = {path: path.read_text() for path in tmp_path.rglob("*.md")}

    with pytest.raises(ValueError, match="across areas"):
        _uc(repo).execute(keys["proj"], "learning_src", "../records/workspace:pattern_tgt", "supersedes")
    assert {path: path.read_text() for path in tmp_path.rglob("*.md")} == files


@pytest.mark.parametrize("target", [
    "../records/workspace:missing", "../nowhere:pattern_tgt", "/etc:passwd", "~/x:y", "../../..:x", "..:*",
    "../records/workspace:a/b", "../records/workspace/../workspace:pattern_tgt", "other:pattern_tgt",
])
def test_cross_area_targets_must_resolve_to_an_existing_entry(two_areas, target):
    repo, keys, _ = two_areas

    with pytest.raises(ValueError):
        _uc(repo).execute(keys["proj"], "learning_src", target, "related")
    assert repo.get_edges(keys["proj"], "learning_src") == []


def test_cross_area_edge_needs_an_area_resolver_and_an_existing_source(two_areas):
    repo, keys, _ = two_areas

    with pytest.raises(ValueError, match="does not resolve"):
        AddEdgeUseCase(repo).execute(keys["proj"], "learning_src", "../records/workspace:pattern_tgt", "related")
    with pytest.raises(ValueError, match="not found"):
        _uc(repo).execute(keys["proj"], "missing", "../records/workspace:pattern_tgt", "related")
    with pytest.raises(ValueError, match="itself"):
        _uc(repo).execute(keys["proj"], "learning_src", ".:learning_src", "derived_from")


def test_missing_target_raises_target_not_found_missing_source_does_not(tmp_repo):
    _seed(tmp_repo, "col", {"a": "entry"})

    with pytest.raises(TargetNotFound, match="not found") as caught:
        AddEdgeUseCase(tmp_repo).execute("col", "a", "ghost", "related")
    assert caught.value.target == "ghost"
    with pytest.raises(ValueError, match="not found") as caught:
        AddEdgeUseCase(tmp_repo).execute("col", "ghost_src", "a", "related")
    assert not isinstance(caught.value, TargetNotFound)


def test_missing_cross_area_target_raises_target_not_found(two_areas):
    repo, keys, _ = two_areas
    with pytest.raises(TargetNotFound) as caught:
        _uc(repo).execute(keys["proj"], "learning_src", "../records/workspace:ghost", "related")
    assert caught.value.target == "../records/workspace:ghost"
