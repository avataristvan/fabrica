"""Serialize/parse ADR-style Markdown files for domain/pattern/anti-pattern/learning entries.

Pure text transform: no filesystem I/O here (see `markdown_adr_repository.py`,
a later chunk, for the repository decorator that writes these to disk).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from ai_mem.infrastructure.adr_paths import DEFAULT_AREA

_FRONTMATTER_SEPARATOR = "\n---\n\n"
# Order `serialize` writes the known keys in; unknown keys follow, `cue` is last. Lint's normaliser reuses it.
KEY_ORDER = ("id", "type", "area", "perspective", "created", "superseded_by", "valid_until", "edges")
KNOWN_KEYS =frozenset({"id", "type", "area", "perspective", "created", "superseded_by", "valid_until", "edges", "cue"})
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


def serialize(entry_id: str, entry_type: str, text: str, metadata: dict) -> str:
    """Render an ADR-style Markdown document: fixed-order frontmatter + separator + raw text.

    Field order is hard-coded (id, type, area, perspective, created, superseded_by, valid_until, edges,
    <unknown keys from `metadata["extra_frontmatter"]` in their own order>, cue) and never
    derived from metadata's own key order, so that two logically-identical entries always
    serialize byte-identically regardless of dict insertion order — a downstream diff-before-
    write step (a later chunk) depends on this to avoid rewriting files on volatile-only changes.
    Volatile fields (confidence/access_count/boost_count/last_accessed_at) are never emitted,
    even if present in `metadata`. `cue` is: it carries the experience index, which must survive
    without ChromaDB (domain_records_model_replaces_chroma_2026_10_04).
    """
    # `area` is always written (default `general`) so serialize(parse(x)) is byte-identical
    # even for entries whose Chroma metadata has no area.
    lines = [f"id: {entry_id}", f"type: {entry_type}", f"area: {metadata.get('area') or DEFAULT_AREA}"]

    perspective = metadata.get("perspective")
    if perspective:
        lines.append(f"perspective: {perspective}")

    created_at = metadata.get("created_at")
    if created_at is not None:
        lines.append(f"created: {created_at}")

    superseded_by = metadata.get("superseded_by")
    if superseded_by:
        lines.append(f"superseded_by: {superseded_by}")

    # "" is the documented "clear" value (un-supersede) -- emitting it would write
    # `valid_until: ` with an empty value, which parse() rejects as a non-float.
    valid_until = metadata.get("valid_until")
    if valid_until not in (None, ""):
        lines.append(f"valid_until: {valid_until}")

    canonical_edges = _canonical_edges(metadata.get("edges"))
    if canonical_edges:
        lines.append(f"edges: {json.dumps(canonical_edges)}")

    for key, value in (metadata.get(EXTRA_FRONTMATTER) or {}).items():
        lines.append(f"{key}: {value}" if value else f"{key}:")

    # normalize_cue() already collapses a cue to one line; re-collapse defensively, since a
    # newline here would break the line-based frontmatter.
    cue = " ".join(str(metadata.get("cue") or "").split())
    if cue:
        lines.append(f"cue: {cue}")

    frontmatter = "\n".join(lines)
    return f"{frontmatter}{_FRONTMATTER_SEPARATOR}{text}"


def check_extra_frontmatter(extra) -> None:
    """Raise ValueError unless `extra` is a dict of one-line `key: value` pairs serialize can re-emit and parse read back."""
    if not isinstance(extra, dict):
        raise ValueError(f"{EXTRA_FRONTMATTER} must be a dict of strings, got {type(extra).__name__}")
    for key, value in extra.items():
        if (not isinstance(key, str) or not isinstance(value, str) or not key or key != key.strip()
                or key in KNOWN_KEYS or key in _VOLATILE_KEYS or ":" in key or "\n" in key or "\n" in value or value != value.strip()):
            raise ValueError(f"frontmatter key {key!r} with value {value!r} cannot be written as one 'key: value' line")


def parse(markdown_text: str) -> ParsedAdr:
    """Parse an ADR-style Markdown document back into its structural fields.

    Simple line-based `key: value` frontmatter parsing suffices — `edges` is a single
    embedded JSON line, never multi-line YAML. Raises ValueError on any malformed
    frontmatter or invalid `edges` JSON: a broken ADR file should be a visible error,
    not a silent skip.
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

    if "id" not in fields or "type" not in fields:
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

    return ParsedAdr(
        id=fields["id"],
        type=fields["type"],
        text=text,
        created_at=created_at,
        superseded_by=fields.get("superseded_by") or None,
        valid_until=valid_until,
        edges=edges,
        area=fields.get("area") or DEFAULT_AREA,
        cue=fields.get("cue") or None,
        perspective=fields.get("perspective") or None,
        extra={key: value for key, value in fields.items() if key not in KNOWN_KEYS and key not in _VOLATILE_KEYS},
    )
