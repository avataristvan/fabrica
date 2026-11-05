type: pattern
topic: general
perspective: agent
created: 1779056778.55903
---

Rule: Safety/warning signals (anti-patterns, contradiction alerts) should bypass quality gates that protect context bandwidth.
When: Designing any injection or notification path where warnings coexist with normal context.
Why: Missing a warning is worse than injecting a false alarm — the cost asymmetry is inverted from normal context injection. Quality gates exist to reduce noise; warnings exist to prevent harm. Applying noise-reduction logic to harm-prevention paths defeats their purpose.
Example: ai-mem anti-pattern and dilemma injection bypasses MIN_LABELED_EXAMPLES / MIN_AVG_SCORE ranker gates entirely (ANTIPATTERN_MIN_SCORE=0.4, high recall). Shipped e6fa559.
Applies broadly to: security alerts bypassing rate limits, pre-commit hooks that must not be skipped for safety checks, error monitoring that bypasses sampling thresholds.
