"""Compare an archivist run against the expected edges.

    python scripts/eval_archivist/compare.py <scratch-run-dir> --report <final-answer.txt>

Reads only <scratch-run-dir> and the fixtures next to this script. Prints the numbers; exit 0 = pass, 1 = fail.
New records (not in baseline.json) are mapped to candidates by body similarity; an edge counts
when the mapped source record carries an edge to the (mapped) target id. Type differences are
listed; only `related` <-> `derived_from` are tolerated for a hit, other differences count as a
pair hit with a wrong type (reported, not counted). Every edge from a new record to a baseline
record needs a back-reference on that record (any edge type, or `superseded_by`).
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from fixtures import Candidate, ExpectedEdge, load_candidates, load_expected, read_record

from ai_mem.domain.memory import is_area_qualified
from ai_mem.infrastructure.adr_markdown import ParsedAdr
from ai_mem.infrastructure.areas import find_area, resolve_ref

LOOSE = {"related", "derived_from"}
MIN_SIMILARITY = 0.15
PASS_RECALL = 0.8
KINDS = ("decisions", "learnings", "todos", "user")


@dataclass(frozen=True)
class Edge:
    edge_type: str
    area: str | None   # target area relative to the workspace; None when the reference does not resolve
    id: str
    raw: str           # target_id as written


@dataclass
class Run:
    workspace: Path
    baseline: dict[str, str]
    records: dict[str, ParsedAdr]           # every parseable record file now, by path relative to the workspace
    by_key: dict[tuple[str, str], str]      # (area, id) -> relative path
    new: list[str]                          # relative paths of records not in the baseline

    def area_of(self, rel: str) -> str:
        return str(find_area(self.workspace / rel).root.relative_to(self.workspace))

    def edges(self, rel: str) -> list[Edge]:
        area = find_area(self.workspace / rel)
        out = []
        for edge in self.records[rel].edges:
            resolved = resolve_ref(area, edge["target_id"])
            target_area = None
            if resolved:
                if resolved[0].root.is_relative_to(self.workspace):
                    target_area = str(resolved[0].root.relative_to(self.workspace))
                else:
                    print(f"  [LEAVES SCRATCH] {rel}: edge {edge['target_id']} resolves to {resolved[0].root}")
            out.append(Edge(edge["edge_type"], target_area, resolved[1] if resolved else edge["target_id"], edge["target_id"]))
        return out


def load_run(run_dir: Path) -> Run:
    workspace = (run_dir / "workspace").resolve()
    baseline = json.loads((run_dir / "baseline.json").read_text())
    records = {}
    for path in sorted(workspace.rglob("docs/records/**/*.md")):
        parsed = read_record(path) if path.parent.name in KINDS else None
        if parsed is not None:
            records[str(path.relative_to(workspace))] = parsed
    run = Run(workspace, baseline, records, {}, [rel for rel in records if rel not in baseline])
    run.by_key = {(run.area_of(rel), r.id): rel for rel, r in records.items()}
    return run


def print_changes(run: Run) -> None:
    current = {str(p.relative_to(run.workspace)): p for p in run.workspace.rglob("docs/records/**/*.md")}
    changed = sorted(rel for rel, h in run.baseline.items()
                     if rel in current and hashlib.sha256(current[rel].read_bytes()).hexdigest() != h
                     and not rel.endswith("INDEX.md"))
    removed = sorted(rel for rel in run.baseline if rel not in current)
    print(f"new records: {len(run.new)}; changed baseline records: {len(changed)}; removed: {len(removed)}")
    for rel in changed:
        print(f"  changed: {rel}")
    for rel in removed:
        print(f"  removed: {rel}")


def map_candidates(run: Run, candidates: list[Candidate]) -> dict[str, str]:
    """candidate number -> relative path of the written record (greedy one-to-one by body similarity)."""
    scored = sorted(((difflib.SequenceMatcher(None, c.body, run.records[rel].text.strip()).ratio(), c.n, rel)
                     for c in candidates for rel in run.new), reverse=True)
    mapped: dict[str, str] = {}
    for ratio, n, rel in scored:
        if ratio >= MIN_SIMILARITY and n not in mapped and rel not in mapped.values():
            mapped[n] = rel
    print(f"candidates mapped to a written record: {len(mapped)}/{len(candidates)}")
    unmapped = sorted({c.n for c in candidates} - set(mapped))
    if unmapped:
        print(f"  unmapped candidates (dropped, merged or rewritten beyond similarity): {', '.join(unmapped)}")
    return mapped


def score_expected(run: Run, candidates: list[Candidate], mapped: dict[str, str],
                   expected: list[ExpectedEdge]) -> tuple[int, int, dict[str, bool]]:
    """-> (hand-set hits, hand-set total, predecessor -> linked across areas)."""
    real_to_n = {c.id: c.n for c in candidates}
    written_id = {n: run.records[rel].id for n, rel in mapped.items()}
    hits = total = 0
    predecessors: dict[str, bool] = {}
    for want in expected:
        rel = mapped.get(real_to_n[want.source])
        mine = run.edges(rel) if rel else []
        if want.predecessor_area is None:
            total += 1
            tn = real_to_n.get(want.target)
            ok_ids = {written_id[tn], want.target} if tn in written_id else {want.target}
            pair = [e for e in mine if e.id in ok_ids]
            exact = [e for e in pair if e.edge_type == want.edge_type]
            loose = [e for e in pair if e.edge_type in LOOSE and want.edge_type in LOOSE]
            status = "hit" if exact else "hit (type swapped related/derived_from)" if loose else \
                f"pair only, type {pair[0].edge_type} != {want.edge_type}" if pair else "MISSING"
            hits += bool(exact or loose)
            print(f"  [{status}] {want.source} -{want.edge_type}-> {want.target}")
        else:
            pair = [e for e in mine if e.id == want.target]
            cross = [e for e in pair if is_area_qualified(e.raw) and e.area == want.predecessor_area]
            predecessors[want.target] = bool(cross)
            print(f"  [{'FOUND ' + cross[0].raw if cross else 'MISSING'}] predecessor {want.target} <- {want.source}"
                  + (f" (edge present but not area-qualified: {pair[0].raw})" if pair and not cross else ""))
    return hits, total, predecessors


def back_references(run: Run) -> tuple[int, int]:
    """Edges from new records to baseline records, and how many of them have a back-reference on the target."""
    ok = total = 0
    for rel in run.new:
        source = (run.area_of(rel), run.records[rel].id)
        for edge in run.edges(rel):
            target_rel = run.by_key.get((edge.area, edge.id))
            if target_rel is None or target_rel not in run.baseline:
                continue
            total += 1
            target = run.records[target_rel]
            superseded_by_source = target.superseded_by == source[1] and edge.area == source[0]
            back = superseded_by_source or any((e.area, e.id) == source for e in run.edges(target_rel))
            ok += back
            if not back:
                print(f"  [NO BACK-REF] {target_rel} lacks an edge to {source[1]} ({source[0]}), which points at it ({edge.edge_type})")
    return ok, total


def duplicate_flagged(report: Path) -> bool:
    return any("user_interaction_style" in line and re.search(r"merge|duplicate|both|twice", line, re.I)
               for line in report.read_text().splitlines())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--report", type=Path, required=True, help="archivist's final answer (text), searched for the duplicate flag")
    args = parser.parse_args(argv)
    run = load_run(args.run_dir.resolve())
    print_changes(run)

    candidates = load_candidates()
    mapped = map_candidates(run, candidates)
    hits, total, predecessors = score_expected(run, candidates, mapped, load_expected())
    recall = hits / max(total, 1)
    print(f"hand-set edge recall: {hits}/{total} = {recall:.0%}")
    print(f"missed predecessors linked across areas: {sum(predecessors.values())}/{len(predecessors)}")

    back_ok, back_total = back_references(run)
    print(f"back-references on existing records: {back_ok}/{back_total}")

    new = [run.records[rel] for rel in run.new]
    print(f"perspective present: {sum(1 for r in new if r.perspective)}/{len(new)}; cue present: {sum(1 for r in new if r.cue)}/{len(new)}")

    dup = duplicate_flagged(args.report)
    print(f"duplicate user_interaction_style flagged in report: {'yes' if dup else 'no'}")
    passed = recall >= PASS_RECALL and all(predecessors.values()) and dup and back_ok == back_total > 0
    print(("PASS" if passed else "FAIL") + " (the outside-scratch check is separate: see README)")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
