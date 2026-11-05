type: learning
topic: evaluation
perspective: agent
created: 1792868079.086224
cue: I am judging how much the librarian helps compared with FOCUS.md and handoff files, or whether a failed attempt deserves its own record.
---

Observed: In hw-projekt-T, resuming on "weiter", FOCUS.md and the handoff gave the largest benefit (several test rounds saved). The librarian was asked twice: two correct "Not documented" answers, and "upstream is not tracked" carried a scope decision. In the later audio-driver sessions of the same project (2026-10-23, 2026-10-24) the agent again said most of the librarian's answer was already in FOCUS.md and the handoff (the 10-23 report was later shown to be partly confabulated). What the librarian added beyond the state files was a boundary: a project learning lists seven registers as "tested and NOT sufficient alone", the librarian handed that list over, and the agent named it the most valuable part ("kept the driver small"). The list exists in the project's records (checked there); its benefit is the agent's self-report only. Cost of the call: 45 tool calls, about 75 s.
Cause: State files say what to do next; the librarian answers why and whether something exists, and is strongest where a record states a limit (rejected, open, "Not documented"). Hypothesis from the self-reports, not tested: a failed attempt recorded as a list of rejected options is retrieved well and saves work, which speaks for giving such a Tried: / Failed because: its own record.
Evidence: docs/sources/field_feedback_librarian_archivist_hw_project_2026_10_24.md (part 1; self-report, see the caveat there); docs/sources/librarian_value_after_clear_audio_session_2026_10_24.md (self-report after /clear; the same agent withdrew two earlier answers there). The librarian also repeated an unchecked cause correctly, see [pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24](../../architecture/decisions/pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24.md).

## Edges

- confirms: [eval_librarian_2026_09_26](eval_librarian_2026_09_26.md)
- related: [pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24](../../architecture/decisions/pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24.md)
- related: [learning_librarian_complete_on_citations_weak_on_completeness_2026_11_05](learning_librarian_complete_on_citations_weak_on_completeness_2026_11_05.md)
