#!/usr/bin/env python3
"""SessionStart hook -- announces the area the session works in (`Area:`), where its records live, and the
upgrade guard / doctor pointers. It pushes no memory content; agents pull via the records and the librarian."""
import json
import math
import os
import sys
import time
from pathlib import Path

from ai_mem.hooks import DOCTOR_STAMP  # stdlib-only, so it stays outside the guarded imports below

DB_PATH = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local" / "share" / "ai-mem"))

# Module-level imports for patchability in tests.
try:
    from ai_mem.infrastructure.areas import find_area
    from ai_mem.upgrade_guard import GUARD_MESSAGE, migration_pending
except ImportError:
    find_area = None  # type: ignore[assignment]
    GUARD_MESSAGE = ""
    migration_pending = None  # type: ignore[assignment]


def _pointer_to(records: Path) -> str:
    focus = "FOCUS.md = current focus, " if (records / "FOCUS.md").is_file() else ""
    return (
        f"Records: {records} ({focus}INDEX.md = catalogue of decisions, learnings, todos). "
        "Read them on demand; for \"why is it like this / was this tried before?\" ask the librarian agent."
    )


_DOCTOR_INTERVAL_DAYS = 14


def _doctor_interval_days() -> float:
    """The plugin option `doctor_cadence_days` (env `CLAUDE_PLUGIN_OPTION_DOCTOR_CADENCE_DAYS`), else the default."""
    try:
        days = float(os.environ.get("CLAUDE_PLUGIN_OPTION_DOCTOR_CADENCE_DAYS", ""))
    except ValueError:
        return _DOCTOR_INTERVAL_DAYS
    return days if math.isfinite(days) and days > 0 else _DOCTOR_INTERVAL_DAYS


def _doctor_pointer(db_path: Path, now: float) -> str:
    """Pointer line only, never findings; `mem doctor` writes the timestamp (epoch seconds) when it runs."""
    try:
        age = now - float((db_path / DOCTOR_STAMP).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        age = math.nan
    if not math.isfinite(age):
        return "Run mem doctor (not run yet)."
    return f"Run mem doctor (last run {int(age // 86400)} days ago)." if age > _doctor_interval_days() * 86400 else ""


def _area_lines() -> list[str]:
    """`Area: <path>` and the Records pointer for the nearest area above the cwd, plus the doctor pointer when due."""
    try:
        area = find_area(Path.cwd())
        if area is None:
            return []
        lines = [f"Area: {area.root}", _pointer_to(area.records_dir), _doctor_pointer(DB_PATH, time.time())]
        return [line for line in lines if line]
    except Exception:
        return []


def main():
    if find_area is None or migration_pending is None:
        return

    parts = []
    try:
        # A Chroma store without records_v1 means this code runs on data it cannot read yet:
        # say so first, as one line (still no content).
        if migration_pending(DB_PATH):
            parts.append(GUARD_MESSAGE)
    except Exception:
        pass
    parts.extend(_area_lines())
    if not parts:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "[ai-mem]\n" + "\n".join(parts),
        }
    }))


if __name__ == "__main__":
    main()
