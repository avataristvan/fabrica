# Changelog

## Unreleased

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
(2026-09-12/13, see `docs/hooks.md`) — SessionStart was the last remaining hook that
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
