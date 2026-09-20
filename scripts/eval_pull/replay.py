#!/usr/bin/env python3
"""Stage B: replay queries against cosine and hybrid retrieval and report where the gold entry lands.

Read-only (calls repo.query directly, so no access tracking). Gold entry ids are read from
gold_ids.local.json ({"<case_id>": ["<entry id>", ...]}, not tracked); without it ranks are not
computed and only the top hit is shown. Usage:
    python3 scripts/eval_pull/replay.py [--collection repo.ai-mem] [--queries queries.json] [-k 8]

Always replays each case's question verbatim ("question" source). --queries adds agent-written
queries harvested in stage A: {"<case_id>": ["query 1", "query 2"]} ("agent" source).
"""
import argparse
import json
from pathlib import Path

from ai_mem.infrastructure.bm25_repository import BM25MemoryRepository
from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository

HERE = Path(__file__).parent
DB_PATH = Path.home() / ".local" / "share" / "ai-mem"


def rank_of(results, gold: set[str]) -> int | None:
    return next((r.rank for r in results if r.id in gold), None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--collection", default="repo.ai-mem")
    ap.add_argument("--queries", type=Path)
    ap.add_argument("-k", type=int, default=8)
    args = ap.parse_args()

    cases = json.loads((HERE / "cases.json").read_text())["cases"]
    gold_path = HERE / "gold_ids.local.json"
    gold_ids = json.loads(gold_path.read_text()) if gold_path.exists() else {}
    if not gold_ids:
        print("note: no gold_ids.local.json -- ranks are not computed, showing the top hit only")
    harvested = json.loads(args.queries.read_text()) if args.queries else {}

    cosine = ChromaMemoryRepository(DB_PATH)
    configs = {"cosine": cosine, "hybrid": BM25MemoryRepository(cosine)}
    hits: dict[tuple[str, str], list[int | None]] = {}

    print(f"{'case':22s} {'src':8s} {'config':7s} {'rank':>4s} {'top1':>5s}  top1_id")
    for case in cases:
        gold = set(gold_ids.get(case["id"], []))
        queries = [("question", case["question"])] + [("agent", q) for q in harvested.get(case["id"], [])]
        for source, query in queries:
            for name, repo in configs.items():
                results = repo.query(args.collection, query, args.k, None)
                for idx, result in enumerate(results, 1):
                    result.rank = idx
                rank = rank_of(results, gold) if gold else None
                top = results[0] if results else None
                shown = "-" if not gold else (str(rank) if rank else f">{args.k}")
                print(f"{case['id']:22s} {source:8s} {name:7s} {shown:>4s} "
                      f"{(top.score if top else 0):5.2f}  {top.id if top else ''}")
                if gold:
                    hits.setdefault((source, name), []).append(rank)

    print("\nhit@1 / hit@3 / hit@k over gap cases")
    for (source, name), ranks in sorted(hits.items()):
        n = len(ranks)
        at = lambda limit: sum(1 for rank in ranks if rank is not None and rank <= limit)
        print(f"{source:8s} {name:7s}  {at(1)}/{n}  {at(3)}/{n}  {at(args.k)}/{n}")
    print("\nControls: a high top1 score on c* rows means retrieval cannot say 'nothing relevant'.")


if __name__ == "__main__":
    main()
