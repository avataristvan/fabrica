type: learning
topic: evaluation
perspective: agent
created: 1792360315.595097
cue: Someone wants to promote pattern 9 (seniority lives in the record), cites it as proven, or proposes a v2 of the seniority measurement.
---

Observed: The seniority measurement (docs/plan_seniority_measurement.md, frozen sha256 5f43d06e..., harness commit 54a2b5a; main run 2026-10-16/17, 96 runs, 0 errors, all graded) did not reach probation. Pattern 9 "seniority lives in the record" (docs/fabrica/patterns/seniority-lives-in-the-record.md) stays a hypothesis. Dead ends avoided (score 2): A0 rarely, but 3/6 in repeat 3 (limit was <=2); A2 never reached >=5/6 in any repeat; the A2 controls failed "2 on both controls in >=2 of 3 repeats". The separate claim "the record carries more than decisions" (D5/D6) is also not met. The plan forbids a v2 after a bad result.
Scores per case: four groups separated by "/" are the arms A0/A1/A2/A3; the three digits inside a group are repeats 1/2/3. D1 102/222/222/222, D2 222/222/222/222, D3 001/101/111/222, D4 001/222/112/222, D5 102/111/012/112, D6 000/000/000/000, C1 222/222/222/000, C2 211/122/111/002.
Records read (tool trace): A0 5/24, A1 11/24, A2 11/24, A3 12/24; A3 asked the librarian in 9 runs.
Caveats: A3 is confounded ([anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18](../decisions/anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18.md)), so it was reported only and is not part of the rule. D2 is 222 in every arm because A0 leaks the confidence decision through code comments; the plan allows this as the realistic baseline, but D2 does not discriminate. Cost $10.12 for 96 runs plus 96 gradings; paused at 55/96 for usage and resumed with --resume. Spot-check: 20 of 96 drawn at random after grading with the arm hidden; the user agreed with all 20; a fresh blind Opus instance disagreed on 2/20 (S4 0->1, S6 1->2); the threshold of more than 1 in 5 was not reached, so the result is not uncertain.
Cause: See [learning_knowledge_loses_against_the_order_2026_10_18](learning_knowledge_loses_against_the_order_2026_10_18.md) (read records lose against the order), [eval_seniority_available_not_used_confirms_pull_gap_2026_10_18](eval_seniority_available_not_used_confirms_pull_gap_2026_10_18.md) (records are not read) and [pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18](../../architecture/decisions/pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18.md) (D6).
Evidence: scripts/eval_seniority/results/main-2026-10-16/summary.json (local only, raw results are never committed); plan commit 2967df1; harness scripts/eval_seniority/run.py.

## Edges

- related: [learning_knowledge_loses_against_the_order_2026_10_18](learning_knowledge_loses_against_the_order_2026_10_18.md)
- related: [eval_pull_gap_test_2026_09_20](eval_pull_gap_test_2026_09_20.md)
- related: [domain_fabrica_seniority_from_the_record_2026_10_14](../../architecture/decisions/domain_fabrica_seniority_from_the_record_2026_10_14.md)
- related: [pattern_spot_check_form_separates_grader_and_expectation_2026_10_19](../decisions/pattern_spot_check_form_separates_grader_and_expectation_2026_10_19.md)
- related: [learning_whole_record_not_better_than_decisions_alone_2026_10_24](learning_whole_record_not_better_than_decisions_alone_2026_10_24.md)
- related: [domain_plan_seniority_measurement_stays_loose_in_docs_2026_11_01](../decisions/domain_plan_seniority_measurement_stays_loose_in_docs_2026_11_01.md)
