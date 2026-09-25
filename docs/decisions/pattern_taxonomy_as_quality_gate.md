id: pattern_taxonomy_as_quality_gate
type: pattern
created: 1779228062.47625
---

Rule: The type taxonomy (anti-pattern, dilemma) is the quality-control mechanism for hooks — not score thresholds.
When: Designing new entry types or new hook paths.
Why: anti-pattern and dilemma warnings must fire immediately — a missed warning is worse than a false alarm. Context injection can be gated by score. Separating 'fire always' (warnings) from 'fire when relevant' (context) keeps the system useful from day one without noise.

Concrete (updated 2026-09-12 to match the live thresholds since the 2026-07-31 scoring fixes): anti-pattern fires at ANTIPATTERN_MIN_SCORE=0.58 (unconditional, no ranker gate). Dilemma fires at DILEMMA_MIN_SCORE=0.58 (unconditional). Context injection ([available]-style id+title listing) fires when hybrid score ≥ CONTEXT_MIN_SCORE=0.62 — no ranker gate (removed 2026-06). The gate lives at the entry's type, not its score.