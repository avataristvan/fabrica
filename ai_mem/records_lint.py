"""`mem lint` -- check the record files of one area against `docs/reference/record-format.md`, optionally normalise them.

Records are read as plain files, not through the repository: `get_by_ids` silently skips a record it
cannot parse, and lint exists to name exactly those (learning_handwritten_records_drift_from_format_2026_10_10).
`--fix` rewrites only the frontmatter shape of files inside the given area; the body is never touched and
a content-preservation guard refuses any rewrite that would lose a frontmatter value or a byte of body.

Exit codes: 0 clean, 1 findings remain, 2 usage or invalid input, 3 migration pending (`--fix` only).
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import get_args

from ai_mem import upgrade_guard
from ai_mem.domain.memory import EdgeType, parse_edges
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import index_is_current, regenerate_index
from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    KIND_BY_TYPE,
    is_contained,
    is_safe_area,
    is_safe_entry_id,
    iter_record_files,
    reference_dir,
    sources_dir,
    write_atomic,
)
from ai_mem.infrastructure.areas import Area, find_area, parse_ref, resolve_ref

OK, FINDINGS, USAGE, PENDING = 0, 1, 2, 3

_EDGE_TYPES = frozenset(get_args(EdgeType))
_INDEX_FILENAME = "INDEX.md"
_KEY = re.compile(r"^[A-Za-z0-9_-]+$")
_FIXABLE_REQUIRED = ("area", "created")
_GIT_TIMEOUT = 20


class Code:
    """Finding codes; a typo is an AttributeError, not a silently unmatched string."""
    UNPARSABLE = "unparsable"
    FRONTMATTER_SHAPE = "frontmatter-shape"
    FRONTMATTER_FORMAT = "frontmatter-format"
    MISSING_FIELD = "missing-field"
    BAD_NUMBER = "bad-number"
    VALUE_CHARS = "value-chars"
    ID_STEM = "id-stem"
    ID_COLON = "id-colon"
    ID_CHARS = "id-chars"
    ID_UNSAFE = "id-unsafe"
    TYPE_INVALID = "type-invalid"
    TYPE_FOLDER = "type-folder"
    TOPIC_FOLDER = "topic-folder"
    LAYOUT = "layout"
    PERSPECTIVE_USER = "perspective-user"
    EDGES_JSON = "edges-json"
    EDGE_TYPE = "edge-type"
    EDGE_TARGET_INVALID = "edge-target-invalid"
    EDGE_DANGLING = "edge-dangling"
    EDGE_UNRESOLVED = "edge-unresolved"
    EDGE_DANGLING_XAREA = "edge-dangling-xarea"
    INDEX_MISSING = "index-missing"
    INDEX_STALE = "index-stale"


@dataclass(frozen=True)
class Finding:
    file: Path
    code: str
    message: str
    fixable: bool


@dataclass
class RawRecord:
    """One record file as found on disk. `fields is None` means the frontmatter could not be read (see `problem`)."""
    path: Path
    rel: Path  # relative to the records directory
    text: str
    fields: list[tuple[str, str]] | None
    body: str
    problem: str | None = None
    leading_fence: bool = False
    blank_missing: bool = False

    def value(self, key: str) -> str:
        return dict(self.fields or []).get(key, "")


def git_output(cwd: Path, *args: str) -> str | None:
    """stdout of `git -C cwd <args>`, or None when git fails (not a repo, no git, timeout)."""
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    try:
        result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=_GIT_TIMEOUT, env=env)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout if result.returncode == 0 else None


def _has_control(value: str, allow_tab: bool = False) -> bool:
    """Control characters (Cc) and the Unicode line separators `str.splitlines` breaks lines at."""
    return any((unicodedata.category(c) == "Cc" and not (allow_tab and c == "\t")) or c in "\u2028\u2029" for c in value)


def _split(text: str) -> tuple[list[tuple[str, str]], str, bool, bool] | str:
    """`(fields, body, leading_fence, blank_missing)`, or the reason the frontmatter cannot be read.

    Accepts the canonical block (`key: value` lines, `---`, blank line, body), an optional leading `---`
    fence and a missing blank line after the closing `---`. The body is everything after that blank line, verbatim.
    """
    lines = text.split("\n")
    leading = lines[0].rstrip() == "---"
    start = 1 if leading else 0
    separator = next((i for i in range(start, len(lines)) if lines[i].rstrip() == "---"), None)
    if separator is None:
        return "no '---' frontmatter separator"
    fields: list[tuple[str, str]] = []
    for line in lines[start:separator]:
        if not line.strip():
            continue
        key, colon, value = line.partition(":")
        key = key.strip()
        if not colon or not _KEY.fullmatch(key):
            return f"frontmatter line is not 'key: value': {line.strip()[:60]!r}"
        if any(existing == key for existing, _ in fields):
            return f"duplicate frontmatter key {key!r}"
        fields.append((key, value.strip()))
    rest = lines[separator + 1:]
    blank_missing = bool(rest) and rest[0] != ""
    body = "\n".join(rest if blank_missing else rest[1:])
    return fields, body, leading, blank_missing


def _canonical(fields: list[tuple[str, str]], body: str) -> str:
    values = dict(fields)
    ordered = [(key, values[key]) for key in adr_markdown.KEY_ORDER if key in values]
    ordered += [(key, value) for key, value in fields if key not in adr_markdown.KNOWN_KEYS]
    ordered += [(key, values[key]) for key in ("cue",) if key in values]
    lines = [f"{key}: {value}" if value else f"{key}:" for key, value in ordered]
    return "\n".join(lines) + "\n---\n\n" + body


def _read(records_dir: Path, path: Path) -> RawRecord:
    rel = path.relative_to(records_dir)
    if not is_contained(path, records_dir, allow_symlink=False):
        return RawRecord(path, rel, "", None, "", problem="symlink or path resolving outside the records directory (not read, never rewritten)")
    try:
        text = path.read_bytes().decode("utf-8")  # no newline translation: the body must survive byte for byte
    except (OSError, UnicodeDecodeError) as exc:
        return RawRecord(path, rel, "", None, "", problem=f"unreadable: {exc.__class__.__name__}")
    parsed = _split(text)
    if isinstance(parsed, str):
        return RawRecord(path, rel, text, None, "", problem=parsed)
    fields, body, leading, blank_missing = parsed
    return RawRecord(path, rel, text, fields, body, leading_fence=leading, blank_missing=blank_missing)


def read_area(area: Area) -> list[RawRecord]:
    return [_read(area.records_dir, path) for path in iter_record_files(area.records_dir)]


def edge_targets(record: RawRecord) -> list[str]:
    """Edge target ids of a record, [] when it has none or its edges are unreadable."""
    raw = record.value("edges")
    try:
        edges = json.loads(raw) if raw else []
        return [edge["target_id"] for edge in edges if isinstance(edge["target_id"], str)]
    except (ValueError, TypeError, KeyError, RecursionError):
        return []


def _stems(area: Area, cache: dict[Path, set[str]]) -> set[str]:
    """Ids an edge may target: the records, plus the plain reference docs (`mem link` resolves those too) and the sources."""
    if area.root not in cache:
        cache[area.root] = {path.stem for path in iter_record_files(area.records_dir)}
        for directory in (reference_dir(area.records_dir), sources_dir(area.records_dir)):
            if directory.is_dir():
                cache[area.root] |= {path.stem for path in directory.glob("*.md")}
    return cache[area.root]


def _check_edges(area: Area, record: RawRecord, add, cache: dict[Path, set[str]]) -> None:
    raw = record.value("edges")
    if not raw:
        return
    try:
        edges = parse_edges(raw)
    except ValueError as exc:
        add(Code.EDGES_JSON, f"{exc} ({exc.__class__.__name__})")
        return
    for edge in edges:
        target, edge_type = edge["target_id"], edge["edge_type"]
        if edge_type not in _EDGE_TYPES:
            add(Code.EDGE_TYPE, f"edge type {edge_type!r} is not one of {sorted(_EDGE_TYPES)}")
        try:
            rel, _ = parse_ref(target)
        except ValueError:
            add(Code.EDGE_TARGET_INVALID, f"edge target {target!r} is not a valid id or <area-path>:<id> reference")
            continue
        if rel is None:
            if target not in _stems(area, cache):
                add(Code.EDGE_DANGLING, f"edge target {target!r} does not exist in this area")
            continue
        resolved = resolve_ref(area, target)
        if resolved is None:
            add(Code.EDGE_UNRESOLVED, f"edge target {target!r} points at no area")
        elif resolved[1] not in _stems(resolved[0], cache):
            add(Code.EDGE_DANGLING_XAREA, f"edge target {target!r} does not exist in the area it points at")


def _check_record(area: Area, record: RawRecord, add, cache: dict[Path, set[str]]) -> None:
    if record.fields is None:
        add(Code.UNPARSABLE, f"frontmatter cannot be read: {record.problem}")
        return
    fields = dict(record.fields)
    entry_id, entry_type, topic = fields.get("id", ""), fields.get("type", ""), fields.get("area", "")
    shape = [reason for reason, present in (("leading '---' fence", record.leading_fence),
                                            ("no blank line after the closing '---'", record.blank_missing)) if present]
    if shape:
        add(Code.FRONTMATTER_SHAPE, "; ".join(shape), True)
    elif record.text != _canonical(record.fields, record.body):
        add(Code.FRONTMATTER_FORMAT, "field order or spacing is not canonical", True)

    for key in ("id", "type"):
        if not fields.get(key):
            add(Code.MISSING_FIELD, f"required field {key!r} is missing")
    for key in _FIXABLE_REQUIRED:
        if not fields.get(key):
            add(Code.MISSING_FIELD, f"required field {key!r} is missing", True)
    for key, value in record.fields:
        if _has_control(value, allow_tab=True):
            add(Code.VALUE_CHARS, f"value of {key!r} contains control or line-break characters")
    for key in ("created", "valid_until"):
        if fields.get(key):
            try:
                float(fields[key])
            except ValueError:
                add(Code.BAD_NUMBER, f"{key} {fields[key]!r} is not a number")

    stem = record.path.stem
    if entry_id and entry_id != stem:
        add(Code.ID_STEM, f"id {entry_id!r} differs from the file name {stem!r}")
    for label, value in (("id", entry_id), ("file name", stem)):
        if value and _has_control(value):
            add(Code.ID_CHARS, f"{label} {value!r} contains control or non-printable characters")
        elif value and ":" in value:
            add(Code.ID_COLON, f"{label} {value!r} contains ':' (reserved for area-qualified references)")
        elif value and not is_safe_entry_id(value):
            add(Code.ID_UNSAFE, f"{label} {value!r} is not a safe record id")

    parts = record.rel.parts
    kind = KIND_BY_TYPE.get(entry_type)
    if entry_type and entry_type not in ADR_TYPES:
        add(Code.TYPE_INVALID, f"type {entry_type!r} is not a record type {sorted(ADR_TYPES)}")
    if len(parts) != 3:
        add(Code.LAYOUT, f"record is not at <topic>/<kind>/<id>.md (found {record.rel.as_posix()})")
    else:
        if kind and parts[1] != kind:
            add(Code.TYPE_FOLDER, f"type {entry_type!r} belongs in folder {kind!r}, found {parts[1]!r}")
        if topic and parts[0] != topic:
            add(Code.TOPIC_FOLDER, f"area: {topic!r} differs from the topic folder {parts[0]!r}")

    if entry_type == "user" and fields.get("perspective") != "user":
        conflict = bool(fields.get("perspective"))
        add(Code.PERSPECTIVE_USER, "user record must carry 'perspective: user'" + (f" (found {fields['perspective']!r})" if conflict else ""), not conflict)
    _check_edges(area, record, add, cache)


def _check_index(area: Area, records: list[RawRecord]) -> list[Finding]:
    if not records:
        return []
    index = area.records_dir / _INDEX_FILENAME
    if not index.exists():
        return [Finding(index, Code.INDEX_MISSING, "INDEX.md does not exist", True)]
    if not index_is_current(area.records_dir):
        return [Finding(index, Code.INDEX_STALE, "INDEX.md differs from what the generator would write", True)]
    return []


def lint_records(area: Area, records: list[RawRecord], check_index: bool = True) -> list[Finding]:
    findings: list[Finding] = []
    cache: dict[Path, set[str]] = {}
    for record in records:
        def add(code: str, message: str, fixable: bool = False, _path: Path = record.path) -> None:
            findings.append(Finding(_path, code, message, fixable))
        _check_record(area, record, add, cache)
    if check_index:
        findings += _check_index(area, records)
    return sorted(findings, key=lambda f: (str(f.file), f.code, f.message))


def lint(area: Area) -> list[Finding]:
    return lint_records(area, read_area(area))


def _created_from_history(area: Area, path: Path) -> str:
    added = git_output(area.root, "log", "--follow", "--diff-filter=A", "--format=%ct", "--", str(path))
    stamps = [line for line in (added or "").splitlines() if line.strip()]
    return str(float(stamps[-1])) if stamps else str(path.stat().st_mtime)


def _normalise(area: Area, record: RawRecord) -> tuple[str, list[str]] | str:
    """`(new_text, changes)` for a readable record, or the reason it is not fixable."""
    assert record.fields is not None
    fields = list(record.fields)
    values = dict(fields)
    if any(_has_control(value, allow_tab=True) for _, value in fields):
        return "a frontmatter value contains control characters"
    changes: list[str] = []

    def put(key: str, value: str) -> None:
        for i, (existing, _) in enumerate(fields):
            if existing == key:
                fields[i] = (key, value)
                return
        fields.append((key, value))

    if record.leading_fence:
        changes.append("dropped leading '---' fence")
    if record.blank_missing:
        changes.append("added blank line after the separator")
    parts = record.rel.parts
    if not values.get("area"):
        if len(parts) != 3 or not is_safe_area(parts[0]):
            return "area: missing and the topic folder is not usable"
        put("area", parts[0])
        changes.append(f"area: {parts[0]} (from folder)")
    if not values.get("created"):
        created = _created_from_history(area, record.path)
        put("created", created)
        changes.append(f"created: {created}")
    if values.get("type") == "user" and not values.get("perspective"):
        put("perspective", "user")
        changes.append("perspective: user")

    new_text = _canonical(fields, record.body)
    if new_text != record.text and not changes:
        changes.append("field order / spacing")
    return new_text, changes


def _preserved(record: RawRecord, new_text: str) -> bool:
    """Content-preservation guard: every original frontmatter value and the whole body survive the rewrite."""
    assert record.fields is not None
    again = _split(new_text)
    if isinstance(again, str):
        return False
    new_fields, new_body, _, _ = again
    new_values = dict(new_fields)
    if new_body != record.body or (record.body and record.body not in new_text):
        return False
    if len(new_fields) < len(record.fields):
        return False
    try:
        adr_markdown.parse(new_text)
    except ValueError:
        return False
    return all(new_values.get(key) == value and (not value or value in new_text) for key, value in record.fields if value)


def _emit(args: argparse.Namespace, area: Area, **payload) -> None:
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return
    file = payload.get("file")
    where = f"{Path(file).relative_to(area.root).as_posix()}: " if file else ""
    print(f"{payload['action']} {where}{payload.get('code') or ''}{' - ' if payload.get('code') else ''}{payload['message']}")


def _fix(area: Area, args: argparse.Namespace) -> list[RawRecord]:
    """Normalise the records, then regenerate INDEX.md if it is stale. Returns the records as they are now."""
    records = read_area(area)
    changed = False
    for record in records:
        if record.fields is None:
            continue
        outcome = _normalise(area, record)
        if isinstance(outcome, str):
            _emit(args, area, action="skipped", file=str(record.path), message=f"not fixable: {outcome}")
            continue
        new_text, changes = outcome
        if new_text == record.text:
            continue
        if not _preserved(record, new_text):
            _emit(args, area, action="skipped", file=str(record.path), message="not fixable: content-preservation guard refused the rewrite")
            continue
        write_atomic(record.path, new_text)
        changed = True
        _emit(args, area, action="fixed", file=str(record.path), message="; ".join(changes))
    if changed:
        records = read_area(area)
    if _check_index(area, records):
        regenerate_index(area.records_dir)
        _emit(args, area, action="fixed", file=str(area.records_dir / _INDEX_FILENAME), message="regenerated")
    return records


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--area", metavar="PATH", help="area folder (default: nearest ancestor of cwd with docs/records/)")
    parser.add_argument("--fix", action="store_true", help="normalise frontmatter shape and regenerate INDEX.md (writes inside the area only)")
    parser.add_argument("--json", action="store_true", help="one JSON object per finding / change")


def run(args: argparse.Namespace) -> int:
    area = find_area(Path(args.area).expanduser() if args.area else Path.cwd())
    if area is None:
        print("mem lint: no area (no docs/records/ in this folder or above)", file=sys.stderr)
        return USAGE
    if args.fix:
        db_path = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local" / "share" / "ai-mem"))
        try:
            upgrade_guard.refuse_if_pending(db_path)
        except upgrade_guard.MigrationPending as exc:
            print(f"mem lint: {exc}", file=sys.stderr)
            return PENDING
        # INDEX.md is fresh after _fix by construction, so it is not rendered a second time.
        findings = lint_records(area, _fix(area, args), check_index=False)
    else:
        findings = lint(area)
    for finding in findings:
        _emit(args, area, action="finding", file=str(finding.file), code=finding.code, fixable=finding.fixable, message=finding.message)
    if not findings and not args.json:
        print("clean")
    return FINDINGS if findings else OK
