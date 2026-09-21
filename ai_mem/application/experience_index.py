"""Experience index: a small block of "situation -> rule" lines derived from entry cues.

An entry earns a line by carrying a `cue` in its metadata: one sentence naming the moment in
which it would have helped, written as a judgment during /reflect (`mem_boost(cue=...)`).
The index is computed on read from those cues, not stored, so it cannot go stale: an entry
that is superseded, expired or deleted drops out on the next read. Which entries earn a line
is decided by whoever wrote the cue, not by a score -- confidence and access_count play no part.
The only ordering signal is boost_count, itself a /reflect judgment, used to decide which lines
survive when there are more cues than room."""
from __future__ import annotations

import time

from ai_mem.application.list_entries import title_of
from ai_mem.domain.memory import MemoryEntry, MemoryRepository

MAX_CUE_CHARS = 140
MAX_LINES = 20  # fixed frame: the block is always small enough to read in full


def normalize_cue(cue: str) -> str:
    """Collapse whitespace to one line; an empty result clears the cue. Raises when too long."""
    text = " ".join(cue.split())
    if len(text) > MAX_CUE_CHARS:
        raise ValueError(
            f"cue is {len(text)} chars (max {MAX_CUE_CHARS}) -- name the moment in one sentence, "
            "the rule itself belongs in the entry"
        )
    return text


def _is_live(entry: MemoryEntry, now_ts: float) -> bool:
    if entry.metadata.get("superseded_by"):
        return False
    try:
        return float(entry.metadata.get("expires_at", now_ts + 1)) > now_ts
    except (TypeError, ValueError):
        return True


def _order_key(entry: MemoryEntry) -> tuple[int, float]:
    try:
        created = float(entry.metadata.get("created_at", 0.0))
    except (TypeError, ValueError):
        created = 0.0
    try:
        boosts = int(entry.metadata.get("boost_count", 0))
    except (TypeError, ValueError):
        boosts = 0
    return (-boosts, -created)


class ExperienceIndexUseCase:
    def __init__(self, repo: MemoryRepository) -> None:
        self._repo = repo

    def execute(self, collections: list[str], max_lines: int = MAX_LINES) -> str:
        """Render the index over `collections`, or "" when no live entry carries a cue.

        Each line reads `- <situation> -> <id> [<collection>]: <title>`; the collection is only
        named for entries outside the first (primary) collection, since that one is the
        default for a follow-up `mem_get`."""
        max_lines = max(0, max_lines)
        now_ts = time.time()
        rows: list[tuple[str, MemoryEntry]] = []
        for collection in collections:
            try:
                entries = self._repo.get_all(collection)
            except Exception:
                continue
            for entry in entries:
                cue = str(entry.metadata.get("cue") or "").strip()
                if cue and _is_live(entry, now_ts):
                    rows.append((collection, entry))

        if not rows or max_lines == 0:
            return ""

        # A stable sort per collection keeps the primary collection's lines ahead on ties.
        rows.sort(key=lambda row: _order_key(row[1]))
        shown, hidden = rows[:max_lines], len(rows) - max_lines

        primary = collections[0]
        lines = []
        for collection, entry in shown:
            cue = " ".join(str(entry.metadata["cue"]).split())
            where = "" if collection == primary else f" [{collection}]"
            lines.append(f"- {cue} -> {entry.id}{where}: {title_of(entry.text, 60)}")
        if hidden > 0:
            lines.append(f"(+{hidden} more cues; mem_query for anything not listed)")
        return "\n".join(lines)
