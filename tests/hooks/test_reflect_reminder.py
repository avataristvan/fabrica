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


# --- incremental scan: only what was appended since the last Stop is read ---


def _append(path: Path, *messages: dict) -> None:
    with open(path, "a") as handle:
        handle.write("".join(json.dumps({"message": m}) + "\n" for m in messages))


def _saved(state: Path, session_id: str = "sess-1") -> dict:
    return json.loads((state / "reflect_scan" / f"{session_id}.json").read_text())


def test_offset_advances_to_the_end_of_complete_lines(tmp_path: Path, state: Path) -> None:
    path = _transcript(tmp_path, _tool_use("Read"))
    assert reflect_reminder.handle(_event(path)) is None
    assert _saved(state)["offset"] == path.stat().st_size


def test_edit_appended_after_an_earlier_stop_reminds(tmp_path: Path) -> None:
    path = _transcript(tmp_path, _tool_use("Read"))
    assert reflect_reminder.handle(_event(path)) is None
    _append(path, _tool_use("Edit"))
    assert reflect_reminder.handle(_event(path)) is not None


def test_already_scanned_lines_are_not_read_again(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _transcript(tmp_path, *[_tool_use("Read")] * 5)
    reflect_reminder.handle(_event(path))
    seen: list[str] = []
    real = reflect_reminder._scan_line
    monkeypatch.setattr(reflect_reminder, "_scan_line", lambda line: seen.append(line) or real(line))
    _append(path, _tool_use("Edit"))
    assert reflect_reminder.handle(_event(path)) is not None
    assert len(seen) == 1 and '"Edit"' in seen[0]


def test_reflect_after_an_earlier_scan_suppresses_for_the_rest_of_the_session(tmp_path: Path) -> None:
    path = _transcript(tmp_path, _tool_use("Read"))
    reflect_reminder.handle(_event(path))
    _append(path, _tool_use("Edit"), {"role": "user", "content": "/reflect"})
    assert reflect_reminder.handle(_event(path)) is None
    _append(path, _tool_use("Write"))
    assert reflect_reminder.handle(_event(path)) is None


def test_reflect_seen_in_an_earlier_scan_still_suppresses_a_later_edit(tmp_path: Path) -> None:
    path = _transcript(tmp_path, {"role": "user", "content": "<command-name>/reflect</command-name>"})
    assert reflect_reminder.handle(_event(path)) is None
    _append(path, _tool_use("Edit"))
    assert reflect_reminder.handle(_event(path)) is None


def test_trailing_partial_line_is_read_again_when_complete(tmp_path: Path, state: Path) -> None:
    path = _transcript(tmp_path, _tool_use("Read"))
    complete = path.stat().st_size
    line = json.dumps({"message": _tool_use("Edit")})
    with open(path, "a") as handle:
        handle.write(line[:20])
    assert reflect_reminder.handle(_event(path)) is None
    assert _saved(state)["offset"] == complete
    with open(path, "a") as handle:
        handle.write(line[20:] + "\n")
    assert reflect_reminder.handle(_event(path)) is not None


def test_truncated_transcript_is_rescanned_from_the_start(tmp_path: Path, state: Path) -> None:
    path = _transcript(tmp_path, *[_tool_use("Read")] * 10)
    reflect_reminder.handle(_event(path))
    path.write_text(json.dumps({"message": _tool_use("Edit")}) + "\n")  # same inode, shorter than the offset
    assert path.stat().st_size < _saved(state)["offset"]
    assert reflect_reminder.handle(_event(path)) is not None


def test_replaced_transcript_is_rescanned_from_the_start(tmp_path: Path) -> None:
    path = _transcript(tmp_path, _tool_use("Read"))
    reflect_reminder.handle(_event(path))
    os.link(path, tmp_path / "keep.jsonl")  # keep the old inode alive so the replacement cannot reuse it
    replacement = tmp_path / "new.jsonl"
    replacement.write_text(json.dumps({"message": _tool_use("Edit")}) + "\n" + json.dumps({"message": _tool_use("Read")}) + "\n")
    os.replace(replacement, path)
    assert reflect_reminder.handle(_event(path)) is not None


@pytest.mark.parametrize("content", [
    "not json", "[]", '{"offset": "x"}',
    '{"offset": -1, "edited": false, "reflected": false, "file": [0, 0]}',
    '{"offset": 0, "edited": 1, "reflected": false, "file": [0, 0]}',
])
def test_malformed_state_is_treated_as_absent(tmp_path: Path, state: Path, content: str) -> None:
    (state / "reflect_scan").mkdir(parents=True)
    (state / "reflect_scan" / "sess-1.json").write_text(content)
    assert reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use("Edit")))) is not None


def test_unwritable_state_dir_still_reminds(tmp_path: Path, state: Path) -> None:
    state.mkdir(parents=True)
    (state / "reflect_scan").write_text("a file, not a directory")
    assert reflect_reminder.handle(_event(_transcript(tmp_path, _tool_use("Edit")))) is not None
