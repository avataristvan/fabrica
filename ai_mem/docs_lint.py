"""Lint of an area's documents outside the records: experiments, handoffs, and records that cite a handoff.

The places and lifecycles are the documentation map (`reference/documentation_map.md`). Every check here only
reports; nothing is fixable, since each finding asks for a judgment about where content belongs.
"""
from __future__ import annotations

import re
from pathlib import Path

EXPERIMENTS_DIRNAME = "experiments"
EXPERIMENT_FILENAME = "README.md"
EXPERIMENT_STATUSES = ("planned", "running", "done")

EXPERIMENT_FRONTMATTER = "experiment-frontmatter"
EXPERIMENT_STATUS = "experiment-status"
HANDOFF_SHAPE = "handoff-shape"
HANDOFF_CITED = "handoff-cited"

_HANDOFF_NAME = re.compile(r"handoff-\d{4}-\d{2}-\d{2}\.md$")
_HANDOFF_SECTIONS = ("charter", "conclusions", "open points", "start with")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}")
_HANDOFF_MENTION = re.compile(r"handoff-\d{4}-\d{2}-\d{2}\.md")
_COMMIT_PREFIX = re.compile(r"[0-9a-f]{7,40}:(?:\S*/)?$")


def docs_dir(records_dir: Path) -> Path:
    return records_dir.parent


def experiments_dir(records_dir: Path) -> Path:
    return docs_dir(records_dir) / EXPERIMENTS_DIRNAME


def records_dir_holding(path: Path, kind: str) -> Path | None:
    """The records directory of the area whose experiment (`kind="experiment"`) or handoff (`"handoff"`) `path` is.

    The area is found by walking up `path` (lexically, as `AI_MEM_ADR_DIR` may move the records directory)."""
    from ai_mem.infrastructure.adr_paths import records_dir_for_root

    is_kind = is_experiment_file if kind == "experiment" else is_handoff_file
    for root in path.parents:
        records_dir = records_dir_for_root(root)
        if is_kind(path, records_dir):
            return records_dir if records_dir.is_dir() else None
    return None


def is_experiment_file(path: Path, records_dir: Path) -> bool:
    return path.name == EXPERIMENT_FILENAME and path.parent.parent == experiments_dir(records_dir)


def is_handoff_file(path: Path, records_dir: Path) -> bool:
    return path.parent == docs_dir(records_dir) and bool(_HANDOFF_NAME.fullmatch(path.name))


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    """(fields, body) of a `---`-fenced frontmatter, or None when the file has none."""
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            fields = {}
            for line in lines[1:end]:
                key, sep, value = line.partition(":")
                if sep and key.strip():
                    fields[key.strip()] = value.strip()
            return fields, "\n".join(lines[end + 1:])
    return None


def experiment_status(text: str) -> str:
    parsed = _frontmatter(text)
    return parsed[0].get("status", "") if parsed else ""


def check_experiment(path: Path) -> list[tuple[str, str]]:
    """(code, message) for one experiment file."""
    text = _read(path)
    if text is None:
        return [(EXPERIMENT_FRONTMATTER, "cannot be read")]
    parsed = _frontmatter(text)
    if parsed is None:
        return [(EXPERIMENT_FRONTMATTER, "no `---` frontmatter (question, status, date)")]
    fields, body = parsed
    status = fields.get("status", "")
    if status not in EXPERIMENT_STATUSES:
        return [(EXPERIMENT_STATUS, f"status {status!r} is not one of {', '.join(EXPERIMENT_STATUSES)}")]
    required = ["question", "date"] + (["setup"] if status in ("running", "done") else [])
    problems = [(EXPERIMENT_FRONTMATTER, f"{key}: missing or empty") for key in required if not fields.get(key)]
    if status == "done" and not re.search(r"(?m)^## Result\b", body):
        problems.append((EXPERIMENT_FRONTMATTER, "done without a `## Result` section"))
    return problems


def check_handoff(path: Path) -> list[tuple[str, str]]:
    """(code, message) for one handoff: only Charter, Conclusions, Open points, Start with; no dated sections or run tables."""
    text = _read(path)
    if text is None:
        return []
    problems = []
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            if _DATE.search(heading):
                problems.append((HANDOFF_SHAPE, f"dated section {heading[:50]!r}: runs and results belong in an experiment"))
            elif not heading.lower().startswith(_HANDOFF_SECTIONS):
                problems.append((HANDOFF_SHAPE, f"section {heading[:50]!r}: a handoff holds Charter, Conclusions, Open points, Start with"))
    if any(_TABLE_RULE.match(line) and "|" in line for line in text.splitlines()):
        problems.append((HANDOFF_SHAPE, "a table: runs belong in an experiment, facts in docs/reference/"))
    return problems


def handoff_citations(text: str) -> list[str]:
    """Handoff file names a record text cites, except as a commit reference `<sha>:docs/handoff-<date>.md`."""
    cited = []
    for match in _HANDOFF_MENTION.finditer(text):
        start = max(text.rfind(sep, 0, match.start()) for sep in " \t\n([`'\"<") + 1
        if not _COMMIT_PREFIX.search(text[start:match.start()]):
            cited.append(match.group())
    return cited


def experiment_files(records_dir: Path) -> list[Path]:
    directory = experiments_dir(records_dir)
    return sorted(directory.glob(f"*/{EXPERIMENT_FILENAME}")) if directory.is_dir() else []


def handoff_files(records_dir: Path) -> list[Path]:
    directory = docs_dir(records_dir)
    return sorted(p for p in directory.glob("handoff-*.md") if _HANDOFF_NAME.fullmatch(p.name)) if directory.is_dir() else []
