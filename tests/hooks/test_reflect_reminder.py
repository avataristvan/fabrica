"""reflect_reminder: Stop hook, D13 -- one user-visible reminder per session, never a block."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from ai_mem.hooks import reflect_reminder


@pytest.fixture(autouse=True)
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("AI_MEM_PATH", str(tmp_path / "state"))
    return tmp_path / "state"


def _transcript(tmp_path: Path, *messages: dict) -> Path:
    path = tmp_path / "t.jsonl"
    path.write_text("\n".join(json.dumps({"message": m}) for m in messages) + "\n")
    return path


def _tool_use(name: str, **tool_input) -> dict:
    return {"role": "assistant", "content": [{"type": "tool_use", "name": name, "input": tool_input}]}


def _event(path: Path, session_id: str = "sess-1") -> dict:
    return {"session_id": session_id, "transcript_path": str(path)}


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit"])
def test_reminds_after_an_edit(tmp_path: Path, tool: str) -> None:
    out = reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use(tool))))
    assert set(out) == {"systemMessage"} and "/reflect" in out["systemMessage"]


def test_reminds_only_once_per_session(tmp_path: Path) -> None:
    event = _event(_transcript(tmp_path, _tool_use("Edit")))
    assert reflect_reminder.handle(event) is not None
    assert reflect_reminder.handle(event) is None
    assert reflect_reminder.handle(_event(Path(event["transcript_path"]), "other-session")) is not None


def test_no_reminder_without_edits(tmp_path: Path) -> None:
    assert reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use("Read")))) is None


def test_no_marker_without_edits_so_a_later_edit_still_reminds(tmp_path: Path, state: Path) -> None:
    reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use("Read"))))
    assert not (state / "reminded").exists() or not list((state / "reminded").iterdir())


def test_no_reminder_after_a_reflect_command(tmp_path: Path) -> None:
    reflected = {"role": "user", "content": "<command-name>/reflect</command-name>"}
    assert reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use("Edit"), reflected))) is None


def test_no_reminder_after_reflect_via_skill_tool(tmp_path: Path) -> None:
    assert reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use("Write"), _tool_use("Skill", skill="reflect")))) is None


def test_stop_hook_active_is_ignored(tmp_path: Path) -> None:
    event = _event(_transcript(tmp_path, _tool_use("Edit")))
    event["stop_hook_active"] = True
    assert reflect_reminder.handle(event) is None


@pytest.mark.parametrize("session_id", ["../x", "a/b", "", "x" * 300, None, 5])
def test_unsafe_session_ids_never_reach_a_path(tmp_path: Path, state: Path, session_id) -> None:
    assert reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use("Edit")), session_id)) is None
    assert not state.exists()


def test_transcript_that_is_not_a_regular_file_is_not_opened(tmp_path: Path) -> None:
    fifo = tmp_path / "fifo"
    os.mkfifo(fifo)
    assert reflect_reminder.handle(_event(fifo)) is None
    assert reflect_reminder.handle(_event(Path("/dev/zero"))) is None
    assert reflect_reminder.handle(_event(tmp_path / "missing.jsonl")) is None


def test_garbage_lines_in_the_transcript_are_skipped(tmp_path: Path) -> None:
    path = tmp_path / "t.jsonl"
    path.write_text("garbage\n[1]\n" + json.dumps({"message": _tool_use("Edit")}) + "\n")
    assert reflect_reminder.handle(_event(path)) is not None
