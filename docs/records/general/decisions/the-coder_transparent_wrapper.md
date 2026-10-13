id: the-coder_transparent_wrapper
type: pattern
area: general
perspective: the-coder
created: 1779142854.871379
---

Rule: Transparent wrappers must carry scores through unchanged, as if the wrapper didn't exist.
When: Wrapping a repository, service, or data source behind the same Protocol (e.g. BM25 over ChromaDB, cache over HTTP client).
Why: Application-layer code that receives a `QueryResult` assumes `score` reflects the best available ranking. If the wrapper re-uses the inner score instead of the fused score, the outer layer sees stale data. The wrapper IS the ranker — its output must be the final score, not an intermediate.
How to apply: The wrapper computes its own score and overwrites `result.score` before returning. The application layer never detects the wrapper — it only sees the Protocol.