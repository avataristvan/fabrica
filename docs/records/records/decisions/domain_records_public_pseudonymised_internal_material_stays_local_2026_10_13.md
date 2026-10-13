id: domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13
type: domain
area: records
perspective: user
created: 1791876534.257867
edges: [{"target_id": "../fabrica:domain_fabrica_records_public_as_self_proof_2026_10_10", "edge_type": "related"}, {"target_id": "../fabrica:domain_clear_dead_weight_keep_reasons_2026_10_10", "edge_type": "derived_from"}, {"target_id": "pattern_text_proposals_replace_body_keep_frontmatter_2026_10_12", "edge_type": "related"}, {"target_id": "todo_check_no_private_records_before_push_2026_10_12", "edge_type": "related"}]
cue: I am about to push records, docs/sources or eval material of ai-mem to a public remote
---

Decision: Going public. Internal working material (raw eval transcripts, the chunk plan, the target picture, session handoffs) stays local through .git/info/exclude. The records and docs/sources are pseudonymised: one consistent pseudonym per project, machine paths as `~/...`, and only fabrica and ai-architecture may be named. Records and docs point only at what the repo still contains; pointers to local-only material are replaced by a code path, a test, a doc or another record id. Commit SHAs of unpushed commits are replaced by the file or test they refer to, because squashing removes them.
Why: The records are meant to be a blueprint readable on their own (../fabrica:domain_fabrica_records_public_as_self_proof_2026_10_10), but they carried traces of private projects and of one machine, and pointers to files a reader cannot open. Dead weight is removed under ../fabrica:domain_clear_dead_weight_keep_reasons_2026_10_10: reasons, measurements and supersede chains stay, only the pointers and names go.
Scope: ai-mem docs/records, docs/sources, scripts/eval_*. Before any push: todo_check_no_private_records_before_push_2026_10_12.
