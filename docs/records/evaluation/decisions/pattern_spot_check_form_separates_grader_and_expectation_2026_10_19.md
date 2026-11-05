type: pattern
topic: evaluation
perspective: agent
created: 1792362455.907015
cue: I am designing a human spot-check form for an LLM-graded eval.
---

Rule: A spot-check form for an LLM-graded eval has two separate fields per item: "did the grader measure correctly against the expectation?" and "is the expectation itself right?".
When: designing the next human spot-check of graded eval results.
Why: in the seniority run one agree/disagree mixed both: the user's first "disagree" lines were lead-ins to plan criticism, not grading verdicts, and were corrected later. Related: [pattern_rubric_levels_defined_with_boundary_examples_2026_10_18](pattern_rubric_levels_defined_with_boundary_examples_2026_10_18.md), [eval_seniority_main_run_result_2026_10_18](../learnings/eval_seniority_main_run_result_2026_10_18.md).

## Edges

- related: [pattern_rubric_levels_defined_with_boundary_examples_2026_10_18](pattern_rubric_levels_defined_with_boundary_examples_2026_10_18.md)
- derived_from: [eval_seniority_main_run_result_2026_10_18](../learnings/eval_seniority_main_run_result_2026_10_18.md)
