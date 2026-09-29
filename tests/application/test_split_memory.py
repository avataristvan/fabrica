"""SplitMemoryUseCase: Claude-based entry splitting."""
from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.detect_split_hints import SPLIT_MIN_TEXT_CHARS
from ai_mem.application.split_memory import SplitMemoryUseCase, _parse_json
from ai_mem.domain.memory import MemoryEdge, MemoryEntry


# ---------------------------------------------------------------------------
# _parse_json unit tests
# ---------------------------------------------------------------------------

def test_parse_json_clean_array():
    data = [{"id": "x_1", "text": "part one"}, {"id": "x_2", "text": "part two"}]
    assert _parse_json(json.dumps(data)) == data


def test_parse_json_extracts_array_from_prose():
    raw = 'Sure, here you go:\n[{"id": "x_1", "text": "a"}, {"id": "x_2", "text": "b"}]\nDone.'
    result = _parse_json(raw)
    assert len(result) == 2
    assert result[0]["id"] == "x_1"


def test_parse_json_raises_on_non_array():
    with pytest.raises((json.JSONDecodeError, ValueError)):
        _parse_json('{"id": "x"}')


def test_parse_json_raises_on_missing_id_key():
    with pytest.raises(ValueError):
        _parse_json('[{"text": "no id here"}]')


# ---------------------------------------------------------------------------
# SplitMemoryUseCase integration tests (subprocess mocked)
# ---------------------------------------------------------------------------

_LONG_TEXT = "a" * SPLIT_MIN_TEXT_CHARS

_SPLIT_RESPONSE = json.dumps([
    {"id": "entry_1", "text": "first sub-topic"},
    {"id": "entry_2", "text": "second sub-topic"},
])


def _make_uc(tmp_repo) -> SplitMemoryUseCase:
    return SplitMemoryUseCase(tmp_repo, AddMemoryUseCase(tmp_repo), AddEdgeUseCase(tmp_repo))


def _add_entry(tmp_repo, entry_id: str, text: str) -> None:
    tmp_repo.upsert("col", [MemoryEntry(
        id=entry_id,
        text=text,
        metadata={"created_at": time.time()},
    )])


@patch("subprocess.run")
def test_split_entry_by_id_deletes_original_and_adds_sub_entries(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=_SPLIT_RESPONSE, returncode=0)
    _add_entry(tmp_repo, "entry", _LONG_TEXT)

    result = _make_uc(tmp_repo).execute("col", entry_id="entry")

    assert len(result) == 1
    r = result[0]
    assert r.original_id == "entry"
    assert r.new_ids == ["entry_1", "entry_2"]
    assert r.skipped is False

    remaining = tmp_repo.get_by_ids("col", ["entry"])
    assert remaining == []  # original deleted

    new_entries = tmp_repo.get_by_ids("col", ["entry_1", "entry_2"])
    assert len(new_entries) == 2


@patch("subprocess.run")
def test_split_all_hints_selects_long_entries_only(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=_SPLIT_RESPONSE, returncode=0)
    _add_entry(tmp_repo, "hinted", _LONG_TEXT)
    _add_entry(tmp_repo, "not_hinted", "a" * (SPLIT_MIN_TEXT_CHARS - 1))

    results = _make_uc(tmp_repo).execute("col")

    assert len(results) == 1
    assert results[0].original_id == "hinted"


@patch("subprocess.run")
def test_split_all_hints_skips_short_text(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=_SPLIT_RESPONSE, returncode=0)
    short_text = "a" * (SPLIT_MIN_TEXT_CHARS - 1)
    _add_entry(tmp_repo, "short_entry", short_text)

    results = _make_uc(tmp_repo).execute("col")

    assert results == []


@patch("subprocess.run")
def test_split_returns_skipped_on_json_parse_error(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout="not valid json", returncode=0)
    _add_entry(tmp_repo, "entry", _LONG_TEXT)

    result = _make_uc(tmp_repo).execute("col", entry_id="entry")

    assert result[0].skipped is True
    assert "JSON parse error" in result[0].skip_reason

    still_there = tmp_repo.get_by_ids("col", ["entry"])
    assert len(still_there) == 1  # original preserved on failure


@patch("subprocess.run")
def test_split_returns_skipped_on_claude_cli_error(mock_run, tmp_repo):
    import subprocess as sp
    mock_run.side_effect = sp.CalledProcessError(1, "claude", stderr="error")
    _add_entry(tmp_repo, "entry", _LONG_TEXT)

    result = _make_uc(tmp_repo).execute("col", entry_id="entry")

    assert result[0].skipped is True
    assert "claude CLI error" in result[0].skip_reason


def test_split_empty_collection_returns_empty(tmp_repo):
    results = _make_uc(tmp_repo).execute("empty_col")
    assert results == []


# ---------------------------------------------------------------------------
# learning + decision mode
# ---------------------------------------------------------------------------

_LD_RESPONSE = json.dumps([
    {"kind": "learning", "id": "fix_x_learning", "text": "Observed: a. Cause: b. Evidence: c."},
    {"kind": "decision", "id": "fix_x", "type": "pattern", "text": "Decision: d. Why: b. Scope: s."},
])


def _add_mixed(tmp_repo, meta: dict | None = None) -> None:
    tmp_repo.upsert("col", [MemoryEntry(
        id="fix_x",
        text="old mixed text",
        metadata={"created_at": 111.0, "type": "domain", "area": "workflow", "boost_count": 3, "cue": "why", **(meta or {})},
    )])


@patch("subprocess.run")
def test_learning_decision_keeps_original_as_decision(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=_LD_RESPONSE, returncode=0)
    _add_mixed(tmp_repo)
    tmp_repo.add_edge("col", "fix_x", MemoryEdge(target_id="other", edge_type="related"))

    result = _make_uc(tmp_repo).execute("col", entry_id="fix_x")[0]

    assert result.skipped is False
    assert result.new_ids == ["fix_x_learning"]
    decision = tmp_repo.get_by_ids("col", ["fix_x"])[0]
    assert decision.text.startswith("Decision:")
    assert decision.metadata["type"] == "domain"  # existing decision type wins over Claude's
    assert decision.metadata["created_at"] == 111.0
    assert decision.metadata["boost_count"] == 3
    assert decision.metadata["cue"] == "why"
    edges = {(e.target_id, e.edge_type) for e in tmp_repo.get_edges("col", "fix_x")}
    assert edges == {("other", "related"), ("fix_x_learning", "derived_from")}
    learning = tmp_repo.get_by_ids("col", ["fix_x_learning"])[0]
    assert learning.metadata["type"] == "learning"
    assert learning.metadata["area"] == "workflow"
    assert learning.text.startswith("Observed:")


@patch("subprocess.run")
def test_learning_decision_uses_claude_type_when_original_not_a_decision(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=_LD_RESPONSE, returncode=0)
    _add_mixed(tmp_repo, {"type": "fix"})

    _make_uc(tmp_repo).execute("col", entry_id="fix_x")

    assert tmp_repo.get_by_ids("col", ["fix_x"])[0].metadata["type"] == "pattern"


@patch("subprocess.run")
def test_learning_decision_skips_without_exactly_one_decision(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=json.dumps([
        {"kind": "learning", "id": "fix_x_learning", "text": "Observed: a."},
        {"kind": "topic", "id": "fix_x_1", "text": "t"},
    ]), returncode=0)
    _add_mixed(tmp_repo)

    result = _make_uc(tmp_repo).execute("col", entry_id="fix_x")[0]

    assert result.skipped is True
    assert tmp_repo.get_by_ids("col", ["fix_x"])[0].text == "old mixed text"
    assert tmp_repo.get_by_ids("col", ["fix_x_learning"]) == []


@patch("subprocess.run")
def test_learning_decision_refuses_to_overwrite_existing_learning(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=_LD_RESPONSE, returncode=0)
    _add_mixed(tmp_repo)
    _add_entry(tmp_repo, "fix_x_learning", "precious")

    result = _make_uc(tmp_repo).execute("col", entry_id="fix_x")[0]

    assert result.skipped is True
    assert tmp_repo.get_by_ids("col", ["fix_x_learning"])[0].text == "precious"
    assert tmp_repo.get_by_ids("col", ["fix_x"])[0].text == "old mixed text"


@patch("subprocess.run")
def test_learning_decision_rolls_back_on_failure_and_never_deletes_original(mock_run, tmp_repo):
    mock_run.return_value = MagicMock(stdout=_LD_RESPONSE, returncode=0)
    _add_mixed(tmp_repo)
    edge_uc = MagicMock()
    edge_uc.execute.side_effect = ValueError("boom")
    uc = SplitMemoryUseCase(tmp_repo, AddMemoryUseCase(tmp_repo), edge_uc)

    result = uc.execute("col", entry_id="fix_x")[0]

    assert result.skipped is True
    assert "rolled back" in result.skip_reason
    restored = tmp_repo.get_by_ids("col", ["fix_x"])[0]
    assert restored.text == "old mixed text"
    assert restored.metadata["boost_count"] == 3
    assert tmp_repo.get_by_ids("col", ["fix_x_learning"]) == []
