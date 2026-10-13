id: the-coder_ucb_cold_start_pattern
type: pattern
area: general
perspective: the-coder
created: 1779227484.145656
---

UCB exploration bonus `c/sqrt(access_count)` is a clean, parameter-free cold-start fix for fallback rankers. New or split entries (access_count=0) get max bonus; established entries converge to near-zero bonus. No new infrastructure, no per-entry state — just one constant and `math.sqrt`. Applies to any system where a learned ranker has a deterministic fallback.