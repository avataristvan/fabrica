"""Serialize/parse ADR-style Markdown files for domain/pattern/anti-pattern/learning entries.

Pure text transform: no filesystem I/O here (`file_repository.py` writes these to disk).
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from ai_mem.infrastructure.adr_paths import DEFAULT_AREA

_FRONTMATTER_SEPARATOR = "\n---\n\n"
# A record's references are relative Markdown links in a closing `## Edges` section, one per line:
# `- <edge_type>: [<file stem>](<path relative to the record>)`. `superseded_by` is written the same way.
EDGES_HEADING = "## Edges"
_EDGES_MARKER = f"\n\n{EDGES_HEADING}\n"
_EDGE_LINE = re.compile(r"- ([a-z_]+): \[([^\]\n]*)\]\(([^()\s]+)\)")
SUPERSEDED_BY = "superseded_by"


@dataclass(frozen=True)
class EdgeLink:
    edge_type: str
    href: str


def split_edges_section(body: str) -> tuple[str, list[EdgeLink]]:
    """`(text, links)`: the body without its closing `## Edges` section, and that section's links in order.

    A body without the section comes back unchanged with no links. The section is the last
    `## Edges` heading after a blank line; every non-blank line below it must be an edge line,
    else ValueError (a malformed section is a visible error, not silently body text).
    """
    if body.startswith(f"{EDGES_HEADING}\n"):
        start, text = 0, ""
    else:
        start = body.rfind(_EDGES_MARKER)
        if start < 0:
            return body, []
        text = body[:start]
        start += 2
    links = []
    for line in body[start + len(EDGES_HEADING) + 1:].split("\n"):
        if not line.strip():
            continue
        match = _EDGE_LINE.fullmatch(line.rstrip())
        if match is None:
            raise ValueError(f"line in '{EDGES_HEADING}' is not '- <type>: [<name>](<path>)': {line.strip()[:60]!r}")
        links.append(EdgeLink(match.group(1), match.group(3)))
    return text, links


def href_stem(href: str) -> str:
    """The record name a link points at: its file name without `.md`."""
    return PurePosixPath(href).stem


def render_edges_section(text: str, links: list[EdgeLink]) -> str:
    """`text` with a closing `## Edges` section for `links`; `text` unchanged when there are none."""
    if not links:
        return text
    lines = "".join(f"- {link.edge_type}: [{href_stem(link.href)}]({link.href})\n" for link in links)
    return text.rstrip("\n") + _EDGES_MARKER + "\n" + lines


# Order `serialize` writes the known keys in; unknown keys follow, `cue` is last. Lint's normaliser reuses it.
KEY_ORDER = ("type", "topic", "perspective", "created", "valid_until")
# Older records also carry these in the frontmatter; read everywhere, written never (`mem lint --fix` moves them:
# the id is the file name, `edges` and `superseded_by` become links in the `## Edges` section).
LEGACY_REF_KEYS = ("id", "superseded_by", "edges")
LEGACY_KEY_ORDER = ("id", "type", "topic", "perspective", "created", "superseded_by", "valid_until", "edges")
LEGACY_TOPIC_KEY = "area"  # old name of `topic:`; read everywhere, written never
KNOWN_KEYS = frozenset({"id", "type", "topic", LEGACY_TOPIC_KEY, "perspective", "created", "superseded_by", "valid_until", "edges", "cue"})
# Telemetry that is never persisted: dropped from a file's frontmatter, never carried as an extra key.
_VOLATILE_KEYS = frozenset({"confidence", "access_count", "boost_count", "last_accessed_at", "expires_at"})
EXTRA_FRONTMATTER = "extra_frontmatter"  # metadata slot carrying unknown frontmatter keys through a rewrite


@dataclass
class ParsedAdr:
    id: str
    type: str
    text: str
    created_at: float | None
    superseded_by: str | None
    valid_until: float | None
    edges: list[dict] = field(default_factory=list)
    area: str = DEFAULT_AREA
    cue: str | None = None
    perspective: str | None = None
    # Unknown frontmatter keys in file order, re-emitted by serialize so normalisation never drops content.
    extra: dict[str, str] = field(default_factory=dict)


def _canonical_edges(raw_edges) -> list[dict] | None:
    """Normalize an edges value (JSON string or list of dicts) to a canonical dict-key-order list.

    Returns None for missing/empty/unparseable input so callers can skip emitting the field.
    """
    edges = raw_edges
    if isinstance(edges, str):
        try:
            edges = json.loads(edges)
        except json.JSONDecodeError:
            return None
    if not edges:
        return None
    return [{"target_id": edge["target_id"], "edge_type": edge["edge_type"]} for edge in edges]


def _default_href(ref: str) -> str:
    if ":" in ref:
        raise ValueError(f"edge target {ref!r} is in another area: serialize needs `href_for` to link it")
    return f"{ref}.md"


def serialize(entry_id: str, entry_type: str, text: str, metadata: dict,
              href_for: Callable[[str], str] | None = None) -> str:
    """Render an ADR-style Markdown document: fixed-order frontmatter + separator + raw text + `## Edges`.

    The id is not written: the file name is the record's name (`entry_id` stays in the signature for
    the callers that name the file). Edges and `superseded_by` become relative links in the closing
    `## Edges` section; `href_for` turns a target reference into the link (default `<id>.md`, same folder).
    Field order is hard-coded (type, topic, perspective, created, valid_until,
    <unknown keys from `metadata["extra_frontmatter"]` in their own order>, cue) and never
    derived from metadata's own key order, so that two logically-identical entries always
    serialize byte-identically regardless of dict insertion order — a downstream diff-before-
    write step (a later chunk) depends on this to avoid rewriting files on volatile-only changes.
    Volatile fields (confidence/access_count/boost_count/last_accessed_at) are never emitted,
    even if present in `metadata`. `cue` is: it carries the experience index, which must survive
    without ChromaDB (domain_records_model_replaces_chroma_2026_10_04).
    """
    # `topic` is always written (default `general`) so serialize(parse(x)) is byte-identical
    # even for entries whose metadata has no topic. The in-memory metadata key stays `area`.
    lines = [f"type: {entry_type}", f"topic: {metadata.get('area') or DEFAULT_AREA}"]

    perspective = metadata.get("perspective")
    if perspective:
        lines.append(f"perspective: {perspective}")

    created_at = metadata.get("created_at")
    if created_at is not None:
        lines.append(f"created: {created_at}")

    # "" is the documented "clear" value (un-supersede) -- emitting it would write
    # `valid_until: ` with an empty value, which parse() rejects as a non-float.
    valid_until = metadata.get("valid_until")
    if valid_until not in (None, ""):
        lines.append(f"valid_until: {valid_until}")

    for key, value in (metadata.get(EXTRA_FRONTMATTER) or {}).items():
        lines.append(f"{key}: {value}" if value else f"{key}:")

    # normalize_cue (domain) already collapses a cue to one line; re-collapse defensively, since a
    # newline here would break the line-based frontmatter.
    cue = " ".join(str(metadata.get("cue") or "").split())
    if cue:
        lines.append(f"cue: {cue}")

    to_href = href_for or _default_href
    links = [EdgeLink(edge["edge_type"], to_href(edge["target_id"])) for edge in _canonical_edges(metadata.get("edges")) or []]
    superseded_by = metadata.get("superseded_by")
    if superseded_by:
        links.append(EdgeLink(SUPERSEDED_BY, to_href(superseded_by)))

    frontmatter = "\n".join(lines)
    return f"{frontmatter}{_FRONTMATTER_SEPARATOR}{render_edges_section(text, links)}"


def check_extra_frontmatter(extra) -> None:
    """Raise ValueError unless `extra` is a dict of one-line `key: value` pairs serialize can re-emit and parse read back."""
    if not isinstance(extra, dict):
        raise ValueError(f"{EXTRA_FRONTMATTER} must be a dict of strings, got {type(extra).__name__}")
    for key, value in extra.items():
        if (not isinstance(key, str) or not isinstance(value, str) or not key or key != key.strip()
                or key in KNOWN_KEYS or key in _VOLATILE_KEYS or ":" in key or "\n" in key or "\n" in value or value != value.strip()):
            raise ValueError(f"frontmatter key {key!r} with value {value!r} cannot be written as one 'key: value' line")


def parse(markdown_text: str, entry_id: str | None = None, ref_for_href: Callable[[str], str] | None = None) -> ParsedAdr:
    """Parse an ADR-style Markdown document back into its structural fields.

    Simple line-based `key: value` frontmatter parsing suffices. Edges come from the closing
    `## Edges` section (relative links; `ref_for_href` turns a link into a target reference,
    by default its file stem) and, in the older format, from a single-line JSON `edges`
    frontmatter field. The id is the frontmatter `id:` when present, else `entry_id` (the
    file name). Raises ValueError on any malformed frontmatter, edges section or `edges`
    JSON: a broken ADR file should be a visible error, not a silent skip.
    """
    if _FRONTMATTER_SEPARATOR not in markdown_text:
        raise ValueError("ADR markdown missing '---' frontmatter separator")

    frontmatter_block, _, text = markdown_text.partition(_FRONTMATTER_SEPARATOR)

    fields: dict[str, str] = {}
    for line in frontmatter_block.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"malformed ADR frontmatter line (missing ':'): {line!r}")
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()

    record_id = fields.get("id") or entry_id
    if not record_id or "type" not in fields:
        raise ValueError("ADR frontmatter missing required 'id' or 'type' field")

    created_at: float | None = None
    if "created" in fields:
        try:
            created_at = float(fields["created"])
        except ValueError as exc:
            raise ValueError(f"invalid 'created' value in ADR frontmatter: {fields['created']!r}") from exc

    valid_until: float | None = None
    if "valid_until" in fields:
        try:
            valid_until = float(fields["valid_until"])
        except ValueError as exc:
            raise ValueError(f"invalid 'valid_until' value in ADR frontmatter: {fields['valid_until']!r}") from exc

    edges: list[dict] = []
    if "edges" in fields:
        try:
            edges = json.loads(fields["edges"])
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in ADR frontmatter 'edges' field: {fields['edges']!r}") from exc

    text, links = split_edges_section(text)
    to_ref = ref_for_href or href_stem
    superseded_by = fields.get("superseded_by") or None
    for link in links:
        if link.edge_type == SUPERSEDED_BY:
            superseded_by = to_ref(link.href)
        else:
            edges.append({"target_id": to_ref(link.href), "edge_type": link.edge_type})

    return ParsedAdr(
        id=record_id,
        type=fields["type"],
        text=text,
        created_at=created_at,
        superseded_by=superseded_by,
        valid_until=valid_until,
        edges=edges,
        area=fields.get("topic") or fields.get(LEGACY_TOPIC_KEY) or DEFAULT_AREA,
        cue=fields.get("cue") or None,
        perspective=fields.get("perspective") or None,
        extra={key: value for key, value in fields.items() if key not in KNOWN_KEYS and key not in _VOLATILE_KEYS},
    )
