"""Score librarian eval arms against the baseline (stdlib only).

    python3 scripts/eval_librarian/score.py BASELINE.json RESULTS.json [--write]

RESULTS.json holds `arms`, each with `questions[].runs[].relied_on`; one arm must be named
`control` (the unchanged librarian, run next to the arm under test). Questions are paired
with the baseline by `id`. --write stores the scores back into RESULTS.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from collections import Counter

CORE_MIN = 2  # an id is core when at least this many baseline runs cite it
PASS_MIN = 2  # a question passes when at least this many of its runs pass

RULE = (
    f"core = ids cited in >= {CORE_MIN} baseline runs; a run passes when it cites >= ceil(|core|/2) "
    f"core ids and every id it cites is in (baseline union | control union); a question passes when "
    f">= {PASS_MIN} of its runs pass"
)


def core_of(runs: list[dict]) -> set[str]:
    counts = Counter(i for r in runs for i in set(r["relied_on"]))
    return {i for i, n in counts.items() if n >= CORE_MIN}


def union_of(runs: list[dict]) -> set[str]:
    return {i for r in runs for i in r["relied_on"]}


def score(baseline: dict, results: dict) -> list[str]:
    arms = {a["arm"]: a for a in results["arms"]}
    if "control" not in arms:
        raise SystemExit("score.py: RESULTS has no arm named 'control'; the rule needs one")
    base = {q["id"]: q for q in baseline["questions"]}
    control = {q["id"]: q for q in arms["control"]["questions"]}
    headers, lines = [], []
    for arm in results["arms"]:
        cells = []
        for q in arm["questions"]:
            assert q["id"] in base and q["id"] in control, f"{arm['arm']}: question {q['id']} not in baseline/control"
            base_runs = base[q["id"]]["runs"]
            core = core_of(base_runs)
            allowed = union_of(base_runs) | union_of(control[q["id"]]["runs"])
            need = math.ceil(len(core) / 2)
            for r in q["runs"]:
                ids = set(r["relied_on"])
                r["core_cited"] = sorted(ids & core)
                r["outside_allowed"] = sorted(ids - allowed)
                r["pass"] = len(r["core_cited"]) >= need and not r["outside_allowed"]
                if not r["pass"]:
                    lines.append(f"  {arm['arm']} {q['id']} run {r['run']}: core {len(r['core_cited'])}/{need}, "
                                 f"outside {r['outside_allowed']}")
            passed = sum(r["pass"] for r in q["runs"])
            question_pass = passed >= PASS_MIN
            q.update(core=sorted(core), core_needed=need, runs_passed=passed, **{"pass": question_pass})
            cells.append(f"{q['id']} {passed}/{len(q['runs'])} {'pass' if question_pass else 'FAIL'}")
        headers.append(f"{arm['arm']}: " + " | ".join(cells))
    results["rule"] = RULE
    return headers + lines


def _write_atomic(path: str, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("baseline")
    parser.add_argument("results")
    parser.add_argument("--write", action="store_true", help="store the scores back into RESULTS")
    args = parser.parse_args(argv)
    with open(args.baseline) as f:
        baseline = json.load(f)
    with open(args.results) as f:
        results = json.load(f)
    for line in score(baseline, results):
        print(line)
    if args.write:
        _write_atomic(args.results, results)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
