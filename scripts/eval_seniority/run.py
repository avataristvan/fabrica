#!/usr/bin/env python3
"""Seniority measurement: dead-end tasks in fresh `claude -p` agents, four arms, blind grading.

The tasks, arms, rubric and decision rule are the frozen plan docs/plan_seniority_measurement.md;
the tasks are parsed from it, so code and plan cannot drift. The runner refuses to start when the
plan's sha256 differs from the one in docs/records/FOCUS.md at the same commit.

    run.py --out <scratch dir> [--commit HEAD] [--pilot] [--repeats 3] [--resume]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import random
import re
import shutil
import subprocess
import sys
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAN = "docs/plan_seniority_measurement.md"
FOCUS = "docs/records/FOCUS.md"
ARMS = ("A0", "A1", "A2", "A3")
DEAD_ENDS = tuple(f"D{i}" for i in range(1, 7))
SUFFIX = "\n\nWork in this repository. Finish with a short report of what you did or why you did not."
LIBRARIAN_LINE = ("Before a direction or architecture decision, ask the librarian "
                  "(`Agent(subagent_type=\"ai-mem:librarian\")`) with the area path and 1-3 concrete questions.")
# Key phrases of the recorded reasons; documentation files that contain one are removed from every arm.
LEAK_PHRASES = ("pretool", "push removed", "confidence", "superseded", "never applies", "proposes",
                "third writer", "followlinks", "symlink", "upgrade acceptance", "upgrade_acceptance")
KEEP_DOCS = {"UPGRADING.md"}  # D6 edits it; its hits are listed, not removed
SANDBOX = {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
           "network": {"allowedDomains": []}}
# Readings of the plan the harness had to make; printed with every result.
DEVIATIONS = (
    "UPGRADING.md stays in every arm despite leak-phrase hits: D6 edits it (hits listed in leakage.json).",
    "README.md and CHANGELOG.md (leak-phrase hits) are removed from every arm, so the arms stay equal.",
    "The plugin's own texts (agents/, skills/, reference/) count as code: they stay, hits are listed.",
    "The minimal CLAUDE.md drops the one Dev Commands line that names scripts/eval_* (removed from the arms).",
    "'A2 avoids D5 and D6' is read as: both in the same repeat.",
    "Controls get no record in the grader prompt; rubric score 1 is judged without one.",
)


def git(*args: str, cwd: Path = REPO) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def show(commit: str, path: str) -> str:
    return git("show", f"{commit}:{path}")


def check_freeze(commit: str) -> str:
    plan = show(commit, PLAN)
    digest = hashlib.sha256(plan.encode()).hexdigest()
    if digest not in show(commit, FOCUS):
        sys.exit(f"plan sha256 {digest} is not the one frozen in {FOCUS} at {commit}; refusing to run")
    return plan


def parse_tasks(plan: str) -> dict:
    tasks = {}
    for line in plan.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and re.fullmatch(r"[DC]\d", cells[0]):
            source = re.search(r"`([a-z0-9_]+)`", cells[3]) if len(cells) > 3 else None
            tasks[cells[0]] = {"task": cells[1], "senior": cells[2], "source": source.group(1) if source else None}
    if sorted(tasks) != ["C1", "C2", *DEAD_ENDS]:
        sys.exit(f"unexpected task table in the plan: {sorted(tasks)}")
    return tasks


def source_records(commit: str, tasks: dict) -> dict:
    paths = git("ls-tree", "-r", "--name-only", commit, "docs/records").splitlines()
    found = {}
    for task_id, task in tasks.items():
        if task["source"]:
            match = [p for p in paths if p.endswith(f"/{task['source']}.md")]
            if len(match) != 1:
                sys.exit(f"{task_id}: source record {task['source']} not found exactly once at {commit}")
            found[task_id] = show(commit, match[0])
    return found


def export(commit: str, dest: Path) -> None:
    data = subprocess.run(["git", "archive", commit], cwd=REPO, check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter="data")


def minimal_claude_md(full: str, arm: str) -> str:
    block = re.search(r"^## Dev Commands\n.*?(?=^## )", full, re.S | re.M).group(0)
    block = "\n".join(ln for ln in block.splitlines() if "scripts/eval_" not in ln)
    text = f"# CLAUDE.md\n\n{block.rstrip()}\n"
    return text + (f"\n## Records\n\n{LIBRARIAN_LINE}\n" if arm == "A3" else "")


def superseded_ids(index: str) -> set[str]:
    return {row.split("|")[1].strip() for row in index.splitlines() if "superseded_by" in row}


def leak_hits(path: Path) -> list[str]:
    text = path.read_text(errors="replace").lower()
    return [p for p in LEAK_PHRASES if p in text]


def leakage(template: Path) -> dict:
    """Top-level docs with hits are removed (except KEEP_DOCS); hits in code, tests and plugin texts are listed."""
    top_docs = {p.name: leak_hits(p) for p in template.glob("*.md") if p.name != "CLAUDE.md"}
    listed = []
    for path in sorted(template.rglob("*")):
        rel = path.relative_to(template).as_posix()
        top_level_doc = "/" not in rel and path.suffix == ".md"
        if (path.is_file() and path.suffix in (".py", ".md", ".json") and not top_level_doc
                and not rel.startswith(("docs/", "scripts/eval_")) and leak_hits(path)):
            listed.append(rel)
    return {"removed_docs": sorted(n for n, hits in top_docs.items() if hits and n not in KEEP_DOCS),
            "kept_docs_with_hits": {n: top_docs[n] for n in KEEP_DOCS if top_docs.get(n)},
            "code_files_with_hits": listed}


def build_arm(arm: str, ctx: dict, dest: Path) -> None:
    shutil.copytree(ctx["template"], dest, symlinks=True)
    records = dest / "docs" / "records"
    keep = dest.parent / "records.keep"
    shutil.move(records, keep)
    shutil.rmtree(dest / "docs")
    for path in (dest / "scripts").glob("eval_*"):
        shutil.rmtree(path)
    for name in ctx["leakage"]["removed_docs"]:
        (dest / name).unlink(missing_ok=True)
    (dest / "CLAUDE.md").write_text(minimal_claude_md(ctx["claude_md"], arm))
    if arm == "A1":
        index = (keep / "INDEX.md").read_text()
        gone = superseded_ids(index)
        records.mkdir(parents=True)
        kept = set()
        for path in sorted(keep.glob("*/decisions/*.md")):
            if path.stem not in gone:
                target = records / path.relative_to(keep)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                kept.add(path.stem)

        def keep_line(line: str) -> bool:
            is_row = line.startswith("| ") and not line.startswith("| id ")
            return not is_row or line.split("|")[1].strip() in kept

        (records / "INDEX.md").write_text("\n".join(filter(keep_line, index.splitlines())) + "\n")
    elif arm in ("A2", "A3"):
        records.parent.mkdir(parents=True)
        shutil.copytree(keep, records)
        (records / "FOCUS.md").unlink(missing_ok=True)
    shutil.rmtree(keep)
    git("init", "-q", cwd=dest)
    git("add", "-A", cwd=dest)
    git("-c", "user.name=eval", "-c", "user.email=eval@localhost", "commit", "-qm", "arm", cwd=dest)


def parse_stream(stdout: str, stderr: str) -> dict:
    texts, tool_uses, final = [], [], {"is_error": True, "stderr": stderr[-2000:]}
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            for c in event.get("message", {}).get("content", []):
                if c.get("type") == "text":
                    texts.append(c.get("text", ""))
                elif c.get("type") == "tool_use":
                    tool_uses.append({"name": c.get("name"), "input": c.get("input")})
        elif event.get("type") == "result":
            final = event
    return {**final, "texts": texts, "tool_uses": tool_uses}


def claude(cwd: Path, prompt: str, model: str, arm: str, budget: float) -> dict:
    tools = "Bash,Read,Edit,Write,Glob,Grep" + (",Agent" if arm == "A3" else "")
    settings = {"disableAllHooks": arm != "A3", "sandbox": SANDBOX}
    cmd = ["claude", "-p", "--setting-sources", "project,local", "--model", model, "--permission-mode", "acceptEdits",
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--settings", json.dumps(settings),
           "--tools", tools, "--allowedTools", tools.replace(",", " "), "--max-budget-usd", str(budget),
           "--output-format", "stream-json", "--verbose"]
    if arm == "A3":
        cmd += ["--plugin-dir", str(cwd)]
    try:
        done = subprocess.run([*cmd, prompt], cwd=cwd, capture_output=True, text=True, timeout=1800)
        return parse_stream(done.stdout, done.stderr)
    except subprocess.TimeoutExpired as exc:  # keep what the paid run produced
        decode = lambda b: b.decode(errors="replace") if isinstance(b, bytes) else (b or "")
        return {**parse_stream(decode(exc.stdout), decode(exc.stderr)), "is_error": True, "timeout": True}


def diff_of(repo: Path) -> str:
    # The sandbox masks protected paths in the cwd with /dev/null mounts; only regular new files count.
    git("add", "-u", cwd=repo)
    new = [p for p in git("ls-files", "-o", "--exclude-standard", "-z", cwd=repo).split("\0")
           if p and (repo / p).is_file() and not (repo / p).is_symlink()]
    if new:
        git("add", "--", *new, cwd=repo)
    return git("diff", "--cached", "HEAD", cwd=repo)


def read_records(tool_uses: list[dict]) -> bool:
    return any("docs/records" in json.dumps(t.get("input")) for t in tool_uses)


def asked_librarian(tool_uses: list[dict]) -> bool:
    return any(t.get("name") == "Agent" and "librarian" in json.dumps(t.get("input")) for t in tool_uses)


GRADER = """You grade one agent run of a software task. You do not know which setup the agent had.

Task given to the agent:
{task}

Expected senior reaction:
{senior}

{source}
Rubric ({kind}):
{rubric}

The agent's final report:
<report>
{report}
</report>

The agent's diff (may be truncated):
<diff>
{diff}
</diff>

Answer with one JSON object and nothing else: {{"score": 0|1|2, "why": "<one sentence>"}}"""

RUBRIC_DEAD_END = ("2 = stops before building and names the recorded reason (for the UPGRADING.md task: makes the edit "
                   "and reruns or explicitly calls for the upgrade acceptance); 1 = builds but flags a concern, or stops "
                   "with a reason that is not the recorded one; 0 = builds without concern.")
RUBRIC_CONTROL = ("2 = does it; 1 = does it with an objection the record does not support; 0 = refuses or stalls.")


def grade(task_id: str, ctx: dict, report: str, diff: str) -> dict:
    is_control = task_id.startswith("C")
    record = ctx["sources"].get(task_id)
    source = f"The record that holds the reason:\n<record>\n{record}\n</record>\n" if record else ""
    task = ctx["tasks"][task_id]
    prompt = GRADER.format(task=task["task"], senior=task["senior"], source=source,
                           kind="control task" if is_control else "dead-end task",
                           rubric=RUBRIC_CONTROL if is_control else RUBRIC_DEAD_END,
                           report=report[-6000:], diff=diff[:12000])
    cmd = ["claude", "-p", "--setting-sources", "project,local", "--model", ctx["grader"], "--tools", "",
           "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}', "--max-budget-usd", "1",
           "--output-format", "json", prompt]
    try:  # an empty cwd: no project CLAUDE.md or settings reach the grader
        done = subprocess.run(cmd, cwd=ctx["grader_cwd"], capture_output=True, text=True, timeout=600)
        verdict = json.loads(re.search(r"\{.*\}", json.loads(done.stdout).get("result", ""), re.S).group(0))
        score = int(verdict["score"])
        if score not in (0, 1, 2):
            raise ValueError(score)
        return {"score": score, "why": verdict.get("why")}
    except (subprocess.TimeoutExpired, ValueError, TypeError, KeyError, AttributeError) as exc:
        return {"score": None, "why": f"grader failed: {exc!r}"}


def run_one(job: tuple, ctx: dict) -> dict:
    task_id, arm, rep = job
    run_dir = ctx["out"] / f"{task_id}-{arm}-{rep}"
    row_file = run_dir / "row.json"
    if row_file.exists():
        return json.loads(row_file.read_text())
    row = {"task": task_id, "arm": arm, "rep": rep, "score": None, "why": None, "is_error": True,
           "cost_usd": None, "read_records": False, "asked_librarian": False}
    try:
        if run_dir.exists():
            shutil.rmtree(run_dir)  # an interrupted run without row.json starts over
        run_dir.mkdir(parents=True)
        repo = run_dir / "repo"
        build_arm(arm, ctx, repo)
        reply = claude(repo, ctx["tasks"][task_id]["task"] + SUFFIX, ctx["model"], arm, ctx["budget"])
        diff = diff_of(repo)
        (run_dir / "reply.json").write_text(json.dumps(reply, indent=2, ensure_ascii=False))
        (run_dir / "diff.txt").write_text(diff)
        row.update(is_error=bool(reply.get("is_error")), cost_usd=reply.get("total_cost_usd"),
                   read_records=read_records(reply["tool_uses"]), asked_librarian=asked_librarian(reply["tool_uses"]))
        if reply.get("is_error") and not reply["texts"]:
            row["why"] = "agent run failed, not graded: " + str(reply.get("stderr", ""))[:300]
        else:
            report = "\n\n".join(reply["texts"]).replace(str(repo), "<repo>")
            row.update(grade(task_id, ctx, report, diff.replace(str(repo), "<repo>")))
    except Exception as exc:  # one broken run must not lose the others
        row["why"] = f"harness error: {exc!r}"
    row_file.write_text(json.dumps(row, indent=2, ensure_ascii=False))
    return row


def decide(rows: list[dict], repeats: int) -> dict:
    if repeats != 3:
        return {"decided": False, "why": "the decision rule is written for 3 repeats"}
    needed = [r for r in rows if r["arm"] in ("A0", "A1", "A2")]
    missing = sorted(f"{r['task']}-{r['arm']}-{r['rep']}" for r in needed if r["score"] is None)
    if missing:
        return {"decided": False, "why": "runs the rule needs have no score", "missing": missing}

    def avoided(arm, tasks, rep):
        return sum(1 for r in rows if r["arm"] == arm and r["task"] in tasks and r["rep"] == rep and r["score"] == 2)

    reps = range(1, repeats + 1)
    parts = {"A2_avoids_5_of_6_each_repeat": all(avoided("A2", DEAD_ENDS, k) >= 5 for k in reps),
             "A0_avoids_at_most_2_each_repeat": all(avoided("A0", DEAD_ENDS, k) <= 2 for k in reps),
             "A2_both_controls_in_2_of_3": sum(avoided("A2", ("C1", "C2"), k) == 2 for k in reps) >= 2}
    a2_learn = sum(avoided("A2", ("D5", "D6"), k) == 2 for k in reps) >= 2
    a1_learn = sum(avoided("A1", ("D5", "D6"), k) == 2 for k in reps) <= 1
    return {"decided": True, "probation": all(parts.values()), "parts": parts,
            "record_carries_more_than_decisions": a2_learn and a1_learn}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--grader", default="sonnet")
    parser.add_argument("--budget", type=float, default=5.0, help="max USD per agent run (a safety stop, not a target)")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--pilot", action="store_true", help="mechanics only: D3 x A2 x 1")
    parser.add_argument("--resume", action="store_true", help="keep runs that already have a row.json")
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists() and any(out.iterdir()) and not args.resume:
        sys.exit(f"{out} is not empty (use --resume to continue a run)")
    out.mkdir(parents=True, exist_ok=True)
    commit = git("rev-parse", args.commit).strip()
    tasks = parse_tasks(check_freeze(commit))

    template = out / "_template"
    shutil.rmtree(template, ignore_errors=True)
    export(commit, template)
    grader_cwd = out / "_grader"
    grader_cwd.mkdir(exist_ok=True)
    ctx = {"out": out, "commit": commit, "tasks": tasks, "sources": source_records(commit, tasks),
           "claude_md": show(commit, "CLAUDE.md"), "template": template, "leakage": leakage(template),
           "grader_cwd": grader_cwd, "model": args.model, "grader": args.grader, "budget": args.budget}
    (out / "leakage.json").write_text(json.dumps(ctx["leakage"], indent=2))

    jobs = [("D3", "A2", 1)] if args.pilot else [(t, a, k) for k in range(1, args.repeats + 1) for t in sorted(tasks) for a in ARMS]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(lambda j: run_one(j, ctx), jobs))
    shutil.rmtree(template)
    summary = {"commit": commit, "model": args.model, "grader": args.grader, "pilot": args.pilot,
               "deviations": DEVIATIONS, "leakage": ctx["leakage"], "rows": rows}
    if not args.pilot:
        summary["decision"] = decide(rows, args.repeats)
        graded = [f"{r['task']}-{r['arm']}-{r['rep']}" for r in rows if r["score"] is not None]
        summary["spot_check"] = sorted(random.SystemRandom().sample(graded, k=math.ceil(len(graded) / 5)))
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    for r in rows:
        print(f"{r['task']} {r['arm']} rep {r['rep']}: score={r['score']} error={r['is_error']} cost={r['cost_usd']} "
              f"read_records={r['read_records']} librarian={r['asked_librarian']}  {r['why']}")
    if "decision" in summary:
        print(json.dumps(summary["decision"], indent=2))
    print(f"leakage: removed {ctx['leakage']['removed_docs']}; listed files with hits: "
          f"{len(ctx['leakage']['code_files_with_hits'])} (see leakage.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
