---
type: research
date: 2026-06-13
origin: memory entry mempalace_comparison (digest of docs/ai-mem-vs-memPalace.md), exported to docs/reference/ on 2026-10-04
status: processed
---

## What the source says

MemPalace-Vergleich — Stand 2026-06-13 (Vollständiger Vergleich: docs/ai-mem-vs-memPalace.md)

MemPalace: hierarchisches verbatimes Memory, 98.4% LongMemEval. ai-mem: abstrahiertes, adaptives Memory.

ai-mem Alleinstellungsmerkmale:
- Evidence-Kanten + Bibliothekar statt Confidence Lifecycle (Stand 2026-09-26, siehe domain_drop_confidence_for_evidence_and_librarian_2026_09_26): keine numerische confidence mehr, statt Score/Decay trägt eine 'confirms'-Kante (neu) plus supersedes/contradicts das Vertrauenssignal; ein Bibliothekar-Subagent (todo_bibliothekar_haiku_retrieval_agent_2026_09_25) liest INDEX.md/Records/Kanten und urteilt beim Abruf, statt nach einer Zahl zu sortieren. War bis 2026-09-26 eine Confidence Lifecycle (confidence 0.0–1.0 per Entry, [available]-Injection bei boost_count≥1, decay via mem_dream) — das ist jetzt abgelöst, kein aktuelles Unterscheidungsmerkmal mehr.
- Type-Ontologie (pattern / anti-pattern / feedback / project / reference / user / domain / learning / dilemma) + TTL-Exempt für Structural Knowledge
- mem_dream: aktive Konsolidierung via Claude (MERGE, DELETE, ADD, LINK, SUPERSEDE-Proposals mit Propagation)
- Typed Causal Edges (contradicts, fixes, causes, related, supersedes, confirms, derived_from) — nur mcp-memory-service hat Vergleichbares
- Expert Agent Collections (subagent.*) für Cross-Projekt-Erfahrung
- 2 Lifecycle-Hooks (SessionStart, PostToolUse) inkl. PostToolUse access tracking (last_accessed_at) -- ursprrünglich 4, PreToolUse und UserPromptSubmit 2026-09 retiriert
- Plan-Code-Reflect Zyklus via /reflect Ritual

Wo andere stärker sind:
- MemPalace: verbatim session reconstruction, 98.4% recall benchmark
- claude-mem: größte Community (v12.6.4, 109 contributors)
- mcp-memory-service / MemPalace: lokale Embeddings (kein API-Key nötig)

Philosophischer Unterschied: Verbatim (MemPalace) vs. Abstraktion (ai-mem). ai-mem wette auf destilliertes Wissen über Session-Transcripts.

Hinweis: ML-Ranker (TorchMicroRanker) wurde in 2026-06 entfernt. Confidence Lifecycle war zunächst das Replacement, wurde selbst 2026-09-26 durch Evidence-Kanten + Bibliothekar abgelöst.

Status 2026-10-04: ai-mem no longer tracks access (PostToolUse retired) and no longer uses ChromaDB by default; memory lives in git-native record files (domain_file_backend_replaces_chroma_2026_10_04).

## Our notes

