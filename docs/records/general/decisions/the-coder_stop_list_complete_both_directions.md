type: pattern
topic: general
perspective: the-coder
created: 1791666541.707247
---

Rule: Instructions for an unattended agent (UPGRADING.md, runbooks) name every STOP condition and say explicitly that everything else is decided and must not be second-guessed.
When: writing docs or prompts that an agent follows without a human, e.g. auto-updating installations.
Why: a fresh claude -p agent stopped on its own judgment over placements the doc did not list as a STOP (ai-mem chunk 0, 2026-10-10); an incomplete list fails in both directions.

## Edges

- related: [learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12](../../plugin/learnings/learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12.md)
- related: [domain_dev_team_stops_on_contradiction_blocked_2026_10_19](../../../../../../docs/records/architecture/decisions/domain_dev_team_stops_on_contradiction_blocked_2026_10_19.md)
