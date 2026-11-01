id: learning_skill_model_frontmatter_honored_eval_under_real_model_2026_10_12
type: learning
topic: plugin
perspective: the-coder
created: 1791833917.45286
edges: [{"target_id": "learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12", "edge_type": "related"}]
cue: I am writing or evaluating a plugin skill and wonder which model it runs under
---

Observed: A plugin skill's `model:` frontmatter is honored (Claude Code 2.1.x). A probe skill with `model: haiku` ran entirely on haiku under `--model sonnet`; the control without `model:` used sonnet. `ai-mem:setup` deliberately sets no `model:`, so this judgment skill runs under the user's session model.
Cause: The skill's own `model:` overrides the session model; absent it, the session model applies.
Rule for evals: run a skill's eval with the model it actually runs under (its `model:`, or the narrowest session model it should work under).
Evidence: the probe runs; scripts/eval_setup/.
