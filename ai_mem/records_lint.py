"""`mem lint` -- check the record files of one area against `docs/reference/record-format.md`, optionally normalise them.

Records are read as plain files, not through the repository: `get_by_ids` silently skips a record it
cannot parse, and lint exists to name exactly those (learning_handwritten_records_drift_from_format_2026_10_10).
`--fix` rewrites only the frontmatter shape of files inside the given area, and repoints edge targets whose id
lives in exactly one area; the body is never touched and a content-preservation guard refuses any rewrite that
would lose a frontmatter value or a byte of body.

Exit codes: 0 clean, 1 findings remain, 2 usage or invalid input.
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
from typing import Callable, get_args

from ai_mem.domain.memory import EdgeType, parse_edges
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.adr_index import index_is_current, regenerate_index
from ai_mem.infrastructure.adr_paths import (
    ADR_TYPES,
    BACKLOG_FILENAME,
    KIND_BY_TYPE,
    RETIRED_TYPES,
    is_contained,
    is_safe_area,
    is_safe_entry_id,
    iter_record_files,
    reference_files,
    sources_dir,
    write_atomic,
)
from ai_mem.infrastructure.areas import Area, ancestor_areas, discover_areas, find_area, parse_ref, qualify, resolve_ref
from ai_mem.infrastructure.record_links import area_of_records_dir, href_for_ref, ref_for_href

OK, FINDINGS, USAGE = 0, 1, 2

_EDGE_TYPES = frozenset(get_args(EdgeType))
_INDEX_FILENAME = "INDEX.md"
_ITEM_MARKER = re.compile(r"^(?:\d+[.)]|[*+-])\s+")
_KEY = re.compile(r"^[A-Za-z0-9_-]+$")
_FIXABLE_REQUIRED = ("topic", "created")
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
    LEGACY_TOPIC_KEY = "legacy-topic-key"
    TOPIC_CONFLICT = "topic-conflict"
    LAYOUT = "layout"
    PERSPECTIVE_USER = "perspective-user"
    EDGES_JSON = "edges-json"
    EDGES_SECTION = "edges-section"
    LEGACY_REFS = "legacy-refs"
    LINK_STALE = "link-stale"
    BARE_ID = "bare-id"
    EDGE_TYPE = "edge-type"
    EDGE_TARGET_INVALID = "edge-target-invalid"
    EDGE_DANGLING = "edge-dangling"
    EDGE_UNRESOLVED = "edge-unresolved"
    EDGE_DANGLING_XAREA = "edge-dangling-xarea"
    INDEX_MISSING = "index-missing"
    INDEX_STALE = "index-stale"
    BACKLOG_FORMAT = "backlog-format"
    BACKLOG_LINE = "backlog-line"


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
    # Edges from the closing `## Edges` section (relative links), as {target_id, edge_type}; superseded_by is not one.
    section_edges: list[dict] | None = None
    section_links: list[adr_markdown.EdgeLink] | None = None  # every link of the section, superseded_by included
    section_problem: str | None = None

    def value(self, key: str) -> str:
        return dict(self.fields or []).get(key, "")

    def all_edges(self) -> list[dict]:
        """Frontmatter `edges` (older format) followed by the `## Edges` links; ValueError when either is malformed."""
        if self.section_problem:
            raise ValueError(self.section_problem)
        raw = self.value("edges")
        return (parse_edges(raw) if raw else []) + list(self.section_edges or [])


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


def _modernise(fields: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], bool]:
    """`fields` with the legacy `area:` key renamed to `topic:` in place, and whether the two keys disagree.

    With both keys present and equal the legacy line is dropped; with differing values both stay (a conflict
    lint reports and `--fix` refuses).
    """
    legacy = adr_markdown.LEGACY_TOPIC_KEY
    values = dict(fields)
    if legacy not in values:
        return fields, False
    if "topic" not in values:
        return [("topic" if key == legacy else key, value) for key, value in fields], False
    if values["topic"] == values[legacy]:
        return [(key, value) for key, value in fields if key != legacy], False
    return fields, True


def _canonical(fields: list[tuple[str, str]], body: str, topic_key: str = "topic") -> str:
    values = dict(fields)
    ordered = [(key, values[key]) for key in adr_markdown.LEGACY_KEY_ORDER if key in values]
    ordered += [(key, value) for key, value in fields if key not in adr_markdown.KNOWN_KEYS]
    ordered += [(key, values[key]) for key in ("cue",) if key in values]
    ordered = [(topic_key if key == "topic" else key, value) for key, value in ordered]
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
    record = RawRecord(path, rel, text, fields, body, leading_fence=leading, blank_missing=blank_missing)
    area = area_of_records_dir(records_dir)
    try:
        _, links = adr_markdown.split_edges_section(body)
        record.section_links = links
        record.section_edges = [{"target_id": ref_for_href(path, area, link.href), "edge_type": link.edge_type}
                                for link in links if link.edge_type != adr_markdown.SUPERSEDED_BY]
    except ValueError as exc:
        record.section_problem = str(exc)
    return record


def read_area(area: Area) -> list[RawRecord]:
    return [_read(area.records_dir, path) for path in iter_record_files(area.records_dir)]


def edge_targets(record: RawRecord) -> list[str]:
    """Edge target ids of a record, [] when it has none or its edges are unreadable."""
    raw = record.value("edges")
    try:
        edges = json.loads(raw) if raw else []
        targets = [edge["target_id"] for edge in edges if isinstance(edge["target_id"], str)]
    except (ValueError, TypeError, KeyError, RecursionError):
        targets = []
    return targets + [edge["target_id"] for edge in record.section_edges or []]


def _stems(area: Area, cache: dict[Path, set[str]]) -> set[str]:
    """Ids an edge may target: the records, plus the plain reference docs (`mem link` resolves those too) and the sources."""
    if area.root not in cache:
        cache[area.root] = {path.stem for path in iter_record_files(area.records_dir)}
        cache[area.root] |= {path.stem for path in reference_files(area.records_dir)}
        directory = sources_dir(area.records_dir)
        if directory.is_dir():
            cache[area.root] |= {path.stem for path in directory.glob("*.md")}
    return cache[area.root]


def _edge_problem(area: Area, target: str, cache: dict[Path, set[str]]) -> tuple[str, str] | None:
    """`(code, message)` when an edge target is invalid or leads nowhere, else None."""
    try:
        rel, _ = parse_ref(target)
    except ValueError:
        return Code.EDGE_TARGET_INVALID, f"edge target {target!r} is not a valid id or <area-path>:<id> reference"
    if rel is None:
        return None if target in _stems(area, cache) else (Code.EDGE_DANGLING, f"edge target {target!r} does not exist in this area")
    resolved = resolve_ref(area, target)
    if resolved is None:
        return Code.EDGE_UNRESOLVED, f"edge target {target!r} points at no area"
    if resolved[1] not in _stems(resolved[0], cache):
        return Code.EDGE_DANGLING_XAREA, f"edge target {target!r} does not exist in the area it points at"
    return None


def _check_edges(area: Area, record: RawRecord, add, cache: dict[Path, set[str]]) -> None:
    raw = record.value("edges")
    edges: list[dict] = []
    if raw:
        try:
            edges = parse_edges(raw)
        except ValueError as exc:
            add(Code.EDGES_JSON, f"{exc} ({exc.__class__.__name__})")
            return
    if record.section_problem:
        add(Code.EDGES_SECTION, record.section_problem)
    for link in record.section_links or []:
        if (record.path.parent / link.href).is_file():
            continue
        try:
            ref = ref_for_href(record.path, area, link.href)
        except ValueError as exc:
            add(Code.EDGE_TARGET_INVALID, str(exc))
            continue
        problem = _edge_problem(area, ref, cache)
        if problem is None:
            add(Code.LINK_STALE, f"link {link.href!r} leads nowhere, but {ref!r} exists at another path", True)
        elif link.edge_type == adr_markdown.SUPERSEDED_BY:
            add(*problem)
    for edge in edges + list(record.section_edges or []):
        if edge["edge_type"] not in _EDGE_TYPES:
            add(Code.EDGE_TYPE, f"edge type {edge['edge_type']!r} is not one of {sorted(_EDGE_TYPES)}")
        problem = _edge_problem(area, edge["target_id"], cache)
        if problem is not None:
            add(*problem)


def _search_root(area: Area) -> Path:
    """Where `--fix` looks for a lost edge target: $AI_MEM_WORKSPACE_ROOT, else the outermost area above, else the parent folder."""
    root = os.environ.get("AI_MEM_WORKSPACE_ROOT")
    if root:
        return Path(root).expanduser().resolve()
    above = ancestor_areas(area, Path(area.root.anchor))
    return above[-1].root if above else area.root.parent


def _repoint_edges(area: Area, record: RawRecord, cache: dict[Path, set[str]], areas: Callable[[], list[Area]]) -> tuple[str, list[str]]:
    """The `edges` value with each lost target repointed to the one area that holds its id (an area moved, a prefix went stale).

    A target whose id is in no area, or in more than one, stays as it is and lint keeps reporting it.
    """
    raw = record.value("edges")
    try:
        edges = parse_edges(raw) if raw else []
    except ValueError:
        return raw, []
    changes = []
    for edge in edges:
        problem = _edge_problem(area, edge["target_id"], cache)
        if problem is None or problem[0] == Code.EDGE_TARGET_INVALID:
            continue
        entry_id = parse_ref(edge["target_id"])[1]
        target = _unique_holder_ref(area, entry_id, cache, areas)
        if target is None:
            continue
        changes.append(f"edge {edge['target_id']} -> {target}")
        edge["target_id"] = target
    if not changes:
        return raw, []
    return json.dumps([{"target_id": e["target_id"], "edge_type": e["edge_type"]} for e in edges]), changes


def _unique_holder_ref(area: Area, entry_id: str, cache: dict[Path, set[str]],
                       areas: Callable[[], list[Area]]) -> str | None:
    """`entry_id` qualified from `area` when exactly one area holds it and the reference is valid, else None."""
    holders = [candidate for candidate in areas() if entry_id in _stems(candidate, cache)]
    if len(holders) != 1:
        return None
    try:
        return qualify(area, holders[0], entry_id)
    except ValueError:
        return None


def _relink_section(area: Area, record: RawRecord, cache: dict[Path, set[str]], areas: Callable[[], list[Area]]) -> tuple[str, list[str]]:
    """The body with every `## Edges` link pointing at where its target lies now: a link whose target moved
    inside its area gets the new path, a target that left its area is repointed when exactly one area holds it.
    A link that leads nowhere and cannot be repointed stays as it is (lint keeps reporting it)."""
    if not record.section_links or record.section_problem:
        return record.body, []
    text, _ = adr_markdown.split_edges_section(record.body)
    links, changes = [], []
    for link in record.section_links:
        try:
            ref = ref_for_href(record.path, area, link.href)
        except ValueError:
            links.append(link)
            continue
        problem = _edge_problem(area, ref, cache)
        if problem is not None and problem[0] != Code.EDGE_TARGET_INVALID:
            target = _unique_holder_ref(area, parse_ref(ref)[1], cache, areas)
            if target is not None:
                ref, problem = target, None
        href = href_for_ref(record.path, area, ref) if problem is None else link.href
        if href != link.href:
            changes.append(f"link {link.href} -> {href}")
        links.append(adr_markdown.EdgeLink(link.edge_type, href))
    return (adr_markdown.render_edges_section(text, links), changes) if changes else (record.body, [])


# Prose references: a record named by its bare id (or `<rel>:<id>`) in the text becomes a relative link.
_SKIP = re.compile(r"(?ms)^(```|~~~).*?^\1[^\n]*$|\[[^\]\n]*\]\([^)\s]*\)|`[^`\n]+`")
_PROSE_REF = re.compile(r"(?<![\w/.:\[-])((?:\.\.?(?:/[\w.-]+)*:)?)([A-Za-z0-9][\w-]*[_-][\w-]*)(?![\w/-])(?!\.[A-Za-z])")


def _prose_target(area: Area, record: RawRecord, prefix: str, entry_id: str,
                  cache: dict[Path, set[str]], areas: Callable[[], list[Area]]) -> str | None:
    """The reference a prose token names, or None when it names no record, reference doc or source (or several)."""
    if entry_id == record.path.stem or not is_safe_entry_id(entry_id):
        return None
    if prefix:
        resolved = resolve_ref(area, prefix + entry_id)
        return prefix + entry_id if resolved is not None and resolved[1] in _stems(resolved[0], cache) else None
    if entry_id in _stems(area, cache):
        return entry_id
    return _unique_holder_ref(area, entry_id, cache, areas)


def _link_prose(area: Area, record: RawRecord, text: str, cache: dict[Path, set[str]],
                areas: Callable[[], list[Area]]) -> tuple[str, list[str]]:
    """`text` with every record id named in prose turned into a relative link; fenced code, existing links
    and inline code longer than one id stay as they are. Returns the new text and the ids it linked."""
    linked: list[str] = []

    def link(prefix: str, entry_id: str) -> str | None:
        ref = _prose_target(area, record, prefix, entry_id, cache, areas)
        if ref is None:
            return None
        linked.append(ref)
        return f"[{entry_id}]({href_for_ref(record.path, area, ref)})"

    def plain(segment: str) -> str:
        return _PROSE_REF.sub(lambda m: link(m.group(1), m.group(2)) or m.group(0), segment)

    out, pos = [], 0
    for match in _SKIP.finditer(text):
        out.append(plain(text[pos:match.start()]))
        token = match.group(0)
        whole = _PROSE_REF.fullmatch(token[1:-1]) if token.startswith("`") else None
        out.append((link(whole.group(1), whole.group(2)) if whole else None) or token)
        pos = match.end()
    out.append(plain(text[pos:]))
    return "".join(out), linked


def _check_record(area: Area, record: RawRecord, add, cache: dict[Path, set[str]]) -> None:
    if record.fields is None:
        add(Code.UNPARSABLE, f"frontmatter cannot be read: {record.problem}")
        return
    modern, conflict = _modernise(record.fields)
    fields = dict(modern)
    entry_id, entry_type, topic = fields.get("id", ""), fields.get("type", ""), fields.get("topic", "")
    legacy_key = adr_markdown.LEGACY_TOPIC_KEY
    legacy = legacy_key in dict(record.fields)
    if conflict:
        add(Code.TOPIC_CONFLICT, f"topic: {fields['topic']!r} and legacy area: {dict(record.fields)[legacy_key]!r} differ")
    elif legacy:
        add(Code.LEGACY_TOPIC_KEY, "legacy key 'area:' (now 'topic:')", True)
    shape = [reason for reason, present in (("leading '---' fence", record.leading_fence),
                                            ("no blank line after the closing '---'", record.blank_missing)) if present]
    if shape:
        add(Code.FRONTMATTER_SHAPE, "; ".join(shape), True)
    elif not conflict and record.text != _canonical(modern, record.body, legacy_key if legacy else "topic"):
        add(Code.FRONTMATTER_FORMAT, "field order or spacing is not canonical", True)

    legacy_refs = [key for key in adr_markdown.LEGACY_REF_KEYS if key in fields]
    if legacy_refs:
        add(Code.LEGACY_REFS, f"{', '.join(legacy_refs)} in the frontmatter (now: the file name, and links in '{adr_markdown.EDGES_HEADING}')", True)
    if not fields.get("type"):  # no `id:` needed: the file name is the record's name
        add(Code.MISSING_FIELD, "required field 'type' is missing")
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
    if entry_type in RETIRED_TYPES:
        add(Code.TYPE_INVALID, f"type {entry_type!r}: {RETIRED_TYPES[entry_type]}")
    elif entry_type and entry_type not in ADR_TYPES:
        add(Code.TYPE_INVALID, f"type {entry_type!r} is not a record type {sorted(ADR_TYPES)}")
    if len(parts) != 3:
        add(Code.LAYOUT, f"record is not at <topic>/<kind>/<id>.md (found {record.rel.as_posix()})")
    else:
        if kind and parts[1] != kind:
            add(Code.TYPE_FOLDER, f"type {entry_type!r} belongs in folder {kind!r}, found {parts[1]!r}")
        if topic and parts[0] != topic:
            add(Code.TOPIC_FOLDER, f"topic: {topic!r} differs from the topic folder {parts[0]!r}")

    if entry_type == "user" and fields.get("perspective") != "user":
        conflict = bool(fields.get("perspective"))
        add(Code.PERSPECTIVE_USER, "user record must carry 'perspective: user'" + (f" (found {fields['perspective']!r})" if conflict else ""), not conflict)
    _check_edges(area, record, add, cache)
    if not record.section_problem:
        text, _ = adr_markdown.split_edges_section(record.body)
        _, linked = _link_prose(area, record, text, cache, lambda: [area])
        if linked:
            add(Code.BARE_ID, f"names {len(linked)} record(s) by bare id in the text, e.g. {linked[0]!r}: write a relative link", True)


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


def _split_backlog(text: str) -> tuple[list[str], list[str]]:
    """(header, rest): the header is the leading paragraph up to the first blank line, unless the file starts with an item."""
    lines = text.rstrip("\n").split("\n")
    if not lines or _ITEM_MARKER.match(lines[0]):
        return [], lines
    blank = next((i for i, line in enumerate(lines) if not line.strip()), len(lines))
    return lines[:blank], lines[blank:]


def normalise_backlog(text: str) -> str:
    """BACKLOG.md in its canonical form: header, one blank line, one unnumbered `- ` line per item, no blank lines between
    items. The order of the lines is the order of work, so it is never changed; a line that is no item is kept as it is."""
    header, rest = _split_backlog(text)
    items = [_ITEM_MARKER.sub("- ", line, count=1) for line in rest if line.strip()]
    return "\n".join(header + ([""] if header and items else []) + items) + "\n"


def _read_backlog(area: Area) -> tuple[Path, str | None]:
    path = area.records_dir / BACKLOG_FILENAME
    try:
        return path, path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return path, None


def check_backlog(area: Area) -> list[Finding]:
    path, text = _read_backlog(area)
    if text is None:
        return []
    findings = []
    if normalise_backlog(text) != text:
        findings.append(Finding(path, Code.BACKLOG_FORMAT, "items are one unnumbered `- ` line each, no blank lines between them", True))
    header, rest = _split_backlog(text)
    for number, line in enumerate(rest, start=len(header) + 1):
        if line.strip() and not _ITEM_MARKER.match(line):
            findings.append(Finding(path, Code.BACKLOG_LINE, f"line {number} is no item (no headings, sections or continuation lines)", False))
    return findings


def _fix_backlog(area: Area, args: argparse.Namespace) -> None:
    path, text = _read_backlog(area)
    if text is None:
        return
    new_text = normalise_backlog(text)
    if new_text != text:
        write_atomic(path, new_text)
        _emit(args, area, action="fixed", file=str(path), message="backlog items as unnumbered `- ` lines")


def lint(area: Area) -> list[Finding]:
    return sorted(lint_records(area, read_area(area)) + check_backlog(area), key=lambda f: (str(f.file), f.code, f.message))


def _created_from_history(area: Area, path: Path) -> str:
    added = git_output(area.root, "log", "--follow", "--diff-filter=A", "--format=%ct", "--", str(path))
    stamps = [line for line in (added or "").splitlines() if line.strip()]
    return str(float(stamps[-1])) if stamps else str(path.stat().st_mtime)


def _normalise(area: Area, record: RawRecord, edges: str, body: str) -> tuple[str, list[str]] | str:
    """`(new_text, changes)` for a readable record with `edges` as its edges value, or the reason it is not fixable."""
    assert record.fields is not None
    fields, conflict = _modernise(list(record.fields))
    if conflict:
        return "topic: and legacy area: differ; decide by hand"
    values = dict(fields)
    if any(_has_control(value, allow_tab=True) for _, value in fields):
        return "a frontmatter value contains control characters"
    changes: list[str] = []
    if edges != values.get("edges", ""):
        fields = [(key, edges if key == "edges" else value) for key, value in fields]

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
    if adr_markdown.LEGACY_TOPIC_KEY in dict(record.fields):
        changes.append("area: renamed to topic:")
    if not values.get("topic"):
        if len(parts) != 3 or not is_safe_area(parts[0]):
            return "topic: missing and the topic folder is not usable"
        put("topic", parts[0])
        changes.append(f"topic: {parts[0]} (from folder)")
    if not values.get("created"):
        created = _created_from_history(area, record.path)
        put("created", created)
        changes.append(f"created: {created}")
    if values.get("type") == "user" and not values.get("perspective"):
        put("perspective", "user")
        changes.append("perspective: user")

    migrated = _migrate_refs(area, record, fields, edges, body)
    if isinstance(migrated, str):
        return migrated
    if migrated is not None:
        fields, body = migrated
        changes.append(f"id/edges/superseded_by -> file name and '{adr_markdown.EDGES_HEADING}' links")

    new_text = _canonical(fields, body)
    if new_text != record.text and not changes:
        changes.append("field order / spacing")
    return new_text, changes


def _migrate_refs(area: Area, record: RawRecord, fields: list[tuple[str, str]], edges: str, body: str) -> tuple[list[tuple[str, str]], str] | str | None:
    """`(fields, body)` with `id`, `edges` and `superseded_by` moved out of the frontmatter, None when there is
    nothing to move, or the reason it cannot be done. Frontmatter edges come first in the section, then the
    links already there, then `superseded_by`."""
    values = dict(fields)
    if not any(key in values for key in adr_markdown.LEGACY_REF_KEYS):
        return None
    if values.get("id") and values["id"] != record.path.stem:
        return "id: differs from the file name; decide by hand"
    if record.section_problem:
        return f"'{adr_markdown.EDGES_HEADING}' cannot be read: {record.section_problem}"
    text, existing = adr_markdown.split_edges_section(body)
    try:
        frontmatter_edges = parse_edges(edges) if edges else []
        links = [adr_markdown.EdgeLink(e["edge_type"], href_for_ref(record.path, area, e["target_id"])) for e in frontmatter_edges]
        links += [link for link in existing if link.edge_type != adr_markdown.SUPERSEDED_BY]
        superseded = [link for link in existing if link.edge_type == adr_markdown.SUPERSEDED_BY]
        if values.get("superseded_by"):
            superseded = [adr_markdown.EdgeLink(adr_markdown.SUPERSEDED_BY, href_for_ref(record.path, area, values["superseded_by"]))]
    except ValueError as exc:
        return f"a reference cannot become a link: {exc}"
    kept = [(key, value) for key, value in fields if key not in adr_markdown.LEGACY_REF_KEYS]
    return kept, adr_markdown.render_edges_section(text, links + superseded)


def _same_edges_but_targets(old: str, new: str) -> bool:
    try:
        before, after = parse_edges(old), parse_edges(new)
    except ValueError:
        return False
    return [e["edge_type"] for e in before] == [e["edge_type"] for e in after]


def _parsed(area: Area, record: RawRecord, text: str) -> adr_markdown.ParsedAdr:
    return adr_markdown.parse(text, entry_id=record.path.stem, ref_for_href=lambda href: ref_for_href(record.path, area, href))


def _preserved(area: Area, record: RawRecord, new_text: str, edges: str, body: str) -> bool:
    """Content-preservation guard: every frontmatter value, the text and every reference survive the rewrite.

    Allowed: `id`, `edges` and `superseded_by` moving from the frontmatter into the file name and the
    `## Edges` links (same references, same order), and edge targets repointed or relinked (`body` is the
    relinked body) with the same edge types in the same order.
    """
    assert record.fields is not None
    again = _split(new_text)
    if isinstance(again, str):
        return False
    new_fields, _, _, _ = again
    new_values = dict(new_fields)
    old_fields, _ = _modernise(record.fields)
    try:
        before = _parsed(area, record, _canonical(old_fields, record.body))
        after = _parsed(area, record, new_text)
    except ValueError:
        return False
    if after.text.rstrip("\n") != before.text.rstrip("\n") or (before.text.strip() and before.text.strip() not in new_text):
        return False
    old_edges = record.value("edges")
    if edges != old_edges and not _same_edges_but_targets(old_edges, edges):
        return False
    try:
        relinked = _parsed(area, record, _canonical([("type", "x")], body))
        _, relinked_links = adr_markdown.split_edges_section(body)
    except ValueError:
        return False
    if [link.edge_type for link in relinked_links] != [link.edge_type for link in record.section_links or []]:
        return False
    expected = (parse_edges(edges) if edges else []) + relinked.edges
    superseded = relinked.superseded_by or before.superseded_by
    if after.edges != expected or after.superseded_by != superseded or after.id != record.path.stem:
        return False
    return all(new_values.get(key) == value and (not value or value in new_text)
               for key, value in old_fields if value and key not in adr_markdown.LEGACY_REF_KEYS)


def _with_prose_links(area: Area, record: RawRecord, new_text: str, cache: dict[Path, set[str]],
                      areas: Callable[[], list[Area]]) -> tuple[str, list[str]]:
    """`new_text` with the ids in its text linked (only the matched tokens change, see `_link_prose`)."""
    frontmatter, separator, body = new_text.partition("\n---\n\n")
    try:
        text, links = adr_markdown.split_edges_section(body)
    except ValueError:
        return new_text, []
    linked_text, linked = _link_prose(area, record, text, cache, areas)
    if not linked:
        return new_text, []
    return frontmatter + separator + adr_markdown.render_edges_section(linked_text, links), linked


def _emit(args: argparse.Namespace, area: Area, **payload) -> None:
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return
    file = payload.get("file")
    where = f"{Path(file).relative_to(area.root).as_posix()}: " if file else ""
    print(f"{payload['action']} {where}{payload.get('code') or ''}{' - ' if payload.get('code') else ''}{payload['message']}")


def _fix(area: Area, args: argparse.Namespace) -> list[RawRecord]:
    """Normalise the records and repoint lost edge targets, then regenerate INDEX.md if it is stale. Returns the records as they are now."""
    records = read_area(area)
    changed = False
    cache: dict[Path, set[str]] = {}
    found: list[Area] = []

    def areas() -> list[Area]:  # scanned once, and only when an edge is lost
        if not found:
            found.append(area)
            found.extend(a for a in discover_areas(_search_root(area)) if a.root != area.root)
        return found

    for record in records:
        if record.fields is None:
            continue
        edges, repointed = _repoint_edges(area, record, cache, areas)
        body, relinked = _relink_section(area, record, cache, areas)
        repointed += relinked
        outcome = _normalise(area, record, edges, body)
        if isinstance(outcome, str):
            _emit(args, area, action="skipped", file=str(record.path), message=f"not fixable: {outcome}")
            continue
        new_text, changes = outcome
        changes = [c for c in changes if c != "field order / spacing" or not repointed] + repointed
        if new_text != record.text and not _preserved(area, record, new_text, edges, body):
            _emit(args, area, action="skipped", file=str(record.path), message="not fixable: content-preservation guard refused the rewrite")
            continue
        new_text, linked = _with_prose_links(area, record, new_text, cache, areas)
        if linked:
            changes.append(f"linked {len(linked)} id(s) in the text")
        if new_text == record.text:
            continue
        write_atomic(record.path, new_text)
        changed = True
        _emit(args, area, action="fixed", file=str(record.path), message="; ".join(changes))
    if changed:
        records = read_area(area)
    if _check_index(area, records):
        regenerate_index(area.records_dir)
        _emit(args, area, action="fixed", file=str(area.records_dir / _INDEX_FILENAME), message="regenerated")
    _fix_backlog(area, args)
    return records


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--area", metavar="PATH", help="area folder (default: nearest ancestor of cwd with docs/records/)")
    parser.add_argument("--fix", action="store_true", help="normalise frontmatter shape, repoint edges whose id lives in exactly one area, regenerate INDEX.md, write BACKLOG.md items as unnumbered `- ` lines (writes inside the area only)")
    parser.add_argument("--json", action="store_true", help="one JSON object per finding / change")


def run(args: argparse.Namespace) -> int:
    area = find_area(Path(args.area).expanduser() if args.area else Path.cwd())
    if area is None:
        print("mem lint: no area (no docs/records/ in this folder or above)", file=sys.stderr)
        return USAGE
    if args.fix:
        # INDEX.md is fresh after _fix by construction, so it is not rendered a second time.
        findings = lint_records(area, _fix(area, args), check_index=False) + check_backlog(area)
    else:
        findings = lint(area)
    for finding in findings:
        _emit(args, area, action="finding", file=str(finding.file), code=finding.code, fixable=finding.fixable, message=finding.message)
    if not findings and not args.json:
        print("clean")
    return FINDINGS if findings else OK
