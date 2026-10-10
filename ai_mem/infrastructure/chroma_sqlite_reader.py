"""Read a ChromaDB store's entries straight from `chroma.sqlite3`, read-only, stdlib only.

The records_v1 migration must stay runnable on installations where chromadb is not installed
(it is an optional extra), and it must never write the store.
So it does not open the store through chromadb: this module opens the SQLite file with the
`mode=ro` URI (plus `PRAGMA query_only`) and reproduces what `collection.get()` returns from
the metadata segment -- ids, documents (`chroma:document`) and metadata, in chromadb's order
(collections by id, entries by rowid).

Anything it does not recognise is an error, never a guess: missing tables or columns, more
than one metadata segment per collection, collections outside the default database, array
metadata, or writes still waiting in `embeddings_queue` that chromadb has not applied to the
metadata segment yet.
"""
from __future__ import annotations

import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from ai_mem.domain.memory import CollectionInfo, MemoryEntry

DOCUMENT_KEY = "chroma:document"
_DEFAULT_TENANT = "default_tenant"
_DEFAULT_DATABASE = "default_database"
_REQUIRED_COLUMNS = {
    "databases": {"id", "name", "tenant_id"},
    "collections": {"id", "name", "database_id"},
    "segments": {"id", "scope", "collection"},
    "embeddings": {"id", "segment_id", "embedding_id"},
    "embedding_metadata": {"id", "key", "string_value", "int_value", "float_value", "bool_value"},
}
_QUEUE_COLUMNS = {
    "embeddings_queue": {"seq_id", "topic"},
    "max_seq_id": {"segment_id", "seq_id"},
}


class ChromaSchemaError(RuntimeError):
    """The store does not look like a schema this reader knows; nothing was read or guessed."""


@dataclass
class ChromaStoreSnapshot:
    """Everything the migration reads, loaded at once; the database is closed again."""

    entries: dict[str, list[MemoryEntry]] = field(default_factory=dict)  # collection -> entries

    def list_collections(self) -> list[CollectionInfo]:
        return [CollectionInfo(name=name, count=len(items)) for name, items in self.entries.items()]

    def get_all(self, collection: str) -> list[MemoryEntry]:
        return list(self.entries.get(collection, []))


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute("SELECT * FROM pragma_table_info(?)", (table,))}


def _check_schema(conn: sqlite3.Connection) -> bool:
    """Raise on a missing required table/column; return whether the write queue can be checked."""
    for table, required in _REQUIRED_COLUMNS.items():
        missing = required - _columns(conn, table)
        if missing:
            raise ChromaSchemaError(f"unknown Chroma schema: table {table!r} lacks {sorted(missing)}")
    present = [required <= _columns(conn, table) for table, required in _QUEUE_COLUMNS.items()]
    if any(present) and not all(present):
        raise ChromaSchemaError("unknown Chroma schema: embeddings_queue and max_seq_id do not match")
    if _columns(conn, "embedding_metadata_array"):
        if conn.execute("SELECT COUNT(*) FROM embedding_metadata_array").fetchone()[0]:
            raise ChromaSchemaError("unsupported Chroma store: entries with array metadata")
    return all(present)


def _metadata_segments(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """(collection id, collection name, metadata segment id), ordered like chromadb lists them."""
    foreign = conn.execute(
        "SELECT COUNT(*) FROM collections c LEFT JOIN databases d ON d.id = c.database_id "
        "WHERE d.id IS NULL OR d.name != ? OR d.tenant_id != ?",
        (_DEFAULT_DATABASE, _DEFAULT_TENANT),
    ).fetchone()[0]
    if foreign:
        raise ChromaSchemaError(f"unsupported Chroma store: {foreign} collections outside {_DEFAULT_DATABASE}")
    rows = conn.execute(
        "SELECT c.id, c.name, s.id FROM collections c "
        "LEFT JOIN segments s ON s.collection = c.id AND s.scope = 'METADATA' ORDER BY c.id, s.id"
    ).fetchall()
    missing = sorted(name for _, name, segment_id in rows if segment_id is None)
    if missing:
        raise ChromaSchemaError(f"unknown Chroma schema: no metadata segment for {missing}")
    per_collection = Counter(collection_id for collection_id, _, _ in rows)
    doubled = sorted({name for collection_id, name, _ in rows if per_collection[collection_id] > 1})
    if doubled:
        raise ChromaSchemaError(f"unknown Chroma schema: several metadata segments for {doubled}")
    return rows


def _check_queue_applied(conn: sqlite3.Connection, segments: list[tuple[str, str, str]]) -> None:
    applied = dict(conn.execute("SELECT segment_id, seq_id FROM max_seq_id").fetchall())
    queued: dict[str, int] = {}
    for topic, seq_id in conn.execute("SELECT topic, MAX(seq_id) FROM embeddings_queue GROUP BY topic"):
        queued[str(topic).rsplit("/", 1)[-1]] = seq_id
    for collection_id, name, segment_id in segments:
        last_queued, last_applied = queued.get(collection_id), applied.get(segment_id, 0)
        if last_queued is None:
            continue
        if not isinstance(last_queued, int) or not isinstance(last_applied, int):
            raise ChromaSchemaError("unknown Chroma schema: seq_id is not an integer")
        if last_queued > last_applied:
            raise ChromaSchemaError(
                f"collection {name!r} has writes in embeddings_queue that are not applied yet "
                f"(queued up to {last_queued}, applied up to {last_applied})"
            )


def _value(string_value, int_value, float_value, bool_value):
    # Same precedence as chromadb's SqliteMetadataSegment._record.
    if string_value is not None:
        return string_value
    if int_value is not None:
        return int_value
    if float_value is not None:
        return float_value
    if bool_value is not None:
        return bool_value == 1
    return None


def _entries(conn: sqlite3.Connection, segment_id: str) -> list[MemoryEntry]:
    rows = conn.execute(
        "SELECT e.id, e.embedding_id, m.key, m.string_value, m.int_value, m.float_value, m.bool_value "
        "FROM embeddings e LEFT JOIN embedding_metadata m ON m.id = e.id "
        "WHERE e.segment_id = ? ORDER BY e.id",
        (segment_id,),
    )
    entries: list[MemoryEntry] = []
    current_rowid = None
    document = None
    metadata: dict = {}
    for rowid, embedding_id, key, *values in rows:
        if rowid != current_rowid:
            if current_rowid is not None:
                entries.append(MemoryEntry(id=entry_id, text=document, metadata=metadata))
            current_rowid, entry_id, document, metadata = rowid, embedding_id, None, {}
        if key is None:
            continue
        value = _value(*values)
        if value is None:
            continue
        if key == DOCUMENT_KEY:
            document = value
        else:
            metadata[key] = value
    if current_rowid is not None:
        entries.append(MemoryEntry(id=entry_id, text=document, metadata=metadata))
    return entries


def read_chroma_store(db_path: Path) -> ChromaStoreSnapshot:
    """Load every collection of `<db_path>/chroma.sqlite3` without ever opening it writable.

    Raises FileNotFoundError when there is no store file, ChromaSchemaError on anything
    unrecognised, sqlite3.Error when SQLite itself cannot read the file.
    """
    sqlite_file = (db_path / "chroma.sqlite3").resolve()
    if not sqlite_file.is_file():
        raise FileNotFoundError(sqlite_file)
    conn = sqlite3.connect(f"{sqlite_file.as_uri()}?mode=ro", uri=True)
    try:
        conn.execute("PRAGMA query_only = ON")
        # One read transaction: a still-running old MCP server may write meanwhile, and the
        # queue check and the entry reads must see the same state.
        conn.execute("BEGIN")
        queue_checkable = _check_schema(conn)
        segments = _metadata_segments(conn)
        if queue_checkable:
            _check_queue_applied(conn, segments)
        return ChromaStoreSnapshot({name: _entries(conn, segment_id) for _, name, segment_id in segments})
    finally:
        conn.close()
