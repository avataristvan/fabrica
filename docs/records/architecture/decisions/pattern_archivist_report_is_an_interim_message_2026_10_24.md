id: pattern_archivist_report_is_an_interim_message_2026_10_24
type: pattern
topic: architecture
perspective: user
created: 1792868078.758435
edges: [{"target_id": "domain_archivist_integration_visible_to_navigator_2026_10_15", "edge_type": "related"}, {"target_id": "learning_call_prompt_does_not_beat_agent_template_2026_10_24", "edge_type": "related"}]
cue: I am changing agents/archivist.md or the format of the integration report the archivist hands back.
---

Rule: The archivist's integration report is an interim message to the caller: one line per candidate (target, new/update/supersede) plus the stale or not-written places, which are tasks for the caller. Lines that say "none" are left out; edges appear only as a count unless one contradicts; no path lists. The searched areas fit in one line.
When: The archivist words its report; someone edits agents/archivist.md.
Why: In one hw-projekt-T session the archivist ran 5 times with reports of about 12 to 25 lines each. Only the target line and the hints to stale places counted ("handoff still lists the findings as open", "two old records still say X"). Full edge and back-reference lists, "none" lines and file paths were noise. The report must stay readable, since the Navigator is meant to see it (domain_archivist_integration_visible_to_navigator_2026_10_15).
Evidence: docs/sources/field_feedback_librarian_archivist_hw_project_2026_10_24.md (part 2, point 3; the agent's own estimate of the line counts).
