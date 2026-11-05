"""Focus gate: changing the focus means a reflect. One module for four events.

- `UserPromptExpansion` (a typed `/fabrica:reflect`) and `PostToolUse` with matcher `Skill` (a model-invoked one)
  write the marker `$AI_MEM_PATH/reflect_started/<session_id>`.
- `PreToolUse` (`Write|Edit`) denies writing an area's `docs/records/FOCUS.md` when this session has no marker,
  with the reason shown to the model; an allowed write is noted in the marker.
- `Stop` removes a marker whose reflect has written FOCUS.md: the next focus change needs the next reflect.
  A reflect that asks the user questions spans several turns; its marker stays until FOCUS.md is written.

Markers are files keyed by session id, not a transcript scan: the transcript format is internal to Claude Code.
Writes through Bash bypass the gate; `mem doctor` (Not concluded) finds what slipped through. Never raises.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from ai_mem.hooks import is_safe_token, run, state_dir

REFLECT_SKILLS = frozenset({"reflect", "fabrica:reflect", "ai-mem:reflect"})
_WROTE_FOCUS = "wrote-focus\n"
_MARKER_DAYS = 7
_DENY = ("A focus change goes through /fabrica:reflect: run it first (it writes FOCUS.md with the handoff and hands "
         "record candidates to the archivist). The user may still edit FOCUS.md by hand.")


def _marker(session_id: str) -> Path:
    return state_dir() / "reflect_started" / session_id


def _is_focus_file(file_path: object) -> bool:
    """An area's FOCUS.md: `<area>/docs/records/FOCUS.md` where that docs/records/ exists (lexical, no symlink followed)."""
    if not isinstance(file_path, str) or not os.path.isabs(file_path):
        return False
    path = Path(os.path.normpath(file_path))
    if path.name != "FOCUS.md":
        return False
    from ai_mem.infrastructure.adr_paths import records_dir_for_root
    return path.parent.is_dir() and any(records_dir_for_root(root) == path.parent for root in path.parents)


def _prune(directory: Path) -> None:
    """Drop markers of sessions long gone: a reflect that never wrote FOCUS.md leaves one behind."""
    cutoff = time.time() - _MARKER_DAYS * 86400
    for old in directory.glob("*") if directory.is_dir() else []:
        if old.is_file() and old.stat().st_mtime < cutoff:
            old.unlink()


def _mark(session_id: str) -> None:
    marker = _marker(session_id)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("started\n")


def handle(event: dict) -> dict | None:
    session_id = event.get("session_id")
    if not is_safe_token(session_id):
        return None
    name = event.get("hook_event_name")
    try:
        if name == "UserPromptExpansion":
            if event.get("command_name") in REFLECT_SKILLS:
                _mark(session_id)
            return None
        if name == "PostToolUse":
            tool_input = event.get("tool_input")
            if event.get("tool_name") == "Skill" and isinstance(tool_input, dict) and tool_input.get("skill") in REFLECT_SKILLS:
                _mark(session_id)
            return None
        if name == "Stop":
            marker = _marker(session_id)
            if marker.is_file() and marker.read_text() == _WROTE_FOCUS:
                marker.unlink()
            _prune(marker.parent)
            return None
        if name == "PreToolUse":
            tool_input = event.get("tool_input")
            if event.get("tool_name") not in ("Write", "Edit") or not isinstance(tool_input, dict):
                return None
            if not _is_focus_file(tool_input.get("file_path")):
                return None
            marker = _marker(session_id)
            if marker.is_file():
                marker.write_text(_WROTE_FOCUS)
                return None
            return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                           "permissionDecisionReason": _DENY}}
    except OSError:
        return None
    return None


def main() -> None:
    run(handle)


if __name__ == "__main__":
    main()
