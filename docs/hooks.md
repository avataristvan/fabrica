# Hook System

ai-mem registers two Claude Code lifecycle hooks. Both are silent on failure (wrapped in try/except) so they never interrupt the session.

## SessionStart (`hook.py`)

Fires at the start of every Claude Code session.

**Default (pull-based):**
1. Detects the repo context (git root + CLAUDE.md presence → collection name)
2. Prints `hookSpecificOutput` JSON naming the active collection — and, inside a subagent whose type is registered for injection (see `agents.yaml`'s `inject_agents`), its own `subagent.<name>` expert collection
3. If the repo has a `docs/records/` directory, adds one line pointing at it (FOCUS.md, INDEX.md) and at the librarian agent.
4. No memory content is pushed, and the default path never opens the database. The agent pulls on purpose: it reads the record files, or asks the librarian agent, which reads them — including each record's `cue:` line — by judgment.

**Output format (default):**
```
[ai-mem]
Expert collection: "subagent.<name>". Store cross-project learnings there with collection="subagent.<name>".
Active collection: "repo.<name>". Pass collection="repo.<name>" to mem_add and mem_query in this session.
Records: <repo>/docs/records (FOCUS.md = current focus, INDEX.md = catalogue of decisions, learnings, todos). Read them on demand; for "why is it like this / was this tried before?" ask the librarian agent.
```
The expert-collection line only appears for a subagent whose type is registered to receive it; the `FOCUS.md` mention only when that file exists. If there's no CLAUDE.md and no such subagent, the hook prints nothing.

**Experience index (retired 2026-10-04):** until then the default mode pushed up to 20 `situation -> entry` lines built from entry cues (~900 tokens per session). The cues now live in the record files' frontmatter and the librarian agent reads them on demand; `session_start_index` is gone.

**Opt-in verbose mode:** set `session_start_verbose: true` under `settings:` in `~/.config/ai-mem/agents.yaml` to restore the pre-2026-09-16 push: `current_focus` text (repo + global + expert), expired-entry warnings, the entry-count delta since the last session, and git commits since the last session. See `agents.yaml.example`.

If no parts are generated, the hook exits silently (no output).

## Retired hooks

Three more hooks existed at various points and were removed:

- **`UserPromptSubmit` (`userprompt_hook.py`)** — retired 2026-09-13. Ran a semantic query against every incoming prompt (up to 4 parallel lookups) and injected top-3 results once a ranker-confidence gate passed. Fired on every message, not once per session, so the token cost scaled with conversation length rather than with actual relevance.
- **`PreToolUse` (`pretool_hook.py`)** — retired 2026-09-12. Injected top-2 results before every Write/Edit. Same problem: automatic push scaled with edit count.
- **`PostToolUse` (`posttool_hook.py`)** — retired 2026-10-04. After every Write/Edit it queried memory with the edited file's path only to bump `last_accessed_at` on the matches. With record files as the store there is no access counter left to bump.

The modules still exist in the repo (unwired) so pre-existing installations uninstall cleanly; `install.py` no longer registers any of them, and self-heals existing installs by removing their hook entries on re-run.

A `Stop` hook (`stop_hook.py`, MEMORY.md auto-demotion + a "update current_focus" reminder) is referenced in older design notes but was never wired into `install.py` and the module doesn't exist in this repo. `memory_index.py`'s auto-demotion logic is built but has no trigger.

---

## Hook Registration

The one remaining hook is registered in `~/.claude/settings.json` by `install.py`. Timeout: 10s.

```json
{
  "hooks": {
    "SessionStart": [{"matcher": "", "hooks": [{"type": "command", "command": "python3 -m ai_mem.hook", "timeout": 10000}]}]
  }
}
```
