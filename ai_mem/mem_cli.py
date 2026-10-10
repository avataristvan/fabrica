"""`mem` -- the write contract for record files (stdlib only; reads go through Read/Grep).

Every write goes through the existing use cases over `FileMemoryRepository` in area mode (the
repository key is the area root), after the upgrade guard. Ids and area paths are validated here,
before any use case, path join or glob (pattern_tool_argument_ids_are_hostile_input).

Exit codes: 0 ok, 1 conflict / not found, 2 usage or invalid input, 3 migration pending.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import get_args

from ai_mem import doctor, records_lint, upgrade_guard
from ai_mem.application.add_edge import AddEdgeUseCase
from ai_mem.application.add_memory import AddMemoryUseCase
from ai_mem.application.delete_memory import DeleteMemoryUseCase
from ai_mem.application.experience_index import normalize_cue
from ai_mem.domain.memory import EdgeType, MemoryRepository
from ai_mem.infrastructure.adr_paths import FOCUS_ID, find_adr_files, focus_path, is_safe_entry_id, records_home
from ai_mem.infrastructure.areas import (
    Area,
    AreaRefResolver,
    area_records_dir,
    find_area,
    parse_ref,
    qualify,
)
from ai_mem.infrastructure.file_repository import FileMemoryRepository

OK, CONFLICT, USAGE, PENDING = 0, 1, 2, 3


class CliError(Exception):
    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


def _db_path() -> Path:
    return Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local" / "share" / "ai-mem"))


def _repository() -> MemoryRepository:
    return FileMemoryRepository(_db_path(), records_dir_for=area_records_dir)


def _guard_writes() -> None:
    try:
        upgrade_guard.refuse_if_pending(_db_path())
    except upgrade_guard.MigrationPending as exc:
        raise CliError(str(exc), PENDING) from exc


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
    _guard_writes()
    entry_id = _bare_id(args.id)
    area = _area(args.area)
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


def _link(args: argparse.Namespace) -> int:
    _guard_writes()
    source = _bare_id(args.source)
    area = _area(args.area)
    if args.to_area:
        to_area = _area(args.to_area)
        target = qualify(area, to_area, _bare_id(args.target))
    else:
        try:
            parse_ref(args.target)
        except ValueError as exc:
            raise CliError(str(exc), USAGE) from exc
        target = args.target

    repo, key = _repository(), str(area.root)
    try:
        AddEdgeUseCase(repo, area_refs=AreaRefResolver()).execute(key, source, target, args.type)
    except ValueError as exc:
        raise CliError(str(exc), CONFLICT) from exc
    _emit(args, {"action": "linked", "source": source, "target": target, "type": args.type, "area": key},
          f"linked {source} --{args.type}--> {target}")
    return OK


def _delete(args: argparse.Namespace) -> int:
    _guard_writes()
    ids = list(dict.fromkeys(_bare_id(entry_id) for entry_id in args.ids))
    area = _area(args.area)
    repo, key = _repository(), str(area.root)
    present = {entry.id for entry in repo.get_by_ids(key, ids)}
    if present:
        DeleteMemoryUseCase(repo).execute(key, [entry_id for entry_id in ids if entry_id in present])
    missing = [entry_id for entry_id in ids if entry_id not in present]
    for entry_id in ids:
        action = "deleted" if entry_id in present else "not_found"
        _emit(args, {"action": action, "id": entry_id, "area": key}, f"{action.replace('_', ' ')} {entry_id}")
    return CONFLICT if missing else OK


def _context(args: argparse.Namespace) -> int:
    area = _area(args.path)
    home = records_home()
    legacy = area.root.name if home is not None and area.root.parent == home.resolve() else None
    info = {
        "area_root": str(area.root),
        "records_dir": str(area.records_dir),
        "index": str(area.records_dir / "INDEX.md"),
        "focus": str(focus_path(area.records_dir)),
        "legacy_collection": legacy,
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
    add.add_argument("--topic", help="topic folder (the frontmatter `area:` key)")
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

    delete = sub.add_parser("delete", parents=[common], help="delete records by id")
    delete.add_argument("ids", nargs="+", metavar="ID")
    delete.set_defaults(handler=_delete)

    context = sub.add_parser("context", help="area root, records dir, INDEX/FOCUS paths")
    context.add_argument("path", nargs="?")
    context.add_argument("--json", action="store_true")
    context.set_defaults(handler=_context)

    for name, module in (("lint", records_lint), ("doctor", doctor)):
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
