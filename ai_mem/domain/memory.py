"""Domain layer: entities and repository interface."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Protocol

EdgeType = Literal["contradicts", "fixes", "causes", "related", "supersedes", "confirms", "derived_from"]


@dataclass
class MemoryEdge:
    target_id: str
    edge_type: EdgeType


@dataclass
class MemoryEntry:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)
    # injected by AddMemoryUseCase / TrackAccessUseCase; canonical values live in metadata
    created_at: datetime | None = None
    expires_at: datetime | None = None
    last_accessed_at: datetime | None = None


@dataclass
class QueryResult:
    rank: int
    id: str
    score: float
    text: str
    metadata: dict


@dataclass
class SplitHint:
    id: str
    text_preview: str   # first 80 chars of the original text


@dataclass
class CollectionInfo:
    name: str
    count: int


class MemoryRepository(Protocol):
    def upsert(self, collection: str, entries: list[MemoryEntry]) -> None: ...

    def query(
        self,
        collection: str,
        text: str,
        n_results: int,
        max_age_days: float | None,
        type_filter: str | None = None,
    ) -> list[QueryResult]: ...

    def get_by_ids(self, collection: str, ids: list[str]) -> list[MemoryEntry]:
        """Fetch entries by id. Missing ids are silently skipped."""
        ...

    def list_collections(self) -> list[CollectionInfo]: ...

    def delete(self, collection: str, ids: list[str] | None) -> int:
        """Delete entries by id, or drop entire collection. Returns affected count."""
        ...

    def delete_expired(self, collection: str) -> int:
        """Remove all entries whose expires_at is in the past. Returns count."""
        ...

    def record_access(self, collection: str, ids: list[str]) -> None:
        """Bump last_accessed_at for the given ids. Missing ids are silently skipped."""
        ...

    def delete_stale(self, collection: str, stale_after_days: float) -> int:
        """Remove entries whose last_accessed_at is older than the cutoff. Returns count."""
        ...

    def get_all(self, collection: str) -> list[MemoryEntry]:
        """Return every entry in a collection (no filtering, no ranking)."""
        ...

    def add_edge(self, collection: str, source_id: str, edge: MemoryEdge) -> None:
        """Append a causal edge to source_id's metadata. Idempotent on same (target_id, edge_type)."""
        ...

    def get_edges(self, collection: str, entry_id: str) -> list[MemoryEdge]:
        """Return all outgoing edges for entry_id. Empty list when none exist or entry missing."""
        ...


def is_area_qualified(target_id: str) -> bool:
    """An edge target `<rel-area-path>:<id>` points into another area; a bare id stays in the same one."""
    return ":" in target_id


def parse_edges(raw: str | None) -> list[dict]:
    """The `edges` frontmatter value as a list of {target_id, edge_type} dicts (both strings); ValueError when malformed."""
    try:
        edges = json.loads(raw or "[]")
        if not isinstance(edges, list) or not all(isinstance(e["target_id"], str) and isinstance(e["edge_type"], str) for e in edges):
            raise ValueError
    except (ValueError, KeyError, TypeError, RecursionError) as exc:
        raise ValueError("edges is not a JSON list of {target_id, edge_type} string objects") from exc
    return edges


class AreaRefs(Protocol):
    def resolve(self, source: str, target_id: str) -> tuple[str, str] | None:
        """`(collection, id)` an area-qualified target points at, seen from collection `source`; None if it does not resolve."""
        ...


MAX_CUE_CHARS = 140
_MAX_TITLE_LEN = 80


_MARKDOWN_LINK = re.compile(r"\[([^\]\n]*)\]\([^)\s]*\)")


def title_of(text: str, max_len: int = _MAX_TITLE_LEN) -> str:
    """First non-empty line of an entry's text, without a Markdown heading marker and with links reduced
    to their text, truncated: the title in listings, INDEX.md and queries."""
    for line in text.splitlines():
        stripped = _MARKDOWN_LINK.sub(r"\1", line.strip().lstrip("#").strip())
        if stripped:
            return stripped[:max_len]
    return ""


def normalize_cue(cue: str) -> str:
    """Collapse whitespace to one line; an empty result clears the cue. Raises when too long."""
    text = " ".join(cue.split())
    if len(text) > MAX_CUE_CHARS:
        raise ValueError(
            f"cue is {len(text)} chars (max {MAX_CUE_CHARS}) -- name the moment in one sentence, "
            "the rule itself belongs in the entry"
        )
    return text
