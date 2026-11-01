id: domain_current_docs_may_carry_one_short_history_section_2026_10_12
type: domain
topic: architecture
perspective: user
created: 1791839311.376888
edges: [{"target_id": "domain_current_docs_hold_history_in_one_upgrade_section_2026_10_12", "edge_type": "supersedes"}, {"target_id": "domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31", "edge_type": "related"}]
cue: Writing or reviewing a current doc that touches a retired system, and about to flag or remove its history section
---

Decision: A current doc (reference, how-to, explanation) may carry one short history section (for example "Retired hooks", "History: collections", "What was left behind"). It says what existed, why it was dropped, and links the evidence in docs/sources/ or records and UPGRADING.md for the steps. Step-by-step upgrade instructions live only in UPGRADING.md. The docs are widened, not trimmed.
Why: The user (2026-10-12): the section is the "why" and carries part of the experience; a reader who meets an old artifact (for example a stale PreToolUse entry) learns on the spot why it is gone. The earlier rule (history only in README "Upgrading from the earlier versions") would have removed that.
Scope: Current documentation (docs/reference, docs/how-to, docs/explanation). A reviewer does not flag such a section as a rule violation. Evidence: docs/reference/hooks.md "Retired hooks", docs/explanation/areas-and-kinds.md "History: collections", docs/explanation/organisational-memory.md "What was left behind"; mem doctor's retired-system check does not flag them. docs/how-to/migrate-to-records.md has no history heading, nothing to trim; no code change.

Narrowed 2026-10-31 (in effect since 3c64e27, pushed), not superseded: the sentences about UPGRADING.md ("and UPGRADING.md for the steps", "Step-by-step upgrade instructions live only in UPGRADING.md") are replaced by domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31: UPGRADING.md is gone and the steps live in tag v1-last-upgrade-path, named in the README. The rule itself (one short history section in a current doc, widened not trimmed) still holds, so the record stays active.
