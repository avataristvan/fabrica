type: learning
topic: evaluation
perspective: agent
created: 1792876752.530407
cue: I rely on the librarian prompt alone to keep it inside its permitted read scope.
---

Observed: In the session of 2026-10-24 the librarian ran one Grep into docs/fabrica/, outside its permitted read scope, and reported it itself.
Cause: Scope is enforced only by the prompt; the same pattern as the earlier out-of-scope reads.
Evidence: [learning_librarian_matched_out_of_scope_files_again_2026_10_12](learning_librarian_matched_out_of_scope_files_again_2026_10_12.md), [learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12](learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12.md); the librarian's self-report in that session.

## Edges

- confirms: [learning_librarian_matched_out_of_scope_files_again_2026_10_12](learning_librarian_matched_out_of_scope_files_again_2026_10_12.md)
