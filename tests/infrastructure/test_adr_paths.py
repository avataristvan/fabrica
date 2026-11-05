"""Tests for path conventions used by ADR Markdown persistence."""
from __future__ import annotations

from pathlib import Path

from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    find_adr_files,
    iter_record_files,
    is_safe_area,
    is_safe_entry_id,
    record_file_path,
    entry_files,
    reference_file,
    reference_files,
    remove_files,
)


def test_adr_types_contains_expected_types():
    assert ADR_TYPES == frozenset({"domain", "pattern", "anti-pattern", "learning", "user"})


def test_record_file_path_shape_per_type_and_area(tmp_path):
    base = tmp_path / "docs" / "records"

    for entry_type, kind in (
        ("domain", "decisions"),
        ("pattern", "decisions"),
        ("anti-pattern", "decisions"),
        ("learning", "learnings"),
    ):
        path = record_file_path(base, "x_1", entry_type, "hooks")
        assert path == base / "hooks" / kind / "x_1.md", entry_type


def test_is_safe_entry_id_rejects_traversal_and_reserved_names():
    assert is_safe_entry_id("domain_foo_2026_09_26")
    for bad in ("", ".", "..", "../x", "a/b", "a\\b", "INDEX", "README"):
        assert not is_safe_entry_id(bad), bad


def test_record_file_path_returns_none_for_unsafe_id(tmp_path):
    assert record_file_path(tmp_path, "../escape", "domain", "general") is None


def test_record_file_path_none_for_untracked_type(tmp_path):
    assert record_file_path(tmp_path, "note_1", "scratch", "general") is None


def test_record_file_path_none_for_unsafe_area(tmp_path):
    for bad in ("", "../x", "a/b", "A", "-a", ".hidden", "a b"):
        assert record_file_path(tmp_path, "domain_1", "domain", bad) is None, bad


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


def _area_with_symlinks(tmp_path):
    """records/ with one real record, a symlinked dir and a symlinked file pointing outside."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "a.md").write_text("victim")
    records = tmp_path / "records"
    (records / "general/decisions").mkdir(parents=True)
    (records / "general/decisions/a.md").write_text("real")
    (records / "general/linked").symlink_to(outside, target_is_directory=True)
    (records / "general/decisions/b.md").symlink_to(outside / "a.md")
    return records, outside


def test_record_walk_does_not_enter_symlinked_dirs(tmp_path):
    # Bites on Python <= 3.12, where rglob followed symlinked dirs; 3.13 rglob already skips them.
    records, _ = _area_with_symlinks(tmp_path)

    # The symlinked file stays visible: lint reports it and mem move refuses it.
    assert iter_record_files(records) == [records / "general/decisions/a.md", records / "general/decisions/b.md"]
    assert find_adr_files(records, "a") == [records / "general/decisions/a.md"]


def test_remove_files_never_deletes_through_a_symlinked_folder(tmp_path):
    records, outside = _area_with_symlinks(tmp_path)

    remove_files(records, [records / "general/linked/a.md"])

    assert (outside / "a.md").read_text() == "victim"


def test_remove_files_unlinks_a_symlinked_record_not_its_target(tmp_path):
    records, outside = _area_with_symlinks(tmp_path)

    remove_files(records, [records / "general/decisions/b.md"])

    assert not (records / "general/decisions/b.md").is_symlink()
    assert (outside / "a.md").read_text() == "victim"


def test_reference_file_and_files_are_the_one_reference_doc_lookup(tmp_path):
    records = tmp_path / "docs" / "records"
    records.mkdir(parents=True)
    assert reference_files(records) == []
    reference = tmp_path / "docs" / "reference"
    (reference / "nested").mkdir(parents=True)
    (reference / "b_doc.md").write_text("b\n")
    (reference / "a_doc.md").write_text("a\n")
    (reference / "nested" / "deep.md").write_text("d\n")

    assert reference_file(records, "a_doc") == reference / "a_doc.md"
    assert reference_file(records, "missing") == reference / "missing.md"
    assert reference_file(records, "../x") is None
    assert reference_files(records) == [reference / "a_doc.md", reference / "b_doc.md"]
    assert entry_files(records, "a_doc") == [reference / "a_doc.md"]
    assert entry_files(records, "missing") == []
