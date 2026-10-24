id: learning_agent_selfreport_about_subagent_output_can_be_confabulated_2026_10_23
type: learning
area: evaluation
perspective: agent
created: 1792789845.875828
edges: [{"target_id": "learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23", "edge_type": "related"}, {"target_id": "pattern_ask_selfreport_with_provenance_marks_2026_10_24", "edge_type": "related"}]
cue: I am judging what a subagent said from the calling agent's own assessment of it, without the transcript.
---

Observed: A coding agent, asked in a /btw how valuable the librarian's message was, described contents (DISPAUD_CFG, a dev-team split, PLL1 from BCLK1) that were not in the librarian's message. It admitted this itself in the next answer; the real message covered roughness, loopback and devsh/flashing.
Cause: A self-report about a subagent's output is generated, not retrieved, and can be confabulated. Without the transcript it is not evidence of what the subagent said; readings built on it are void (here, a correction candidate against an RT5659 PLL1 record was dropped for that reason).
Evidence: docs/sources/librarian_value_audio_session_2026_10_23.md (the confabulated report), docs/sources/librarian_recall_moment_audio_session_2026_10_23.md (the correction).
