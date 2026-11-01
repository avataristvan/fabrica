id: ddd-remove-trust-signal-preserve-legacy-data
type: pattern
topic: general
perspective: the-coder
created: 1790438437.090794
---

Removing a numeric trust/score signal (e.g. confidence) that's threaded through a codebase is safer done as: (1) grep every file touching the field name first, including docstrings/comments -- not just the obvious read/write sites; (2) classify each hit into 'computes the signal' (delete), 'preserves a stored legacy value via generic dict merge' (keep -- never delete stored data, only stop producing it), and 'uses it as an inert example value in an unrelated test' (leave alone); (3) when a test asserts the removed signal's behavior, don't just delete the test -- rewrite it to assert the *replacement* invariant (e.g. an access-tracking test that asserted access_count increments becomes a last_accessed_at timestamp-ordering assertion), otherwise real coverage silently disappears. Concretely: replacing a mutable score with append-only edges/counters (e.g. 'confirms' edge instead of a confidence bump) makes the trust signal auditable (who confirmed what, when) instead of an opaque accumulated number.