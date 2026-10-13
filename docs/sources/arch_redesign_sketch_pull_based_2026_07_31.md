---
type: design-doc
date: 2026-07-31
origin: memory entry arch_redesign_sketch_pull_based_2026_07_31, exported to docs/reference/ on 2026-10-04
status: processed
---
> Translated from the German original on 2026-10-13; content unchanged.

## What the source says

Status addendum (2026-09-29): Two statements in the status block below were later reversed -- point 1 (delete userprompt_hook), noted here as REJECTED, was implemented after all on 2026-09-13 (arch_decision_userprompt_push_removed_2026_09_13); point 5 (keep PreToolUse) was dropped on 2026-09-12, PreToolUse removed entirely (arch_decision_pretool_push_removed_2026_09_12). Points 2-4 and 6 remain valid. chunk2_available_format_mem_topics_shipped_2026_07_31 has been merged into arch_decision_push_vs_pull_2026_07_31.

# Concrete pull-based redesign proposal (Opus, 2026-07-31) -- reference, decision already made

Starting point: the pull ladder already exists in server.py (mem_list -> collections+counts, mem_list(collection) -> {id,title} pairs, mem_get(ids) -> full text without ranking) -- analogous to an existing MCP pattern (list_tool_categories -> list_tools_in_category -> get_tool_signature). Push was built ON TOP OF an already working pull system, not instead of a missing one.

## Proposal (7 points, unchanged from the original report)
1. Delete the `userprompt_hook` injection entirely (not just tune it) -- reason: the judge (an isolated prompt string without task context) is structurally worse informed than the agent itself, and the scoring gate was demonstrably ineffective (see l2/BM25 bug, now fixed).
2. Keep SessionStart, but shrink it to an index, not content -- current_focus + git commits + collection names + title index, not entry bodies.
3. Replace `[always-present]` with `[available]` -- show only titles+IDs, `mem_get` is one cheap call away if needed.
4. Add `mem_topics(collection)` -- the missing `list_tools_in_category` rung; cluster/tag titles so that even a 300-entry collection stays browsable.
5. Keep PreToolUse, but fix it and justify it as the only action-triggered push point -- the trigger is a concrete action (file X is being edited), not a vague prompt string.
6. Fix scoring independently of the architecture decision (l2/cosine, BM25 residual bug).
7. Either make `access_count` meaningful (only count up when the agent deliberately `mem_get`s by ID or cites in /reflect) or drop it.

## Sonnet's reservation about this proposal
Do not adopt 1:1 without taking the blind-test result into account (see pattern_gap_test_evaluation) -- the blind test showed a more nuanced picture than 'pull always beats push'. Recommendation: implement step by step, not as one big rewrite.

## Status (2026-07-31, end of session)
The decision has been made (see arch_decision_push_vs_pull_2026_07_31): points 2-6 were adopted and implemented (chunk1_daemon_shipped_2026_07_31, chunk2_available_format_mem_topics_shipped_2026_07_31, chunk3_access_count_semantics_shipped_2026_07_31, bm25_saturating_transform_final_2026_07_31). Point 1 (delete userprompt_hook entirely) was REJECTED -- the blind test argued against it. This entry is a historical reference for Opus' original proposal, no longer an open work item.

## Our notes

