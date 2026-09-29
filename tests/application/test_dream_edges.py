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
    _parse_link_proposals,
    _parse_supersede_proposals,
    _shared_collection,
)
from ai_mem.application.get_edges import GetEdgesUseCase
from ai_mem.domain.memory import EdgeType, MemoryEntry


def _seed(repo, collection: str, docs: dict[str, str], metadatas: list[dict] | None = None) -> None:
    AddMemoryUseCase(repo).execute(
        collection=collection,
        documents=list(docs.values()),
        ids=list(docs.keys()),
        metadatas=metadatas or [{}] * len(docs),
    )


def _dream(repo, synthesis: str, **flags) -> str:
    with patch("ai_mem.application.dream_memory._call", return_value=synthesis):
        return DreamMemoryUseCase(repo).execute("col", mode="single-haiku", **flags)


def _meta(repo, collection: str, entry_id: str) -> dict:
    return repo.get_by_ids(collection, [entry_id])[0].metadata


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


# ── parsing ───────────────────────────────────────────────────────────────────

class TestParseLinkProposals:
    def test_bullet_styles(self):
        assert _parse_link_proposals("- LINK src -> tgt [type=contradicts]: r") == [("src", "tgt", "contradicts")]
        assert _parse_link_proposals("* LINK src -> tgt [type=fixes]: r") == [("src", "tgt", "fixes")]
        assert _parse_link_proposals("• LINK src -> tgt [type=related]: r") == [("src", "tgt", "related")]

    def test_case_insensitive_and_whitespace_in_type(self):
        assert _parse_link_proposals("- link src -> tgt [type=causes]: r") == [("src", "tgt", "causes")]
        assert _parse_link_proposals("- LINK a -> b [type=  related  ]: r") == [("a", "b", "related")]

    def test_multiple_links(self):
        synthesis = "- LINK a -> b [type=contradicts]: x\n- LINK c -> d [type=fixes]: y\n"
        assert _parse_link_proposals(synthesis) == [("a", "b", "contradicts"), ("c", "d", "fixes")]

    def test_missing_type_not_matched_and_empty_synthesis(self):
        assert _parse_link_proposals("- LINK a -> b: no type here") == []
        assert _parse_link_proposals("") == []


class TestParseSupersedeProposals:
    def test_parses_bullet_styles_and_case(self):
        assert _parse_supersede_proposals("- SUPERSEDE new -> old: reason") == [("new", "old")]
        assert _parse_supersede_proposals("* supersede n -> o: reason") == [("n", "o")]
        assert _parse_supersede_proposals("• SUPERSEDE n -> o: reason") == [("n", "o")]

    def test_multiple_and_none(self):
        synthesis = "- SUPERSEDE a -> b: x\n- SUPERSEDE c -> d: y"
        assert _parse_supersede_proposals(synthesis) == [("a", "b"), ("c", "d")]
        assert _parse_supersede_proposals("- DELETE a: stale") == []

    def test_link_lines_are_not_supersede_lines(self):
        assert _parse_supersede_proposals("- LINK a -> b [type=related]: r") == []


class TestSharedCollection:
    def test_same_collection(self):
        assert _shared_collection({"a": {"col"}, "b": {"col"}}, "a", "b") == ("col", "")

    def test_unknown_ids(self):
        assert _shared_collection({"b": {"col"}}, "a", "b")[1] == "unknown id 'a'"
        assert _shared_collection({"a": {"col"}}, "a", "b")[1] == "unknown id 'b'"

    def test_different_collections(self):
        collection, reason = _shared_collection({"a": {"one"}, "b": {"two"}}, "a", "b")
        assert collection is None and "different collections" in reason

    def test_ambiguous_when_both_exist_in_several(self):
        collection, reason = _shared_collection({"a": {"one", "two"}, "b": {"one", "two"}}, "a", "b")
        assert collection is None and "ambiguous" in reason


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


# ── execute(): auto_link ──────────────────────────────────────────────────────

class TestDreamExecuteAutoLink:
    def test_creates_edge_and_reports_it(self, tmp_repo):
        _seed(tmp_repo, "col", {"e1": "pattern text here", "e2": "anti-pattern text here"})

        report = _dream(tmp_repo, "- LINK e1 -> e2 [type=related]: they are connected", auto_link=True)

        assert "Auto-Applied Links" in report and "Applied `e1 -> e2` [related]" in report
        assert any(e.target_id == "e2" and e.edge_type == "related" for e in GetEdgesUseCase(tmp_repo).execute("col", "e1"))

    def test_not_applied_when_flag_false(self, tmp_repo):
        _seed(tmp_repo, "col", {"e1": "text", "e2": "text"})

        report = _dream(tmp_repo, "- LINK e1 -> e2 [type=related]: connected", auto_link=False)

        assert "Auto-Applied Links" not in report
        assert GetEdgesUseCase(tmp_repo).execute("col", "e1") == []

    def test_unknown_source_is_reported_not_silently_dropped(self, tmp_repo):
        _seed(tmp_repo, "col", {"e2": "target text"})

        report = _dream(tmp_repo, "- LINK ghost -> e2 [type=related]: ghost does not exist", auto_link=True)

        assert "### Skipped Links" in report and "unknown id 'ghost'" in report

    def test_invalid_edge_type_is_reported_with_the_valid_ones(self, tmp_repo):
        _seed(tmp_repo, "col", {"e1": "text", "e2": "text"})

        report = _dream(tmp_repo, "- LINK e1 -> e2 [type=invalid_type]: wrong", auto_link=True)

        assert GetEdgesUseCase(tmp_repo).execute("col", "e1") == []
        assert "invalid edge type" in report and "contradicts, fixes, causes, related" in report

    def test_supersedes_is_not_accepted_as_a_link_type(self, tmp_repo):
        _seed(tmp_repo, "col", {"e1": "text", "e2": "text"})

        report = _dream(tmp_repo, "- LINK e1 -> e2 [type=supersedes]: overtaken", auto_link=True)

        assert "invalid edge type" in report
        assert not _meta(tmp_repo, "col", "e2").get("superseded_by")

    def test_link_across_collections_is_skipped_with_reason(self, tmp_repo):
        _seed(tmp_repo, "col", {"e1": "text one"})
        _seed(tmp_repo, "other", {"e2": "text two"})
        with patch("ai_mem.application.dream_memory._call", return_value="- LINK e1 -> e2 [type=related]: x"):
            report = DreamMemoryUseCase(tmp_repo).execute(None, mode="single-haiku", auto_link=True)

        assert "different collections" in report
        assert GetEdgesUseCase(tmp_repo).execute("col", "e1") == []

    def test_reports_when_no_link_actions_were_proposed(self, tmp_repo):
        _seed(tmp_repo, "col", {"e1": "text"})
        assert "None (no LINK actions found)" in _dream(tmp_repo, "- DELETE e1: stale", auto_link=True)


# ── execute(): auto_supersede ─────────────────────────────────────────────────

class TestDreamExecuteAutoSupersede:
    def test_flags_old_entry_and_writes_the_edge(self, tmp_repo):
        _seed(tmp_repo, "col", {"old": "the old decision", "new": "the new decision"})

        report = _dream(tmp_repo, "- SUPERSEDE new -> old: the decision was reversed", auto_supersede=True)

        assert "Auto-Applied Supersessions" in report and "Applied `new -> old` in `col`" in report
        assert _meta(tmp_repo, "col", "old")["superseded_by"] == "new"
        assert [(e.target_id, e.edge_type) for e in GetEdgesUseCase(tmp_repo).execute("col", "new")] == [("old", "supersedes")]
        assert tmp_repo.get_by_ids("col", ["old"])[0].text == "the old decision"  # kept, not deleted

    def test_not_applied_when_flag_false(self, tmp_repo):
        _seed(tmp_repo, "col", {"old": "old", "new": "new"})

        report = _dream(tmp_repo, "- SUPERSEDE new -> old: reversed", auto_supersede=False)

        assert "Supersessions" not in report
        assert not _meta(tmp_repo, "col", "old").get("superseded_by")

    def test_does_not_apply_link_actions_and_vice_versa(self, tmp_repo):
        _seed(tmp_repo, "col", {"old": "old", "new": "new"})

        _dream(tmp_repo, "- SUPERSEDE new -> old: reversed", auto_link=True)

        assert not _meta(tmp_repo, "col", "old").get("superseded_by")

    def test_already_superseded_source_is_skipped_with_the_use_case_reason(self, tmp_repo):
        _seed(tmp_repo, "col", {"a": "a", "b": "b", "c": "c"})
        AddEdgeUseCase(tmp_repo).execute("col", "b", "a", "supersedes")  # a is superseded by b

        report = _dream(tmp_repo, "- SUPERSEDE a -> c: a is newer", auto_supersede=True)

        assert "### Skipped Supersessions" in report and "is itself superseded by 'b'" in report
        assert not _meta(tmp_repo, "col", "c").get("superseded_by")

    def test_self_supersede_and_unknown_id_are_skipped(self, tmp_repo):
        _seed(tmp_repo, "col", {"a": "a"})

        report = _dream(tmp_repo, "- SUPERSEDE a -> a: nonsense\n- SUPERSEDE ghost -> a: nothing", auto_supersede=True)

        assert "cannot supersede itself" in report and "unknown id 'ghost'" in report

    def test_supersede_across_collections_is_skipped(self, tmp_repo):
        _seed(tmp_repo, "col", {"new": "new"})
        _seed(tmp_repo, "other", {"old": "old"})
        with patch("ai_mem.application.dream_memory._call", return_value="- SUPERSEDE new -> old: reversed"):
            report = DreamMemoryUseCase(tmp_repo).execute(None, mode="single-haiku", auto_supersede=True)

        assert "different collections" in report
        assert not _meta(tmp_repo, "other", "old").get("superseded_by")

    def test_mixed_proposals_apply_the_valid_ones(self, tmp_repo):
        _seed(tmp_repo, "col", {"old": "old", "new": "new"})

        report = _dream(tmp_repo, "- SUPERSEDE ghost -> old: x\n- SUPERSEDE new -> old: reversed", auto_supersede=True)

        assert _meta(tmp_repo, "col", "old")["superseded_by"] == "new"
        assert "Applied `new -> old`" in report and "unknown id 'ghost'" in report
