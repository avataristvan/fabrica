"""ExperienceIndexUseCase and the cue on mem_boost: membership by cue, live-only, bounded."""
from __future__ import annotations

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.boost_confidence import BoostConfidenceUseCase
from ai_mem.application.experience_index import MAX_CUE_CHARS, ExperienceIndexUseCase, normalize_cue
from ai_mem.application.get_memory import GetMemoryUseCase


def _add(repo, col, id_, text="Rule text", **meta):
    AddMemoryUseCase(repo).execute(col, [text], [id_], metadatas=[meta] if meta else None)


def test_entries_without_cue_are_not_listed(tmp_repo):
    _add(tmp_repo, "col", "a")
    assert ExperienceIndexUseCase(tmp_repo).execute(["col"]) == ""


def test_line_names_situation_id_and_title(tmp_repo):
    _add(tmp_repo, "col", "a", text="Do not merge review branches\nlonger body", cue="before merging a foreign branch")
    out = ExperienceIndexUseCase(tmp_repo).execute(["col"])
    assert out == "- before merging a foreign branch -> a: Do not merge review branches"


def test_membership_ignores_confidence_and_access_count(tmp_repo):
    """The cue is the judgment; low confidence and zero access do not keep an entry out."""
    _add(tmp_repo, "col", "a", cue="c", confidence=0.1)
    assert "-> a:" in ExperienceIndexUseCase(tmp_repo).execute(["col"])


def test_superseded_entry_drops_out_and_successor_can_take_over(tmp_repo):
    _add(tmp_repo, "col", "old", cue="situation")
    _add(tmp_repo, "col", "new", cue="situation")
    AddEdgeUseCase(tmp_repo).execute("col", "new", "old", "supersedes")
    out = ExperienceIndexUseCase(tmp_repo).execute(["col"])
    assert "-> new:" in out
    assert "-> old:" not in out


def test_expired_entry_is_not_listed(tmp_repo):
    _add(tmp_repo, "col", "a", cue="c", expires_at=1.0)
    assert ExperienceIndexUseCase(tmp_repo).execute(["col"]) == ""


def test_other_collection_is_tagged_and_primary_is_not(tmp_repo):
    _add(tmp_repo, "repo.x", "a", cue="repo situation")
    _add(tmp_repo, "global", "b", cue="global situation")
    out = ExperienceIndexUseCase(tmp_repo).execute(["repo.x", "global"])
    assert "-> a:" in out and "[repo.x]" not in out
    assert "-> b [global]:" in out


def test_missing_collection_is_skipped(tmp_repo):
    _add(tmp_repo, "col", "a", cue="c")

    class Flaky:
        def get_all(self, collection):
            if collection == "gone":
                raise RuntimeError("no such collection")
            return tmp_repo.get_all(collection)

    assert "-> a [col]:" in ExperienceIndexUseCase(Flaky()).execute(["gone", "col"])


def test_cap_keeps_most_boosted_then_newest_and_reports_overflow(tmp_repo):
    for idx in range(5):
        _add(tmp_repo, "col", f"e{idx}", cue=f"situation {idx}", boost_count=1 if idx == 0 else 0)
    out = ExperienceIndexUseCase(tmp_repo).execute(["col"], max_lines=3)
    lines = out.splitlines()
    assert len(lines) == 4
    assert "-> e0:" in lines[0]
    assert "-> e4:" in lines[1]  # newest of the unboosted ones comes next
    assert lines[-1] == "(+2 more cues; mem_query for anything not listed)"


def test_multiline_cue_is_flattened(tmp_repo):
    _add(tmp_repo, "col", "a", cue="two\nlines   here")
    assert "- two lines here -> a:" in ExperienceIndexUseCase(tmp_repo).execute(["col"])


# --- cue via mem_boost -------------------------------------------------------

def test_boost_with_cue_sets_cue_and_boosts(tmp_repo):
    _add(tmp_repo, "col", "a")
    BoostConfidenceUseCase(tmp_repo).execute("col", ["a"], 0.1, cue="  when   X happens ")
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["cue"] == "when X happens"
    assert meta["boost_count"] == 1


def test_delta_zero_records_cue_without_boost(tmp_repo):
    _add(tmp_repo, "col", "a")
    BoostConfidenceUseCase(tmp_repo).execute("col", ["a"], 0, cue="when X")
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["cue"] == "when X"
    assert "boost_count" not in meta
    assert meta["confidence"] == 0.7


def test_empty_cue_clears_it(tmp_repo):
    _add(tmp_repo, "col", "a", cue="when X")
    BoostConfidenceUseCase(tmp_repo).execute("col", ["a"], 0, cue="")
    assert not GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata.get("cue")
    assert ExperienceIndexUseCase(tmp_repo).execute(["col"]) == ""


def test_boost_without_cue_leaves_cue_alone(tmp_repo):
    _add(tmp_repo, "col", "a", cue="when X")
    BoostConfidenceUseCase(tmp_repo).execute("col", ["a"], 0.1)
    assert GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata["cue"] == "when X"


def test_too_long_cue_is_rejected_before_any_write(tmp_repo):
    _add(tmp_repo, "col", "a")
    with pytest.raises(ValueError, match="max"):
        BoostConfidenceUseCase(tmp_repo).execute("col", ["a"], 0.1, cue="x" * (MAX_CUE_CHARS + 1))
    meta = GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
    assert meta["confidence"] == 0.7 and not meta.get("cue")


def test_normalize_cue_boundary():
    assert normalize_cue("x" * MAX_CUE_CHARS) == "x" * MAX_CUE_CHARS
    assert normalize_cue("   ") == ""


def test_non_positive_max_lines_yields_no_block(tmp_repo):
    _add(tmp_repo, "col", "a", cue="c")
    assert ExperienceIndexUseCase(tmp_repo).execute(["col"], max_lines=0) == ""
    assert ExperienceIndexUseCase(tmp_repo).execute(["col"], max_lines=-1) == ""


def test_delta_zero_does_not_create_confidence(tmp_repo):
    """An entry written without a confidence key must not gain one (default 1.0) from a cue-only call."""
    from ai_mem.domain.memory import MemoryEntry
    tmp_repo.upsert("col", [MemoryEntry(id="a", text="x", metadata={"created_at": 1.0})])
    BoostConfidenceUseCase(tmp_repo).execute("col", ["a"], 0, cue="when X")
    assert "confidence" not in GetMemoryUseCase(tmp_repo).execute("col", ["a"])[0].metadata
