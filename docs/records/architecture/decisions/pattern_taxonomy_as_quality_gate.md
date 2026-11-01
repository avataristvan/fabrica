id: pattern_taxonomy_as_quality_gate
type: pattern
topic: architecture
created: 1779228062.47625
edges: [{"target_id": "domain_direction_judgment_over_scores_2026_09_20", "edge_type": "related"}]
---

Rule: The type taxonomy (anti-pattern, dilemma) is the quality-control mechanism for hooks — not score thresholds.
When: Designing new entry types or new hook paths.
Why: anti-pattern and dilemma warnings must fire immediately — a missed warning is worse than a false alarm. Context injection can be gated by score. Separating 'fire always' (warnings) from 'fire when relevant' (context) keeps the system useful from day one without noise.

History (these three thresholds lived only in ai_mem/userprompt_hook.py, whose UserPromptSubmit registration install.py retired 2026-09-13 — verified: ANTIPATTERN_MIN_SCORE/DILEMMA_MIN_SCORE/CONTEXT_MIN_SCORE exist nowhere else in the codebase): anti-pattern fired at ANTIPATTERN_MIN_SCORE=0.58 (unconditional, no ranker gate). Dilemma fired at DILEMMA_MIN_SCORE=0.58 (unconditional). Context injection ([available]-style id+title listing) fired when hybrid score ≥ CONTEXT_MIN_SCORE=0.62 — no ranker gate (removed 2026-06). The gate lives at the entry's type, not its score — that principle predates the retirement and still applies to whatever hook path fires today (e.g. SessionStart's [available] gate, PostToolUse tracking).

Status 2026-10-04: The gate is now a write gate: mem_add rejects types without a record file (FileMemoryRepository).
