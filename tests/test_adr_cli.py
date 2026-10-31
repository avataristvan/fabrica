"""Tests for the mem-adr-sync CLI: reindex."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from ai_mem.adr_cli import _cmd_reindex, main
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_paths import record_collection_root


def _reindex_args(collection: str, db_path: Path) -> argparse.Namespace:
    return argparse.Namespace(collection=collection, db_path=str(db_path))


@pytest.fixture
def wired(tmp_path):
    """A db_path + repo_root pair, with the collection->root mapping already recorded and one record file."""
    db_path = tmp_path / "db"
    repo_root = tmp_path / "repo"
    collection = "repo.example"
    record_collection_root(db_path, collection, repo_root)
    record = repo_root / "docs" / "records" / "general" / "decisions" / "domain_example.md"
    record.parent.mkdir(parents=True)
    record.write_text(adr_markdown.serialize("domain_example", "domain", "Decision: use X.\nWhy: Y.\nScope: Z.", {"type": "domain"}))
    return argparse.Namespace(db_path=db_path, repo_root=repo_root, collection=collection)


def test_cli_help_lists_the_subcommands(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["mem-adr-sync", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "reindex" in out and "migrate" not in out
    assert "export" not in out and "import" not in out


def test_reindex_regenerates_index_from_existing_files(wired):
    index_file = wired.repo_root / "docs" / "records" / "INDEX.md"
    assert not index_file.exists()

    rc = _cmd_reindex(_reindex_args(wired.collection, wired.db_path))

    assert rc == 0
    assert "domain_example" in index_file.read_text()


def test_reindex_missing_adr_dir_returns_nonzero(tmp_path):
    assert _cmd_reindex(_reindex_args("repo.nowhere", tmp_path / "db")) == 1
