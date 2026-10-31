id: learning_chunk0_upgrade_acceptance_passed_2026_10_15
type: learning
area: plugin
perspective: agent
created: 1792061619.972849
edges: [{"target_id": "learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12", "edge_type": "confirms"}, {"target_id": "domain_rebuild_closing_scoped_to_two_todos_2026_10_15", "edge_type": "related"}, {"target_id": "domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31", "edge_type": "related"}]
cue: You are asked whether UPGRADING.md works for an unattended agent, or you are about to ship the next breaking upgrade step.
---

Observed: The chunk 0 upgrade acceptance ran on 2026-10-15 against code d5b73b1 (scripts/upgrade_acceptance/run.sh, BASE_PY = pyenv 3.13.11, fresh claude -p agents for B and C) and passed: ACCEPTANCE: PASS, all 19 checks green. A: dry run and apply with sentinel. Hook guard line with empty stderr. B: pulled, migrated, no chromadb, workspaces and reports equal to A. C: on the diverged checkout stopped without merge, rebase or migration. Real-data checksums identical.
Cause: UPGRADING.md is followable by an unattended agent as written; the run is the proof. Rerun it before the next breaking upgrade step and after every UPGRADING.md edit.
Evidence: commit d5b73b1; log kept local in the session scratchpad; learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12.
