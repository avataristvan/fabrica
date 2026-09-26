#!/usr/bin/env python3
"""SessionStart hook — announces the active collection and prints the experience index; verbose mode adds focus text."""
import json
import os
import sys
from pathlib import Path

import time

DB_PATH = Path(os.environ.get("AI_MEM_PATH", Path.home() / ".local" / "share" / "ai-mem"))

# Module-level imports for patchability in tests (same pattern as posttool_hook.py).
try:
    from ai_mem.agent_context import _CONFIG_PATH, _load_settings, detect_for_session_start, write_to_env_file
    from ai_mem.application.experience_index import ExperienceIndexUseCase
    from ai_mem.application.get_memory import GetMemoryUseCase
    from ai_mem.application.list_collections import ListCollectionsUseCase
    from ai_mem.application.list_entries import title_of
    from ai_mem.infrastructure.chroma_repository import ChromaMemoryRepository
    from ai_mem.repo_context import GLOBAL_COLLECTION, WORKSPACE_COLLECTION, detect_repo_context
    from ai_mem.session_stats import record_injection
except ImportError:
    _CONFIG_PATH = None  # type: ignore[assignment]
    _load_settings = None  # type: ignore[assignment]
    detect_for_session_start = None  # type: ignore[assignment]
    write_to_env_file = None  # type: ignore[assignment]
    ExperienceIndexUseCase = None  # type: ignore[assignment]
    GetMemoryUseCase = None  # type: ignore[assignment]
    ListCollectionsUseCase = None  # type: ignore[assignment]
    title_of = None  # type: ignore[assignment]
    ChromaMemoryRepository = None  # type: ignore[assignment]
    GLOBAL_COLLECTION = "global"
    WORKSPACE_COLLECTION = "workspace"
    detect_repo_context = None  # type: ignore[assignment]
    record_injection = None  # type: ignore[assignment]

FOCUS_ID = "current_focus"
# Pull-based by default (2026-09-16): SessionStart only announces the active collection
# so agents fetch context deliberately via mem_query instead of receiving an automatic
# push of focus text, boosted entries, and session deltas on every launch. Set
# session_start_verbose: true in ~/.config/ai-mem/agents.yaml to restore the old push
# behavior for a workflow that wants it.
_SETTING_VERBOSE = "session_start_verbose"
# The experience index (chunk 3) is the one content block SessionStart still pushes: a fixed,
# small frame of "situation -> entry" lines built from cues written during /reflect. It exists
# because agents do not think to query memory unless something in their context points at an
# entry (eval_pull). Set session_start_index: false to get the routing line alone.
_SETTING_INDEX = "session_start_index"
_STATS_PATH = DB_PATH / "session_stats.json"
_SESSION_START_FILE = DB_PATH / "session_start.txt"
_PREV_SESSION_MAX_AGE_DAYS = 7
_FOCUS_PREVIEW_CHARS = 150
_GIT_COMMITS_MAX = 5
_AVAILABLE_MIN_BOOSTS = 1
_AVAILABLE_MAX = 3
_AVAILABLE_GLOBAL_MAX = 2
_EXPIRED_MAX = 3
_EXPIRED_PREVIEW_CHARS = 120


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def _session_delta(db_path: Path, current_count: int) -> int | None:
    """Return entry delta since the last session, or None if no valid prior record exists."""
    prev_file = db_path / "prev_session.json"
    try:
        data = json.loads(prev_file.read_text(encoding="utf-8"))
        age_days = (time.time() - data["ts"]) / 86400
        if age_days > _PREV_SESSION_MAX_AGE_DAYS:
            return None
        delta = current_count - int(data["count"])
        return delta if delta > 0 else None
    except Exception:
        return None


def _git_commits_since(db_path: Path) -> list[str]:
    """Return one-line git log entries since the previous session. Silent on failure."""
    import subprocess
    from datetime import datetime
    prev_file = db_path / "prev_session.json"
    try:
        data = json.loads(prev_file.read_text(encoding="utf-8"))
        age_days = (time.time() - data["ts"]) / 86400
        if age_days > _PREV_SESSION_MAX_AGE_DAYS:
            return []
        since = datetime.fromtimestamp(data["ts"]).strftime("%Y-%m-%dT%H:%M:%S")
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={since}", f"-{_GIT_COMMITS_MAX}"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _write_prev_session(db_path: Path, current_count: int) -> None:
    prev_file = db_path / "prev_session.json"
    try:
        prev_file.write_text(
            json.dumps({"ts": time.time(), "count": current_count}),
            encoding="utf-8",
        )
    except Exception:
        pass


def _focus_text(get_memory, collection: str) -> str | None:
    try:
        entries = get_memory.execute(collection, [FOCUS_ID])
        return entries[0].text if entries and entries[0].text else None
    except Exception:
        return None


def _boosted_entries(repo, collection: str, exclude_ids: set[str], max_count: int = _AVAILABLE_MAX) -> list:
    """Return entries with an explicit /reflect boost, sorted by boost_count desc (ties by id)."""
    try:
        all_entries = repo.get_all(collection)
        candidates = []
        for entry in all_entries:
            if entry.id in exclude_ids:
                continue
            boost_count = int(entry.metadata.get("boost_count", 0))
            if boost_count >= _AVAILABLE_MIN_BOOSTS:
                candidates.append((boost_count, entry))
        candidates.sort(key=lambda x: (-x[0], x[1].id))
        return [entry for _, entry in candidates[:max_count]]
    except Exception:
        return []



def _expired_entries(repo, collection: str, now_ts: float) -> list:
    """Return entries with expires_at in the past, sorted oldest-first."""
    try:
        result = []
        for entry in repo.get_all(collection):
            raw = entry.metadata.get("expires_at")
            if raw is None:
                continue
            try:
                exp = float(raw)
            except (ValueError, TypeError):
                continue
            if exp < now_ts:
                result.append((exp, entry))
        result.sort(key=lambda x: x[0])
        return [entry for _, entry in result]
    except Exception:
        return []


def _experience_block(repo, ctx) -> str | None:
    """The experience index for this session's scope plus global, or None when empty."""
    if ExperienceIndexUseCase is None:
        return None
    collections = [ctx.collection, GLOBAL_COLLECTION] if ctx.has_claude_md else [GLOBAL_COLLECTION]
    try:
        lines = ExperienceIndexUseCase(repo).execute(collections)
    except Exception:
        return None
    if not lines:
        return None
    return (
        "[experience index]\n"
        "If the situation you are in matches a line, fetch the entry before acting: "
        f'mem_get(ids=[...], collection="{collections[0]}") (collection shown in brackets when different).\n'
        + lines
    )


def main():
    try:
        stdin_json: dict = json.load(sys.stdin)
    except Exception:
        stdin_json = {}

    if (detect_for_session_start is None or write_to_env_file is None
            or ChromaMemoryRepository is None or GetMemoryUseCase is None
            or ListCollectionsUseCase is None or title_of is None
            or detect_repo_context is None or record_injection is None):
        return

    agent_type: str | None = None
    try:
        agent_ctx = detect_for_session_start(stdin_json)
        agent_type = agent_ctx.agent_type
        write_to_env_file(agent_ctx)
        if not agent_ctx.should_inject:
            return
    except Exception:
        pass

    if not DB_PATH.exists():
        return

    try:
        _SESSION_START_FILE.write_text(str(time.time()))
    except Exception:
        pass

    settings: dict = {}
    try:
        settings = _load_settings(_CONFIG_PATH)
    except Exception:
        pass
    verbose = bool(settings.get(_SETTING_VERBOSE, False))
    with_index = bool(settings.get(_SETTING_INDEX, True))

    try:
        ctx = detect_repo_context()

        parts = []

        # Minimal, always-on routing info: which collection this session writes to.
        # No memory content is pushed here — the agent pulls content itself via mem_query.
        expert_collection: str | None = f"subagent.{agent_type}" if agent_type else None
        if expert_collection:
            parts.append(
                f'Expert collection: "{expert_collection}". '
                f'Store cross-project learnings there with collection="{expert_collection}".'
            )
        if ctx.has_claude_md:
            parts.append(
                f'Active collection: "{ctx.collection}". '
                f'Pass collection="{ctx.collection}" to mem_add and mem_query in this session.'
            )

        # The default path used to touch no storage at all. Build the repo only when the index or
        # verbose mode reads it, and never let a failing build swallow the routing line.
        repo = None
        if with_index or verbose:
            try:
                repo = ChromaMemoryRepository(DB_PATH)
            except Exception:
                repo = None
        index_block = _experience_block(repo, ctx) if with_index and repo is not None else None

        if not verbose or repo is None:
            if not parts and not index_block:
                return
            body = "\n".join(parts)
            if index_block:
                body = f"{body}\n\n{index_block}" if body else index_block
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "[ai-mem]\n" + body,
                }
            }
            print(json.dumps(output))
            return

        get_memory = GetMemoryUseCase(repo)

        collections = ListCollectionsUseCase(repo).execute()
        current_count = sum(col_info.count for col_info in collections)

        # Suppress the lookup only for the genuinely unscoped fallback (no CLAUDE.md
        # anywhere). When CLAUDE.md lives at the workspace root itself, ctx.collection
        # is still WORKSPACE_COLLECTION but has_claude_md is True — that's a real scope
        # with its own current_focus, and comparing against WORKSPACE_COLLECTION alone
        # produced a false "No focus entry found" warning even when one existed.
        repo_focus = _focus_text(get_memory, ctx.collection) if ctx.has_claude_md else None
        global_focus = _focus_text(get_memory, GLOBAL_COLLECTION)

        expert_focus: str | None = None
        expert_entries: list = []
        if agent_type:
            expert_focus = _focus_text(get_memory, expert_collection)
            _query = repo_focus or f"{ctx.collection} patterns and best practices"
            try:
                _results = repo.query(expert_collection, _query, n_results=3, max_age_days=None)
                expert_entries = [result for result in _results if result.id != FOCUS_ID][:2]
            except Exception:
                pass

        try:
            record_injection(_STATS_PATH, GLOBAL_COLLECTION, injected=global_focus is not None)
        except Exception:
            pass

        if repo_focus:
            # scope_name is None when CLAUDE.md sits at the workspace root itself
            # (collection falls back to WORKSPACE_COLLECTION); fall back to the
            # collection name so the label reads "[workspace focus]" instead of "[None focus]".
            scope_label = ctx.scope_name or ctx.collection
            parts.append(f"[{scope_label} focus]\n{_truncate(repo_focus, _FOCUS_PREVIEW_CHARS)}")
        if global_focus:
            parts.append(f"[global focus]\n{_truncate(global_focus, _FOCUS_PREVIEW_CHARS)}")
        if expert_focus or expert_entries:
            block = f"[{agent_type} expertise]"
            if expert_focus:
                block += f"\n{_truncate(expert_focus, _FOCUS_PREVIEW_CHARS)}"
            if expert_entries:
                block += "\nRelevant past learnings:\n" + "\n".join(
                    f"- {_truncate(entry.text, 200)}" for entry in expert_entries
                )
            parts.append(block)
        _avail_exclude = {FOCUS_ID}
        if ctx.has_claude_md:
            _avail_entries = _boosted_entries(repo, ctx.collection, _avail_exclude)
            if _avail_entries:
                parts.append(
                    "[available]\n"
                    + "\n".join(f"- {entry.id}: {title_of(entry.text)}" for entry in _avail_entries)
                    + f"\n(mem_get(ids=[...], collection=\"{ctx.collection}\") for full text)"
                )
        # Unconditional: global applies everywhere, regardless of repo/CLAUDE.md context.
        # Separate, smaller cap so a full repo-scoped pool never crowds out global entries
        # (or vice versa) -- same fixed-cap-not-dump discipline as every other injection point.
        _avail_global_entries = _boosted_entries(repo, GLOBAL_COLLECTION, _avail_exclude, max_count=_AVAILABLE_GLOBAL_MAX)
        if _avail_global_entries:
            parts.append(
                "[available: global]\n"
                + "\n".join(f"- {entry.id}: {title_of(entry.text)}" for entry in _avail_global_entries)
                + '\n(mem_get(ids=[...], collection="global") for full text)'
            )
        _now_ts = time.time()
        _expired: list = []
        if ctx.has_claude_md:
            _expired.extend(_expired_entries(repo, ctx.collection, _now_ts))
        _expired.extend(_expired_entries(repo, GLOBAL_COLLECTION, _now_ts))
        if _expired:
            from datetime import datetime
            _exp_lines = []
            for entry in _expired[:_EXPIRED_MAX]:
                exp_ts = float(entry.metadata.get("expires_at", 0))
                exp_date = datetime.fromtimestamp(exp_ts).strftime("%Y-%m-%d")
                preview = _truncate(entry.text, _EXPIRED_PREVIEW_CHARS)
                _exp_lines.append(f"⏰ {entry.id}: \"{preview}\" (expired {exp_date})")
            parts.append("[ai-mem expired]\n" + "\n".join(_exp_lines))

        if index_block:
            parts.append(index_block)

        if ctx.has_claude_md and not repo_focus:
            parts.append("No focus entry found. Add one via mem_add with id=\"current_focus\".")

        delta = _session_delta(DB_PATH, current_count)
        if delta is not None:
            label = "entry" if delta == 1 else "entries"
            parts.append(f"Since last session: {delta} new {label} added")

        git_commits = _git_commits_since(DB_PATH)
        if git_commits:
            parts.append("Git commits since last session:\n" + "\n".join(f"  {commit}" for commit in git_commits))

        _write_prev_session(DB_PATH, current_count)

        if not parts:
            return

        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "[ai-mem]\n" + "\n\n".join(parts),
            }
        }
        print(json.dumps(output))
    except Exception:
        pass


if __name__ == "__main__":
    main()
