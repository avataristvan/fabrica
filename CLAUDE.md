# CLAUDE.md

Agent-facing supplement to README.md: what is true now and bites in the first hour.
History and rationale live in `docs/records/` (start with `INDEX.md`, or ask the librarian agent).

## Map

- `ai_mem/domain/` contracts (`MemoryRepository`) → `ai_mem/application/` one use case per file → `ai_mem/infrastructure/` storage. `server.py` (MCP tools), `hook.py` (SessionStart), `dream_cli.py`, `adr_cli.py` (`mem-adr-sync`) are adapters.
- Storage is the record files only: `FileMemoryRepository`, chosen in `infrastructure/repository_factory.py`. No database is opened. `AI_MEM_BACKEND=chroma` is the rollback — its facts are in `docs/reference/chroma_rollback_backend.md`.
- Sources vs. deployed copies: `skills/examples/reflect.md` and `install.py`'s `_MEM_INIT_CONTENT` are installed to `~/.claude/commands/` (sync: `install.py --sync-commands`); `examples/agents/librarian.md` is symlinked to `~/.claude/agents/`.

## Dev Commands

```bash
pip install -e .                 # editable install
python -m pytest tests/ -q       # run tests
python3 -m ai_mem.hook           # SessionStart hook by hand (pipe a JSON payload on stdin)
python3 -m ai_mem.server         # MCP server by hand
mem-adr-sync reindex --collection <c>   # rebuild docs/records/INDEX.md
mem-adr-sync migrate             # records_v1 dry run, ChromaDB -> files (--apply writes; install.py offers it once)
mem-dream --dry-run              # preview what mem-dream would read, no API calls
python3 install.py               # interactive — the user runs it, not the agent
```

## Records

- One Markdown file per entry: `docs/records/<area>/<kind>/<id>.md`, kind `decisions/` (domain, pattern, anti-pattern), `learnings/`, `todos/`, `user/`. `current_focus` → `docs/records/FOCUS.md` (plain text, overwritten). `reference` → `docs/reference/<id>.md`. Format: `docs/adr-format.md`.
- `global`, `workspace`, `subagent.*` live in the records home `$AI_MEM_WORKSPACE_ROOT/ai-mem-records/<collection>/` (only if that directory exists).
- `user` records are a role's yardstick, pulled on a fixed trigger (the reviewer template in `dev-team.md`); preferences that must act in every session belong in CLAUDE.md instead.

## Gotchas

- `mem_add` rejects types without a file (`feedback`, `project`, `fact`, `dilemma`, untyped). The id `current_focus` takes any type.
- A collection can only be written when its directory resolves: mapping file `~/.local/share/ai-mem/adr_collection_roots.json` (the server records its cwd's collection at startup), cwd detection, or the records home.
- `mem_delete` without `ids` is refused. `record_access`, `delete_expired`, `delete_stale` are no-ops; `boost_count`, `last_accessed_at`, `expires_at` are never stored. `mem_query` is keyword overlap, not semantic.
- `cue` is the last frontmatter line; `mem_boost(cue=...)` rewrites the file, INDEX.md only changes when a row changes.
- `get_by_ids` silently skips missing ids.
- SessionStart pushes no content: routing line(s) plus one `Records:` pointer. Only that hook is registered; the PreToolUse/UserPromptSubmit/PostToolUse modules exist but are unwired.
- `detect_repo_context()` names collections from the CLAUDE.md path relative to `AI_MEM_WORKSPACE_ROOT`, before the git fallback; worktrees map to their main checkout. Hook subprocesses don't inherit the MCP server's env, so `install.py` prefixes the hook command with `AI_MEM_WORKSPACE_ROOT=`. Subagents get no SessionStart output — `mem_context(cwd)` tells them their collection.
- `mem_move` bypasses `AddMemoryUseCase` (its merge would reset metadata across collections); a differing id at the target is a `MoveConflict`, and incoming edges to a moved entry go dangling.
- `mem_dream` calls the `claude` CLI with bare model aliases (`sonnet`, `haiku`), never versioned tags, and surfaces the CLI's stderr on failure.
- Never edit `~/.claude/commands/*.md` copies that have a repo source — edit the source and sync. Global-only files (`chunk-plan.md`, `dev-team.md`) are edited in place.

## Known noise

- `tests/test_daemon.py` fails sporadically (ConnectionRefusedError); rerun it alone before suspecting a change.
- A running MCP server and agent definitions keep the code they started with — changes show up only after a Claude Code restart. Test changes with the modules or a fresh process, not through this session's `mem_*` tools.
- `tests/conftest.py` sets `AI_MEM_PATH` to a temp dir, `AI_MEM_ADR_DISABLED=1`, and unsets `AI_MEM_RECORDS_HOME`/`AI_MEM_WORKSPACE_ROOT`.
