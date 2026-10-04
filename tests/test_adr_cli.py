"""Tests for the mem-adr-sync CLI: export/import round trip between Chroma and Markdown."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from ai_mem.adr_cli import _cmd_export, _cmd_import, _cmd_reindex, main
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.boost_confidence import BoostConfidenceUseCase
from ai_mem.infrastructure.adr_paths import record_collection_root
from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository


def _export_args(collection: str | None, db_path: Path) -> argparse.Namespace:
    return argparse.Namespace(collection=collection, db_path=str(db_path))


def _import_args(collection: str, db_path: Path) -> argparse.Namespace:
    return argparse.Namespace(collection=collection, db_path=str(db_path))


def _reindex_args(collection: str, db_path: Path) -> argparse.Namespace:
    return argparse.Namespace(collection=collection, db_path=str(db_path))


@pytest.fixture
def wired(tmp_path):
    """A db_path + repo_root pair, with the collection->root mapping already recorded."""
    db_path = tmp_path / "db"
    repo_root = tmp_path / "repo"
    collection = "repo.example"
    record_collection_root(db_path, collection, repo_root)
    repo = ChromaMemoryRepository(db_path)
    return argparse.Namespace(db_path=db_path, repo_root=repo_root, collection=collection, repo=repo)


def test_export_writes_file_with_correct_content(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_example"],
        metadatas=[{"type": "domain"}],
    )

    rc = _cmd_export(_export_args(wired.collection, wired.db_path))

    assert rc == 0
    adr_file = wired.repo_root / "docs" / "records" / "general" / "decisions" / "domain_example.md"
    assert adr_file.exists()
    content = adr_file.read_text()
    assert "id: domain_example" in content
    assert "type: domain" in content
    assert "Decision: use X." in content


def test_export_writes_todo_under_todos_kind(wired):
    AddMemoryUseCase(wired.repo).execute(wired.collection, ["open work"], ["todo_example"], metadatas=[{"type": "todo"}])

    _cmd_export(_export_args(wired.collection, wired.db_path))

    assert (wired.repo_root / "docs" / "records" / "general" / "todos" / "todo_example.md").exists()


def test_focus_roundtrip_via_focus_md(wired):
    AddMemoryUseCase(wired.repo).execute(wired.collection, ["Fokus: X"], ["current_focus"], metadatas=[{"type": "project"}])

    _cmd_export(_export_args(wired.collection, wired.db_path))
    assert (wired.repo_root / "docs" / "records" / "FOCUS.md").read_text() == "Fokus: X\n"

    fresh_db_path = wired.db_path.parent / "fresh_db"
    record_collection_root(fresh_db_path, wired.collection, wired.repo_root)
    rc = _cmd_import(_import_args(wired.collection, fresh_db_path))

    assert rc == 0
    [focus] = ChromaMemoryRepository(fresh_db_path).get_by_ids(wired.collection, ["current_focus"])
    assert focus.text == "Fokus: X"
    assert focus.metadata["type"] == "project"


def test_export_skips_untyped_and_unknown_types(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(wired.collection, ["a"], ["untyped_example"], metadatas=[{"source": "x"}])
    add_memory.execute(wired.collection, ["b"], ["scratch_example"], metadatas=[{"type": "scratch"}])

    _cmd_export(_export_args(wired.collection, wired.db_path))

    adr_dir = wired.repo_root / "docs" / "records"
    assert not adr_dir.exists() or not any(adr_dir.iterdir())


def test_import_produces_identical_text_and_created_at(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_example"],
        metadatas=[{"type": "domain"}],
    )
    original = wired.repo.get_by_ids(wired.collection, ["domain_example"])[0]
    _cmd_export(_export_args(wired.collection, wired.db_path))

    fresh_db_path = wired.db_path.parent / "fresh_db"
    record_collection_root(fresh_db_path, wired.collection, wired.repo_root)
    fresh_repo = ChromaMemoryRepository(fresh_db_path)

    rc = _cmd_import(_import_args(wired.collection, fresh_db_path))

    assert rc == 0
    [imported] = fresh_repo.get_by_ids(wired.collection, ["domain_example"])
    assert imported.text == original.text
    assert imported.metadata["type"] == original.metadata["type"]
    assert imported.metadata["created_at"] == original.metadata["created_at"]


def test_roundtrip_export_delete_import_restores_entry(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_example"],
        metadatas=[{"type": "domain"}],
    )
    original = wired.repo.get_by_ids(wired.collection, ["domain_example"])[0]
    _cmd_export(_export_args(wired.collection, wired.db_path))

    wired.repo.delete(wired.collection, ["domain_example"])
    assert wired.repo.get_by_ids(wired.collection, ["domain_example"]) == []

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc == 0
    [restored] = wired.repo.get_by_ids(wired.collection, ["domain_example"])
    assert restored.text == original.text
    assert restored.metadata["created_at"] == original.metadata["created_at"]


def test_second_import_does_not_overwrite_boosted_boost_count(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_example"],
        metadatas=[{"type": "domain"}],
    )
    _cmd_export(_export_args(wired.collection, wired.db_path))

    boost = BoostConfidenceUseCase(wired.repo)
    boost.execute(wired.collection, ["domain_example"], cue="when deciding X")
    boosted_count = wired.repo.get_by_ids(wired.collection, ["domain_example"])[0].metadata["boost_count"]

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc == 0
    after_import = wired.repo.get_by_ids(wired.collection, ["domain_example"])[0]
    assert after_import.metadata["boost_count"] == boosted_count


def test_import_restores_cue_from_file(wired):
    AddMemoryUseCase(wired.repo).execute(
        wired.collection, ["Decision: use X."], ["domain_example"], metadatas=[{"type": "domain", "cue": "when deciding X"}]
    )
    _cmd_export(_export_args(wired.collection, wired.db_path))

    fresh_db_path = wired.db_path.parent / "fresh_db"
    record_collection_root(fresh_db_path, wired.collection, wired.repo_root)
    assert _cmd_import(_import_args(wired.collection, fresh_db_path)) == 0

    [restored] = ChromaMemoryRepository(fresh_db_path).get_by_ids(wired.collection, ["domain_example"])
    assert restored.metadata["cue"] == "when deciding X"


def test_import_skips_malformed_file_reports_it_and_continues(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_good"],
        metadatas=[{"type": "domain"}],
    )
    _cmd_export(_export_args(wired.collection, wired.db_path))

    adr_dir = wired.repo_root / "docs" / "records"
    broken_file = adr_dir / "domain_broken.md"
    broken_file.write_text("not valid frontmatter at all")

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc != 0
    assert wired.repo.get_by_ids(wired.collection, ["domain_good"]) != []


def test_import_missing_adr_dir_returns_nonzero(tmp_path):
    db_path = tmp_path / "db"
    args = _import_args("repo.nowhere", db_path)

    rc = _cmd_import(args)

    assert rc == 1


def test_cli_help_lists_all_subcommands(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["mem-adr-sync", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "export" in out
    assert "import" in out
    assert "reindex" in out


def test_export_regenerates_index(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_example"],
        metadatas=[{"type": "domain"}],
    )

    _cmd_export(_export_args(wired.collection, wired.db_path))

    index_file = wired.repo_root / "docs" / "records" / "INDEX.md"
    assert index_file.exists()
    assert "domain_example" in index_file.read_text()


def test_reindex_regenerates_index_from_existing_files(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_example"],
        metadatas=[{"type": "domain"}],
    )
    _cmd_export(_export_args(wired.collection, wired.db_path))
    index_file = wired.repo_root / "docs" / "records" / "INDEX.md"
    index_file.unlink()

    rc = _cmd_reindex(_reindex_args(wired.collection, wired.db_path))

    assert rc == 0
    assert index_file.exists()
    assert "domain_example" in index_file.read_text()


def test_reindex_missing_adr_dir_returns_nonzero(tmp_path):
    db_path = tmp_path / "db"
    args = _reindex_args("repo.nowhere", db_path)

    rc = _cmd_reindex(args)

    assert rc == 1


def test_import_ignores_readme_and_succeeds(wired):
    AddMemoryUseCase(wired.repo).execute(
        wired.collection, ["Decision: use X."], ["domain_good"], metadatas=[{"type": "domain"}]
    )
    _cmd_export(_export_args(wired.collection, wired.db_path))
    adr_dir = wired.repo_root / "docs" / "records"
    (adr_dir / "README.md").write_text("# Decision records\n\nHandwritten, no frontmatter.\n")

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc == 0


def _add(wired, entry_id, entry_type="domain", **meta):
    AddMemoryUseCase(wired.repo).execute(
        wired.collection, ["Decision: use X."], [entry_id], metadatas=[{"type": entry_type, **meta}]
    )


def test_export_uses_area_and_kind_subfolders(wired):
    _add(wired, "domain_a", area="billing")
    _add(wired, "learning_b", "learning")

    _cmd_export(_export_args(wired.collection, wired.db_path))

    records = wired.repo_root / "docs" / "records"
    assert (records / "billing" / "decisions" / "domain_a.md").exists()
    assert (records / "general" / "learnings" / "learning_b.md").exists()


def test_export_removes_stale_duplicate_after_area_change(wired):
    _add(wired, "domain_a")
    _cmd_export(_export_args(wired.collection, wired.db_path))
    old = wired.repo_root / "docs" / "records" / "general" / "decisions" / "domain_a.md"
    assert old.exists()

    entry = wired.repo.get_by_ids(wired.collection, ["domain_a"])[0]
    entry.metadata["area"] = "billing"
    wired.repo.upsert(wired.collection, [entry])
    _cmd_export(_export_args(wired.collection, wired.db_path))

    assert not old.exists()
    assert (wired.repo_root / "docs" / "records" / "billing" / "decisions" / "domain_a.md").exists()


def test_import_restores_area_recursively_and_defaults_general(wired):
    _add(wired, "domain_a", area="billing")
    _add(wired, "domain_b")
    _cmd_export(_export_args(wired.collection, wired.db_path))
    wired.repo.delete(wired.collection, ["domain_a", "domain_b"])

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc == 0
    assert wired.repo.get_by_ids(wired.collection, ["domain_a"])[0].metadata["area"] == "billing"
    assert wired.repo.get_by_ids(wired.collection, ["domain_b"])[0].metadata["area"] == "general"


def test_import_warns_on_misplaced_file_but_imports(wired, capsys):
    _add(wired, "domain_a", area="billing")
    _cmd_export(_export_args(wired.collection, wired.db_path))
    records = wired.repo_root / "docs" / "records"
    moved = records / "elsewhere" / "domain_a.md"
    moved.parent.mkdir()
    (records / "billing" / "decisions" / "domain_a.md").rename(moved)
    wired.repo.delete(wired.collection, ["domain_a"])

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc == 0
    assert "does not match its expected location" in capsys.readouterr().err
    assert wired.repo.get_by_ids(wired.collection, ["domain_a"]) != []


def test_import_skips_only_top_level_index_and_readme(wired):
    _add(wired, "domain_a")
    _cmd_export(_export_args(wired.collection, wired.db_path))
    nested = wired.repo_root / "docs" / "records" / "general" / "decisions" / "README.md"
    nested.write_text("no frontmatter")

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc != 0


@pytest.mark.parametrize(("entry_type", "kind"), [("todo", "todos"), ("user", "user")])
def test_roundtrip_restores_todo_and_user_types(wired, entry_type, kind):
    _add(wired, "entry_x", entry_type)
    _cmd_export(_export_args(wired.collection, wired.db_path))
    assert (wired.repo_root / "docs" / "records" / "general" / kind / "entry_x.md").exists()

    wired.repo.delete(wired.collection, ["entry_x"])
    assert _cmd_import(_import_args(wired.collection, wired.db_path)) == 0

    [restored] = wired.repo.get_by_ids(wired.collection, ["entry_x"])
    assert restored.metadata["type"] == entry_type
    assert restored.text == "Decision: use X."


def test_export_and_import_roundtrip_for_rootless_collection(tmp_path, monkeypatch):
    home = tmp_path / "records"
    home.mkdir()
    monkeypatch.setenv("AI_MEM_RECORDS_HOME", str(home))
    db_path = tmp_path / "db"
    repo = ChromaMemoryRepository(db_path)
    AddMemoryUseCase(repo).execute("global", ["Rule: x"], ["pattern_g"], metadatas=[{"type": "pattern"}])
    AddMemoryUseCase(repo).execute("subagent.the-coder", ["no"], ["learning_s"], metadatas=[{"type": "learning"}])

    _cmd_export(_export_args(None, db_path))

    assert (home / "global" / "docs" / "records" / "general" / "decisions" / "pattern_g.md").exists()
    assert (home / "subagent.the-coder" / "docs" / "records" / "general" / "learnings" / "learning_s.md").exists()

    repo.delete("global", ["pattern_g"])
    assert _cmd_import(_import_args("global", db_path)) == 0
    assert repo.get_by_ids("global", ["pattern_g"])[0].text == "Rule: x"
