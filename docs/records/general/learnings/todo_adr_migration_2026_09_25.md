id: todo_adr_migration_2026_09_25
type: learning
topic: general
created: 1790366791.438984
edges: [{"target_id": "domain_bmad_vs_ai_mem_epistemology_2026_09_25", "edge_type": "related"}]
---

RESULT (completed 2026-09-25): Switch to ADRs -- domain/pattern/anti-pattern entries (since b0063b8 also learning) are persisted as Markdown files in the repo (MarkdownAdrRepository). Commits: b7548a1 (implementation), 12aac54 (fixes from the holistic review), f7d802c (README fix); layout since b0063b8/093dc1b docs/records/<area>/<kind>/ instead of docs/decisions/. Motivation: git-native team distribution, PR review, currency guarantee. Related: domain_bmad_vs_ai_mem_epistemology_2026_09_25, docs/sources/epistemology_framework.md (the former docs/epistemology-framework.md, now a source).

Deliberately not solved: the retrieval trigger problem (eval_pull_gap_test_2026_09_20, agents do not query memory on their own) -- independent work, addressed by the librarian (todo_bibliothekar_haiku_retrieval_agent_2026_09_25). Resolved instead of open: the lifecycle mismatch between frequent confidence mutations and rarely changing ADR files -- confidence/access_count were dropped (domain_drop_confidence_for_evidence_and_librarian_2026_09_26), replaced by rare, explicit evidence edges (confirms/supersedes/contradicts).
