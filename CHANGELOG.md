# Changelog

## Unreleased

### Removed: the legacy upgrade path

- `install.py`, `uninstall.py`, `UPGRADING.md` and `docs/how-to/migrate-to-records.md`; the records_v1 migration (`mem-adr-sync migrate`, `records_migration.py`, `chroma_sqlite_reader.py`); the upgrade guard (`upgrade_guard.py`: the SessionStart line, `mem` exit 3, the `mem doctor` "Migration" section and JSON key `migration`); `scripts/upgrade_acceptance/`; the `chromadb` entry of the `dev` extra. `mem-adr-sync reindex` (also `--collection`) stays.
- The last version that carries the upgrade path is the tag `v1-last-upgrade-path`: an old installation checks out that tag, upgrades, then moves to `main`. The tag `v0-last-mcp` stays as the rollback to the MCP version.
- `tests/test_stdlib_only.py` keeps the `dependencies = []` check that lived in `tests/test_upgrade_guard.py`.

### Changed: agent definitions after a field report (librarian scope, archivist edges)

- `librarian` also reads `docs/*.md` (plans, handoffs) and says "not read: ..." when material is out of its reach.
- `archivist`: a resolved contradiction is unlinked and replaced by `confirms`; back-references are always written by the archivist, in any area; `mem add --id` is documented to keep edges; `mem find`/`Grep` is the fallback when `Glob` is missing.

### Removed: the MCP server, the daemon and the Chroma backend (cutover to the plugin)

- **Breaking:** `ai_mem/server.py` (`mem_*` MCP tools), the query daemon, `repository_factory.py` with the Chroma/BM25/Markdown-projection repositories (`AI_MEM_BACKEND=chroma`), the PreToolUse/UserPromptSubmit/PostToolUse push modules, `agent_context.py`, `session_stats.py`, `injection_log.py`, the use cases only the server called, `mem-adr-sync export`/`import`, `mem-dream --collection`/`--expert`, `agents.yaml` handling and `scripts/eval_pull/replay.py`. The last commit that has them is the tag `v0-last-mcp`.
- `pyproject.toml`: `dependencies = []`; the only extra is `dev` (`pytest`, plus `chromadb` for the migration test fixtures). The `chroma`, `hybrid` and `config` extras are gone.
- SessionStart prints `Area:`, `Records:` and the upgrade/doctor pointers; the `Active collection:` and `Expert collection:` lines and the verbose mode are gone.
- The records_v1 migration (`mem-adr-sync migrate`, stdlib sqlite reader, no extra) and `mem-adr-sync reindex` stay. The ChromaDB store on disk is never touched.
- `install.py` no longer registers an MCP server for Claude Code, Gemini CLI or Cursor; `install.py --plugin-switch` offers to remove the old registration, the `mcp__ai-mem__*` permissions and the retired push hooks. `UPGRADING.md` has part 2 of "MCP server -> plugin".

### Added: Claude Code plugin package (`ai-mem@ai-mem`)

- `.claude-plugin/plugin.json` and `marketplace.json`; `agents/` (`librarian`, `archivist`, `anchor-lint`, moved from `examples/agents/`), `skills/reflect/SKILL.md` (was `skills/examples/reflect.md`), `skills/handoff-protocol/`, `hooks/hooks.json` (all four hooks through `hooks/run.py`), `bin/mem` and `bin/mem-dream` (sh shims, system `python3`, no `pip install`). Names are namespaced: `ai-mem:librarian`, `/ai-mem:reflect`.
- Plugin options `retro_roles` and `doctor_cadence_days` reach the hooks as `CLAUDE_PLUGIN_OPTION_*`; the files and defaults of before stay the fallback. `retro_check` lists `ai-mem:anchor-lint`, not the bare name.
- SessionStart no longer stays silent when `~/.local/share/ai-mem` does not exist, so the `Area:` line works on a plugin-only machine.
- `install.py` no longer registers hooks, copies `/reflect` or links agents, skills and the navigation reference; `install.py --plugin-switch` and `uninstall.py` remove what older versions left in `~/.claude`. `UPGRADING.md` has part 1 of "MCP server -> plugin".

### Added: upgrade path for auto-updating installations (`UPGRADING.md`)

- `UPGRADING.md` walks an unattended agent through each breaking step with exact commands and
  explicit STOP conditions (a diverged `git pull --ff-only` is never merged or reset).
- SessionStart prints one `ai-mem upgrade pending` line first while a ChromaDB store exists
  without `.migrations/records_v1.done` (`ai_mem/upgrade_guard.py`, stdlib only).
- `mem-adr-sync migrate` reads the store read-only with stdlib `sqlite3`
  (`chroma_sqlite_reader.py`) and never writes it; an unknown schema or unapplied queued writes
  stop it with exit 1. `--apply` writes `records_v1.done` only for a plan without unplaced
  entries or conflicts, else exits 1. It no longer aligns Chroma metadata of auto-classified
  entries, and its store backup skips sockets (a running daemon's `daemon.sock` aborted it).
- **Breaking (packaging):** `chromadb` moved to the optional `chroma` extra, needed only for the
  `AI_MEM_BACKEND=chroma` rollback and `mem-adr-sync export`/`import`. `.[dev]` includes it.

### Added: `supersedes` edge — flag overtaken entries instead of deleting them

`mem_link(source_id=<new>, target_id=<old>, edge_type="supersedes")` marks `<old>` with
`superseded_by` / `valid_until` metadata. `mem_query` keeps returning it but flags it
(top-level `superseded_by` in the result) and appends the newest surviving successor before
ordinary edge targets. A superseded entry cannot supersede another (no cycles). `mem_dream`
no longer treats a `supersedes` target as protected by its edge or by `access_count`.
Note: edges are stored on the source entry only, so other edge types still surface from the
source's side alone — `supersedes` works from the target's side because of the metadata flag.

### Added: experience index — `cue` on entries, shown at SessionStart

Agents only fetched memory when an entry id already stood in their context (`scripts/eval_pull`),
so `SessionStart` now also prints a small `[experience index]`: up to 20 lines
`<situation> -> <entry id>: <title>`, derived on every read from entries whose metadata carries a `cue`.
- `mem_boost` takes an optional `cue` (one sentence, max 140 chars, whitespace collapsed; empty string clears it).
  `delta=0` records the cue without a boost. `/reflect` Step 3.1 asks for it.
- Membership is decided by the cue, not by `confidence`/`access_count`. Superseded and expired entries are
  left out, so the index cannot go stale. Over the cap, higher `boost_count`, then newer entries stay and a
  `(+N more cues)` line reports the rest.
- `session_start_index: false` in `agents.yaml` switches it off; it appears in default and verbose mode.

### Added: `mem_dream` proposes and applies LINK and SUPERSEDE

- **LINK** (`- LINK <source> -> <target> [type=<edge_type>]: <reason>`) documents a relationship between
  two entries instead of merging them; `auto_link=true` creates the edges. The valid types are derived
  from `EdgeType` (minus `supersedes`), so a new edge type cannot drift out of the prompt or the parser.
- **SUPERSEDE** (`- SUPERSEDE <new> -> <old>: <reason>`) flags the old entry via the `supersedes` edge;
  `auto_supersede=true` applies it. The old entry stays readable.
- Actions that cannot be applied — unknown ids, ids in different collections, invalid types, a source that
  is itself superseded — are listed under "Skipped" with their reason instead of being dropped silently.
- MERGE proposals whose entries share a `contradicts` or `supersedes` edge are flagged under
  "Merge Conflicts". Based on the LINK action and merge guard from the review branch, reworked for the
  current code (the branch itself is not mergeable: it predates the removal of the ML ranker).

### Breaking: SessionStart is pull-based by default

`SessionStart` used to push `current_focus` text, the `[available]` high-confidence
listing, expired-entry warnings, the entry-count delta, and recent git commits into
every session automatically. It now prints only a one-line routing hint (the active
collection, and a subagent's own `subagent.<name>` collection where applicable) —
retrieving anything else is a deliberate `mem_query`/`mem_get` call the agent makes.

**To restore the old behavior:** set `session_start_verbose: true` under `settings:`
in `~/.config/ai-mem/agents.yaml` (see `agents.yaml.example`).

This pairs with the `UserPromptSubmit`/`PreToolUse` push hooks retired earlier
(2026-09-12/13, see `docs/reference/hooks.md`) — SessionStart was the last remaining hook that
pushed memory *content* rather than routing.

`~/.config/ai-mem/agents.yaml`'s `inject_agents` no longer implies "this agent should
receive ai-mem content" — it only lets SessionStart's routing line recognize a custom
agent type and name its collection. Whether an agent actually uses ai-mem is now
decided per agent, in the agent's own prompt — see `examples/agents/`.

### Breaking: boost_count gate for [always-present] (commit 2088853)

Entries injected proactively at every session start (`[always-present]`) now require:

- `confidence > 0.9`
- `access_count ≥ 3`
- **`boost_count ≥ 1`** ← new

Existing entries (created before this change) have no `boost_count` key and will
no longer appear in `[always-present]` until they receive an explicit `/reflect` boost.

**Migration:** run once after `git pull`:

```bash
python3 scripts/migrate_boost_count.py --dry-run   # preview
python3 scripts/migrate_boost_count.py             # apply
```

The script sets `boost_count=1` for entries with `confidence ≥ 1.0` and
`access_count ≥ 3` — entries that were heavily used before the boost_count signal
existed. New entries (confidence = 0.7) are not affected.

---

### Breaking: confidence default changed from 1.0 to 0.7 (commit 7308f82)

New entries now start at `confidence = 0.7`. Upserts preserve the stored value.

**Effect:** New entries require 2 explicit `/reflect` boosts (`+0.1` each) to reach
`confidence > 0.9` and qualify for `[always-present]`.

No migration needed — existing entries are unaffected.

---

### Removed: ML ranker (commit a7110da)

`TorchMicroRanker`, `RankerRegistry`, `BuildFeaturesUseCase`, `TrainRankerUseCase`,
and the `[ml]` pip extra have been removed. The `mem_train` MCP tool no longer exists.

`QueryMemoryUseCase` now returns ChromaDB cosine results directly. Confidence lifecycle
(`/reflect` → `mem_boost`) is the replacement signal.

**Migration:** remove `pip install -e ".[ml]"` from any automation scripts. If you have
`.pt` ranker weight files in `~/.local/share/ai-mem/rankers/`, they can be deleted.

---

## Update procedure

```bash
cd ai-mem && git pull
python3 scripts/migrate_boost_count.py   # run after any update that lists a migration above
```

No reinstall needed — installed in editable mode.
