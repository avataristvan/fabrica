"""Stop hook: remind once per session to run /reflect when the session changed files and never reflected.

The transcript is only searched for a Write/Edit/MultiEdit tool use and for a /reflect invocation; nothing
from it is output. The reminder is a user-visible `systemMessage`, never a `block` (a Stop block forces
another turn and can loop), and a marker `$AI_MEM_PATH/reminded/<session_id>` makes it fire at most once.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from ai_mem.hooks import is_safe_token, run, state_dir

_EDIT_TOOLS = frozenset({"Write", "Edit", "MultiEdit"})
REMINDER = (
    "ai-mem: this session changed files. At the next boundary run /reflect to write the handoff and hand "
    "record candidates to the archivist."
)


def _mentions_reflect(content: object) -> bool:
    if isinstance(content, str):
        texts = [content]
    elif isinstance(content, list):
        texts = [block.get("text", "") for block in content if isinstance(block, dict)]
    else:
        return False
    return any(isinstance(text, str) and ("<command-name>/reflect" in text or text.lstrip().startswith("/reflect")) for text in texts)


def _scan(transcript: Path) -> tuple[bool, bool]:
    """(edited, reflected) for the session transcript; streamed, so a long session is never held in memory."""
    edited = reflected = False
    with open(transcript, encoding="utf-8", errors="replace") as lines:
        for line in lines:
            if '"tool_use"' not in line and "reflect" not in line:  # cheap prefilter before json.loads
                continue
            try:
                message = json.loads(line).get("message")
            except (ValueError, AttributeError):
                continue
            if not isinstance(message, dict):
                continue
            content = message.get("content")
            if message.get("role") == "user" and _mentions_reflect(content):
                reflected = True
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name, tool_input = block.get("name"), block.get("input")
                if name in _EDIT_TOOLS:
                    edited = True
                elif name == "Skill" and isinstance(tool_input, dict) and tool_input.get("skill") in ("reflect", "fabrica:reflect", "ai-mem:reflect"):
                    reflected = True
            if reflected:
                return edited, True
    return edited, reflected


def _marker_dir() -> Path:
    return state_dir() / "reminded"


def _claim_marker(session_id: str) -> bool:
    """Create the once-per-session marker; False when it already exists or cannot be created."""
    directory = _marker_dir()
    try:
        directory.mkdir(parents=True, exist_ok=True)
        os.close(os.open(directory / session_id, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644))
    except OSError:
        return False
    return True


def handle(event: dict) -> dict | None:
    session_id, transcript_path = event.get("session_id"), event.get("transcript_path")
    if not is_safe_token(session_id) or not isinstance(transcript_path, str) or event.get("stop_hook_active") is True:
        return None
    transcript = Path(transcript_path)
    # The exists() check only skips the scan; _claim_marker's O_EXCL is the authoritative once-guard.
    if (_marker_dir() / session_id).exists() or not transcript.is_file():  # is_file: never open a FIFO or device
        return None
    try:
        edited, reflected = _scan(transcript)
    except OSError:
        return None
    if not edited or reflected or not _claim_marker(session_id):
        return None
    return {"systemMessage": REMINDER}


def main() -> None:
    run(handle)


if __name__ == "__main__":
    main()
