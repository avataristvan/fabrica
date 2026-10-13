id: the-coder_feature_cap
type: pattern
area: general
perspective: the-coder
created: 1779142854.871379
---

Rule: Cap unbounded count/frequency features before feeding them into a learned ranker or scoring function.
When: Building a re-ranker, recommendation engine, or any model that takes a mix of frequency and similarity signals.
Why: A high-access incumbent accumulates an unbounded count while cosine similarity is bounded in [0,1]. Without a cap, frequency drowns out similarity and the ranker degrades to a popularity contest. Cap at a value where the feature carries signal but not dominance (e.g. 50 for access_count).
How to apply: Define `_FEATURE_CAP = N` as a named constant with a comment explaining the invariant it preserves.