"""Filesystem-path resolution for ADR-style Markdown persistence.

Pure logic module: no ChromaDB, no MemoryRepository imports. Every function
takes `db_path` explicitly rather than reading server.py's AI_MEM_PATH itself,
to avoid a circular import between infrastructure and the MCP server entry point.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from ai_mem.repo_context import GLOBAL_COLLECTION, WORKSPACE_COLLECTION, detect_repo_context

KIND_BY_TYPE = {
    "learning": "learnings",
    "domain": "decisions",
    "pattern": "decisions",
    "anti-pattern": "decisions",
}
ADR_TYPES = frozenset(KIND_BY_TYPE)

DEFAULT_AREA = "general"
_AREA_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

_MAPPING_FILENAME = "adr_collection_roots.json"


def _mapping_file(db_path: Path) -> Path:
    return db_path / _MAPPING_FILENAME


def _read_mapping(db_path: Path) -> dict[str, str]:
    mapping_file = _mapping_file(db_path)
    if not mapping_file.exists():
        return {}
    try:
        return json.loads(mapping_file.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def record_collection_root(db_path: Path, collection: str, root: Path) -> None:
    """Merge `collection -> root` into the mapping file, written atomically."""
    mapping = _read_mapping(db_path)
    mapping[collection] = str(root)
    mapping_file = _mapping_file(db_path)
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = mapping_file.with_suffix(mapping_file.suffix + ".tmp")
    tmp_file.write_text(json.dumps(mapping, indent=2, sort_keys=True))
    tmp_file.replace(mapping_file)


def resolve_repo_root_for_collection(db_path: Path, collection: str) -> Path | None:
    """Resolve the filesystem repo root backing a `repo.<name>` collection.

    `global`/`workspace` never have a 1:1 repo root and always resolve to None.
    """
    if collection in (GLOBAL_COLLECTION, WORKSPACE_COLLECTION):
        return None

    mapping = _read_mapping(db_path)
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


def adr_dir_for(db_path: Path, collection: str) -> Path | None:
    root = resolve_repo_root_for_collection(db_path, collection)
    if root is None:
        return None
    return root / os.environ.get("AI_MEM_ADR_DIR", "docs/records")


_RESERVED_STEMS = frozenset({"INDEX", "README"})
# Files that live in the ADR directory but aren't decision records (INDEX.md generated, README.md handwritten).
NON_ADR_FILENAMES = frozenset(f"{stem}.md" for stem in _RESERVED_STEMS)


def is_safe_entry_id(entry_id: str) -> bool:
    """True if `entry_id` can be used as a filename stem inside the ADR directory.

    Rejects path separators / `..` (which would write outside docs/records/) and the
    stems of the directory's own generated/handwritten files (INDEX.md, README.md).
    """
    return (
        bool(entry_id)
        and entry_id not in (".", "..")
        and "/" not in entry_id
        and "\\" not in entry_id
        and entry_id not in _RESERVED_STEMS
    )


def is_safe_area(area: str) -> bool:
    return bool(_AREA_PATTERN.fullmatch(area))


def adr_file_path(db_path: Path, collection: str, entry_id: str, entry_type: str, area: str) -> Path | None:
    """`<root>/<area>/<kind>/<id>.md`, or None if the type isn't an ADR type or id/area are unsafe."""
    kind = KIND_BY_TYPE.get(entry_type)
    if kind is None or not is_safe_entry_id(entry_id) or not is_safe_area(area):
        return None
    adr_dir = adr_dir_for(db_path, collection)
    if adr_dir is None:
        return None
    return adr_dir / area / kind / f"{entry_id}.md"


def find_adr_files(adr_dir: Path, entry_id: str) -> list[Path]:
    """Every `<entry_id>.md` anywhere below `adr_dir`, sorted; [] for an unsafe id or missing dir."""
    if not is_safe_entry_id(entry_id) or not adr_dir.is_dir():
        return []
    return sorted(adr_dir.glob(f"**/{entry_id}.md"))
