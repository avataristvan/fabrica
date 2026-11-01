id: domain_plan_seniority_measurement_stays_loose_in_docs_2026_11_01
type: domain
topic: evaluation
perspective: agent
created: 1793524157.494791
edges: [{"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "related"}]
cue: You are tidying docs/ and tempted to move docs/plan_seniority_measurement.md to sources or add frontmatter.
---

Decision: docs/plan_seniority_measurement.md stays loose in docs/ although it looks like an internal plan, with no frontmatter added.
Why: It is the preregistration, frozen by a sha256 that scripts/eval_seniority/run.py checks; moving it or editing it breaks the evidence.
Scope: tidying docs/ or moving plans to docs/sources/. Result of the run: eval_seniority_main_run_result_2026_10_18.
