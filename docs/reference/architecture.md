# Architecture

Reference for how the code is laid out. For why ai-mem is built around record files and roles rather than a store with a query engine, see [Organisational memory](../explanation/organisational-memory.md).

ai-mem uses capability-centric DDD with three strict layers. Imports only flow downward: infrastructure -> application -> domain. The adapters (CLIs and hooks) sit on top.

```
ai_mem/
  domain/            pure contracts, no I/O
  application/       one use case per file, single execute(), deps injected
  infrastructure/    file-backed repository, area resolution, record format, migration reader
  mem_cli.py         `mem` CLI: add, link, delete, move, find, context, lint, doctor
  records_lint.py    `mem lint`: checks and normalises one area's record files
  doctor.py          `mem doctor`: deterministic, read-only diagnosis of the practice
  doctor_sources.py  doctor's Sources section (sources nothing points to, docs describing retired systems)
  hook.py            SessionStart hook: Area: line, Records: pointer, doctor pointer
  hooks/             enforcing hooks: retro_check, lint_after_write, reflect_reminder
  dream_cli.py       `mem-dream`: consolidates an area's records with the claude CLI
  adr_cli.py         `mem-adr-sync`: reindex, and one-time migration into record files
  view_cli.py        `mem-view`: interactive terminal browser
  upgrade_guard.py   one SessionStart line while an upgrade step is pending
  repo_context.py    legacy collection naming, kept only until the plugin cutover
```

Retired modules that still sit in the tree until the cutover (the query server and its client side, the unwired prompt/tool hooks) are listed in `CLAUDE.md`; do not build on them.

## Domain (`ai_mem/domain/memory.py`)

- `MemoryEntry`: id, text, metadata, plus timestamp fields.
- `QueryResult`: rank, id, score, text, metadata.
- `EdgeType`: `Literal["contradicts", "fixes", "causes", "related", "supersedes", "confirms", "derived_from"]` (`derived_from`: a decision points at the learning it rests on).
- `MemoryEdge`: target_id, edge_type.
- `MemoryRepository` Protocol: `upsert`, `query`, `get_by_ids`, `list_collections`, `delete`, `get_all`, `add_edge`, `get_edges` (a few members are no-ops on the file backend, see `CLAUDE.md` Gotchas).

There is no ranking-related domain type: no model decides relevance. Reading is by judgment (the librarian), not by score.

## Application (`ai_mem/application/`)

One use case per file, each with a single public `execute()`.

| File | Use case | Responsibility |
|---|---|---|
| `add_memory.py` | `AddMemoryUseCase` | upsert with timestamps; preserves `created` on re-add |
| `get_memory.py` | `GetMemoryUseCase` | fetch by exact ids |
| `query_memory.py` | `QueryMemoryUseCase` | keyword overlap over the record files, not semantic |
| `delete_memory.py` | `DeleteMemoryUseCase` | delete by ids; a delete without ids is refused |
| `list_entries.py`, `list_topics.py`, `list_collections.py` | listing use cases | id + title pairs, grouping by type |
| `add_edge.py`, `get_edges.py` | edge use cases | validate both endpoints exist, dedup on (target_id, edge_type), persist |
| `move_memory.py` | `MoveMemoryUseCase` | move records verbatim (bypasses `AddMemoryUseCase`'s merge) |
| `split_memory.py` | `SplitMemoryUseCase` | break a coarse record into focused ones via a `claude` CLI call |
| `detect_split_hints.py` | | flags records that have grown too coarse |
| `dream_memory.py` | `DreamMemoryUseCase` | consolidate an area via a `claude` CLI call: contradictions, redundancy, stale records |

## Infrastructure (`ai_mem/infrastructure/`)

| File | Role |
|---|---|
| `file_repository.py` | `FileMemoryRepository`: the store. Records are the files; area mode (`records_dir_for=`) resolves each area by folder |
| `repository_factory.py` | `build_repository()`: chooses the repository |
| `areas.py` | area resolution (nearest ancestor with `docs/records/`), area discovery, cross-area reference parsing |
| `adr_markdown.py`, `adr_paths.py`, `adr_index.py` | record serialisation, path conventions, INDEX.md generation ([record format](record-format.md)) |
| `chroma_sqlite_reader.py`, `records_migration.py` | read-only reader and planner for the one-time migration ([how-to](../how-to/migrate-to-records.md)) |
| `chroma_repository.py`, `markdown_adr_repository.py`, `bm25_repository.py` | the rollback stack, only with `AI_MEM_BACKEND=chroma` ([facts](chroma_rollback_backend.md)) |

Runtime code of the practice (`mem`, hooks, lint, doctor) uses the standard library only.

## Doctor (`ai_mem/doctor.py`)

`mem doctor [--root DIR] [--home DIR] [--days N] [--json]` is a deterministic, read-only, stdlib-only diagnosis of whether the records practice is still alive; the only file it writes is `$AI_MEM_PATH/doctor_last_run` (`ai_mem.hooks.DOCTOR_STAMP`, read by the SessionStart pointer). Sections:

- **Records**: the lint checks over every area below `--root`.
- **Sources**: sources nothing points to, sources with a missing field, and current docs that still describe a retired system as current.
- **State**: handoff or `FOCUS.md` behind the newest change.
- **Migration**: a pending upgrade step.
- **Wiring**: commands, agents and skills under `<home>/.claude` that spawn agents or name memory but lack `handoff-protocol`; whether the four ai-mem hooks are registered in `settings.json` or the plugin is enabled.
- **Effect**: per agent type over the last N days of `retro_log.jsonl` (deduplicated by `agent_id`, last entry wins), the share with `records_consulted` / `record_candidates` given and with missing retro fields; records with at least three incoming `confirms` edges as cue-sharpening candidates.

Everything under `~/.claude` and the log is treated as untrusted input: size-capped regular-file reads, malformed lines and unreadable files skipped, no path built from file content.

## Key invariants

The current-state list lives in `CLAUDE.md` ("Gotchas"), which loads every session, rather than being duplicated here. Incident history behind dated invariants is in the area's records (`docs/records/`, ask the librarian).
