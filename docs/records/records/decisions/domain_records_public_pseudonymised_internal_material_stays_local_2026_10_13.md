id: domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13
type: domain
area: records
perspective: user
created: 1791876534.257867
edges: [{"target_id": "../fabrica:domain_fabrica_records_public_as_self_proof_2026_10_10", "edge_type": "related"}, {"target_id": "../fabrica:domain_clear_dead_weight_keep_reasons_2026_10_10", "edge_type": "derived_from"}, {"target_id": "pattern_text_proposals_replace_body_keep_frontmatter_2026_10_12", "edge_type": "related"}, {"target_id": "learning_public_history_pushed_clean_2026_10_13", "edge_type": "related"}, {"target_id": "pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13", "edge_type": "related"}, {"target_id": "pattern_cite_file_or_test_not_unpushed_sha_before_squash_2026_10_13", "edge_type": "related"}, {"target_id": "todo_doctor_scan_private_names_paths_unpushed_shas_2026_10_13", "edge_type": "related"}]
cue: I am about to push records, docs/sources or eval material of ai-mem to a public remote
---

Decision: Going public. Internal working material (raw eval transcripts, the chunk plan, the target picture, session handoffs) stays local through .git/info/exclude. The records and docs/sources are pseudonymised: one consistent pseudonym per project, machine paths as `~/...`, and only fabrica and ai-architecture may be named. Records and docs point only at what the repo still contains; pointers to local-only material are replaced by a code path, a test, a doc or another record id. Commit SHAs of unpushed commits are replaced by the file or test they refer to, because squashing removes them.
Why: The records are meant to be a blueprint readable on their own (../fabrica:domain_fabrica_records_public_as_self_proof_2026_10_10), but they carried traces of private projects and of one machine, and pointers to files a reader cannot open. Dead weight is removed under ../fabrica:domain_clear_dead_weight_keep_reasons_2026_10_10: reasons, measurements and supersede chains stay, only the pointers and names go.
Scope: ai-mem docs/records, docs/sources, scripts/eval_*. The pre-push check was done and the push happened on 2026-10-13: learning_public_history_pushed_clean_2026_10_13. How to push safely: pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13.
