"""Build a scratch copy of the workspace's record areas, for exit checks that must not touch real records.

    python scripts/scratch_mirror.py <target> [--source ~/workspace] [--drop-suffix _2026_10_10]

Copies `<area>/docs/records/` of every area below <source> (nested areas and every
`ai-mem-records/<collection>/` included) to the same relative paths below <target>. The sources
are only read. <target> must not exist yet (or be empty) and must lie outside <source>.

`--drop-suffix S` (for the archivist acceptance run): in the ai-mem copy, every record whose id
ends in S is removed and INDEX.md regenerated; in every copied area, edges pointing at a removed
record are stripped, and a `superseded_by` naming one is cleared (with its `valid_until`).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_mem.infrastructure.adr_paths import ADR_TYPES, records_dir_for_root  # noqa: E402
from ai_mem.infrastructure.areas import area_records_dir, discover_areas, resolve_ref  # noqa: E402
from ai_mem.infrastructure.file_repository import FileMemoryRepository  # noqa: E402

RECORDS_HOME = "ai-mem-records"
DROP_AREA = "ai-mem"


def area_paths(source: Path) -> list[str]:
    source = source.resolve()
    return [str(area.root.relative_to(source)) for area in discover_areas(source)]


def mirror(source: Path, target: Path) -> list[str]:
    rels = area_paths(source)
    for rel in rels:
        shutil.copytree(records_dir_for_root(source / rel), records_dir_for_root(target / rel))
    return rels


def drop_suffix(target: Path, suffix: str) -> tuple[list[str], int]:
    """Remove the ai-mem records whose id ends in `suffix`; strip references to them everywhere."""
    repo = FileMemoryRepository(target / ".no-db", records_dir_for=area_records_dir)
    areas = {str(area.root): area for area in discover_areas(target)}
    drop_area = (target / DROP_AREA).resolve()
    drop_key = str(drop_area)
    if drop_key not in areas:
        return [], 0
    dropped = sorted(e.id for e in repo.get_all(drop_key)
                     if e.metadata.get("type") in ADR_TYPES and e.id.endswith(suffix))
    dropped_set = set(dropped)

    def points_at_dropped(area, target_id: str) -> bool:
        resolved = resolve_ref(area, target_id)
        return resolved is not None and resolved[0].root == drop_area and resolved[1] in dropped_set

    rewritten = 0
    for key, area in areas.items():
        changed = []
        for entry in repo.get_all(key):
            if entry.metadata.get("type") not in ADR_TYPES or (key == drop_key and entry.id in dropped_set):
                continue
            edges = json.loads(entry.metadata.get("edges") or "[]")
            kept = [edge for edge in edges if not points_at_dropped(area, edge["target_id"])]
            superseded_by = entry.metadata.get("superseded_by")
            if len(kept) == len(edges) and not (superseded_by and points_at_dropped(area, superseded_by)):
                continue
            if kept:
                entry.metadata["edges"] = json.dumps(kept)
            else:
                entry.metadata.pop("edges", None)
            if superseded_by and points_at_dropped(area, superseded_by):
                entry.metadata.pop("superseded_by")
                entry.metadata.pop("valid_until", None)
            changed.append(entry)
        if changed:
            repo.upsert(key, changed)
            rewritten += len(changed)
    repo.delete(drop_key, dropped)
    return dropped, rewritten


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("target", type=Path)
    parser.add_argument("--source", type=Path, default=Path("~/workspace").expanduser())
    parser.add_argument("--drop-suffix", default=None)
    args = parser.parse_args(argv)

    source, target = args.source.resolve(), args.target.resolve()
    if target == source or target.is_relative_to(source):
        print(f"refused: {target} lies inside the source {source}", file=sys.stderr)
        return 2
    if target.exists() and any(target.iterdir()):
        print(f"refused: {target} is not empty", file=sys.stderr)
        return 2

    rels = mirror(source, target)
    print(f"mirrored {len(rels)} areas to {target}: {', '.join(rels)}")
    if args.drop_suffix:
        dropped, rewritten = drop_suffix(target, args.drop_suffix)
        print(f"dropped {len(dropped)} records ending in {args.drop_suffix!r}; stripped references in {rewritten} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
