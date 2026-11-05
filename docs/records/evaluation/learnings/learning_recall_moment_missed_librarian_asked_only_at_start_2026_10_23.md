type: learning
topic: evaluation
perspective: agent
created: 1792789845.565192
cue: I am about to run a risky tool or write straight to hardware or state, and wonder whether the librarian was asked at the right moment.
---

Observed: In an audio-driver session the librarian was asked only at session start. The moment its knowledge mattered came later, when the agent decided to write straight into mixer registers with memtool; a memtool learning existed but was never retrieved because the agent had not asked about it. The CLAUDE.md rule "ask at direction changes" existed and did not fire.
Cause: The rule depends on the agent recognising the moment itself, the same failure as a category-named trigger ([learning_trigger_must_name_observable_moment_2026_10_10](../../architecture/learnings/learning_trigger_must_name_observable_moment_2026_10_10.md)). Another rule of this kind would probably fail the same way. Scope: recall timing, not the quality of the librarian's answer. The recall-moment problem is open, not solved (see [domain_no_hardcoded_keyword_pretool_hook_recall_moment_open_2026_10_23](../../architecture/decisions/domain_no_hardcoded_keyword_pretool_hook_recall_moment_open_2026_10_23.md)).
Evidence: docs/sources/librarian_recall_moment_audio_session_2026_10_23.md (the agent's own correction and analysis). The companion source docs/sources/librarian_value_audio_session_2026_10_23.md is confabulated by the agent's own account and is no evidence for this learning.

## Edges

- confirms: [learning_trigger_must_name_observable_moment_2026_10_10](../../architecture/learnings/learning_trigger_must_name_observable_moment_2026_10_10.md)
- related: [eval_pull_gap_test_2026_09_20](eval_pull_gap_test_2026_09_20.md)
- related: [learning_knowledge_loses_against_the_order_2026_10_18](learning_knowledge_loses_against_the_order_2026_10_18.md)
- related: [eval_librarian_2026_09_26](eval_librarian_2026_09_26.md)
- related: [learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31](../../workflow/learnings/learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31.md)
- related: [pattern_pre_action_rules_go_to_claude_md_cue_names_the_moment_2026_11_05](../../workflow/decisions/pattern_pre_action_rules_go_to_claude_md_cue_names_the_moment_2026_11_05.md)
