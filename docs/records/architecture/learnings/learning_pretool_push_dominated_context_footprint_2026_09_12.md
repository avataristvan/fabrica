id: learning_pretool_push_dominated_context_footprint_2026_09_12
type: learning
area: architecture
created: 1790678546.434832
---

Observed: Another Claude session (in another project) delivered a doctor scan over 50 transcripts (30.08.-12.09.): 348 Edit/Write calls -> ~270k characters ~= 67.6k tokens injected, ~92% of ai-mem's total context footprint. Verified against the real code (pretool_hook.py: TOP_K=2, MAX_CHARS_PER_HIT=500, query against GLOBAL_COLLECTION + repo.<project>) -- the figure is plausible, not merely asserted.
Cause: the-coder is registered as an inject_agent via ~/.config/ai-mem/agents.yaml, so most of the 348 calls presumably ran through the-coder subagents in dev-team/chunk-plan chunks (conjecture, not individually proven).
Evidence: doctor scan of that project (50 transcripts) plus code check. New evidence, not a repetition: the July cost simulation (arch_critique_opus_quantified_costs_2026_07_31) measured ONLY userprompt_hook (~4,800 tokens/session) -- PreToolUse was not quantified at all back then.
