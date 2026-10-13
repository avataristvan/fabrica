id: the-coder_fallback_heuristics
type: pattern
area: general
perspective: the-coder
created: 1779142854.871379
---

Rule: Protocol-compatible fallbacks should still apply meaningful heuristics — not just return raw scores.
When: Designing a fallback (NullRanker, NullCache, NullQueue) that satisfies the same interface as the real implementation.
Why: A fallback that returns raw scores unchanged creates a system that degrades silently to a popularity contest or stale-cache hit pattern. A fallback that mirrors at least the structural guarantees of the real thing (e.g. session-hit penalty, deduplication) makes the system useful even without the heavyweight implementation.
How to apply: For each behavioral invariant the real impl enforces (diversity, recency, session novelty), apply a simplified heuristic version in the fallback.