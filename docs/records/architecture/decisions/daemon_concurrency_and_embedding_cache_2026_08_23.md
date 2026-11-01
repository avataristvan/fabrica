id: daemon_concurrency_and_embedding_cache_2026_08_23
type: domain
topic: architecture
created: 1787512794.273834
edges: [{"target_id": "chunk1_daemon_shipped_2026_07_31", "edge_type": "related"}, {"target_id": "learning_daemon_latency_and_record_access_race_2026_08_23", "edge_type": "derived_from"}]
---

# Daemon concurrency fix (commit 5419baa, 2026-08-23; formerly cited as 7e4b87f)

userprompt_hook.py::main() fires its 4 independent queries (global, repo context, antipattern, dilemma) via `ThreadPoolExecutor(max_workers=4)`, joined before continuing -- `detect_repo_context()` still runs first (fast, local) to decide whether the 3 repo-scoped queries are needed at all. (Note: this call site no longer executes now that userprompt_hook.py is unwired -- see arch_decision_userprompt_push_removed_2026_09_13 -- but the daemon/threading/cache fixes below are still live and used by SessionStart/PostToolUse.)

daemon.py::run() spawns one thread per connection (`_serve_connection`); the `shutdown` op signals the exit via a `threading.Event` instead of a direct return value, and since the accept loop can block in `accept()` for up to `ACCEPT_POLL_SECONDS`, the shutdown handler thread opens a throwaway connection to itself to unblock it immediately. `last_activity` (idle-timeout gate) stays lock-free by construction -- it is only read/written by the single accept-loop thread, never by a handler thread (a new connection is itself the activity signal).

`ChromaMemoryRepository.record_access()`: `threading.Lock` (`self._write_lock`) around the body -- the only write path that the daemon's `query`/`ping`/`shutdown` ops can reach (`upsert`/`delete` are never called by the daemon). Reads (`query()`, `get_by_ids()`) stay unlocked. `BM25MemoryRepository` needed no change -- freshly instantiated per query call, holds no shared mutable state. `PROTOCOL_VERSION` 1->2.

The embedding cache introduced in the same commit is described in daemon_embedding_cache_per_key_locking_2026_08_23. Observations, measurements and the race proof: learning_daemon_latency_and_record_access_race_2026_08_23.

