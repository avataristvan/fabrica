"""Upgrade guard: is this installation still on ChromaDB without the records_v1 migration?

Stdlib only -- the SessionStart hook and the `mem` CLI ask this before anything else, also on
an installation where chromadb is not (or no longer) installed. The sentinel is the same file
`install.py` and `mem-adr-sync migrate --apply` write.
"""
from __future__ import annotations

from pathlib import Path

CHROMA_SQLITE = "chroma.sqlite3"
MIGRATIONS_DIRNAME = ".migrations"
RECORDS_V1_SENTINEL = "records_v1.done"
GUARD_MESSAGE = (
    "ai-mem upgrade pending: this installation still keeps memory in ChromaDB and has not run the "
    "records_v1 migration. Follow UPGRADING.md in the ai-mem checkout before using ai-mem."
)


class MigrationPending(RuntimeError):
    def __init__(self) -> None:
        super().__init__(GUARD_MESSAGE)


def migrations_dir(db_path: Path) -> Path:
    return db_path / MIGRATIONS_DIRNAME


def records_v1_sentinel(db_path: Path) -> Path:
    return migrations_dir(db_path) / RECORDS_V1_SENTINEL


def migration_pending(db_path: Path) -> bool:
    """True when a Chroma store exists in `db_path` and records_v1 has not been marked done."""
    return (db_path / CHROMA_SQLITE).is_file() and not records_v1_sentinel(db_path).exists()


def refuse_if_pending(db_path: Path) -> None:
    if migration_pending(db_path):
        raise MigrationPending()


def mark_records_v1_done(db_path: Path) -> Path:
    sentinel = records_v1_sentinel(db_path)
    sentinel.parent.mkdir(parents=True, exist_ok=True)
    sentinel.touch()
    return sentinel
