"""Tests for hook.py — SessionStart hook expert-agent collection injection."""
from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai_mem import hook


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_agent_ctx(agent_type: str | None, should_inject: bool = True) -> MagicMock:
    ctx = MagicMock()
    ctx.agent_type = agent_type
    ctx.should_inject = should_inject
    return ctx


def _make_repo_ctx(
    collection: str = "workspace",
    has_claude_md: bool = False,
    scope_name: str = "test",
    git_root: Path | None = None,
) -> MagicMock:
    ctx = MagicMock()
    ctx.collection = collection
    ctx.has_claude_md = has_claude_md
    ctx.scope_name = scope_name
    ctx.claude_md_dir = None
    ctx.git_root = git_root
    return ctx


def _make_entry(id: str, text: str) -> MagicMock:
    e = MagicMock()
    e.id = id
    e.text = text
    return e


def _run_main(
    tmp_path: Path,
    agent_type: str | None = None,
    should_inject: bool = True,
    focus_map: dict[str, str | None] | None = None,
    repo_collection: str = "workspace",
    session_delta: int | None = None,
    git_commits: list[str] | None = None,
    expert_query_results: list | None = None,
    expired_entries: list | None = None,
    expired_entries_by_collection: dict[str, list] | None = None,
    has_claude_md: bool = False,
    scope_name: str = "test",
    verbose: bool = True,
    extra_settings: dict | None = None,
    chroma_cls: MagicMock | None = None,
    git_root: Path | None = None,
) -> str:
    """Run hook.main() with mocked dependencies; return captured stdout.

    All imports in hook.py are now module-level, so patch.object(hook, ...) works.
    _focus_text, _session_delta, and _write_prev_session are patched directly
    to control output without standing up ChromaDB.

    expert_query_results: list of mock entries returned by repo.query() for the expert
    collection. Use _make_entry(id, text) to build them. Default: empty list (MagicMock
    default iteration yields nothing).

    expired_entries_by_collection: maps collection name -> entries returned by
    _expired_entries for that specific collection, so tests can tell apart the
    ctx.collection call from the unconditional GLOBAL_COLLECTION call. Takes
    precedence over the flat `expired_entries` when given.

    verbose: patches _load_settings to control session_start_verbose (default True,
    matching the pre-2026-09-16 push behavior these tests were written against). Pass
    False to exercise the new pull-based default (routing lines only, no content).

    extra_settings: further keys merged into the patched settings dict (e.g. session_start_index).

    chroma_cls: replaces the build_repository factory mock, to assert on or break construction.
    """
    if expired_entries_by_collection is not None:
        def fake_expired_entries(repo, collection: str, now_ts: float) -> list:
            return expired_entries_by_collection.get(collection, [])
    else:
        def fake_expired_entries(repo, collection: str, now_ts: float) -> list:
            return expired_entries or []
    focus_map = focus_map or {}

    def fake_focus_text(get_memory_uc, collection: str) -> str | None:
        return focus_map.get(collection)

    mock_list_uc = MagicMock()
    mock_list_uc.return_value.execute.return_value = []

    mock_chroma_cls = chroma_cls if chroma_cls is not None else MagicMock()
    mock_repo_instance = mock_chroma_cls.return_value
    mock_repo_instance.query.return_value = expert_query_results or []

    agent_ctx = _make_agent_ctx(agent_type, should_inject)
    repo_ctx = _make_repo_ctx(collection=repo_collection, has_claude_md=has_claude_md, scope_name=scope_name,
                              git_root=git_root)

    stdin_stream = StringIO(json.dumps({"transcript_path": None}))

    with (
        patch.object(sys, "stdin", stdin_stream),
        patch.object(hook, "DB_PATH", tmp_path),
        patch.object(hook, "_focus_text", side_effect=fake_focus_text),
        patch.object(hook, "_session_delta", return_value=session_delta),
        patch.object(hook, "_git_commits_since", return_value=git_commits or []),
        patch.object(hook, "_write_prev_session"),
        patch.object(hook, "detect_for_session_start", return_value=agent_ctx),
        patch.object(hook, "write_to_env_file"),
        patch.object(hook, "build_repository", mock_chroma_cls),
        patch.object(hook, "GetMemoryUseCase"),
        patch.object(hook, "detect_repo_context", return_value=repo_ctx),
        patch.object(hook, "record_injection"),
        patch.object(hook, "GLOBAL_COLLECTION", "global"),
        patch.object(hook, "WORKSPACE_COLLECTION", "workspace"),
        patch.object(hook, "ListCollectionsUseCase", mock_list_uc),
        patch.object(hook, "_expired_entries", side_effect=fake_expired_entries),
        patch.object(hook, "_load_settings", return_value={"session_start_verbose": verbose, **(extra_settings or {})}),
    ):
        tmp_path.mkdir(parents=True, exist_ok=True)
        captured: list[str] = []
        with patch("builtins.print", side_effect=lambda s: captured.append(s)):
            hook.main()

    return "\n".join(captured)


# ---------------------------------------------------------------------------
# 1. No agent_type → no expert block, no routing hint
# ---------------------------------------------------------------------------

def test_no_agent_type_produces_no_expert_output(tmp_path: Path) -> None:
    out = _run_main(tmp_path, agent_type=None, focus_map={"global": "global memory content"})

    assert out  # something is printed (global focus)
    assert "expertise" not in out
    assert "Expert collection" not in out
    assert "subagent" not in out


# ---------------------------------------------------------------------------
# 2. agent_type set, expert collection empty → routing hint still appears
# ---------------------------------------------------------------------------

def test_routing_hint_appears_even_when_expert_collection_empty(tmp_path: Path) -> None:
    out = _run_main(
        tmp_path,
        agent_type="the-coder",
        focus_map={"global": "global mem"},  # expert collection absent → None
    )

    assert out
    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert 'Expert collection: "subagent.the-coder"' in ctx
    assert 'collection="subagent.the-coder"' in ctx
    # expertise block absent since collection is empty
    assert "[the-coder expertise]" not in ctx


# ---------------------------------------------------------------------------
# 3. agent_type set, expert focus present → both expertise block and hint appear
# ---------------------------------------------------------------------------

def test_expert_focus_and_routing_hint_both_appear(tmp_path: Path) -> None:
    expert_text = "Prefer integration tests over mocks in Python projects."
    out = _run_main(
        tmp_path,
        agent_type="the-coder",
        focus_map={
            "global": "global mem",
            "subagent.the-coder": expert_text,
        },
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "[the-coder expertise]" in ctx
    assert expert_text in ctx
    assert 'Expert collection: "subagent.the-coder"' in ctx


# ---------------------------------------------------------------------------
# 4. expert_focus longer than _FOCUS_PREVIEW_CHARS is truncated
# ---------------------------------------------------------------------------

def test_expert_focus_is_truncated_to_preview_limit(tmp_path: Path) -> None:
    long_text = "A" * 300  # well beyond _FOCUS_PREVIEW_CHARS = 150
    out = _run_main(
        tmp_path,
        agent_type="general-purpose",
        focus_map={"subagent.general-purpose": long_text},
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    # The truncated text ends with the ellipsis character, not the full 300 chars
    assert "AAAA…" in ctx
    assert long_text not in ctx


# ---------------------------------------------------------------------------
# 4b. expert_query_results injected under "Relevant past learnings"
# ---------------------------------------------------------------------------

def test_expert_query_results_appear_in_expertise_block(tmp_path: Path) -> None:
    entry = _make_entry("learned_ddd", "Always push domain logic down — never let infra leak upward.")
    out = _run_main(
        tmp_path,
        agent_type="the-coder",
        focus_map={"global": "global mem"},
        expert_query_results=[entry],
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "[the-coder expertise]" in ctx
    assert "Relevant past learnings" in ctx
    assert "Always push domain logic down" in ctx


def test_current_focus_excluded_from_expert_query_results(tmp_path: Path) -> None:
    focus_entry = _make_entry("current_focus", "This is the focus entry.")
    other_entry = _make_entry("learned_xyz", "Use dependency injection consistently.")
    out = _run_main(
        tmp_path,
        agent_type="the-coder",
        focus_map={"global": "global mem"},
        expert_query_results=[focus_entry, other_entry],
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "This is the focus entry." not in ctx  # focus entry filtered out
    assert "Use dependency injection consistently." in ctx


# ---------------------------------------------------------------------------
# 5. should_inject=False → hook exits early, no output at all
# ---------------------------------------------------------------------------

def test_should_inject_false_produces_no_output(tmp_path: Path) -> None:
    out = _run_main(
        tmp_path,
        agent_type="the-coder",
        should_inject=False,
        focus_map={
            "global": "global mem",
            "subagent.the-coder": "expert mem",
        },
    )

    assert out == ""


# ---------------------------------------------------------------------------
# 9. Cross-session delta — positive delta shows the line
# ---------------------------------------------------------------------------

def test_session_delta_positive_shows_new_entries_line(tmp_path: Path) -> None:
    out = _run_main(
        tmp_path,
        focus_map={"global": "some context"},
        session_delta=5,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "Since last session: 5 new entries added" in ctx


def test_session_delta_singular_uses_entry_not_entries(tmp_path: Path) -> None:
    out = _run_main(
        tmp_path,
        focus_map={"global": "some context"},
        session_delta=1,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "Since last session: 1 new entry added" in ctx


# ---------------------------------------------------------------------------
# 10. Cross-session delta — None (no change or no prior) suppresses the line
# ---------------------------------------------------------------------------

def test_session_delta_none_suppresses_line(tmp_path: Path) -> None:
    out = _run_main(
        tmp_path,
        focus_map={"global": "some context"},
        session_delta=None,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "Since last session" not in ctx


# ---------------------------------------------------------------------------
# 11. Git commits since last session — commits present
# ---------------------------------------------------------------------------

def test_git_commits_shown_when_present(tmp_path: Path) -> None:
    commits = ["abc1234 feat: add dilemma warnings", "def5678 fix: early exit guard"]
    out = _run_main(
        tmp_path,
        focus_map={"global": "some context"},
        git_commits=commits,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "Git commits since last session" in ctx
    assert "abc1234 feat: add dilemma warnings" in ctx
    assert "def5678 fix: early exit guard" in ctx


# ---------------------------------------------------------------------------
# 12. Git commits since last session — no commits → no block
# ---------------------------------------------------------------------------

def test_no_git_commits_suppresses_block(tmp_path: Path) -> None:
    out = _run_main(
        tmp_path,
        focus_map={"global": "some context"},
        git_commits=[],
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "Git commits since last session" not in ctx


# ---------------------------------------------------------------------------
# Workspace-root CLAUDE.md — repo_focus lookup and "not found" warning accuracy
# ---------------------------------------------------------------------------

def test_workspace_focus_shown_when_claude_md_at_workspace_root(tmp_path: Path) -> None:
    """CLAUDE.md at the workspace root → collection is still 'workspace' but
    has_claude_md is True (see repo_context.py). A real current_focus entry there
    must be displayed, not silently dropped."""
    out = _run_main(
        tmp_path,
        repo_collection="workspace",
        has_claude_md=True,
        scope_name=None,
        focus_map={"workspace": "Ship the launch checklist.", "global": "global mem"},
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "[workspace focus]" in ctx
    assert "Ship the launch checklist." in ctx
    assert "No focus entry found" not in ctx


def test_workspace_not_found_warning_when_actually_missing(tmp_path: Path) -> None:
    """When CLAUDE.md is at the workspace root but no current_focus entry exists yet,
    the warning must still fire accurately."""
    out = _run_main(
        tmp_path,
        repo_collection="workspace",
        has_claude_md=True,
        scope_name=None,
        focus_map={"global": "global mem"},  # no "workspace" key → not found
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "No focus entry found" in ctx
    assert "[workspace focus]" not in ctx


def test_workspace_focus_suppressed_when_no_claude_md_anywhere(tmp_path: Path) -> None:
    """Genuinely unscoped session (no CLAUDE.md found at all): repo_focus lookup
    stays suppressed even if the 'workspace' collection happens to contain a
    current_focus entry, and no warning is shown either (has_claude_md gates both)."""
    out = _run_main(
        tmp_path,
        repo_collection="workspace",
        has_claude_md=False,
        focus_map={"workspace": "Should not surface here.", "global": "global mem"},
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "[workspace focus]" not in ctx
    assert "Should not surface here." not in ctx
    assert "No focus entry found" not in ctx


# ---------------------------------------------------------------------------
# Expired entries
# ---------------------------------------------------------------------------

def _make_expired_entry(id: str, text: str, expires_at: float) -> MagicMock:
    e = MagicMock()
    e.id = id
    e.text = text
    e.metadata = {"expires_at": str(expires_at)}
    return e


def test_expired_entries_appear_in_output(tmp_path: Path) -> None:
    """Expired entries must appear as [ai-mem expired] block."""
    entry = _make_expired_entry("todo_sprint", "Finish BLE refactor before team meeting", expires_at=1000.0)
    out = _run_main(
        tmp_path,
        focus_map={"global": "global mem"},
        repo_collection="repo.ai-mem",
        expired_entries=[entry],
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "[ai-mem expired]" in ctx
    assert "⏰" in ctx
    assert "todo_sprint" in ctx


def test_no_expired_block_when_none_expired(tmp_path: Path) -> None:
    """No [ai-mem expired] block when all entries are current."""
    out = _run_main(
        tmp_path,
        focus_map={"global": "global mem"},
        repo_collection="repo.ai-mem",
        expired_entries=[],
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "[ai-mem expired]" not in ctx


def test_expired_entry_text_truncated(tmp_path: Path) -> None:
    """Expired entry text must be truncated to _EXPIRED_PREVIEW_CHARS."""
    long_text = "X" * 300
    entry = _make_expired_entry("todo_long", long_text, expires_at=1000.0)
    out = _run_main(
        tmp_path,
        focus_map={"global": "global mem"},
        repo_collection="repo.ai-mem",
        expired_entries=[entry],
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert long_text not in ctx
    assert "…" in ctx


def test_expired_entries_capped_at_max(tmp_path: Path) -> None:
    """At most _EXPIRED_MAX expired entries must appear."""
    entries = [_make_expired_entry(f"todo_{i}", f"Entry {i}", expires_at=float(i)) for i in range(6)]
    out = _run_main(
        tmp_path,
        focus_map={"global": "global mem"},
        repo_collection="repo.ai-mem",
        expired_entries=entries,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    # Only _EXPIRED_MAX = 3 entries should appear
    assert ctx.count("⏰") == hook._EXPIRED_MAX


def test_expired_entries_helper_filters_by_now(tmp_path: Path) -> None:
    """_expired_entries returns only entries whose expires_at < now_ts."""
    mock_repo = MagicMock()
    past = _make_expired_entry("old", "past entry", expires_at=1000.0)
    future = _make_expired_entry("new", "future entry", expires_at=9_999_999_999.0)
    no_ttl = MagicMock()
    no_ttl.metadata = {}
    mock_repo.get_all.return_value = [past, future, no_ttl]

    result = hook._expired_entries(mock_repo, "repo.ai-mem", now_ts=2000.0)

    assert len(result) == 1
    assert result[0].id == "old"


def test_expired_block_shown_for_workspace_collection_with_claude_md(tmp_path: Path) -> None:
    """CLAUDE.md at the workspace root → collection is still 'workspace' but
    has_claude_md is True. Distinguishes the ctx.collection expired lookup from
    the unconditional GLOBAL_COLLECTION lookup by only seeding entries under
    'workspace': with the old collection-based gate this scope's own expired
    entries would never be fetched at all."""
    entry = _make_expired_entry("todo_root", "Root-scope task that expired", expires_at=1000.0)
    out = _run_main(
        tmp_path,
        focus_map={"global": "global mem"},
        repo_collection="workspace",
        has_claude_md=True,
        expired_entries_by_collection={"workspace": [entry], "global": []},
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "[ai-mem expired]" in ctx
    assert "todo_root" in ctx


# ---------------------------------------------------------------------------
# Pull-based default (2026-09-16): session_start_verbose defaults to False,
# so SessionStart announces routing only -- no focus text, [available] lists,
# expired warnings, session deltas, or git commits get pushed automatically.
# ---------------------------------------------------------------------------

def test_default_is_non_verbose_routing_only(tmp_path: Path) -> None:
    """With no agents.yaml override, only the Active collection line appears --
    focus text, though present in the mocked data, is never pulled into the output."""
    out = _run_main(
        tmp_path,
        focus_map={"repo.ai-mem": "repo focus text", "global": "global focus text"},
        repo_collection="repo.ai-mem",
        has_claude_md=True,
        verbose=False,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert 'Active collection: "repo.ai-mem"' in ctx
    assert "repo focus text" not in ctx
    assert "global focus text" not in ctx
    assert "[available]" not in ctx
    assert "focus]" not in ctx


def test_non_verbose_still_names_expert_collection(tmp_path: Path) -> None:
    """Routing to a subagent's own collection is not "content" -- it's the wiring a
    self-directed agent needs to store its own learnings, so it stays on by default."""
    out = _run_main(
        tmp_path,
        agent_type="the-coder",
        repo_collection="repo.ai-mem",
        has_claude_md=True,
        verbose=False,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert 'Expert collection: "subagent.the-coder"' in ctx
    assert "expertise" not in ctx
    assert "Relevant past learnings" not in ctx


def test_non_verbose_silent_when_no_claude_md_and_no_agent_type(tmp_path: Path) -> None:
    """No routing to announce and no subagent collection -> nothing is printed at all,
    matching the silent-on-failure convention other hooks follow."""
    out = _run_main(
        tmp_path,
        agent_type=None,
        has_claude_md=False,
        verbose=False,
    )

    assert out == ""


def test_verbose_true_restores_full_push_behavior(tmp_path: Path) -> None:
    """session_start_verbose: true in agents.yaml opts back into the pre-2026-09-16
    behavior -- focus text included -- for workflows that want the push."""
    out = _run_main(
        tmp_path,
        focus_map={"repo.ai-mem": "repo focus text"},
        repo_collection="repo.ai-mem",
        has_claude_md=True,
        verbose=True,
    )

    parsed = json.loads(out)
    ctx = parsed["hookSpecificOutput"]["additionalContext"]
    assert "repo focus text" in ctx


# ---------------------------------------------------------------------------
# Records pointer (2026-10-04): replaces the pushed experience index with one line
# naming docs/records/ and the librarian; the default path touches no storage.
# ---------------------------------------------------------------------------

def _with_records(tmp_path: Path, focus: bool = True) -> Path:
    root = tmp_path / "repo"
    (root / "docs" / "records").mkdir(parents=True)
    if focus:
        (root / "docs" / "records" / "FOCUS.md").write_text("focus\n")
    return root


def test_records_pointer_names_focus_index_and_librarian(tmp_path: Path) -> None:
    root = _with_records(tmp_path)
    out = _run_main(tmp_path / "db", repo_collection="repo.x", has_claude_md=True, verbose=False, git_root=root)
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert ctx.index('Active collection: "repo.x"') < ctx.index("Records: ")
    assert str(root / "docs" / "records") in ctx
    assert "FOCUS.md" in ctx and "INDEX.md" in ctx and "librarian" in ctx
    assert "experience index" not in ctx


def test_records_pointer_omits_focus_when_no_focus_file(tmp_path: Path) -> None:
    root = _with_records(tmp_path, focus=False)
    out = _run_main(tmp_path / "db", repo_collection="repo.x", has_claude_md=True, verbose=False, git_root=root)
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "Records: " in ctx and "FOCUS.md" not in ctx


def test_no_records_pointer_without_records_dir(tmp_path: Path) -> None:
    out = _run_main(tmp_path / "db", repo_collection="repo.x", has_claude_md=True, verbose=False, git_root=tmp_path)
    assert "Records: " not in json.loads(out)["hookSpecificOutput"]["additionalContext"]


def test_no_records_pointer_without_claude_md(tmp_path: Path) -> None:
    root = _with_records(tmp_path)
    out = _run_main(tmp_path / "db", has_claude_md=False, verbose=False, git_root=root)
    assert out == ""


def test_default_mode_never_builds_the_repository(tmp_path: Path) -> None:
    chroma = MagicMock()
    root = _with_records(tmp_path)
    out = _run_main(tmp_path / "db", repo_collection="repo.x", has_claude_md=True, verbose=False,
                    chroma_cls=chroma, git_root=root)
    chroma.assert_not_called()
    assert 'Active collection: "repo.x"' in json.loads(out)["hookSpecificOutput"]["additionalContext"]


def test_repo_construction_failure_keeps_routing_line(tmp_path: Path) -> None:
    """A locked or broken database must not cost the agent its collection routing."""
    out = _run_main(
        tmp_path, repo_collection="repo.x", has_claude_md=True, verbose=False,
        chroma_cls=MagicMock(side_effect=RuntimeError("chroma db locked")),
    )
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert 'Active collection: "repo.x"' in ctx and "experience index" not in ctx


def test_repo_construction_failure_in_verbose_mode_falls_back_to_routing(tmp_path: Path) -> None:
    out = _run_main(
        tmp_path, repo_collection="repo.x", has_claude_md=True, verbose=True,
        chroma_cls=MagicMock(side_effect=RuntimeError("chroma db locked")),
    )
    assert 'Active collection: "repo.x"' in json.loads(out)["hookSpecificOutput"]["additionalContext"]


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
    out = _run_main(db, repo_collection="repo.x", has_claude_md=True, verbose=False)
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    lines = ctx.splitlines()
    assert lines[0] == "[ai-mem]" and lines[1] == hook.GUARD_MESSAGE
    assert 'Active collection: "repo.x"' in ctx


def test_no_guard_line_once_migrated(tmp_path: Path) -> None:
    db = _chroma_store(tmp_path / "db", sentinel=True)
    out = _run_main(db, repo_collection="repo.x", has_claude_md=True, verbose=False)
    assert "upgrade pending" not in out


def test_guard_line_alone_outside_any_project(tmp_path: Path) -> None:
    db = _chroma_store(tmp_path / "db", sentinel=False)
    out = _run_main(db, has_claude_md=False, verbose=False)
    assert json.loads(out)["hookSpecificOutput"]["additionalContext"] == "[ai-mem]\n" + hook.GUARD_MESSAGE


def test_guard_check_failure_never_raises(tmp_path: Path) -> None:
    with patch.object(hook, "migration_pending", side_effect=OSError("boom")):
        out = _run_main(tmp_path, repo_collection="repo.x", has_claude_md=True, verbose=False)
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert 'Active collection: "repo.x"' in ctx and "upgrade pending" not in ctx


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
