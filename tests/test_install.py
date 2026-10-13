"""Tests for install.py — what the plugin replaced, workspace root recovery, migrations."""
from __future__ import annotations

import json
from unittest.mock import patch

import pytest

import install
import uninstall


def _hook(command: str, timeout: int = 5) -> dict:
    return {"type": "command", "command": command, "timeout": timeout}


def _group(hooks: list[dict]) -> dict:
    return {"hooks": hooks}


# ---------------------------------------------------------------------------
# _existing_workspace_root
# ---------------------------------------------------------------------------

def test_existing_workspace_root_recovered_from_installed_hook_command(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(json.dumps({
        "hooks": {
            "SessionStart": [_group([_hook(
                "AI_MEM_WORKSPACE_ROOT=/home/user/workspace python3 -m ai_mem.hook 2>/dev/null || true"
            )])]
        }
    }))

    assert install._existing_workspace_root(settings_path, "ai_mem.hook") == "/home/user/workspace"


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


# ---------------------------------------------------------------------------
# what install.py no longer deploys, and the plugin switch (temp HOME only)
# ---------------------------------------------------------------------------

@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "HOME", tmp_path)
    monkeypatch.setattr(uninstall, "HOME", tmp_path)
    return tmp_path


def test_sync_commands_is_gone_and_does_not_fall_through_to_the_interactive_install(home):
    with patch("sys.argv", ["install.py", "--sync-commands"]), pytest.raises(SystemExit) as exit_info:
        install.main()
    assert exit_info.value.code == 2
    assert not (home / ".claude").exists()


def test_register_claude_no_longer_deploys_hooks_or_commands(home):
    install.register_claude()
    settings = json.loads((home / ".claude" / "settings.json").read_text())
    assert "SessionStart" not in settings.get("hooks", {})
    assert not (home / ".claude" / "commands").exists()


LEGACY_SETTINGS = {"hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "AI_MEM_WORKSPACE_ROOT=/ws /py -m ai_mem.hook 2>/dev/null || true"}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "/py -m ai_mem.hooks.reflect_reminder 2>/dev/null || true"},
                         {"type": "command", "command": "my-own-stop-hook"}]}],
}}


def _legacy_home(home):
    (home / ".claude" / "commands").mkdir(parents=True)
    (home / ".claude" / "settings.json").write_text(json.dumps(LEGACY_SETTINGS))
    (home / ".claude" / "commands" / "reflect.md").write_text("ai-mem /reflect: hand candidates to the archivist")
    (home / ".claude" / "commands" / "mem-init.md").write_text("Initialize or update the ai-mem memory for the current project scope.\n\n1. Detect the active scope")


def test_plugin_switch_removes_leftovers_on_yes_and_keeps_user_hooks(home, capsys):
    _legacy_home(home)
    with patch("builtins.input", return_value="y"):
        install.offer_plugin_switch()
    settings = json.loads((home / ".claude" / "settings.json").read_text())
    assert "SessionStart" not in settings["hooks"]
    assert [h["command"] for g in settings["hooks"]["Stop"] for h in g["hooks"]] == ["my-own-stop-hook"]
    assert not any((home / ".claude" / "commands").iterdir())
    out = capsys.readouterr().out
    assert "SessionStart hook in settings.json" in out and "command mem-init.md" in out


def test_plugin_switch_flag_runs_only_the_offer(home):
    _legacy_home(home)
    with patch("sys.argv", ["install.py", "--plugin-switch"]), patch("builtins.input", return_value="y"):
        install.main()
    assert not (home / ".claude" / "commands" / "reflect.md").exists()
    assert not (home / ".claude.json").exists()


def test_plugin_switch_declined_changes_nothing(home):
    _legacy_home(home)
    before = (home / ".claude" / "settings.json").read_text()
    with patch("builtins.input", return_value="n"):
        install.offer_plugin_switch()
    assert (home / ".claude" / "settings.json").read_text() == before
    assert (home / ".claude" / "commands" / "reflect.md").exists()
    assert (home / ".claude" / "commands" / "mem-init.md").exists()


def test_plugin_switch_is_silent_without_leftovers(home):
    with patch("builtins.input", side_effect=AssertionError("must not ask")):
        install.offer_plugin_switch()


def test_failed_apply_message_does_not_call_the_migration_non_fatal(tmp_path, capsys):
    db_path = tmp_path / "db"
    db_path.mkdir()
    dry = type("Completed", (), {"returncode": 0, "stdout": "1 files to write", "stderr": ""})
    applied = type("Completed", (), {"returncode": 1, "stdout": "Report: x", "stderr": "records_v1 NOT marked done (2 unplaced)"})
    with (
        patch.object(install, "DB_PATH", db_path),
        patch.object(install, "python_exe", return_value="python3"),
        patch.object(install.subprocess, "run", side_effect=[dry, applied]),
        patch("builtins.input", side_effect=["n", "y"]),
    ):
        install.run_records_migration(str(tmp_path / "ws"))
    out = capsys.readouterr().out
    assert "NOT marked done" in out and "non-fatal" not in out


def test_unreadable_store_apply_failure_says_nothing_was_written(tmp_path, capsys):
    db_path = tmp_path / "db"
    db_path.mkdir()
    dry = type("Completed", (), {"returncode": 0, "stdout": "1 files to write", "stderr": ""})
    applied = type("Completed", (), {"returncode": 1, "stdout": "", "stderr": "cannot read the ChromaDB store"})
    with (
        patch.object(install, "DB_PATH", db_path),
        patch.object(install, "python_exe", return_value="python3"),
        patch.object(install.subprocess, "run", side_effect=[dry, applied]),
        patch("builtins.input", side_effect=["n", "y"]),
    ):
        install.run_records_migration(str(tmp_path / "ws"))
    out = capsys.readouterr().out
    assert "nothing was marked done" in out and "applied" not in out
