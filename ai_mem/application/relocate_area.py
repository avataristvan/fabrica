"""Relocate an area folder (`mem move-area`): rewrite every reference that the move would break.

An area's address is its folder, and cross-area references are relative paths (`<rel-area-path>:<id>`), so moving
a folder breaks references in both directions: from the moved areas outwards and from every other area into them.
The use case only plans and writes records; the addressing (path arithmetic) and the folder rename are the caller's.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol

from ai_mem.application.move_memory import with_edges, edges_of
from ai_mem.domain.memory import MemoryEntry, MemoryRepository


class RelocationAddressing(Protocol):
    def relocated_ref(self, from_key: str, ref: str) -> str | None:
        """`ref` (an edge target written in area `from_key`) as it must read after the move; None when unchanged."""
        ...

    def relocated_text(self, from_key: str, text: str) -> tuple[str, list[tuple[str, str]]]:
        """`text` with every reference that resolves to a real record rewritten, and the (old, new) pairs."""
        ...


@dataclass
class Rewrite:
    area: str
    id: str
    where: Literal["edge", "text"]
    old: str
    new: str


@dataclass
class RelocationPlan:
    rewrites: list[Rewrite] = field(default_factory=list)
    entries: dict[str, list[MemoryEntry]] = field(default_factory=dict)  # area key -> rewritten entries
    malformed: list[tuple[str, str]] = field(default_factory=list)  # (area key, id) with an unreadable edges field


class RelocateAreaUseCase:
    def __init__(self, repo: MemoryRepository, addressing: RelocationAddressing) -> None:
        self._repo = repo
        self._addr = addressing

    def plan(self, keys: list[str]) -> RelocationPlan:
        plan = RelocationPlan()
        for key in keys:
            for entry in self._repo.get_all(key):
                rewritten = self._rewrite(plan, key, entry)
                if rewritten is not None:
                    plan.entries.setdefault(key, []).append(rewritten)
        return plan

    def _rewrite(self, plan: RelocationPlan, key: str, entry: MemoryEntry) -> MemoryEntry | None:
        try:
            edges = edges_of(entry)
        except ValueError:
            plan.malformed.append((key, entry.id))
            return None
        changed = False
        new_edges = []
        for edge in edges:
            new = self._addr.relocated_ref(key, edge["target_id"])
            if new is not None:
                plan.rewrites.append(Rewrite(key, entry.id, "edge", edge["target_id"], new))
                edge, changed = {**edge, "target_id": new}, True
            new_edges.append(edge)
        text, pairs = self._addr.relocated_text(key, entry.text)
        plan.rewrites += [Rewrite(key, entry.id, "text", old, new) for old, new in pairs]
        if not changed and not pairs:
            return None
        result = MemoryEntry(id=entry.id, text=text, metadata=entry.metadata)
        return with_edges(result, new_edges) if changed else result

    def apply(self, plan: RelocationPlan, key_after: Callable[[str], str] = lambda key: key) -> None:
        """Write the rewritten entries; `key_after` maps a planned area key to where that area is now."""
        for key, entries in plan.entries.items():
            self._repo.upsert(key_after(key), entries)
