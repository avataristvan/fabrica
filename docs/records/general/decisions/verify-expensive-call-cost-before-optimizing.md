id: verify-expensive-call-cost-before-optimizing
type: pattern
area: general
perspective: the-coder
created: 1787510914.666054
---

Rule: Before implementing a caching/dedup optimization around an expensive third-party call (an embedding function, an API client, an ML inference call), spend 5 minutes in a REPL confirming: (a) the actual per-call cost (don't assume it's a one-time 'warm-up' cost -- many ML/inference costs are per-call, not per-process, e.g. ONNX embedding inference measured constant at ~150-250ms across repeated calls on an already-warm model); (b) that a 'shortcut' path exists in the library's public API to skip the expensive part when you already have the result (e.g. chromadb's collection.query() accepts query_embeddings=[...] as a documented alternative to query_texts=[...], letting you precompute once and skip its internal re-embed); (c) that your own instance of the underlying resource (e.g. constructing your own DefaultEmbeddingFunction() instead of reaching into a library object's private _embedding_function attribute) produces byte-identical output to what the library would have used internally -- diff two calls with the same input and assert equality, don't assume.
When: Optimizing away redundant expensive computation that a library performs implicitly (embeddings, parsing, hashing) as a side effect of a higher-level call.
Why: Confirms the optimization actually targets the real cost (not a phantom one-time cost that caching wouldn't help anyway), and confirms the alternate code path is a supported, correctness-preserving substitute rather than a private-API hack that could silently diverge from the library's own internal behavior.