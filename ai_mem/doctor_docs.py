"""The Docs and Not-concluded sections of `mem doctor`: does an area follow the documentation map, and what was left open?

The map is `reference/documentation_map.md`. Every finding names what fixes it: a command (mechanical), `/fabrica:setup`
(texts of the project's own agents and skills), or `/fabrica:tidy` (content that needs judgment). "Not concluded" is the
detector for a skipped reflect: it lists ages, no threshold. Read-only; stdlib only.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from ai_mem import docs_lint
from ai_mem.infrastructure.areas import Area
from ai_mem.records_lint import git_output

# Folders of docs/ that have a place in the map (Diátaxis plus records, experiments, plans, sources).
MAP_FOLDERS = frozenset({"records", "experiments", "plans", "reference", "how-to", "tutorial", "explanation", "sources"})
MIGRATION_CODES = frozenset({"legacy-refs", "bare-id", "link-stale"})
_DAY = 86400
_READ_LIMIT = 1_000_000
_BARE_NAME = r"(?<![\w/.\[-]){name}(?![\w-])(?!\.md)"


def _git(root: Path, *args: str) -> str | None:
    return git_output(root, *args)


def _age_days(root: Path, path: Path, versioned: bool, now: float) -> float:
    stamp = None
    if versioned:
        out = (_git(root, "log", "-1", "--format=%ct", "--", str(path)) or "").strip()
        stamp = float(out) if out else None
    if stamp is None:
        stamp = path.stat().st_mtime
    return round(max(0.0, now - stamp) / _DAY, 1)


def _text(path: Path) -> str:
    try:
        if path.is_symlink() or not path.is_file():
            return ""
        with open(path, "rb") as handle:
            return handle.read(_READ_LIMIT).decode("utf-8", errors="replace")
    except OSError:
        return ""


def _project_texts(root: Path) -> list[Path]:
    """The project's own agent and skill definitions and its CLAUDE.md files at the area root."""
    texts = [root / name for name in ("CLAUDE.md", "CLAUDE.local.md") if (root / name).is_file()]
    claude = root / ".claude"
    if claude.is_dir():
        texts += sorted((claude / "agents").glob("*.md")) if (claude / "agents").is_dir() else []
        texts += sorted((claude / "skills").glob("*/SKILL.md")) if (claude / "skills").is_dir() else []
    return [p for p in texts if not p.is_symlink()]


def _names_by_bare_id(text: str, names: set[str]) -> list[str]:
    """Record names `text` mentions bare (not as part of a path or link), the way an id was written before links."""
    candidates = {token for token in re.findall(r"[A-Za-z0-9][\w-]*_[\w-]*", text) if token in names}
    return sorted(name for name in candidates if re.search(_BARE_NAME.format(name=re.escape(name)), text))


def collect_docs(area: Area, record_stems: set[str], record_texts: list[str], finding_codes: dict[str, int],
                 versioned: bool, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    records_dir = area.records_dir
    docs = docs_lint.docs_dir(records_dir)
    migration = sum(n for code, n in finding_codes.items() if code in MIGRATION_CODES)

    handoffs = [{"file": p.relative_to(area.root).as_posix(), "age_days": _age_days(area.root, p, versioned, now)}
                for p in docs_lint.handoff_files(records_dir) if not p.is_symlink()]
    loose, folders = [], []
    if docs.is_dir():
        for entry in sorted(docs.iterdir()):
            if entry.is_symlink() or entry.name.startswith("."):
                continue
            if entry.is_dir() and entry.name not in MAP_FOLDERS:
                folders.append(entry.relative_to(area.root).as_posix())
            elif entry.is_file() and entry.suffix == ".md" and not docs_lint.is_handoff_file(entry, records_dir) and entry.name != "README.md":
                loose.append(entry.relative_to(area.root).as_posix())

    texts = []
    for path in _project_texts(area.root):
        named = _names_by_bare_id(_text(path), record_stems)
        if named:
            texts.append({"file": path.relative_to(area.root).as_posix(), "names": named[:5], "count": len(named)})

    data = area.root / "data"
    data_unignored = versioned and data.is_dir() and _git(area.root, "check-ignore", "-q", "data/") is None

    running, unconcluded = [], []
    corpus = "\n".join(record_texts)
    for path in docs_lint.experiment_files(records_dir):
        slug = path.parent.name
        status = _status(_text(path))
        if status == "running":
            running.append({"file": path.relative_to(area.root).as_posix(), "age_days": _age_days(area.root, path, versioned, now)})
        elif status == "done" and f"experiments/{slug}" not in corpus:
            unconcluded.append(path.relative_to(area.root).as_posix())

    commits_since_records = None
    if versioned:
        last = (_git(area.root, "log", "-1", "--format=%H", "--", str(records_dir)) or "").strip()
        if last:
            count = (_git(area.root, "rev-list", "--count", f"{last}..HEAD", "--", str(area.root)) or "").strip()
            commits_since_records = int(count) if count.isdigit() else None

    return {
        "docs": {"old_format": migration, "handoffs": handoffs, "loose_files": loose, "folders_outside_map": folders,
                 "texts_naming_records_by_id": texts, "data_not_ignored": data_unignored},
        "not_concluded": {"running_experiments": running, "done_without_record": unconcluded,
                          "handoffs": handoffs, "commits_since_records": commits_since_records},
    }


def _status(text: str) -> str:
    match = re.search(r"(?m)^status:\s*(\S+)", text.split("\n---\n", 1)[0]) if text.startswith("---\n") else None
    return match.group(1) if match else ""


def render_docs(area_label: str, area_root: str, docs: dict) -> list[str]:
    out = []
    if docs["old_format"]:
        out.append(f"  {area_label}: {docs['old_format']} finding(s) of the older record format -> mem lint --fix --area {area_root}")
    if docs["handoffs"]:
        out.append(f"  {area_label}: {len(docs['handoffs'])} handoff(s) to close by the map -> /fabrica:tidy")
    if docs["loose_files"]:
        out.append(f"  {area_label}: files in docs/ that fit no place of the map -> /fabrica:tidy")
        out += [f"    {name}" for name in docs["loose_files"]]
    if docs["folders_outside_map"]:
        out.append(f"  {area_label}: folders in docs/ outside the map (keep, or move with /fabrica:tidy): " + ", ".join(docs["folders_outside_map"]))
    for item in docs["texts_naming_records_by_id"]:
        out.append(f"  {area_label}: {item['file']} names {item['count']} record(s) by bare name, e.g. {item['names'][0]} -> /fabrica:setup")
    if docs["data_not_ignored"]:
        out.append(f"  {area_label}: data/ exists and is not git-ignored (raw data stays out of git)")
    return out


def render_not_concluded(area_label: str, nc: dict) -> list[str]:
    out = []
    for item in nc["running_experiments"]:
        out.append(f"  {area_label}: {item['file']} running, last change {item['age_days']} day(s) ago")
    for name in nc["done_without_record"]:
        out.append(f"  {area_label}: {name} done, no record links to it (data without a conclusion)")
    for item in nc["handoffs"]:
        out.append(f"  {area_label}: {item['file']} still open, last change {item['age_days']} day(s) ago")
    if nc["commits_since_records"]:
        out.append(f"  {area_label}: {nc['commits_since_records']} commit(s) since the records or FOCUS.md last changed")
    return out
