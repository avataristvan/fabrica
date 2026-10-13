"""Tests for the upgrade guard (Chroma store without the records_v1 sentinel)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from unittest.mock import patch

from ai_mem.upgrade_guard import (
    GUARD_MESSAGE,
    MigrationPending,
    mark_records_v1_done,
    migration_pending,
    records_v1_sentinel,
    refuse_if_pending,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _store(tmp_path: Path, sqlite: bool, sentinel: bool) -> Path:
    db_path = tmp_path / "db"
    db_path.mkdir()
    if sqlite:
        (db_path / "chroma.sqlite3").write_bytes(b"")
    if sentinel:
        mark_records_v1_done(db_path)
    return db_path


@pytest.mark.parametrize(("sqlite", "sentinel", "pending"), [
    (False, False, False),
    (False, True, False),
    (True, False, True),
    (True, True, False),
])
def test_guard_matrix(tmp_path, sqlite, sentinel, pending):
    db_path = _store(tmp_path, sqlite, sentinel)

    assert migration_pending(db_path) is pending


def test_missing_db_path_is_not_pending(tmp_path):
    assert migration_pending(tmp_path / "absent") is False


def test_refuse_if_pending_raises_with_the_guard_message(tmp_path):
    db_path = _store(tmp_path, sqlite=True, sentinel=False)

    with pytest.raises(MigrationPending, match="UPGRADING.md"):
        refuse_if_pending(db_path)

    mark_records_v1_done(db_path)
    refuse_if_pending(db_path)


def test_sentinel_is_the_file_install_py_uses(tmp_path):
    import install

    assert records_v1_sentinel(tmp_path) == tmp_path / ".migrations" / "records_v1.done"
    assert not hasattr(install, "MIGRATIONS_DIR")  # install.py asks upgrade_guard instead of defining the path again
    with patch.object(install, "DB_PATH", tmp_path / "no-store"):
        install.run_records_migration()
    assert records_v1_sentinel(tmp_path / "no-store").exists()


def test_guard_message_is_one_line_naming_upgrading_md():
    assert "\n" not in GUARD_MESSAGE and "UPGRADING.md" in GUARD_MESSAGE


_NO_CHROMA_IMPORT = """
import sys
sys.modules['chromadb'] = None  # any import of chromadb now raises ImportError
sys.modules['mcp'] = None
sys.path.insert(0, {root!r})
import ai_mem.upgrade_guard, ai_mem.adr_cli, ai_mem.hook
assert ai_mem.hook.build_repository is not None
assert ai_mem.hook.detect_repo_context is not None
assert ai_mem.hook.migration_pending is not None
loaded = sorted(m for m in sys.modules if m.split('.')[0] in ('chromadb', 'mcp') and sys.modules[m] is not None)
assert not loaded, loaded
"""


def test_guard_cli_and_hook_import_without_chromadb_or_mcp():
    result = subprocess.run([sys.executable, "-I", "-c", _NO_CHROMA_IMPORT.format(root=str(REPO_ROOT))],
                            capture_output=True, text=True)

    assert result.returncode == 0, result.stderr


def test_server_imports_without_chromadb(tmp_path):
    shim = (f"import sys; sys.modules['chromadb'] = None; sys.path.insert(0, {str(REPO_ROOT)!r}); "
            "import ai_mem.server")
    result = subprocess.run([sys.executable, "-I", "-c", shim], capture_output=True, text=True, cwd=tmp_path,
                            env={"AI_MEM_PATH": str(tmp_path / "db"), "AI_MEM_ADR_DISABLED": "1",
                                 "HOME": str(tmp_path), "PATH": "/usr/bin:/bin"})

    assert result.returncode == 0, result.stderr
