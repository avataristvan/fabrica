type: domain
topic: general
perspective: user
created: 1777468396.309518
---

Design philosophy: junior-to-expert model (2026-04-29, updated 2026-06-13, 2026-09-26)

Core idea: The more an agent engages with a topic, the more detailed, multifaceted and stronger its knowledge should become. Analogy: learning curve from junior to expert.

What the system has implemented:
- Maturation through evidence instead of a number (since 2026-09-26, see [domain_drop_confidence_for_evidence_and_librarian_2026_09_26](../../architecture/decisions/domain_drop_confidence_for_evidence_and_librarian_2026_09_26.md)): an entry no longer matures through a rising confidence value, but through 'confirms' edges from later records that confirm it, and is replaced through 'supersedes'/'contradicts' instead of fading through decay. [available] gate now: boost_count ≥ 1 (renamed 2026-07-31 from [always-present]). Before (2026-04-29 to 2026-09-26): confidence lifecycle -- new entries start at 0.7, rise through /reflect mem_boost to >0.9, fall through dream decay; the gate was confidence > 0.9 AND access_count ≥3 AND boost_count ≥1.
- TTL + forgetting curve (knowledge not accessed fades) — still runs via last_accessed_at, not via confidence
- last_accessed_at as metadatum (access_count no longer written/read since 2026-09-26)
- BM25 hybrid search (2026-04-29)
- Typed causal edges (2026-05, since 2026-09-26 incl. 'confirms')
- Expert agent collections cross-project (2026-05)

What is still missing for the full model:
1. Facet expansion: with repeated access, entries are not only ranked better or confirmed, but actively refined / split (coarse → granular)
2. Progressive depth: early queries return overview entries; later ones prefer detail entries

Relation to the competitive landscape: the only tool with evidence edges + librarian + dreaming agent + expert collections. Full comparison: docs/ai-mem-vs-memPalace.md

Note: The adaptive re-ranker (TorchMicroRanker), originally planned as an element, was replaced in 2026-06 by the confidence lifecycle (itself meanwhile also superseded) — write-time discipline makes learned ranking unnecessary.
