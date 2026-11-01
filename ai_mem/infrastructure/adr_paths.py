"""Filesystem paths and small file helpers for the record files.

No MemoryRepository imports.
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

KIND_BY_TYPE = {
    "learning": "learnings",
    "domain": "decisions",
    "pattern": "decisions",
    "anti-pattern": "decisions",
    "todo": "todos",
    "user": "user",
}
ADR_TYPES = frozenset(KIND_BY_TYPE)
REFERENCE_TYPE = "reference"  # stored as plain docs/reference/<id>.md, not as a record
FOCUS_TYPE = "project"  # type given to current_focus when it is read back from FOCUS.md

DEFAULT_AREA = "general"
_AREA_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")



def is_contained(path: Path, records_dir: Path, *, allow_symlink: bool) -> bool:
    """Whether `path` resolves inside `records_dir`; with allow_symlink=False a symlink at `path` itself also fails."""
    if not allow_symlink and path.is_symlink():
        return False
    return path.resolve().is_relative_to(records_dir.resolve())


def write_atomic(target: Path, content: str) -> None:
    """Write via a uniquely named temp file + os.replace: readers and concurrent writers never see a torn file."""
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write(content)
        os.replace(tmp_name, target)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def records_dir_for_root(root: Path) -> Path:
    """`<root>/docs/records`, or `<root>/$AI_MEM_ADR_DIR`."""
    return root / os.environ.get("AI_MEM_ADR_DIR", "docs/records")


def reference_dir(records_dir: Path) -> Path:
    """Plain reference docs live next to the records directory: `docs/reference/` by default."""
    return records_dir.parent / "reference"


def sources_dir(records_dir: Path) -> Path:
    """Sources (dated evidence, claims frozen) live next to the records directory: `docs/sources/` by default."""
    return records_dir.parent / "sources"


_RESERVED_STEMS = frozenset({"INDEX", "README", "FOCUS"})
# Files that live in the ADR directory but aren't decision records (INDEX.md generated, README.md handwritten,
# FOCUS.md the overwritten projection of the `current_focus` entry).
NON_ADR_FILENAMES = frozenset(f"{stem}.md" for stem in _RESERVED_STEMS)

FOCUS_ID = "current_focus"
FOCUS_FILENAME = "FOCUS.md"


def focus_path(records_dir: Path) -> Path:
    """`<records_dir>/FOCUS.md`: one per records directory, holds the `current_focus` text whatever its type."""
    return records_dir / FOCUS_FILENAME


def plain_file_content(text: str) -> str:
    """Content of a frontmatter-less file (FOCUS.md, reference docs): the text plus one trailing newline."""
    return text.rstrip("\n") + "\n"


def _walk_markdown(adr_dir: Path):
    """Every `*.md` below `adr_dir`, without entering symlinked directories.

    Not `rglob`: up to Python 3.12 it descends into symlinked directories, so callers that
    delete could reach files outside the area. Symlinked files are still yielded: lint reports
    them and `mem move` refuses them (`is_contained`).
    """
    for root, _dirs, filenames in os.walk(adr_dir, followlinks=False):
        for name in filenames:
            if name.endswith(".md"):
                yield Path(root, name)


def iter_record_files(adr_dir: Path) -> list[Path]:
    """Every record file below `adr_dir`, sorted -- all `*.md` except the top-level INDEX/README/FOCUS."""
    if not adr_dir.is_dir():
        return []
    return sorted(
        path for path in _walk_markdown(adr_dir)
        if not (path.parent == adr_dir and path.name in NON_ADR_FILENAMES)
    )


def remove_files(adr_dir: Path, files) -> None:
    """Delete `files` and prune the `<area>/<kind>` folders they leave empty (never `adr_dir` itself).

    A file whose folder resolves outside `adr_dir` (reached through a symlinked folder) is
    skipped. A symlinked file inside the area is unlinked; that never touches its target.
    """
    root = adr_dir.resolve()
    for file_path in files:
        if not file_path.parent.resolve().is_relative_to(root):
            continue
        file_path.unlink(missing_ok=True)
        for parent in (file_path.parent, file_path.parent.parent):
            if parent != adr_dir and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()


_UNSAFE_SEGMENT_CHARS = frozenset("/\\*?[]\0")


def is_safe_path_segment(name: str) -> bool:
    """One plain path component: not empty, not `.`/`..`, no separators, glob metacharacters or NUL."""
    return bool(name) and name not in (".", "..") and not any(char in name for char in _UNSAFE_SEGMENT_CHARS)


def is_safe_entry_id(entry_id: str) -> bool:
    """True if `entry_id` can be used as a filename stem inside the ADR directory.

    Rejects path separators / `..` (which would write outside docs/records/), glob
    metacharacters, and the stems of the directory's own files (INDEX/README/FOCUS.md).
    """
    return is_safe_path_segment(entry_id) and entry_id not in _RESERVED_STEMS


def is_safe_area(area: str) -> bool:
    return bool(_AREA_PATTERN.fullmatch(area))


def _record_relpath(entry_id: str, entry_type: str, topic: str) -> Path | None:
    kind = KIND_BY_TYPE.get(entry_type)
    if kind is None or not is_safe_entry_id(entry_id) or not is_safe_area(topic):
        return None
    return Path(topic, kind, f"{entry_id}.md")


def record_file_path(records_dir: Path, entry_id: str, entry_type: str, topic: str) -> Path | None:
    """`<records_dir>/<topic>/<kind>/<id>.md`, or None if the type isn't an ADR type or id/topic are unsafe."""
    relpath = _record_relpath(entry_id, entry_type, topic)
    return records_dir / relpath if relpath is not None else None


def find_adr_files(adr_dir: Path, entry_id: str) -> list[Path]:
    """Every `<entry_id>.md` anywhere below `adr_dir`, sorted; [] for an unsafe id or missing dir.

    Matched by exact filename, never by building a glob from the id: an id like `*` must not
    select every record (callers delete what this returns).
    """
    if not is_safe_entry_id(entry_id) or not adr_dir.is_dir():
        return []
    filename = f"{entry_id}.md"
    return sorted(path for path in _walk_markdown(adr_dir) if path.name == filename)


def entry_files(records_dir: Path, entry_id: str) -> list[Path]:
    """Every file `entry_id` names in one area, as a link target: records, a top-level reference doc, a source.

    Unsafe ids, symlinks and files resolving outside their directory are skipped.
    """
    if not is_safe_entry_id(entry_id):
        return []
    found = [path for path in find_adr_files(records_dir, entry_id) if is_contained(path, records_dir, allow_symlink=False)]
    for directory in (reference_dir(records_dir), sources_dir(records_dir)):
        path = directory / f"{entry_id}.md"
        if path.is_file() and is_contained(path, directory, allow_symlink=False):
            found.append(path)
    return found
