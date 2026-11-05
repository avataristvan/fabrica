"""`mem` -- the write contract for record files (stdlib only; reads go through Read/Grep).

Every write goes through the existing use cases over `FileMemoryRepository` in area mode (the
repository key is the area root). Ids and area paths are validated here,
before any use case, path join or glob (pattern_tool_argument_ids_are_hostile_input).

Exit codes: 0 ok, 1 conflict / not found, 2 usage or invalid input.
A write into an area whose INDEX.md is hand-kept (differs from the generated one) is refused with 1, nothing
written; `mem lint --fix` is exempt and adopts the area. current_focus (FOCUS.md) is not INDEX-bound.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import get_args

from ai_mem import doctor, records_lint, review
from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.delete_memory import DeleteMemoryUseCase
from ai_mem.application.move_memory import AreaMovePlan, MoveRow, MoveToAreaUseCase, OpKind
from ai_mem.application.relocate_area import RelocateAreaUseCase
from ai_mem.application.remove_edge import RemoveEdgeUseCase
from ai_mem.domain.memory import EdgeType, MemoryRepository, TargetNotFound, is_area_qualified, normalize_cue, parse_edges
from ai_mem.infrastructure.adr_index import index_is_current
from ai_mem.infrastructure.adr_paths import (
    FOCUS_ID,
    entry_files,
    find_adr_files,
    focus_path,
    is_contained,
    is_safe_area,
    is_safe_entry_id,
    iter_record_files,
    record_file_path,
)
from ai_mem.infrastructure.areas import (
    Area,
    AreaRefResolver,
    area_for_key,
    area_records_dir,
    discover_areas,
    find_area,
    parse_ref,
    qualify,
    resolve_ref,
    search_order,
)
from ai_mem.infrastructure.area_relocation import AreaRelocation, is_versioned, machine_state
from ai_mem.infrastructure.file_repository import FileMemoryRepository
from ai_mem.infrastructure.source_files import SOURCE_STATUSES, set_status, source_file

OK, CONFLICT, USAGE = 0, 1, 2


class CliError(Exception):
    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


def _repository() -> MemoryRepository:
    return FileMemoryRepository(area_records_dir)


def _refuse_hand_kept_index(*areas: Area) -> None:
    """Every record write regenerates INDEX.md; one that differs from the generated text is hand-kept (or
    merely stale, e.g. a record file was added by hand) and would be overwritten, so nothing is written."""
    for area in areas:
        index = area.records_dir / "INDEX.md"
        if index.exists() and not index_is_current(area.records_dir):
            raise CliError(
                f"{index} is hand-kept (or stale); a write would overwrite it. "
                "Adopt the area with `mem lint --fix` from inside it first", CONFLICT)


def _area(path: str | None) -> Area:
    start = Path(path).expanduser() if path else Path.cwd()
    area = find_area(start)
    if area is None:
        raise CliError(f"no area (a folder with docs/records/) at or above {start}; pass --area PATH", USAGE)
    return area


def _bare_id(entry_id: str) -> str:
    if ":" in entry_id or not is_safe_entry_id(entry_id) or not entry_id.isprintable() or entry_id != entry_id.strip():
        raise CliError(f"invalid id {entry_id!r}: a plain file stem without ':', separators or glob characters", USAGE)
    return entry_id


def _emit(args: argparse.Namespace, payload: dict, line: str) -> None:
    print(json.dumps(payload, ensure_ascii=False) if args.json else line)


def _read_text(args: argparse.Namespace) -> str | None:
    sources = [name for name, given in (("--text", args.text is not None), ("--file", args.file is not None), ("-", args.stdin)) if given]
    if len(sources) > 1:
        raise CliError(f"give the text once, not via {' and '.join(sources)}", USAGE)
    if args.text is not None:
        return args.text
    if args.stdin or args.file == "-":
        return sys.stdin.read()
    if args.file is not None:
        try:
            return Path(args.file).expanduser().read_text()
        except OSError as exc:
            raise CliError(f"cannot read {args.file}: {exc}", USAGE) from exc
    return None


def _add(args: argparse.Namespace) -> int:
    entry_id = _bare_id(args.id)
    area = _area(args.area)
    if entry_id != FOCUS_ID:
        _refuse_hand_kept_index(area)
    text = _read_text(args)
    try:
        cue = normalize_cue(args.cue) if args.cue is not None else None
    except ValueError as exc:
        raise CliError(str(exc), USAGE) from exc

    repo, key = _repository(), str(area.root)
    existing = repo.get_by_ids(key, [entry_id])
    if not existing and entry_id != FOCUS_ID and find_adr_files(area.records_dir, entry_id):
        # get_by_ids skips records whose frontmatter does not parse; writing would overwrite them.
        raise CliError(f"{entry_id!r} exists but cannot be read (malformed frontmatter); fix the file by hand first", CONFLICT)
    if entry_id == FOCUS_ID and text is None:
        raise CliError("current_focus needs text (--text, --file or -)", USAGE)
    metadata: dict = {}
    if entry_id != FOCUS_ID:
        for field, value in (("type", args.type), ("area", args.topic), ("perspective", args.perspective), ("cue", cue)):
            if value is not None:
                metadata[field] = value

    if existing:
        if text is None:
            if not metadata:
                raise CliError(f"{entry_id!r} exists: give new text or something to change (--type/--topic/--perspective/--cue)", USAGE)
            # Re-adding the stored text keeps type/topic/created/edges; only the given fields change.
            text = existing[0].text
        action = "updated"
    else:
        if text is None or (entry_id != FOCUS_ID and args.type is None):
            raise CliError(f"new id {entry_id!r} needs --type and text (--text, --file or -)", USAGE)
        action = "added"
    try:
        AddMemoryUseCase(repo).execute(key, [text], [entry_id], [metadata])
    except ValueError as exc:
        raise CliError(str(exc), USAGE) from exc
    _emit(args, {"action": action, "id": entry_id, "area": key}, f"{action} {entry_id}")
    return OK


def _search_root(home: Area, root: str | None) -> Path:
    """`--root`, else $AI_MEM_WORKSPACE_ROOT, else the parent of the home area."""
    root = root or os.environ.get("AI_MEM_WORKSPACE_ROOT")
    return Path(root).expanduser().resolve() if root else home.root.parent


def _usable_ref(home: Area, area: Area, entry_id: str) -> bool:
    """False when the area path holds characters `mem link` refuses in a reference."""
    try:
        qualify(home, area, entry_id)
    except ValueError:
        return False
    return True


def _source_exists(key: str, slug: str) -> bool:
    """For AddEdgeUseCase: does the area behind `key` hold the source `slug`?"""
    area = area_for_key(key)
    return area is not None and source_file(area.records_dir, slug) is not None


def _locate(entry_id: str, home: Area, root: str | None) -> tuple[list[tuple[Area, Path]], int]:
    """Every record, docs/reference doc or source named `entry_id` (read-only). Files resolving outside their directory are skipped."""
    if not is_safe_entry_id(entry_id):
        return [], 0
    areas = search_order(home, _search_root(home, root))
    hits = []
    for area in areas:
        found = entry_files(area.records_dir, entry_id)
        if found and _usable_ref(home, area, entry_id):
            hits += [(area, path) for path in found]
    return hits, len(areas)


def _find(args: argparse.Namespace) -> int:
    entry_id = _bare_id(args.id)
    home = _area(args.area)
    hits, searched = _locate(entry_id, home, args.root)
    for area, path in hits:
        ref = qualify(home, area, entry_id)
        _emit(args, {"ref": ref, "path": str(path), "area": str(area.root)}, f"{ref}  {path}")
    if not hits:
        _emit(args, {"action": "not_found", "id": entry_id, "areas": searched}, f"not found in {searched} areas")
        return CONFLICT
    return OK


def _link(args: argparse.Namespace) -> int:
    source = _bare_id(args.source)
    area = _area(args.area)
    if args.to_area:
        to_area = _area(args.to_area)
        try:
            target = qualify(area, to_area, _bare_id(args.target))
        except ValueError as exc:
            raise CliError(str(exc), CONFLICT) from exc
    else:
        try:
            parse_ref(args.target)
        except ValueError as exc:
            raise CliError(str(exc), USAGE) from exc
        target = args.target
    _refuse_hand_kept_index(area)

    repo, key = _repository(), str(area.root)
    try:
        AddEdgeUseCase(repo, area_refs=AreaRefResolver(), source_exists=_source_exists).execute(key, source, target, args.type)
    except ValueError as exc:
        about_target = not args.to_area and isinstance(exc, TargetNotFound)
        raise CliError(f"{exc}{_found_at_hint(area, args.target) if about_target else ''}", CONFLICT) from exc
    _emit(args, {"action": "linked", "source": source, "target": target, "type": args.type, "area": key},
          f"linked {source} --{args.type}--> {target}")
    return OK


def _unlink(args: argparse.Namespace) -> int:
    source = _bare_id(args.source)
    area = _area(args.area)
    _refuse_hand_kept_index(area)
    repo, key = _repository(), str(area.root)
    try:
        removed = RemoveEdgeUseCase(repo).execute(key, source, args.target, args.type)
    except ValueError as exc:
        raise CliError(str(exc), CONFLICT) from exc
    _emit(args, {"action": "unlinked", "source": source, "target": args.target, "types": removed, "area": key},
          f"unlinked {source} --{','.join(removed)}--> {args.target}")
    return OK


def _source(args: argparse.Namespace) -> int:
    slug = _bare_id(args.slug)
    area = _area(args.area)
    path = source_file(area.records_dir, slug)
    if path is None:
        raise CliError(f"no source {slug!r} in {area.root} (docs/sources/{slug}.md)", CONFLICT)
    try:
        changed = set_status(path, args.status)
    except (ValueError, UnicodeDecodeError) as exc:
        raise CliError(str(exc), CONFLICT) from exc
    action = "updated" if changed else "unchanged"
    _emit(args, {"action": action, "source": slug, "status": args.status, "path": str(path)},
          f"{action} {slug}: status {args.status}")
    return OK


def _move_area(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if Path(args.old).expanduser().is_symlink():
        raise CliError(f"{args.old} is a symlink; pass the folder itself", USAGE)
    old = Path(args.old).expanduser().resolve()
    new_arg = Path(args.new).expanduser()
    new = new_arg.parent.resolve() / new_arg.name
    if not (old.is_relative_to(root) and new.is_relative_to(root)) or old == root:
        raise CliError(f"OLD and NEW must both lie below --root {root}", USAGE)
    relocation = AreaRelocation(old, new)
    areas = discover_areas(root)
    if not any(relocation.moves(area.root) for area in areas):
        raise CliError(f"no area at or below {old}", USAGE)
    if (reason := relocation.preflight()) is not None:
        raise CliError(reason, CONFLICT)

    repo = _repository()
    use_case = RelocateAreaUseCase(repo, relocation)
    plan = use_case.plan([str(area.root) for area in areas])
    if plan.malformed:
        raise CliError("malformed edges field in " + ", ".join(f"{key}:{entry_id}" for key, entry_id in plan.malformed)
                       + "; fix the files by hand first", CONFLICT)

    def name(key: str) -> str:
        return Path(key).relative_to(root).as_posix() or "."

    written = [area for area in areas if str(area.root) in plan.entries]
    blockers = [f"{name(str(area.root))}: INDEX.md is hand-kept (or stale); run `mem lint --fix` there first"
                for area in written
                if (area.records_dir / "INDEX.md").exists() and not index_is_current(area.records_dir)]
    if not args.include_unversioned:
        blockers += [f"{name(str(area.root))}: not under version control (no undo); commit it or pass --include-unversioned"
                     for area in written if not is_versioned(area)]

    for rewrite in plan.rewrites:
        _emit(args, {"action": "rewrite", "area": rewrite.area, "id": rewrite.id, "where": rewrite.where,
                     "old": rewrite.old, "new": rewrite.new},
              f"rewrite {name(rewrite.area)}: {rewrite.id} ({rewrite.where}) {rewrite.old} -> {rewrite.new}")
    _emit(args, {"action": "rename", "old": str(old), "new": str(new)}, f"rename {old} -> {new}")
    for line in machine_state(old, new, root, areas):
        _emit(args, {"action": "left_to_you", "detail": line}, f"left to you: {line}")
    for blocker in blockers:
        _emit(args, {"action": "blocked", "detail": blocker}, f"blocked: {blocker}")
    if blockers:
        return CONFLICT
    if args.dry_run:
        return OK
    # Rename first: a failed rename leaves nothing written, while rewritten references would only resolve after it.
    try:
        relocation.rename()
    except OSError as exc:
        raise CliError(f"rename failed, nothing written: {exc}", CONFLICT) from exc
    use_case.apply(plan, key_after=lambda key: str(relocation.after(Path(key))))
    records = sum(map(len, plan.entries.values()))
    _emit(args, {"action": "done", "rewrites": len(plan.rewrites), "records": records},
          f"done: folder renamed, {len(plan.rewrites)} reference(s) in {records} record(s) rewritten")
    return OK


def _found_at_hint(home: Area, target: str) -> str:
    """For a bare link target: where else the id exists. Never auto-qualifies; the caller decides."""
    if ":" in target:
        return ""
    hits, searched = _locate(target, home, None)
    if any(area.root == home.root for area, _ in hits):
        return ""
    if not hits:
        return f"; {target!r} found nowhere ({searched} areas searched)"
    return f"; not in this area; found at {', '.join(dict.fromkeys(qualify(home, area, target) for area, _ in hits))}"


def _delete(args: argparse.Namespace) -> int:
    ids = list(dict.fromkeys(_bare_id(entry_id) for entry_id in args.ids))
    area = _area(args.area)
    if any(entry_id != FOCUS_ID for entry_id in ids):
        _refuse_hand_kept_index(area)
    repo, key = _repository(), str(area.root)
    present = {entry.id for entry in repo.get_by_ids(key, ids)}
    dangling = []
    if present:
        dangling = DeleteMemoryUseCase(repo).execute(key, [entry_id for entry_id in ids if entry_id in present])
    missing = [entry_id for entry_id in ids if entry_id not in present]
    for entry_id in ids:
        action = "deleted" if entry_id in present else "not_found"
        _emit(args, {"action": action, "id": entry_id, "area": key}, f"{action.replace('_', ' ')} {entry_id}")
    for edge in dangling:
        _emit(args, {"action": "dangling", "source": edge.referrer, "target": edge.target, "type": edge.edge_type, "area": key},
              f"dangling: {edge.referrer} --{edge.edge_type}--> {edge.target}")
    return CONFLICT if missing else OK


class _AreaAddressing(AreaRefResolver):
    def __init__(self) -> None:
        self._areas: dict[str, Area | None] = {}

    def _area(self, key: str) -> Area:
        if key not in self._areas:
            self._areas[key] = area_for_key(key)
        area = self._areas[key]
        if area is None:
            raise ValueError(f"not an area: {key}")
        return area

    def translate(self, from_key: str, to_key: str, ref: str) -> str:
        from_area, to_area = self._area(from_key), self._area(to_key)
        rel, entry_id = parse_ref(ref)
        if rel is None:
            origin = from_area
        else:
            hit = resolve_ref(from_area, ref)
            if hit is None:
                raise ValueError(f"reference {ref!r} points at no area")
            origin = hit[0]
        return qualify(to_area, origin, entry_id)


def _escaping_files(area: Area, files: list[Path]) -> list[Path]:
    return [path for path in files if not is_contained(path, area.records_dir, allow_symlink=True)]


def _preflight_move(sources: list[Area], targets: dict[Area, list[str]], repo: MemoryRepository) -> None:
    """Refuse before planning when a file the move would write, rewrite or delete is not what it seems:
    a target file that get_by_ids cannot read (it would be overwritten), or a symlink leaving a records dir."""
    escaping = [path for source in sources for path in _escaping_files(source, iter_record_files(source.records_dir))]
    for target, ids in targets.items():
        escaping += _escaping_files(target, [f for entry_id in ids for f in find_adr_files(target.records_dir, entry_id)])
    if escaping:
        raise CliError(f"refusing to move: {escaping[0]} resolves outside its records directory", CONFLICT)
    for target, ids in targets.items():
        readable = {entry.id for entry in repo.get_by_ids(str(target.root), ids)}
        for entry_id in ids:
            if entry_id not in readable and find_adr_files(target.records_dir, entry_id):
                raise CliError(f"{entry_id!r} exists in the target area but cannot be read (malformed frontmatter); fix it by hand first", CONFLICT)


def _scan_areas(args: argparse.Namespace, involved: list[Area]) -> list[str]:
    if args.scan_root:
        scan_root = Path(args.scan_root).expanduser()
    else:
        scan_root = Path(os.path.commonpath([area.root for area in involved]))
        home = Path.home().resolve()
        if scan_root == home or scan_root in home.parents:
            raise CliError(f"the areas only share {scan_root}, too wide to scan for referrers; pass --scan-root DIR", USAGE)
    return [str(area.root) for area in discover_areas(scan_root)]


def _move(args: argparse.Namespace) -> int:
    if args.batch:
        if args.ids or args.to_area or args.area:
            raise CliError("--batch takes its areas and ids from the file; give no ids, --to-area or --area", USAGE)
        rows, areas = _read_batch(Path(args.batch).expanduser())
    else:
        if not args.ids or not args.to_area:
            raise CliError("give ids and --to-area, or --batch FILE", USAGE)
        ids = list(dict.fromkeys(_bare_id(entry_id) for entry_id in args.ids))
        if FOCUS_ID in ids:
            raise CliError("current_focus is not a record and is not moved", USAGE)
        source, target = _area(args.area), _area(args.to_area)
        if source.root == target.root:
            raise CliError("source and target area are the same", USAGE)
        areas = {str(source.root): source, str(target.root): target}
        rows = [MoveRow(str(source.root), entry_id, str(target.root)) for entry_id in ids]
    _refuse_hand_kept_index(*areas.values())
    scan = _scan_areas(args, list(areas.values()))
    repo = _repository()
    targets: dict[Area, list[str]] = {}
    for row in rows:
        targets.setdefault(areas[row.target], []).append(row.id)
    _preflight_move([areas[key] for key in dict.fromkeys(row.source for row in rows)], targets, repo)
    use_case = MoveToAreaUseCase(repo, _AreaAddressing())
    plan = use_case.plan_batch(rows, scan, resume=bool(args.batch))

    if plan.conflicts or (args.batch and plan.not_found_ids):
        for conflict in plan.conflicts:
            _emit(args, {"action": "conflict", "id": conflict.id, "reason": conflict.reason}, f"conflict {conflict.id}: {conflict.reason}")
        if args.batch:
            _report_not_found(args, plan)
        return CONFLICT
    _print_move_plan(args, plan, areas)
    if not args.dry_run:
        use_case.apply(plan)
    for entry_id in plan.done_ids:
        _emit(args, {"action": "done", "id": entry_id}, f"done {entry_id} (already in its target)")
    _report_not_found(args, plan)
    return CONFLICT if plan.not_found_ids else OK


def _report_not_found(args: argparse.Namespace, plan: AreaMovePlan) -> None:
    for entry_id in plan.not_found_ids:
        _emit(args, {"action": "not_found", "id": entry_id}, f"not found {entry_id}")


def _batch_area(base: Path, text: str, lineno: int) -> Area:
    path = Path(text).expanduser()
    root = (path if path.is_absolute() else base / path).resolve()
    area = find_area(root)
    if area is None or area.root != root:
        raise CliError(f"line {lineno}: {text!r} is not an area root (a folder with docs/records/)", USAGE)
    return area


def _read_batch(file: Path) -> tuple[list[MoveRow], dict[str, Area]]:
    """TSV `source_area<TAB>id<TAB>target_area[<TAB>perspective]`; `#` comments; paths relative to the file."""
    try:
        lines = file.read_text().splitlines()
    except OSError as exc:
        raise CliError(f"cannot read {file}: {exc}", USAGE) from exc
    rows, areas = [], {}
    seen_in_source, seen_in_target = set(), set()
    for lineno, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        cols = line.split("\t")
        if not 3 <= len(cols) <= 4 or not all(cols[:3]):
            raise CliError(f"line {lineno}: expected source_area<TAB>id<TAB>target_area[<TAB>perspective]", USAGE)
        source, target = (_batch_area(file.resolve().parent, cols[i], lineno) for i in (0, 2))
        entry_id, perspective = _bare_id(cols[1]), (cols[3] if len(cols) == 4 else "")
        if entry_id == FOCUS_ID:
            raise CliError(f"line {lineno}: current_focus is not a record and is not moved", USAGE)
        if source.root == target.root:
            raise CliError(f"line {lineno}: source and target area are the same", USAGE)
        if perspective and not is_safe_area(perspective):
            raise CliError(f"line {lineno}: perspective {perspective!r} must match the topic pattern ^[a-z0-9][a-z0-9_-]*$", USAGE)
        if (source.root, entry_id) in seen_in_source:
            raise CliError(f"line {lineno}: {entry_id!r} is listed twice for {source.root}", USAGE)
        if (target.root, entry_id) in seen_in_target:
            raise CliError(f"line {lineno}: two rows move {entry_id!r} into {target.root}", USAGE)
        seen_in_source.add((source.root, entry_id))
        seen_in_target.add((target.root, entry_id))
        areas.update({str(source.root): source, str(target.root): target})
        rows.append(MoveRow(str(source.root), entry_id, str(target.root), perspective))
    if not rows:
        raise CliError(f"{file} has no rows", USAGE)
    return rows, areas


_OP_VERBS: dict[OpKind, str] = {"write": "write", "delete": "delete", "rewrite_edge": "rewrite edge", "report": "report (not edited)"}


def _print_move_plan(args: argparse.Namespace, plan: AreaMovePlan, areas: dict[str, Area]) -> None:
    prefix = "would " if args.dry_run else ""
    for op in plan.ops:
        area = areas.get(op.area)
        detail = op.detail
        if op.kind in ("write", "delete") and area is not None and op.entry is not None:
            if op.kind == "delete":
                detail = " ".join(str(f) for f in find_adr_files(area.records_dir, op.id))
            else:
                detail = str(record_file_path(area.records_dir, op.id, op.entry.metadata["type"], op.entry.metadata.get("area") or "general"))
        verb = _OP_VERBS[op.kind]
        _emit(args, {"action": op.kind, "area": op.area, "id": op.id, "detail": detail, "dry_run": args.dry_run},
              f"{prefix}{verb} {op.area}:{op.id} {detail}".rstrip())


def _context_map(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser() if args.root else Path.cwd()
    repo = _repository()
    areas = discover_areas(root)
    pairs: dict[tuple[str, str], dict[str, int]] = {}
    unresolved = []
    entries_by_area = {str(area.root): repo.get_all(str(area.root)) for area in areas}
    ids_by_area = {key: {entry.id for entry in entries} for key, entries in entries_by_area.items()}

    def exists(area_root: str, entry_id: str) -> bool:
        if area_root not in ids_by_area:
            ids_by_area[area_root] = {entry.id for entry in repo.get_all(area_root)}
        return entry_id in ids_by_area[area_root]

    for area in areas:
        key = str(area.root)
        for entry in entries_by_area[key]:
            try:
                entry_edges = parse_edges(entry.metadata.get("edges"))
            except ValueError:
                unresolved.append({"area": key, "id": entry.id, "ref": "<malformed edges field>", "type": "-"})
                continue
            for edge in entry_edges:
                ref = edge["target_id"]
                if not is_area_qualified(ref):
                    continue
                hit = resolve_ref(area, ref)
                if hit is not None and exists(str(hit[0].root), hit[1]):
                    types = pairs.setdefault((key, str(hit[0].root)), {})
                    types[edge["edge_type"]] = types.get(edge["edge_type"], 0) + 1
                else:
                    unresolved.append({"area": key, "id": entry.id, "ref": ref, "type": edge["edge_type"]})
    edges = [{"from": a, "to": b, "count": sum(t.values()), "types": dict(sorted(t.items()))} for (a, b), t in sorted(pairs.items())]
    if args.json:
        print(json.dumps({"areas": [str(a.root) for a in areas], "edges": edges, "unresolved": unresolved}, ensure_ascii=False))
        return OK

    def name(path: str) -> str:
        return os.path.relpath(path, root.resolve())

    print("areas:", ", ".join(name(str(a.root)) for a in areas) or "-")
    for edge in edges:
        print(f"{name(edge['from'])} \u2192 {name(edge['to'])}: {edge['count']} ({', '.join(edge['types'])})")
    for item in unresolved:
        print(f"unresolved: {name(item['area'])}:{item['id']} --{item['type']}--> {item['ref']}")
    return OK


def _context(args: argparse.Namespace) -> int:
    if args.map:
        return _context_map(args)
    area = _area(args.path)
    info = {
        "area_root": str(area.root),
        "records_dir": str(area.records_dir),
        "index": str(area.records_dir / "INDEX.md"),
        "focus": str(focus_path(area.records_dir)),
    }
    if args.json:
        print(json.dumps(info, ensure_ascii=False))
    else:
        for name, value in info.items():
            print(f"{name}: {value if value is not None else '-'}")
    return OK


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mem", description="Write and inspect ai-mem record files.")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--area", metavar="PATH", help="area folder (default: nearest ancestor of cwd with docs/records/)")
    common.add_argument("--json", action="store_true", help="one JSON object per action")

    add = sub.add_parser("add", parents=[common], help="create a record, or update fields of an existing one")
    add.add_argument("--id", required=True)
    add.add_argument("--type")
    add.add_argument("--topic", help="topic folder (the frontmatter `topic:` key)")
    add.add_argument("--perspective")
    add.add_argument("--cue", help="situation in which the record helps; empty string clears it")
    add.add_argument("--text")
    add.add_argument("--file", metavar="F", help="read the text from F ('-' for stdin)")
    add.add_argument("stdin", nargs="?", choices=["-"], help="read the text from stdin")
    add.set_defaults(handler=_add)

    link = sub.add_parser("link", parents=[common], help="add a typed edge from SOURCE to TARGET")
    link.add_argument("source")
    link.add_argument("target", help="bare id (same area) or <rel-area-path>:<id>")
    link.add_argument("--type", required=True, choices=get_args(EdgeType))
    link.add_argument("--to-area", metavar="PATH", help="area of TARGET; the qualified reference is built from it")
    link.set_defaults(handler=_link)

    unlink = sub.add_parser("unlink", parents=[common], help="remove the edges from SOURCE to TARGET")
    unlink.add_argument("source")
    unlink.add_argument("target", help="the target as stored in SOURCE's edges (bare id or <rel-area-path>:<id>)")
    unlink.add_argument("--type", choices=get_args(EdgeType), help="only the edge of this type (default: every type)")
    unlink.set_defaults(handler=_unlink)

    delete = sub.add_parser("delete", parents=[common], help="delete records by id")
    delete.add_argument("ids", nargs="+", metavar="ID")
    delete.set_defaults(handler=_delete)

    move = sub.add_parser("move", parents=[common], help="move records into another area (edges re-qualified)")
    move.add_argument("ids", nargs="*", metavar="ID")
    move.add_argument("--to-area", metavar="PATH")
    move.add_argument("--batch", metavar="FILE", help="TSV of source_area, id, target_area[, perspective]: one order-independent plan, rerunnable")
    move.add_argument("--dry-run", action="store_true", help="print every planned write and edge rewrite, change nothing")
    move.add_argument("--scan-root", metavar="DIR", help="where to look for referrers to report (default: common parent of both areas)")
    move.set_defaults(handler=_move)

    move_area = sub.add_parser("move-area", parents=[common], help="rename or move an area folder and rewrite every reference into and out of it")
    move_area.add_argument("old", help="the folder to move (an area, or a folder holding areas)")
    move_area.add_argument("new", help="its new path (must not exist)")
    move_area.add_argument("--root", required=True, metavar="DIR", help="the workspace: every area below it is scanned for references")
    move_area.add_argument("--dry-run", action="store_true", help="print the rewrites, the rename and what is left to you; change nothing")
    move_area.add_argument("--include-unversioned", action="store_true", help="also rewrite records in areas not under git (no undo)")
    move_area.set_defaults(handler=_move_area)

    source = sub.add_parser("source", parents=[common], help="set a source's status (only its `status:` frontmatter line changes)")
    source.add_argument("slug", help="the source's slug: docs/sources/<slug>.md")
    source.add_argument("--status", required=True, choices=SOURCE_STATUSES)
    source.set_defaults(handler=_source)

    find = sub.add_parser("find", parents=[common], help="where an id (record, reference doc or source) exists: home area, ancestor areas, then all areas below --root (read-only)")
    find.add_argument("id")
    find.add_argument("--root", metavar="DIR", help="where to look for areas (default: $AI_MEM_WORKSPACE_ROOT, else the parent of the home area)")
    find.set_defaults(handler=_find)

    context = sub.add_parser("context", help="area root, records dir, INDEX/FOCUS paths")
    context.add_argument("path", nargs="?")
    context.add_argument("--map", action="store_true", help="areas below --root and the edges between them")
    context.add_argument("--root", metavar="DIR", help="with --map: where to look for areas (default: cwd)")
    context.add_argument("--json", action="store_true")
    context.set_defaults(handler=_context)

    for name, module in (("lint", records_lint), ("doctor", doctor), ("review", review)):
        stub = sub.add_parser(name)
        module.configure(stub)
        stub.set_defaults(handler=module.run)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except CliError as exc:
        print(f"mem: {exc}", file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
