# Hook System

ai-mem registers two Claude Code lifecycle hooks. Both are silent on failure (wrapped in try/except) so they never interrupt the session.

## SessionStart (`hook.py`)

Fires at the start of every Claude Code session.

**Default (pull-based):**
1. Detects the repo context (git root + CLAUDE.md presence → collection name)
2. Prints `hookSpecificOutput` JSON naming the active collection — and, inside a subagent whose type is registered for injection (see `agents.yaml`'s `inject_agents`), its own `subagent.<name>` expert collection
3. No memory content is pushed. The agent decides when to pull — `mem_query`, `mem_get`, or the `[available]`-style listing a skill/agent prompt asks for explicitly.

**Output format (default):**
```
[ai-mem]
Expert collection: "subagent.<name>". Store cross-project learnings there with collection="subagent.<name>".
Active collection: "repo.<name>". Pass collection="repo.<name>" to mem_add and mem_query in this session.
```
The expert-collection line only appears for a subagent whose type is registered to receive it. If there's no CLAUDE.md and no such subagent, the hook prints nothing.

**Opt-in verbose mode:** set `session_start_verbose: true` under `settings:` in `~/.config/ai-mem/agents.yaml` to restore the pre-2026-09-16 push: `current_focus` text (repo + global + expert), the `[available]` high-confidence listing, expired-entry warnings, the entry-count delta since the last session, and git commits since the last session. See `agents.yaml.example`.

If no parts are generated, the hook exits silently (no output).

## PostToolUse (`posttool_hook.py`)

Fires after each Write or Edit tool call. Records a passive access signal — no output to Claude.

**What it does:**
1. Extracts `file_path` from the tool input
2. Queries global + repo collections with `"<filename> <path>"` as the query
3. `QueryMemoryUseCase` internally calls `TrackAccessUseCase`, setting `last_accessed_at` and incrementing `access_count` on matches above `min_label_score`

**Why it matters:** Every file edit is implicit evidence that the matched memory entries were relevant, feeding the confidence lifecycle (see README's Confidence Lifecycle section) without any manual step.

Does not wrap the repo with BM25 — the hook only needs semantic proximity, not high-precision ranking.

---

## Retired hooks

Two more hooks existed at various points and were removed because they pushed content rather than letting agents pull it:

- **`UserPromptSubmit` (`userprompt_hook.py`)** — retired 2026-09-13. Ran a semantic query against every incoming prompt (up to 4 parallel lookups) and injected top-3 results once a ranker-confidence gate passed. Fired on every message, not once per session, so the token cost scaled with conversation length rather than with actual relevance.
- **`PreToolUse` (`pretool_hook.py`)** — retired 2026-09-12. Injected top-2 results before every Write/Edit. Same problem: automatic push scaled with edit count.

Both modules still exist in the repo (unwired) so pre-existing installations uninstall cleanly; `install.py` no longer registers either, and self-heals existing installs by removing their hook entries on re-run.

A `Stop` hook (`stop_hook.py`, MEMORY.md auto-demotion + a "update current_focus" reminder) is referenced in older design notes but was never wired into `install.py` and the module doesn't exist in this repo. `memory_index.py`'s auto-demotion logic is built but has no trigger.

---

## Hook Registration

Hooks are registered in `~/.claude/settings.json` by `install.py`. Timeouts: SessionStart 10s, PostToolUse 10s.

```json
{
  "hooks": {
    "SessionStart": [{"matcher": "", "hooks": [{"type": "command", "command": "python3 -m ai_mem.hook", "timeout": 10000}]}],
    "PostToolUse": [{"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "python3 -m ai_mem.posttool_hook", "timeout": 10000}]}]
  }
}
```
