# CLAUDE.md

Agent-facing supplement to README.md. Dev commands and critical contributor gotchas.

## Dev Commands

```bash
pip install -e .            # editable install (no ML, no BM25)
pip install -e ".[hybrid]"  # with BM25 hybrid search
pip install -e ".[config]"  # with pyyaml for agents.yaml support
python3 -m ai_mem.server    # run MCP server directly
python3 install.py          # register with Claude Code / Gemini CLI / Cursor
python3 uninstall.py        # remove all integration artifacts (preserves data)
python3 -m ai_mem.hook          # run SessionStart hook manually
python3 -m ai_mem.posttool_hook # run PostToolUse hook manually (pipe JSON payload on stdin)
python -m pytest tests/ -v  # run tests
mem-dream --dry-run         # preview entries without API calls
mem-dream --mode hier       # consolidate all collections (hier = default)
mem-dream --expert          # consolidate all subagent.* collections with expert focus hint
```

## Automation Subsystems

- `session_stats.py` — rolling per-scope injection tracking (20-entry window). `record_injection()` is called from `hook.py` (SessionStart). `injection_rate()` has no production caller besides its own test; whether to delete it is an open decision.
- `memory_index.py` — MEMORY.md auto-demotion (180→160 line threshold) — **built but not yet deployed, no trigger wired**

## Decision Records

`domain`/`pattern`/`anti-pattern`-Wissen ist git-nativ unter `docs/decisions/` (eine
Markdown-Datei pro Entscheidung, Dateiname = ai-mem-Entry-ID) — direkt durchsuchbar mit
grep/ls/Read, ohne ai-mem-Tools. ChromaDB ist ein lokal regenerierbarer Semantik-Index
darüber (`mem-adr-sync import` baut ihn aus den Dateien neu auf), nicht die Wahrheitsquelle.

**Offen, durch diese Migration NICHT gelöst:** das generelle mem_query-Retrieval-Trigger-
Problem (`eval_pull_gap_test_2026_09_20`, Collection `repo.ai-mem`) — ein Agent, der eine
Frage hat, ruft mem_query in den meisten Fällen nicht von sich aus auf. Dieser Abschnitt
macht `docs/decisions/` nur über den Kanal auffindbar, der im Gap-Test nachweislich
funktionierte (CLAUDE.md-Verweis + Repo-Grep), löst aber nicht das Trigger-Problem für
ai-mems eigene Query-Tools.

`docs/decisions/INDEX.md` listet alle Entscheidungen kompakt (id + Titel + Status) —
bei vielen Dateien zuerst diese eine Datei lesen statt einzeln zu greppen;
`mem-adr-sync reindex`/`export` hält sie aktuell.

## Critical Invariants

Things that will bite you in the first hour. Current-state facts only.

- `get_by_ids(collection, ids)` silently skips missing IDs — no error, no placeholder; the returned list only contains found entries.
- Tests that call `upsert` directly must include non-empty metadata (ChromaDB rejects empty dicts). Use `AddMemoryUseCase` in tests — it always injects timestamps.
- `posttool_hook.py` imports `GLOBAL_COLLECTION` and `detect_repo_context` at **module level** (not lazily inside `main()`) so tests can patch them via `patch.object`. Check test-side `patch.object` targets before removing an import that looks dead in source — a test may still patch it by name.
- `mem_delete` with no `ids` drops the **entire collection**; repo signals this by returning `-1`.
- `QueryMemoryUseCase` takes only `(repo, track_access)` — no ranker, no build_features.
- Cosine similarity from ChromaDB distance: `cos_sim = 1 - dist/2` (collections use `l2`/squared-L2 space, not cosine space — verified via `col.configuration_json`). The older `1 - dist` formula was wrong.
- `_hook_deps.py` exposes `_build_query_uc(db_path, with_bm25)` — the single assembly point for hooks. `posttool_hook` passes `with_bm25=False`.
- The ML ranker (`TorchMicroRanker`, `RankerRegistry`) was removed in 2026-06. No `[ml]` extra or `torch` dependency remains.
- Never edit `~/.claude/commands/*.md` directly to change a skill/command — those are the *installed* copies, not source. Edit the actual source (e.g. `skills/examples/reflect.md`), then re-run `install.py` (or the relevant sync step) to update the deployed copy; a direct edit silently drifts from source and gets overwritten on the next install.
- `confidence` and `access_count` are no longer written or read (dropped 2026-09-26 for evidence edges — `confirms`/`contradicts`/`supersedes`). Old values stay in stored metadata untouched; never migrate them away. `mem_boost` only records a `/reflect` citation (`boost_count` + optional `cue`); a passed `delta` is ignored.
- `[available]` gate: `boost_count ≥ 1` only, scanned against both the repo collection and a separately (smaller) capped `GLOBAL_COLLECTION`. Entries without an explicit `/reflect` boost never qualify, regardless of age. The block lists id + title only.
- `last_accessed_at` means deliberate use (an explicit `min_score_for_tracking` query, a `mem_get` by id, or a `mem_boost`) — not passive query surfacing; a plain `mem_query` with no threshold tracks nothing.
- `mem_move` deliberately bypasses `AddMemoryUseCase` (whose metadata-preserving merge only looks within the collection it's writing to, which would wrongly reset `boost_count`/`cue`/`created_at` on a cross-collection move) — reads via `get_by_ids`, writes via `upsert`, deletes the confirmed subset from source. An id that already exists at the target with different text is skipped as a `MoveConflict`, not overwritten. `from_collection == to_collection` raises `ValueError`. Known v1 limitation: edges only reference `target_id`, no collection field — a moved entry's old incoming edges go dangling.
- `detect_repo_context()` checks `AI_MEM_WORKSPACE_ROOT` before the git-based fallback, deriving collection names from the CLAUDE.md path relative to that root instead of `git remote`. Hook subprocesses don't inherit the MCP server's own `env` block, so `install.py` prefixes hook commands with `AI_MEM_WORKSPACE_ROOT=<path>` directly.
- Only `SessionStart` and `PostToolUse` hooks are registered. The `PreToolUse` and `UserPromptSubmit` push hooks were retired (per-edit and per-message injection cost more context than it was worth). `install.py` no longer registers either; both self-heal off existing installations on re-run via `_remove_hook_command`. Module files and tests for both still exist, just unwired.
- `mem_dream`'s `claude` CLI subprocess call (`dream_memory.py::_call()`) uses bare model aliases (`"sonnet"`, `"haiku"`), not versioned tags — a versioned tag is a bitrot risk since the CLI can stop resolving it whenever Anthropic retires it. On failure it raises with the CLI's actual `stderr`/`stdout` included, not just a bare exit code.
- Daemon (`daemon.py`) is thread-per-connection with a locked `record_access()` write path; `ChromaMemoryRepository` caches embeddings per-text with per-key locking.
- `injection_log.py` has had no live writer since 2026-09-13, when `userprompt_hook.py` — `record_pushed`'s only production caller — was unwired from Claude Code's hook registration (the module and call site still exist, per the hook-retirement bullet above; `install.py` just stopped registering it). `mem-dream`'s pull-through report (`dream_memory.py`, cross-referencing the log against `last_accessed_at`) still runs, but only ever covers the pushes logged before the log went frozen.
- `MarkdownAdrRepository` additionally persists `domain`/`pattern`/`anti-pattern` entries as Markdown under `docs/decisions/` (or `$AI_MEM_ADR_DIR`); `boost_count`/`last_accessed_at`/`cue` (and legacy `confidence`/`access_count`) are never written to the file — `mem_boost` never produces a file diff. Both `server.py` and `dream_cli.py`'s `_build_repo()` wire it in identically (not optional): `mem-dream --auto_delete/--auto_link/--auto_supersede` mutate the same repository stack and would otherwise orphan or silently desync a `.md` file. `AI_MEM_ADR_DISABLED=1` skips the Markdown layer entirely as a rollback escape hatch. Re-typing an entry away from an ADR type deletes its file; an ADR-type id that isn't a safe filename (`/`, `..`, `INDEX`, `README`) makes `upsert` raise before Chroma is written. `tests/conftest.py` sets `AI_MEM_PATH` to a temp dir and `AI_MEM_ADR_DISABLED=1` for the whole suite — ADR tests build `MarkdownAdrRepository` directly.
