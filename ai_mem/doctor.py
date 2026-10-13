"""`mem doctor` -- a deterministic, read-only diagnosis of whether the records practice is still alive.

No LLM, no repair (domain_doctor_diagnoses_ritual_erosion_2026_10_10). The only file written is the
timestamp `$AI_MEM_PATH/doctor_last_run` (epoch seconds, `DOCTOR_STAMP`), which the SessionStart pointer reads (D7).
Findings go to the archivist (records) or the setup assistant (wiring). Output depends only on the
files scanned; the clock enters only as the Effect window (`--days`). Exit code 0 (the report is the result), 2 for invalid input.
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from ai_mem import upgrade_guard
from ai_mem.doctor_sources import collect_sources
from ai_mem.domain.memory import parse_edges
from ai_mem.hooks import DOCTOR_STAMP, RETRO_LOG, state_dir
from ai_mem.infrastructure.adr_paths import focus_path, records_home, write_atomic
from ai_mem.infrastructure.areas import Area, discover_areas, find_area, resolve_ref
from ai_mem.records_lint import Code, RawRecord, edge_targets, git_output, lint_records, read_area

_DANGLING = (Code.EDGE_DANGLING, Code.EDGE_UNRESOLVED, Code.EDGE_DANGLING_XAREA)
_INDEX_CODES = (Code.INDEX_MISSING, Code.INDEX_STALE)
_LEGACY_PARENT = "ai-mem-records"
_TICKED = re.compile(r"`([^`\n]+)`")
_REPO_PATH = re.compile(r"^[\w@+-][\w.@+-]*(?:/[\w.@+-]+)+$")
_EXTENSION = re.compile(r"\.[A-Za-z][A-Za-z0-9]{0,4}$")
_HOOK_IN = "handoff-protocol"
_TEAM_SIGNALS = re.compile(r"Agent\(|subagent_type|ai-mem|mem_query|mem_add|\blibrarian\b|\barchivist\b|docs/records")
_EXPECTED_HOOKS = (("SessionStart", "ai_mem.hook"), ("SubagentStop", "ai_mem.hooks.retro_check"),
                   ("PostToolUse", "ai_mem.hooks.lint_after_write"), ("Stop", "ai_mem.hooks.reflect_reminder"))
_READ_LIMIT = 1_000_000  # bytes of one scanned file; everything under ~/.claude and the log is untrusted input
_MAX_FILES = 2000
_MAX_LOG_LINES = 200_000
_CUE_SHARPENING_CONFIRMS = 3
_RETRO_FIELDS = ("records_consulted", "record_candidates", "missing_fields")
_DAY = 86400
_STATE_TOLERANCE_SECONDS = 3600  # a record written minutes after FOCUS.md is not erosion


def _toplevel(root: Path) -> Path | None:
    """The git work tree containing `root`, or None when `root` is not under version control."""
    out = (git_output(root, "rev-parse", "--show-toplevel") or "").strip()
    return Path(out) if out else None


def _commit_time(root: Path, pathspec: str) -> float | None:
    out = (git_output(root, "log", "-1", "--format=%ct", "--", pathspec) or "").strip()
    return float(out) if out else None


def _missing_paths(body: str, roots: list[Path]) -> list[str]:
    """Backticked repo-relative file paths in `body` (contain '/', end in an extension) that exist under none of `roots`."""
    missing = []
    for ticked in _TICKED.findall(body):
        path = ticked.removeprefix("./")
        if not _REPO_PATH.fullmatch(path) or any(not segment.strip(".") for segment in path.split("/")) or not _EXTENSION.search(path):
            continue
        if not any(os.path.exists(root / path) for root in roots) and path not in missing:
            missing.append(path)
    return missing


def _index_tokens(area: Area) -> set[str]:
    index = area.records_dir / "INDEX.md"
    try:
        return set(re.split(r"[\s|\[\]()]+", index.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError):
        return set()


def _is_legacy(area: Area) -> bool:
    home = records_home()
    return area.root.parent.name == _LEGACY_PARENT or (home is not None and area.root.parent == home.resolve())


def _state(area: Area, records: list[RawRecord], versioned: bool) -> list[dict]:
    """FOCUS.md and the newest docs/handoff-*.md compared with the newest change in the area."""
    handoffs = sorted(p for p in (area.root / "docs").glob("handoff-*.md") if p.is_file() and not p.is_symlink())
    files = [p for p in (focus_path(area.records_dir), *handoffs[-1:]) if p.is_file() and not p.is_symlink()]
    if not files:
        return []
    if versioned:
        newest = _commit_time(area.root, ".")

        def stamp(path: Path) -> float:
            return _commit_time(area.root, str(path)) or path.stat().st_mtime
    else:
        newest = max((r.path.stat().st_mtime for r in records if r.path.is_file()), default=None)

        def stamp(path: Path) -> float:
            return path.stat().st_mtime
    if newest is None:
        return []
    out = []
    for path in files:
        written = stamp(path)
        if newest - written >= _STATE_TOLERANCE_SECONDS:
            out.append({"file": path.relative_to(area.root).as_posix(), "behind_days": round((newest - written) / _DAY, 1),
                        "basis": "last commit" if versioned else "mtime"})
    return out


def _read_text(path: Path) -> str | None:
    """Up to `_READ_LIMIT` bytes of a regular file (symlinks to files are followed); None for anything else or on error."""
    try:
        if not path.is_file():  # also False for FIFOs and devices, which could block a read
            return None
        with open(path, "rb") as handle:
            return handle.read(_READ_LIMIT).decode("utf-8", errors="replace")
    except OSError:
        return None


def _printable(value: str, limit: int = 80) -> str:
    return "".join(c if c.isprintable() else "?" for c in value)[:limit]


def _team_files(home: Path) -> list[Path]:
    claude = home / ".claude"
    found: list[Path] = []
    for folder, pattern in (("commands", "*.md"), ("agents", "*.md"), ("skills", "*/SKILL.md")):
        try:
            found += sorted(claude.joinpath(folder).glob(pattern))
        except OSError:
            continue
    return found[:_MAX_FILES]


def _hook_commands(hooks: object, event: str) -> list[str]:
    groups = hooks.get(event) if isinstance(hooks, dict) else None
    if not isinstance(groups, list):
        return []
    return [h["command"] for g in groups if isinstance(g, dict) and isinstance(g.get("hooks"), list)
            for h in g["hooks"] if isinstance(h, dict) and isinstance(h.get("command"), str)]


def _registered_hooks(settings: object) -> tuple[list[str], bool]:
    """(expected hook modules found in the settings' `hooks`, whether `enabledPlugins` enables ai-mem)."""
    if not isinstance(settings, dict):
        return [], False
    hooks = settings.get("hooks")
    registered = [module for event, module in _EXPECTED_HOOKS
                  if any(re.search(rf"-m\s+{re.escape(module)}(?:\s|$)", c) for c in _hook_commands(hooks, event))]
    plugins = settings.get("enabledPlugins")
    plugin = isinstance(plugins, dict) and any(isinstance(k, str) and k.startswith("ai-mem@") and v is True for k, v in plugins.items())
    return registered, plugin


def collect_wiring(home: Path) -> dict:
    """Teams (commands, agents, skills that spawn agents or name memory) lacking the hand-off marker, and the registered hooks."""
    without, scanned = [], 0
    for path in _team_files(home):
        text = _read_text(path)
        if text is None or not _TEAM_SIGNALS.search(text):
            continue
        scanned += 1
        if _HOOK_IN not in text:
            without.append(_printable(path.relative_to(home / ".claude").as_posix(), 200))
    settings_text = _read_text(home / ".claude" / "settings.json")
    try:
        settings = json.loads(settings_text) if settings_text else None
    except (ValueError, RecursionError):
        settings = None
    registered, plugin = _registered_hooks(settings)
    # TODO(chunk 6): also scan the skills/agents of enabled ai-mem@... plugins (needs the plugin cache layout).
    return {"claude_dir": (home / ".claude").is_dir(), "teams": scanned, "teams_without_hook_in": without, "plugin_enabled": plugin,
            "hooks_registered": registered, "hooks_missing": [m for _, m in _EXPECTED_HOOKS if m not in registered]}


def _log_entries(log: Path) -> list[dict]:
    """Retro log objects, malformed lines skipped; a blocked agent logs twice with one agent_id, the last entry wins."""
    by_agent: dict[str, dict] = {}
    anonymous: list[dict] = []
    try:
        if not log.is_file():  # a FIFO would block the open
            return []
        with open(log, "rb") as handle:
            for _ in range(_MAX_LOG_LINES):
                line = handle.readline(_READ_LIMIT)
                if not line:
                    break
                try:
                    item = json.loads(line)
                except (ValueError, RecursionError):
                    continue
                if not isinstance(item, dict):
                    continue
                agent_id = item.get("agent_id")
                if isinstance(agent_id, str) and agent_id:
                    by_agent[agent_id] = item
                else:
                    anonymous.append(item)
    except OSError:
        return []
    return [*by_agent.values(), *anonymous]


def _given(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower().rstrip(".") not in ("", "none")


def collect_effect(log: Path, days: int, now: float, confirmed: list[dict]) -> dict:
    entries = _log_entries(log)
    cutoff = now - days * _DAY
    stats: dict[str, dict[str, int]] = {}
    for item in entries:
        ts, agent_type = item.get("ts"), item.get("agent_type")
        in_window = isinstance(ts, (int, float)) and not isinstance(ts, bool) and cutoff <= ts <= now + _DAY  # tolerate clock skew
        if not in_window or not isinstance(agent_type, str):
            continue
        entry = stats.setdefault(_printable(agent_type), dict.fromkeys(("entries", *_RETRO_FIELDS), 0))
        entry["entries"] += 1
        entry["records_consulted"] += int(_given(item.get("records_consulted")))
        entry["record_candidates"] += int(_given(item.get("record_candidates")))
        entry["missing_fields"] += int(bool(item.get("missing")))
    return {"days": days, "log_entries": len(entries),
            "retro": {name: {**s, **{f"{k}_rate": round(s[k] / s["entries"], 2) for k in _RETRO_FIELDS}} for name, s in sorted(stats.items())},
            "cue_sharpening": confirmed}


def collect(areas: list[Area]) -> dict:
    scans = {area.root: read_area(area) for area in areas}
    incoming: set[tuple[Path, str]] = set()
    confirms: dict[tuple[Path, str], set[Path]] = {}
    existing: set[tuple[Path, str]] = set()
    for area in areas:
        for record in scans[area.root]:
            existing.add((area.root, record.path.stem))
            try:
                edges = parse_edges(record.value("edges"))
                targets = [edge["target_id"] for edge in edges]
            except ValueError:  # lint's lenient reader still finds the targets of a half-valid list
                edges, targets = [], edge_targets(record)
            for target in targets:
                resolved = resolve_ref(area, target)
                if resolved is not None:
                    incoming.add((resolved[0].root, resolved[1]))
            for edge in edges:
                resolved = resolve_ref(area, edge["target_id"]) if edge["edge_type"] == "confirms" else None
                if resolved is not None:
                    key = (resolved[0].root, resolved[1])
                    confirms.setdefault(key, set()).add(record.path)

    report_areas, state = [], []
    for area in areas:
        records = scans[area.root]
        findings = lint_records(area, records)
        toplevel = _toplevel(area.root)
        versioned = toplevel is not None
        roots = [area.root, *([toplevel] if toplevel else [])]
        tokens = _index_tokens(area)
        fixable_files = sorted({f.file.relative_to(area.records_dir).as_posix() for f in findings if f.fixable and f.code not in _INDEX_CODES})
        not_in_index = sorted(r.rel.as_posix() for r in records if r.fields is not None and r.value("id") and r.value("id") not in tokens)
        dead_weight = []
        for record in records:
            if record.fields is None or (area.root, record.path.stem) in incoming:
                continue
            gone = _missing_paths(record.body, roots)
            if gone:
                dead_weight.append({"file": record.rel.as_posix(), "missing": gone})
        counts: dict[str, int] = {}
        for finding in findings:
            counts[finding.code] = counts.get(finding.code, 0) + 1
        report_areas.append({
            "root": str(area.root),
            "records": len(records),
            "findings": counts,
            "fixable": sum(1 for f in findings if f.fixable),
            "dangling_edges": [f"{f.file.relative_to(area.records_dir).as_posix()}: {f.message}" for f in findings if f.code in _DANGLING],
            "legacy_collection": _is_legacy(area),
            "hand_written": {"fix_would_change": fixable_files, "missing_from_index": not_in_index,
                             "index_differs": any(f.code in _INDEX_CODES for f in findings)},
            "dead_weight": dead_weight,
            "versioned": versioned,
            "sources": collect_sources(area, [r.body for r in records],
                                       {entry_id for root, entry_id in incoming if root == area.root}),
        })
        state += [{"root": str(area.root), **item} for item in _state(area, records, versioned)]
    confirmed = [{"root": str(root), "id": entry_id, "confirms": len(sources)} for (root, entry_id), sources in sorted(confirms.items())
                 if len(sources) >= _CUE_SHARPENING_CONFIRMS and (root, entry_id) in existing]
    return {"areas": report_areas, "state": state, "confirmed": confirmed}


def _label(root: str, base: Path) -> str:
    rel = os.path.relpath(root, base)
    return "." if rel == "." else Path(rel).as_posix()


def _render_wiring(wiring: dict) -> list[str]:
    hooks = wiring["hooks_registered"]
    if wiring["plugin_enabled"]:
        out = ["  hooks: ai-mem plugin enabled"]
    elif wiring["hooks_missing"]:
        out = [f"  hooks: {len(hooks)}/{len(_EXPECTED_HOOKS)} registered in settings.json, missing: {', '.join(wiring['hooks_missing'])}"]
    else:
        out = [f"  hooks: all {len(_EXPECTED_HOOKS)} registered in settings.json"]
    if not wiring["claude_dir"]:
        return out + ["  no .claude directory under the home that was checked: nothing scanned"]
    without = wiring["teams_without_hook_in"]
    out.append(f"  teams without `{_HOOK_IN}` ({len(without)} of {wiring['teams']} that spawn agents or name memory):" if without
               else f"  all {wiring['teams']} teams that spawn agents or name memory carry `{_HOOK_IN}`")
    return out + [f"    {name}" for name in without]


def _render_effect(effect: dict, base: Path) -> list[str]:
    retro = effect["retro"]
    if retro:
        out = [f"  retro log, last {effect['days']} days:"]
    else:
        out = ["  no retro data yet" if not effect["log_entries"] else f"  no retro entries in the last {effect['days']} days"]
    for name, s in retro.items():
        out.append(f"    {name}: {s['entries']} stop(s), records_consulted given {s['records_consulted_rate']:.0%}, "
                   f"record_candidates given {s['record_candidates_rate']:.0%}, retro fields missing {s['missing_fields_rate']:.0%}")
    if effect["cue_sharpening"]:
        out.append(f"  cue-sharpening candidates (>= {_CUE_SHARPENING_CONFIRMS} incoming confirms):")
        out += [f"    {_label(c['root'], base)}: {c['id']} ({c['confirms']})" for c in effect["cue_sharpening"]]
    return out


def _render_sources(areas: list[dict], base: Path) -> list[str]:
    out = []
    for a in areas:
        s = a["sources"]
        if not (s["total"] or s["retired_in_current"]):
            continue
        label = _label(a["root"], base)
        out.append(f"  {label}: {s['total']} sources, {len(s['unprocessed'])} unprocessed (awaiting the archivist)")
        for title, key in (("sources with a bad or missing frontmatter field", "malformed"),
                           ("processed sources that no record points to", "unpointed")):
            lines = [f"{item['file']}: {item['problem']}" if key == "malformed" else item for item in s[key]]
            out += [f"    {title}:", *(f"      {line}" for line in lines)] if lines else []
        if s["retired_in_current"]:
            out.append("    docs naming a retired system without a historical marker (move to docs/sources/ or mark):")
            out += [f"      {d['file']}: {', '.join(d['keywords'])}" for d in s["retired_in_current"]]
    return out or ["  no sources and no docs to check"]


def render(report: dict, base: Path) -> str:
    out = [f"mem doctor (root: {base})", "", "Records"]
    areas = report["areas"]
    if not areas:
        out.append("  no areas found")
    for item in areas:
        label = _label(item["root"], base)
        total = sum(item["findings"].values())
        detail = ", ".join(f"{code} {n}" for code, n in sorted(item["findings"].items()))
        out.append(f"  {label}: {item['records']} records, " + (f"{total} lint findings ({item['fixable']} fixable): {detail}" if total else "lint clean"))
    for title, picked in (
        ("dangling edges", lambda a: a["dangling_edges"]),
        ("dead-weight candidates (no incoming edges, backticked path no longer exists)",
         lambda a: [f"{d['file']}: {', '.join(d['missing'])}" for d in a["dead_weight"]]),
    ):
        lines = [f"    {_label(a['root'], base)}: {line}" for a in areas for line in picked(a)]
        out += [f"  {title}:", *lines] if lines else []
    legacy = [_label(a["root"], base) for a in areas if a["legacy_collection"]]
    if legacy:
        out += ["  records under collection names (legacy folders under ai-mem-records/):", *(f"    {name}" for name in legacy)]
    adopt = []
    for a in areas:
        hand = a["hand_written"]
        if hand["fix_would_change"] or hand["missing_from_index"] or hand["index_differs"]:
            adopt.append(f"    {_label(a['root'], base)}: lint --fix would change {len(hand['fix_would_change'])} file(s), "
                         f"{len(hand['missing_from_index'])} missing from INDEX.md, INDEX.md {'differs from generated' if hand['index_differs'] else 'matches generated'}")
    if adopt:
        out += ["  hand-written records not yet adopted:", *adopt]
    unversioned = [_label(a["root"], base) for a in areas if not a["versioned"]]
    if unversioned:
        out += ["  areas not under version control:", *(f"    {name}" for name in unversioned)]
    out += ["", "Sources"] + _render_sources(areas, base)
    out += ["", "State"]
    if report["state"]:
        out += [f"  {_label(s['root'], base)}: {s['file']} is {s['behind_days']} day(s) behind the newest change ({s['basis']})" for s in report["state"]]
    else:
        out.append("  FOCUS.md and handoff are current")
    migration = report["migration"]
    out += ["", "Migration", f"  {'pending: Chroma store without records_v1.done, see UPGRADING.md' if migration['pending'] else 'none pending'}",
            "", "Wiring", *_render_wiring(report["wiring"]), "", "Effect", *_render_effect(report["effect"], base)]
    return "\n".join(out)


def configure(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", metavar="DIR", help="scan every area at or below DIR (default: the current area)")
    parser.add_argument("--home", metavar="DIR", help="home whose .claude/ is checked for wiring (default: the real home)")
    parser.add_argument("--days", type=int, default=30, help="retro log window for the Effect section (default 30)")
    parser.add_argument("--json", action="store_true", help="print the report as one JSON object")


def run(args: argparse.Namespace) -> int:
    if not 1 <= args.days <= 36500:
        print("mem doctor: --days must be between 1 and 36500", file=sys.stderr)
        return 2
    try:
        home = Path(args.home).expanduser() if args.home else Path.home()
    except RuntimeError:
        print("mem doctor: cannot determine the home directory", file=sys.stderr)
        return 2
    if args.root:
        base = Path(args.root).expanduser().resolve()
        if not base.is_dir():
            print(f"mem doctor: {args.root} is not a directory", file=sys.stderr)
            return 2
        areas = discover_areas(base)
    else:
        current = find_area(Path.cwd())
        if current is None:
            print("mem doctor: no area here (no docs/records/ in this folder or above); use --root", file=sys.stderr)
            return 2
        base, areas = current.root, [current]
    db_path = state_dir()
    report = collect(areas)
    report["root"] = str(base)
    report["wiring"] = collect_wiring(home)
    report["effect"] = collect_effect(db_path / RETRO_LOG, args.days, time.time(), report.pop("confirmed"))
    report["migration"] = {"pending": upgrade_guard.migration_pending(db_path)}
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render(report, base))
    try:
        write_atomic(db_path / DOCTOR_STAMP, f"{int(time.time())}\n")
    except OSError as exc:
        print(f"mem doctor: could not record the run time: {exc}", file=sys.stderr)
    return 0
