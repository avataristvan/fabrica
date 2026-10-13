"""Fixtures and the record reader shared by build.py and compare.py (archivist acceptance run)."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from ai_mem.infrastructure.adr_markdown import ParsedAdr, parse  # noqa: E402

CANDIDATES = HERE / "candidates.json"
EXPECTED_EDGES = HERE / "expected_edges.json"


@dataclass(frozen=True)
class Candidate:
    n: str      # "01".."18", the number the archivist sees
    id: str     # the real record's id, never shown to the archivist
    type: str   # as shown: "decision" for domain records
    body: str   # redacted text


@dataclass(frozen=True)
class ExpectedEdge:
    source: str
    edge_type: str
    target: str
    # None: a hand-set edge of the real record. Otherwise a predecessor missed on 2026-10-10, living in this
    # area folder (relative to the workspace); any of `related`/`derived_from` counts, and it must be area-qualified.
    predecessor_area: str | None = None


def read_record(path: Path) -> ParsedAdr | None:
    """The parsed record, or None for a malformed (e.g. hand-written) file."""
    try:
        return parse(path.read_text())
    except (ValueError, UnicodeDecodeError):
        return None


def save(path: Path, rows: list) -> None:
    path.write_text(json.dumps([asdict(row) for row in rows], indent=1, ensure_ascii=False) + "\n")


def load_candidates() -> list[Candidate]:
    return [Candidate(**row) for row in json.loads(CANDIDATES.read_text())]


def load_expected() -> list[ExpectedEdge]:
    return [ExpectedEdge(**row) for row in json.loads(EXPECTED_EDGES.read_text())]


def render_candidates(candidates: list[Candidate]) -> str:
    """The plain text the archivist receives: numbers, types and bodies, no ids."""
    blocks = [f"Candidate {c.n} ({c.type})\n\n{c.body}\n" for c in candidates]
    return "Record candidates from a planning session (2026-10-10). Home area: ai-mem.\n\n" + "\n".join(blocks)
