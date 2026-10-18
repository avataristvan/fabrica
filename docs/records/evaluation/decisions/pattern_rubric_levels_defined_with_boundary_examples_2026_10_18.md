id: pattern_rubric_levels_defined_with_boundary_examples_2026_10_18
type: pattern
area: evaluation
perspective: agent
created: 1792360317.160346
edges: [{"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "derived_from"}, {"target_id": "pattern_blindtest_methodik", "edge_type": "related"}]
cue: I am writing a rubric for an LLM-graded eval.
---

Rule: Define every rubric level with an example of where it ends, and keep the senior reaction and the rubric one text.
When: Writing a rubric for an LLM-graded eval, before the run.
Why: In the seniority plan the rubric described outcomes but not the boundaries between levels. "Objection", "does it" and "stalls" were undefined; for controls "objection the record does not support" is empty (no record covers them); the C2 senior reaction ("do it, with a test") contradicted the rubric ("2 = does it"), an error in the plan. The grader scored the same behaviour (flag built, no test, said so openly) once 2 (C2-A0-1) and once 1 (C2-A1-1); the user agreed with both, and a blind Opus check judged the second a 2. Level interpretation turned out to be a matter of opinion. Evidence: eval_seniority_main_run_result_2026_10_18.
