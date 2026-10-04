"""Tests for repo-root resolution and path conventions used by ADR Markdown persistence."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    records_home,
    adr_dir_for,
    adr_file_path,
    find_adr_files,
    is_safe_area,
    is_safe_entry_id,
    record_collection_root,
    resolve_repo_root_for_collection,
)
from ai_mem.repo_context import RepoContext


def test_adr_types_contains_expected_types():
    assert ADR_TYPES == frozenset({"domain", "pattern", "anti-pattern", "learning", "todo", "user"})


def test_rootless_collections_none_without_records_home(tmp_path):
    assert resolve_repo_root_for_collection(tmp_path, "global") is None
    assert resolve_repo_root_for_collection(tmp_path, "workspace") is None
    assert resolve_repo_root_for_collection(tmp_path, "subagent.the-coder") is None


def test_rootless_collections_resolve_below_records_home(tmp_path, monkeypatch):
    home = tmp_path / "records"
    home.mkdir()
    monkeypatch.setenv("AI_MEM_RECORDS_HOME", str(home))

    for collection in ("global", "workspace", "subagent.the-coder"):
        assert resolve_repo_root_for_collection(tmp_path, collection) == home / collection
    assert adr_dir_for(tmp_path, "global") == home / "global" / "docs" / "records"


def test_records_home_falls_back_to_workspace_root_and_requires_existing_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_MEM_WORKSPACE_ROOT", str(tmp_path))
    assert records_home() is None  # ai-mem-records/ not created yet: opt-in only

    (tmp_path / "ai-mem-records").mkdir()
    assert records_home() == tmp_path / "ai-mem-records"


def test_records_home_env_overrides_workspace_root(tmp_path, monkeypatch):
    explicit = tmp_path / "elsewhere"
    explicit.mkdir()
    monkeypatch.setenv("AI_MEM_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AI_MEM_RECORDS_HOME", str(explicit))
    assert records_home() == explicit


def test_global_and_workspace_ignore_existing_mapping(tmp_path):
    # Even if a stray mapping entry existed for these names, they must never resolve.
    record_collection_root(tmp_path, "global", tmp_path / "somewhere")
    assert resolve_repo_root_for_collection(tmp_path, "global") is None


def test_record_and_resolve_roundtrip(tmp_path):
    root = tmp_path / "my-repo"
    record_collection_root(tmp_path, "repo.my-repo", root)

    resolved = resolve_repo_root_for_collection(tmp_path, "repo.my-repo")

    assert resolved == root


def test_record_collection_root_merges_existing_entries(tmp_path):
    record_collection_root(tmp_path, "repo.a", tmp_path / "a")
    record_collection_root(tmp_path, "repo.b", tmp_path / "b")

    mapping_file = tmp_path / "adr_collection_roots.json"
    mapping = json.loads(mapping_file.read_text())

    assert mapping["repo.a"] == str(tmp_path / "a")
    assert mapping["repo.b"] == str(tmp_path / "b")


def test_record_collection_root_writes_atomically_no_tmp_leftover(tmp_path):
    record_collection_root(tmp_path, "repo.a", tmp_path / "a")

    assert not (tmp_path / "adr_collection_roots.json.tmp").exists()
    assert (tmp_path / "adr_collection_roots.json").exists()


def test_missing_mapping_file_falls_back_to_detect_repo_context(tmp_path):
    fake_root = tmp_path / "detected-repo"
    fake_ctx = RepoContext(
        scope_name="my-repo",
        collection="repo.my-repo",
        has_claude_md=True,
        claude_md_dir=fake_root,
        git_root=fake_root,
    )

    with patch("ai_mem.infrastructure.adr_paths.detect_repo_context", return_value=fake_ctx):
        resolved = resolve_repo_root_for_collection(tmp_path, "repo.my-repo")

    assert resolved == fake_root
    # A hit via detect_repo_context() must self-populate the mapping file.
    mapping = json.loads((tmp_path / "adr_collection_roots.json").read_text())
    assert mapping["repo.my-repo"] == str(fake_root)


def test_fallback_prefers_git_root_over_claude_md_dir(tmp_path):
    git_root = tmp_path / "git-root"
    claude_md_dir = tmp_path / "git-root" / "sub"
    fake_ctx = RepoContext(
        scope_name="my-repo",
        collection="repo.my-repo",
        has_claude_md=True,
        claude_md_dir=claude_md_dir,
        git_root=git_root,
    )

    with patch("ai_mem.infrastructure.adr_paths.detect_repo_context", return_value=fake_ctx):
        resolved = resolve_repo_root_for_collection(tmp_path, "repo.my-repo")

    assert resolved == git_root


def test_fallback_uses_claude_md_dir_when_no_git_root(tmp_path):
    claude_md_dir = tmp_path / "no-git-repo"
    fake_ctx = RepoContext(
        scope_name="my-repo",
        collection="repo.my-repo",
        has_claude_md=True,
        claude_md_dir=claude_md_dir,
        git_root=None,
    )

    with patch("ai_mem.infrastructure.adr_paths.detect_repo_context", return_value=fake_ctx):
        resolved = resolve_repo_root_for_collection(tmp_path, "repo.my-repo")

    assert resolved == claude_md_dir


def test_fallback_returns_none_when_collection_mismatch(tmp_path):
    fake_ctx = RepoContext(
        scope_name="other-repo",
        collection="repo.other-repo",
        has_claude_md=True,
        claude_md_dir=tmp_path / "other",
        git_root=tmp_path / "other",
    )

    with patch("ai_mem.infrastructure.adr_paths.detect_repo_context", return_value=fake_ctx):
        resolved = resolve_repo_root_for_collection(tmp_path, "repo.my-repo")

    assert resolved is None


def test_fallback_returns_none_when_no_root_available(tmp_path):
    fake_ctx = RepoContext(
        scope_name=None,
        collection="repo.my-repo",
        has_claude_md=False,
        claude_md_dir=None,
        git_root=None,
    )

    with patch("ai_mem.infrastructure.adr_paths.detect_repo_context", return_value=fake_ctx):
        resolved = resolve_repo_root_for_collection(tmp_path, "repo.my-repo")

    assert resolved is None


def test_missing_mapping_file_does_not_crash(tmp_path):
    # No adr_collection_roots.json has ever been written under this db_path.
    with patch("ai_mem.infrastructure.adr_paths.detect_repo_context") as mock_ctx:
        mock_ctx.return_value = RepoContext(None, "workspace", False, None, None)
        resolved = resolve_repo_root_for_collection(tmp_path, "repo.unknown")

    assert resolved is None


def test_adr_dir_for_appends_default_dir(tmp_path):
    root = tmp_path / "my-repo"
    record_collection_root(tmp_path, "repo.my-repo", root)

    adr_dir = adr_dir_for(tmp_path, "repo.my-repo")

    assert adr_dir == root / "docs" / "records"


def test_adr_dir_for_respects_env_override(tmp_path, monkeypatch):
    root = tmp_path / "my-repo"
    record_collection_root(tmp_path, "repo.my-repo", root)
    monkeypatch.setenv("AI_MEM_ADR_DIR", "custom/decisions")

    adr_dir = adr_dir_for(tmp_path, "repo.my-repo")

    assert adr_dir == root / "custom" / "decisions"


def test_adr_dir_for_none_when_root_unresolvable(tmp_path):
    assert adr_dir_for(tmp_path, "global") is None


def test_adr_file_path_shape_per_type_and_area(tmp_path):
    root = tmp_path / "my-repo"
    record_collection_root(tmp_path, "repo.my-repo", root)
    base = root / "docs" / "records"

    for entry_type, kind in (
        ("domain", "decisions"),
        ("pattern", "decisions"),
        ("anti-pattern", "decisions"),
        ("learning", "learnings"),
    ):
        path = adr_file_path(tmp_path, "repo.my-repo", "x_1", entry_type, "hooks")
        assert path == base / "hooks" / kind / "x_1.md", entry_type


def test_adr_file_path_none_when_root_unresolvable(tmp_path):
    assert adr_file_path(tmp_path, "workspace", "domain_example", "domain", "general") is None


def test_is_safe_entry_id_rejects_traversal_and_reserved_names():
    assert is_safe_entry_id("domain_foo_2026_09_26")
    for bad in ("", ".", "..", "../x", "a/b", "a\\b", "INDEX", "README"):
        assert not is_safe_entry_id(bad), bad


def test_adr_file_path_returns_none_for_unsafe_id(tmp_path):
    record_collection_root(tmp_path / "db", "repo.x", tmp_path / "repo")
    assert adr_file_path(tmp_path / "db", "repo.x", "../escape", "domain", "general") is None


def test_adr_file_path_none_for_untracked_type(tmp_path):
    record_collection_root(tmp_path, "repo.x", tmp_path / "repo")
    assert adr_file_path(tmp_path, "repo.x", "note_1", "scratch", "general") is None


def test_adr_file_path_none_for_unsafe_area(tmp_path):
    record_collection_root(tmp_path, "repo.x", tmp_path / "repo")
    for bad in ("", "../x", "a/b", "A", "-a", ".hidden", "a b"):
        assert adr_file_path(tmp_path, "repo.x", "domain_1", "domain", bad) is None, bad


def test_is_safe_area_accepts_slug_forms():
    for good in ("general", "ai-mem", "a_b", "0x", "hooks2"):
        assert is_safe_area(good), good


def test_find_adr_files_finds_matches_across_subfolders(tmp_path):
    for rel in ("general/decisions/a.md", "hooks/learnings/a.md", "hooks/decisions/b.md"):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x")
    (tmp_path / "a.md").write_text("flat legacy")

    found = find_adr_files(tmp_path, "a")

    assert found == sorted([tmp_path / "a.md", tmp_path / "general/decisions/a.md", tmp_path / "hooks/learnings/a.md"])


def test_find_adr_files_empty_for_unsafe_id_or_missing_dir(tmp_path):
    assert find_adr_files(tmp_path, "../a") == []
    assert find_adr_files(tmp_path / "nope", "a") == []
