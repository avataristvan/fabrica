type: domain
topic: architecture
perspective: agent
created: 1792757456.502053
cue: You are making mem doctor Wiring flag teams without handoff-protocol and a tool-installed skill like graphify keeps showing up as a miss.
---

Decision: mem doctor lists skills installed by a tool (folder with .git, VERSION or .*_version) apart as external, not as teams missing the handoff-protocol line.
Why: external skills are never edited ([domain_agents_learn_environment_never_edit_external_2026_10_11](domain_agents_learn_environment_never_edit_external_2026_10_11.md)), so flagging them as missing was a permanent spurious hit (graphify). Listing them apart keeps them visible (flag, not hide, cf. [domain_superseded_flag_not_hide_2026_09_20](domain_superseded_flag_not_hide_2026_09_20.md)) without an exemption list.
Scope: ai_mem/doctor.py collect_wiring/_is_external; refines "no exemption list" in the Wiring check. Evidence: tests/test_doctor.py test_wiring_lists_external_skills_apart; 616/616 passing 2026-10-23.

## Edges

- derived_from: [domain_agents_learn_environment_never_edit_external_2026_10_11](domain_agents_learn_environment_never_edit_external_2026_10_11.md)
- related: [domain_superseded_flag_not_hide_2026_09_20](domain_superseded_flag_not_hide_2026_09_20.md)
