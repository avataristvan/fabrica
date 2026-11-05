type: pattern
topic: evaluation
created: 1790700225.163243
---

Rule: Eval cases, gold IDs and discriminators are not stored where the tested agent can read (only scripts/eval_pull/, and that is moved out of the repo during runs). Eval results are recorded as records without case text and gold IDs.
When: Before eval learnings are persisted as records, and before every librarian or gap-test run.
Why: In the re-test [eval_librarian_rerun_records_layout_2026_09_29](../learnings/eval_librarian_rerun_records_layout_2026_09_29.md), [eval_librarian_2026_09_26](../learnings/eval_librarian_2026_09_26.md) and [eval_pull_gap_test_2026_09_20](../learnings/eval_pull_gap_test_2026_09_20.md) lay as files under docs/records/evaluation/learnings/ with case and gold IDs and were readable for the librarian -- the result (4/6, likewise 5/6 from 2026-09-26) may be inflated.
Proposal for runs (not yet implemented, no tooling): temporarily move docs/records/evaluation/ out of the repo during the run, or instruct the librarian to skip the evaluation area. Existing eval records are not rewritten -- the history stays.

Note 2026-10-04: The leak is the path docs/records/evaluation/ inside the corpus the librarian reads, not git tracking -- gitignoring the records does not hide them from it.

## Edges

- derived_from: [eval_librarian_rerun_records_layout_2026_09_29](../learnings/eval_librarian_rerun_records_layout_2026_09_29.md)
- related: [pattern_gap_test_evaluation](pattern_gap_test_evaluation.md)
