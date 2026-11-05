"""Enforcing Claude Code hooks: they check that a ritual happened or remind of it, never inject record content.

Every hook module is a `python -m ai_mem.hooks.<name>` entry point that exits 0 with nothing on stderr,
whatever its stdin holds (pattern_hooks_must_not_raise). Stdlib only, so a hook runs on an installation
without any third-party package.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TypeGuard

DOCTOR_STAMP = "doctor_last_run"  # epoch seconds, written by `mem doctor`, read by the SessionStart pointer
RETRO_LOG = "retro_log.jsonl"  # written by retro_check, read by `mem doctor`
_SAFE_TOKEN = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


def state_dir() -> Path:
    return Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local" / "share" / "ai-mem"))


def is_safe_token(value: object) -> TypeGuard[str]:
    """Whether `value` may become a file name: hook stdin is not trusted (session ids, agent ids)."""
    return isinstance(value, str) and _SAFE_TOKEN.fullmatch(value) is not None


def run(handler: Callable[[dict], dict | None]) -> None:
    """Feed the hook's stdin JSON object to `handler` and print its result; swallow everything else."""
    try:
        event = json.load(sys.stdin)
        result = handler(event) if isinstance(event, dict) else None
        if result:
            sys.stdout.write(json.dumps(result))
            sys.stdout.flush()
    except BaseException:  # noqa: BLE001 -- a hook must not raise, not even on KeyboardInterrupt/SystemExit
        pass
