"""mem-adr-sync CLI -- the records_v1 migration (`migrate`) and INDEX.md rebuilds (`reindex`).

`migrate` reads an old ChromaDB store read-only through `chroma_sqlite_reader` (stdlib sqlite3, no
chromadb needed) and writes record files; it stays so an installation that is still on ChromaDB can
upgrade. The Chroma export/import round trip left with the Chroma backend (tag v0-last-mcp).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from ai_mem.infrastructure.adr_index import regenerate_index
from ai_mem.infrastructure.adr_paths import adr_dir_for
from ai_mem.upgrade_guard import CHROMA_SQLITE, mark_records_v1_done

_DB_PATH = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local/share/ai-mem"))


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
    parser = argparse.ArgumentParser(description="ai-mem record maintenance: INDEX.md rebuilds and the one-time ChromaDB -> record files migration.")
    subparsers = parser.add_subparsers(dest="command", required=True)

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
