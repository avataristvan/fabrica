"""`mem review` -- the records a push would publish, for a last look before squashing and pushing.

Lists the records added, changed, renamed, deleted or superseded between a base (default `@{upstream}`) and HEAD,
and flags in their text what should not leave this machine or will not survive a squash:
- an absolute home path (`/home/<name>/`, `/Users/<name>/`);
- a private name from `$AI_MEM_PATH/private_names` (one per line; optional);
- a commit hash that is not on this branch (squashed away or local-only), or that is on this branch but not yet in
  the base (squashing at the push would orphan it).
Read-only; corrections go through the archivist. Exit 0 (the list is the result), 2 for invalid input. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from ai_mem.domain.memory import title_of
from ai_mem.hooks import state_dir
from ai_mem.infrastructure import adr_markdown
from ai_mem.infrastructure.areas import find_area
from ai_mem.records_lint import git_output

PRIVATE_NAMES = "private_names"
_HOME_PATH = re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+/")
# A cited hash: 7-40 hex digits with at least one digit and one letter, not part of a word, path or UUID.
# (An all-numeric short hash is missed; a measurement or an epoch is far more common in a record.)
_SHA = re.compile(r"(?<![\w-])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w-])")
_STATUS = {"A": "added", "M": "changed", "D": "deleted", "R": "renamed"}


def _private_names() -> list[str]:
    try:
        lines = (state_dir() / PRIVATE_NAMES).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


class _Commits:
    """Which cited hashes are commits, on this branch, and already in the base: two rev-lists, one rev-parse per hash."""

    def __init__(self, root: Path, base: str) -> None:
        self._root, self._base = root, base
        self._on_branch = set((git_output(root, "rev-list", "HEAD") or "").split())
        self._unpushed = set((git_output(root, "rev-list", f"{base}..HEAD") or "").split())
        self._full: dict[str, str | None] = {}

    def problem(self, sha: str) -> str | None:
        if sha not in self._full:
            out = git_output(self._root, "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}")
            self._full[sha] = out.strip() if out else None
        full = self._full[sha]
        if full is None or not self._on_branch:
            return None  # not a commit here (a hash of something else, an unknown one), or git failed: not judged
        if full not in self._on_branch:
            return f"cites commit {sha}, which is not on this branch (squashed away or local-only)"
        if full in self._unpushed:
            return f"cites commit {sha}, not yet in {self._base}: a squash at the push would orphan it"
        return None


def _flags(text: str, commits: _Commits, names: list[str]) -> list[str]:
    flags = [f"machine path {path}" for path in sorted(set(_HOME_PATH.findall(text)))]
    flags += [f"private name {name!r}" for name in names if re.search(rf"(?i)\b{re.escape(name)}\b", text)]
    flags += [problem for sha in sorted(set(_SHA.findall(text))) if (problem := commits.problem(sha))]
    return flags


def collect(root: Path, records_dir: Path, base: str) -> list[dict]:
    out = git_output(root, "diff", "-z", "--relative", "--name-status", "--find-renames", f"{base}..HEAD", "--", str(records_dir))
    if out is None:
        raise ValueError(f"cannot compare with {base!r} (no upstream? pass --since <ref>)")
    names, commits = _private_names(), _Commits(root, base)
    fields, changes = out.split("\0"), []
    i = 0
    while i + 1 < len(fields):  # -z: status, path (renames: status, old path, new path)
        status = fields[i][:1]
        step = 3 if status in ("R", "C") else 2
        changes.append((status, fields[i + step - 1]))
        i += step
    items = []
    for status, path in changes:
        file = root / path
        if file.suffix != ".md" or file.parent == records_dir:  # INDEX.md, FOCUS.md, BACKLOG.md are not records
            continue
        item = {"file": path, "change": _STATUS.get(status, status), "title": "", "superseded": False, "flags": []}
        if status != "D":
            text = git_output(root, "show", f"HEAD:./{path}") or ""
            try:
                parsed = adr_markdown.parse(text, entry_id=file.stem)
                item["title"], item["superseded"] = title_of(parsed.text), bool(parsed.superseded_by)
            except ValueError:
                item["title"] = "(unparsable)"
            item["flags"] = _flags(text, commits, names)
        items.append(item)
    return items


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--area", metavar="PATH", help="area folder (default: nearest ancestor of cwd with docs/records/)")
    parser.add_argument("--since", default="@{upstream}", metavar="REF", help="compare HEAD with REF (default: @{upstream})")
    parser.add_argument("--json", action="store_true", help="one JSON object per record")


def run(args: argparse.Namespace) -> int:
    area = find_area(Path(args.area).expanduser() if args.area else Path.cwd())
    if area is None:
        print("mem review: no area (no docs/records/ in this folder or above)", file=sys.stderr)
        return 2
    try:
        items = collect(area.root, area.records_dir, args.since)
    except ValueError as exc:
        print(f"mem review: {exc}", file=sys.stderr)
        return 2
    for item in items:
        if args.json:
            print(json.dumps(item, ensure_ascii=False))
            continue
        mark = " (superseded)" if item["superseded"] else ""
        print(f"{item['change']:8} {item['file']}{mark}\n         {item['title']}")
        for flag in item["flags"]:
            print(f"         ! {flag}")
    if not items and not args.json:
        print(f"no record changes since {args.since}")
    return 0
