"""Regenerate docs/records/INDEX.md -- a compact id/title/status table over ADR files.

Pure storage-layer artifact, regenerated periodically via `mem-adr-sync export`/`reindex`
(see docs/adr-migration-chunk-plan.md, Chunk 3b) -- deliberately not kept live on every
mem_add through MarkdownAdrRepository, to avoid a read-modify-write race on one shared file.
"""
from __future__ import annotations

import sys
from pathlib import Path

from ai_mem.application.list_entries import title_of
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_paths import NON_ADR_FILENAMES

_INDEX_FILENAME = "INDEX.md"


def regenerate_index(adr_dir: Path) -> None:
    """Rebuild `<adr_dir>/INDEX.md` from every `*.md` file below `adr_dir`, except the
    top-level INDEX.md/README.md (same-named files in subfolders are ordinary records).

    A malformed file is skipped and reported by name (stderr) rather than aborting the
    run, matching `adr_cli.py`'s import behavior. Rows are sorted by id and the field
    order is fixed, so output is byte-identical across runs given unchanged sources.
    """
    rows: list[tuple[str, str, str, str, str]] = []
    for file_path in sorted(adr_dir.glob("**/*.md")):
        if file_path.parent == adr_dir and file_path.name in NON_ADR_FILENAMES:
            continue
        try:
            parsed = adr_markdown.parse(file_path.read_text())
        except ValueError as exc:
            print(f"skipping {file_path.relative_to(adr_dir)}: {exc}", file=sys.stderr)
            continue

        status = f"superseded_by: {parsed.superseded_by}" if parsed.superseded_by else "active"
        rows.append((parsed.id, parsed.area, parsed.type, title_of(parsed.text), status))

    rows.sort(key=lambda row: row[0])

    lines = ["# Decision Records Index", "", "| id | area | type | title | status |", "|---|---|---|---|---|"]
    lines.extend(f"| {row_id} | {area} | {entry_type} | {title} | {status} |" for row_id, area, entry_type, title, status in rows)

    (adr_dir / _INDEX_FILENAME).write_text("\n".join(lines) + "\n")
