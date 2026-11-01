id: arch_decision_push_vs_pull_2026_07_31
type: domain
topic: architecture
perspective: agent
created: 1785508569.588063
edges: [{"target_id": "learning_gap_test_first_run_and_blindtest_2026_07_31", "edge_type": "derived_from"}, {"target_id": "arch_critique_push_vs_pull_synthesis_2026_07_31", "edge_type": "derived_from"}]
cue: Asked why push was replaced by pull, or whether to push memory content into a session again
---


# Push-vs-pull architecture: decision (2026-07-31)

Synthesis of arch_critique_push_vs_pull_synthesis_2026_07_31, arch_redesign_sketch_pull_based_2026_07_31 (now docs/sources/arch_redesign_sketch_pull_based_2026_07_31.md), arch_critique_opus_quantified_costs_2026_07_31 (figures from it are now documented in ai-mem/CLAUDE.md's Critical Invariants -- the entry itself was deleted 2026-09-12, superseded by the daemon/embedding-cache fixes of 2026-08-23), pattern_gap_test_evaluation. Resolves todo_push_vs_pull_architecture_decision.

## Decision
Opus' point 1 (delete userprompt_hook completely, now) is REJECTED. Rationale: the blind test is the decisive evidence and speaks against it -- a very thorough purely-pull agent reconstructed accurate answers about LATER design refinements, but never reached the original, non-derivable design motivation -- without any signal of incompleteness. Exactly the entries that are worth the most (deep, not obvious, no keyword hook in the current prompt) are the ones an agent would never ask for on its own initiative. Deleting push before proof that pull covers this gap is the wrong order. It is also premature: today's threshold recalibration (0.62/0.58) has not yet been measured on real sessions -- a decision based on the old (pre-fix) cost figures would repeat the very mistake the Opus report itself criticises (never measured benefit).

## Implementation order -- status 2026-07-31 end of session, updated 2026-09-13
1. DONE -- cache embedding model + BM25 index: background query daemon, commit 4ebef7f (chunk1_daemon_shipped_2026_07_31).
2. DONE -- [available]-style title+ID lists + mem_topics(collection): commit 4ebef7f, bundled with item 1. Result: SessionStart's [always-present] gate was renamed [available] (hook.py) and renders `id: title` instead of a ~300-character text dump plus a mem_get hint; the same rebuild in the (meanwhile removed) userprompt_hook block, where [warnings]/[dilemmas] deliberately stayed full text (action-triggered, low-volume, readable without an additional mem_get round trip). The new MCP tool mem_topics(collection) completes the pull ladder mem_list -> mem_topics -> mem_get. Answers Opus' cost criticism (~5,350 tokens/session) without losing the serendipity shown in the blind test. (Formerly its own entry chunk2_available_format_mem_topics_shipped_2026_07_31, merged in here.)
3. DONE -- make access_count meaningful: commit 4be5ae8 (chunk3_access_count_semantics_shipped_2026_07_31).
4. DONE -- BM25 residual bug: commit 4ebef7f, same session as items 1+2 (bm25_saturating_transform_2026_07_31).
5. SUPERSEDED 2026-09-12 -- was: 'PreToolUse as the only action-triggered push point (commit baa09db)'. PreToolUse was removed completely, not just kept (arch_decision_pretool_push_removed_2026_09_12).
6. **RESOLVED 2026-09-13, but NOT as planned.** The planned pull-through-rate analysis (see pull_through_measurement_impl_2026_07_31, now docs/sources/pull_through_measurement_impl_2026_07_31.md) was never carried out -- instead userprompt_hook was removed completely, triggered by an entirely independent incident (the user tried to disable ai-mem's 'auto-inject', found that no configuration level had ever had that effect, and identified UserPromptSubmit as the source of 'actions on every chat' -- see arch_decision_userprompt_push_removed_2026_09_13). The original question ('keep or remove, based on pull-through rate') is thereby obsolete, not answered -- injection_log.py's data (281 entries) will never be evaluated, the log is frozen (record_pushed's only caller, userprompt_hook.py, no longer runs).
7. UNBLOCKED 2026-09-13 -- todo_confidence_decay_adsr_design can now be tackled, since item 6 is no longer open (resolved, albeit differently than planned).

See also: arch_critique_push_vs_pull_synthesis_2026_07_31, pattern_gap_test_evaluation, todo_confidence_decay_adsr_design, chunk1_daemon_shipped_2026_07_31, chunk3_access_count_semantics_shipped_2026_07_31, bm25_saturating_transform_2026_07_31, arch_decision_pretool_push_removed_2026_09_12, arch_decision_userprompt_push_removed_2026_09_13.

Evidence: docs/sources/arch_redesign_sketch_pull_based_2026_07_31.md (the seven-point pull redesign; points 2-6 adopted, 1 and 5 later reversed; pull ladder list -> list(collection) -> get(ids)); docs/sources/pull_through_measurement_impl_2026_07_31.md (a push outcome needs a log joined to later access; the measurement infrastructure died with userprompt_hook).
