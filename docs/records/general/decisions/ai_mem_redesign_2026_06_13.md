id: ai_mem_redesign_2026_06_13
type: domain
area: general
created: 1781302341.02234
superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26
valid_until: 1790440703.114531
edges: [{"target_id": "key_invariants", "edge_type": "related"}]
---

# ai-mem architecture redesign: confidence lifecycle model (2026-06-13)

Synthesis from a reflection session. Replaces the 6-point list of the same day.

## Implementation status (complete, 2026-06-13)
1. ✓ DONE — `confidence` field in AddMemoryUseCase (commit be37fbe). Default 0.7 for new entries.
2. ✓ DONE — `mem_boost` MCP tool + /reflect step 3.1 (commit 61228c2)
3. ✓ DONE — Dream report: _confidence_report() with decay/promotion sections
4. ✓ DONE — Hook: proactively inject high-confidence entries as [available] (commit e71fded, renamed from [always-present] 2026-07-31)
5. ✓ DONE — ML ranker removed completely (commit a7110da). QueryMemoryUseCase uses ChromaDB cosine order directly.

## Core finding
Confidence (float 0.0–1.0) is the primary lifecycle signal — not retrieval frequency.
Write-time discipline (type tagging, anti-pattern format, TTL, reflect ritual) ensures quality.
Cosine similarity suffices for retrieval when the collection is clean.

## Memory hierarchy
- ephemeral: confidence < 0.3 → decay candidate
- retrievable: 0.3–0.9 → reachable via query
- available (renamed 2026-07-31 from always-present): confidence > 0.9 + access_count ≥ 3 → **Update 2026-09-16**: no longer "injected every session" — since the pull-based redesign (arch_decision_..._2026_09_16, see hook_system) SessionStart is by default only a routing hint. The [available] list appears only with `session_start_verbose: true` in agents.yaml, or when an agent queries it explicitly. **Update 2026-09-26:** the gate additionally requires boost_count ≥ 1 (see key_invariants).
