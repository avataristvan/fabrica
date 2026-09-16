# Automation Pipeline

ai-mem used to run a threshold-driven pipeline that decided *for* the agent when to seed,
inject, and demote memory — no manual judgment involved. That pipeline is retired. The
current design is pull-based: an agent queries a collection deliberately (`mem_query`,
`mem_get`) when it wants context, instead of receiving it automatically. This page
documents what remains, what was removed, and why.

## What's still automatic

### MEMORY.md structure (`memory_index.py`)

Auto-demotion logic — moving old entries out of `MEMORY.md` into ai-mem once the file
crosses a line-count threshold — is implemented but **has no trigger wired in**. No hook
calls it. It's dead code pending a decision on whether it's worth reviving now that the
push-based hooks it was designed to complement are gone.

```python
DEMOTION_THRESHOLD = 180  # demote when MEMORY.md reaches this many lines
_TARGET_LINES = 160       # bring index down to this after demotion
_TYPE_PRIORITY = {"project": 0, "reference": 1, "user": 2, "feedback": 3}
```

### Session injection stats (`session_stats.py`)

Tracks whether SessionStart successfully found `current_focus`, per scope, in a
20-session rolling window. `record_injection()` is still called from `hook.py` when
`session_start_verbose` is on (see `docs/hooks.md`). `injection_rate()` itself has no
production caller anymore — its one consumer, the repo seeder (below), was removed.
Kept as-is rather than deleted; a call it's worth reviving if a future gate needs it.

## What was removed, and why

### Repo Seeder (`repo_seeder.py`)

Used to auto-populate a new `repo.*` collection from CLAUDE.md's H2 sections once
`injection_rate("global") >= 0.60`. Removed in favor of **agent-driven exploration**:
run `/mem-init` in a project to seed its collection — the agent reads the codebase and
writes what actually matters, instead of a mechanical H2-section split gated on an
unrelated global stat. The module is gone; `docs/collections.md` still describes the
old CLAUDE.md-splitting behavior in one place and needs the same update.

### UserPromptSubmit Auto-Injection (`userprompt_hook.py`)

Used to query global + repo collections against every incoming prompt (once a ranker
confidence gate passed) and inject the top-3 results. Retired 2026-09-13: it fired on
every single message rather than once per session, so token cost scaled with
conversation length, not with actual relevance. `install.py` no longer registers the
hook; re-running it on an existing install self-heals by removing the stale entry. Full
rationale: `<memory-entry>` in ai-mem's own memory.

### PreToolUse Auto-Injection (`pretool_hook.py`)

Same shape, different trigger: injected top-2 results before every Write/Edit. Retired
2026-09-12 for the same reason — automatic push that scaled with edit count instead of
relevance. Full rationale: `<memory-entry>`.

## The current loop

```
/mem-init          →  agent explores the repo, seeds the collection deliberately
SessionStart        →  announces the active collection (routing only, not content)
[agent works]        →  pulls context explicitly via mem_query / mem_get when it wants it
/reflect             →  writes back learnings, confirms or decays what was pulled
```

See `docs/skill-agent-integration.md` for how to wire an agent or skill into this loop,
and `agents.yaml.example` for the `session_start_verbose` setting that restores the old
SessionStart push for workflows that still want it.
