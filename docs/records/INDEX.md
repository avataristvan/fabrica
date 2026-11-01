# Decision Records Index

| id | topic | type | title | status |
|---|---|---|---|---|
| ai_mem_redesign_2026_06_13 | general | domain | ai-mem architecture redesign: confidence lifecycle model (2026-06-13) | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| anti-pattern-patch-object-requires-existing-attr | general | anti-pattern | Tried: removing an unused import (e.g. WORKSPACE_COLLECTION) from a module after | active |
| anti_pattern_convention_fragility_ai_mem_2026_10_04 | general | learning | Observed: Primary operational risk of ai-mem (assessed 2026-05-08) is convention | active |
| anti_pattern_eval_loads_repo_under_test_as_plugin_blocks_edits_2026_10_18 | evaluation | anti-pattern | Tried: Running the arm with --plugin-dir pointing at the arm (the repo under tes | active |
| anti_pattern_python_m_in_shim_puts_cwd_on_syspath_2026_10_12 | plugin | anti-pattern | Tried: A shim that starts the CLI with `python3 -m <pkg>`. | active |
| antipattern-partial-fix-of-minmax-normalization-in-hybrid-fusion | general | anti-pattern | Anti-pattern: min-max normalization anywhere in a hybrid-scoring fusion pipeline | active |
| antipattern_ai_mem_path_via_mcp_env_misses_hooks | evaluation | anti-pattern | Tried: Setting `env: {AI_MEM_PATH: /tmp/blind}` in the MCP server entry of `~/.c | active |
| antipattern_document_symptom_not_cause | general | anti-pattern | Tried: documenting only the symptom of a hook/component failure (e.g. 'Stop hook | active |
| antipattern_mem_add_metadata_repass | workflow | anti-pattern | Tried: Manually re-passing all existing metadata fields (access_count, boost_cou | active |
| arch_critique_push_vs_pull_synthesis_2026_07_31 | architecture | learning | Observed: Two independent devil's-advocate runs (Sonnet, Opus) against ai-mem's  | active |
| arch_decision_pretool_push_removed_2026_09_12 | architecture | domain | PreToolUse push removed: return to pure pull for Edit/Write (2026-09-12) | active |
| arch_decision_push_vs_pull_2026_07_31 | architecture | domain | Push-vs-pull architecture: decision (2026-07-31) | active |
| arch_decision_sessionstart_pull_based_2026_09_16 | architecture | domain | SessionStart becomes pull-based by default (2026-09-16) | active |
| arch_decision_userprompt_push_removed_2026_09_13 | architecture | domain | UserPromptSubmit push removed (2026-09-13) | active |
| arch_expert_agent_collections | architecture | domain | Decision: subagent.<name> collections serve as a cross-project experience layer  | superseded_by: domain_area_path_is_the_address_of_knowledge_2026_10_10 |
| arch_workspace_root_collection_naming | architecture | domain | Decision: When AI_MEM_WORKSPACE_ROOT is set, detect_repo_context() names collect | superseded_by: domain_area_path_is_the_address_of_knowledge_2026_10_10 |
| bm25_saturating_transform_2026_07_31 | architecture | domain | BM25 residual min-max flooring: decision & final shipped state (2026-07-31) | active |
| chromadb-default-space-is-l2-not-cosine | general | anti-pattern | Tried: assuming ChromaDB get_or_create_collection(name) with no explicit metadat | active |
| chunk1_daemon_shipped_2026_07_31 | architecture | learning | Observed: A Unix-socket daemon (ai_mem/daemon.py) keeps a warm ChromaMemoryRepos | active |
| chunk3_access_count_semantics_shipped_2026_07_31 | general | learning | Push-vs-Pull Chunk 3 shipped: access_count means deliberate use (2026-07-31) | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| chunk3b_adr_index_shipped_2026_09_25 | architecture | learning | Observed: A second .md file (INDEX.md) in a directory that another command globs | active |
| chunk5_adr_backfill_shipped_2026_09_25 | general | learning | Chunk 5 shipped: ADR backfill + Decision Records CLAUDE.md section (2026-09-25,  | superseded_by: domain_learning_decision_split_subfolders_2026_09_29 |
| cross-store-move-bypasses-add-usecase | general | anti-pattern | Tried: implement a cross-store 'move' operation (moving an entity between collec | active |
| daemon_concurrency_and_embedding_cache_2026_08_23 | architecture | domain | Daemon concurrency fix (commit 5419baa, 2026-08-23; formerly cited as 7e4b87f) | active |
| daemon_embedding_cache_per_key_locking_2026_08_23 | architecture | domain | Embedding cache in ChromaMemoryRepository (commit 5419baa, 2026-08-23; formerly  | active |
| ddd-remove-trust-signal-preserve-legacy-data | general | pattern | Removing a numeric trust/score signal (e.g. confidence) that's threaded through  | active |
| ddd-usecase-preserved-field-needs-followup-upsert-on-fresh-insert | general | pattern | Rule: When a use-case (e.g. AddMemoryUseCase) deliberately preserves a field onl | active |
| decision_hybrid_fusion_cosine_saturated_bm25_2026_10_04 | general | domain | Decision: BM25 hybrid score = alpha x cosine_raw + (1-alpha) x bm25_sat, with co | superseded_by: domain_file_backend_replaces_chroma_2026_10_04 |
| design_philosophy_junior_to_expert | general | domain | Design philosophy: junior-to-expert model (2026-04-29, updated 2026-06-13, 2026- | active |
| design_three_tier_pull_the_coder_2026_09_12 | workflow | domain | Status addendum (2026-09-29): The premise of the global tier ('SessionStart's [a | active |
| domain_acceptance_checksum_skips_hook_written_paths_2026_10_13 | plugin | domain | Decision: scripts/upgrade_acceptance/run.sh skips reminded/, retro_log.jsonl, do | active |
| domain_agents_learn_environment_never_edit_external_2026_10_11 | architecture | domain | Decision: ai-mem never edits externally installed agents/skills/plugins (e.g. th | active |
| domain_archivist_acceptance_closed_fail_use_carries_2026_10_13 | evaluation | domain | Decision: The archivist acceptance (scripts/eval_archivist/; pass rule >= 80% of | active |
| domain_archivist_integration_visible_to_navigator_2026_10_15 | architecture | domain | Decision: Mutual visibility is resolved: the archivist does not integrate silent | active |
| domain_archivist_may_retype_weak_confirms_2026_10_23 | architecture | domain | Decision: The archivist may retype a `confirms` edge on its own judgment when it | active |
| domain_archivist_mechanism_mem_and_mem_dream_2026_10_11 | architecture | domain | Decision: `mem` and `mem-dream` are the archivist's tools, and it calls mem-drea | active |
| domain_archivist_who_what_how_2026_10_10 | architecture | domain | Decision: The archivist is the default writer of records, not the only door. Han | active |
| domain_archivist_write_threshold_2026_10_19 | architecture | domain | Decision: The archivist applies a write threshold. A candidate becomes a record  | active |
| domain_archivist_writes_home_and_ancestors_only_2026_10_23 | architecture | domain | Decision: The archivist writes only into its home area and the areas above it, u | active |
| domain_area_path_is_the_address_of_knowledge_2026_10_10 | architecture | domain | Decision: Knowledge is addressed by the folder of its area: the nearest ancestor | active |
| domain_bmad_vs_ai_mem_epistemology_2026_09_25 | architecture | domain | Decision: The comparison of BMAD and the ai-mem framework converges on a three-l | active |
| domain_chunk7_followups_dream_area_only_mem_view_gone_cue_helper_2026_10_13 | architecture | domain | Decision: DreamMemoryUseCase works on areas only (area_refs required; collection | active |
| domain_clear_dead_weight_keep_reasons_2026_10_10 | architecture | domain | Decision: Records should become a good blueprint, so they may be edited and clea | active |
| domain_current_docs_hold_history_in_one_upgrade_section_2026_10_12 | architecture | domain | Decision: Current docs describe history only in one upgrade section (README.md " | superseded_by: domain_current_docs_may_carry_one_short_history_section_2026_10_12 |
| domain_current_docs_may_carry_one_short_history_section_2026_10_12 | architecture | domain | Decision: A current doc (reference, how-to, explanation) may carry one short his | active |
| domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12 | architecture | domain | Decision: The cutover (chunk 7 of the plugin plan) removed the MCP server, the d | active |
| domain_dev_team_own_plugin_ai_mem_ships_record_parts_2026_10_12 | architecture | domain | Decision: ai-mem ships only the record-facing parts (`ai-mem:anchor-lint`, libra | active |
| domain_direction_judgment_over_scores_2026_09_20 | architecture | domain | Decision: Direction for ai-mem (2026-09-20): judgment instead of score. The epis | active |
| domain_docs_split_into_documentation_and_sources_2026_10_10 | architecture | domain | Decision: Every file under docs/ and docs/reference/ is classified as one of thr | active |
| domain_doctor_and_reflect_reminder_accept_old_ai_mem_names_2026_10_31 | plugin | domain | Decision: After the rename to fabrica, mem doctor (plugin enabled check) and the | active |
| domain_doctor_diagnoses_ritual_erosion_2026_10_10 | architecture | domain | Decision: ai-mem gets a doctor, similar to Claude Code's /doctor. It diagnoses w | active |
| domain_doctor_lists_external_skills_apart_2026_10_23 | architecture | domain | Decision: mem doctor lists skills installed by a tool (folder with .git, VERSION | active |
| domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12 | architecture | domain | Decision: The doctor's "retired system in current doc" check is a keyword heuris | active |
| domain_domain_decisions_immediate_capture_2026_10_04 | general | domain | Decision: Domain/business decisions should be captured immediately when they sur | active |
| domain_dream_after_every_reflect_2026_09_26 | workflow | domain | Decision: mem_dream runs after every /reflect (step 6), limited to the active ar | active |
| domain_dream_proposes_never_applies_2026_10_13 | workflow | domain | Decision: mem-dream proposes, it never applies. The auto-apply path of DreamMemo | active |
| domain_drop_confidence_for_evidence_and_librarian_2026_09_26 | architecture | domain | Decision: ai-mem drops confidence and access_count as a trust signal. In their p | active |
| domain_drop_mcp_server_for_cli_plugin_2026_10_10 | architecture | domain | Decision: The MCP server (server.py, mem_* tools) is dropped. ai-mem becomes a C | active |
| domain_fabrica_kinship_with_kaizen_2026_10_14 | architecture | domain | Decision: Fabrica is positioned by its kinship with Kaizen (Toyota Production Sy | active |
| domain_fabrica_method_ai_mem_build_user_environment_use_2026_10_13 | architecture | domain | Decision: Fabrica is the method level: the framework, including the human-agent  | active |
| domain_fabrica_name_collision_checked_2026_10_15 | architecture | domain | Decision: The name Fabrica stands after a collision check (2026-10-15); no block | active |
| domain_fabrica_practice_not_process_pattern_language_2026_10_14 | architecture | domain | Decision: Fabrica is a practice, not a process. Definition: "Fabrica is a practi | active |
| domain_fabrica_records_public_as_self_proof_2026_10_10 | architecture | domain | Decision: Records about the framework itself are published with Fabrica. Fabrica | active |
| domain_fabrica_seniority_from_the_record_2026_10_14 | architecture | domain | Decision: In Fabrica, seniority comes from the record itself, not from the agent | active |
| domain_file_backend_replaces_chroma_2026_10_04 | architecture | domain | Decision: The record files are ai-mem's only store. FileMemoryRepository impleme | active |
| domain_framework_named_fabrica_2026_10_10 | architecture | domain | Decision: The framework is called Fabrica. ai-mem keeps its name and is the memo | active |
| domain_glossary_is_state_per_area_2026_10_19 | architecture | domain | Decision: Each area may keep a glossary at docs/reference/glossary.md (ai-mem ha | active |
| domain_handoff_points_instead_of_copying_2026_10_19 | workflow | domain | Decision: The /reflect handoff points instead of copying: anything already in a  | active |
| domain_handoffs_may_be_published_pseudonymised_after_review_2026_11_01 | records | domain | Decision: Handoffs (docs/handoff-*.md) may be published after all, pseudonymised | active |
| domain_handoffs_stay_local_records_and_sources_public_2026_11_01 | records | domain | Decision: Handoffs (docs/handoff-*.md) stay local and are not published. Records | superseded_by: domain_handoffs_may_be_published_pseudonymised_after_review_2026_11_01 |
| domain_hook_in_line_canonical_form_is_namespaced_2026_10_12 | plugin | domain | Decision: The canonical hook-in line is "At this boundary follow the Fabrica han | active |
| domain_hooks_enforce_that_roles_decide_how_2026_10_10 | architecture | domain | Decision: Hooks enforce THAT a ritual happens. Roles decide HOW. Planned hooks:  | active |
| domain_how_fabrica_built_itself_is_the_curated_entry_2026_11_01 | architecture | domain | Decision: docs/explanation/how-fabrica-built-itself.md is the curated entry for  | active |
| domain_internal_material_judged_by_content_and_references_2026_10_31 | records | domain | Decision: Internal material is judged by its content and by what points at it, n | active |
| domain_internal_records_stay_out_of_public_areas_2026_10_12 | architecture | domain | Decision: Records are a blueprint, and the freedom to clean them is kept. Intern | active |
| domain_last_upgrade_path_version_is_tagged_and_named_in_readme_2026_10_31 | architecture | domain | Decision: Before an upgrade, migration or cleanup path is removed from main, the | active |
| domain_learning_decision_split_subfolders_2026_09_29 | architecture | domain | Decision: Decision records are not limited to software architecture (ADR, market | active |
| domain_librarian_at_review_handoff_2026_10_10 | retrieval | domain | Decision: The librarian is firmly integrated at handoff points of the dev team i | active |
| domain_librarian_replaces_experience_index_2026_10_04 | architecture | domain | Decision: SessionStart pushes no memory content anymore. The experience index bl | active |
| domain_mem_delete_names_dangling_edges_2026_10_13 | records | domain | Decision: `mem delete` prints `dangling: REF --TYPE--> ID` for every same-area e | active |
| domain_mem_move_area_renames_with_references_rename_first_2026_11_01 | records | domain | Decision: `mem move-area OLD NEW --root DIR` renames or moves an area folder det | active |
| domain_mem_source_sets_status_and_link_find_reach_sources_2026_11_01 | records | domain | Decision: `mem link` accepts a source slug (docs/sources/<slug>.md) as target (n | active |
| domain_mem_unlink_removes_edges_2026_10_13 | records | domain | Decision: `mem unlink SOURCE TARGET [--type T]` (RemoveEdgeUseCase, ai_mem/appli | active |
| domain_no_hardcoded_keyword_pretool_hook_recall_moment_open_2026_10_23 | architecture | domain | Decision: Rejected (user, 2026-10-23): a PreToolUse hook on Bash that greps reco | active |
| domain_perspective_is_a_lens_not_a_location_2026_10_10 | architecture | domain | Decision: Every record can carry a `perspective:` field naming whose knowledge o | active |
| domain_plan_seniority_measurement_stays_loose_in_docs_2026_11_01 | evaluation | domain | Decision: docs/plan_seniority_measurement.md stays loose in docs/ although it lo | active |
| domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13 | plugin | domain | Decision: `PLUGIN_HOOK_EVENTS` (install.py / uninstall.py) deliberately stays a  | active |
| domain_plugin_renamed_fabrica_package_and_cli_keep_names_2026_10_31 | architecture | domain | Decision: The plugin and marketplace are renamed to fabrica (agents fabrica:<age | active |
| domain_plugin_target_picture_implemented_and_closed_2026_10_15 | architecture | domain | Decision: The plugin target picture (docs/target_picture_plugin.md, local only)  | active |
| domain_pseudonymisation_covers_the_whole_public_repo_2026_10_31 | records | domain | Decision: Pseudonymisation applies to the whole public repo, not only to records | active |
| domain_public_face_experience_report_not_launch_2026_10_24 | architecture | domain | Decision: The public face of Fabrica is an experience report, not a tool launch. | active |
| domain_public_records_are_written_in_english_2026_10_12 | architecture | domain | Decision: Records that go public are written in English. German records are tran | active |
| domain_rebuild_closing_scoped_to_three_todos_2026_10_15 | architecture | domain | Decision: Closing the long-running rebuild is scoped to three items (user, 2026- | superseded_by: domain_rebuild_closing_scoped_to_two_todos_2026_10_15 |
| domain_rebuild_closing_scoped_to_two_todos_2026_10_15 | architecture | domain | Decision: Closing the long-running rebuild needs two items (user, 2026-10-15): t | active |
| domain_record_edges_single_line_json_with_ids_2026_10_23 | records | domain | Decision: Record edges are stored as single-line JSON in the frontmatter (`edges | active |
| domain_records_home_stays_for_migration_2026_10_13 | architecture | domain | Decision: ai-mem's code keeps the records home (`$AI_MEM_WORKSPACE_ROOT/ai-mem-r | active |
| domain_records_model_replaces_chroma_2026_10_04 | records | domain | Decision: ChromaDB is replaced. The source of truth is git-native files in four  | active |
| domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13 | records | domain | Decision: Going public. Internal working material (raw eval transcripts, the chu | active |
| domain_reflect_yields_handoff_and_record_candidates_2026_10_10 | architecture | domain | Decision: /reflect at a context boundary produces two things. (1) A carry-only-c | active |
| domain_repo_renamed_fabrica_folder_and_plugin_stay_2026_10_15 | architecture | domain | Decision: The GitHub repo is renamed from avataristvan/ai-mem to avataristvan/fa | active |
| domain_retro_default_roles_only_plugin_shipped_agents_2026_10_12 | plugin | domain | Decision: The default retro roles of the SubagentStop hook retro_check are only  | active |
| domain_review_is_skill_with_anchor_lint_agent_2026_10_12 | workflow | domain | Decision: ai-mem ships `anchor-lint`, an own agent for the linting part of a rev | active |
| domain_setup_applies_claude_md_changes_only_on_approval_2026_10_12 | plugin | domain | Decision (user, 2026-10-12): the setup skill applies CLAUDE.md changes only on a | active |
| domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12 | plugin | domain | Decision: The setup skill (`ai-mem:setup`, successor of /mem-init) does no seedi | active |
| domain_source_status_unprocessed_or_processed_2026_10_12 | architecture | domain | Decision: A source in docs/sources/ has `status: unprocessed` or `status: proces | active |
| domain_stop_hook_replaced_by_reflect_2026_10_04 | general | domain | Decision: stop_hook.py (Stop hook reminding Claude to update current_focus when  | active |
| domain_superseded_flag_not_hide_2026_09_20 | architecture | domain | Decision: An entry that has been superseded via 'supersedes' is marked on retrie | active |
| domain_three_kinds_of_knowledge_age_differently_2026_10_10 | architecture | domain | Decision: Records distinguish three kinds of knowledge that age differently. Sta | active |
| domain_todo_prefix_ambiguity_2026_10_04 | workflow | domain | Decision: The id prefix todo_ is ambiguous in repo.ai-mem and stays so. Older to | active |
| domain_upgrade_steps_live_in_the_named_tag_not_upgrading_md_2026_10_31 | architecture | domain | Decision: The step-by-step upgrade instructions live in the tag that the README  | active |
| domain_user_records_as_role_perspective_2026_10_04 | architecture | domain | Decision: 'user' stays a record type (docs/records/<area>/user/). Two kinds of u | active |
| domain_why_travels_with_chunk_spec_2026_10_10 | architecture | domain | Decision: The why of a task reaches the coder through the handoff. /chunk-plan a | active |
| eval_experience_index_ab_2026_09_21 | evaluation | learning | Observed: With the SessionStart cue block, 3/3 gap cases went directly to the go | active |
| eval_librarian_2026_09_26 | evaluation | learning | Observed: The librarian (Haiku) solved 5/6 gap cases, both controls correctly 'n | active |
| eval_librarian_rerun_records_layout_2026_09_29 | evaluation | learning | Observed: Librarian repetition after the migration to docs/records/<area>/<kind> | active |
| eval_pull_gap_test_2026_09_20 | evaluation | learning | Observed: In all 7 gap cases 0 mem_query calls; only the ID pointer in CLAUDE.md | active |
| eval_seniority_available_not_used_confirms_pull_gap_2026_10_18 | evaluation | learning | Observed: With all records in the repo (arm A2), the agent read docs/records/ in | active |
| eval_seniority_main_run_result_2026_10_18 | evaluation | learning | Observed: The seniority measurement (docs/plan_seniority_measurement.md, frozen  | active |
| feedback_current_focus_stale_after_limit_abort_2026_09_26 | workflow | learning | Observed: The session started with 'continue'; current_focus reported 'uncommitt | active |
| feedback_dilemma_frame_leverage | general | learning | The dilemma frame has a surprisingly large leverage in practice: instead of choo | active |
| feedback_install_py_user_only | general | pattern | install.py is interactive and to be run by the user only (who briefly ends the s | active |
| fix_dream_stale_model_id_and_swallowed_stderr_2026_09_12 | architecture | domain | Decision (fixed 2026-09-12): (1) `MODELS` in dream_memory.py switched to unversi | active |
| fix_index_reindex_on_supersede_2026_09_27 | architecture | domain | Decision: MarkdownAdrRepository.upsert() now triggers regenerate_index() automat | active |
| fix_install_hook_registration_2026_07_31 | architecture | learning | Observed: has_claude_md gate inconsistent across hooks. | active |
| fix_install_workspace_root_hook_regression_2026_09_27 | architecture | domain | Decision: install.py's register_claude() now recovers an already-installed AI_ME | active |
| fix_workspace_collection_catchall_2026_07_31 | architecture | domain | Fix (2026-07-31): a directory that has its own CLAUDE.md but falls outside `AI_M | active |
| fix_workspace_focus_false_negative | architecture | learning | Observed: hook.py wrongly reported 'No focus entry found' although an active cur | active |
| glob-loop-breaks-on-new-sibling-artifact-file | general | anti-pattern | Tried: Adding a new sibling artifact file (e.g. INDEX.md) into a directory that  | active |
| learning_abstraction_vs_verbatim_tradeoff_2026_10_04 | general | domain | Decision: ai-mem bets on abstracted, distilled knowledge rather than verbatim se | active |
| learning_agent_selfreport_about_subagent_output_can_be_confabulated_2026_10_23 | evaluation | learning | Observed: A coding agent, asked in a /btw how valuable the librarian's message w | active |
| learning_area_move_invalidates_relative_edges_and_editable_install_2026_10_23 | records | learning | Observed: After ai-mem moved under ai-architecture/, 11 cross-area edges dangled | active |
| learning_autoinject_disable_never_took_effect_2026_09_13 | architecture | learning | Observed: The user noticed that a deactivation of ai-mem's 'auto-inject' that th | active |
| learning_bang_commands_have_no_stdin_2026_10_12 | plugin | learning | Observed: `!` commands in Claude Code get no stdin, so `input()` in install.py r | active |
| learning_banner_label_and_paraphrase_pass_retired_check_2026_10_12 | architecture | learning | Observed: (1) The README label "retired, kept until removal" for the rollback do | active |
| learning_bash_sandbox_masks_protected_paths_in_cwd_2026_10_12 | plugin | learning | Observed: Claude Code's Bash sandbox masks protected paths in its cwd (.bashrc,  | active |
| learning_bm25_minmax_floors_irrelevant_top_hit_2026_07_31 | architecture | learning | Observed: Empirically against the live DB (the production ai-mem store, global + | active |
| learning_call_prompt_does_not_beat_agent_template_2026_10_24 | architecture | learning | Observed: A request in the call prompt ("keep the report short") did not beat th | active |
| learning_chunk0_upgrade_acceptance_passed_2026_10_15 | plugin | learning | Observed: The chunk 0 upgrade acceptance ran on 2026-10-15 against code d5b73b1  | active |
| learning_claude_p_json_result_is_last_message_grade_stream_json_2026_10_12 | plugin | learning | Observed: `claude -p --output-format json` `result` holds only the last assistan | active |
| learning_config_rewrite_keeps_file_mode_and_backs_up_once_2026_10_12 | plugin | learning | Observed: Rewriting `~/.claude.json` (mode 0600, holds credentials) via `write_t | active |
| learning_context_boundary_is_read_and_write_point_2026_10_10 | architecture | learning | Observed: Chelsea Troy's practices (DDD Europe 2026, distilled in the records of | active |
| learning_context_load_after_pull_switch_2026_10_04 | evaluation | learning | Observed: /context in a fresh session after the switch (1M window) shows ai-mem' | active |
| learning_daemon_latency_and_record_access_race_2026_08_23 | architecture | learning | Observed: Two latency problems, diagnosed by measuring both hook paths live: war | active |
| learning_deleting_a_removed_modules_test_file_loses_tests_of_moved_functions_2026_10_31 | workflow | learning | Observed: When the test file of a removed module was deleted (tests/test_repo_co | active |
| learning_dev_team_plugin_step2_done_2026_10_10 | workflow | learning | Observed: /dev-team step 2 on the plugin briefing is done. Chunk 1b-1 (mem CLI:  | active |
| learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12 | architecture | learning | Observed: In the doctor's Effect section the `[retro]` fields show as "missing"  | active |
| learning_dont_infer_plugin_reload_rules_from_one_observation_2026_10_12 | plugin | learning | Observed: After the pull, the new plugin skill ai-mem:setup appeared in the sess | active |
| learning_dream_failure_hid_cause_stale_model_tag_2026_09_12 | architecture | learning | Observed: `mem_dream(collection="repo.ai-mem")` failed with only: "Task failed:  | active |
| learning_e2e_file_backend_after_restart_2026_10_04 | evaluation | learning | Observed: After the restart on the file backend everything worked through the re | active |
| learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12 | workflow | learning | Observed: Under an editable pyenv install, a `python -I` subprocess resolves `ai | active |
| learning_field_use_handoff_files_helped_most_librarian_scope_2026_10_24 | evaluation | learning | Observed: In hw-projekt-T, resuming on "weiter", FOCUS.md and the handoff gave t | active |
| learning_first_visitor_review_found_what_authors_sessions_missed_2026_11_01 | architecture | learning | Observed: A first-visitor review by a fresh agent (git-tracked files only, role  | active |
| learning_folder_rename_orphans_linked_worktrees_run_git_worktree_repair_2026_10_31 | workflow | learning | Observed: After the repo folder was renamed, a linked worktree (.claude/worktree | active |
| learning_gap_test_first_run_and_blindtest_2026_07_31 | evaluation | learning | Observed: First gap test (2026-05-29, WITH memory): candidate `origin_story`, qu | active |
| learning_get_by_ids_hides_unparsable_records_2026_10_10 | workflow | learning | Observed: `FileMemoryRepository.get_by_ids` silently skips record files whose fr | active |
| learning_glob_id_injection_missed_by_review_2026_10_04 | architecture | learning | Observed: find_adr_files built a glob from the entry id (`**/<id>.md`), so mem_d | active |
| learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12 | plugin | learning | Observed: A guard on an artefact of the old backend (`DB_PATH.exists()` in hook. | active |
| learning_haiku_can_run_setup_skill_mostly_eval_2026_10_12 | plugin | learning | Observed: The final-script setup eval under haiku (`run.py --model haiku --repea | active |
| learning_handwritten_records_drift_from_format_2026_10_10 | architecture | learning | Observed: Areas where sessions wrote records by hand, without ai-mem tools, foll | active |
| learning_hooks_do_not_inherit_mcp_env_2026_07_03 | architecture | learning | Observed: Hook subprocesses (hook.py / userprompt_hook.py / posttool_hook.py) do | active |
| learning_incoming_edge_list_held_in_5b2_2026_10_12 | records | learning | Observed: In the docs-move chunk the coder followed the rule to list referrers b | active |
| learning_index_status_stale_after_supersede_2026_09_27 | architecture | learning | Observed: A parallel session in another project (migrating its collections to AD | active |
| learning_knowledge_loses_against_the_order_2026_10_18 | evaluation | learning | Observed: Where the record was read, the agent often built the rejected thing an | active |
| learning_librarian_answer_must_be_in_before_first_edit_at_chunk_start_2026_10_31 | workflow | learning | Observed: At a chunk start the coder's first librarian call failed (a missing pa | active |
| learning_librarian_files_only_eval_chunk3_2026_10_11 | evaluation | learning | Observed: Chunk 3 (librarian without mem_* tools, Read/Grep/Glob only): the libr | active |
| learning_librarian_grepped_outside_scope_again_2026_10_24 | evaluation | learning | Observed: In the session of 2026-10-24 the librarian ran one Grep into docs/fabr | active |
| learning_librarian_matched_out_of_scope_files_again_2026_10_12 | evaluation | learning | Observed: The librarian again matched out-of-scope files (plan, handoff) by grep | active |
| learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12 | evaluation | learning | Observed: The librarian read plan and handoff files outside its permitted scope  | active |
| learning_librarian_reads_nav_reference_in_installed_plugin_2026_10_12 | plugin | learning | Observed: In a normal interactive session with the installed plugin, the librari | active |
| learning_librarian_scope_was_the_game_changer_2026_10_11 | architecture | learning | Observed: The user names the librarian itself as the game changer: judgment over | active |
| learning_lint_and_doctor_check_edge_fields_only_body_ids_go_stale_2026_10_31 | records | learning | Observed: After the ai-mem folder was renamed, the body of todo_build_dev_team_p | active |
| learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29 | workflow | learning | Observed: After a change to the persistence layer (record layout docs/records, c | active |
| learning_mem_in_a_worktree_reports_on_the_main_checkouts_records_2026_10_31 | workflow | learning | Observed: In a worktree, `bin/mem doctor` reports on the main checkout's records | active |
| learning_migrate_apply_exit1_has_two_meanings_2026_10_11 | workflow | learning | Observed: migrate --apply exits 1 in two different cases: files were written but | active |
| learning_old_agent_worktree_branches_covered_by_pre_squash_tags_2026_10_31 | workflow | learning | Observed: Old agent worktree branches from before the history squash are covered | active |
| learning_organizational_not_personal_memory_2026_10_10 | architecture | learning | Observed: The starting question on 2026-10-10 was how ai-mem could give the agen | active |
| learning_our_orchestration_matches_magentic_2026_10_11 | plugin | learning | Observed: Our way of working matches magentic orchestration (Microsoft Azure Arc | active |
| learning_plugin_from_local_marketplace_loads_in_place_2026_10_12 | plugin | learning | Observed: A plugin from a marketplace added from a local path with a relative so | active |
| learning_plugin_keeps_loading_from_clean_clone_when_marketplace_repointed_2026_10_31 | plugin | learning | Observed: The installed plugin must keep loading from a clean clone outside the  | active |
| learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12 | plugin | learning | Observed: Claude Code plugin mechanics, verified on claude 2.1.296 while packagi | active |
| learning_pretool_push_dominated_context_footprint_2026_09_12 | architecture | learning | Observed: Another Claude session (in another project) delivered a doctor scan ov | active |
| learning_public_history_pushed_clean_2026_10_13 | records | learning | Observed: Going public is done. main (48fabdb) and the tag v0-last-mcp (60d85d8, | active |
| learning_pull_needs_situation_triggers_2026_10_04 | evaluation | learning | Observed: In the Navigator's experience ranking and push brought misdirected noi | active |
| learning_push_check_2026_10_15_was_clean | records | learning | Observed: The push check before the 2026-10-15 push (12 commits, 164 files) was  | active |
| learning_recall_at_boundaries_stopped_a_destructive_change_across_sessions_2026_10_31 | architecture | learning | Observed: A briefing written in another session carried a wrong premise ("exactl | active |
| learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23 | evaluation | learning | Observed: In an audio-driver session the librarian was asked only at session sta | active |
| learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12 | plugin | learning | Observed: Rerun the UPGRADING.md acceptance run after every edit to UPGRADING.md | active |
| learning_safe_entry_id_misses_control_chars_2026_10_10 | workflow | learning | Observed: `is_safe_entry_id` only rejects path and glob metacharacters. Ids with | active |
| learning_setting_sources_drops_user_claude_md_for_claude_p_2026_10_12 | plugin | learning | Observed: `claude -p --setting-sources project,local` also drops the user's `~/. | active |
| learning_skill_model_frontmatter_honored_eval_under_real_model_2026_10_12 | plugin | learning | Observed: A plugin skill's `model:` frontmatter is honored (Claude Code 2.1.x).  | active |
| learning_subagents_no_sessionstart_output_2026_10_04 | general | learning | Observed: Subagents receive no SessionStart output at all in practice, contradic | active |
| learning_subagentstop_fires_for_nested_subagents_2026_10_11 | plugin | learning | Observed: SubagentStop fires for nested subagents too. On 2026-10-11 an Explore  | active |
| learning_symlink_following_walk_fixed_python_312_2026_10_15 | workflow | learning | Observed: The symlink-following delete is fixed in commit dee347c. iter_record_f | active |
| learning_temp_home_cannot_run_claude_p_2026_10_12 | plugin | learning | Observed: Temp-HOME tests cannot run `claude -p` (copying credentials into the t | active |
| learning_temp_home_record_held_again_in_6b_2026_10_12 | plugin | learning | Observed: learning_temp_home_cannot_run_claude_p_2026_10_12 held again in the se | active |
| learning_trigger_must_name_observable_moment_2026_10_10 | architecture | learning | Observed: In the session of 2026-10-10 the orchestrator did not consult memory w | active |
| learning_undoing_supersede_removes_both_fields_2026_10_12 | records | learning | Observed: Undoing a supersede means removing both `superseded_by` and `valid_unt | active |
| learning_upsert_hook_command_identity_vs_value_equality_2026_07_31 | architecture | learning | Observed: `entries.remove(entry)` in install.py's `_upsert_hook_command` deleted | active |
| learning_upsert_hook_command_matcher_overwrite_2026_07_31 | architecture | learning | Observed: install.py's `_upsert_hook_command` unconditionally overwrote `entry[" | active |
| learning_whole_record_not_better_than_decisions_alone_2026_10_24 | evaluation | learning | Observed: In the seniority measurement the whole record (A2) was not better than | active |
| learning_workspace_collection_catchall_dumped_unrelated_entries_2026_07_31 | architecture | learning | Observed: If a directory had its own CLAUDE.md but lay outside `AI_MEM_WORKSPACE | active |
| learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27 | architecture | learning | Observed: A parallel session in another project reported that the SessionStart h | active |
| memory_validation_neutral | general | pattern | Memory validation is neutral — neither code nor memory is authoritative. Code ca | active |
| pattern_always_parse_agent_type_2026_10_04 | general | pattern | Rule: SessionStart must parse the transcript to detect agent type; never trust i | active |
| pattern_archivist_report_is_an_interim_message_2026_10_24 | architecture | pattern | Rule: The archivist's integration report is an interim message to the caller: on | active |
| pattern_ask_selfreport_with_provenance_marks_2026_10_24 | evaluation | pattern | Rule: When asking an agent (other session, subagent) for a self-report on concre | active |
| pattern_auto_mode_rewrite_as_new_branch_and_tag_user_runs_overwrite_2026_10_13 | workflow | pattern | Rule: Build the rewritten target as a new branch and a new tag (git commit-tree  | active |
| pattern_batch_move_builds_destination_map_first_2026_10_12 | records | pattern | Rule: Build the destination map for all rows of a batch first, before planning a | active |
| pattern_batch_referrer_rewrite_needs_versioned_areas_2026_10_12 | records | pattern | Rule: A batch move rewrites referrers only in versioned source areas. Referrers  | active |
| pattern_blindtest_methodik | evaluation | pattern | Blind-test methodology for ai-mem evaluation | active |
| pattern_bubble_up_lookup_stops_at_root_2026_10_11 | plugin | pattern | Rule: A bubble-up (ancestor-walk) search names its stop explicitly (the root) an | active |
| pattern_bypass_gate_for_safety_signals | general | pattern | Rule: Safety/warning signals (anti-patterns, contradiction alerts) should bypass | active |
| pattern_check_secondary_edges_before_public_move_2026_10_12 | records | pattern | Rule: Before a move into a public area, check the secondary edges (`related`, `d | active |
| pattern_cite_file_or_test_not_unpushed_sha_before_squash_2026_10_13 | records | pattern | Rule: Before squashing, records cite the file or test instead of a commit SHA th | active |
| pattern_confidence_lifecycle | architecture | pattern | Rule: Use confidence (float 0.0–1.0) as the primary lifecycle signal for memory  | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| pattern_convention_enforcement_gap | general | pattern | Rule: Convention-only workflows degrade silently under time pressure — nothing e | active |
| pattern_delayed_outcome_needs_log_not_counter_2026_10_04 | general | pattern | Rule: A live rolling counter cannot measure a result whose outcome is still unkn | active |
| pattern_doctor_exit_criterion_check_scanner_covers_destination_2026_10_12 | architecture | pattern | Rule: After moving docs or changing the doc layout, verify that the scanner behi | active |
| pattern_duplicate_ids_delete_covered_copy_2026_10_12 | records | pattern | Rule: When an id exists in two areas, delete the copy whose substance is covered | active |
| pattern_duties_belong_in_enforcing_mechanisms_not_learnings_2026_10_18 | architecture | pattern | Rule: A duty ("always do X after Y") belongs in an enforcing mechanism (hook or  | active |
| pattern_english_output_strings | workflow | pattern | Rule: Keep all user-facing strings in ai-mem code in English. | active |
| pattern_error_hint_checks_error_concerns_argument_2026_10_11 | plugin | pattern | Rule: A hint attached to a use-case error must first check that the error concer | active |
| pattern_eval_artifacts_outside_agent_readable_corpus | evaluation | pattern | Rule: Eval cases, gold IDs and discriminators are not stored where the tested ag | active |
| pattern_every_pushed_ref_must_be_clean_before_public_push_2026_10_13 | records | pattern | Rule: Before making a history public, every ref that is pushed must be clean, no | active |
| pattern_findings_about_outside_files_go_to_their_topic_area_2026_10_13 | architecture | pattern | Rule: Separate three levels of work in an ai-mem session. (1) Method: the Fabric | active |
| pattern_gap_test_evaluation | evaluation | pattern | Gap test: objective evaluation of whether ai-mem helps the agent | active |
| pattern_generic_core_selective_agent_activation | architecture | pattern | Rule: ai-mem's own source must stay agent-agnostic. Per-agent behavior is opt-in | active |
| pattern_handoff_is_overwritten_not_appended_2026_10_12 | workflow | pattern | Rule: Overwrite the handoff with the current state each time; never only append. | active |
| pattern_hook_stdin_is_untrusted_2026_10_11 | plugin | pattern | Rule: Treat hook stdin and state paths as untrusted. (1) Accept session_id and o | active |
| pattern_injection_caps_not_dumps | architecture | pattern | Rule: Every automatic/session-level memory injection point (today: the opt-in ve | active |
| pattern_install_plugin_from_clean_clone_2026_10_12 | plugin | pattern | Rule: Install a locally developed plugin from a clean clone, not from the dev ch | active |
| pattern_knowledge_distribution_rule_2026_10_04 | general | pattern | Rule: Distribute knowledge by relevance and derivability. | active |
| pattern_lightweight_as_feature | architecture | pattern | Rule: ai-mem's lightweight design (ChromaDB + cosine similarity, no local infere | active |
| pattern_lint_hook_reports_codes_only_2026_10_11 | plugin | pattern | Rule: A hook's block reason about record lint carries finding codes only, never  | active |
| pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12 | records | pattern | Rule: Before moving or merging a doc, list every record that points at it (edges | active |
| pattern_load_bearing_entries_require_maintenance_discipline | workflow | pattern | Rule: When a change alters observable system behavior (thresholds, renamed conce | active |
| pattern_local_adaptive_learning_from_behavior_2026_10_04 | general | domain | Decision: ai-mem keeps record data local and uses no pretrained embedding model. | active |
| pattern_look_up_records_when_task_feels_trivial_2026_10_18 | architecture | pattern | Rule: An agent should get curious whenever it would decide differently than a re | active |
| pattern_lookup_refs_use_consumer_validation_2026_10_11 | plugin | pattern | Rule: A lookup that emits references for another command must use that command's | active |
| pattern_observed_holds_only_what_was_seen_cause_carries_origin_2026_10_24 | architecture | pattern | Rule: The Observed field of a record holds only what was seen. Every attribution | active |
| pattern_persistence_migration_bypasses_mcp | workflow | pattern | Rule: A migration that changes ai-mem's persistence layer or file layout runs vi | active |
| pattern_planner_run_exit_criterion_greps_on_current_tree_2026_10_12 | workflow | pattern | Rule: A chunk that adds an agent to a symlink-deployed set lists install.py and  | active |
| pattern_prospective_plan_validation | general | pattern | Rule: Prospective thinking as plan validation — name the dilemma before implemen | active |
| pattern_quality_at_write_time | architecture | pattern | Rule: Memory quality is determined at write time (type tagging, anti-pattern for | active |
| pattern_reflect_between_chunks | general | pattern | Rule: Between chunks in a multi-chunk implementation session, always run /reflec | active |
| pattern_repoint_edges_before_deleting_dead_weight_2026_10_12 | records | pattern | Rule: Re-point the edges that target a dead-weight copy to the surviving record  | active |
| pattern_retrieval_needs_fixed_trigger_in_role_prompt | general | pattern | Rule: A retrieval aid (records, the librarian, user records) only gets used when | active |
| pattern_retro_learned_nothing_is_valid_2026_10_11 | plugin | pattern | Rule: `learned: nothing` is a valid retro answer. retro_check must block a missi | active |
| pattern_rewiring_grep_old_collection_names_2026_10_11 | plugin | pattern | Rule: After rewiring memory writes to record candidates, grep every old collecti | active |
| pattern_rubric_levels_defined_with_boundary_examples_2026_10_18 | evaluation | pattern | Rule: Define every rubric level with an example of where it ends, and keep the s | active |
| pattern_runtime_lookup_for_patchable_path_constants_2026_10_12 | general | pattern | Rule: Do not compute a second module-level constant from a path constant (`X = D | active |
| pattern_saturating_transform_nonnegativity_precondition | general | pattern | Rule: Before applying a saturating rescale of the form raw / (raw + k) as a pool | active |
| pattern_spot_check_form_separates_grader_and_expectation_2026_10_19 | evaluation | pattern | Rule: A spot-check form for an LLM-graded eval has two separate fields per item: | active |
| pattern_spot_check_transcripts_use_tilde_fences_2026_10_18 | evaluation | pattern | Rule: In a spot-check file use ~~~~ fences for embedded transcripts, not ```. Dr | active |
| pattern_stale_by_neighbouring_retirement | workflow | pattern | Rule: Entries written or last edited shortly before a retirement commit silently | active |
| pattern_status_markers_rot_in_memory | workflow | pattern | Rule: Never embed mutable status strings ("NOT YET COMMITTED", "not started", "s | active |
| pattern_sync_commands_only_from_main_checkout_2026_10_11 | workflow | pattern | Rule: Run install.py --sync-commands and install.py --plugin-switch only from th | active |
| pattern_taxonomy_as_quality_gate | architecture | pattern | Rule: The type taxonomy (anti-pattern, dilemma) is the quality-control mechanism | active |
| pattern_text_proposals_replace_body_keep_frontmatter_2026_10_12 | records | pattern | Rule: A text proposal (pseudonymised or translated) keeps the source record's fr | active |
| pattern_triggers_beat_storage_and_ranking | evaluation | pattern | Rule: What gets an agent to access memory is an ID pointer or a situation cue in | active |
| pattern_uninstall_matches_hooks_by_module_marker_2026_10_11 | plugin | pattern | Rule: uninstall.py matches ai-mem hooks by the module marker (-m ai_mem.hooks.), | active |
| pattern_uninstall_recognises_commands_by_distinctive_shipped_line_2026_10_12 | plugin | pattern | Rule: uninstall recognises an ai-mem-installed copy of a deployed file by a dist | active |
| pattern_untrusted_json_catch_recursionerror_2026_10_11 | plugin | pattern | Rule: For untrusted JSON, catch RecursionError as well as ValueError around json | active |
| the-coder_python_patchability | general | pattern | Rule: In Python, import module-level names at the top of the file — never inside | active |
| the-coder_stop_list_complete_both_directions | general | pattern | Rule: Instructions for an unattended agent (UPGRADING.md, runbooks) name every S | active |
| todo_adr_migration_2026_09_25 | general | learning | RESULT (completed 2026-09-25): Switch to ADRs -- domain/pattern/anti-pattern ent | active |
| todo_after_confidence_drop_cleanup_2026_09_26 | general | learning | Cleanup after the confidence removal (b5e5d38), completed 2026-09-26 after the f | active |
| todo_ai_mem_violates_link_type | architecture | todo | TODO: In an ai-mem session, propose a new link type 'violates' (anti-pattern → p | active |
| todo_archivist_flag_cross_area_duplicates_2026_10_13 | architecture | todo | TODO: The archivist does not look for duplicates of a candidate in other areas.  | active |
| todo_archivist_report_names_searched_areas_2026_10_11 | architecture | todo | TODO: Make the archivist's search of the records home (ai-mem-records/global, wo | active |
| todo_bibliothekar_haiku_retrieval_agent_2026_09_25 | general | learning | RESULT (closed 2026-09-26): 'The librarian' — originally a TODO/idea of 2026-09- | active |
| todo_confidence_decay_adsr_design | general | learning | Design and implement a confidence-decay mechanism modeled on an ADSR envelope (A | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| todo_decide_librarian_core_or_optional_2026_10_24 | evaluation | todo | TODO: Settle whether the librarian is the core of Fabrica or too much, since an  | active |
| todo_detect_skipped_reflect_gate_2026_10_11 | architecture | todo | TODO: Make `mem doctor` detect a skipped reflect gate, e.g. commits on main sinc | active |
| todo_doctor_reads_environment_records_2026_10_11 | architecture | todo | TODO: make `mem doctor` (Wiring) read environment records (e.g. "external team,  | active |
| todo_doctor_retired_system_check_sidestepped_by_softer_wording_2026_10_12 | architecture | todo | TODO (user confirmed): The doctor's retired-system check can be sidestepped by s | active |
| todo_doctor_scan_private_names_paths_unpushed_shas_2026_10_13 | records | todo | TODO: A `mem doctor` (or `mem lint`) check that lists hits in docs/records and d | active |
| todo_doctor_wiring_deferred_from_4c_2026_10_11 | plugin | todo | TODO (deferred from a /simplify review of the doctor): hooks registered only in  | active |
| todo_dream_area_refs_refactor | workflow | todo | TODO (from the mem-dream area-mode review): replace AreaRefResolver.resolve(..., | active |
| todo_dream_maintenance_batch_2026_09_25 | general | learning | RESULT (worked off 2026-09-26): mem_dream maintenance batch of 2026-09-25 on rep | active |
| todo_dream_trigger_candidates_not_count_2026_09_25 | general | learning | RESULT (implemented): Idea of 2026-09-25 -- the mem_dream trigger in /reflect co | superseded_by: domain_dream_after_every_reflect_2026_09_26 |
| todo_holistic_opus_review_adr_migration_2026_09_25 | workflow | learning | Observed: The holistic Opus review of the ADR migration (b7548a1, carried out 20 | active |
| todo_librarian_cannot_read_handoffs_2026_10_20 | general | todo | TODO (Hinweis aus ai-architecture, dort nicht zu entscheiden): Der Bibliothekar  | active |
| todo_librarian_hostile_input_test_2026_10_11 | evaluation | todo | TODO: Write a hostile-input test for the librarian, and decide whether to harden | active |
| todo_librarian_scope_and_relied_on_parser_2026_10_11 | evaluation | todo | TODO: Add a committed `Relied on` parser to scripts/eval_librarian/score.py, plu | active |
| todo_mem_cli_simplify_deferred_from_1b4_2026_10_11 | plugin | todo | TODO (deferred from a /simplify review of the mem CLI): (1) a TargetNotFound exc | active |
| todo_plan_time_anti_pattern_query_and_retrieval_hypotheses_2026_10_12 | architecture | todo | TODO: Test three still-open ideas from the 2026-05-12 friction collection, one a | active |
| todo_policy_for_edges_to_reference_docs_and_sources_2026_10_12 | records | todo | TODO: Decide a policy for edges and Evidence paths that point at reference docs  | active |
| todo_pseudonymise_foreign_evidence_on_filing_rule_open_2026_10_24 | architecture | todo | TODO: Settle the rule. docs/reference/record-format.md "Sources" allows pseudony | active |
| todo_pull_trigger_points_per_situation | architecture | todo | TODO: Define fixed pull trigger points per situation, one at a time, each tested | active |
| todo_readme_first_impression_problem_first_2026_10_31 | architecture | todo | TODO (user confirmed): Write the README for the first impression: the problem fi | active |
| todo_reflect_reminder_rescans_transcript_2026_10_11 | plugin | todo | TODO: reflect_reminder rescans the whole transcript on every Stop in sessions wi | active |
| todo_resolve_public_lodge_book_vs_handoffs_local_2026_10_31 | records | todo | TODO (user confirmed): Resolve the tension between domain_fabrica_records_public | active |
| todo_retrieval_confidence_gradient | architecture | learning | Observed: Entries with a low access_count were not found despite targeted querie | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| todo_show_second_environment_beyond_claude_code_2026_10_24 | architecture | todo | TODO: Show a second environment, for example an AGENTS.md pointing to docs/recor | active |
| todo_state_dir_single_stdlib_definition_2026_10_11 | architecture | todo | TODO: Make ai_mem.hooks.state_dir the single stdlib-only definition of the $AI_M | active |
| todo_verify_retro_log_measurement_against_real_report_2026_10_12 | architecture | todo | TODO: Verify the retro-log measurement (retro_check and the doctor Effect sectio | active |
| userprompt_hook_threshold_recalibration_2026_07_31 | architecture | learning | Observed: Off-topic prompts reached 0.45-0.60 as top hits against global/repo.ai | active |
