id: learning_haiku_can_run_setup_skill_mostly_eval_2026_10_12
type: learning
topic: plugin
perspective: agent
created: 1791833919.862938
edges: [{"target_id": "learning_skill_model_frontmatter_honored_eval_under_real_model_2026_10_12", "edge_type": "derived_from"}]
cue: I am judging whether a narrow model such as haiku can run the ai-mem:setup skill
---

Observed: The final-script setup eval under haiku (`run.py --model haiku --repeats 3`, after the session-limit reset): teams 3/3, claude_md 3/3, doctor 2/3; the one miss judged correctly but wrote no `VERDICT` line (format, not judgment). Under sonnet 9/9. `~/.claude` was unchanged in all runs.
Cause: The residual failure is output-format discipline of the narrow model, not the judgment.
Evidence: scripts/eval_setup/run.py.
