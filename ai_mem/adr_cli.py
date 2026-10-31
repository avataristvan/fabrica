"""mem-adr-sync CLI -- INDEX.md rebuilds (`reindex`).

The Chroma export/import round trip and the records_v1 migration left with the upgrade path
(tags v0-last-mcp, v1-last-upgrade-path).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from ai_mem.infrastructure.adr_index import regenerate_index
from ai_mem.infrastructure.adr_paths import adr_dir_for

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


def main() -> None:
    parser = argparse.ArgumentParser(description="ai-mem record maintenance: INDEX.md rebuilds.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    reindex_parser = subparsers.add_parser("reindex", help="Regenerate docs/records/INDEX.md from existing ADR Markdown files")
    reindex_parser.add_argument("--collection", metavar="NAME", required=True, help="Collection whose ADR directory to reindex")
    reindex_parser.add_argument("--db-path", metavar="PATH", help="Override the ai-mem state directory")
    reindex_parser.set_defaults(func=_cmd_reindex)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
