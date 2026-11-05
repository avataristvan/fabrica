# Architecture

Reference for how the code is laid out. For why ai-mem is built around record files and roles rather than a store with a query engine, see [Organisational memory](../explanation/organisational-memory.md).

ai-mem uses capability-centric DDD with three strict layers. Imports only flow downward: infrastructure -> application -> domain. The adapters (CLIs and hooks) sit on top.

```
ai_mem/
  domain/            pure contracts, no I/O
  application/       one use case per file, single execute(), deps injected
  infrastructure/    file-backed repository, area resolution, record format
  mem_cli.py         `mem` CLI: add, link, delete, move, find, context, lint, doctor
  records_lint.py    `mem lint`: checks and normalises one area's record files
  doctor.py          `mem doctor`: deterministic, read-only diagnosis of the practice
  doctor_sources.py  doctor's Sources section (sources nothing points to)
  doctor_docs.py     doctor's Docs and Not-concluded sections (the documentation map; what a skipped reflect leaves)
  docs_lint.py       lint of experiments, handoff shape and records citing a handoff
  review.py          `mem review`: the records a push would publish, flagged for a last look
  hook.py            SessionStart hook: Area: line, Records: pointer, doctor pointer
  hooks/             enforcing hooks: retro_check, lint_after_write, reflect_reminder
  dream_cli.py       `mem-dream`: consolidates an area's records with the claude CLI
```

The tool server, the warm query process, the vector-store backend and the prompt/tool push hooks were removed at the plugin cutover; the last commit that has them is the tag `v0-last-mcp`.

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
| `delete_memory.py` | `DeleteMemoryUseCase` | delete by ids; a delete without ids is refused |
| `add_edge.py` | `AddEdgeUseCase` | validate both endpoints exist, dedup on (target_id, edge_type), persist |
| `move_memory.py` | `MoveToAreaUseCase` | move records between areas verbatim (`mem move`; bypasses `AddMemoryUseCase`'s merge) |
| `relocate_area.py` | `RelocateAreaUseCase` | plan and write the reference rewrites of an area folder move (`mem move-area`) |
| `dream_memory.py` | `DreamMemoryUseCase` | consolidate an area via a `claude` CLI call: contradictions, redundancy, stale records |

## Infrastructure (`ai_mem/infrastructure/`)

| File | Role |
|---|---|
| `file_repository.py` | `FileMemoryRepository`: the store. Records are the files; `records_dir_for` resolves each area by folder |
| `areas.py` | area resolution (nearest ancestor with `docs/records/`, linked worktrees mapped to the main checkout), area discovery, cross-area reference parsing |
| `area_relocation.py` | path arithmetic, preflight and rename for `mem move-area`; reports what else names the old path (worktrees, editable installs, Claude Code memory, config) |
| `source_files.py` | locate a source; `mem source` changes its `status:` line and nothing else |
| `adr_markdown.py`, `adr_paths.py`, `adr_index.py` | record serialisation, path conventions, INDEX.md generation ([record format](record-format.md)) |

There are no runtime dependencies (`dependencies = []`): everything uses the standard library. The `dev` extra holds `pytest`; `tests/test_stdlib_only.py` checks the promise.

## Doctor (`ai_mem/doctor.py`)

`mem doctor [--root DIR] [--home DIR] [--days N] [--json]` is a deterministic, read-only, stdlib-only diagnosis of whether the records practice is still alive; the only file it writes is `$AI_MEM_PATH/doctor_last_run` (`ai_mem.hooks.DOCTOR_STAMP`, read by the SessionStart pointer). Sections:

- **Records**: the lint checks over every area below `--root`.
- **Sources**: sources nothing points to and sources with a missing field.
- **Docs** (`doctor_docs.py`, by [the documentation map](../../reference/documentation_map.md)): findings of the older record format (`mem lint --fix`), handoffs still open and files or folders in `docs/` that fit no place of the map (`/fabrica:tidy`), the project's own CLAUDE.md, agents and skills that name records by bare name (`/fabrica:setup`), a `data/` that is not git-ignored.
- **Not concluded**: what a skipped reflect leaves behind, as ages without a threshold: experiments `running` (age of their last commit), experiments `done` that no record links to, open handoffs, commits since the records or `FOCUS.md` last changed.
- **State**: handoff or `FOCUS.md` behind the newest change.
- **Wiring**: commands, agents and skills under `<home>/.claude` that spawn agents or name memory but lack `handoff-protocol` (skills installed by a tool, i.e. a folder with `.git`, `VERSION` or a `.*_version` marker, are listed apart as external: they are never edited); whether the four ai-mem hooks are registered in `settings.json` or the plugin is enabled.
- **Effect**: per agent type over the last N days of `retro_log.jsonl` (deduplicated by `agent_id`, last entry wins), the share with `records_consulted` / `record_candidates` given and with missing retro fields; records with at least three incoming `confirms` edges as cue-sharpening candidates.

Everything under `~/.claude` and the log is treated as untrusted input: size-capped regular-file reads, malformed lines and unreadable files skipped, no path built from file content.

## Key invariants

The current-state list lives in `CLAUDE.md` ("Gotchas"), which loads every session, rather than being duplicated here. Incident history behind dated invariants is in the area's records (`docs/records/`, ask the librarian).
