"""PostToolUse hook (Write|Edit): lint the record file that was just written.

Only a file under some area's `docs/records/` is checked, with `records_lint` over that one record plus
INDEX.md, or over the format of BACKLOG.md when that is the file. Findings come back as a PostToolUse `block` reason (the tool already ran; the reason is shown
next to its result); a clean file produces no output. Never `--fix`: the hook reports, the author repairs.
When every finding is a migration finding (an older record format that `mem lint --fix` converts), the hook gives a
hint instead of a block: a project whose plugin was updated keeps editing its old records until the migration runs.
"""
from __future__ import annotations

import os
from pathlib import Path

from ai_mem.hooks import run

_MAX_FINDINGS = 5
_REASON_LIMIT = 800


def _record_area(path: Path):
    """The area whose records directory holds `path`, from the lexical path (no symlink is followed here)."""
    from ai_mem.infrastructure.adr_paths import BACKLOG_FILENAME, NON_ADR_FILENAMES, is_contained, records_dir_for_root
    from ai_mem.infrastructure.areas import Area

    for directory in path.parents:
        records_dir = records_dir_for_root(directory)
        if not records_dir.is_dir():
            continue
        if not is_contained(records_dir, directory, allow_symlink=False):
            return None
        top_level_state = path.parent == records_dir and path.name in NON_ADR_FILENAMES and path.name != BACKLOG_FILENAME
        if path.is_relative_to(records_dir) and not top_level_state:
            return Area(directory, records_dir)
        return None
    return None


def handle(event: dict) -> dict | None:
    tool_input = event.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(file_path, str) or not os.path.isabs(file_path) or not file_path.endswith(".md"):
        return None
    path = Path(os.path.normpath(file_path))
    if "/docs/records/" not in file_path.replace(os.sep, "/"):  # not a record: maybe an experiment or a handoff
        return _docs_findings(path)
    area = _record_area(path)
    if area is None or not (path.is_file() or path.is_symlink()):
        return None
    from ai_mem.infrastructure.adr_paths import BACKLOG_FILENAME
    from ai_mem.records_lint import MIGRATION_CODES, _read, check_backlog, lint_records  # lazy: an import failure must stay inside run()'s guard
    if path.parent == area.records_dir and path.name == BACKLOG_FILENAME:
        findings = check_backlog(area)
    else:
        findings = lint_records(area, [_read(area.records_dir, path)])
    if not findings:
        return None
    lines = [f"{Path(f.file).name}: {f.code}" for f in findings[:_MAX_FINDINGS]]  # codes only: no record text is echoed
    more = len(findings) - _MAX_FINDINGS
    if more > 0:
        lines.append(f"... and {more} more")
    if all(f.code in MIGRATION_CODES for f in findings):
        hint = ("ai-mem lint: this area still has the older record format (" + "; ".join(lines)
                + "). `mem lint --fix --area <area>` migrates it; editing on is fine.")
        return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": hint[:_REASON_LIMIT]}}
    reason = "ai-mem lint (run `mem lint` for details): " + "; ".join(lines)
    return {"decision": "block", "reason": reason[:_REASON_LIMIT]}


def _docs_findings(path: Path) -> dict | None:
    """An experiment or handoff of an area, checked by the documentation map; None for any other file."""
    if path.name != "README.md" and not path.name.startswith("handoff-"):
        return None
    from ai_mem import docs_lint

    for kind, check in (("experiment", docs_lint.check_experiment), ("handoff", docs_lint.check_handoff)):
        if docs_lint.records_dir_holding(path, kind) is not None and path.is_file() and not path.is_symlink():
            findings = check(path)
            if not findings:
                return None
            lines = [code + ": " + message for code, message in findings[:_MAX_FINDINGS]]
            plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
            where = f"{plugin_root}/reference/documentation_map.md" if plugin_root else "the documentation map"
            reason = f"ai-mem lint ({path.name}, see {where}): " + "; ".join(lines)
            return {"decision": "block", "reason": reason[:_REASON_LIMIT]}
    return None


def main() -> None:
    run(handle)


if __name__ == "__main__":
    main()
