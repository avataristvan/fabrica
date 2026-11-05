type: learning
topic: plugin
perspective: agent
created: 1791725662.851305
cue: I am asked how our chunk plan, handoff and FOCUS.md compare to established agent orchestration patterns
---

Observed: Our way of working matches magentic orchestration (Microsoft Azure Architecture Center, AI agent orchestration patterns). A manager keeps a task/progress ledger (plan, handoff, FOCUS.md), replans on new findings, and a human reviews at gates; the page requires persisting state at mandatory gates. Deviations: our chunk skeleton is more deterministic than the pattern intends, and the Navigator acts as co-manager, not only as an escalation target.
Cause: Both arrive at the same structure for long-running multi-agent work.
Evidence: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns#magentic-orchestration (question by the Navigator, 2026-10-11).

pseudonymised for publication, 2026-10-11

## Edges

- related: [domain_reflect_yields_handoff_and_record_candidates_2026_10_10](../../architecture/decisions/domain_reflect_yields_handoff_and_record_candidates_2026_10_10.md)
