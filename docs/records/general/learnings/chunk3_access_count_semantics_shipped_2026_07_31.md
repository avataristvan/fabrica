id: chunk3_access_count_semantics_shipped_2026_07_31
type: learning
area: general
created: 1785512083.147452
superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26
valid_until: 1790699174.460505
---

# Push-vs-Pull Chunk 3 shipped: access_count means deliberate use (2026-07-31)

Implements item 3 of arch_decision_push_vs_pull_2026_07_31's rollout order. Committed as 4be5ae8. Files changed: ai_mem/application/query_memory.py, get_memory.py, boost_confidence.py, ai_mem/server.py; tests/application/test_query_memory.py, test_boost_confidence.py (modified); tests/application/test_get_memory.py (new). Also fixed a pre-existing test race in tests/test_daemon.py/test_daemon_client.py's _wait_for_socket helper (polled for socket-file existence, not actual daemon readiness -- flaked under full-suite load; now polls a real ping until it succeeds).

## What changed
QueryMemoryUseCase.execute() used to track_access on EVERY returned result by default (min_score_for_tracking=None meant 'track everything', not 'track nothing') -- since userprompt_hook/pretool_hook query on nearly every turn with no threshold, this made the [available] gate's access_count>=3 clause nearly meaningless (Opus's live measurement: excluded only ~9% of global candidates, self-reinforcing since querying is what bumped the counter the gate itself gates on -- see arch_critique_opus_quantified_costs_2026_07_31). Flipped: no tracking happens unless the caller explicitly passes min_score_for_tracking (posttool_hook's real usage signal, unaffected by this change). Two new deliberate-use signals added: GetMemoryUseCase gained an optional track_access param, wired in server.py's mem_get (deliberate retrieval by id -- now the natural next action after seeing a chunk-2 [available] title+id listing) but deliberately left unwired in hook.py's SessionStart current_focus lookup (automatic plumbing, not an agent's deliberate choice). BoostConfidenceUseCase gained the same optional param, bumping access_count only on a positive boost (mem_boost delta>0 -- the /reflect Step 3.1 citation signal already existed, just never touched access_count before); a decay does not count as usage. Both params default to None so untouched call sites keep working.

Verified against the real production DB (repo.ai-mem's current_focus entry): plain mem_query left access_count unchanged (179->179), mem_get bumped it by exactly 1 (179->180).

CLAUDE.md's Critical Invariants updated: renamed [always-present] references to [available] (stale from chunk 2, not updated at the time), added the access_count semantics change as its own bullet.

343 tests passing (full suite, confirmed clean across 2 consecutive full runs after fixing the daemon test race).

## Next in the rollout
Item 6 (userprompt_hook's fate) is still deferred -- the data-gathering step for it shipped 2026-07-31 as a separate piece of work, see pull_through_measurement_impl_2026_07_31 (commits b13d4d0, fddfa9d). The actual keep/remove decision itself still requires real post-fix usage data to accumulate, and has not been made. Item 7 (confidence-decay/ADSR, todo_confidence_decay_adsr_design) starts only after that decision.

See also: arch_decision_push_vs_pull_2026_07_31, chunk1_daemon_shipped_2026_07_31, pull_through_measurement_impl_2026_07_31.