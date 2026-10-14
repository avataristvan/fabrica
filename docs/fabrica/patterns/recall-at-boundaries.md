# Recall at boundaries

**Status: probation**

## Problem

Knowledge pushed into every prompt drowns what matters. Knowledge left for the agent to look up never gets looked up.

## Forces

- Push costs context, whether it is relevant or not.
- Pull needs a trigger, and an agent has none of its own: it does not know what it does not know.

## Solution

Fixed points where the record is consulted: the start of a session, a chunk or a review. There, the Librarian answers from the record by judgment, and "not documented" is a valid answer. Between those points, nothing is pushed.

## Status

Probation. Push was measured and removed: over 50 sessions, the push before every edit was 92% of ai-mem's context footprint. Without a fixed call point, agents did not look anything up. The Librarian found 5 of 6 gap cases, then 4 of 6 in a rerun; each run had n=1, and the records flag that both numbers may be inflated.

## Evidence

- [`arch_decision_pretool_push_removed_2026_09_12`](../../records/architecture/decisions/arch_decision_pretool_push_removed_2026_09_12.md): the push measured and retired.
- [`eval_pull_gap_test_2026_09_20`](../../records/evaluation/learnings/eval_pull_gap_test_2026_09_20.md): agents did not query memory unless an id was in their context.
- [`eval_librarian_2026_09_26`](../../records/evaluation/learnings/eval_librarian_2026_09_26.md) and [`eval_librarian_rerun_records_layout_2026_09_29`](../../records/evaluation/learnings/eval_librarian_rerun_records_layout_2026_09_29.md): the Librarian against plain retrieval.
- [`learning_librarian_files_only_eval_chunk3_2026_10_11`](../../records/evaluation/learnings/learning_librarian_files_only_eval_chunk3_2026_10_11.md): a failed restriction, merged anyway; the doubts are named.

## Related practice

**Pull system** (Kanban): material moves when the next station needs it, not when the previous one has it.
