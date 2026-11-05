type: domain
topic: architecture
perspective: user
created: 1789925427.11298
cue: Scoring, ranking or mechanical counters are about to be introduced or changed in ai-mem
---

Decision: Direction for ai-mem (2026-09-20): judgment instead of score. The epistemological framework (Taskly, /reflect, [retro], convention) is the most valuable part; mechanical scores should not replace or undermine it.
1. Signals that protect, mature or let entries be forgotten come from judgments (/reflect, mem_boost, a reasoned DELETE), not from mechanical counters. access_count from the PostToolUse filename hit (cosine >= 0.5) is a diagnostic, not a protection or maturity signal.
2. mem_dream is understood as placement (judgment), not as tidying up: relating new experience to existing experience (edges, contradiction, generalisation, scope, marking what is outdated), leaving the unresolved standing as tension (dilemma). The action vocabulary needs LINK and SUPERSEDE for this.
3. Cosine/BM25 is a candidate tool, not a relevance measure: no score threshold, no ranking signals from confidence/access_count in retrieval. The agent judges what applies in the current context.

Why:
- The Navigator's principle: the real rank is the current context (what is relevant here and now); a context-free scalar per entry contradicts this. The MLP ranker was removed for the same reason.
- The Navigator's image: ranking by frequency/intensity has something of trauma — what has fired often or strongly becomes entrenched, regardless of whether it was right in context. Mechanism in the code (as of 2026-09-20, gone since b5e5d38 on 2026-09-26: access_count is no longer kept, the dream prompt no longer knows it): the dream prompt protects access_count >= 5 as 'load-bearing' from DELETE/MERGE; mem_cleanup deletes by last_accessed_at; PostToolUse bumps entries whose text resembles the filename of the edited file (name proximity is not usefulness).
- The Navigator's image for dream: like dreaming in living beings — processing and placing, not compressing.
- The framework documentation says it itself: 'Automation would give the agent more signals. Convention gives it better ones.' The mechanical signal contradicts this principle.
- Measurement ([eval_pull_gap_test_2026_09_20](../../evaluation/learnings/eval_pull_gap_test_2026_09_20.md), plus a probe on 11 queries): cosine is usable only with vocabulary overlap, a threshold does not separate correct from noise (0.20 for the correct entry, 0.26 for a nonsense query), confidence does not influence the order anyway. The scores act mainly in maintenance, i.e. where they replace judgments.
- Correction to the original idea 'agent judges candidates': the real bottleneck is the trigger, not the ranking. In all gap cases mem_query was called 0 times; only the ID pointer in CLAUDE.md was successful. An agent only judges what is put before it.
- Currency beats ranking: the outdated is more dangerous than the badly ranked (example: ai-mem's docs/friction-and-research.md marks _ranker_signal() as Done, which no longer exists). Cosine cannot recognise the outdated; placement (marking as superseded) can.

Scope: applies to the architecture of ai-mem (retrieval, confidence lifecycle, mem_dream, mem_cleanup, PostToolUse tracking). Does not apply to the basic structure (ChromaDB, typed entries, causal edges, collections hierarchy), which stays. Implementation proceeds chunk by chunk; the respective state is in the commit, not in this entry. Open core question: which mechanism triggers retrieval when no ID is in context (see [eval_pull_gap_test_2026_09_20](../../evaluation/learnings/eval_pull_gap_test_2026_09_20.md)). To check before implementation: mem_cleanup forgetting by last_accessed_at then needs a judgment criterion instead of access recency.

Addendum 2026-10-04: The Scope clause 'ChromaDB ... bleibt' is overtaken -- record files replaced ChromaDB ([domain_file_backend_replaces_chroma_2026_10_04](domain_file_backend_replaces_chroma_2026_10_04.md)). The direction itself was carried through: no scores, keyword search only as a candidate tool.

pseudonymised for publication, 2026-10-11

## Edges

- related: [eval_pull_gap_test_2026_09_20](../../evaluation/learnings/eval_pull_gap_test_2026_09_20.md)
- related: [pattern_confidence_lifecycle](pattern_confidence_lifecycle.md)
- related: [todo_retrieval_confidence_gradient](../learnings/todo_retrieval_confidence_gradient.md)
- derived_from: [eval_pull_gap_test_2026_09_20](../../evaluation/learnings/eval_pull_gap_test_2026_09_20.md)
