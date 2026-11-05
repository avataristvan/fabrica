# CLAUDE.md

Agent-facing supplement to README.md: what is true now and bites in the first hour.
History and rationale live in `docs/records/` (start with `INDEX.md`, or ask the librarian agent).

## Map

- `ai_mem/domain/` contracts (`MemoryRepository`) → `ai_mem/application/` one use case per file → `ai_mem/infrastructure/` storage. `mem_cli.py` (`mem`), `hook.py` (SessionStart; also `Area:` line and `mem doctor` pointer), `hooks/{retro_check,lint_after_write,reflect_reminder,focus_gate}.py` (enforcing SubagentStop/PostToolUse/Stop hooks, `docs/reference/hooks.md`), `dream_cli.py` are adapters.
- Storage is the record files only: `FileMemoryRepository`. No database is opened, and there are no runtime dependencies (`dependencies = []`; extra `dev` = pytest). The MCP server, daemon and Chroma/BM25 backend are gone; the last commit with them is the tag `v0-last-mcp` (`docs/reference/chroma_rollback_backend.md`).
- Areas: `infrastructure/areas.py` resolves the nearest ancestor with `docs/records/`; edges are relative links in a record's closing `## Edges` section, also across areas; the CLI names a record in another area `<relative-area-path>:<name>` (`docs/reference/record-format.md`). `FileMemoryRepository(records_dir_for)` takes the resolver `area_records_dir`; an area key is the area root as an absolute path. `areas.py` also maps a linked git worktree to its main checkout (`_to_main_checkout`).
- Sources: `docs/sources/<slug>.md` is frozen evidence (frontmatter `type/date/origin/status`, format in `docs/reference/record-format.md` "Sources"); never edit a source body. `mem doctor` (Sources section, `ai_mem/doctor_sources.py`) lists sources nothing points to.
- Docs follow Diátaxis: `docs/tutorial/`, `docs/how-to/`, `docs/reference/` (`cli.md`, `record-format.md`, `hooks.md`, `architecture.md`), `docs/explanation/`; `README.md` is concept-first and must link every current doc. `docs/sources/` is evidence, not documentation.
- Fabrica, the method ai-mem implements, lives in `docs/fabrica/` (`core.md`, `patterns/` with one file per pattern, its status and evidence); its earlier drafts (`epistemology_framework.md`, the manifesto v0.1) are sources.
- `skills/handoff-protocol/SKILL.md` is the boundary contract (librarian call, `records_consulted`/`record_candidates`, reviewer template); `docs/how-to/wire-skills-and-agents.md` is the how-to for wiring skills and agents.
- The repo is the Claude Code plugin (`.claude-plugin/plugin.json`, local marketplace `marketplace.json`, name `fabrica@fabrica`): `agents/{librarian,archivist,anchor-lint}.md`, `skills/{reflect,setup,handoff-protocol,tidy}/`, `reference/navigating_records.md` and `reference/documentation_map.md` (what goes where in an area: experiments, plans, handoffs, raw data; named as `${CLAUDE_PLUGIN_ROOT}/reference/...` in the agent texts), `hooks/hooks.json` (every hook via `hooks/run.py <module>`), `bin/{mem,mem-dream}` (sh shims, `PYTHONPATH` = plugin root, system `python3`). Plugin agents are `fabrica:<agent>`, skills `/fabrica:<skill>`. `/fabrica:setup` (`skills/setup/SKILL.md`) proposes hook-ins, CLAUDE.md lines, the docs layout of the documentation map, and the update of a project set up earlier (format migration `mem lint --fix` and text diffs, each on approval; state read from `mem doctor`, no version stamp), writes no records. `/fabrica:tidy` places an area's handoffs and loose docs by the documentation map (proposal per file, applies on approval, record candidates to the archivist, never writes FOCUS.md). There is no installer: the plugin needs no `pip install`. The legacy upgrade path (`install.py`, `uninstall.py`, `UPGRADING.md`, the records_v1 migration, the upgrade guard) is gone; the last version with it is the tag `v1-last-upgrade-path`, the MCP version is `v0-last-mcp`.

## Dev Commands

```bash
pip install -e ".[dev]"          # editable install (the plugin itself needs no pip install)
python -m pytest tests/ -q       # run tests
python3 -m ai_mem.hook           # SessionStart hook by hand (pipe a JSON payload on stdin)
mem add|link|unlink|delete|context ...   # write record files in the nearest area (docs/records/)
mem-dream --area <path> --dry-run   # preview what mem-dream would read, no API calls
python3 scripts/eval_setup/run.py --out <scratch> --model sonnet --repeats 3   # /fabrica:setup exit check (fresh claude -p, real HOME, project settings only)
```

## Records

- One Markdown file per entry: `docs/records/<topic>/<kind>/<name>.md` (the file name is the record's name; there is no `id:` line), kind `decisions/` (domain, pattern, anti-pattern), `learnings/`, `user/`. `current_focus` → `docs/records/FOCUS.md` (plain text, overwritten); `BACKLOG.md` next to it (plain text, ordered, hand-written). There is no `todo` type (`mem add` and `mem lint` reject it). `reference` → `docs/reference/<id>.md`. Format: `docs/reference/record-format.md`.
- `user` records are a role's yardstick, pulled on a fixed trigger (the reviewer template in `skills/handoff-protocol/SKILL.md`); preferences that must act in every session belong in CLAUDE.md instead.

## Gotchas

- `mem add` rejects types without a file (`feedback`, `project`, `fact`, `dilemma`, untyped). The id `current_focus` takes any type.
- Delete without `ids` is refused (`mem delete`). `record_access`, `delete_expired`, `delete_stale` are no-ops; `boost_count`, `last_accessed_at`, `expires_at` are never stored. `FileMemoryRepository.query` is keyword overlap, not semantic.
- `cue` is the last frontmatter line; `mem add --cue` rewrites the file, INDEX.md only changes when a row changes.
- `get_by_ids` silently skips missing ids.
- Inside the use cases an edge target is still a name (`<name>` or `<rel>:<name>`); only `adr_markdown.py` + `record_links.py` turn it into a relative link and back, by path alone. A link is rendered against where its target lies at write time: `mem move` rewrites what it wrote at the end, a retype/new topic relinks referrers in the same area, everything else heals with `mem lint --fix` (`link-stale`). Older records (`id:`/`edges:`/`superseded_by:` in the frontmatter) are still read; `mem lint --fix` migrates them (`legacy-refs`) and links bare names in the text (`bare-id`).
- `mem review [--since REF]` (default `@{upstream}`) lists the records a push would publish and flags machine paths, names from `$AI_MEM_PATH/private_names`, and cited commits that are off the branch or that a squash would orphan; `/fabrica:reflect` runs by itself and leaves the review to that moment.
- Focus gate (`hooks/focus_gate.py`): a Write/Edit of an area's `docs/records/FOCUS.md` is denied unless `/fabrica:reflect` ran in this session; the marker closes at the Stop after FOCUS.md was written. Writes through Bash (`mem add --id current_focus`) bypass it.
- SessionStart pushes no content: the `Area:` line, one `Records:` pointer and the doctor pointer. Besides it only the enforcing hooks below are registered.
- The `Area:` line is found by walking up from the cwd, with no environment variable. Subagents get no SessionStart output; they ask the librarian or run `mem context`.
- `mem move` (area to area) bypasses `AddMemoryUseCase` (its merge would reset metadata); a differing id at the target is a conflict, and incoming edges to a moved record go dangling.
- `mem move-area` renames the folder first, then rewrites references at the new paths (a failed rename writes nothing); it refuses areas without git unless `--include-unversioned`, and only reports machine state (worktrees, editable install, `~/.claude`).
- `mem-dream --area` calls the `claude` CLI with bare model aliases (`sonnet`, `haiku`), never versioned tags, and surfaces the CLI's stderr on failure.
- Enforcing hooks (`ai_mem/hooks/`) are registered by the plugin's `hooks/hooks.json`; they check or remind, never raise, never write stderr, and `retro_check` blocks at most once (`stop_hook_active`). Plugin variables: `CLAUDE_PLUGIN_ROOT` reaches hooks (expanded in `hooks.json`, exported to hook processes) and agent/skill bodies, but NOT the Bash tool; `CLAUDE_PLUGIN_OPTION_<KEY>` reaches hooks only once a value is set (no default is exported), so every option has a file/default fallback; `${user_config.KEY}` is not substituted in agent bodies. A plugin skill's `model:` frontmatter is honored (the turn switches model); `skills/setup` sets none on purpose. `bin/` is on a subagent's Bash PATH. SubagentStop `agent_type` for a plugin agent is `fabrica:<agent>`.
- Who writes records: the archivist (via `/reflect`) and the user; every other skill, agent or command only asks the librarian and delivers `record_candidates` in its `[retro]`. The contract is `skills/handoff-protocol/SKILL.md`; each team file carries the line "At this boundary follow the Fabrica handoff protocol (skill `fabrica:handoff-protocol`)." (`mem doctor` Wiring lists every team without it; no exemption list — external agents are never edited, `domain_agents_learn_environment_never_edit_external_2026_10_11`).
- The dev-team (`dev-team:dev-team`, `dev-team:chunk-plan`, `dev-team:review`, `dev-team:the-coder`) lives in its own plugin repo `ai-architecture/dev-team` and is edited there; ai-mem's own skills and agents only in this repo.

## Known noise

- Agent definitions and hooks keep the code they started with — changes show up only after a Claude Code restart. Test changes with the modules or a fresh process.
- `tests/conftest.py` sets `AI_MEM_PATH` to a temp dir and unsets `AI_MEM_WORKSPACE_ROOT`; `tmp_repo` is an in-memory repository.
- A subprocess test that must see the worktree's code uses `python -I -S` with `sys.path.insert(0, root)`: under a pyenv editable install, plain `-I` still resolves `ai_mem` to the main checkout. `tests/test_stdlib_only.py` imports every `ai_mem` module that way, which is the STDLIB CHECK for `dependencies = []`.
