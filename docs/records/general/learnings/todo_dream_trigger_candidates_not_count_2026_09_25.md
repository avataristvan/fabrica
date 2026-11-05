type: learning
topic: general
created: 1790367224.873221
valid_until: 1790440445.555816
---

RESULT (implemented): Idea of 2026-09-25 -- the mem_dream trigger in /reflect counted the raw entry count (>30), a weak heuristic that is exactly the kind of mechanical threshold that 'judgment instead of score' ([domain_direction_judgment_over_scores_2026_09_20](../../architecture/decisions/domain_direction_judgment_over_scores_2026_09_20.md)) wanted to avoid. Implemented as 'dream after every reflect' (skills/examples/reflect.md step 6, [domain_dream_after_every_reflect_2026_09_26](../../workflow/decisions/domain_dream_after_every_reflect_2026_09_26.md), supersedes): smaller, more frequent dream runs instead of rare collective runs (mem_dream(mode=hier) without a collection scope had produced 205k tokens, exceeding the CLI limit).

## Edges

- superseded_by: [domain_dream_after_every_reflect_2026_09_26](../../workflow/decisions/domain_dream_after_every_reflect_2026_09_26.md)
