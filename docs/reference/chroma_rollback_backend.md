Chroma rollback backend and dormant modules -- facts that only matter with AI_MEM_BACKEND=chroma or when touching code that is no longer wired. Moved out of CLAUDE.md on 2026-10-04 when the record files became the only store (domain_file_backend_replaces_chroma_2026_10_04); removal is tracked in todo_drop_chromadb_dependency.

## Chroma rollback stack (AI_MEM_BACKEND=chroma)

- Needs the optional extra: `pip install -e '.[chroma]'` (chromadb is no longer a default dependency; `.[dev]` includes it for the test suite). `mem-adr-sync export`/`import` need it too; `migrate` and `reindex` do not.
- The records_v1 migration no longer aligns the stored `type`/`area` of auto-classified entries with their new files (it never writes the store). So on this stack a `mem_add` to such an entry with its old stored type (e.g. `feedback`) removes its record file -- retype it first.
- Built by `repository_factory.build_repository()`: `ChromaMemoryRepository` -> `MarkdownAdrRepository` (unless `AI_MEM_ADR_DISABLED=1`) -> `BM25MemoryRepository` (when `rank_bm25` is installed). `server.py` and `dream_cli.py` share it, so `mem-dream --auto_*` never desyncs a file from its entry.
- `mem_delete` with no `ids` drops the entire collection; the repo signals this by returning `-1`. Files are never touched by a whole-collection delete.
- Cosine similarity from ChromaDB distance: `cos_sim = 1 - dist/2` (collections use l2/squared-L2 space, verified via `col.configuration_json`). The older `1 - dist` formula was wrong.
- Tests that call `upsert` on Chroma directly must pass non-empty metadata (ChromaDB rejects empty dicts); `AddMemoryUseCase` always injects timestamps.
- `MarkdownAdrRepository` projects every record type in `KIND_BY_TYPE` to `docs/records/<area>/<kind>/<id>.md` and `current_focus` to `FOCUS.md`. Volatile fields (`boost_count`, `last_accessed_at`, legacy `confidence`/`access_count`) never reach the file, so a plain `mem_boost` produces no diff; a `cue` change does. INDEX.md is regenerated (full rescan, atomic replace) when a record file is created, removed or moved or an INDEX row changes -- never on a boost-only upsert. Re-typing or re-areaing removes the old file; re-typing to a non-record type deletes it.
- `last_accessed_at` meant deliberate use (a `mem_get`, a `mem_boost`, or a query with `min_score_for_tracking`), never passive surfacing.
- `confidence` and `access_count` were dropped 2026-09-26 in favour of evidence edges; old values stay untouched in stored metadata -- never migrate them away.
- The daemon (`daemon.py`, `daemon_client.py`) keeps one warm `ChromaMemoryRepository` for hook calls: thread-per-connection, a locked `record_access()` write path, and a per-text embedding cache with per-key locking. `_hook_deps._build_query_uc()` only tries it on the Chroma backend.
- The ML ranker (`TorchMicroRanker`, `RankerRegistry`) was removed in 2026-06; no `[ml]` extra or torch dependency remains.

## Dormant modules (present, not wired)

- Hooks `posttool_hook.py`, `pretool_hook.py`, `userprompt_hook.py`: unregistered by `install.py`, which removes them from existing installs via `_remove_hook_command`. `posttool_hook.py` imports `GLOBAL_COLLECTION` and `detect_repo_context` at module level so tests can `patch.object` them -- check test-side patch targets before removing an import that looks dead.
- `experience_index.py`: no production caller since the librarian replaced the pushed index; only `normalize_cue` is used (by `mem_boost`).
- `injection_log.py`: no live writer since 2026-09-13; `mem-dream`'s pull-through report only covers pushes logged before that.
- `session_stats.py`: `record_injection()` runs only in the opt-in verbose SessionStart path; `injection_rate()` has no production caller.
- `memory_index.py`: MEMORY.md auto-demotion (180 -> 160 lines), built but no trigger wired.
