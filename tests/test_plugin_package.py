"""The plugin package: manifest, hook runner and bin shims run from the checkout with the system python3 (stdlib only)."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from ai_mem.hooks.retro_check import DEFAULT_ROLES

ROOT = Path(__file__).resolve().parent.parent
ENV_DROP = ("PYTHONPATH", "AI_MEM_PATH", "AI_MEM_WORKSPACE_ROOT")


def _env(tmp_path: Path, **extra: str) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in ENV_DROP and not k.startswith("CLAUDE_PLUGIN")}
    return {**env, "HOME": str(tmp_path / "home"), "AI_MEM_PATH": str(tmp_path / "state"), **extra}


def _area(tmp_path: Path) -> Path:
    area = tmp_path / "testarea"
    (area / "docs" / "records").mkdir(parents=True)
    return area


def test_manifest_and_marketplace_name_the_same_plugin() -> None:
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert manifest["name"] == "fabrica"
    assert [p["name"] for p in market["plugins"]] == ["fabrica"]
    assert manifest["userConfig"]["retro_roles"]["default"].split(",") == list(DEFAULT_ROLES)


def test_no_mcp_json_in_the_plugin() -> None:
    # The plugin is what git tracks; a developer's ignored local .mcp.json (IDE servers) never ships.
    tracked = subprocess.run(["git", "ls-files", ".mcp.json"], cwd=ROOT, capture_output=True, text=True, check=True)
    assert tracked.stdout.strip() == ""


def test_hooks_json_runs_every_enforcing_module_through_the_runner() -> None:
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())["hooks"]
    commands = {event: groups[0]["hooks"][0]["command"] for event, groups in hooks.items()}
    assert set(commands) == {"SessionStart", "SubagentStop", "PostToolUse", "Stop"}
    assert all(c.startswith('python3 "${CLAUDE_PLUGIN_ROOT}/hooks/run.py" ai_mem.') for c in commands.values())
    assert commands["SubagentStop"].endswith("ai_mem.hooks.retro_check")
    assert hooks["PostToolUse"][0]["matcher"] == "Write|Edit"


def test_agents_and_skills_name_plugin_paths_and_namespaced_agents() -> None:
    for name in ("librarian", "archivist"):
        text = (ROOT / "agents" / f"{name}.md").read_text()
        assert "${CLAUDE_PLUGIN_ROOT}/reference/navigating_records.md" in text
        assert "~/.claude/ai-mem" not in text
    assert (ROOT / "reference" / "navigating_records.md").is_file()
    assert (ROOT / "reference" / "documentation_map.md").is_file()
    for path in ("agents/archivist.md", "skills/reflect/SKILL.md", "skills/handoff-protocol/SKILL.md", "skills/tidy/SKILL.md"):
        assert "${CLAUDE_PLUGIN_ROOT}/reference/documentation_map.md" in (ROOT / path).read_text()
    assert (ROOT / "agents" / "anchor-lint.md").is_file() and (ROOT / "skills" / "reflect" / "SKILL.md").is_file()
    assert 'subagent_type="fabrica:archivist"' in (ROOT / "skills" / "reflect" / "SKILL.md").read_text()


def test_mem_shim_runs_without_install(tmp_path: Path) -> None:
    area = _area(tmp_path)
    result = subprocess.run(["/bin/sh", str(ROOT / "bin" / "mem"), "context"], cwd=area, env=_env(tmp_path),
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert str(area) in result.stdout


def test_mem_dream_shim_dry_run_starts(tmp_path: Path) -> None:
    result = subprocess.run(["/bin/sh", str(ROOT / "bin" / "mem-dream"), "--help"], cwd=tmp_path, env=_env(tmp_path),
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0 and "usage" in result.stdout.lower()


def _run_hook(tmp_path: Path, module: str, payload: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["python3", "-I", str(ROOT / "hooks" / "run.py"), module], input=payload, cwd=cwd,
                          env=_env(tmp_path), capture_output=True, text=True, timeout=60)


def test_runner_session_start_prints_the_area_line(tmp_path: Path) -> None:
    area = _area(tmp_path)
    result = _run_hook(tmp_path, "ai_mem.hook", json.dumps({"hook_event_name": "SessionStart", "cwd": str(area)}), area)
    assert result.returncode == 0 and result.stderr == ""
    assert f"Area: {area}" in result.stdout


def test_runner_retro_check_blocks_once(tmp_path: Path) -> None:
    event = {"agent_type": "fabrica:anchor-lint", "agent_id": "a1", "session_id": "s1", "last_assistant_message": "no retro"}
    result = _run_hook(tmp_path, "ai_mem.hooks.retro_check", json.dumps(event), tmp_path)
    assert result.returncode == 0 and result.stderr == ""
    assert json.loads(result.stdout)["decision"] == "block"


def test_runner_is_silent_and_exits_zero_on_hostile_input(tmp_path: Path) -> None:
    for module, payload in (("ai_mem.hooks.retro_check", "{not json"), ("ai_mem.nope", ""), ("os", ""),
                            ("ai_mem.hooks.retro_check;import os", "[]"), ("../x", "")):
        result = _run_hook(tmp_path, module, payload, tmp_path)
        assert (result.returncode, result.stdout, result.stderr) == (0, "", ""), module


def test_runner_without_a_module_is_silent(tmp_path: Path) -> None:
    result = subprocess.run(["python3", "-I", str(ROOT / "hooks" / "run.py")], input="", env=_env(tmp_path),
                            capture_output=True, text=True, timeout=60)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
