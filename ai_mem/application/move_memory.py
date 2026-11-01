"""Move entries between areas (`mem move`), preserving id/text/metadata."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal, Protocol

from ai_mem.domain.memory import AreaRefs, EdgeType, MemoryEntry, MemoryRepository, is_area_qualified, parse_edges

_PREVIEW_LEN = 120


_SUPERSEDES: EdgeType = "supersedes"
OpKind = Literal["write", "rewrite_edge", "delete", "report"]


class AreaAddressing(AreaRefs, Protocol):
    def translate(self, from_key: str, to_key: str, ref: str) -> str:
        """`ref`, written in area `from_key`, as it must be written in area `to_key`; ValueError if invalid."""
        ...


@dataclass
class PlannedOp:
    kind: OpKind
    area: str
    id: str
    detail: str = ""
    entry: MemoryEntry | None = None
    moved_from: str = ""  # on a "write": the source area of a record arriving here (else a referrer rewrite)


@dataclass
class AreaMoveConflict:
    id: str
    reason: str


@dataclass(frozen=True)
class MoveRow:
    source: str
    id: str
    target: str
    perspective: str = ""


@dataclass
class AreaMovePlan:
    ops: list[PlannedOp] = field(default_factory=list)
    conflicts: list[AreaMoveConflict] = field(default_factory=list)
    not_found_ids: list[str] = field(default_factory=list)
    done_ids: list[str] = field(default_factory=list)

    def _ops(self, kind: OpKind, arrivals: bool | None = None) -> dict[str, list[PlannedOp]]:
        by_area: dict[str, list[PlannedOp]] = {}
        for op in self.ops:
            if op.kind == kind and (arrivals is None or bool(op.moved_from) == arrivals):
                by_area.setdefault(op.area, []).append(op)
        return by_area


def edges_of(entry: MemoryEntry) -> list[dict]:
    """The entry's edges; ValueError when the stored field is not a list of {target_id, edge_type}."""
    try:
        return parse_edges(entry.metadata.get("edges"))
    except ValueError as exc:
        raise ValueError(f"malformed edges in {entry.id!r}") from exc


def with_edges(entry: MemoryEntry, edges: list[dict]) -> MemoryEntry:
    unique = list({(e["target_id"], e["edge_type"]): e for e in edges}.values())
    return MemoryEntry(id=entry.id, text=entry.text, metadata={**entry.metadata, "edges": json.dumps(unique)})


def _edges_or_conflict(plan: "AreaMovePlan", area: str, entry: MemoryEntry) -> list[dict] | None:
    try:
        return edges_of(entry)
    except ValueError:
        plan.conflicts.append(AreaMoveConflict(entry.id, f"malformed edges field in {area}:{entry.id}; fix the file by hand first"))
        return None


def _with_perspective(entry: MemoryEntry, perspective: str) -> MemoryEntry:
    return MemoryEntry(id=entry.id, text=entry.text, metadata={**entry.metadata, "perspective": perspective})


Key = tuple[str, str]  # (area key, record id)


class MoveToAreaUseCase:
    """Area -> area move, one record set or a whole batch. Collections here are area keys. A target area
    only receives files: nothing but the moved records is written there. Referrers are rewritten only in
    the areas the records leave; referrers anywhere else are reported, never edited."""

    def __init__(self, repo: MemoryRepository, addressing: AreaAddressing) -> None:
        self._repo = repo
        self._addr = addressing

    def plan(self, source: str, target: str, ids: list[str], scan: list[str]) -> AreaMovePlan:
        if source == target:
            raise ValueError("source and target area must differ")
        return self.plan_batch([MoveRow(source, i, target) for i in dict.fromkeys(ids)], scan)

    def plan_batch(self, rows: list[MoveRow], scan: list[str], resume: bool = False) -> AreaMovePlan:
        """One plan for all rows, independent of their order: every edge is written against the final
        location of what it points at. With `resume`, a row whose record is gone from the source but
        present in the target counts as done (an interrupted run, repeated)."""
        if any(row.source == row.target for row in rows):
            raise ValueError("source and target area must differ")
        plan = AreaMovePlan()
        found: dict[Key, MemoryEntry] = {}
        for source in dict.fromkeys(row.source for row in rows):
            ids = [row.id for row in rows if row.source == source]
            found.update({(source, entry.id): entry for entry in self._repo.get_by_ids(source, ids)})
        existing: dict[Key, MemoryEntry] = {}
        for target in dict.fromkeys(row.target for row in rows):
            ids = [row.id for row in rows if row.target == target]
            existing.update({(target, entry.id): entry for entry in self._repo.get_by_ids(target, ids)})

        dest: dict[Key, str] = {}  # (source, id) -> final area, for every record that moves or already moved
        for row in rows:
            key = (row.source, row.id)
            if key in found:
                dest[key] = row.target
            elif resume and (row.target, row.id) in existing:
                dest[key] = row.target
                plan.done_ids.append(row.id)
            else:
                plan.not_found_ids.append(row.id)

        for row in rows:
            if (row.source, row.id) in found:
                self._plan_moved(plan, row, found[(row.source, row.id)], dest, existing.get((row.target, row.id)))
        sources = list(dict.fromkeys(row.source for row in rows))
        for source in sources:
            self._plan_source_referrers(plan, source, dest)
        targets = list(dict.fromkeys(row.target for row in rows))
        self._plan_reports(plan, dest, [key for key in dict.fromkeys([*scan, *targets]) if key not in sources])
        conflicted = {c.id for c in plan.conflicts}
        for row in rows:
            if (row.source, row.id) in found and row.id not in conflicted:
                plan.ops.append(PlannedOp("delete", row.source, row.id, entry=found[(row.source, row.id)]))
        return plan

    def _final_ref(self, hit: Key, dest: dict[Key, str], viewpoint: str) -> str:
        """The reference to `hit` (at its final location) as written in area `viewpoint`."""
        return self._addr.translate(dest.get(hit, hit[0]), viewpoint, hit[1])

    def _plan_moved(self, plan: AreaMovePlan, row: MoveRow, entry: MemoryEntry, dest: dict[Key, str], existing: MemoryEntry | None) -> None:
        source, target = row.source, row.target
        if entry.metadata.get("type") == "reference":
            plan.conflicts.append(AreaMoveConflict(entry.id, "reference documents are not records and are not moved"))
            return
        successor = entry.metadata.get("superseded_by")
        if successor and dest.get((source, successor)) != target:
            plan.conflicts.append(AreaMoveConflict(entry.id, f"superseded by {successor!r}, which does not move to the same area; move both together"))
            return
        edges, ops = [], []
        old_edges = _edges_or_conflict(plan, source, entry)
        if old_edges is None:
            return
        for edge in old_edges:
            old = edge["target_id"]
            hit = self._addr.resolve(source, old)
            try:
                if hit is not None and hit in dest:
                    new = self._final_ref(hit, dest, target)
                else:
                    new = self._addr.translate(source, target, old)
            except ValueError:
                edges.append(edge)  # invalid refs stay as they are; `mem lint` reports them
                continue
            if new != old:
                if is_area_qualified(new) and edge["edge_type"] == _SUPERSEDES:
                    plan.conflicts.append(AreaMoveConflict(entry.id, f"supersedes {old!r} would cross areas; move both together"))
                    return
                ops.append(PlannedOp("rewrite_edge", target, entry.id, f"{old} -> {new}"))
            edges.append({**edge, "target_id": new})
        final = with_edges(entry, edges) if edges else entry
        perspective = "user" if entry.metadata.get("type") == "user" else row.perspective  # D6: kind user is always perspective user
        if perspective:
            final = _with_perspective(final, perspective)
        if existing is not None and (existing.text != final.text or existing.metadata != final.metadata):
            plan.conflicts.append(AreaMoveConflict(entry.id, "a different record with this id exists in the target area"))
            return
        plan.ops.append(PlannedOp("write", target, entry.id, entry=final, moved_from=source))
        plan.ops.extend(ops)

    def _plan_source_referrers(self, plan: AreaMovePlan, source: str, dest: dict[Key, str]) -> None:
        for entry in self._repo.get_all(source):
            if (source, entry.id) in dest:
                continue
            successor = entry.metadata.get("superseded_by")
            if successor and (source, successor) in dest:
                plan.conflicts.append(AreaMoveConflict(successor, f"{entry.id!r} is superseded by it; move both together"))
                continue
            edges, ops = [], []
            old_edges = _edges_or_conflict(plan, source, entry)
            if old_edges is None:
                continue
            for edge in old_edges:
                hit = self._addr.resolve(source, edge["target_id"])
                if hit is not None and hit in dest:
                    if edge["edge_type"] == _SUPERSEDES:
                        plan.conflicts.append(AreaMoveConflict(hit[1], f"{entry.id!r} supersedes it; move both together"))
                        continue
                    new = self._final_ref(hit, dest, source)
                    ops.append(PlannedOp("rewrite_edge", source, entry.id, f"{edge['target_id']} -> {new}"))
                    edge = {**edge, "target_id": new}
                edges.append(edge)
            if ops:
                plan.ops.append(PlannedOp("write", source, entry.id, entry=with_edges(entry, edges)))
                plan.ops.extend(ops)

    def _plan_reports(self, plan: AreaMovePlan, dest: dict[Key, str], keys: list[str]) -> None:
        arrived = {(area, key[1]) for key, area in dest.items()}
        for key in keys:
            for entry in self._repo.get_all(key):
                edges = _edges_or_conflict(plan, key, entry)
                for edge in edges or []:
                    ref = edge["target_id"]
                    hit = self._addr.resolve(key, ref)
                    if hit is None:
                        continue
                    if hit in dest:
                        plan.ops.append(PlannedOp("report", key, entry.id, ref))
                    elif hit in arrived and hit[0] == key and is_area_qualified(ref):
                        plan.ops.append(PlannedOp("report", key, entry.id, f"keeps {ref}; now resolvable bare as {hit[1]}"))

    def apply(self, plan: AreaMovePlan) -> None:
        """Arrivals first and confirmed, then referrer rewrites, then deletes: an interruption leaves
        duplicates (which `plan_batch(resume=True)` accepts), never a lost record."""
        if plan.conflicts:
            raise ValueError("plan has conflicts; nothing to apply")
        arrivals = plan._ops("write", arrivals=True)
        for area, ops in arrivals.items():
            self._repo.upsert(area, [op.entry for op in ops])
        for area, ops in arrivals.items():
            landed = {e.id for e in self._repo.get_by_ids(area, [op.id for op in ops])}
            if len(landed) != len(ops):
                raise ValueError("target write not confirmed; source left untouched")
        for area, ops in plan._ops("write", arrivals=False).items():
            self._repo.upsert(area, [op.entry for op in ops])
        for area, ops in plan._ops("delete").items():
            self._repo.delete(area, [op.id for op in ops])
