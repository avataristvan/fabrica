# How Fabrica built itself

This repository was built the Fabrica way, so its own record is the best example of what the record is for. Nobody reads 296 records; this page follows four chains through them. Each one starts with something observed and ends with a decision. In each, the earlier state stays readable, and the reason it was given up is part of the record.

The links go to the record files themselves. Each file opens with its decision or observation, the reason, and the edges to the records it rests on.

## 1. Pushing memory into prompts, measured and retired

The first versions injected memory automatically: search results before every edit and every prompt.

- **Observed:** a scan over 50 sessions found 348 edits had injected about 67k tokens, about 92% of the plugin's whole context footprint, relevant or not ([`learning_pretool_push_dominated_context_footprint_2026_09_12`](../records/architecture/learnings/learning_pretool_push_dominated_context_footprint_2026_09_12.md)).
- **Decided:** the push before edits was removed, even though an earlier decision had kept it on purpose. The record names that tension and says why the new measurement outweighed it ([`arch_decision_pretool_push_removed_2026_09_12`](../records/architecture/decisions/arch_decision_pretool_push_removed_2026_09_12.md), against [`arch_decision_push_vs_pull_2026_07_31`](../records/architecture/decisions/arch_decision_push_vs_pull_2026_07_31.md)).
- **Observed next:** pull does not work on its own. In a gap test, agents never queried the memory unless something in their context pointed at it ([`eval_pull_gap_test_2026_09_20`](../records/evaluation/learnings/eval_pull_gap_test_2026_09_20.md)).
- **Decided:** a librarian agent is asked at fixed points, and the session start carries a pointer instead of content. The record also names its open risk ([`domain_librarian_replaces_experience_index_2026_10_04`](../records/architecture/decisions/domain_librarian_replaces_experience_index_2026_10_04.md)).

## 2. Scores replaced by judgment

Records once carried a confidence number that rose with use.

- **Decided as a direction:** signals that protect or retire a record come from judgments, not from counters. Ranking by frequency entrenches whatever fired often, whether or not it was right ([`domain_direction_judgment_over_scores_2026_09_20`](../records/architecture/decisions/domain_direction_judgment_over_scores_2026_09_20.md)).
- **Decided:** confidence and access counts are dropped. They are replaced by edges a reader can check (`confirms`, `supersedes`, `contradicts`) and by the librarian, which solved 5 of 6 gap cases against 2 of 6 for similarity search. The old confidence design is superseded and still there to read ([`domain_drop_confidence_for_evidence_and_librarian_2026_09_26`](../records/architecture/decisions/domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md), superseding [`pattern_confidence_lifecycle`](../records/architecture/decisions/pattern_confidence_lifecycle.md); measurement: [`eval_librarian_2026_09_26`](../records/evaluation/learnings/eval_librarian_2026_09_26.md)).

## 3. The central claim, measured, not confirmed

Fabrica's claim is that seniority can live in the record: an agent with the record pushes back on a dead end that was already tried.

- **Planned:** the measurement was preregistered, and the plan was frozen by hash before the first run, with a rule that a bad result forbids a second version ([plan](../plan_seniority_measurement.md)).
- **Observed:** 96 runs did not reach the threshold, so the pattern stays a hypothesis ([`eval_seniority_main_run_result_2026_10_18`](../records/evaluation/learnings/eval_seniority_main_run_result_2026_10_18.md)).
- **Learned:** where agents did read the reason, they often built the rejected thing anyway and flagged the conflict afterwards. Knowledge loses against an order ([`learning_knowledge_loses_against_the_order_2026_10_18`](../records/evaluation/learnings/learning_knowledge_loses_against_the_order_2026_10_18.md)). The full account is in [what we measured](what-we-measured.md).

## 4. A decision corrected the same day

The record is not only for the large decisions.

- **Decided:** session handoffs stay local, because a handoff is a roadmap rather than a line of thought ([`domain_handoffs_stay_local_records_and_sources_public_2026_11_01`](../records/records/decisions/domain_handoffs_stay_local_records_and_sources_public_2026_11_01.md)).
- **Superseded within the hour:** a handoff shows how the work was steered from session to session, and that is part of the proof. Handoffs are published, pseudonymised ([`domain_handoffs_may_be_published_pseudonymised_after_review_2026_11_01`](../records/records/decisions/domain_handoffs_may_be_published_pseudonymised_after_review_2026_11_01.md)). Both decisions stay readable. The two past handoffs are now [sources](../sources/handoff_2026_10_21.md).

## Reading further

- [`docs/records/INDEX.md`](../records/INDEX.md) is the catalogue of every record.
- [`docs/sources/`](../sources/) holds the frozen evidence: measurements, retired designs and past handoffs.
- [Organisational memory](organisational-memory.md) explains why the record is built this way.
