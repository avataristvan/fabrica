id: todo_confidence_decay_adsr_design
type: learning
area: general
created: 1785505681.516074
superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26
valid_until: 1790412165.713779
edges: [{"target_id": "../fabrica:domain_direction_judgment_over_scores_2026_09_20", "edge_type": "contradicts"}]
---

Design and implement a confidence-decay mechanism modeled on an ADSR envelope (Attack/Sustain/Release), per user's analogy from a DAW spectrum curve. Currently confidence only moves via manual mem_boost (+/-) or the static default 0.7 -- no passive time-based decay exists. Wanted: Sustain phase where continued relevance holds or raises confidence toward max; Release phase where confidence echoes/persists a bit across sessions before gradually fading (not a step function) once no longer accessed/boosted; plus a 'deranking' signal distinct from passive decay -- an active push-down when an entry is found wrong/misleading, not just fading from disuse. Explicitly scoped separate from the 2026-07-31 scoring-bug fix.

(Status 2026-10-04: obsolete — confidence was dropped on 2026-09-26, see domain_drop_confidence_for_evidence_and_librarian_2026_09_26.)
