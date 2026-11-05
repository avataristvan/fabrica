"""focus_gate: changing FOCUS.md needs a reflect in this session."""
from __future__ import annotations

from pathlib import Path

import pytest

from ai_mem.hooks import focus_gate


@pytest.fixture(autouse=True)
def _state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_MEM_PATH", str(tmp_path / "state"))


def _focus(tmp_path: Path) -> Path:
    records = tmp_path / "area" / "docs" / "records"
    records.mkdir(parents=True)
    return records / "FOCUS.md"


def _write(path: Path, session: str = "s1", tool: str = "Write") -> dict | None:
    return focus_gate.handle({"hook_event_name": "PreToolUse", "session_id": session, "tool_name": tool,
                              "tool_input": {"file_path": str(path)}})


def _denied(out: dict | None) -> bool:
    return bool(out) and out["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_focus_write_without_reflect_is_denied_with_a_reason(tmp_path: Path) -> None:
    out = _write(_focus(tmp_path))
    assert _denied(out) and "/fabrica:reflect" in out["hookSpecificOutput"]["permissionDecisionReason"]


def test_typed_reflect_opens_the_gate(tmp_path: Path) -> None:
    focus = _focus(tmp_path)
    focus_gate.handle({"hook_event_name": "UserPromptExpansion", "session_id": "s1", "command_name": "fabrica:reflect"})
    assert _write(focus) is None
    assert _write(focus, tool="Edit") is None  # several writes in the same reflect


def test_model_invoked_reflect_opens_the_gate(tmp_path: Path) -> None:
    focus = _focus(tmp_path)
    focus_gate.handle({"hook_event_name": "PostToolUse", "session_id": "s1", "tool_name": "Skill",
                       "tool_input": {"skill": "fabrica:reflect"}})
    assert _write(focus) is None


def test_the_gate_closes_at_the_stop_after_focus_was_written(tmp_path: Path) -> None:
    focus = _focus(tmp_path)
    focus_gate.handle({"hook_event_name": "UserPromptExpansion", "session_id": "s1", "command_name": "fabrica:reflect"})
    focus_gate.handle({"hook_event_name": "Stop", "session_id": "s1"})  # reflect asked a question: turn ends, gate stays open
    assert _write(focus) is None
    focus_gate.handle({"hook_event_name": "Stop", "session_id": "s1"})
    assert _denied(_write(focus))


def test_other_sessions_skills_and_files_are_not_affected(tmp_path: Path) -> None:
    focus = _focus(tmp_path)
    focus_gate.handle({"hook_event_name": "UserPromptExpansion", "session_id": "s1", "command_name": "fabrica:reflect"})
    assert _denied(_write(focus, session="s2"))
    focus_gate.handle({"hook_event_name": "UserPromptExpansion", "session_id": "s3", "command_name": "fabrica:tidy"})
    assert _denied(_write(focus, session="s3"))
    other = focus.parent / "BACKLOG.md"
    assert _write(other, session="s4") is None
    stray = tmp_path / "notes" / "FOCUS.md"
    assert _write(stray, session="s4") is None


def test_hostile_or_missing_input_never_raises(tmp_path: Path) -> None:
    assert focus_gate.handle({"hook_event_name": "PreToolUse", "session_id": "../x", "tool_name": "Write",
                              "tool_input": {"file_path": str(_focus(tmp_path))}}) is None
    assert focus_gate.handle({"hook_event_name": "PreToolUse", "session_id": "s1", "tool_name": "Write", "tool_input": "x"}) is None
    assert focus_gate.handle({}) is None
