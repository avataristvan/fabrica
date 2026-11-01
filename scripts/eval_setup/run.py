#!/usr/bin/env python3
"""Exit check of the setup skill (/fabrica:setup) in fresh `claude -p` processes; see README.md."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CANONICAL = "At this boundary follow the Fabrica handoff protocol (skill `fabrica:handoff-protocol`)."
REMOVED = " At this boundary follow the Fabrica handoff protocol (skill `handoff-protocol`)."

CLAUDE_MD = """# CLAUDE.md

## Overview

Bookshop is a small Next.js storefront. App Router only.

## Commands

```bash
npm run dev     # local server
npm test        # unit tests
```

## Conventions

- Prices are stored in cents.
- Never call Firestore from the frontend.
"""

RELEASE_TRAIN = """---
name: release-train
description: "Cut a release: spawn a coder to prepare the changelog and version bump, then a reviewer on the diff, then tag."
---

# Release train

1. Collect merged PRs since the last tag (`git log --oneline <last-tag>..HEAD`).
2. Spawn the coder with the release scope:
   Agent(subagent_type="the-coder", prompt="Prepare release <version>: bump the version in package.json, write CHANGELOG.md from these PRs: <list>. Touch nothing else.")
3. When the coder reports back, spawn the reviewer on the diff:
   Agent(subagent_type="pr-review-toolkit:code-reviewer", prompt="Review the release diff in <worktree>: version bump consistent, changelog complete.")
4. Apply the reviewer's findings, then tag `v<version>` (the user pushes).
"""

BOOKSHOP_COPY = """---
name: bookshop-copy
description: "Write product descriptions for the bookshop in the house voice."
---

# Bookshop copy

Write one product description per book the user names: 60-80 words, warm, no superlatives.
The house voice is a friendly librarian who has read the book and recommends it to a regular:
personal, concrete, one sentence about who will love it. Never invent awards or quotes.
"""

DOCTOR_REPORT = """mem doctor (root: {root})

Records
  .: 3 records, lint clean
  dangling edges:
    .: domain_prices_in_cents_2026_09_01 -> pattern_currency_formatting (missing)

Sources
  no sources and no docs to check

State
  FOCUS.md and handoff are current

Wiring
  hooks: ai-mem plugin enabled
  teams without `handoff-protocol` (2 of 3 that spawn agents or name memory):
    commands/release-train.md
    skills/bookshop-copy/SKILL.md

Effect
  no retro data yet
"""

PROMPTS = {
    "teams": "/fabrica:setup Part 1 only, for the team in .claude/commands/dev-team.md (project scope, the user wrote it). Skip parts 2 and 3.",
    "claude_md": "/fabrica:setup Part 2 only (CLAUDE.md), for this project; the user's ~/.claude/CLAUDE.md is out of scope here. Skip parts 1 and 3.",
    "doctor": ("/fabrica:setup Part 3 only: judge the mem doctor report in ./doctor_report.txt (the flagged files are under ./.claude/, "
               "written by the user). Do not run mem doctor yourself. Skip parts 1 and 2 except what part 3 sends you to; propose, do not apply. "
               "After your answer, add one line per flagged file: VERDICT <path as in the report> real|spurious"),
}
APPROVAL = "both lines"
TRACKED = ("CLAUDE.md", ".claude/commands/dev-team.md", ".claude/commands/release-train.md", ".claude/skills/bookshop-copy/SKILL.md")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boundary_phrase(dev_team: Path) -> str:
    """The last word before the hook-in on its line in the team file (its boundary heading): a reply must name it."""
    text = dev_team.read_text(encoding="utf-8")
    line = next((ln for ln in text.splitlines() if REMOVED in ln), None)
    phrase = line.split(REMOVED)[0].strip().rstrip(":").split()[-1] if line and line.split(REMOVED)[0].strip(" :") else ""
    if not phrase:
        sys.exit(f"{dev_team} needs a line '<boundary heading>:{REMOVED}'; the check removes the hook-in and expects the heading named")
    return phrase


def fixture(root: Path, dev_team: Path) -> None:
    """The area the run works in: a git repo with an existing CLAUDE.md, the team copy without its hook-in, two flagged files and a doctor report."""
    text = dev_team.read_text(encoding="utf-8")
    files = {
        "CLAUDE.md": CLAUDE_MD,
        ".claude/commands/dev-team.md": text.replace(REMOVED, ""),
        ".claude/commands/release-train.md": RELEASE_TRAIN,
        ".claude/skills/bookshop-copy/SKILL.md": BOOKSHOP_COPY,
        "docs/records/FOCUS.md": "Building the Bookshop app (Next.js); next: checkout flow.\n",
        "doctor_report.txt": DOCTOR_REPORT.format(root=root),
    }
    for rel, content in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(content, encoding="utf-8")
    git = ["git", "-C", str(root), "-c", "user.email=eval@local", "-c", "user.name=eval"]
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", "fixture"], check=True)


def claude(cwd: Path, model: str, plugin_dir: Path, prompt: str, resume: str | None = None) -> dict:
    cmd = ["claude", "-p", "--setting-sources", "project,local", "--plugin-dir", str(plugin_dir), "--model", model,
           "--permission-mode", "acceptEdits", "--output-format", "stream-json", "--verbose"]
    if resume:
        cmd += ["--resume", resume]
    done = subprocess.run([*cmd, prompt], cwd=cwd, capture_output=True, text=True, timeout=1200)
    # A proposal can sit in an earlier message (e.g. before a background librarian returns), so grade every assistant text.
    texts, final = [], {"is_error": True, "stderr": done.stderr[-2000:]}
    for line in done.stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":
            texts += [c.get("text", "") for c in event.get("message", {}).get("content", []) if c.get("type") == "text"]
        elif event.get("type") == "result":
            final = event
    return {**final, "result": "\n\n".join(texts)}


def verdicts(result: str) -> dict:
    return {re.sub(r"^(\./)?(\.claude/)?", "", m.group(1).strip("`")): m.group(2).lower() for m in re.finditer(r"VERDICT\s+(\S+)\s+(real|spurious)", result, re.IGNORECASE)}


def proposed_as_addition(result: str) -> bool:
    return any(ln.lstrip().startswith("+") and CANONICAL in ln for ln in result.splitlines())


def run_one(part: str, index: int, model: str, plugin_dir: Path, dev_team: Path, out: Path) -> dict:
    root = out / model / f"{part}-{index}"
    fixture(root, dev_team)
    def snapshot() -> dict:
        return {rel: sha(root / rel) for rel in TRACKED}

    before = snapshot()
    reply = claude(root, model, plugin_dir, PROMPTS[part])
    result = reply.get("result", "")
    after = snapshot()
    checks = {"no_error": not reply.get("is_error"), "files_unchanged_before_approval": before == after}
    if part == "teams":
        checks["canonical_line_proposed_in_diff"] = proposed_as_addition(result)
        checks["removed_boundary_named"] = boundary_phrase(dev_team) in result
    elif part == "claude_md":
        checks["routing_line_proposed"] = "docs/records/" in result and "fabrica:librarian" in result
        approved = claude(root, model, plugin_dir, APPROVAL, resume=reply.get("session_id"))
        numstat = subprocess.run(["git", "-C", str(root), "diff", "--numstat", "--", "CLAUDE.md"], capture_output=True, text=True).stdout.split()
        checks["applied_after_approval_additions_only"] = (not approved.get("is_error") and len(numstat) == 3
                                                           and int(numstat[0]) > 0 and numstat[1] == "0")
    else:
        found = verdicts(result)
        checks["release_train_real"] = found.get("commands/release-train.md") == "real"
        checks["bookshop_copy_spurious"] = found.get("skills/bookshop-copy/SKILL.md") == "spurious"
    (root.parent / f"{part}-{index}.json").write_text(json.dumps({"checks": checks, "reply": reply}, indent=2, ensure_ascii=False))
    models = sorted(reply.get("modelUsage", {}))
    return {"part": part, "run": index, "model": model, "models_used": models, "pass": all(checks.values()), "checks": checks}


def home_sums() -> dict:
    """The user's own configuration under ~/.claude (not session state, caches or installed plugins, which live sessions change)."""
    claude_dir = Path.home() / ".claude"
    paths = [p for folder in ("commands", "agents", "skills") for p in (claude_dir / folder).rglob("*")]
    paths += [claude_dir / "CLAUDE.md", claude_dir / "settings.json", claude_dir / "settings.local.json"]
    return {str(p): sha(p) for p in paths if p.is_file()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="empty scratch directory for fixtures and replies")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--parts", default="teams,claude_md,doctor")
    parser.add_argument("--plugin-dir", type=Path, default=REPO)
    parser.add_argument("--dev-team", type=Path, default=Path.home() / ".claude" / "commands" / "dev-team.md")
    args = parser.parse_args()
    out = args.out.resolve()
    if (out / args.model).exists():
        sys.exit(f"{out / args.model} exists; use a fresh --out")
    boundary_phrase(args.dev_team)
    home_before = home_sums()
    jobs = [(part, i) for part in args.parts.split(",") for i in range(1, args.repeats + 1)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(lambda j: run_one(j[0], j[1], args.model, args.plugin_dir.resolve(), args.dev_team, out), jobs))
    home_unchanged = home_sums() == home_before
    need = args.repeats // 2 + 1
    summary = {"model": args.model, "repeats": args.repeats, "home_claude_unchanged": home_unchanged, "runs": rows, "parts": {}}
    for part in args.parts.split(","):
        passed = sum(r["pass"] for r in rows if r["part"] == part)
        summary["parts"][part] = {"passed": passed, "of": args.repeats, "pass": passed >= need}
    (out / f"summary_{args.model}.json").write_text(json.dumps(summary, indent=2))
    for r in rows:
        print(f"{r['model']:7} {r['part']:10} run {r['run']}: {'PASS' if r['pass'] else 'FAIL'}  used={','.join(r['models_used'])}  "
              + " ".join(k for k, v in r["checks"].items() if not v))
    for part, s in summary["parts"].items():
        print(f"{args.model} {part}: {s['passed']}/{s['of']} -> {'PASS' if s['pass'] else 'FAIL'}")
    print(f"~/.claude unchanged: {home_unchanged}")
    return 0 if home_unchanged and all(s["pass"] for s in summary["parts"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
