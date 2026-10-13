---
type: research
date: 2026-06-13
origin: memory entry mempalace_comparison (digest of docs/ai-mem-vs-memPalace.md), exported to docs/reference/ on 2026-10-04
status: processed
---
> Translated from the German original on 2026-10-13; content unchanged.

## What the source says

MemPalace comparison — as of 2026-06-13 (full comparison: docs/ai-mem-vs-memPalace.md)

MemPalace: hierarchical verbatim memory, 98.4% LongMemEval. ai-mem: abstracted, adaptive memory.

ai-mem unique selling points:
- Evidence edges + librarian instead of confidence lifecycle (as of 2026-09-26, see domain_drop_confidence_for_evidence_and_librarian_2026_09_26): no numeric confidence any more, instead of score/decay a 'confirms' edge (new) plus supersedes/contradicts carries the trust signal; a librarian subagent (todo_bibliothekar_haiku_retrieval_agent_2026_09_25) reads INDEX.md/records/edges and judges at retrieval, instead of sorting by a number. Until 2026-09-26 this was a confidence lifecycle (confidence 0.0–1.0 per entry, [available] injection at boost_count≥1, decay via mem_dream) — that is now superseded, no longer a current distinguishing feature.
- Type ontology (pattern / anti-pattern / feedback / project / reference / user / domain / learning / dilemma) + TTL exemption for structural knowledge
- mem_dream: active consolidation via Claude (MERGE, DELETE, ADD, LINK, SUPERSEDE proposals with propagation)
- Typed Causal Edges (contradicts, fixes, causes, related, supersedes, confirms, derived_from) — only mcp-memory-service has something comparable
- Expert agent collections (subagent.*) for cross-project experience
- 2 lifecycle hooks (SessionStart, PostToolUse) incl. PostToolUse access tracking (last_accessed_at) -- originally 4, PreToolUse and UserPromptSubmit retired 2026-09
- Plan-Code-Reflect cycle via the /reflect ritual

Where others are stronger:
- MemPalace: verbatim session reconstruction, 98.4% recall benchmark
- claude-mem: largest community (v12.6.4, 109 contributors)
- mcp-memory-service / MemPalace: local embeddings (no API key needed)

Philosophical difference: verbatim (MemPalace) vs. abstraction (ai-mem). ai-mem bets on distilled knowledge over session transcripts.

Note: the ML ranker (TorchMicroRanker) was removed in 2026-06. The confidence lifecycle was initially the replacement, and was itself superseded on 2026-09-26 by evidence edges + librarian.

Status 2026-10-04: ai-mem no longer tracks access (PostToolUse retired) and no longer uses ChromaDB by default; memory lives in git-native record files (domain_file_backend_replaces_chroma_2026_10_04).

## Our notes

