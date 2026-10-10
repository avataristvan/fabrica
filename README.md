# ai-mem

A pull-based knowledge base for AI agents — not automatic context injection. Decisions, learnings, todos and the current focus live as git-native Markdown files in each project (`docs/records/`), reviewable and greppable without any tooling; ai-mem's MCP tools write and link them, and a librarian agent reads them by judgment. No database (since 2026-10-04; an existing ChromaDB store is migrated once, see `docs/migration-chroma-to-records.md`).

Works with **Claude Code**, **Gemini CLI**, and **Cursor**.

> **Beyond memory.** Paired with the `/reflect` ritual, ai-mem lets agents accumulate structured experience across tasks and projects — patterns that held, approaches that failed and why, decisions worth remembering. It's a knowledge base an agent queries deliberately, not a feed pushed into every prompt. [Read the framework docs →](docs/epistemology-framework.md) · [Wire your own skills and agents →](docs/skill-agent-integration.md)

## Workflow

ai-mem is designed around a three-phase task loop:

```
/plan  →  [coding]  →  /reflect
  ↑                        |
  └──── memories updated ←─┘
```

| Phase | What happens | ai-mem role |
|-------|-------------|-------------|
| **Plan** | Review goals, prior decisions, current focus | `mem_query` surfaces relevant context |
| **Code** | Implement the task | — |
| **Reflect** | Capture what was learned, good and bad | `mem_add` stores learnings for the next session |

Run `/reflect` after completing a task. It walks through a lightweight standup: agent observations first, two questions, then next-todo aggregation. The next session starts where this one left off.

## Install

```bash
git clone https://github.com/avataristvan/ai-mem.git
cd ai-mem
python3 install.py
```

> **First steps:** Run `/mem-init` in your project directory, then `/reflect` after every task.
> Storage alone doesn't make ai-mem useful — the reflect ritual is what closes the loop.

## Tools

| Tool | Description |
|------|-------------|
| `mem_add` | Store or update entries. Set `ttl_days` for automatic expiry. Set `type` for filtering (`feedback`, `project`, `reference`, `pattern`, `anti-pattern`). |
| `mem_query` | Semantic search. Returns results ordered by cosine similarity, with scores. Optionally filter by `type` or `max_age_days`. |
| `mem_list` | List collections with counts, or list all entries in a specific collection. |
| `mem_delete` | Delete entries by ID, or drop an entire collection. |
| `mem_cleanup` | Remove expired (TTL) entries. Pass `stale_after_days` to prune entries not accessed within that window. |
| `mem_split` | Split a long entry into focused sub-entries for more precise retrieval. |
| `mem_dream` | Consolidate a collection using Claude — detects contradictions, redundancies, and stale entries. Proposes UPDATE / MERGE / DELETE / ADD / SPLIT / LINK / SUPERSEDE; `auto_delete`, `auto_link` and `auto_supersede` apply the respective actions. |
| `mem_get` | Fetch entries by ID directly — bypasses semantic search and ranking. Use when the exact ID is known. |
| `mem_boost` | Cite an entry as decisive during `/reflect`: increments `boost_count` and bumps `last_accessed_at`. No `delta` parameter. Optional `cue` names the situation in which the entry would have helped; it is written into the record file's frontmatter, where the librarian agent reads it. |
| `mem_link` | Create a typed causal edge between two entries (`contradicts`, `fixes`, `causes`, `related`, `supersedes`, `confirms`). |
| `mem_edges` | List all outgoing edges for an entry. |

## `mem` CLI

`mem` writes record files directly, without the MCP server: stdlib only, one line per action (`--json` for agents). The area is the nearest ancestor of the cwd with `docs/records/` (`--area PATH` overrides).

```bash
mem add --id ID --type learning --topic tools --text "..."   # or --file F, or - for stdin
mem add --id ID --cue "situation in which this helps"        # existing record: only the given fields change
mem add --id current_focus --text "..."                      # writes FOCUS.md
mem link SOURCE TARGET --type related [--to-area PATH]       # TARGET bare, or <rel-area-path>:<id>
mem delete ID...
mem context [PATH] [--json]                                  # area root, records dir, INDEX/FOCUS paths
```

Ids are plain file stems (no `:`, separators or glob characters). Exit codes: 0 ok, 1 conflict or not found, 2 usage or invalid input, 3 migration pending (see `UPGRADING.md`; nothing is written). `mem lint` and `mem doctor` are reserved and print "not implemented yet" (exit 2).

## Memory Scoping

Collections are auto-detected from the working directory:

| Scenario | Collection |
|---|---|
| `CLAUDE.md` at git root | `repo.<repo-name>` |
| `CLAUDE.md` in monorepo subdir | `repo.<repo-name>.<subdir>` |
| No `CLAUDE.md` found | `workspace` |
| Cross-session general knowledge | `global` |

The `SessionStart` hook injects the active collection on every session start.

## Lifecycle Hooks

ai-mem registers one Claude Code hook during install:

| Hook | Trigger | What it does |
|------|---------|--------------|
| `SessionStart` | Session opens | Announces the active collection (and, for a registered subagent, its own expert collection) — no memory content by default |

**Pull, not push.** Earlier versions injected `current_focus` text, high-confidence entries, and even per-prompt semantic search results automatically. That got expensive and noisy — content unrelated to the task in hand was in context on every message. Now `SessionStart` only tells the agent *which* collection to use; retrieving anything from it is a deliberate `mem_query` or `mem_get` call the agent (or a skill like `/reflect`) makes on purpose. Set `session_start_verbose: true` in `agents.yaml` to opt back into the old push behavior — see `docs/hooks.md`.

**A pointer instead of content.** Agents rarely think to query memory unless something in their context points at it (`scripts/eval_pull` measured this). So `SessionStart` adds one line naming the repo's `docs/records/` (FOCUS.md, INDEX.md) and the librarian agent. The librarian reads the record files by judgment, including each record's `cue` — the situation in which it helps, written during `/reflect` (`mem_boost(ids=[...], cue="...")`). Until 2026-10-04 those cues were pushed as an "experience index" block at every session start; the librarian replaces it.

## Trust Signals

`confidence` and `access_count` were dropped 2026-09-26 as trust signals in favor of evidence edges and a librarian-style retrieval agent — see `docs/records/architecture/decisions/domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md`. They are no longer written or read; legacy values remain untouched in stored metadata. What's current:

| Event | Effect |
|-------|--------|
| `/reflect` cites an entry as decisive | `mem_boost(ids=[...])` — increments `boost_count`, bumps `last_accessed_at` |
| `mem_boost(ids=[...], cue="...")` | Additionally records the situation in which the entry helps, in the record file's `cue:` line |

The `[available]` listing that `boost_count ≥ 1` used to unlock was retired 2026-10-04 (push → pull, see `docs/hooks.md`).

Retrieval is INDEX.md, grep, and the librarian agent; `mem_query` is a keyword search over the files.

## Typed Causal Edges

Entries can be linked with directional typed edges to model relationships between knowledge:

```
mem_link(source_id="antipattern_xyz", target_id="pattern_abc", edge_type="contradicts", collection="repo.my-project")
```

Edge types: `contradicts` · `fixes` · `causes` · `related` · `supersedes` · `confirms` (later record → earlier one it bears out)

During `mem_query`, linked entries are automatically surfaced alongside their source (1-hop, budget: 2 entries per query). Appended entries are tagged with `via_edge` and `via_source` in their metadata.

**Superseding an entry.** `mem_link(source_id=<new>, target_id=<old>, edge_type="supersedes")` marks `<old>` as overtaken instead of deleting it: `mem_query` still returns it, flagged with a top-level `superseded_by`, and appends the newest surviving successor (following chains) ahead of ordinary edge targets. The old entry keeps its reasoning; a superseded entry cannot itself supersede another, which rules out cycles. To undo, `mem_add` the old entry with `metadatas=[{"superseded_by": "", "valid_until": ""}]`. `mem_dream` does not treat a `supersedes` target as protected.

**Primary use case:** link `type=anti-pattern` entries to the `type=pattern` they contradict. When you retrieve a best-practice, the matching anti-pattern surfaces automatically — and vice versa.

```
mem_edges(entry_id="pattern_abc", collection="repo.my-project")
# → [{"target_id": "antipattern_xyz", "edge_type": "contradicts"}]
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_MEM_PATH` | `~/.local/share/ai-mem` | Database location |
| `AI_MEM_WORKSPACE_ROOT` | unset (git-based detection) | Root directory used to name collections by folder structure instead of git remotes, e.g. `~/workspace` → `acme-project/filming` → `repo.acme-project.filming`. Set interactively during `install.py`, or manually in the `env` block of the `ai-mem` entry in `~/.claude.json`. |

### Wiring an agent into memory: `examples/agents/`, not a registry

Whether an agent uses ai-mem is decided per agent, by editing that agent's own prompt
— not by listing it somewhere central. Copy `examples/agents/example-agent-with-memory.md`
to `~/.claude/agents/<name>.md`, adapt it, and it pulls (`mem_query`) and stores
(`mem_add`) on its own. See `docs/skill-agent-integration.md` for the full pattern.

### Tuning hooks (`~/.config/ai-mem/agents.yaml`)

```yaml
inject_agents:
  - my-coding-agent       # let SessionStart's routing line name this custom agent's
                           # own subagent.my-coding-agent collection (it still has to
                           # query/write it itself — see examples/agents/ above)

signatures:
  - name: my-coding-agent
    markers:
      - "unique phrase from the agent's system prompt"

settings:
  session_start_verbose: false   # true restores focus text + expired warnings + deltas at session start
```

Requires `pyyaml`: `pip install ai-mem[config]`. Falls back to defaults if absent.

## Architecture

Three-layer capability-centric DDD — imports only flow downward.

| Layer | Path | Role |
|---|---|---|
| Domain | `ai_mem/domain/` | Pure contracts (`MemoryRepository` protocol). No I/O. |
| Application | `ai_mem/application/` | One use case per file, single `execute()`, deps injected. |
| Infrastructure | `ai_mem/infrastructure/` | `FileMemoryRepository` (default), chosen in `repository_factory.py`; `ChromaMemoryRepository` + `MarkdownAdrRepository` + `BM25MemoryRepository` only with `AI_MEM_BACKEND=chroma`. |

`server.py` is the adapter — wires use cases at module load, exposes MCP tools.

## Uninstall

```bash
python3 uninstall.py          # interactive — remove hooks, MCP entry, commands
python3 uninstall.py --dry-run  # preview without changes
```

Memory data (`~/.local/share/ai-mem`) and user config (`~/.config/ai-mem`) are never touched.

## Update

```bash
cd ai-mem && git pull
```

No reinstall needed — installed in editable mode.

## Requirements

- Python 3.10+
