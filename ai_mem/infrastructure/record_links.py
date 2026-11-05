"""Relative links between record files <-> the internal edge references (`<id>` or `<rel-area-path>:<id>`).

A link is resolved by its path alone, without touching the disk: the target's area is the nearest
ancestor whose records, reference or sources directory holds the link target. So a link to a file
that is gone still yields a reference, and lint can report it as dangling.
"""
from __future__ import annotations

import os
from pathlib import Path

from ai_mem.infrastructure.adr_paths import entry_files, records_dir_for_root, reference_dir, sources_dir
from ai_mem.infrastructure.areas import Area, parse_ref, qualify_unchecked


def _area_of(target: Path) -> Area | None:
    for root in target.parents:
        area = Area(root, records_dir_for_root(root))
        if _in_area(target, area):
            return area
    return None


def area_of_records_dir(records_dir: Path) -> Area:
    """The area whose records directory `records_dir` is (its root is the ancestor it hangs below)."""
    for root in records_dir.parents:
        if records_dir_for_root(root) == records_dir:
            return Area(root, records_dir)
    return Area(records_dir, records_dir)


def _in_area(target: Path, area: Area) -> bool:
    records_dir = area.records_dir
    return any(target.is_relative_to(directory) for directory in (records_dir, reference_dir(records_dir), sources_dir(records_dir)))


def ref_for_href(source_file: Path, source_area: Area, href: str) -> str:
    """The edge reference a relative link in `source_file` stands for; ValueError when it leads into no area."""
    target = Path(os.path.normpath(source_file.parent / href))
    area = source_area if _in_area(target, source_area) else _area_of(target)
    if area is None or target.suffix != ".md":
        raise ValueError(f"link {href!r} does not point at a record, reference doc or source")
    return qualify_unchecked(source_area, area, target.stem)


def locate(records_dir: Path, entry_id: str) -> Path | None:
    """The file holding `entry_id` in an area: a record, else a reference doc, else a source."""
    found = entry_files(records_dir, entry_id)
    return found[0] if found else None


def href_for_ref(source_file: Path, source_area: Area, target_ref: str) -> str:
    """The relative link `source_file` writes for an edge reference.

    A target that exists nowhere gets a link to `<records dir>/<id>.md` of its area, which reads back
    as the same reference, so a dangling edge survives a rewrite and lint keeps reporting it.
    """
    rel, entry_id = parse_ref(target_ref)
    if rel is None:
        records_dir = source_area.records_dir
    else:
        records_dir = records_dir_for_root(Path(os.path.normpath(source_area.root / rel)))
    target = locate(records_dir, entry_id) or records_dir / f"{entry_id}.md"
    return Path(os.path.relpath(target, source_file.parent)).as_posix()
