type: learning
topic: plugin
perspective: the-coder
created: 1791838321.007471
cue: I am editing UPGRADING.md or any other document an unattended agent follows
---

Observed: Rerun the UPGRADING.md acceptance run after every edit to UPGRADING.md. One leftover "not yet released" sentence made agent B stop after part 1; one mention of `claude mcp list` made it create `.claude` state in its workspace, which failed the diff A/ws vs B/ws.
Cause: An agent follows the document literally, so a single stale sentence or an unrelated command is read as an instruction or a stop reason; reading the text does not reveal this.
Evidence: scripts/upgrade_acceptance/run.sh, UPGRADING.md.

Historical since 3c64e27 (2026-10-31): UPGRADING.md and the acceptance run are removed from main; they live at tag v1-last-upgrade-path. The general point (an agent follows a document literally) stands for any document an unattended agent follows.

## Edges

- related: [the-coder_stop_list_complete_both_directions](../../general/decisions/the-coder_stop_list_complete_both_directions.md)
- related: [learning_chunk0_upgrade_acceptance_passed_2026_10_15](learning_chunk0_upgrade_acceptance_passed_2026_10_15.md)
- related: [pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18](../../architecture/decisions/pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18.md)
- related: [domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31](../../architecture/decisions/domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31.md)
