"""Tests for hook.py -- the SessionStart hook: Area line, records pointer, upgrade guard, doctor pointer."""
from __future__ import annotations

import json
import sys
import time
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_mem import hook


def _run_main(db_path: Path, area: object | None = None) -> str:
    """Run hook.main() with the area lookup mocked; return captured stdout."""
    db_path.mkdir(parents=True, exist_ok=True)
    captured: list[str] = []
    with (
        patch.object(sys, "stdin", StringIO("{}")),
        patch.object(hook, "DB_PATH", db_path),
        patch.object(hook, "find_area", return_value=area),
        patch("builtins.print", side_effect=lambda s: captured.append(s)),
    ):
        hook.main()
    return "\n".join(captured)


def _with_records(tmp_path: Path, focus: bool = True) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "records").mkdir(parents=True)
    if focus:
        (root / "docs" / "records" / "FOCUS.md").write_text("focus\n")
    return root


# ---------------------------------------------------------------------------
# Upgrade guard: Chroma store without records_v1.done
# ---------------------------------------------------------------------------

def _chroma_store(db_path: Path, sentinel: bool) -> Path:
    db_path.mkdir(parents=True, exist_ok=True)
    (db_path / "chroma.sqlite3").write_bytes(b"")
    if sentinel:
        (db_path / ".migrations").mkdir()
        (db_path / ".migrations" / "records_v1.done").touch()
    return db_path


def test_guard_line_comes_first_when_migration_pending(tmp_path: Path) -> None:
    db = _chroma_store(tmp_path / "db", sentinel=False)
    root = _with_records(tmp_path)
    out = _run_main(db, area=_area(root))
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    lines = ctx.splitlines()
    assert lines[0] == "[ai-mem]" and lines[1] == hook.GUARD_MESSAGE
    assert f"Area: {root}" in ctx


def test_no_guard_line_once_migrated(tmp_path: Path) -> None:
    db = _chroma_store(tmp_path / "db", sentinel=True)
    out = _run_main(db, area=_area(_with_records(tmp_path)))
    assert "upgrade pending" not in out


def test_guard_line_alone_outside_any_project(tmp_path: Path) -> None:
    db = _chroma_store(tmp_path / "db", sentinel=False)
    out = _run_main(db)
    assert json.loads(out)["hookSpecificOutput"]["additionalContext"] == "[ai-mem]\n" + hook.GUARD_MESSAGE


def test_guard_check_failure_never_raises(tmp_path: Path) -> None:
    with patch.object(hook, "migration_pending", side_effect=OSError("boom")):
        out = _run_main(tmp_path, area=_area(_with_records(tmp_path)))
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "Area: " in ctx and "upgrade pending" not in ctx


def test_hook_process_prints_guard_line_for_a_store_without_sentinel(tmp_path: Path) -> None:
    """End to end in a fresh process: no mocks, a store without records_v1.done."""
    import subprocess

    db = _chroma_store(tmp_path / "db", sentinel=False)
    repo_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "ai_mem.hook"], input="{}", capture_output=True, text=True, cwd=tmp_path,
        env={"AI_MEM_PATH": str(db), "HOME": str(tmp_path), "PATH": "/usr/bin:/bin", "PYTHONPATH": str(repo_root)},
    )
    assert result.returncode == 0 and result.stderr == ""
    assert hook.GUARD_MESSAGE in json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]


# ---------------------------------------------------------------------------
# Area line (D3) and doctor pointer (D7)
# ---------------------------------------------------------------------------

def _area(root: Path) -> MagicMock:
    area = MagicMock()
    area.root = root
    area.records_dir = root / "docs" / "records"
    return area


def _context_for_area(tmp_path: Path) -> str:
    root = _with_records(tmp_path)
    out = _run_main(tmp_path / "db", area=_area(root))
    return json.loads(out)["hookSpecificOutput"]["additionalContext"]


def test_area_line_and_records_pointer_without_claude_md(tmp_path: Path) -> None:
    ctx = _context_for_area(tmp_path)
    assert f"Area: {tmp_path / 'repo'}" in ctx
    assert ctx.index("Area: ") < ctx.index("Records: ")
    assert "collection" not in ctx


def test_records_pointer_names_focus_index_and_librarian(tmp_path: Path) -> None:
    ctx = _context_for_area(tmp_path)
    assert "FOCUS.md = current focus" in ctx and "INDEX.md" in ctx and "librarian" in ctx


def test_records_pointer_omits_focus_when_no_focus_file(tmp_path: Path) -> None:
    root = _with_records(tmp_path, focus=False)
    ctx = json.loads(_run_main(tmp_path / "db", area=_area(root)))["hookSpecificOutput"]["additionalContext"]
    assert "FOCUS.md" not in ctx


def test_no_output_outside_an_area(tmp_path: Path) -> None:
    assert _run_main(tmp_path / "db") == ""


def test_doctor_pointer_when_never_run(tmp_path: Path) -> None:
    assert "Run mem doctor (not run yet)." in _context_for_area(tmp_path)


def test_doctor_pointer_names_age_when_older_than_14_days(tmp_path: Path) -> None:
    db = tmp_path / "db"
    db.mkdir()
    (db / "doctor_last_run").write_text(f"{int(time.time()) - 20 * 86400}\n")
    assert "Run mem doctor (last run 20 days ago)." in _context_for_area(tmp_path)


def test_no_doctor_pointer_when_run_recently(tmp_path: Path) -> None:
    db = tmp_path / "db"
    db.mkdir()
    (db / "doctor_last_run").write_text(f"{int(time.time()) - 3 * 86400}\n")
    assert "mem doctor" not in _context_for_area(tmp_path)


def test_doctor_cadence_option_moves_the_threshold(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "db"
    db.mkdir()
    (db / "doctor_last_run").write_text(f"{int(time.time()) - 3 * 86400}\n")
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_DOCTOR_CADENCE_DAYS", "2")
    assert "Run mem doctor (last run 3 days ago)." in _context_for_area(tmp_path)


def test_doctor_cadence_option_garbage_keeps_the_default(tmp_path: Path, monkeypatch) -> None:
    db = tmp_path / "db"
    db.mkdir()
    (db / "doctor_last_run").write_text(f"{int(time.time()) - 3 * 86400}\n")
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_DOCTOR_CADENCE_DAYS", "soon")
    assert "mem doctor" not in _context_for_area(tmp_path)


def test_doctor_pointer_on_unreadable_timestamp(tmp_path: Path) -> None:
    db = tmp_path / "db"
    db.mkdir()
    (db / "doctor_last_run").write_text("garbage\n")
    assert "Run mem doctor (not run yet)." in _context_for_area(tmp_path)


def test_area_lines_never_raise(tmp_path: Path) -> None:
    with patch.object(hook, "find_area", side_effect=RuntimeError("boom")):
        assert hook._area_lines() == []


def test_doctor_pointer_survives_overflowing_timestamp(tmp_path: Path) -> None:
    (tmp_path / "doctor_last_run").write_text("-1e999\n")
    assert hook._doctor_pointer(tmp_path, time.time()) == "Run mem doctor (not run yet)."
