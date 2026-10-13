"""mem-dream CLI — manually invoke memory consolidation.

`--area PATH` consolidates the area (nearest ancestor of PATH holding docs/records/) from its
record files; this is the archivist's entry point. Proposals are reported, never applied by this CLI.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from ai_mem.application.dream_memory import DreamMemoryUseCase, MODES, select_neighbourhood
from ai_mem.infrastructure.areas import AreaRefResolver, area_records_dir, find_area
from ai_mem.infrastructure.file_repository import FileMemoryRepository

_DB_PATH = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local/share/ai-mem"))
_LOG_DIR = Path.home() / ".claude/dream-log"

def _save_log(result: str, label: str, no_save: bool) -> None:
    if no_save:
        return
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d-%H%M")
    log_path = _LOG_DIR / f"{ts}-{label}.md"
    log_path.write_text(result)
    print(f"\n→ saved: {log_path}", file=sys.stderr)


def _run_area(args: argparse.Namespace) -> None:
    area = find_area(Path(args.area).expanduser())
    if area is None:
        print(f"Error: no area (folder with docs/records/) at or above {args.area}", file=sys.stderr)
        sys.exit(1)
    key = str(area.root)
    repo = FileMemoryRepository(_DB_PATH, records_dir_for=area_records_dir)

    if args.dry_run:
        try:
            entries = repo.get_all(key)
            if args.neighbourhood:
                entries = select_neighbourhood(entries, args.neighbourhood)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"area {key}: {len(entries)} entries")
        for entry in entries:
            print(f"  {entry.id}")
        return

    label = f"area:{args.mode}"
    print(f"[dream:{label}] running on {key} ...", file=sys.stderr)
    use_case = DreamMemoryUseCase(repo, area_refs=AreaRefResolver())
    try:
        result = use_case.execute(key, args.mode, neighbourhood=args.neighbourhood)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(result)
    _save_log(result, label, args.no_save)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consolidate ai-mem memories using Claude models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Modes: {', '.join(MODES)}\n\n"
            "Area mode: mem-dream --area PATH [--neighbourhood ID...] reads the records of the area "
            "containing PATH. --neighbourhood narrows the review to the named records and the "
            "records of that area they link to or are linked from."
        ),
    )
    parser.add_argument("--mode", choices=MODES, default="hier",
                        help="Consolidation mode (default: hier)")
    parser.add_argument("--area", metavar="PATH", required=True,
                        help="Consolidate the area containing PATH (nearest ancestor with docs/records/)")
    parser.add_argument("--neighbourhood", metavar="ID", nargs="+",
                        help="With --area: only these record ids and their one-hop linked records")
    parser.add_argument("--dry-run", action="store_true",
                        help="List entries that would be processed, no API calls")
    parser.add_argument("--no-save", action="store_true",
                        help="Print result only, don't write to dream-log/")
    args = parser.parse_args()
    _run_area(args)


if __name__ == "__main__":
    main()
