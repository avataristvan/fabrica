"""One-time migration of a ChromaDB-only installation to git-native record files (records_v1).

Turns every entry of every collection into a file, following the model in
domain_records_model_replaces_chroma_2026_10_04:
- domain/pattern/anti-pattern/learning/todo -> docs/records/<area>/<kind>/<id>.md (as is)
- other types are classified by a fixed rule (`classify`), and reported as auto-classified
- current_focus -> docs/records/FOCUS.md, reference -> docs/reference/<id>.md (plain text)
- user entries -> docs/records/<area>/user/<id>.md: the user's perspective, pulled by roles that need it
  (e.g. a reviewer; domain_user_records_as_role_perspective_2026_10_04)

Collections are mapped to directories with the same naming logic the hooks use at runtime
(`detect_repo_context` over every CLAUDE.md directory found below the scan roots), so no
name is guessed. ChromaDB is never deleted from: the store is copied first, and only the
`type`/`area` metadata of auto-classified entries is aligned with the files they now have.
Existing files are never overwritten; a run is idempotent.
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Literal

from ai_mem.domain.memory import MemoryEntry, MemoryRepository
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import regenerate_index
from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    DEFAULT_AREA,
    FOCUS_FILENAME,
    FOCUS_ID,
    KIND_BY_TYPE,
    REFERENCE_TYPE,
    find_adr_files,
    has_no_repo_root,
    is_safe_area,
    is_safe_entry_id,
    plain_file_content,
    read_mapping,
    record_collection_root,
    records_dir_for_root,
    reference_dir,
    rootless_collection_root,
    write_atomic,
)
from ai_mem.repo_context import detect_repo_context

REPORT_FILENAME = "records-migration-report.md"
BACKUP_SUFFIX = ".bak-records-v1"
_SKIP_DIRS = frozenset({".git", "node_modules", "build", ".gradle", "__pycache__", ".venv", "venv", ".idea"})
_MAX_SCAN_DEPTH = 5
_STRUCTURE_PREFIXES = (
    ("tried:", "anti-pattern"),
    ("anti-pattern", "anti-pattern"),
    ("decision:", "domain"),
    ("observed:", "learning"),
    ("rule:", "pattern"),
)


PlacementKind = Literal["record", "focus", "reference"]


@dataclass(frozen=True)
class Placement:
    kind: PlacementKind
    type: str | None = None  # record type, for kind == "record"
    auto: bool = False  # True when the type was derived by rule rather than stored


def classify(entry_id: str, entry_type: str | None, text: str) -> Placement:
    """Where an entry goes. Record types are kept; everything else follows one fixed rule."""
    if entry_id == FOCUS_ID:
        return Placement("focus")
    if entry_type in ADR_TYPES:
        return Placement("record", entry_type)
    if entry_type == REFERENCE_TYPE:
        return Placement("reference")
    # The mem_add body templates name their type in the first word (Tried:/Rule:/Decision:/Observed:).
    stripped = text.lstrip().lstrip("#").lstrip()
    for prefix, structured_type in _STRUCTURE_PREFIXES:
        if stripped.lower().startswith(prefix):
            return Placement("record", structured_type, auto=True)
    if entry_type == "feedback":
        return Placement("record", "pattern", auto=True)
    head = text.lstrip()[:20].upper()
    # todo_* entries that carry a RESULT are closed work: per the records model they become a learning.
    if entry_id.startswith("todo_") or head.startswith("TODO"):
        return Placement("record", "learning" if head.startswith("RESULT") else "todo", auto=True)
    return Placement("record", "learning", auto=True)


def _walk_dirs(scan_roots: list[Path], max_depth: int = _MAX_SCAN_DEPTH) -> Iterator[tuple[Path, list[str]]]:
    """(directory, filenames) below `scan_roots`, skipping build/VCS dirs and dot-dirs (incl. .claude/worktrees)."""
    for scan_root in scan_roots:
        if not scan_root.is_dir():
            continue
        base_depth = len(scan_root.parts)
        for dirpath, dirnames, filenames in os.walk(scan_root):
            depth = len(Path(dirpath).parts) - base_depth
            dirnames[:] = [] if depth >= max_depth else [
                d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")
            ]
            yield Path(dirpath), filenames


def _roots_from(walked: list[tuple[Path, list[str]]]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for directory, filenames in walked:
        if "CLAUDE.md" not in filenames:
            continue
        ctx = detect_repo_context(directory)
        if ctx.has_claude_md and ctx.claude_md_dir is not None:
            found.setdefault(ctx.collection, ctx.claude_md_dir)
    return found


def discover_roots(scan_roots: list[Path]) -> dict[str, Path]:
    """collection -> directory, for every CLAUDE.md directory below `scan_roots`.

    The collection name comes from `detect_repo_context`, i.e. exactly the name the hooks and
    the MCP server derive for a session started in that directory. Agent worktrees map to their
    main checkout there, so they never produce a separate collection here either.
    """
    return _roots_from(list(_walk_dirs(scan_roots)))


def _name_candidates(collection: str, directories: list[Path]) -> tuple[Path | None, list[Path]]:
    parts = collection.removeprefix("repo.").split(".")
    candidates = [path for path in directories
                  if len(path.parts) >= len(parts) and list(path.parts[-len(parts):]) == parts]
    return (candidates[0] if len(candidates) == 1 else None), candidates


def match_by_name(collection: str, scan_roots: list[Path]) -> tuple[Path | None, list[Path]]:
    """Fallback for collection names from older naming rules: the one directory whose trailing
    path components equal the name's dot-separated parts (`repo.a.b` -> `.../a/b`).

    Returns (match, candidates); match is None unless exactly one directory fits.
    """
    return _name_candidates(collection, [directory for directory, _ in _walk_dirs(scan_roots)])


@dataclass
class FileWrite:
    collection: str
    entry_id: str
    path: Path
    content: str
    placement: Placement
    old_type: str | None = None
    entry: MemoryEntry | None = None
    area: str | None = None  # for records only


@dataclass
class MigrationPlan:
    writes: list[FileWrite] = field(default_factory=list)
    already: int = 0
    conflicts: list[FileWrite] = field(default_factory=list)
    unresolved: dict[str, int] = field(default_factory=dict)  # collection -> entry count
    unsafe: list[tuple[str, str]] = field(default_factory=list)  # (collection, id)
    roots: dict[str, Path] = field(default_factory=dict)  # resolved collection -> root used
    name_matched: set[str] = field(default_factory=set)  # collections placed by directory name only
    ambiguous: dict[str, list[Path]] = field(default_factory=dict)  # unresolved, several name matches

    @property
    def auto_classified(self) -> list[FileWrite]:
        return [write for write in self.writes + self.conflicts if write.placement.auto]


def _resolve_root(db_path: Path, collection: str, overrides: dict[str, Path], discovered: dict[str, Path]) -> Path | None:
    if collection in overrides:
        return overrides[collection]
    if has_no_repo_root(collection):
        return rootless_collection_root(collection)
    cached = read_mapping(db_path).get(collection)
    if cached:
        return Path(cached)
    return discovered.get(collection)


def _record_content(entry: MemoryEntry, record_type: str, area: str) -> str:
    metadata = {**entry.metadata, "area": area}
    return adr_markdown.serialize(entry.id, record_type, entry.text, metadata)


def build_plan(repo: MemoryRepository, db_path: Path, scan_roots: list[Path],
               overrides: dict[str, Path] | None = None) -> MigrationPlan:
    overrides = overrides or {}
    walked = list(_walk_dirs(scan_roots))  # one walk, shared by root discovery and name matching
    discovered = _roots_from(walked)
    directories = [directory for directory, _ in walked]
    plan = MigrationPlan()

    for col_info in repo.list_collections():
        collection = col_info.name
        entries = repo.get_all(collection)
        if not entries:
            continue
        root = _resolve_root(db_path, collection, overrides, discovered)
        if root is None and collection.startswith("repo."):
            root, candidates = _name_candidates(collection, directories)
            if root is not None:
                plan.name_matched.add(collection)
            elif len(candidates) > 1:
                plan.ambiguous[collection] = candidates
        if root is None:
            plan.unresolved[collection] = len(entries)
            continue
        plan.roots[collection] = root
        records_dir = records_dir_for_root(root)
        references = reference_dir(records_dir)

        for entry in entries:
            placement = classify(entry.id, entry.metadata.get("type"), entry.text)
            if not is_safe_entry_id(entry.id) and placement.kind != "focus":
                plan.unsafe.append((collection, entry.id))
                continue
            area = None
            if placement.kind == "focus":
                path, content = records_dir / FOCUS_FILENAME, plain_file_content(entry.text)
            elif placement.kind == "reference":
                path, content = references / f"{entry.id}.md", plain_file_content(entry.text)
            else:
                area = entry.metadata.get("area") or DEFAULT_AREA
                if not is_safe_area(area):
                    area = DEFAULT_AREA
                path = records_dir / area / KIND_BY_TYPE[placement.type] / f"{entry.id}.md"
                content = _record_content(entry, placement.type, area)
            write = FileWrite(collection, entry.id, path, content, placement, entry.metadata.get("type"), entry, area)
            # An entry already filed somewhere else -- another area/kind, or records vs. docs/reference
            # (e.g. sorted by hand before the migration) -- is not duplicated.
            elsewhere = []
            if placement.kind in ("record", "reference"):
                reference_path = references / f"{entry.id}.md"
                elsewhere = [p for p in [*find_adr_files(records_dir, entry.id), reference_path]
                             if p != path and p.is_file()]
            if elsewhere and not path.exists():
                plan.conflicts.append(write)
                continue
            if path.exists():
                if path.read_text() == content:
                    plan.already += 1
                else:
                    plan.conflicts.append(write)
                continue
            plan.writes.append(write)
    return plan


def apply_plan(plan: MigrationPlan, repo: MemoryRepository, db_path: Path) -> Path | None:
    """Back up the store, write the planned files, refresh INDEX.md files, align Chroma types.

    Returns the backup directory (None when one already existed from an earlier run).
    """
    backup = db_path.with_name(db_path.name + BACKUP_SUFFIX)
    created_backup = None
    if db_path.is_dir() and not backup.exists():
        shutil.copytree(db_path, backup)
        created_backup = backup

    touched_dirs: set[Path] = set()
    for write in plan.writes:
        write_atomic(write.path, write.content)
        if write.placement.kind == "record":
            touched_dirs.add(records_dir_for_root(plan.roots[write.collection]))

    for records_dir in sorted(touched_dirs):
        regenerate_index(records_dir)

    for collection, root in plan.roots.items():
        if not has_no_repo_root(collection):
            record_collection_root(db_path, collection, root)

    # Keep the still-running stack consistent with the files: an entry whose stored type is not
    # a record type would otherwise lose its new file on the next mem_add (MarkdownAdrRepository
    # removes files of non-record entries). Metadata only -- nothing is deleted.
    for write in plan.writes + plan.conflicts:
        if write.placement.kind == "record" and write.entry is not None:
            meta = write.entry.metadata
            if meta.get("type") != write.placement.type or (meta.get("area") or DEFAULT_AREA) != write.area:
                write.entry.metadata = {**meta, "type": write.placement.type, "area": write.area}
                repo.upsert(write.collection, [write.entry])
    return created_backup


def render_summary(plan: MigrationPlan) -> str:
    by_kind: dict[str, int] = {}
    for write in plan.writes:
        by_kind[write.placement.kind] = by_kind.get(write.placement.kind, 0) + 1
    lines = [
        f"{len(plan.writes)} files to write ({', '.join(f'{n} {k}' for k, n in sorted(by_kind.items())) or 'none'}) "
        f"in {len({w.collection for w in plan.writes})} collections; {plan.already} already migrated.",
        f"{len(plan.auto_classified)} entries auto-classified by rule (review them in the report).",
    ]
    if plan.name_matched:
        lines.append(f"{len(plan.name_matched)} collections placed by directory name only: "
                     + ", ".join(f"{c} -> {plan.roots[c]}" for c in sorted(plan.name_matched)))
    if plan.conflicts:
        lines.append(f"{len(plan.conflicts)} conflicts: a different file already exists -- left untouched.")
    if plan.unresolved:
        lines.append(f"{len(plan.unresolved)} collections without a directory (skipped): "
                     + ", ".join(f"{c} ({n})" for c, n in sorted(plan.unresolved.items())))
    if plan.unsafe:
        lines.append(f"{len(plan.unsafe)} ids cannot be filenames (skipped).")
    return "\n".join(lines)


def render_report(plan: MigrationPlan) -> str:
    out = ["# ai-mem records migration (records_v1)", "", render_summary(plan), ""]
    out += ["## Collections", "", "| collection | directory | files written |", "|---|---|---|"]
    for collection, root in sorted(plan.roots.items()):
        count = sum(1 for w in plan.writes if w.collection == collection)
        out.append(f"| {collection} | {root} | {count} |")
    if plan.auto_classified:
        out += ["", "## Auto-classified (check these)", "",
                "Stored type -> record type by rule: feedback -> pattern; todo_*/TODO -> todo (RESULT -> learning); "
                "everything else -> learning. Fix a wrong one by retyping it with mem_add.", "",
                "| collection | id | stored type | now |", "|---|---|---|---|"]
        for w in plan.auto_classified:
            out.append(f"| {w.collection} | {w.entry_id} | {w.old_type or '-'} | {w.placement.type} |")
    if plan.conflicts:
        out += ["", "## Conflicts (not written)", ""]
        out += [f"- {w.collection}/{w.entry_id}: {w.path} exists with different content" for w in plan.conflicts]
    if plan.unresolved:
        out += ["", "## Collections without a directory", "",
                "Re-run with `mem-adr-sync migrate --root <collection>=<path>` to place them. "
                "`global`, `workspace` and `subagent.*` need a records home: create "
                "`$AI_MEM_WORKSPACE_ROOT/ai-mem-records` (or set `AI_MEM_RECORDS_HOME`).", ""]
        for collection, count in sorted(plan.unresolved.items()):
            candidates = plan.ambiguous.get(collection)
            hint = f" -- several directories match: {', '.join(map(str, candidates))}" if candidates else ""
            out.append(f"- {collection}: {count} entries{hint}")
    if plan.unsafe:
        out += ["", "## Ids that cannot be filenames", ""]
        out += [f"- {c}/{i}" for c, i in plan.unsafe]
    return "\n".join(out) + "\n"
