"""Tests for the mem_context tool in server.py."""
from __future__ import annotations

import asyncio
import json

import ai_mem.server as server_module


def _call(cwd):
    result = asyncio.run(server_module.call_tool("mem_context", {"cwd": cwd}))
    return result[0].text


def test_nested_project_under_workspace_root(monkeypatch, tmp_path):
    workspace = tmp_path / "ws"
    project = workspace / "acme" / "app"
    project.mkdir(parents=True)
    (project / "CLAUDE.md").write_text("# app\n")
    monkeypatch.setenv("AI_MEM_WORKSPACE_ROOT", str(workspace))
    data = json.loads(_call(str(project)))
    assert data["collection"] == "repo.acme.app"
    assert data["match"] == "workspace_root"
    assert data["claude_md_dir"] == str(project)


def test_workspace_root_itself(monkeypatch, tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# ws\n")
    monkeypatch.setenv("AI_MEM_WORKSPACE_ROOT", str(tmp_path))
    assert json.loads(_call(str(tmp_path)))["collection"] == "workspace"


def test_no_claude_md_returns_workspace(monkeypatch, tmp_path):
    monkeypatch.delenv("AI_MEM_WORKSPACE_ROOT", raising=False)
    data = json.loads(_call(str(tmp_path)))
    assert data["collection"] == "workspace"
    assert data["match"] == "none"


def test_relative_or_missing_cwd_is_an_error(tmp_path):
    assert _call("relative/path").startswith("Error:")
    assert _call(str(tmp_path / "missing")).startswith("Error:")
