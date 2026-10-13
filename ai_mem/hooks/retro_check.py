"""SubagentStop hook: does a listed role's last answer end in a `[retro]` block with the two memory fields?

The first miss blocks once with a one-line reason (the subagent continues and adds the block); with
`stop_hook_active` the hook only logs, so it can never loop. Every checked stop appends one line to
`$AI_MEM_PATH/retro_log.jsonl` (schema in docs/reference/hooks.md, read by `mem doctor`). Roles are listed in
the plugin option `CLAUDE_PLUGIN_OPTION_RETRO_ROLES` (comma-separated agent types), else
`$AI_MEM_PATH/retro_roles.json` (a JSON list); other agent types produce no output and no log.
"""
from __future__ import annotations

import json
import os
import re
import time

from ai_mem.hooks import RETRO_LOG, run, state_dir

DEFAULT_ROLES = ("ai-mem:anchor-lint",)
REQUIRED_FIELDS = ("records_consulted", "record_candidates")
_FIELDS = ("learned", "blocked", "next", *REQUIRED_FIELDS)
_MARKER = re.compile(r"\[retro\]", re.IGNORECASE)
_FIELD_LINE = re.compile(r"^[\s>*#-]*\**(" + "|".join(_FIELDS) + r")\**\s*:\s*\**\s*(.*)$", re.IGNORECASE)
_VALUE_LIMIT = 2000
_ID_LIMIT = 200


def _roles() -> tuple[str, ...]:
    configured = [role.strip() for role in os.environ.get("CLAUDE_PLUGIN_OPTION_RETRO_ROLES", "").split(",") if role.strip()]
    if configured:
        return tuple(configured)
    try:
        data = json.loads((state_dir() / "retro_roles.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return DEFAULT_ROLES
    if isinstance(data, list) and all(isinstance(item, str) for item in data):
        return tuple(data)
    return DEFAULT_ROLES


def parse_retro(message: str) -> dict[str, str] | None:
    """Field values of the last `[retro]` block in `message`; None when there is no block."""
    markers = list(_MARKER.finditer(message))
    if not markers:
        return None
    fields: dict[str, str] = {}
    current: str | None = None
    for line in message[markers[-1].end():].splitlines():
        match = _FIELD_LINE.match(line)
        if match:
            current = match.group(1).lower()
            fields[current] = match.group(2).strip()
        elif current is not None and line.strip():
            fields[current] = f"{fields[current]} {line.strip()}".strip()
    return fields


def _text(value: object, limit: int) -> str:
    return value[:limit] if isinstance(value, str) else ""


def _field(fields: dict[str, str], name: str) -> str | None:
    return fields.get(name, "")[:_VALUE_LIMIT] or None


def _log(entry: dict) -> None:
    try:
        directory = state_dir()
        directory.mkdir(parents=True, exist_ok=True)
        with open(directory / RETRO_LOG, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # an unwritable log must not turn off the block


def handle(event: dict) -> dict | None:
    agent_type = event.get("agent_type")
    if not isinstance(agent_type, str) or agent_type not in _roles():
        return None
    message = event.get("last_assistant_message")
    fields = parse_retro(message if isinstance(message, str) else "")
    present = fields or {}
    missing = [name for name in REQUIRED_FIELDS if not present.get(name)]
    _log({
        "ts": time.time(),
        "session_id": _text(event.get("session_id"), _ID_LIMIT),
        "agent_type": agent_type[:_ID_LIMIT],
        "agent_id": _text(event.get("agent_id"), _ID_LIMIT),
        "has_retro": fields is not None,
        "missing": missing,
        "records_consulted": _field(present, "records_consulted"),
        "record_candidates": _field(present, "record_candidates"),
        "learned": _field(present, "learned"),
    })
    if not missing or event.get("stop_hook_active") is True:
        return None
    return {
        "decision": "block",
        "reason": f"Your [retro] block is missing: {', '.join(missing)}. Add it as the last part of your answer.",
    }


def main() -> None:
    run(handle)


if __name__ == "__main__":
    main()
