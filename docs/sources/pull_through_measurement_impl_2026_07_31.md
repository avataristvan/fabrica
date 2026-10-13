---
type: measurement
date: 2026-07-31
origin: memory entry pull_through_measurement_impl_2026_07_31, exported to docs/reference/ on 2026-10-04
status: processed
---
> Translated from the German original on 2026-10-13; content unchanged.

## What the source says

# Pull-through measurement implemented (2026-07-31)

Implementation of the data-collection step from arch_decision_push_vs_pull_2026_07_31, point 6 (the fate of userprompt_hook is decided only after real usage data, not guessed). Committed as b13d4d0 (main implementation) + fddfa9d (fix: the session_stats.json path was also affected by the class of bug described in the gotcha below, corrected in the same go).

## Mechanics
- New module `ai_mem/injection_log.py`: `record_pushed(log_path, collection, ids)` logs every ID pushed by userprompt_hook per collection ({DB_PATH}/injection_log.json, JSON {id, ts}, capped 500/collection).
- `userprompt_hook.py` calls record_pushed for all three blocks (dilemmas, warnings, available) -- the collection assignment follows the existing coll variable per result.
- `dream_memory._pull_through_report(entries, log_path)`: matches the log against `last_accessed_at` of each entry -- pulled = last_accessed_at > push_ts. Deleted entries (no longer resolvable) are excluded from both numerator AND denominator, not counted as 'not pulled' -- the log cannot tell 'never used' from 'no longer determinable'.
- Rendered as its own report section in mem-dream (analogous to _confidence_report), activated via `DreamMemoryUseCase(repo, injection_log_path=...)` in dream_cli.py.

## Why no live counter
The first idea was a rolling counter analogous to session_stats.py, incremented on every track_access event. Rejected: the outcome of a push event ('was pulled later') is not yet known at push time -- a live counter can only record true hits, never the absence. So: a log of the push events + a report that later (on every mem-dream run) matches against last_accessed_at, instead of instrumentation at the three TrackAccessUseCase construction sites (server.py, daemon.py, _hook_deps.py). Generalised as pattern_delayed_outcome_needs_log_not_counter in global.

## Gotcha while building
A module-level constant `X = DB_PATH / "..."` in a hook cannot be patched in tests -- `patch.object(hook, "DB_PATH", tmp_path)` only affects code that looks up the name DB_PATH at runtime, not a separate constant already computed at import. Fix: compute the path inline in main(), do not hoist it into a module constant. `_STATS_PATH` in userprompt_hook.py had the same bug -- fixed in the same PR (fddfa9d).

## Status (final, 2026-09-13) -- the infrastructure is now DEAD
The log stayed frozen at 281 push events across 5 collections (global:184, repo.ai-mem:30, repo.project-a:7, repo.workspace:17, repo.project-b:43) -- and will not grow any more: record_pushed's only caller was userprompt_hook.py, which was removed entirely on 2026-09-13 (arch_decision_userprompt_push_removed_2026_09_13). The planned pull-through-rate evaluation (arch_decision_push_vs_pull_2026_07_31 point 6) was NEVER carried out -- the question this infrastructure was meant to answer was resolved instead by an independent incident (userprompt_hook simply removed entirely, for a different reason). `injection_log.py`, `_pull_through_report` and this module remain in the code, but are now dead infrastructure answering a question nobody asks any more.

## Our notes

