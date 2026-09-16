# CLAUDE.md

Agent-facing supplement to README.md. Dev commands and critical contributor gotchas.

## Dev Commands

```bash
pip install -e .            # editable install (no ML, no BM25)
pip install -e ".[hybrid]"  # with BM25 hybrid search
pip install -e ".[dream]"   # with Anthropic SDK for mem-dream
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

- `session_stats.py` — rolling per-scope injection tracking (20-entry window). `record_injection()` is still called from `hook.py` (SessionStart). `injection_rate()` is now dead code in production (no caller besides its own test) — its only consumer, `repo_seeder.py`, was removed in commit `1efe78a` ("replace file-based seeder with agent-driven mem-init exploration"), and `userprompt_hook.py`'s own `record_injection()` call site (2026-09-13 retirement) no longer executes either. Not removed as part of any of those changes — a deliberate decision on whether to delete it hasn't been made.
- `memory_index.py` — MEMORY.md auto-demotion (180→160 line threshold) — **built but not yet deployed, no trigger wired**

(This used to list `repo_seeder.py` and `userprompt_hook.py` as two more "threshold-driven subsystems" — both gone, see above and the PreToolUse/UserPromptSubmit retirement bullets below. Project seeding is `/mem-init`'s agent-driven exploration now, not an automatic hook.)

## Critical Invariants

Things that will bite you in the first hour. This list is current-state facts only — full incident history, measurements, and rejected alternatives for anything dated live in ai-mem's own memory (`repo.ai-mem` collection, query it or `mem_get` the ids below) rather than here, since CLAUDE.md has no cap and loads in full every session; ai-mem is the decision graph, this is just what's true right now.

- `get_by_ids(collection, ids)` silently skips missing IDs — no error, no placeholder; the returned list only contains found entries.
- Tests that call `upsert` directly must include non-empty metadata (ChromaDB rejects empty dicts). Use `AddMemoryUseCase` in tests — it always injects timestamps.
- `posttool_hook.py` imports `GLOBAL_COLLECTION` and `detect_repo_context` at **module level** (not lazily inside `main()`) so tests can patch them via `patch.object`. Check test-side `patch.object` targets before removing an import that looks dead in source — a test may still patch it by name.
- `mem_delete` with no `ids` drops the **entire collection**; repo signals this by returning `-1`.
- `QueryMemoryUseCase` takes only `(repo, track_access)` — no ranker, no build_features.
- Cosine similarity from ChromaDB distance: `cos_sim = 1 - dist/2` (collections use `l2`/squared-L2 space, not cosine space — verified via `col.configuration_json`). Full incident history (the old, wrong `1-dist` formula, compounded by BM25's since-fixed double min-max normalization): `<memory-entry>`, `<memory-entry>`.
- `_hook_deps.py` exposes `_build_query_uc(db_path, with_bm25)` — the single assembly point for hooks. `posttool_hook` passes `with_bm25=False`.
- The ML ranker (`TorchMicroRanker`, `RankerRegistry`) was removed in 2026-06. No `[ml]` extra or `torch` dependency remains.
- Never edit `~/.claude/commands/*.md` directly to change a skill/command — those are the *installed* copies, not source. Edit the actual source (e.g. `skills/examples/reflect.md`), then re-run `install.py` (or the relevant sync step) to update the deployed copy; a direct edit silently drifts from source and gets overwritten on the next install.
- `[available]` gate: `confidence > 0.9` AND `access_count ≥ 3` AND `boost_count ≥ 1`, scanned against both the repo collection and a separately (smaller) capped `GLOBAL_COLLECTION`. Entries without an explicit `/reflect` boost never qualify, regardless of age. Full history (the `[always-present]` rename, the once-missing GLOBAL_COLLECTION scan, the id+title-only format): `<memory-entry>`, `<memory-entry>`, `<memory-entry>`.
- `access_count` means deliberate use (an explicit `min_score_for_tracking` query, a `mem_get` by id, or a positive `mem_boost`) — not passive query surfacing; a plain `mem_query` with no threshold tracks nothing.
- `dream_memory._confidence_report`'s promotion-candidate list is purely deterministic (no memory of past runs) — set `keep_in_ai_mem: true` in an entry's metadata to stop it being re-proposed every `mem-dream` run.
- `mem_move` deliberately bypasses `AddMemoryUseCase` (whose metadata-preserving merge only looks within the collection it's writing to, which would wrongly reset confidence/access_count on a cross-collection move) — reads via `get_by_ids`, writes via `upsert`, deletes the confirmed subset from source. An id that already exists at the target with different text is skipped as a `MoveConflict`, not overwritten. `from_collection == to_collection` raises `ValueError`. Known v1 limitation: edges only reference `target_id`, no collection field — a moved entry's old incoming edges go dangling.
- `detect_repo_context()` checks `AI_MEM_WORKSPACE_ROOT` before the git-based fallback, deriving collection names from the CLAUDE.md path relative to that root instead of `git remote`. Hook subprocesses don't inherit the MCP server's own `env` block, so `install.py` prefixes hook commands with `AI_MEM_WORKSPACE_ROOT=<path>` directly.
- Only `SessionStart` and `PostToolUse` hooks are registered. `PreToolUse` (2026-09-12) and `UserPromptSubmit` (2026-09-13) were both retired after real token-cost/noise measurements showed each firing far more than its value justified (per-edit, then per-message, automatic push). `install.py` no longer registers either; both self-heal off existing installations on re-run via `_remove_hook_command`. Module files and tests for both still exist, just unwired.
- `mem_dream`'s `claude` CLI subprocess call (`dream_memory.py::_call()`) uses bare model aliases (`"sonnet"`, `"haiku"`), not versioned tags — a versioned tag is a bitrot risk since the CLI can stop resolving it whenever Anthropic retires it. On failure it now raises with the CLI's actual `stderr`/`stdout` included, not just a bare exit code.
- Daemon (`daemon.py`) is thread-per-connection with a locked `record_access()` write path; `ChromaMemoryRepository` caches embeddings per-text with per-key locking.
- `injection_log.py` logs every SessionStart push; `mem-dream` cross-references it against `last_accessed_at` to report per-collection pull-through rate on demand (not a live counter — a push's "was it pulled" outcome isn't knowable until later).
