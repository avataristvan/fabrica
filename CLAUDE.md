# CLAUDE.md

Agent-facing supplement to README.md: what is true now and bites in the first hour.
History and rationale live in `docs/records/` (start with `INDEX.md`, or ask the librarian agent).

## Map

- `ai_mem/domain/` contracts (`MemoryRepository`) → `ai_mem/application/` one use case per file → `ai_mem/infrastructure/` storage. `server.py` (MCP tools), `hook.py` (SessionStart; also `Area:` line and `mem doctor` pointer), `hooks/{retro_check,lint_after_write,reflect_reminder}.py` (enforcing SubagentStop/PostToolUse/Stop hooks, `docs/reference/hooks.md`), `dream_cli.py`, `adr_cli.py` (`mem-adr-sync`) are adapters.
- Storage is the record files only: `FileMemoryRepository`, chosen in `infrastructure/repository_factory.py`. No database is opened. `AI_MEM_BACKEND=chroma` is the rollback (needs the `[chroma]` extra) — its facts are in `docs/reference/chroma_rollback_backend.md`.
- Areas: `infrastructure/areas.py` resolves the nearest ancestor with `docs/records/`; cross-area edges are `<relative-area-path>:<id>` (`docs/reference/record-format.md`). `FileMemoryRepository(records_dir_for=...)` is area mode; without it, collection mode (the MCP server) is unchanged.
- Sources: `docs/sources/<slug>.md` is frozen evidence (frontmatter `type/date/origin/status`, format in `docs/reference/record-format.md` "Sources"); never edit a source body. `mem doctor` (Sources section, `ai_mem/doctor_sources.py`) lists sources nothing points to and current docs that still describe a retired system.
- Docs follow Diátaxis: `docs/tutorial/`, `docs/how-to/`, `docs/reference/` (`cli.md`, `record-format.md`, `hooks.md`, `architecture.md`), `docs/explanation/`; `README.md` is concept-first and must link every current doc. `docs/sources/` is evidence, not documentation. A current doc may name a retired system (ChromaDB, MCP server, BM25, daemon, experience index) only with a top banner or `status: historical`; otherwise `mem doctor` flags it. `docs/epistemology-framework.md` is the one accepted hit (frozen text, untouched).
- `skills/handoff-protocol/SKILL.md` is the boundary contract (librarian call, `records_consulted`/`record_candidates`, reviewer template); `docs/how-to/wire-skills-and-agents.md` is the how-to for wiring skills and agents.
- The repo is the Claude Code plugin (`.claude-plugin/plugin.json`, local marketplace `marketplace.json`, name `ai-mem@ai-mem`): `agents/{librarian,archivist,anchor-lint}.md`, `skills/{reflect,setup,handoff-protocol}/`, `reference/navigating_records.md` (named as `${CLAUDE_PLUGIN_ROOT}/reference/...` in the agent texts), `hooks/hooks.json` (all four hooks via `hooks/run.py <module>`), `bin/{mem,mem-dream}` (sh shims, `PYTHONPATH` = plugin root, system `python3`). Plugin agents are `ai-mem:<agent>`, skills `/ai-mem:<skill>`. `/ai-mem:setup` (`skills/setup/SKILL.md`) proposes hook-ins and CLAUDE.md lines, applies on approval, writes no records. `install.py` deploys nothing into `~/.claude`; `install.py --plugin-switch` offers to remove what older versions put there (hooks, `reflect.md`/`mem-init.md` command copies, links).

## Dev Commands

```bash
pip install -e .                 # editable install
python -m pytest tests/ -q       # run tests
python3 -m ai_mem.hook           # SessionStart hook by hand (pipe a JSON payload on stdin)
python3 -m ai_mem.server         # MCP server by hand
mem-adr-sync reindex --collection <c>   # rebuild docs/records/INDEX.md
mem-adr-sync migrate             # records_v1 dry run, ChromaDB -> files (--apply writes; install.py offers it once)
mem add|link|delete|context ...   # write record files in the nearest area (docs/records/); exit 3 while a migration is pending
mem-dream --dry-run              # preview what mem-dream would read, no API calls
python3 scripts/eval_setup/run.py --out <scratch> --model sonnet --repeats 3   # /ai-mem:setup exit check (fresh claude -p, real HOME, project settings only)
python3 install.py               # interactive — the user runs it, not the agent
```

## Records

- One Markdown file per entry: `docs/records/<area>/<kind>/<id>.md`, kind `decisions/` (domain, pattern, anti-pattern), `learnings/`, `todos/`, `user/`. `current_focus` → `docs/records/FOCUS.md` (plain text, overwritten). `reference` → `docs/reference/<id>.md`. Format: `docs/reference/record-format.md`.
- `global`, `workspace`, `subagent.*` live in the records home `$AI_MEM_WORKSPACE_ROOT/ai-mem-records/<collection>/` (only if that directory exists).
- `user` records are a role's yardstick, pulled on a fixed trigger (the reviewer template in `skills/handoff-protocol/SKILL.md`); preferences that must act in every session belong in CLAUDE.md instead.

## Gotchas

- `mem add` (and the MCP add tool) rejects types without a file (`feedback`, `project`, `fact`, `dilemma`, untyped). The id `current_focus` takes any type.
- A collection can only be written when its directory resolves: mapping file `~/.local/share/ai-mem/adr_collection_roots.json` (the server records its cwd's collection at startup), cwd detection, or the records home.
- Delete without `ids` is refused (`mem delete` and the MCP tool). `record_access`, `delete_expired`, `delete_stale` are no-ops; `boost_count`, `last_accessed_at`, `expires_at` are never stored. `mem_query` is keyword overlap, not semantic.
- `cue` is the last frontmatter line; Boosting with a `cue` (MCP) rewrites the file, INDEX.md only changes when a row changes.
- `get_by_ids` silently skips missing ids.
- SessionStart pushes no content: routing line(s) plus one `Records:` pointer. Besides it only the enforcing hooks below are registered; the old PreToolUse/UserPromptSubmit/PostToolUse modules exist but are unwired.
- `detect_repo_context()` names collections from the CLAUDE.md path relative to `AI_MEM_WORKSPACE_ROOT`, before the git fallback; worktrees map to their main checkout. Hook subprocesses don't inherit the MCP server's env, and the plugin's hooks carry no `AI_MEM_WORKSPACE_ROOT=` prefix: the `Area:` line is found by walking up from the cwd, only the collection routing line still depends on the session's own env. Subagents get no SessionStart output — `mem_context(cwd)` tells them their collection.
- The MCP move tool bypasses `AddMemoryUseCase` (its merge would reset metadata across collections); a differing id at the target is a `MoveConflict`, and incoming edges to a moved entry go dangling.
- `migrate` and `reindex` need no chromadb: the store is read via `infrastructure/chroma_sqlite_reader.py`, opened read-only, never written. `migrate --apply` writes `.migrations/records_v1.done` only on a clean plan (else exit 1); while a `chroma.sqlite3` exists without it, SessionStart prints one guard line pointing to `UPGRADING.md`.
- `mem-dream` (and the MCP dream tool) calls the `claude` CLI with bare model aliases (`sonnet`, `haiku`), never versioned tags, and surfaces the CLI's stderr on failure.
- Enforcing hooks (`ai_mem/hooks/`) are registered by the plugin's `hooks/hooks.json`, not by `install.py` any more; they check or remind, never raise, never write stderr, and `retro_check` blocks at most once (`stop_hook_active`). Plugin variables: `CLAUDE_PLUGIN_ROOT` reaches hooks (expanded in `hooks.json`, exported to hook processes) and agent/skill bodies, but NOT the Bash tool; `CLAUDE_PLUGIN_OPTION_<KEY>` reaches hooks only once a value is set (no default is exported), so every option has a file/default fallback; `${user_config.KEY}` is not substituted in agent bodies. A plugin skill's `model:` frontmatter is honored (the turn switches model); `skills/setup` sets none on purpose. `bin/` is on a subagent's Bash PATH. SubagentStop `agent_type` for a plugin agent is `ai-mem:<agent>`. Run `install.py`/`uninstall.py` against a temp `HOME` in tests, never the real `~/.claude`.
- Who writes records: the archivist (via `/reflect`) and the user; every other skill, agent or command only asks the librarian and delivers `record_candidates` in its `[retro]`. The contract is `skills/handoff-protocol/SKILL.md`; each team file carries the line "At this boundary follow the ai-mem handoff protocol (skill `ai-mem:handoff-protocol`)." (`mem doctor` Wiring lists every team without it; no exemption list — external agents are never edited, `domain_agents_learn_environment_never_edit_external_2026_10_11`).
- Global-only files (`chunk-plan.md`, `dev-team.md`) are edited in place; ai-mem's own skills and agents only in this repo.

## Known noise

- `tests/test_daemon.py` fails sporadically (ConnectionRefusedError); rerun it alone before suspecting a change.
- A running MCP server and agent definitions keep the code they started with — changes show up only after a Claude Code restart. Test changes with the modules or a fresh process, not through this session's `mem_*` tools.
- `tests/conftest.py` sets `AI_MEM_PATH` to a temp dir, `AI_MEM_ADR_DISABLED=1`, and unsets `AI_MEM_RECORDS_HOME`/`AI_MEM_WORKSPACE_ROOT`.
