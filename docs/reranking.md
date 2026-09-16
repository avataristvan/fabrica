# Confidence Lifecycle

> The ML re-ranker was removed in 2026-06 and replaced by the confidence model below. As of 2026-09-16, `SessionStart` no longer surfaces any of this automatically by default — see `docs/hooks.md`.

ai-mem tracks the epistemic status of each entry via a `confidence` field (float 0.0–1.0) stored in ChromaDB metadata.

## Lifecycle

| Stage | Trigger | Effect |
|-------|---------|--------|
| Write | New entry created | `confidence = 0.7` |
| Boost | `/reflect` confirms entry was decisive | `mem_boost(delta=+0.1)` |
| Decay | Dream cycle flags it as stale | `mem_boost(delta=-0.1)` |
| `[available]`-eligible | `confidence > 0.9` AND `access_count ≥ 3` AND `boost_count ≥ 1` | Listed (id + title only) at `SessionStart` when `session_start_verbose: true`, or fetched on request |
| Decay candidate | `confidence < 0.3` | Flagged in `mem_dream` report |
| Promotion candidate | `confidence > 0.9` AND `access_count ≥ 3` | Flagged in `mem_dream` report for CLAUDE.md |

Explicit override: pass `confidence=<value>` in `mem_add` metadata to set a precise start value. Pass `confidence_delta=<±value>` to apply an additive adjustment relative to the stored value.

## Retrieval

`QueryMemoryUseCase` returns results in ChromaDB's native cosine order. No re-ranking step. `TrackAccessUseCase` increments `access_count` and updates `last_accessed_at` — but only when the caller passes an explicit `min_score_for_tracking` (deliberate use, not passive query surfacing). These feed the confidence gate for `[available]`.

## mem_boost

```python
mem_boost(ids=["entry_id"], collection="repo.my-project", delta=0.1)   # boost
mem_boost(ids=["entry_id"], collection="repo.my-project", delta=-0.1)  # decay
```

Called by `/reflect` Step 3.1 for entries that were decisive in the session.

## [available] listing

`hook.py`'s `_high_confidence_entries()` scans a collection for entries meeting the gate (`confidence > 0.9`, `access_count ≥ 3`, `boost_count ≥ 1`). By default this never runs automatically — it's part of the `session_start_verbose: true` opt-in (see `docs/hooks.md`); an agent can also ask for it explicitly. When it does run, only `id` + `title_of(text)` are shown, with a `mem_get(ids=[...])` hint — full text is never dumped.

Constants (in `hook.py`):
- `_HIGH_CONFIDENCE_THRESHOLD = 0.9`
- `_HIGH_CONFIDENCE_MIN_ACCESS = 3`
- `_HIGH_CONFIDENCE_MIN_BOOSTS = 1` (must have been explicitly boosted at least once via /reflect)
- `_HIGH_CONFIDENCE_MAX = 3` (max repo-scoped entries listed)
- `_HIGH_CONFIDENCE_GLOBAL_MAX = 2` (separate, smaller cap for the `global` collection's own listing)
