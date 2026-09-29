"""mem-adr-sync CLI -- export/import round trip between ChromaDB and ADR Markdown files.

Both subcommands operate on a bare ChromaMemoryRepository, never the
MarkdownAdrRepository decorator (a later chunk): export is a pure read, and import
needs to control the correction upsert (see _cmd_import) itself rather than have a
decorator re-serialize the very files it's reading.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.domain.memory import MemoryEdge
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import regenerate_index
from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    DEFAULT_AREA,
    NON_ADR_FILENAMES,
    adr_dir_for,
    adr_file_path,
    find_adr_files,
    is_safe_entry_id,
)
from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository
from ai_mem.repo_context import GLOBAL_COLLECTION, WORKSPACE_COLLECTION

_DB_PATH = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local/share/ai-mem"))


def _exportable_collections(repo: ChromaMemoryRepository, db_path: Path) -> list[str]:
    names = []
    for col_info in repo.list_collections():
        name = col_info.name
        if name in (GLOBAL_COLLECTION, WORKSPACE_COLLECTION):
            print(f"skipping {name}: no file-backed repo root for this collection", file=sys.stderr)
            continue
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

    if adr_dir.is_dir():
        regenerate_index(adr_dir)

    plural = "y" if len(entries) == 1 else "ies"
    print(f"{collection}: exported {len(entries)} entr{plural} to {adr_dir}")
    return len(entries)


def _cmd_export(args: argparse.Namespace) -> int:
    db_path = Path(args.db_path) if args.db_path else _DB_PATH
    repo = ChromaMemoryRepository(db_path)

    if args.collection:
        _export_collection(repo, db_path, args.collection)
        return 0

    for name in _exportable_collections(repo, db_path):
        _export_collection(repo, db_path, name)
    return 0


def _cmd_import(args: argparse.Namespace) -> int:
    db_path = Path(args.db_path) if args.db_path else _DB_PATH
    repo = ChromaMemoryRepository(db_path)
    add_memory = AddMemoryUseCase(repo)

    adr_dir = adr_dir_for(db_path, args.collection)
    if adr_dir is None or not adr_dir.is_dir():
        print(f"no ADR directory found for collection {args.collection!r}", file=sys.stderr)
        return 1

    skipped: list[str] = []
    imported = 0
    for file_path in sorted(adr_dir.rglob("*.md")):
        if file_path.parent == adr_dir and file_path.name in NON_ADR_FILENAMES:
            continue
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

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
