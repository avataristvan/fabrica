"""mem-adr-sync CLI -- the records_v1 migration, INDEX.md rebuilds, and the Chroma round trip.

`migrate` and `reindex` need no chromadb: the migration reads the store read-only through
`chroma_sqlite_reader`. Only `export`/`import` (Chroma rollback, needs the `chroma` extra)
import ChromaMemoryRepository, lazily. Both operate on a bare ChromaMemoryRepository, never
the MarkdownAdrRepository decorator: export is a pure read, and import needs to control the
correction upsert (see _cmd_import) itself rather than have a decorator re-serialize the
very files it's reading.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.domain.memory import MemoryEdge
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import regenerate_index
from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    DEFAULT_AREA,
    FOCUS_ID,
    FOCUS_TYPE,
    adr_dir_for,
    adr_file_path,
    find_adr_files,
    focus_file_path,
    is_safe_entry_id,
    iter_record_files,
    plain_file_content,
)
from ai_mem.upgrade_guard import CHROMA_SQLITE, mark_records_v1_done

if TYPE_CHECKING:
    from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository

_DB_PATH = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local/share/ai-mem"))


def _exportable_collections(repo: ChromaMemoryRepository, db_path: Path) -> list[str]:
    names = []
    for col_info in repo.list_collections():
        name = col_info.name
        if adr_dir_for(db_path, name) is None:
            print(f"skipping {name}: could not resolve a repo root", file=sys.stderr)
            continue
        names.append(name)
    return names


def _export_collection(repo: ChromaMemoryRepository, db_path: Path, collection: str) -> int:
    adr_dir = adr_dir_for(db_path, collection)
    if adr_dir is None:
        print(f"skipping {collection}: could not resolve a repo root", file=sys.stderr)
        return 0

    entries = [entry for entry in repo.get_all(collection) if entry.metadata.get("type") in ADR_TYPES]
    if entries:
        adr_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        if not is_safe_entry_id(entry.id):
            print(f"skipping {entry.id!r}: cannot be used as an ADR filename", file=sys.stderr)
            continue
        target = adr_file_path(
            db_path, collection, entry.id, entry.metadata["type"], entry.metadata.get("area") or DEFAULT_AREA
        )
        if target is None:
            print(f"skipping {entry.id!r}: unsafe area {entry.metadata.get('area')!r}", file=sys.stderr)
            continue
        content = adr_markdown.serialize(entry.id, entry.metadata["type"], entry.text, entry.metadata)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        for stale in find_adr_files(adr_dir, entry.id):
            if stale != target:
                stale.unlink()

    focus = repo.get_by_ids(collection, [FOCUS_ID])
    if focus:
        adr_dir.mkdir(parents=True, exist_ok=True)
        focus_file_path(db_path, collection).write_text(plain_file_content(focus[0].text))

    if adr_dir.is_dir():
        regenerate_index(adr_dir)

    plural = "y" if len(entries) == 1 else "ies"
    print(f"{collection}: exported {len(entries)} entr{plural} to {adr_dir}")
    return len(entries)


def _cmd_export(args: argparse.Namespace) -> int:
    from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository

    db_path = Path(args.db_path) if args.db_path else _DB_PATH
    repo = ChromaMemoryRepository(db_path)

    if args.collection:
        _export_collection(repo, db_path, args.collection)
        return 0

    for name in _exportable_collections(repo, db_path):
        _export_collection(repo, db_path, name)
    return 0


def _cmd_import(args: argparse.Namespace) -> int:
    from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository

    db_path = Path(args.db_path) if args.db_path else _DB_PATH
    repo = ChromaMemoryRepository(db_path)
    add_memory = AddMemoryUseCase(repo)

    adr_dir = adr_dir_for(db_path, args.collection)
    if adr_dir is None or not adr_dir.is_dir():
        print(f"no ADR directory found for collection {args.collection!r}", file=sys.stderr)
        return 1

    skipped: list[str] = []
    imported = 0
    for file_path in iter_record_files(adr_dir):
        try:
            parsed = adr_markdown.parse(file_path.read_text())
        except ValueError as exc:
            print(f"skipping {file_path.name}: {exc}", file=sys.stderr)
            skipped.append(file_path.name)
            continue

        expected = adr_file_path(db_path, args.collection, parsed.id, parsed.type, parsed.area)
        if expected != file_path:
            print(f"warning: {file_path} does not match its expected location {expected}", file=sys.stderr)

        metadata: dict = {"type": parsed.type, "area": parsed.area}
        if parsed.superseded_by:
            metadata["superseded_by"] = parsed.superseded_by
        if parsed.valid_until is not None:
            metadata["valid_until"] = parsed.valid_until
        if parsed.cue:
            metadata["cue"] = parsed.cue

        add_memory.execute(args.collection, [parsed.text], [parsed.id], metadatas=[metadata])

        for edge in parsed.edges:
            repo.add_edge(
                args.collection,
                parsed.id,
                MemoryEdge(target_id=edge["target_id"], edge_type=edge["edge_type"]),
            )

        if parsed.created_at is not None:
            # AddMemoryUseCase.execute() only ever reads created_at from metadata already
            # present in Chroma, never from the metadatas argument -- on a fresh-clone
            # rebuild (id not yet in Chroma) it silently stamps "now" instead of the
            # file's original created_at. Correct it with a direct follow-up upsert.
            [refreshed] = repo.get_by_ids(args.collection, [parsed.id])
            refreshed.metadata["created_at"] = parsed.created_at
            repo.upsert(args.collection, [refreshed])

        imported += 1

    focus_path = focus_file_path(db_path, args.collection)
    if focus_path.is_file():
        # The type is only set on a fresh rebuild; an existing current_focus keeps its metadata.
        metadata = {} if repo.get_by_ids(args.collection, [FOCUS_ID]) else {"type": FOCUS_TYPE}
        add_memory.execute(args.collection, [focus_path.read_text().rstrip("\n")], [FOCUS_ID],
                           metadatas=[metadata])
        imported += 1

    plural = "y" if imported == 1 else "ies"
    summary = f"{args.collection}: imported {imported} entr{plural}"
    if skipped:
        summary += f", skipped {len(skipped)}: {', '.join(skipped)}"
    print(summary)
    return 1 if skipped else 0


def _cmd_reindex(args: argparse.Namespace) -> int:
    db_path = Path(args.db_path) if args.db_path else _DB_PATH
    adr_dir = adr_dir_for(db_path, args.collection)
    if adr_dir is None or not adr_dir.is_dir():
        print(f"no ADR directory found for collection {args.collection!r}", file=sys.stderr)
        return 1

    regenerate_index(adr_dir)
    print(f"{args.collection}: regenerated {adr_dir / 'INDEX.md'}")
    return 0


_STOP = "Stop and ask a human before going on (UPGRADING.md)."


def _cmd_migrate(args: argparse.Namespace) -> int:
    import sqlite3

    from ai_mem.infrastructure import records_migration
    from ai_mem.infrastructure.chroma_sqlite_reader import ChromaSchemaError, read_chroma_store

    db_path = Path(args.db_path) if args.db_path else _DB_PATH
    if not (db_path / CHROMA_SQLITE).is_file():
        print(f"no ChromaDB store at {db_path} -- nothing to migrate")
        return 0
    overrides: dict[str, Path] = {}
    for spec in args.root or []:
        name, sep, path = spec.partition("=")
        if not sep or not name or not path:
            print(f"--root expects <collection>=<path>, got {spec!r}", file=sys.stderr)
            return 2
        overrides[name] = Path(path).expanduser()
    scan_roots = [Path(p).expanduser() for p in args.scan_root or []]
    workspace_root = os.environ.get("AI_MEM_WORKSPACE_ROOT")
    if not scan_roots and workspace_root:
        scan_roots = [Path(workspace_root).expanduser()]

    try:
        snapshot = read_chroma_store(db_path)
    except (ChromaSchemaError, sqlite3.Error, FileNotFoundError) as exc:
        print(f"cannot read the ChromaDB store at {db_path}: {exc}. Nothing was written. {_STOP}", file=sys.stderr)
        return 1
    plan = records_migration.build_plan(snapshot, db_path, scan_roots, overrides)
    unclean = "; ".join(plan.unclean_reasons)
    report_path = db_path / records_migration.REPORT_FILENAME
    if not args.apply:
        print(records_migration.render_summary(plan))
        if unclean:
            print(f"NOT CLEAN ({unclean}): --apply would exit 1 and not mark records_v1 done.")
        print("Dry run -- nothing written. Re-run with --apply to write the files.")
        return 0

    backup = records_migration.apply_plan(plan, db_path)
    report_path.write_text(records_migration.render_report(plan))
    print(records_migration.render_summary(plan))
    if backup is not None:
        print(f"Backup of the store: {backup}")
    print(f"Report: {report_path}")
    if unclean:
        print(f"records_v1 NOT marked done ({unclean}); see the report. {_STOP}", file=sys.stderr)
        return 1
    print(f"records_v1 marked done: {mark_records_v1_done(db_path)}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync ADR-style Markdown files with ai-mem's ChromaDB store.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Write ADR-typed Chroma entries out as Markdown files")
    export_parser.add_argument("--collection", metavar="NAME",
                                help="Limit to one collection (default: all repo.* collections with a resolvable root)")
    export_parser.add_argument("--db-path", metavar="PATH", help="Override the ai-mem ChromaDB path")
    export_parser.set_defaults(func=_cmd_export)

    import_parser = subparsers.add_parser("import", help="Rebuild Chroma entries from ADR Markdown files")
    import_parser.add_argument("--collection", metavar="NAME", required=True, help="Collection to import into")
    import_parser.add_argument("--db-path", metavar="PATH", help="Override the ai-mem ChromaDB path")
    import_parser.set_defaults(func=_cmd_import)

    reindex_parser = subparsers.add_parser("reindex", help="Regenerate docs/records/INDEX.md from existing ADR Markdown files")
    reindex_parser.add_argument("--collection", metavar="NAME", required=True, help="Collection whose ADR directory to reindex")
    reindex_parser.add_argument("--db-path", metavar="PATH", help="Override the ai-mem ChromaDB path")
    reindex_parser.set_defaults(func=_cmd_reindex)

    migrate_parser = subparsers.add_parser(
        "migrate", help="One-time move of a ChromaDB-only store to record files (dry run unless --apply)")
    migrate_parser.add_argument("--apply", action="store_true", help="Write the files (default: only show the plan)")
    migrate_parser.add_argument("--root", action="append", metavar="COLLECTION=PATH",
                                help="Place a collection the scan cannot resolve (repeatable)")
    migrate_parser.add_argument("--scan-root", action="append", metavar="PATH",
                                help="Where to look for CLAUDE.md directories (default: $AI_MEM_WORKSPACE_ROOT)")
    migrate_parser.add_argument("--db-path", metavar="PATH", help="Override the ai-mem ChromaDB path")
    migrate_parser.set_defaults(func=_cmd_migrate)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
