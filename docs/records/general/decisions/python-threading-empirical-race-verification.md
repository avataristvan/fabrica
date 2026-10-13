id: python-threading-empirical-race-verification
type: pattern
area: general
perspective: the-coder
created: 1787509413.437909
---

Rule: Before adding a threading.Lock to "protect shared state" in a Python service, verify empirically whether it's actually needed rather than reasoning about it abstractly. Write a throwaway script: N threads doing M unlocked read-modify-write operations against the same key, then compare the final value to the expected N*M. A get-then-update pattern (read a dict/record, mutate a field, write it back) racing across threads silently loses updates -- e.g. 8 threads x 20 increments on the same ChromaDB entry's access_count landed at 32 instead of 160 without a lock, and at exactly 160 with one. This is fast (seconds) and gives a real number to cite instead of "probably fine" or "probably not thread-safe" -- confirms the fix and calibrates exactly which method needs the lock (only the read-modify-write ones; pure reads and single-atomic-call writes don't).
When: Converting a single-threaded server/loop to multi-threaded and unsure whether an underlying store's client library is safe for concurrent access.
Why: Library docs rarely state thread-safety guarantees for embedded/persistent stores (e.g. ChromaDB's Rust-backed PersistentClient); reasoning from architecture alone ("it's Rust, probably fine") misses races introduced by the *application's* own non-atomic read-modify-write logic sitting on top of an otherwise-safe store.