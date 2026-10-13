"""Tests for the mem-adr-sync CLI: reindex and the records_v1 migration."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from ai_mem.adr_cli import _cmd_migrate, _cmd_reindex, main
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_paths import record_collection_root
from tests.chroma_store import ChromaStore


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
    assert "reindex" in out and "migrate" in out
    assert "export" not in out and "import" not in out


def test_reindex_regenerates_index_from_existing_files(wired):
    index_file = wired.repo_root / "docs" / "records" / "INDEX.md"
    assert not index_file.exists()

    rc = _cmd_reindex(_reindex_args(wired.collection, wired.db_path))

    assert rc == 0
    assert "domain_example" in index_file.read_text()


def test_reindex_missing_adr_dir_returns_nonzero(tmp_path):
    assert _cmd_reindex(_reindex_args("repo.nowhere", tmp_path / "db")) == 1


# ---------------------------------------------------------------------------
# migrate: records_v1.done only after a clean apply
# ---------------------------------------------------------------------------

@pytest.fixture
def migratable(tmp_path):
    """A Chroma store with one placeable collection (repo.alpha under a scanned workspace)."""
    ws = tmp_path / "ws"
    (ws / "alpha").mkdir(parents=True)
    (ws / "alpha" / "CLAUDE.md").write_text("# alpha\n")
    db_path = tmp_path / "db"
    repo = ChromaStore(db_path)
    AddMemoryUseCase(repo).execute("repo.alpha", ["Decision: keep X"], ["domain_x"], metadatas=[{"type": "domain"}])
    return argparse.Namespace(db_path=db_path, ws=ws, repo=repo,
                              sentinel=db_path / ".migrations" / "records_v1.done",
                              record=ws / "alpha" / "docs" / "records" / "general" / "decisions" / "domain_x.md")


def _migrate(m, apply: bool, root: list[str] | None = None) -> int:
    return _cmd_migrate(argparse.Namespace(db_path=str(m.db_path), apply=apply, root=root, scan_root=[str(m.ws)]))


def test_migrate_clean_apply_writes_sentinel(migratable, capsys):
    assert _migrate(migratable, apply=False) == 0
    assert not migratable.sentinel.exists() and not migratable.record.exists()

    assert _migrate(migratable, apply=True) == 0
    assert migratable.sentinel.exists() and migratable.record.exists()
    assert "records_v1 marked done" in capsys.readouterr().out


def test_migrate_rerun_after_clean_apply_stays_clean(migratable):
    assert _migrate(migratable, apply=True) == 0
    migratable.sentinel.unlink()

    assert _migrate(migratable, apply=True) == 0
    assert migratable.sentinel.exists()


def test_migrate_with_unplaced_collection_applies_the_rest_and_exits_1(migratable, capsys):
    AddMemoryUseCase(migratable.repo).execute("repo.nowhere", ["lost"], ["lost_1"], metadatas=[{"type": "domain"}])

    assert _migrate(migratable, apply=False) == 0
    assert "NOT CLEAN (1 collections without a directory)" in capsys.readouterr().out

    assert _migrate(migratable, apply=True) == 1
    assert migratable.record.exists() and not migratable.sentinel.exists()
    assert "NOT marked done" in capsys.readouterr().err


def test_migrate_with_conflict_exits_1_without_sentinel(migratable):
    migratable.record.parent.mkdir(parents=True)
    migratable.record.write_text("hand-written\n")

    assert _migrate(migratable, apply=True) == 1
    assert migratable.record.read_text() == "hand-written\n" and not migratable.sentinel.exists()


def test_migrate_with_unsafe_id_exits_1_without_sentinel(migratable):
    AddMemoryUseCase(migratable.repo).execute("repo.alpha", ["evil"], ["../../x"], metadatas=[{"type": "domain"}])

    assert _migrate(migratable, apply=True) == 1
    assert not migratable.sentinel.exists()
    assert not (migratable.ws / "alpha" / "docs" / "x.md").exists() and not (migratable.ws / "x.md").exists()


def test_migrate_unreadable_store_exits_1_and_writes_nothing(tmp_path, capsys):
    db_path = tmp_path / "db"
    db_path.mkdir()
    (db_path / "chroma.sqlite3").write_bytes(b"not a database")

    rc = _cmd_migrate(argparse.Namespace(db_path=str(db_path), apply=True, root=None, scan_root=[str(tmp_path)]))

    assert rc == 1 and "Stop and ask" in capsys.readouterr().err
    assert sorted(p.name for p in db_path.iterdir()) == ["chroma.sqlite3"]


def test_migrate_without_chroma_store_is_a_no_op(tmp_path):
    db_path = tmp_path / "db"
    db_path.mkdir()

    rc = _cmd_migrate(argparse.Namespace(db_path=str(db_path), apply=True, root=None, scan_root=[str(tmp_path)]))

    assert rc == 0 and list(db_path.iterdir()) == []


def test_migrate_runs_in_a_process_without_chromadb(migratable):
    """migrate --apply end to end with chromadb unimportable (the `chroma` extra not installed)."""
    import subprocess
    import sys

    repo_root = Path(__file__).resolve().parent.parent
    code = (f"import sys; sys.modules['chromadb'] = None; sys.path.insert(0, {str(repo_root)!r}); "
            "from ai_mem.adr_cli import main; main()")
    result = subprocess.run(
        [sys.executable, "-I", "-c", code, "migrate", "--apply", "--db-path", str(migratable.db_path),
         "--scan-root", str(migratable.ws)],
        capture_output=True, text=True, cwd=migratable.ws,
    )

    assert result.returncode == 0, result.stderr
    assert migratable.sentinel.exists() and migratable.record.exists()
