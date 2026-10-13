id: antipattern-partial-fix-of-minmax-normalization-in-hybrid-fusion
type: anti-pattern
area: general
perspective: the-coder
created: 1785504680.937064
edges: [{"target_id": "the-coder_transparent_wrapper", "edge_type": "related"}]
---

Anti-pattern: min-max normalization anywhere in a hybrid-scoring fusion pipeline (e.g. BM25+cosine) rescales the best-in-candidate-pool item to ~1.0 regardless of its absolute relevance to the query. This means even a genuinely irrelevant query gets an artificially inflated top-hit score, because 'best of 50 candidates' always gets normalized toward the ceiling. Fixing this on one side of a fusion formula (e.g. making cosine a real absolute similarity) does NOT fix it if the other side (e.g. BM25) still gets min-max normalized — the inflation just moves to whichever term still uses relative normalization. Lesson: when recalibrating score thresholds after a scoring-pipeline fix, measure real top-hit scores for clearly-irrelevant queries against production data first: don't assume the fix fully solved the 'top hit always scores high' problem just because one component was corrected. Validated in ai-mem's userprompt_hook.py threshold recalibration (2026-07-31): irrelevant queries still scored 0.45-0.60 post-fix due to BM25's remaining min-max normalization, even though the cosine component was already a real absolute similarity.