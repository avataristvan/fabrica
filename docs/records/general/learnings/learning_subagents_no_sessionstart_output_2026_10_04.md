type: learning
topic: general
perspective: agent
created: 1791067532.967105
cue: Assuming a subagent sees the SessionStart routing line or a routing table
---

Observed: Subagents receive no SessionStart output at all in practice, contradicting the routing table and the assumption in [design_three_tier_pull_the_coder_2026_09_12](../../workflow/decisions/design_three_tier_pull_the_coder_2026_09_12.md)
Cause: unknown
Evidence: [eval_experience_index_ab_2026_09_21](../../evaluation/learnings/eval_experience_index_ab_2026_09_21.md); docs/sources/hook_routing_subagent.md (the routing table's check marks describe module logic, not delivery; agent-type detection by signature is brittle); the-coder's explicit mem_query pulls exist because of this gap

## Edges

- confirms: [eval_experience_index_ab_2026_09_21](../../evaluation/learnings/eval_experience_index_ab_2026_09_21.md)
