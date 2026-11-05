type: anti-pattern
topic: general
perspective: the-coder
created: 1785504094.286085
cue: Computing a similarity score from a vector DB distance without checking its metric
---

Tried: assuming ChromaDB get_or_create_collection(name) with no explicit metadata uses cosine distance for score = 1 - dist calculations.
Failed because: the default space is `l2` (squared L2), not cosine. For normalized embeddings, squared-L2 dist = 2 - 2*cos_sim, not 1 - cos_sim, so scores were silently wrong (verified empirically: cos_sim=0.1208, but returned dist=1.7583, not the ~0.879 a cosine-distance assumption would imply).
Instead: either pass `metadata={'hnsw:space': 'cosine'}` at collection creation, or if stuck with the l2 default, convert explicitly: cos_sim = 1 - dist/2. Never assume a vector DB's default distance metric without checking docs or verifying empirically with two known embeddings.
Evidence: docs/sources/key_invariants.md (ChromaDB-era invariants; they apply only to the rollback backend).
