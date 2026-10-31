id: learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12
type: learning
area: plugin
perspective: the-coder
created: 1791838321.007471
edges: [{"target_id": "the-coder_stop_list_complete_both_directions", "edge_type": "related"}, {"target_id": "learning_chunk0_upgrade_acceptance_passed_2026_10_15", "edge_type": "related"}, {"target_id": "pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18", "edge_type": "related"}, {"target_id": "domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31", "edge_type": "related"}]
cue: I am editing UPGRADING.md or any other document an unattended agent follows
---

Observed: Rerun the UPGRADING.md acceptance run after every edit to UPGRADING.md. One leftover "not yet released" sentence made agent B stop after part 1; one mention of `claude mcp list` made it create `.claude` state in its workspace, which failed the diff A/ws vs B/ws.
Cause: An agent follows the document literally, so a single stale sentence or an unrelated command is read as an instruction or a stop reason; reading the text does not reveal this.
Evidence: scripts/upgrade_acceptance/run.sh, UPGRADING.md.

Historical since 3c64e27 (2026-10-31): UPGRADING.md and the acceptance run are removed from main; they live at tag v1-last-upgrade-path. The general point (an agent follows a document literally) stands for any document an unattended agent follows.
