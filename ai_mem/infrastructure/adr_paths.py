"""Filesystem paths and small file helpers for the record files.

No ChromaDB, no MemoryRepository imports. Every function takes `db_path` explicitly
rather than reading AI_MEM_PATH itself.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from ai_mem.repo_context import GLOBAL_COLLECTION, WORKSPACE_COLLECTION, detect_repo_context

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

_MAPPING_FILENAME = "adr_collection_roots.json"
RECORDS_HOME_ENV = "AI_MEM_RECORDS_HOME"
SUBAGENT_PREFIX = "subagent."


def is_contained(path: Path, records_dir: Path, *, allow_symlink: bool) -> bool:
    """Whether `path` resolves inside `records_dir`; with allow_symlink=False a symlink at `path` itself also fails."""
    if not allow_symlink and path.is_symlink():
        return False
    return path.resolve().is_relative_to(records_dir.resolve())


def _mapping_file(db_path: Path) -> Path:
    return db_path / _MAPPING_FILENAME


def read_mapping(db_path: Path) -> dict[str, str]:
    mapping_file = _mapping_file(db_path)
    if not mapping_file.exists():
        return {}
    try:
        return json.loads(mapping_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def record_collection_root(db_path: Path, collection: str, root: Path) -> None:
    """Merge `collection -> root` into the mapping file, written atomically."""
    mapping = read_mapping(db_path)
    mapping[collection] = str(root)
    write_atomic(_mapping_file(db_path), json.dumps(mapping, indent=2, sort_keys=True))


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


def records_home() -> Path | None:
    """Directory holding the records of collections without a 1:1 repo root, or None if unset/missing.

    `$AI_MEM_RECORDS_HOME`, else `$AI_MEM_WORKSPACE_ROOT/ai-mem-records`. Opt-in: the directory must
    already exist, so nothing is written to a path the user never created.
    """
    explicit = os.environ.get(RECORDS_HOME_ENV)
    if explicit:
        home = Path(explicit).expanduser()
    else:
        workspace_root = os.environ.get("AI_MEM_WORKSPACE_ROOT")
        home = Path(workspace_root).expanduser() / "ai-mem-records" if workspace_root else None
    return home if home is not None and home.is_dir() else None


def has_no_repo_root(collection: str) -> bool:
    return collection in (GLOBAL_COLLECTION, WORKSPACE_COLLECTION) or collection.startswith(SUBAGENT_PREFIX)


def rootless_collection_root(collection: str) -> Path | None:
    """`<records_home>/<collection>` for global/workspace/subagent.*; None without a records home
    or when the name is not a single plain path segment (no traversal out of the records home)."""
    home = records_home()
    return home / collection if home is not None and is_safe_path_segment(collection) else None


def resolve_repo_root_for_collection(db_path: Path, collection: str) -> Path | None:
    """Resolve the filesystem root backing a collection's record files.

    `global`, `workspace` and `subagent.*` have no 1:1 repo root: they resolve to
    `<records_home>/<collection>`, or None while no records home exists.
    """
    if has_no_repo_root(collection):
        return rootless_collection_root(collection)

    mapping = read_mapping(db_path)
    cached = mapping.get(collection)
    if cached:
        return Path(cached)

    ctx = detect_repo_context(Path.cwd())
    if ctx.collection == collection:
        root = ctx.git_root or ctx.claude_md_dir
        if root is not None:
            record_collection_root(db_path, collection, root)
            return root

    return None


def records_dir_for_root(root: Path) -> Path:
    """`<root>/docs/records`, or `<root>/$AI_MEM_ADR_DIR`."""
    return root / os.environ.get("AI_MEM_ADR_DIR", "docs/records")


def reference_dir(records_dir: Path) -> Path:
    """Plain reference docs live next to the records directory: `docs/reference/` by default."""
    return records_dir.parent / "reference"


def sources_dir(records_dir: Path) -> Path:
    """Sources (dated evidence, claims frozen) live next to the records directory: `docs/sources/` by default."""
    return records_dir.parent / "sources"


def adr_dir_for(db_path: Path, collection: str) -> Path | None:
    root = resolve_repo_root_for_collection(db_path, collection)
    return records_dir_for_root(root) if root is not None else None


_RESERVED_STEMS = frozenset({"INDEX", "README", "FOCUS"})
# Files that live in the ADR directory but aren't decision records (INDEX.md generated, README.md handwritten,
# FOCUS.md the overwritten projection of the `current_focus` entry).
NON_ADR_FILENAMES = frozenset(f"{stem}.md" for stem in _RESERVED_STEMS)

FOCUS_ID = "current_focus"
FOCUS_FILENAME = "FOCUS.md"


def focus_path(records_dir: Path) -> Path:
    """`<records_dir>/FOCUS.md`: one per records directory, holds the `current_focus` text whatever its type."""
    return records_dir / FOCUS_FILENAME


def focus_file_path(db_path: Path, collection: str) -> Path | None:
    adr_dir = adr_dir_for(db_path, collection)
    return focus_path(adr_dir) if adr_dir is not None else None


def plain_file_content(text: str) -> str:
    """Content of a frontmatter-less file (FOCUS.md, reference docs): the text plus one trailing newline."""
    return text.rstrip("\n") + "\n"


def iter_record_files(adr_dir: Path) -> list[Path]:
    """Every record file below `adr_dir`, sorted -- all `*.md` except the top-level INDEX/README/FOCUS."""
    if not adr_dir.is_dir():
        return []
    return sorted(
        path for path in adr_dir.rglob("*.md")
        if not (path.parent == adr_dir and path.name in NON_ADR_FILENAMES)
    )


def remove_files(adr_dir: Path, files) -> None:
    """Delete `files` and prune the `<area>/<kind>` folders they leave empty (never `adr_dir` itself)."""
    for file_path in files:
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


def adr_file_path(db_path: Path, collection: str, entry_id: str, entry_type: str, area: str) -> Path | None:
    # Validated before the collection is resolved: resolving may record a mapping-file entry.
    relpath = _record_relpath(entry_id, entry_type, area)
    if relpath is None:
        return None
    adr_dir = adr_dir_for(db_path, collection)
    return adr_dir / relpath if adr_dir is not None else None


def find_adr_files(adr_dir: Path, entry_id: str) -> list[Path]:
    """Every `<entry_id>.md` anywhere below `adr_dir`, sorted; [] for an unsafe id or missing dir.

    Matched by exact filename, never by building a glob from the id: an id like `*` must not
    select every record (callers delete what this returns).
    """
    if not is_safe_entry_id(entry_id) or not adr_dir.is_dir():
        return []
    filename = f"{entry_id}.md"
    return sorted(path for path in adr_dir.rglob("*.md") if path.name == filename)
