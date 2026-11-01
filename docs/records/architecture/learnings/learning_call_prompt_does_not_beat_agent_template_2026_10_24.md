id: learning_call_prompt_does_not_beat_agent_template_2026_10_24
type: learning
topic: architecture
perspective: agent
created: 1792868399.374574
edges: [{"target_id": "pattern_archivist_report_is_an_interim_message_2026_10_24", "edge_type": "related"}, {"target_id": "pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18", "edge_type": "related"}]
cue: I want to change an agent's output format and consider only saying so in the call prompt.
---

Observed: A request in the call prompt ("keep the report short") did not beat the report template in agents/archivist.md. The archivist still delivered "none" lines and full edge lists.
Cause: The agent file is the standing instruction; a one-off prompt request loses against it. Format duties belong in the agent file, not in the call.
Evidence: archivist run of 2026-10-24 in the ai-mem session; fix in agents/archivist.md (uncommitted); pattern_archivist_report_is_an_interim_message_2026_10_24.
