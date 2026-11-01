id: pattern_convention_enforcement_gap
type: pattern
topic: general
perspective: agent
created: 1781307523.670864
---

Rule: Convention-only workflows degrade silently under time pressure — nothing enforces the loop except discipline.
When: Designing any system where correctness depends on a human practice (commit rituals, review gates, reflection steps) rather than a code gate.
Why: Skipped steps accumulate invisibly; the degradation is self-reinforcing (sparse data → weak injections → less motivation to maintain the loop). If the system gets less useful when the convention is skipped, the convention is load-bearing and should be enforced by tooling, not policy.

Concrete instance: The Plan→Code→Reflect loop and ai-mem practices (mem_dream, upward propagation) have no code enforcement. A skipped Reflect step means learnings are lost permanently. The system's value is directly proportional to loop adherence.
