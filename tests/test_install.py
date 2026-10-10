"""Tests for install.py — _upsert_hook_command dedup logic."""
from __future__ import annotations

import json
from unittest.mock import patch

import install


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hook(command: str, timeout: int = 5) -> dict:
    return {"type": "command", "command": command, "timeout": timeout}


def _group(hooks: list[dict], matcher: str | None = None) -> dict:
    entry = {"hooks": hooks}
    if matcher is not None:
        entry["matcher"] = matcher
    return entry


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_matcher_not_overwritten_when_group_has_unrelated_hook():
    """A hook group that bundles an ai-mem hook alongside a user's own hook must keep
    its own matcher untouched — ai-mem should not claim a group it doesn't own outright."""
    ai_mem_hook = _hook("python3 -m ai_mem.sometest_hook ")
    unrelated_hook = _hook("some-other-tool --do-thing")
    entries = [_group([ai_mem_hook, unrelated_hook], matcher="UserPromptSubmit")]

    install._upsert_hook_command(
        entries, "ai_mem.sometest_hook", "python3 -m ai_mem.sometest_hook ", 5, matcher="SessionStart"
    )

    assert entries[0]["matcher"] == "UserPromptSubmit"
    assert unrelated_hook in entries[0]["hooks"]
    assert len(entries[0]["hooks"]) == 2


def test_matcher_overwritten_when_group_is_ai_mem_only():
    """When the group ends up holding only the ai-mem hook, the matcher may be updated."""
    ai_mem_hook = _hook("python3 -m ai_mem.sometest_hook ")
    entries = [_group([ai_mem_hook], matcher="OldMatcher")]

    install._upsert_hook_command(
        entries, "ai_mem.sometest_hook", "python3 -m ai_mem.sometest_hook ", 5, matcher="NewMatcher"
    )

    assert entries[0]["matcher"] == "NewMatcher"


def test_remove_by_identity_not_value_equality():
    """Two dict-value-equal empty groups in `entries` must not cause list.remove to drop
    the wrong one — removal must target the specific emptied entry by identity."""
    unrelated_empty = {"hooks": []}
    first_dup = _group([_hook("python3 -m ai_mem.sometest_hook ")])
    second_dup = _group([_hook("python -m ai_mem.sometest_hook ")])
    entries = [unrelated_empty, first_dup, second_dup]

    install._upsert_hook_command(
        entries, "ai_mem.sometest_hook", "python3 -m ai_mem.sometest_hook ", 5
    )

    # first_dup is kept (updated in place), second_dup gets emptied and removed by
    # identity — the pre-existing unrelated empty entry must survive untouched.
    assert any(e is unrelated_empty for e in entries)
    assert any(e is first_dup for e in entries)
    assert not any(e is second_dup for e in entries)
    assert len(entries) == 2


# ---------------------------------------------------------------------------
# _existing_workspace_root
# ---------------------------------------------------------------------------

def test_existing_workspace_root_recovered_from_installed_hook_command(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(json.dumps({
        "hooks": {
            "SessionStart": [_group([_hook(
                "AI_MEM_WORKSPACE_ROOT=/home/istvan/workspace python3 -m ai_mem.hook 2>/dev/null || true"
            )])]
        }
    }))

    assert install._existing_workspace_root(settings_path, "ai_mem.hook") == "/home/istvan/workspace"


def test_existing_workspace_root_empty_when_prefix_absent(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(json.dumps({
        "hooks": {"SessionStart": [_group([_hook("python3 -m ai_mem.hook 2>/dev/null || true")])]}
    }))

    assert install._existing_workspace_root(settings_path, "ai_mem.hook") == ""


def test_existing_workspace_root_empty_when_settings_file_missing(tmp_path):
    assert install._existing_workspace_root(tmp_path / "does_not_exist.json", "ai_mem.hook") == ""


# ---------------------------------------------------------------------------
# stop_running_daemon
# ---------------------------------------------------------------------------

def test_stop_running_daemon_calls_stop_daemon_with_db_path():
    with patch("ai_mem.daemon.stop_daemon", return_value=True) as stop_daemon:
        install.stop_running_daemon()
    stop_daemon.assert_called_once_with(install.DB_PATH)


def test_stop_running_daemon_silent_when_package_not_yet_installed():
    """A fresh machine has no ai_mem.daemon to import yet — must not raise."""
    with patch.dict("sys.modules", {"ai_mem.daemon": None}):
        install.stop_running_daemon()  # must not raise


# ---------------------------------------------------------------------------
# run_records_migration (records_v1)
# ---------------------------------------------------------------------------

def _run_records_migration(tmp_path, answers, db_exists=True, returncode=0):
    db_path = tmp_path / "db"
    if db_exists:
        db_path.mkdir()
    completed = type("Completed", (), {"returncode": returncode, "stdout": "1 files to write\nReport: x", "stderr": "boom"})
    with (
        patch.object(install, "DB_PATH", db_path),
        patch.object(install, "MIGRATIONS_DIR", db_path / ".migrations"),
        patch.object(install, "python_exe", return_value="python3"),
        patch.object(install.subprocess, "run", return_value=completed) as run,
        patch("builtins.input", side_effect=answers),
    ):
        install.run_records_migration(str(tmp_path / "ws"))
    return run, db_path / ".migrations" / "records_v1.done"


def test_records_migration_declined_runs_only_dry_run_and_asks_again_later(tmp_path):
    run, sentinel = _run_records_migration(tmp_path, ["n", "n"])
    assert run.call_count == 1 and "--apply" not in run.call_args.args[0]
    assert not sentinel.exists()


def test_records_migration_accepted_applies_and_marks_done(tmp_path):
    run, sentinel = _run_records_migration(tmp_path, ["n", "y"])
    assert run.call_count == 2 and run.call_args.args[0][-1] == "--apply"
    assert "--scan-root" in run.call_args.args[0]
    assert sentinel.exists()


def test_records_migration_failed_apply_leaves_no_sentinel(tmp_path):
    run, sentinel = _run_records_migration(tmp_path, ["n", "y"], returncode=1)
    assert run.call_count == 1  # the failed dry run stops before asking
    assert not sentinel.exists()


def test_records_migration_apply_exit_1_after_clean_dry_run_leaves_no_sentinel(tmp_path):
    """`migrate --apply` exits 1 for an unclean plan (unplaced/conflicts); install.py must not mark it done."""
    db_path = tmp_path / "db"
    db_path.mkdir()
    dry = type("Completed", (), {"returncode": 0, "stdout": "1 files to write", "stderr": ""})
    applied = type("Completed", (), {"returncode": 1, "stdout": "Report: x", "stderr": "records_v1 NOT marked done"})
    with (
        patch.object(install, "DB_PATH", db_path),
        patch.object(install, "MIGRATIONS_DIR", db_path / ".migrations"),
        patch.object(install, "python_exe", return_value="python3"),
        patch.object(install.subprocess, "run", side_effect=[dry, applied]) as run,
        patch("builtins.input", side_effect=["n", "y"]),
    ):
        install.run_records_migration(str(tmp_path / "ws"))

    assert run.call_count == 2 and run.call_args.args[0][-1] == "--apply"
    assert not (db_path / ".migrations" / "records_v1.done").exists()


def test_records_migration_without_store_only_marks_done(tmp_path):
    run, sentinel = _run_records_migration(tmp_path, [], db_exists=False)
    run.assert_not_called()
    assert sentinel.exists()
