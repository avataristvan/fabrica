"""Equivalence check: the stdlib Chroma reader vs. the chromadb path, on copies of a real store.

    python scripts/upgrade_acceptance/equivalence.py <store-copy-dir> [--scan-root DIR]

Needs chromadb (run it with the dev interpreter, not the chromadb-free venv). The given
directory is copied twice into a temporary sibling first: chromadb may write when it opens a
store, so each path reads its own copy and the given directory is not opened by chromadb.
Compares collections, ids, documents and metadata in order, then the migration plans built
from both. Exit 0 = identical, 1 = a difference (printed). Writes nothing outside the copies.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ai_mem.infrastructure.chroma_sqlite_reader import read_chroma_store  # noqa: E402
from ai_mem.infrastructure.records_migration import build_plan  # noqa: E402


def _dump(source) -> list[tuple]:
    return [(info.name, [(e.id, e.text, e.metadata) for e in source.get_all(info.name)])
            for info in source.list_collections()]


def _plan_key(plan) -> dict:
    def writes(items):
        return [(w.collection, w.entry_id, str(w.path), w.content, w.placement, w.old_type, w.area) for w in items]
    return {
        "writes": writes(plan.writes), "conflicts": writes(plan.conflicts), "already": plan.already,
        "unresolved": plan.unresolved, "unsafe": plan.unsafe,
        "roots": {k: str(v) for k, v in plan.roots.items()}, "name_matched": sorted(plan.name_matched),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("store")
    parser.add_argument("--scan-root", action="append", default=[])
    args = parser.parse_args()
    store = Path(args.store).resolve()
    scan_roots = [Path(p) for p in args.scan_root]

    from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository

    with tempfile.TemporaryDirectory(dir=store.parent) as tmp:
        via_reader, via_chroma = Path(tmp) / "reader", Path(tmp) / "chroma"
        shutil.copytree(store, via_reader, symlinks=True, ignore_dangling_symlinks=True,
                        ignore=lambda d, names: [n for n in names if n.endswith(".sock")])
        shutil.copytree(via_reader, via_chroma)
        snapshot = read_chroma_store(via_reader)
        repo = ChromaMemoryRepository(via_chroma)

        data_reader, data_chroma = _dump(snapshot), _dump(repo)
        failures = []
        if data_reader != data_chroma:
            names_r, names_c = [n for n, _ in data_reader], [n for n, _ in data_chroma]
            failures.append(f"collections differ: {names_r} vs {names_c}" if names_r != names_c
                            else "entries differ in at least one collection: "
                            + ", ".join(n for (n, a), (_, b) in zip(data_reader, data_chroma) if a != b))
        # Both plans resolve roots against the same mapping file (the reader's copy), so only
        # the entry source differs.
        plan_reader = _plan_key(build_plan(snapshot, via_reader, scan_roots))
        plan_chroma = _plan_key(build_plan(repo, via_reader, scan_roots))
        for key in plan_reader:
            if plan_reader[key] != plan_chroma[key]:
                failures.append(f"plan differs in {key!r}")

    entries = sum(len(items) for _, items in data_reader)
    print(f"{store}: {len(data_reader)} collections, {entries} entries, "
          f"{len(plan_reader['writes'])} planned writes, {plan_reader['already']} already, "
          f"{len(plan_reader['conflicts'])} conflicts, {len(plan_reader['unresolved'])} unresolved")
    for failure in failures:
        print(f"DIFFERENCE: {failure}")
    print("EQUIVALENT" if not failures else "NOT EQUIVALENT -- stop and report, do not guess")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
