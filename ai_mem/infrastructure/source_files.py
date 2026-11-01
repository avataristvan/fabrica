"""Sources (`docs/sources/<slug>.md`): locate one, and change its `status:` frontmatter line -- the only write a source allows.

A source's claims are frozen (docs/reference/record-format.md, "Sources"), so `set_status` rewrites exactly one
frontmatter line and leaves every other byte as it was. Stdlib only.
"""
from __future__ import annotations

from pathlib import Path

from ai_mem.infrastructure.adr_paths import is_contained, is_safe_entry_id, sources_dir

SOURCE_STATUSES = ("unprocessed", "processed")


def source_file(records_dir: Path, slug: str) -> Path | None:
    """The source file `slug` names in the area of `records_dir`, or None (unsafe slug, missing, symlink, escaping)."""
    if not is_safe_entry_id(slug):
        return None
    directory = sources_dir(records_dir)
    path = directory / f"{slug}.md"
    if path.is_symlink() or not path.is_file() or not is_contained(path, directory, allow_symlink=False):
        return None
    return path


def set_status(path: Path, status: str) -> bool:
    """Set the `status:` line of the source's frontmatter; True when the file changed.

    Raises ValueError for an unknown status, or when the file has no frontmatter or no `status:` line in it.
    """
    if status not in SOURCE_STATUSES:
        raise ValueError(f"status must be one of {', '.join(SOURCE_STATUSES)}, not {status!r}")
    raw = path.read_bytes()
    lines = raw.decode("utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path.name} has no frontmatter")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            break
        key, separator, value = line.partition(":")
        if separator and key.strip() == "status":
            if value.strip() == status:
                return False
            ending = line[len(line.rstrip("\r\n")):]
            lines[index] = f"status: {status}{ending}"
            path.write_bytes("".join(lines).encode("utf-8"))
            return True
    raise ValueError(f"{path.name} has no `status:` line in its frontmatter")
