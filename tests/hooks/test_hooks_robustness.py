"""Every enforcing hook exits 0 with empty stderr, whatever its stdin holds (pattern_hooks_must_not_raise)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

MODULES = ["retro_check", "lint_after_write", "reflect_reminder"]
HOSTILE_STDIN = [
    b"",
    b"not json",
    b"[]",
    b"null",
    b'{"agent_type": 5, "last_assistant_message": ["x"], "session_id": {}, "tool_input": "x", "transcript_path": 7}',
    b'{"agent_type": "the-coder", "session_id": "../../etc", "agent_id": "../x", "last_assistant_message": null}',
    b'{"tool_input": {"file_path": "../../docs/records/x/y/z.md"}, "session_id": "a/../b", "transcript_path": "/dev/zero"}',
    b"\xff\xfe\x00",
]


@pytest.mark.parametrize("module", MODULES)
@pytest.mark.parametrize("stdin", HOSTILE_STDIN)
def test_exit_zero_and_no_stderr_on_malformed_stdin(module: str, stdin: bytes, tmp_path: Path) -> None:
    env = {"AI_MEM_PATH": str(tmp_path / "state"), "PATH": "/usr/bin:/bin"}
    result = subprocess.run(
        [sys.executable, "-m", f"ai_mem.hooks.{module}"],
        input=stdin, capture_output=True, env=env, timeout=20, cwd=Path(__file__).parents[2],
    )
    assert result.returncode == 0
    assert result.stderr == b""


@pytest.mark.parametrize("module", MODULES)
def test_exit_zero_when_state_dir_is_unwritable(module: str, tmp_path: Path) -> None:
    blocker = tmp_path / "state"
    blocker.write_text("a file where the state directory should be")
    stdin = (
        b'{"agent_type": "the-coder", "last_assistant_message": "x", "session_id": "s1", '
        b'"transcript_path": "' + str(tmp_path / "t.jsonl").encode() + b'"}'
    )
    (tmp_path / "t.jsonl").write_text('{"message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Write", "input": {}}]}}\n')
    result = subprocess.run(
        [sys.executable, "-m", f"ai_mem.hooks.{module}"],
        input=stdin, capture_output=True, env={"AI_MEM_PATH": str(blocker), "PATH": "/usr/bin:/bin"},
        timeout=20, cwd=Path(__file__).parents[2],
    )
    assert result.returncode == 0 and result.stderr == b""


def test_hook_modules_import_nothing_beyond_the_stdlib() -> None:
    code = (
        "import sys; sys.path.insert(0, %r); "
        "import ai_mem.hooks.retro_check, ai_mem.hooks.lint_after_write, ai_mem.hooks.reflect_reminder; "
        "bad = [m for m in ('chromadb', 'mcp') if m in sys.modules]; assert not bad, bad"
    ) % str(Path(__file__).parents[2])
    result = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr.decode()


def test_session_start_hook_keeps_its_guarded_imports_without_chromadb_or_mcp() -> None:
    code = (
        "import sys; sys.path.insert(0, %r); import ai_mem.hook as h; "
        "assert h.find_area is not None and h.migration_pending is not None and h.detect_repo_context is not None; "
        "bad = [m for m in ('chromadb', 'mcp') if m in sys.modules]; assert not bad, bad"
    ) % str(Path(__file__).parents[2])
    result = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, timeout=20)
    assert result.returncode == 0, result.stderr.decode()
