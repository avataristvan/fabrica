id: pattern_saturating_transform_nonnegativity_precondition
type: pattern
topic: general
perspective: agent
created: 1785517827.962589
---

Rule: Before applying a saturating rescale of the form raw / (raw + k) as a pool-independent replacement for min-max normalization, verify the raw signal's domain is non-negative -- or clamp it (max(raw, 0.0)) before dividing.
When: Designing any 'absolute, pool-independent' normalization transform intended to replace a min-max/pool-relative one.
Why: BM25Okapi (rank_bm25) can return negative raw scores for small or near-duplicate corpora (it floors negative IDFs at 0.25×average_idf, which is itself negative). raw/(raw+k) is not monotonic across its pole at raw=-k: a raw score of -5.05 saturated to 1.66 -- mapped ABOVE a genuine match, a full rank inversion -- and raw==-k exactly raises an uncaught ZeroDivisionError. Every 'saturating transform' formula carries an implicit domain precondition (usually non-negativity); the transform is only safe if that precondition is actually guaranteed by the upstream signal's library, never merely assumed because the formula 'looks bounded.'