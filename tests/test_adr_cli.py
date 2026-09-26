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
    adr_file = wired.repo_root / "docs" / "decisions" / "domain_example.md"
    assert adr_file.exists()
    content = adr_file.read_text()
    assert "id: domain_example" in content
    assert "type: domain" in content
    assert "Decision: use X." in content


def test_export_skips_non_adr_types(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(wired.collection, ["some feedback"], ["feedback_example"], metadatas=[{"type": "feedback"}])

    _cmd_export(_export_args(wired.collection, wired.db_path))

    adr_dir = wired.repo_root / "docs" / "decisions"
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


def test_second_import_does_not_overwrite_boosted_confidence(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_example"],
        metadatas=[{"type": "domain"}],
    )
    _cmd_export(_export_args(wired.collection, wired.db_path))

    boost = BoostConfidenceUseCase(wired.repo)
    boost.execute(wired.collection, ["domain_example"], delta=0.2)
    boosted_confidence = wired.repo.get_by_ids(wired.collection, ["domain_example"])[0].metadata["confidence"]

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc == 0
    after_import = wired.repo.get_by_ids(wired.collection, ["domain_example"])[0]
    assert after_import.metadata["confidence"] == boosted_confidence


def test_import_skips_malformed_file_reports_it_and_continues(wired):
    add_memory = AddMemoryUseCase(wired.repo)
    add_memory.execute(
        wired.collection,
        ["Decision: use X.\nWhy: Y.\nScope: Z."],
        ["domain_good"],
        metadatas=[{"type": "domain"}],
    )
    _cmd_export(_export_args(wired.collection, wired.db_path))

    adr_dir = wired.repo_root / "docs" / "decisions"
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

    index_file = wired.repo_root / "docs" / "decisions" / "INDEX.md"
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
    index_file = wired.repo_root / "docs" / "decisions" / "INDEX.md"
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
    adr_dir = wired.repo_root / "docs" / "decisions"
    (adr_dir / "README.md").write_text("# Decision records\n\nHandwritten, no frontmatter.\n")

    rc = _cmd_import(_import_args(wired.collection, wired.db_path))

    assert rc == 0
