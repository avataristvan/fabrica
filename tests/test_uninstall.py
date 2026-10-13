"""Tests for uninstall.py -- the full uninstall runs against a temp HOME only."""
from __future__ import annotations

import json

import uninstall


def test_dry_run_changes_nothing_and_full_uninstall_removes_mcp_and_mem_dream_permission(tmp_path, monkeypatch):
    monkeypatch.setattr(uninstall, "HOME", tmp_path)
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude.json").write_text(json.dumps({"mcpServers": {"ai-mem": {}}}))
    settings = {"permissions": {"allow": ["mcp__ai-mem__mem_add", "Bash(mem-dream *)", "Bash(ls)"]}}
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps(settings))

    uninstall.unregister_claude(tmp_path, dry_run=True)
    assert "ai-mem" in json.loads((tmp_path / ".claude.json").read_text())["mcpServers"]

    uninstall.unregister_claude(tmp_path, dry_run=False)
    assert json.loads((tmp_path / ".claude.json").read_text())["mcpServers"] == {}
    assert json.loads((tmp_path / ".claude" / "settings.json").read_text())["permissions"]["allow"] == ["Bash(ls)"]


def test_save_json_keeps_owner_only_mode_of_a_credentials_file(tmp_path):
    target = tmp_path / ".claude.json"
    target.write_text('{"oauthAccount": "secret"}')
    target.chmod(0o600)
    uninstall._save_json(target, {"oauthAccount": "secret"}, dry_run=False)
    assert target.stat().st_mode & 0o777 == 0o600
    assert (tmp_path / ".claude.json.ai-mem.bak").stat().st_mode & 0o777 == 0o600
    assert not (tmp_path / ".claude.json.ai-mem.tmp").exists()


def test_backup_keeps_the_original_when_one_run_saves_settings_twice(tmp_path):
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    original = {
        "permissions": {"allow": ["mcp__ai-mem__mem_add", "Bash(mem-dream *)", "Read"]},
        "hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": "python3 -m ai_mem.hook "}]}]},
    }
    settings.write_text(json.dumps(original))
    uninstall.unregister_claude(tmp_path, dry_run=False)
    assert json.loads((settings.parent / "settings.json.ai-mem.bak").read_text()) == original
    assert json.loads(settings.read_text()) == {"permissions": {"allow": ["Read"]}, "hooks": {}}


def test_remove_commands_removes_shipped_copies_and_keeps_a_users_own(tmp_path):
    commands = tmp_path / ".claude" / "commands"
    commands.mkdir(parents=True)
    (commands / "reflect.md").write_text("Lightweight standup.\n\n## [retro] convention for subagents\n")
    own = commands / "mem-init.md"
    own.write_text("My own init: ask the ai-mem archivist.")
    uninstall._remove_commands(tmp_path, dry_run=False)
    assert not (commands / "reflect.md").exists() and own.exists()
