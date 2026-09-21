# Architecture

ai-mem uses capability-centric DDD with three strict layers. Imports only flow downward: infrastructure → application → domain.

```
ai_mem/
  domain/            pure contracts — no I/O
  application/       one use case per file, single execute(), deps injected
  infrastructure/    ChromaDB + optional BM25 hybrid wrapper
  server.py          MCP adapter — wires everything at module load, exposes mem_* tools
  hook.py            SessionStart hook (routing by default; content push opt-in)
  posttool_hook.py   PostToolUse hook — passive access-count signal after Write/Edit
  daemon.py          background query daemon — one warm repository across hook calls
  daemon_client.py   hook-side helper: talk to the daemon, fall back to an in-process repo
  daemon_protocol.py shared constants/paths for the daemon; PROTOCOL_VERSION gates compat
  dream_cli.py       `mem-dream` CLI entry point
  view_cli.py        `mem-view` CLI — interactive terminal browser for collections/entries
  memory_index.py    MEMORY.md auto-demotion logic (built, not wired to any hook)
  session_stats.py   rolling per-scope injection stats (20-session window)
  injection_log.py   logs SessionStart pushes so mem-dream can report pull-through
  repo_context.py    git-root/CLAUDE.md detection → collection name derivation
  agent_context.py   subagent-vs-orchestrator detection; agents.yaml loading
  _hook_deps.py      shared use-case wiring for hooks (daemon-or-in-process)

  # Retired, kept only so existing installs uninstall cleanly (see docs/hooks.md):
  userprompt_hook.py UserPromptSubmit hook — not registered by install.py
  pretool_hook.py    PreToolUse hook — not registered by install.py
```

## Domain (`ai_mem/domain/memory.py`)

- `MemoryEntry` — id, text, metadata + datetime fields (created_at, expires_at, last_accessed_at, access_count)
- `QueryResult` — rank, id, score, text, metadata
- `SplitHint` — id, text_preview (first 80 chars), access_count — surfaced by `detect_split_hints.py`
- `CollectionInfo` — name, count
- `EdgeType` — `Literal["contradicts", "fixes", "causes", "related", "supersedes"]`
- `MemoryEdge` — target_id, edge_type
- `MemoryRepository` Protocol — `upsert`, `query`, `get_by_ids`, `list_collections`, `delete`, `delete_expired`, `record_access`, `delete_stale`, `get_all`, `add_edge`, `get_edges`

There is no ranking-related domain type (`RankingFeatures`, `LearnedRanker`, etc.) — the ML ranker was removed in 2026-06 (see CLAUDE.md's Critical Invariants).

## Application (`ai_mem/application/`)

| File | Use case | Responsibility |
|------|----------|----------------|
| `add_memory.py` | `AddMemoryUseCase` | upsert with timestamps; preserves existing history (created_at, access_count, confidence) on re-add |
| `query_memory.py` | `QueryMemoryUseCase` | semantic query; tracks access only when the caller passes `min_score_for_tracking` |
| `get_memory.py` | `GetMemoryUseCase` | fetch by exact IDs; optional `track_access` |
| `delete_memory.py` | `DeleteMemoryUseCase` | delete by IDs, or drop an entire collection (no `ids` → repo returns `-1`) |
| `list_collections.py` | `ListCollectionsUseCase` | list collections with counts |
| `list_entries.py` | `ListEntriesUseCase` | id + title pairs for a collection |
| `list_topics.py` | `ListTopicsUseCase` | group a collection's entries by `type` — the rung between `mem_list`'s flat dump and `mem_get`'s full text |
| `cleanup_memory.py` | `CleanupMemoryUseCase` | TTL expiry + optional stale-entry delete |
| `track_access.py` | `TrackAccessUseCase` | bump `last_accessed_at` + `access_count` |
| `boost_confidence.py` | `BoostConfidenceUseCase` | adjust `confidence`; a positive delta also bumps `access_count` (the `/reflect` citation signal); optional `cue` sets/clears the entry's experience-index cue |
| `experience_index.py` | `ExperienceIndexUseCase` | render "situation -> entry" lines from live entries that carry a `cue` (superseded/expired excluded, capped); computed on read, never stored |
| `add_edge.py` | `AddEdgeUseCase` | validate both endpoints exist, dedup on (target_id, edge_type), persist via `repo.add_edge()` |
| `get_edges.py` | `GetEdgesUseCase` | thin wrapper over `repo.get_edges()` |
| `move_memory.py` | `MoveMemoryUseCase` | move entries between collections verbatim (bypasses `AddMemoryUseCase`'s merge — see CLAUDE.md) |
| `split_memory.py` | `SplitMemoryUseCase` | break a coarse entry into focused sub-entries via a `claude` CLI call |
| `detect_split_hints.py` | — | flags entries that have grown too coarse and should be split |
| `dream_memory.py` | `DreamMemoryUseCase` | consolidate a collection via a `claude` CLI call — contradictions, redundancy, decay candidates, promotion candidates |

`QueryMemoryUseCase` returns results in ChromaDB's native cosine order — no re-ranking step.

## Infrastructure (`ai_mem/infrastructure/`)

| File | Class | Notes |
|------|-------|-------|
| `chroma_repository.py` | `ChromaMemoryRepository` | timestamps as Unix float metadata; edges stored as a JSON string in the `edges` metadata field; owns its own embedding function with a per-text LRU cache |
| `bm25_repository.py` | `BM25MemoryRepository` | wraps any `MemoryRepository`; fetches extra candidates and fuses BM25 + cosine scores; delegates `add_edge`/`get_edges` to the inner repo |

No ranker infrastructure remains (`torch_ranker.py`, `null_ranker.py`, `ranker_storage.py` are gone with the 2026-06 removal).

## Key Invariants

See CLAUDE.md's "Critical Invariants" section — kept there (loads every session) rather than duplicated here, since it's the up-to-date, current-state list; incident history for anything dated lives in ai-mem's own `repo.ai-mem` memory collection.
