id: the-coder_recalibrate_thresholds_empirically_post_fix
type: pattern
area: general
perspective: the-coder
created: 1785505717.204282
---

Rule: After fixing a scoring/heuristic bug, recalibrate any dependent thresholds empirically against real data rather than assuming the fix alone means values will now cleanly separate.
When: Any fix to a scoring formula, ranker, or similarity metric that other code thresholds against.
Why: The old bug may have masked additional, structurally similar issues one layer down (e.g. a second normalization step with the same flaw) that only become visible once real numbers are measured -- guessed thresholds tend to be wrong in the optimistic direction, assuming a cleaner separation than actually exists.