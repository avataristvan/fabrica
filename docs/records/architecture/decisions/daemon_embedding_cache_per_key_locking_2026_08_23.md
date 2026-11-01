id: daemon_embedding_cache_per_key_locking_2026_08_23
type: domain
topic: architecture
created: 1790700224.810241
edges: [{"target_id": "learning_daemon_latency_and_record_access_race_2026_08_23", "edge_type": "derived_from"}, {"target_id": "daemon_concurrency_and_embedding_cache_2026_08_23", "edge_type": "related"}]
---

# Embedding cache in ChromaMemoryRepository (commit 5419baa, 2026-08-23; formerly cited as 7e4b87f)

`ChromaMemoryRepository.__init__` now owns its own `DefaultEmbeddingFunction()` instance (`chromadb.utils.embedding_functions`) plus an `_EmbeddingCache`: an LRU-bounded (`_EMBEDDING_CACHE_MAXSIZE = 128`) dict, keyed by **text alone, not (collection, text)** -- all collections share the same default embedding function, so the same text always embeds to the same vector; if this assumption ever stops holding (a per-collection embedding function is introduced), the cache must be re-keyed by `(collection, text)`. `query()` computes the embedding via the cache and passes `query_embeddings=[vector]` to `col.query()` instead of `query_texts=[text]`.

The cache uses **per-key locking**, not one lock over the whole cache: one `threading.Lock` per text in flight (tracked in `_pending`, cleaned up after the compute, whether success or exception) -- only true duplicates of the same text block each other, requests for different texts run fully in parallel and thereby preserve the point of the daemon threading fix.

Shared commit with the daemon concurrency fix: daemon_concurrency_and_embedding_cache_2026_08_23. Observations, measurements and the race proof: learning_daemon_latency_and_record_access_race_2026_08_23.
