"""Assert that every record in a scratch mirror survives parse/serialize and a repository read -> write byte for byte.

    python scripts/roundtrip_check.py <scratch>

For each area below <scratch> (see scripts/scratch_mirror.py), every record file is checked twice:
1. text: serialize(parse(x)) == x;
2. repository: FileMemoryRepository (area resolver mode) reads every record and upserts it back;
   afterwards every file in the area's docs/ (records, INDEX.md) must be byte-identical.
Exit 0 with zero diffs, 1 otherwise. Refuses to run where an area root is a git checkout, since
step 2 writes whatever does not round-trip: run it on a mirror, never on real areas.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai_mem.infrastructure import adr_markdown  # noqa: E402
from ai_mem.infrastructure.adr_paths import ADR_TYPES, iter_record_files  # noqa: E402
from ai_mem.infrastructure.areas import area_records_dir, discover_areas  # noqa: E402
from ai_mem.infrastructure.file_repository import FileMemoryRepository  # noqa: E402


def text_diffs(records_dir: Path) -> list[str]:
    diffs = []
    for path in iter_record_files(records_dir):
        original = path.read_text()
        try:
            parsed = adr_markdown.parse(original)
        except ValueError as exc:
            diffs.append(f"{path}: parse error: {exc}")
            continue
        metadata = {"area": parsed.area, "perspective": parsed.perspective, "created_at": parsed.created_at,
                    "superseded_by": parsed.superseded_by, "valid_until": parsed.valid_until,
                    "edges": parsed.edges, adr_markdown.EXTRA_FRONTMATTER: parsed.extra, "cue": parsed.cue}
        if adr_markdown.serialize(parsed.id, parsed.type, parsed.text, metadata) != original:
            diffs.append(f"{path}: serialize(parse(x)) differs")
    return diffs


def snapshot(directory: Path) -> dict[Path, bytes]:
    return {path: path.read_bytes() for path in sorted(directory.rglob("*")) if path.is_file()}


def repository_diffs(repo: FileMemoryRepository, key: str, docs_dir: Path) -> tuple[int, list[str]]:
    before = snapshot(docs_dir)
    records = [entry for entry in repo.get_all(key) if entry.metadata.get("type") in ADR_TYPES]
    repo.upsert(key, records)
    after = snapshot(docs_dir)
    diffs = [f"{path}: changed by read -> write" for path in sorted(before.keys() | after.keys())
             if before.get(path) != after.get(path)]
    return len(records), diffs


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    scratch = Path(argv[0]).resolve()
    areas = discover_areas(scratch)
    checkouts = [str(area.root) for area in areas if (area.root / ".git").exists()]
    if checkouts:
        print(f"refused: git checkouts among the areas ({', '.join(checkouts)}); run on a scratch mirror", file=sys.stderr)
        return 2

    repo = FileMemoryRepository(scratch / ".no-db", records_dir_for=area_records_dir)
    total_files = total_diffs = 0
    for area in areas:
        diffs = text_diffs(area.records_dir)
        count, repo_diffs = repository_diffs(repo, str(area.root), area.records_dir.parent)
        diffs += repo_diffs
        total_files += len(iter_record_files(area.records_dir))
        total_diffs += len(diffs)
        print(f"{area.root.relative_to(scratch)}: {count} records, {len(diffs)} diffs")
        for diff in diffs:
            print(f"  {diff}")
    print(f"total: {len(areas)} areas, {total_files} record files, {total_diffs} diffs")
    return 1 if total_diffs or not areas else 0


if __name__ == "__main__":
    sys.exit(main())
