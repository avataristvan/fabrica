"""Tests for uninstall.py — stop_running_daemon."""
from __future__ import annotations

from unittest.mock import patch

import uninstall


def test_stop_running_daemon_calls_stop_daemon_with_db_path():
    with patch("ai_mem.daemon.stop_daemon", return_value=True) as stop_daemon:
        uninstall.stop_running_daemon(dry_run=False)
    stop_daemon.assert_called_once_with(uninstall.DB_PATH)


def test_stop_running_daemon_dry_run_does_not_call_stop_daemon():
    with patch("ai_mem.daemon.stop_daemon") as stop_daemon:
        uninstall.stop_running_daemon(dry_run=True)
    stop_daemon.assert_not_called()


def test_stop_running_daemon_silent_when_package_not_importable():
    with patch.dict("sys.modules", {"ai_mem.daemon": None}):
        uninstall.stop_running_daemon(dry_run=False)  # must not raise


# ---------------------------------------------------------------------------
# hooks, command and links the plugin replaced (temp HOME only)
# ---------------------------------------------------------------------------

import json

import pytest

import install


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(install, "HOME", tmp_path)
    monkeypatch.setattr(uninstall, "HOME", tmp_path)
    return tmp_path


def _write_settings(home, hooks):
    (home / ".claude").mkdir(exist_ok=True)
    (home / ".claude" / "settings.json").write_text(json.dumps({"hooks": hooks}))


def _hooks(home):
    return json.loads((home / ".claude" / "settings.json").read_text())["hooks"]


def _command(text):
    return {"hooks": [{"type": "command", "command": text}]}


LEGACY = {
    "SessionStart": [_command("AI_MEM_WORKSPACE_ROOT=/ws /py -m ai_mem.hook 2>/dev/null || true")],
    "SubagentStop": [_command("/py -m ai_mem.hooks.retro_check 2>/dev/null || true")],
    "PostToolUse": [_command("/py -m ai_mem.hooks.lint_after_write 2>/dev/null || true")],
    "Stop": [_command("/py -m ai_mem.hooks.reflect_reminder 2>/dev/null || true"), _command("my-own-stop-hook")],
}


def test_uninstall_removes_the_plugin_provided_hooks_and_keeps_the_rest(home):
    _write_settings(home, LEGACY)
    uninstall.unregister_claude(dry_run=False)
    assert _hooks(home) == {"Stop": [_command("my-own-stop-hook")]}


def test_uninstall_matches_hooks_whatever_interpreter_or_env_prefix(home):
    _write_settings(home, {"SessionStart": [_command("/some/other/python -m ai_mem.hook 2>/dev/null || true")]})
    uninstall.unregister_claude(dry_run=False)
    assert _hooks(home) == {}


def test_uninstall_leaves_a_user_hook_that_merely_mentions_ai_mem(home):
    kept = {"SessionStart": [_command("echo ai_mem.hooks are nice")]}
    _write_settings(home, kept)
    uninstall.unregister_claude(dry_run=False)
    assert _hooks(home) == kept


def test_dry_run_changes_nothing(home):
    _write_settings(home, LEGACY)
    before = (home / ".claude" / "settings.json").read_text()
    uninstall.unregister_claude(dry_run=True)
    assert (home / ".claude" / "settings.json").read_text() == before


def test_uninstall_removes_symlinks_into_this_checkout_only(home):
    claude = home / ".claude"
    (claude / "agents").mkdir(parents=True)
    (claude / "ai-mem").mkdir()
    (claude / "skills").mkdir()
    # the old locations of the agents (symlinks may dangle after the move into agents/)
    for name in ("librarian", "archivist", "anchor-lint"):
        (claude / "agents" / f"{name}.md").symlink_to(uninstall.REPO_ROOT / "examples" / "agents" / f"{name}.md")
    (claude / "ai-mem" / "navigating_records.md").symlink_to(uninstall.REPO_ROOT / "reference" / "navigating_records.md")
    elsewhere = home / "elsewhere"
    elsewhere.mkdir()
    (claude / "skills" / "handoff-protocol").symlink_to(elsewhere)
    uninstall.unregister_claude(dry_run=False)
    assert not any(p.is_symlink() for p in (claude / "agents").iterdir())
    assert not (claude / "ai-mem").exists()
    assert (claude / "skills" / "handoff-protocol").is_symlink()


def test_uninstall_leaves_a_real_file_where_a_link_would_be(home):
    target = home / ".claude" / "agents" / "archivist.md"
    target.parent.mkdir(parents=True)
    target.write_text("my own archivist\n")
    uninstall.unregister_claude(dry_run=False)
    assert target.read_text() == "my own archivist\n"


def test_plugin_leftovers_lists_hooks_command_and_links(home):
    _write_settings(home, LEGACY)
    (home / ".claude" / "commands").mkdir()
    (home / ".claude" / "commands" / "reflect.md").write_text("ai-mem /reflect: hand candidates to the archivist")
    (home / ".claude" / "agents").mkdir()
    (home / ".claude" / "agents" / "librarian.md").symlink_to(uninstall.REPO_ROOT / "agents" / "librarian.md")
    found = uninstall.plugin_leftovers(home)
    assert len(found) == 6 and "command reflect.md" in found and any("librarian.md" in item for item in found)


def test_plugin_covers_every_hook_of_hooks_json():
    plugin_hooks = json.loads((uninstall.REPO_ROOT / "hooks" / "hooks.json").read_text())["hooks"]
    assert set(plugin_hooks) == set(uninstall.PLUGIN_HOOK_EVENTS)
    for groups in plugin_hooks.values():
        module = groups[0]["hooks"][0]["command"].rsplit(" ", 1)[1]
        assert any(marker in f"-m {module} " for marker in uninstall.PLUGIN_HOOK_MARKERS)


def test_a_users_own_reflect_command_is_not_a_leftover(home):
    (home / ".claude" / "commands").mkdir(parents=True)
    (home / ".claude" / "commands" / "reflect.md").write_text("my own standup")
    assert uninstall.plugin_leftovers(home) == []
    uninstall.remove_plugin_provided(home, dry_run=False)
    assert (home / ".claude" / "commands" / "reflect.md").read_text() == "my own standup"


def test_an_old_mem_init_copy_is_a_leftover_and_removed_but_a_users_own_stays(home):
    commands = home / ".claude" / "commands"
    commands.mkdir(parents=True)
    (commands / "mem-init.md").write_text("Initialize or update the ai-mem memory for the current project scope.")
    assert uninstall.plugin_leftovers(home) == ["command mem-init.md"]
    uninstall.remove_plugin_provided(home, dry_run=False)
    assert not (commands / "mem-init.md").exists()
    (commands / "mem-init.md").write_text("my own init, it mentions ai-mem and the archivist")
    uninstall.unregister_claude(dry_run=False)
    assert (commands / "mem-init.md").read_text() == "my own init, it mentions ai-mem and the archivist"


def test_a_link_that_climbs_out_of_the_checkout_is_left_alone(home):
    agents = home / ".claude" / "agents"
    agents.mkdir(parents=True)
    (agents / "librarian.md").symlink_to(uninstall.REPO_ROOT / ".." / ".." / "elsewhere.md")
    assert uninstall.plugin_leftovers(home) == []
    uninstall.remove_plugin_provided(home, dry_run=False)
    assert (agents / "librarian.md").is_symlink()


@pytest.mark.parametrize("hooks", [[], {"Stop": "x"}, {"Stop": [None, 3, {"hooks": "x"}, {"hooks": [None, {"command": 5}]}]}])
def test_malformed_settings_hooks_are_skipped(home, hooks):
    _write_settings(home, hooks)
    assert uninstall.plugin_leftovers(home) == []
    uninstall.remove_plugin_provided(home, dry_run=False)
