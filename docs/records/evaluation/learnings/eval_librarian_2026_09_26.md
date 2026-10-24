id: eval_librarian_2026_09_26
type: learning
area: evaluation
created: 1790413679.919859
edges: [{"target_id": "domain_drop_confidence_for_evidence_and_librarian_2026_09_26", "edge_type": "related"}, {"target_id": "eval_experience_index_ab_2026_09_21", "edge_type": "related"}, {"target_id": "design_three_tier_pull_the_coder_2026_09_12", "edge_type": "related"}, {"target_id": "learning_librarian_files_only_eval_chunk3_2026_10_11", "edge_type": "related"}, {"target_id": "eval_pull_gap_test_2026_09_20", "edge_type": "related"}, {"target_id": "domain_direction_judgment_over_scores_2026_09_20", "edge_type": "confirms"}, {"target_id": "learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23", "edge_type": "related"}, {"target_id": "learning_field_use_handoff_files_helped_most_librarian_scope_2026_10_24", "edge_type": "related"}]
---

Observed: The librarian (Haiku) solved 5/6 gap cases, both controls correctly 'not documented'; plain retrieval hit@1 2/6.
Cause: Judgment over a catalog instead of a score; the tools: restriction was not actually enforced in the measurement (general-purpose instead of the registered type).
Evidence: scripts/eval_pull/README.md 'Librarian arm'; prototype da3f2ab.

# Librarian prototype: measurement against the pull gap test (2026-09-26)

Prototype for todo_bibliothekar_haiku_retrieval_agent_2026_09_25 / domain_drop_confidence_for_evidence_and_librarian_2026_09_26. Definition: examples/agents/librarian.md (Haiku, read-only, tools mem_list/mem_get/mem_edges/mem_query/Read restricted to docs/decisions/ by instruction -- as of 2026-09-26, today docs/records/ --, no write tools). Measurement and method in detail: scripts/eval_pull/README.md, section 'Librarian arm'.

## Setup
A different question from the original gap test: not 'does an agent ask on its own', but 'what does a cheap agent find when explicitly asked'. n=1 per case, Agent tool, model=haiku, subagent_type=general-purpose (no registered 'librarian' type available, definition inserted verbatim as a prompt preamble — the tools: restriction was therefore not actually enforced). Isolation maintained: scripts/eval_pull/ moved out of the repo before every run, back afterwards, git diff verified empty. replay.py run again today: the baseline does NOT hold exactly (cosine hit@1 2/6, hybrid hit@3 2/6, versus 3/7 and 4/7 on 2026-09-20) — the collection has changed since, cases.json has 6 instead of 7 gap cases today.

## Result
5/6 gap cases ok (g1, g2, g3, g4, g5), g6 fail (run delivered no Answer/Relied-on format, wrong/no gold ID). Both controls (c1, c2) correctly 'not documented', no fabrication, no padding with loosely related entries. The gold IDs of g1/g3/g4 are verbatim in CLAUDE.local.md (moved there since 2026-09-20, previously CLAUDE.md) — so they test the pointer, not the catalog-scan judgment (2-3 tool calls, no INDEX.md scan needed). The real new hits without a pointer are g2 and g5 — two of the three cases (g2, g5, g6) that the original test missed completely. g6 remains unsolved for the librarian as well. For comparison: eval_experience_index_ab_2026_09_21 solved the same trio 3/3, but with hand-written situation cues for exactly these questions; the librarian reaches 2/3 without any case-specific preparation, just a generic catalog scan. Compared with plain retrieval (replay.py, same 6 cases, hit@1 2/6), the judgment procedure is clearly superior — consistent with pattern_triggers_beat_storage_and_ranking, here as judgment instead of score, not as a better ranking formula.
g7 (reviewer pull) is not in cases.json (posed live on 2026-09-20 and discarded as invalid, never persisted; reconstructed from the session transcript) — run separately, 1 of 2 gold IDs, not included in the count above.

## Limits
n=1 per case, one model, one collection (~55 entries, favourable for a full scan, untested at 10x). general-purpose had unrestricted tool access, the tools: list of the definition was not actually enforced in this measurement. Questions written by an agent that knew the entries. Most important limitation: this measures WHAT the librarian finds when asked — NOT whether an orchestrator agent would think of asking it on its own. The trigger problem (pattern_triggers_beat_storage_and_ranking, eval_pull_gap_test_2026_09_20) remains completely open; the librarian deliberately has no fixed call point yet.

## Evaluation standard (from domain_drop_confidence_for_evidence_and_librarian_2026_09_26)
The librarian is an approach on probation. This first run shows: it improves WHAT is found (5/6 instead of the plain score hit rate of 2/6), but does not solve the trigger problem and still needs fixed call points.

Addendum (2026-09-29): The re-test with the registered type 'librarian' has taken place, see eval_librarian_rerun_records_layout_2026_09_29. This file lies under docs/records/evaluation/learnings/, contains case and gold IDs and was readable for the librarian in the re-test; the results (5/6 here, 4/6 there) may therefore be inflated. Fix before the next run (pattern_eval_artifacts_outside_agent_readable_corpus). The path references 'docs/decisions/' above reflect the state of 2026-09-26.
