id: pattern_spot_check_form_separates_grader_and_expectation_2026_10_19
type: pattern
topic: evaluation
perspective: agent
created: 1792362455.907015
edges: [{"target_id": "pattern_rubric_levels_defined_with_boundary_examples_2026_10_18", "edge_type": "related"}, {"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "derived_from"}]
cue: I am designing a human spot-check form for an LLM-graded eval.
---

Rule: A spot-check form for an LLM-graded eval has two separate fields per item: "did the grader measure correctly against the expectation?" and "is the expectation itself right?".
When: designing the next human spot-check of graded eval results.
Why: in the seniority run one agree/disagree mixed both: the user's first "disagree" lines were lead-ins to plan criticism, not grading verdicts, and were corrected later. Related: pattern_rubric_levels_defined_with_boundary_examples_2026_10_18, eval_seniority_main_run_result_2026_10_18.
