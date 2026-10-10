"""Areas: knowledge is addressed by the folder that holds `docs/records/`.

An area is the nearest ancestor (inclusive) of a path with a records directory
(domain_area_path_is_the_address_of_knowledge_2026_10_10). A reference to a record in
another area is `<rel>:<id>`, `<rel>` being the POSIX path from the source area root to the
target area root, always starting with `.` or `..` (e.g. `../ai-architecture:learning_x`).
A bare id is a record of the same area. References are never absolute.

Every ref and area key is validated here before it reaches a path join; ids go through
`is_safe_entry_id` (learning_glob_id_injection_missed_by_review_2026_10_04). Stdlib only.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ai_mem.infrastructure.adr_paths import is_safe_entry_id, is_safe_path_segment, records_dir_for_root
from ai_mem.repo_context import _to_main_checkout

REF_SEPARATOR = ":"
_SKIPPED_DIRS = frozenset({"node_modules"})


@dataclass(frozen=True)
class Area:
    root: Path
    records_dir: Path


def _area_at(directory: Path) -> Area | None:
    records_dir = records_dir_for_root(directory)
    return Area(directory, records_dir) if records_dir.is_dir() else None


def find_area(path: Path) -> Area | None:
    """The area containing `path`: nearest ancestor (inclusive) with a records directory.

    Worktree paths map to their main checkout first. A path inside `<root>/docs/records/`
    resolves to `<root>`, because each ancestor is checked for a `docs/records` child.
    """
    start = Path(path).resolve()
    if not start.is_dir():
        start = start.parent
    start = _to_main_checkout(start)
    for directory in (start, *start.parents):
        area = _area_at(directory)
        if area is not None:
            return area
    return None


def discover_areas(root: Path, max_depth: int = 4) -> list[Area]:
    """Every area at or below `root` (nested areas included), sorted by root path.

    Hidden directories (`.git`, `.claude/worktrees`, ...) and `node_modules` are skipped, and
    an area's own records directory is never searched.
    """
    root = Path(root).resolve()
    found: list[Area] = []
    records_dirs: set[Path] = set()
    for dirpath, dirnames, _ in os.walk(root):
        directory = Path(dirpath)
        if directory in records_dirs:
            dirnames[:] = []
            continue
        area = _area_at(directory)
        if area is not None:
            found.append(area)
            records_dirs.add(area.records_dir)
        if len(directory.relative_to(root).parts) >= max_depth:
            dirnames[:] = []
        else:
            dirnames[:] = [name for name in dirnames if not name.startswith(".") and name not in _SKIPPED_DIRS]
    return sorted(found, key=lambda area: str(area.root))


def _validate_rel(rel: str) -> None:
    """`.` or `..`(/`..`)* as the leading part, then plain segments. No absolute, `~`, empty segment, NUL."""
    if not rel or rel.startswith(("/", "~")) or "\0" in rel or "\\" in rel:
        raise ValueError(f"area path {rel!r} must be relative and start with '.' or '..'")
    segments = rel.split("/")
    if segments[0] == ".":
        rest = segments[1:]
    else:
        ups = 0
        while ups < len(segments) and segments[ups] == "..":
            ups += 1
        if ups == 0:
            raise ValueError(f"area path {rel!r} must start with '.' or '..'")
        rest = segments[ups:]
    for segment in rest:
        if not is_safe_path_segment(segment) or segment.startswith("~"):
            raise ValueError(f"area path {rel!r} has an invalid segment {segment!r}")


def parse_ref(target_id: str) -> tuple[str | None, str]:
    """Split an edge target into `(rel_path, id)`; `rel_path` is None for a bare id.

    Splits at the last `:`, so ids never contain one. Raises ValueError for an invalid
    area path or an id that is not a safe filename stem.
    """
    rel, separator, entry_id = target_id.rpartition(REF_SEPARATOR)
    if not is_safe_entry_id(entry_id):
        raise ValueError(f"id {entry_id!r} in reference {target_id!r} is not a valid record id")
    if not separator:
        return None, entry_id
    _validate_rel(rel)
    return rel, entry_id


def qualify(from_area: Area, to_area: Area, entry_id: str) -> str:
    """The reference to `entry_id` in `to_area` as written in `from_area`: bare id for the same area."""
    if not is_safe_entry_id(entry_id):
        raise ValueError(f"id {entry_id!r} is not a valid record id")
    if from_area.root == to_area.root:
        return entry_id
    rel = Path(os.path.relpath(to_area.root, from_area.root)).as_posix()
    if not rel.startswith(".."):
        rel = f"./{rel}"
    return f"{rel}{REF_SEPARATOR}{entry_id}"


def resolve_ref(from_area: Area, target_id: str) -> tuple[Area, str] | None:
    """`(area, id)` a reference points at, or None when it is invalid or no area is there."""
    try:
        rel, entry_id = parse_ref(target_id)
    except ValueError:
        return None
    if rel is None:
        return from_area, entry_id
    # Lexical normalisation is enough: `_validate_rel` allows `..` only as the leading part.
    target = _area_at(Path(os.path.normpath(from_area.root / rel)))
    return (target, entry_id) if target is not None else None


def area_for_key(key: str) -> Area | None:
    """The area behind an area key (its absolute root path as a string), or None."""
    if not key or "\0" in key or not os.path.isabs(key):
        return None
    root = Path(key)
    if Path(os.path.normpath(root)) != root:
        return None
    return _area_at(root)


def area_records_dir(key: str) -> Path | None:
    """Records-dir resolver for `FileMemoryRepository(records_dir_for=...)`: area key -> records dir."""
    area = area_for_key(key)
    return area.records_dir if area is not None else None


class AreaRefResolver:
    """`AreaRefs` over area keys: resolves a qualified target from the source area's key."""

    def resolve(self, source: str, target_id: str) -> tuple[str, str] | None:
        from_area = area_for_key(source)
        if from_area is None:
            return None
        resolved = resolve_ref(from_area, target_id)
        return (str(resolved[0].root), resolved[1]) if resolved is not None else None
