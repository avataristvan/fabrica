"""Stop hook: remind once per session to run /reflect when the session changed files and never reflected.

The transcript is only searched for a Write/Edit/MultiEdit tool use and for a /reflect invocation; nothing
from it is output. The reminder is a user-visible `systemMessage`, never a `block` (a Stop block forces
another turn and can loop), and a marker `$AI_MEM_PATH/reminded/<session_id>` makes it fire at most once.

The scan is incremental: `$AI_MEM_PATH/reflect_scan/<session_id>.json` keeps the byte offset after the last
complete line, the file identity and the (edited, reflected) seen so far, so each Stop reads only what was
appended. A transcript that shrank or was replaced (offset beyond size, other inode) is rescanned from 0;
an unreadable or malformed state file is treated as absent.
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


def _scan_line(line: str) -> tuple[bool, bool]:
    """(edited, reflected) for one transcript line."""
    if '"tool_use"' not in line and "reflect" not in line:  # cheap prefilter before json.loads
        return False, False
    try:
        message = json.loads(line).get("message")
    except (ValueError, AttributeError):
        return False, False
    if not isinstance(message, dict):
        return False, False
    edited = reflected = False
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
    return edited, reflected


def _scan_dir() -> Path:
    return state_dir() / "reflect_scan"


def _load_state(session_id: str, identity: list[int], size: int) -> tuple[int, bool, bool]:
    """(offset, edited, reflected) to resume from; (0, False, False) when absent, malformed or stale."""
    try:
        saved = json.loads((_scan_dir() / f"{session_id}.json").read_text(encoding="utf-8"))
        offset, edited, reflected = saved["offset"], saved["edited"], saved["reflected"]
    except (OSError, ValueError, TypeError, KeyError):
        return 0, False, False
    valid = (
        type(offset) is int and 0 <= offset <= size
        and isinstance(edited, bool) and isinstance(reflected, bool)
        and saved.get("file") == identity
    )
    return (offset, edited, reflected) if valid else (0, False, False)


def _save_state(session_id: str, identity: list[int], offset: int, edited: bool, reflected: bool) -> None:
    """Best effort: a failed write only means the next Stop rescans more."""
    directory = _scan_dir()
    try:
        directory.mkdir(parents=True, exist_ok=True)
        tmp = directory / f"{session_id}.json.tmp"
        tmp.write_text(json.dumps({"file": identity, "offset": offset, "edited": edited, "reflected": reflected}), encoding="utf-8")
        os.replace(tmp, directory / f"{session_id}.json")
    except OSError:
        pass


def _scan(transcript: Path, session_id: str) -> tuple[bool, bool]:
    """(edited, reflected) for the session transcript, resuming after the last complete line already scanned.

    Streamed, so a long session is never held in memory. A trailing line without a newline may still be
    growing; it is scanned but the saved offset stays before it, so the next Stop reads it again whole.
    """
    with open(transcript, "rb") as lines:
        stat = os.fstat(lines.fileno())
        identity = [stat.st_dev, stat.st_ino]
        offset, edited, reflected = _load_state(session_id, identity, stat.st_size)
        if not reflected:
            lines.seek(offset)
            for raw in lines:
                line_edited, line_reflected = _scan_line(raw.decode("utf-8", errors="replace"))
                edited, reflected = edited or line_edited, reflected or line_reflected
                if raw.endswith(b"\n"):
                    offset += len(raw)
                if reflected:
                    break
    _save_state(session_id, identity, offset, edited, reflected)
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
        edited, reflected = _scan(transcript, session_id)
    except OSError:
        return None
    if not edited or reflected or not _claim_marker(session_id):
        return None
    return {"systemMessage": REMINDER}


def main() -> None:
    run(handle)


if __name__ == "__main__":
    main()
