"""The Sources section of `mem doctor`: are the area's sources pointed to?

A source is `docs/sources/<slug>.md` (format: docs/reference/record-format.md, "Sources"). It is *pointed to* when a record of the same
area names its path (`docs/sources/<slug>.md`) in the text or has an edge to `<slug>`, from any area. A source nothing points to
must say `status: unprocessed`; that is the archivist's queue, not a finding. Stdlib only; read-only.
"""
from __future__ import annotations

from pathlib import Path

from ai_mem.infrastructure.adr_paths import sources_dir
from ai_mem.infrastructure.areas import Area
from ai_mem.infrastructure.source_files import SOURCE_STATUSES

SOURCE_FIELDS = ("type", "date", "origin", "status")
_READ_LIMIT = 1_000_000


def _text(path: Path) -> str | None:
    try:
        if path.is_symlink() or not path.is_file():
            return None
        with open(path, "rb") as handle:
            return handle.read(_READ_LIMIT).decode("utf-8", errors="replace")
    except OSError:
        return None


def _frontmatter(text: str) -> dict[str, str] | None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return None


def _source_files(area: Area) -> list[Path]:
    directory = sources_dir(area.records_dir)
    try:
        return sorted(p for p in directory.glob("*.md") if p.is_file() and not p.is_symlink())
    except OSError:
        return []


def collect_sources(area: Area, record_texts: list[str], pointed_slugs: set[str]) -> dict:
    """`record_texts`: the area's record bodies; `pointed_slugs`: ids that records of any area have an edge to in this area."""
    unprocessed, unpointed, malformed = [], [], []
    for path in _source_files(area):
        name = path.relative_to(area.root).as_posix()
        fields = _frontmatter(_text(path) or "")
        if fields is None:
            malformed.append({"file": name, "problem": "no frontmatter"})
            continue
        missing = [key for key in SOURCE_FIELDS if not fields.get(key)]
        if missing:
            malformed.append({"file": name, "problem": f"missing {', '.join(missing)}"})
            continue
        if fields["status"] not in SOURCE_STATUSES:
            malformed.append({"file": name, "problem": f"status {fields['status'][:40]!r} is not one of {', '.join(SOURCE_STATUSES)}"})
            continue
        slug = path.stem
        pointed = slug in pointed_slugs or any(f"docs/sources/{slug}.md" in text or f"docs/sources/{slug}/" in text for text in record_texts)
        if fields["status"] == "unprocessed":
            unprocessed.append(name)
        elif not pointed:
            unpointed.append(name)
    return {"total": len(_source_files(area)), "unprocessed": unprocessed, "unpointed": unpointed, "malformed": malformed}
