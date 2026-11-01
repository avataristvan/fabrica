id: domain_internal_material_judged_by_content_and_references_2026_10_31
type: domain
topic: records
perspective: agent
created: 1793470087.224786
edges: [{"target_id": "domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13", "edge_type": "related"}, {"target_id": "learning_librarian_files_only_eval_chunk3_2026_10_11", "edge_type": "related"}]
cue: I am deciding whether a file in scripts/ or docs/ stays public or local, and was going to decide it by file name or rule.
---

Decision: Internal material is judged by its content and by what points at it, not by file name plus a blanket rule. The eval JSONs in scripts/eval_librarian/ are scored results that records cite as evidence (score.py reads them; learning_librarian_files_only_eval_chunk3_2026_10_11 cites one), so they stay public. Only the raw streams stay local.
Why: A rule like "eval material stays local" would cut a pointer that a public record rests on and leave the reader with evidence they cannot open, which is the thing domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13 wants to avoid.
Scope: Refines that record for scripts/eval_*; the scored JSONs are public, raw transcripts and streams are local.
