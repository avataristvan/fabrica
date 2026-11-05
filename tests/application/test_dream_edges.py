"""Dream edge actions: LINK, SUPERSEDE and the MERGE conflict guard.

The LINK parsing, edge index and merge-guard tests are ported from the review branch's LINK commit;
the SUPERSEDE, skip-reason, cross-collection and edge-type-derivation tests are new.
"""
from __future__ import annotations

import json
from typing import get_args
from unittest.mock import patch

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.dream_memory import (
    _ACTION_FORMAT,
    _LINK_EDGE_TYPES,
    DreamMemoryUseCase,
    _build_edge_index,
    _check_merge_conflicts,
)
from ai_mem.domain.memory import EdgeType, MemoryEntry


def _seed(repo, collection: str, docs: dict[str, str], metadatas: list[dict] | None = None) -> None:
    AddMemoryUseCase(repo).execute(
        collection=collection,
        documents=list(docs.values()),
        ids=list(docs.keys()),
        metadatas=metadatas or [{}] * len(docs),
    )


def _dream(repo, synthesis: str) -> str:
    # Plain ids never reach the resolver, so the in-memory repo can stand in for an area.
    from ai_mem.infrastructure.areas import AreaRefResolver
    with patch("ai_mem.application.dream_memory._call", return_value=synthesis):
        return DreamMemoryUseCase(repo, area_refs=AreaRefResolver()).execute("col", mode="single-haiku")


# ── edge types are derived, not hard-coded ───────────────────────────────────

class TestLinkEdgeTypes:
    def test_derived_from_edge_type_without_supersedes(self):
        assert set(_LINK_EDGE_TYPES) == set(get_args(EdgeType)) - {"supersedes", "derived_from"}

    def test_derived_from_is_manual_only(self):
        assert "derived_from" not in _LINK_EDGE_TYPES
        assert "derived_from" not in _ACTION_FORMAT

    def test_supersedes_is_not_a_link_type(self):
        assert "supersedes" not in _LINK_EDGE_TYPES

    def test_action_format_lists_every_link_type_and_supersede(self):
        for edge_type in _LINK_EDGE_TYPES:
            assert edge_type in _ACTION_FORMAT
        assert "SUPERSEDE <new-id> -> <old-id>" in _ACTION_FORMAT


# ── _build_edge_index ─────────────────────────────────────────────────────────

class TestBuildEdgeIndex:
    def _entry(self, id: str, edges: list[dict]) -> MemoryEntry:
        return MemoryEntry(id=id, text="t", metadata={"edges": json.dumps(edges), "_collection": "col"})

    def test_extracts_edges_from_metadata(self):
        entry = self._entry("a", [{"target_id": "b", "edge_type": "contradicts"}])
        assert _build_edge_index([entry]) == {("a", "b"): "contradicts"}

    def test_multiple_edges_on_one_entry(self):
        entry = self._entry("a", [
            {"target_id": "b", "edge_type": "contradicts"},
            {"target_id": "c", "edge_type": "fixes"},
        ])
        index = _build_edge_index([entry])
        assert index[("a", "b")] == "contradicts"
        assert index[("a", "c")] == "fixes"

    def test_empty_and_missing_edges_give_empty_index(self):
        assert _build_edge_index([self._entry("a", [])]) == {}
        assert _build_edge_index([MemoryEntry(id="a", text="t", metadata={"_collection": "col"})]) == {}

    def test_malformed_json_silently_skipped(self):
        entry = MemoryEntry(id="a", text="t", metadata={"edges": "not-json", "_collection": "col"})
        assert _build_edge_index([entry]) == {}

    def test_multiple_entries_merged(self):
        first = self._entry("a", [{"target_id": "b", "edge_type": "causes"}])
        second = self._entry("b", [{"target_id": "c", "edge_type": "related"}])
        assert _build_edge_index([first, second]) == {("a", "b"): "causes", ("b", "c"): "related"}

    def test_superseded_by_flag_yields_a_supersedes_pair(self):
        old = MemoryEntry(id="old", text="t", metadata={"superseded_by": "new", "_collection": "col"})
        assert _build_edge_index([old]) == {("new", "old"): "supersedes"}

    def test_cleared_superseded_by_flag_is_ignored(self):
        old = MemoryEntry(id="old", text="t", metadata={"superseded_by": "", "_collection": "col"})
        assert _build_edge_index([old]) == {}


# ── _check_merge_conflicts ────────────────────────────────────────────────────

class TestCheckMergeConflicts:
    def test_flags_contradicts_edge(self):
        warnings = _check_merge_conflicts("- MERGE a + b: combine", {("a", "b"): "contradicts"})
        assert len(warnings) == 1
        assert "contradicts" in warnings[0] and "a" in warnings[0] and "b" in warnings[0]

    def test_bidirectional_detection(self):
        assert len(_check_merge_conflicts("- MERGE a + b: combine", {("b", "a"): "contradicts"})) == 1

    def test_related_edge_does_not_block_merge(self):
        assert _check_merge_conflicts("- MERGE a + b: combine", {("a", "b"): "related"}) == []

    def test_no_merge_or_no_edge_returns_empty(self):
        assert _check_merge_conflicts("- DELETE a: stale", {("a", "b"): "contradicts"}) == []
        assert _check_merge_conflicts("- MERGE a + b: combine", {}) == []

    def test_multiple_merges_only_flags_conflicting(self):
        synthesis = "- MERGE a + b: combine\n- MERGE c + d: also combine"
        warnings = _check_merge_conflicts(synthesis, {("a", "b"): "contradicts"})
        assert len(warnings) == 1 and "a" in warnings[0] and "b" in warnings[0]

    def test_flags_merge_of_a_superseded_pair_in_either_order(self):
        for synthesis in ("- MERGE new + old: fold", "- MERGE old + new: fold"):
            warnings = _check_merge_conflicts(synthesis, {("new", "old"): "supersedes"})
            assert len(warnings) == 1
            assert "supersedes" in warnings[0] and "history" in warnings[0]


# ── execute(): merge guard ────────────────────────────────────────────────────

class TestDreamExecuteMergeConflict:
    def test_contradicts_conflict_flagged_in_report(self, tmp_repo):
        _seed(tmp_repo, "col",
              {"p1": "Rule: always validate\nWhen: input received\nWhy: safety",
               "ap1": "Tried: skip validation\nFailed because: injection\nInstead: validate"},
              [{"type": "pattern"}, {"type": "anti-pattern"}])
        AddEdgeUseCase(tmp_repo).execute("col", "ap1", "p1", "contradicts")

        report = _dream(tmp_repo, "- MERGE ap1 + p1: combine into unified guidance")

        assert "## ⚠ Merge Conflicts" in report and "contradicts" in report

    def test_bidirectional_edge_also_flagged(self, tmp_repo):
        _seed(tmp_repo, "col", {"p1": "pattern text", "ap1": "anti-pattern text"})
        AddEdgeUseCase(tmp_repo).execute("col", "p1", "ap1", "contradicts")
        assert "## ⚠ Merge Conflicts" in _dream(tmp_repo, "- MERGE ap1 + p1: combine")

    def test_merge_without_edge_not_flagged(self, tmp_repo):
        _seed(tmp_repo, "col", {"e1": "entry one text", "e2": "entry two text"})
        assert "## ⚠ Merge Conflicts" not in _dream(tmp_repo, "- MERGE e1 + e2: duplicate content")

    def test_merging_a_superseded_pair_is_flagged(self, tmp_repo):
        _seed(tmp_repo, "col", {"old": "the old decision", "new": "the new decision"})
        AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")

        report = _dream(tmp_repo, "- MERGE old + new: fold the old into the new")

        assert "## ⚠ Merge Conflicts" in report and "erase the history" in report


# ── area mode: qualified edges across areas (real FileMemoryRepository, fake claude runner) ──

import pytest

from ai_mem.application.dream_memory import _area_add_targets
from ai_mem.infrastructure.areas import AreaRefResolver, area_records_dir
from ai_mem.infrastructure.file_repository import FileMemoryRepository


def _area(root):
    (root / "docs" / "records").mkdir(parents=True)
    return str(root.resolve())


def _put(repo, key: str, entry_id: str, entry_type: str = "learning") -> None:
    AddMemoryUseCase(repo).execute(
        collection=key, documents=[f"Text of {entry_id}"], ids=[entry_id], metadatas=[{"type": entry_type}],
    )


@pytest.fixture
def two_areas(tmp_path):
    repo = FileMemoryRepository(area_records_dir)
    here = _area(tmp_path / "ws" / "here")
    other = _area(tmp_path / "ws" / "other")
    _put(repo, here, "learning_a")
    _put(repo, here, "learning_b")
    _put(repo, other, "learning_x")
    return repo, here, other, tmp_path


def _area_dream(repo, key, synthesis):
    with patch("ai_mem.application.dream_memory._call", return_value=synthesis):
        return DreamMemoryUseCase(repo, area_refs=AreaRefResolver()).execute(key, "single-haiku")


class TestAreaAddTargets:
    def test_other_area_is_a_propagation_candidate_own_area_is_not(self, two_areas):
        _, here, other, _ = two_areas
        text = "- ADD new_one [target=../other]: s\n- ADD mine [target=.]: s"
        accepted, rejected = _area_add_targets(text, here, AreaRefResolver())
        assert accepted == [("new_one", "../other", other)]
        assert rejected == []

    def test_targets_go_through_resolve_area_not_a_probe_ref(self, two_areas):
        _, here, other, _ = two_areas
        seen = []

        class OnlyAreas:
            def resolve(self, source, target_id):
                raise AssertionError("resolve() must not be used for ADD targets")

            def resolve_area(self, source, rel):
                seen.append((source, rel))
                return other if rel == "../other" else None

        accepted, rejected = _area_add_targets("- ADD a [target=../other]: s\n- ADD b [target=../x]: s", here, OnlyAreas())
        assert accepted == [("a", "../other", other)]
        assert rejected == [("b", "../x")]
        assert seen == [(here, "../other"), (here, "../x")]

    @pytest.mark.parametrize("target", ["/tmp", "~", "~/x", "../..", "../nope", "other", "../other/..", "../o*", "../other/../../etc"])
    def test_hostile_targets_are_rejected(self, two_areas, target):
        _, here, _, _ = two_areas
        accepted, rejected = _area_add_targets(f"- ADD x [target={target}]: s", here, AreaRefResolver())
        assert accepted == []
        assert rejected == [("x", target)]

    def test_report_lists_candidates_and_rejections_and_writes_nothing(self, two_areas):
        repo, here, other, tmp = two_areas
        before = {p: p.read_bytes() for p in tmp.rglob("*") if p.is_file()}
        report = _area_dream(repo, here, (
            "- ADD n1 [target=../other]: s\n- ADD n2 [target=/etc]: s\n"
            "- LINK learning_a -> learning_b [type=related]: r\n"
            "- SUPERSEDE learning_b -> learning_a: r\n- DELETE learning_b: stale\n"
        ))
        assert "## Propagation Candidates" in report and "`n1`" in report
        assert "## Rejected ADD Targets" in report and "`n2`" in report
        assert {p: p.read_bytes() for p in tmp.rglob("*") if p.is_file()} == before  # proposals are never applied
