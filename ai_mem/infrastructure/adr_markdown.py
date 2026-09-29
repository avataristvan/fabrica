"""Serialize/parse ADR-style Markdown files for domain/pattern/anti-pattern/learning entries.

Pure text transform: no filesystem I/O here (see `markdown_adr_repository.py`,
a later chunk, for the repository decorator that writes these to disk).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from ai_mem.infrastructure.adr_paths import DEFAULT_AREA

_FRONTMATTER_SEPARATOR = "\n---\n\n"


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

    Field order is hard-coded (id, type, area, created, superseded_by, valid_until, edges) and never
    derived from metadata's own key order, so that two logically-identical entries always
    serialize byte-identically regardless of dict insertion order — a downstream diff-before-
    write step (a later chunk) depends on this to avoid rewriting files on volatile-only changes.
    Volatile fields (confidence/access_count/boost_count/last_accessed_at/cue) are never emitted,
    even if present in `metadata`.
    """
    # `area` is always written (default `general`) so serialize(parse(x)) is byte-identical
    # even for entries whose Chroma metadata has no area.
    lines = [f"id: {entry_id}", f"type: {entry_type}", f"area: {metadata.get('area') or DEFAULT_AREA}"]

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

    frontmatter = "\n".join(lines)
    return f"{frontmatter}{_FRONTMATTER_SEPARATOR}{text}"


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
    )
