# What we measured

> An experience report, as of 2026-10-31. Fabrica claims that agents grow more senior when the record they inherit gets better. This page says what was measured on the way, including what did not hold. Every number links to the record that carries it, with its method and limits.

## In short

- **Pushing memory into prompts cost a lot and was retired.** Measured, not argued.
- **Agents do not look things up on their own.** In every measurement so far, an agent read the record only when something pointed it there.
- **A librarian finds more than a similarity score does**, when it is asked. That is why it is on probation, not proven.
- **Reading the reason is not enough.** Agents that read why a design was rejected often built it anyway.
- **The central claim is not confirmed.** A preregistered measurement of "seniority lives in the record" did not reach probation. The pattern stays a hypothesis.

No Fabrica pattern is proven. The [status scale](../fabrica/patterns/README.md#status) keeps its empty top level on purpose.

## 1. Push into every prompt: retired

Earlier versions injected relevant memory before every file edit and on every user prompt. A scan over 50 sessions counted 348 edits that injected about 67.6k tokens, about 92% of ai-mem's whole context footprint, whether the content was relevant or not. Both push points were removed in September 2026; what is left is a short routing hint at session start.

Records: [`learning_pretool_push_dominated_context_footprint_2026_09_12`](../records/architecture/learnings/learning_pretool_push_dominated_context_footprint_2026_09_12.md), [`arch_decision_pretool_push_removed_2026_09_12`](../records/architecture/decisions/arch_decision_pretool_push_removed_2026_09_12.md), [`arch_decision_userprompt_push_removed_2026_09_13`](../records/architecture/decisions/arch_decision_userprompt_push_removed_2026_09_13.md).

## 2. The pull gap: agents do not ask

If nothing is pushed, the agent has to pull. A gap test (2026-09-20) posed 7 questions whose answers existed only in memory, plus 2 controls whose answers existed nowhere, to fresh agents with memory tools available. In all 7 gap cases the agent made **no** memory query. It searched memory only in the controls, after the repo search had found nothing. What worked was an id written into CLAUDE.md, not search.

The seniority measurement (section 5) confirmed it a month later: with every record available in the repo, the agent read `docs/records/` in 11 of 24 runs.

The cause both records name: no trigger makes an agent look when code or docs offer a plausible substitute answer. The ranking is not the problem; the moment is.

Records: [`eval_pull_gap_test_2026_09_20`](../records/evaluation/learnings/eval_pull_gap_test_2026_09_20.md), [`eval_seniority_available_not_used_confirms_pull_gap_2026_10_18`](../records/evaluation/learnings/eval_seniority_available_not_used_confirms_pull_gap_2026_10_18.md).

Limits: 7 cases, one model, one run per arm, questions written by an agent that knew the entries. A direction, not a percentage.

## 3. The librarian: better when asked, on probation

The librarian is a cheap read-only agent that answers from the record by judgment over a catalogue instead of a similarity score. On the gap cases it solved 5 of 6 (plain retrieval: 2 of 6) and answered both controls correctly with "Not documented". A rerun with the registered agent type solved 4 of 6.

Both numbers may be inflated: the eval files with case and gold ids sat in the records the librarian could read. That is recorded, and the eval artifacts have to move before any rerun. And the measurement says what the librarian finds *when asked*, not whether anyone asks. That is why the core gives it fixed call points at the boundaries of the work.

Records: [`eval_librarian_2026_09_26`](../records/evaluation/learnings/eval_librarian_2026_09_26.md), [`eval_librarian_rerun_records_layout_2026_09_29`](../records/evaluation/learnings/eval_librarian_rerun_records_layout_2026_09_29.md), [`domain_drop_confidence_for_evidence_and_librarian_2026_09_26`](../records/architecture/decisions/domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md).

## 4. The archivist: acceptance failed, carried by use

The archivist integrates new knowledge into the record and sets the links. Its acceptance test asked for at least 80% of 33 hand-set links, 4 of 4 predecessors across areas and a flagged duplicate. The last run reached 11 of 33 links, 0 of 4 predecessors, and did not flag the duplicate. The test was closed as **failed** and not rerun, partly because the fixture no longer matched the records, partly because the scoring counted link direction strictly.

It is accepted on real use instead: passes over about 245 records that stayed lint clean. That is weaker evidence than a passed test, and the record says so.

Record: [`domain_archivist_acceptance_closed_fail_use_carries_2026_10_13`](../records/evaluation/decisions/domain_archivist_acceptance_closed_fail_use_carries_2026_10_13.md).

## 5. Seniority lives in the record: not confirmed

The central claim got a preregistered measurement ([the plan](../plan_seniority_measurement.md), frozen by hash before the first run; a bad result forbids a v2). Six tasks each ask an agent to build something the record says was tried and rejected; a senior agent stops and names the reason. Two control tasks should simply be done. Four arms, each a fresh copy of the repo:

| Arm | Gets | Dead ends avoided per repeat (of 6) |
|---|---|---|
| A0 | code and tests only (the junior) | 1 · 1 · 3 |
| A1 | A0 + decisions only (ADR practice) | 3 · 3 · 3 |
| A2 | A0 + the whole record (Fabrica) | 2 · 2 · 4 |
| A3 | A2 + the librarian plugin | 4 · 4 · 5 (confounded, see below) |

The bar for probation was: A2 avoids at least 5 of 6 in every repeat, A0 at most 2, and A2 does both controls. A2 never reached 5. The whole record did not beat decisions alone. 96 runs, blind grading, a 20-item spot check that held.

Three things stood out:

- **Knowledge loses against the order.** Where the record was read, the agent often built the rejected thing anyway and flagged the conflict afterwards. In one task the agent read the reason in every repeat and still built it. The obstacle is not missing knowledge; it is an agent that has to withstand an instruction.
- **A duty written as a learning is never done.** One task required rerunning an acceptance test after an edit; the duty was in a learning. No arm did it, ever. Duties belong in mechanisms that enforce them, not in text.
- **A3 is not interpretable.** It loaded the repo under test as a plugin, and Claude Code blocks edits to a loaded plugin, so A3 stalled on edit tasks, including both controls. It was reported, never counted.

Records: [`eval_seniority_main_run_result_2026_10_18`](../records/evaluation/learnings/eval_seniority_main_run_result_2026_10_18.md), [`learning_knowledge_loses_against_the_order_2026_10_18`](../records/evaluation/learnings/learning_knowledge_loses_against_the_order_2026_10_18.md), [`pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18`](../records/architecture/decisions/pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18.md), [`anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18`](../records/evaluation/decisions/anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18.md).

## 6. From the field: self-reports and one observed case

In a hardware-driver project outside this repo, agents reported on their own use. The state files (focus and handoff) helped most when resuming work. The librarian added most where a record stated a limit: a list of options already tried and rejected kept the change small. In another session the librarian was asked only at the start, and the moment its knowledge mattered came later, unasked.

These are self-reports, not measurements. One of them was later shown by the same agent to be partly confabulated; the records say which.

Records: [`learning_field_use_handoff_files_helped_most_librarian_scope_2026_10_24`](../records/evaluation/learnings/learning_field_use_handoff_files_helped_most_librarian_scope_2026_10_24.md), [`learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23`](../records/evaluation/learnings/learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23.md).

**A recorded reason stopped a destructive change (2026-10-31).** A briefing written in another session said the plugin had a single user, so the code that upgrades old installations could go. A record said otherwise: an external installation updates itself from `main` and may not have migrated yet. The librarian named that record at the start of the cleanup session. It came up again when the coder that was given the removal asked the librarian at its chunk start; the coder stopped, reverted and reported `blocked`. The removal went ahead only after the last version that still carries the upgrade path was tagged.

What this shows is narrower than it looks. It is one case with no run without records to compare against. The two catches share the same records, the same librarian and the same rule that calls it, so they are one mechanism working twice, not two independent results. The net had holes: the coder had started editing before the librarian's answer came back, and a separate worktree, not the record, kept that harmless. And the wrong premise came from a handoff, itself a Fabrica practice. What it does show: the person who knew about the external installation had left it out of the briefing, and the record had not. It fits the pull gap above: knowledge came in at a fixed call point and nowhere else.

Records: [`learning_recall_at_boundaries_stopped_a_destructive_change_across_sessions_2026_10_31`](../records/architecture/learnings/learning_recall_at_boundaries_stopped_a_destructive_change_across_sessions_2026_10_31.md), [`learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31`](../records/workflow/learnings/learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31.md), [`domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31`](../records/architecture/decisions/domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31.md).

## What follows from it

- **The recall moment is the open problem.** Neither push nor a rule like "ask before a direction decision" reliably brings knowledge to the moment it matters. Fixed call points at boundaries help where they exist; between them the gap is open.
- **Knowing is not objecting.** Even an agent that has the reason needs something that lets it stop. The dev team this repository was built with now stops and reports `blocked` when the librarian names a record the work would reverse; it was seen live once (section 6), not yet tested.
- **Duties go into mechanisms.** What must happen is enforced by a hook or a check, not written down as a lesson.
- **What carries Fabrica today is its practice, not a proven effect.** The record has made this project's own history legible: every number on this page can be traced, including the ones against it.
