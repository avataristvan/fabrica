# Decision Records Index

| id | area | type | title | status |
|---|---|---|---|---|
| ai_mem_redesign_2026_06_13 | general | domain | # ai-mem architecture redesign: confidence lifecycle model (2026-06-13) | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| anti-pattern-magicmock-default-truthy-attr | general | anti-pattern | Tried: replacing a `ctx.collection not in (A, B)` guard with `ctx.has_claude_md` | active |
| anti-pattern-patch-object-requires-existing-attr | general | anti-pattern | Tried: removing an unused import (e.g. WORKSPACE_COLLECTION) from a module after | active |
| anti_pattern_convention_fragility_ai_mem_2026_10_04 | general | learning | Observed: Primary operational risk of ai-mem (assessed 2026-05-08) is convention | active |
| anti_pattern_python_m_in_shim_puts_cwd_on_syspath_2026_10_12 | plugin | anti-pattern | Tried: A shim that starts the CLI with `python3 -m <pkg>`. | active |
| antipattern-partial-fix-of-minmax-normalization-in-hybrid-fusion | general | anti-pattern | Anti-pattern: min-max normalization anywhere in a hybrid-scoring fusion pipeline | active |
| antipattern_ai_mem_path_via_mcp_env_misses_hooks | evaluation | anti-pattern | Tried: Setting `env: {AI_MEM_PATH: /tmp/blind}` in the MCP server entry of `~/.c | active |
| antipattern_mem_add_metadata_repass | workflow | anti-pattern | Tried: Manually re-passing all existing metadata fields (access_count, boost_cou | active |
| arch_critique_push_vs_pull_synthesis_2026_07_31 | architecture | learning | Observed: Two independent devil's-advocate runs (Sonnet, Opus) against ai-mem's  | active |
| arch_decision_pretool_push_removed_2026_09_12 | architecture | domain | # PreToolUse push removed: return to pure pull for Edit/Write (2026-09-12) | active |
| arch_decision_push_vs_pull_2026_07_31 | architecture | domain | # Push-vs-pull architecture: decision (2026-07-31) | active |
| arch_decision_sessionstart_pull_based_2026_09_16 | architecture | domain | # SessionStart becomes pull-based by default (2026-09-16) | active |
| arch_decision_userprompt_push_removed_2026_09_13 | architecture | domain | # UserPromptSubmit push removed (2026-09-13) | active |
| arch_expert_agent_collections | architecture | domain | Decision: subagent.<name> collections serve as a cross-project experience layer  | active |
| arch_workspace_root_collection_naming | architecture | domain | Decision: When AI_MEM_WORKSPACE_ROOT is set, detect_repo_context() names collect | active |
| bm25_saturating_transform_2026_07_31 | architecture | domain | # BM25 residual min-max flooring: decision & final shipped state (2026-07-31) | active |
| chromadb-default-space-is-l2-not-cosine | general | anti-pattern | Tried: assuming ChromaDB get_or_create_collection(name) with no explicit metadat | active |
| chunk1_daemon_shipped_2026_07_31 | architecture | learning | Observed: A Unix-socket daemon (ai_mem/daemon.py) keeps a warm ChromaMemoryRepos | active |
| chunk3_access_count_semantics_shipped_2026_07_31 | general | learning | # Push-vs-Pull Chunk 3 shipped: access_count means deliberate use (2026-07-31) | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| chunk3b_adr_index_shipped_2026_09_25 | architecture | learning | Observed: A second .md file (INDEX.md) in a directory that another command globs | active |
| chunk5_adr_backfill_shipped_2026_09_25 | general | learning | Chunk 5 shipped: ADR backfill + Decision Records CLAUDE.md section (2026-09-25,  | superseded_by: domain_learning_decision_split_subfolders_2026_09_29 |
| cross-store-move-bypasses-add-usecase | general | anti-pattern | Tried: implement a cross-store 'move' operation (moving an entity between collec | active |
| daemon_concurrency_and_embedding_cache_2026_08_23 | architecture | domain | # Daemon concurrency fix (commit 5419baa, 2026-08-23; formerly cited as 7e4b87f) | active |
| daemon_embedding_cache_per_key_locking_2026_08_23 | architecture | domain | # Embedding cache in ChromaMemoryRepository (commit 5419baa, 2026-08-23; formerl | active |
| ddd-remove-trust-signal-preserve-legacy-data | general | pattern | Removing a numeric trust/score signal (e.g. confidence) that's threaded through  | active |
| ddd-usecase-preserved-field-needs-followup-upsert-on-fresh-insert | general | pattern | Rule: When a use-case (e.g. AddMemoryUseCase) deliberately preserves a field onl | active |
| decision_hybrid_fusion_cosine_saturated_bm25_2026_10_04 | general | domain | Decision: BM25 hybrid score = alpha x cosine_raw + (1-alpha) x bm25_sat, with co | superseded_by: domain_file_backend_replaces_chroma_2026_10_04 |
| design_three_tier_pull_the_coder_2026_09_12 | workflow | domain | Status addendum (2026-09-29): The premise of the global tier ('SessionStart's [a | active |
| domain_acceptance_checksum_skips_hook_written_paths_2026_10_13 | plugin | domain | Decision: scripts/upgrade_acceptance/run.sh skips reminded/, retro_log.jsonl, do | active |
| domain_agents_learn_environment_never_edit_external_2026_10_11 | architecture | domain | Decision: ai-mem never edits externally installed agents/skills/plugins (e.g. th | active |
| domain_archivist_mechanism_mem_and_mem_dream_2026_10_11 | architecture | domain | Decision: `mem` and `mem-dream` are the archivist's tools, and it calls mem-drea | active |
| domain_chunk7_followups_dream_area_only_mem_view_gone_cue_helper_2026_10_13 | architecture | domain | Decision: DreamMemoryUseCase works on areas only (area_refs required; collection | active |
| domain_chunk_plan_carries_all_boundary_anchors_2026_10_12 | workflow | domain | Decision: Chunk-plan entries carry every anchor that draws a boundary for the ch | active |
| domain_current_docs_hold_history_in_one_upgrade_section_2026_10_12 | architecture | domain | Decision: Current docs describe history only in one upgrade section (README.md " | superseded_by: domain_current_docs_may_carry_one_short_history_section_2026_10_12 |
| domain_current_docs_may_carry_one_short_history_section_2026_10_12 | architecture | domain | Decision: A current doc (reference, how-to, explanation) may carry one short his | active |
| domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12 | architecture | domain | Decision: The cutover (chunk 7 of the plugin plan) removed the MCP server, the d | active |
| domain_dev_team_own_plugin_ai_mem_ships_record_parts_2026_10_12 | architecture | domain | Decision: dev-team becomes its own plugin (home ~/workspace/ai-architecture) wit | active |
| domain_docs_split_into_documentation_and_sources_2026_10_10 | architecture | domain | Decision: Every file under docs/ and docs/reference/ is classified as one of thr | active |
| domain_doctor_diagnoses_ritual_erosion_2026_10_10 | architecture | domain | Decision: ai-mem gets a doctor, similar to Claude Code's /doctor. It diagnoses w | active |
| domain_doctor_retired_system_check_is_keyword_heuristic_2026_10_12 | architecture | domain | Decision: The doctor's "retired system in current doc" check is a keyword heuris | active |
| domain_dream_after_every_reflect_2026_09_26 | workflow | domain | Decision: mem_dream runs after every /reflect (step 6), limited to the active ar | active |
| domain_dream_proposes_never_applies_2026_10_13 | workflow | domain | Decision: mem-dream proposes, it never applies. The auto-apply path of DreamMemo | active |
| domain_drop_confidence_for_evidence_and_librarian_2026_09_26 | architecture | domain | Decision: ai-mem drops confidence and access_count as a trust signal. In their p | active |
| domain_drop_mcp_server_for_cli_plugin_2026_10_10 | architecture | domain | Decision: The MCP server (server.py, mem_* tools) is dropped. ai-mem becomes a C | active |
| domain_file_backend_replaces_chroma_2026_10_04 | architecture | domain | Decision: The record files are ai-mem's only store. FileMemoryRepository impleme | active |
| domain_hook_in_line_canonical_form_is_namespaced_2026_10_12 | plugin | domain | Decision: The canonical hook-in line is "At this boundary follow the ai-mem hand | active |
| domain_learning_decision_split_subfolders_2026_09_29 | architecture | domain | Decision: Decision records are not limited to software architecture (ADR, market | active |
| domain_librarian_at_review_handoff_2026_10_10 | retrieval | domain | Decision: The librarian is firmly integrated at handoff points of the dev team i | active |
| domain_librarian_replaces_experience_index_2026_10_04 | architecture | domain | Decision: SessionStart pushes no memory content anymore. The experience index bl | active |
| domain_mem_delete_names_dangling_edges_2026_10_13 | records | domain | Decision: `mem delete` prints `dangling: REF --TYPE--> ID` for every same-area e | active |
| domain_mem_unlink_removes_edges_2026_10_13 | records | domain | Decision: `mem unlink SOURCE TARGET [--type T]` (RemoveEdgeUseCase, ai_mem/appli | active |
| domain_plugin_hook_events_fixed_list_not_derived_from_hooks_json_2026_10_13 | plugin | domain | Decision: `PLUGIN_HOOK_EVENTS` (install.py / uninstall.py) deliberately stays a  | active |
| domain_records_model_replaces_chroma_2026_10_04 | records | domain | Decision: ChromaDB is replaced. The source of truth is git-native files in four  | active |
| domain_records_public_pseudonymised_internal_material_stays_local_2026_10_13 | records | domain | Decision: Going public. Internal working material (raw eval transcripts, the chu | active |
| domain_retro_default_roles_only_plugin_shipped_agents_2026_10_12 | plugin | domain | Decision: The default retro roles of the SubagentStop hook retro_check are only  | active |
| domain_review_is_skill_with_anchor_lint_agent_2026_10_12 | workflow | domain | Decision: The reviewer checks every anchor the coder had. Review is a skill, not | active |
| domain_setup_applies_claude_md_changes_only_on_approval_2026_10_12 | plugin | domain | Decision (user, 2026-10-12): the setup skill applies CLAUDE.md changes only on a | active |
| domain_setup_seeds_nothing_first_records_come_from_work_2026_10_12 | plugin | domain | Decision: The setup skill (`ai-mem:setup`, successor of /mem-init) does no seedi | active |
| domain_source_status_unprocessed_or_processed_2026_10_12 | architecture | domain | Decision: A source in docs/sources/ has `status: unprocessed` or `status: proces | active |
| domain_stop_hook_replaced_by_reflect_2026_10_04 | general | domain | Decision: stop_hook.py (Stop hook reminding Claude to update current_focus when  | active |
| domain_todo_prefix_ambiguity_2026_10_04 | workflow | domain | Decision: The id prefix todo_ is ambiguous in repo.ai-mem and stays so. Older to | active |
| domain_user_records_as_role_perspective_2026_10_04 | architecture | domain | Decision: 'user' stays a record type (docs/records/<area>/user/). Two kinds of u | active |
| eval_experience_index_ab_2026_09_21 | evaluation | learning | Observed: With the SessionStart cue block, 3/3 gap cases went directly to the go | active |
| eval_librarian_2026_09_26 | evaluation | learning | Observed: The librarian (Haiku) solved 5/6 gap cases, both controls correctly 'n | active |
| eval_librarian_rerun_records_layout_2026_09_29 | evaluation | learning | Observed: Librarian repetition after the migration to docs/records/<area>/<kind> | active |
| feedback_count_dont_estimate_in_commit_messages | general | pattern | Count numbers in commit messages and completion reports (files, entries, tests)  | active |
| feedback_current_focus_stale_after_limit_abort_2026_09_26 | workflow | learning | Observed: The session started with 'continue'; current_focus reported 'uncommitt | active |
| feedback_install_py_user_only | general | pattern | install.py is interactive and to be run by the user only (who briefly ends the s | active |
| fix_dream_stale_model_id_and_swallowed_stderr_2026_09_12 | architecture | domain | Decision (fixed 2026-09-12): (1) `MODELS` in dream_memory.py switched to unversi | active |
| fix_index_reindex_on_supersede_2026_09_27 | architecture | domain | Decision: MarkdownAdrRepository.upsert() now triggers regenerate_index() automat | active |
| fix_install_hook_registration_2026_07_31 | architecture | learning | Observed: has_claude_md gate inconsistent across hooks. | active |
| fix_install_workspace_root_hook_regression_2026_09_27 | architecture | domain | Decision: install.py's register_claude() now recovers an already-installed AI_ME | active |
| fix_workspace_collection_catchall_2026_07_31 | architecture | domain | Fix (2026-07-31): a directory that has its own CLAUDE.md but falls outside `AI_M | active |
| fix_workspace_focus_false_negative | architecture | learning | Observed: hook.py wrongly reported 'No focus entry found' although an active cur | active |
| glob-loop-breaks-on-new-sibling-artifact-file | general | anti-pattern | Tried: Adding a new sibling artifact file (e.g. INDEX.md) into a directory that  | active |
| learning_abstraction_vs_verbatim_tradeoff_2026_10_04 | general | domain | Decision: ai-mem bets on abstracted, distilled knowledge rather than verbatim se | active |
| learning_autoinject_disable_never_took_effect_2026_09_13 | architecture | learning | Observed: The user noticed that a deactivation of ai-mem's 'auto-inject' that th | active |
| learning_bang_commands_have_no_stdin_2026_10_12 | plugin | learning | Observed: `!` commands in Claude Code get no stdin, so `input()` in install.py r | active |
| learning_banner_label_and_paraphrase_pass_retired_check_2026_10_12 | architecture | learning | Observed: (1) The README label "retired, kept until removal" for the rollback do | active |
| learning_bash_sandbox_masks_protected_paths_in_cwd_2026_10_12 | plugin | learning | Observed: Claude Code's Bash sandbox masks protected paths in its cwd (.bashrc,  | active |
| learning_bm25_minmax_floors_irrelevant_top_hit_2026_07_31 | architecture | learning | Observed: Empirically against the live DB (the production ai-mem store, global + | active |
| learning_claude_p_json_result_is_last_message_grade_stream_json_2026_10_12 | plugin | learning | Observed: `claude -p --output-format json` `result` holds only the last assistan | active |
| learning_config_rewrite_keeps_file_mode_and_backs_up_once_2026_10_12 | plugin | learning | Observed: Rewriting `~/.claude.json` (mode 0600, holds credentials) via `write_t | active |
| learning_context_load_after_pull_switch_2026_10_04 | evaluation | learning | Observed: /context in a fresh session after the switch (1M window) shows ai-mem' | active |
| learning_daemon_latency_and_record_access_race_2026_08_23 | architecture | learning | Observed: Two latency problems, diagnosed by measuring both hook paths live: war | active |
| learning_dev_team_plugin_step2_done_2026_10_10 | workflow | learning | Observed: /dev-team step 2 on the plugin briefing is done. Chunk 1b-1 (mem CLI:  | active |
| learning_doctor_effect_retro_missing_signal_unreliable_2026_10_12 | architecture | learning | Observed: In the doctor's Effect section the `[retro]` fields show as "missing"  | active |
| learning_dont_infer_plugin_reload_rules_from_one_observation_2026_10_12 | plugin | learning | Observed: After the pull, the new plugin skill ai-mem:setup appeared in the sess | active |
| learning_dream_failure_hid_cause_stale_model_tag_2026_09_12 | architecture | learning | Observed: `mem_dream(collection="repo.ai-mem")` failed with only: "Task failed:  | active |
| learning_e2e_file_backend_after_restart_2026_10_04 | evaluation | learning | Observed: After the restart on the file backend everything worked through the re | active |
| learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12 | workflow | learning | Observed: Under an editable pyenv install, a `python -I` subprocess resolves `ai | active |
| learning_gap_test_first_run_and_blindtest_2026_07_31 | evaluation | learning | Observed: First gap test (2026-05-29, WITH memory): candidate `origin_story`, qu | active |
| learning_get_by_ids_hides_unparsable_records_2026_10_10 | workflow | learning | Observed: `FileMemoryRepository.get_by_ids` silently skips record files whose fr | active |
| learning_glob_id_injection_missed_by_review_2026_10_04 | architecture | learning | Observed: find_adr_files built a glob from the entry id (`**/<id>.md`), so mem_d | active |
| learning_guard_on_old_backend_artefact_silenced_sessionstart_2026_10_12 | plugin | learning | Observed: A guard on an artefact of the old backend (`DB_PATH.exists()` in hook. | active |
| learning_haiku_can_run_setup_skill_mostly_eval_2026_10_12 | plugin | learning | Observed: The final-script setup eval under haiku (`run.py --model haiku --repea | active |
| learning_handwritten_records_drift_from_format_2026_10_10 | architecture | learning | Observed: On 2026-10-10 three areas (~/workspace/ai-architecture, ~/workspace/in | active |
| learning_hooks_do_not_inherit_mcp_env_2026_07_03 | architecture | learning | Observed: Hook subprocesses (hook.py / userprompt_hook.py / posttool_hook.py) do | active |
| learning_incoming_edge_list_held_in_5b2_2026_10_12 | records | learning | Observed: In the docs-move chunk the coder followed the rule to list referrers b | active |
| learning_index_status_stale_after_supersede_2026_09_27 | architecture | learning | Observed: A parallel session in another project (migrating its collections to AD | active |
| learning_large_chunk_plan_held_over_one_weekend_2026_10_12 | workflow | learning | Observed: A very large chunk plan (about 30 chunks plus pauses) was worked throu | active |
| learning_librarian_files_only_eval_chunk3_2026_10_11 | evaluation | learning | Observed: Chunk 3 (librarian without mem_* tools, Read/Grep/Glob only): the libr | active |
| learning_librarian_matched_out_of_scope_files_again_2026_10_12 | evaluation | learning | Observed: The librarian again matched out-of-scope files (plan, handoff) by grep | active |
| learning_librarian_read_plan_and_handoff_outside_scope_2026_10_12 | evaluation | learning | Observed: The librarian read plan and handoff files outside its permitted scope  | active |
| learning_librarian_reads_nav_reference_in_installed_plugin_2026_10_12 | plugin | learning | Observed: In a normal interactive session with the installed plugin, the librari | active |
| learning_librarian_scope_was_the_game_changer_2026_10_11 | architecture | learning | Observed: The user names the librarian itself as the game changer: judgment over | active |
| learning_mcp_servers_keep_old_code_and_cached_schema_2026_09_29 | workflow | learning | Observed: After a change to the persistence layer (record layout docs/records, c | active |
| learning_migrate_apply_exit1_has_two_meanings_2026_10_11 | workflow | learning | Observed: migrate --apply exits 1 in two different cases: files were written but | active |
| learning_plan_exit_criterion_conflicted_with_do_not_touch_list_2026_10_12 | workflow | learning | Observed: The plan of a docs-rewrite chunk demanded zero doctor hits while forbi | active |
| learning_plugin_from_local_marketplace_loads_in_place_2026_10_12 | plugin | learning | Observed: A plugin from a marketplace added from a local path with a relative so | active |
| learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12 | plugin | learning | Observed: Claude Code plugin mechanics, verified on claude 2.1.296 while packagi | active |
| learning_pretool_push_dominated_context_footprint_2026_09_12 | architecture | learning | Observed: Another Claude session (in another project) delivered a doctor scan ov | active |
| learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12 | plugin | learning | Observed: Rerun the UPGRADING.md acceptance run after every edit to UPGRADING.md | active |
| learning_review_design_converged_stepwise_2026_10_12 | workflow | learning | Observed: The review design converged in conversation in steps (own agent -> dec | active |
| learning_safe_entry_id_misses_control_chars_2026_10_10 | workflow | learning | Observed: `is_safe_entry_id` only rejects path and glob metacharacters. Ids with | active |
| learning_setting_sources_drops_user_claude_md_for_claude_p_2026_10_12 | plugin | learning | Observed: `claude -p --setting-sources project,local` also drops the user's `~/. | active |
| learning_skill_model_frontmatter_honored_eval_under_real_model_2026_10_12 | plugin | learning | Observed: A plugin skill's `model:` frontmatter is honored (Claude Code 2.1.x).  | active |
| learning_subagents_no_sessionstart_output_2026_10_04 | general | learning | Observed: Subagents receive no SessionStart output at all in practice, contradic | active |
| learning_subagentstop_fires_for_nested_subagents_2026_10_11 | plugin | learning | Observed: SubagentStop fires for nested subagents too. On 2026-10-11 an Explore  | active |
| learning_temp_home_cannot_run_claude_p_2026_10_12 | plugin | learning | Observed: Temp-HOME tests cannot run `claude -p` (copying credentials into the t | active |
| learning_temp_home_record_held_again_in_6b_2026_10_12 | plugin | learning | Observed: learning_temp_home_cannot_run_claude_p_2026_10_12 held again in the se | active |
| learning_undoing_supersede_removes_both_fields_2026_10_12 | records | learning | Observed: Undoing a supersede means removing both `superseded_by` and `valid_unt | active |
| learning_upsert_hook_command_identity_vs_value_equality_2026_07_31 | architecture | learning | Observed: `entries.remove(entry)` in install.py's `_upsert_hook_command` deleted | active |
| learning_upsert_hook_command_matcher_overwrite_2026_07_31 | architecture | learning | Observed: install.py's `_upsert_hook_command` unconditionally overwrote `entry[" | active |
| learning_workspace_collection_catchall_dumped_unrelated_entries_2026_07_31 | architecture | learning | Observed: If a directory had its own CLAUDE.md but lay outside `AI_MEM_WORKSPACE | active |
| learning_workspace_root_hook_prefix_lost_on_reinstall_2026_09_27 | architecture | learning | Observed: A parallel session in another project reported that the SessionStart h | active |
| learning_worktree_base_lagged_main_in_5b2_2026_10_12 | workflow | learning | Observed: The worktree agent of a docs chunk started from a base that lagged beh | active |
| learning_worktree_isolation_branches_from_origin_2026_10_10 | workflow | learning | Observed: Two coders were spawned with Agent isolation "worktree" while local ma | active |
| learning_worktree_isolation_stale_base_2026_10_10 | plugin | learning | Observed: Both parallel the-coder spawns with isolation="worktree" (step 1 of th | active |
| mock-discriminate-multi-call-site-by-argument | general | pattern | When a test helper mocks a function with a flat return_value for ALL call sites, | active |
| pattern_always_parse_agent_type_2026_10_04 | general | pattern | Rule: SessionStart must parse the transcript to detect agent type; never trust i | active |
| pattern_attribute_records_by_created_timestamp_2026_10_12 | records | pattern | Rule: To attribute a the-coder record to its project when the text does not say, | active |
| pattern_batch_move_builds_destination_map_first_2026_10_12 | records | pattern | Rule: Build the destination map for all rows of a batch first, before planning a | active |
| pattern_batch_referrer_rewrite_needs_versioned_areas_2026_10_12 | records | pattern | Rule: A batch move rewrites referrers only in versioned source areas. Referrers  | active |
| pattern_blindtest_methodik | evaluation | pattern | # Blind-test methodology for ai-mem evaluation | active |
| pattern_bubble_up_lookup_stops_at_root_2026_10_11 | plugin | pattern | Rule: A bubble-up (ancestor-walk) search names its stop explicitly (the root) an | active |
| pattern_bypass_gate_for_safety_signals | general | pattern | Rule: Safety/warning signals (anti-patterns, contradiction alerts) should bypass | active |
| pattern_check_secondary_edges_before_public_move_2026_10_12 | records | pattern | Rule: Before a move into a public area, check the secondary edges (`related`, `d | active |
| pattern_confidence_lifecycle | architecture | pattern | Rule: Use confidence (float 0.0–1.0) as the primary lifecycle signal for memory  | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| pattern_delayed_outcome_needs_log_not_counter_2026_10_04 | general | pattern | Rule: A live rolling counter cannot measure a result whose outcome is still unkn | active |
| pattern_deployed_artifact_source_classes | workflow | pattern | Rule: Before editing a deployed file (skill, command, agent), determine its sour | active |
| pattern_doctor_exit_criterion_check_scanner_covers_destination_2026_10_12 | architecture | pattern | Rule: After moving docs or changing the doc layout, verify that the scanner behi | active |
| pattern_duplicate_ids_delete_covered_copy_2026_10_12 | records | pattern | Rule: When an id exists in two areas, delete the copy whose substance is covered | active |
| pattern_english_output_strings | workflow | pattern | Rule: Keep all user-facing strings in ai-mem code in English. | active |
| pattern_error_hint_checks_error_concerns_argument_2026_10_11 | plugin | pattern | Rule: A hint attached to a use-case error must first check that the error concer | active |
| pattern_eval_artifacts_outside_agent_readable_corpus | evaluation | pattern | Rule: Eval cases, gold IDs and discriminators are not stored where the tested ag | active |
| pattern_gap_test_evaluation | evaluation | pattern | # Gap test: objective evaluation of whether ai-mem helps the agent | active |
| pattern_generic_core_selective_agent_activation | architecture | pattern | Rule: ai-mem's own source must stay agent-agnostic. Per-agent behavior is opt-in | active |
| pattern_handoff_is_overwritten_not_appended_2026_10_12 | workflow | pattern | Rule: Overwrite the handoff with the current state each time; never only append. | active |
| pattern_hook_stdin_is_untrusted_2026_10_11 | plugin | pattern | Rule: Treat hook stdin and state paths as untrusted. (1) Accept session_id and o | active |
| pattern_injection_caps_not_dumps | architecture | pattern | Rule: Every automatic/session-level memory injection point (today: the opt-in ve | active |
| pattern_insights_plus_memory_depth | general | pattern | Rule: /insights gives behavioral patterns from the outside; ai-mem gives archite | active |
| pattern_install_plugin_from_clean_clone_2026_10_12 | plugin | pattern | Rule: Install a locally developed plugin from a clean clone, not from the dev ch | active |
| pattern_lightweight_as_feature | architecture | pattern | Rule: ai-mem's lightweight design (ChromaDB + cosine similarity, no local infere | active |
| pattern_lint_hook_reports_codes_only_2026_10_11 | plugin | pattern | Rule: A hook's block reason about record lint carries finding codes only, never  | active |
| pattern_list_incoming_edges_before_moving_or_merging_a_doc_2026_10_12 | records | pattern | Rule: Before moving or merging a doc, list every record that points at it (edges | active |
| pattern_load_bearing_entries_require_maintenance_discipline | workflow | pattern | Rule: When a change alters observable system behavior (thresholds, renamed conce | active |
| pattern_local_adaptive_learning_from_behavior_2026_10_04 | general | domain | Decision: ai-mem keeps record data local and uses no pretrained embedding model. | active |
| pattern_lookup_refs_use_consumer_validation_2026_10_11 | plugin | pattern | Rule: A lookup that emits references for another command must use that command's | active |
| pattern_persistence_migration_bypasses_mcp | workflow | pattern | Rule: A migration that changes ai-mem's persistence layer or file layout runs vi | active |
| pattern_planner_run_exit_criterion_greps_on_current_tree_2026_10_12 | workflow | pattern | Rule: Run every exit-criterion grep against the current tree before writing it.  | active |
| pattern_quality_at_write_time | architecture | pattern | Rule: Memory quality is determined at write time (type tagging, anti-pattern for | active |
| pattern_repoint_edges_before_deleting_dead_weight_2026_10_12 | records | pattern | Rule: Re-point the edges that target a dead-weight copy to the surviving record  | active |
| pattern_retro_learned_nothing_is_valid_2026_10_11 | plugin | pattern | Rule: `learned: nothing` is a valid retro answer. retro_check must block a missi | active |
| pattern_rewiring_grep_old_collection_names_2026_10_11 | plugin | pattern | Rule: After rewiring memory writes to record candidates, grep every old collecti | active |
| pattern_runtime_lookup_for_patchable_path_constants_2026_10_12 | general | pattern | Rule: Do not compute a second module-level constant from a path constant (`X = D | active |
| pattern_saturating_transform_nonnegativity_precondition | general | pattern | Rule: Before applying a saturating rescale of the form raw / (raw + k) as a pool | active |
| pattern_stale_by_neighbouring_retirement | workflow | pattern | Rule: Entries written or last edited shortly before a retirement commit silently | active |
| pattern_sync_commands_only_from_main_checkout_2026_10_11 | workflow | pattern | Rule: Run install.py --sync-commands and install.py --plugin-switch only from th | active |
| pattern_taxonomy_as_quality_gate | architecture | pattern | Rule: The type taxonomy (anti-pattern, dilemma) is the quality-control mechanism | active |
| pattern_text_proposals_replace_body_keep_frontmatter_2026_10_12 | records | pattern | Rule: A text proposal (pseudonymised or translated) keeps the source record's fr | active |
| pattern_uninstall_matches_hooks_by_module_marker_2026_10_11 | plugin | pattern | Rule: uninstall.py matches ai-mem hooks by the module marker (-m ai_mem.hooks.), | active |
| pattern_uninstall_recognises_commands_by_distinctive_shipped_line_2026_10_12 | plugin | pattern | Rule: uninstall recognises an ai-mem-installed copy of a deployed file by a dist | active |
| pattern_untrusted_json_catch_recursionerror_2026_10_11 | plugin | pattern | Rule: For untrusted JSON, catch RecursionError as well as ValueError around json | active |
| pattern_worktree_chunk_copies_git_ignored_files_explicitly_2026_10_12 | workflow | pattern | Rule: Git-ignored files exist only in the main checkout. A worktree chunk that n | active |
| python-per-key-lock-dedup-cache-pattern | general | pattern | Pattern: A per-key locking cache (as opposed to one lock guarding the whole cach | active |
| python-threading-empirical-race-verification | general | pattern | Rule: Before adding a threading.Lock to "protect shared state" in a Python servi | active |
| socket-server-single-to-thread-per-connection-conversion | general | pattern | Pattern: Converting a single-threaded accept-loop socket server (accept -> handl | active |
| the-coder_audit_tests_for_encoded_old_behavior | general | pattern | Rule: When fixing a scoring/behavior bug, explicitly audit existing tests for on | active |
| the-coder_explicit_params | general | pattern | Thread new parameters explicitly through function signatures instead of a module | active |
| the-coder_fallback_heuristics | general | pattern | Rule: Protocol-compatible fallbacks should still apply meaningful heuristics — n | active |
| the-coder_feature_cap | general | pattern | Rule: Cap unbounded count/frequency features before feeding them into a learned  | active |
| the-coder_grep_before_default_change | general | pattern | Rule: When changing a default value, grep all tests that implicitly assume the o | active |
| the-coder_grep_single_char_false_positives | general | pattern | Rule: When grepping for single-character variable names to rename, always visual | active |
| the-coder_investigation_first | general | pattern | Investigation before implementation: if the analysis shows that the existing des | active |
| the-coder_mcp_tool_description_contract | general | pattern | Rule: When authoring MCP tools or AI-facing APIs, include explicit routing instr | active |
| the-coder_protocol_completeness | general | pattern | Rule: Protocol definitions must cover all methods that callers actually call — n | active |
| the-coder_python_patchability | general | pattern | Rule: In Python, import module-level names at the top of the file — never inside | active |
| the-coder_read_all_before_subsystem_removal | general | pattern | Rule: When removing a subsystem, read ALL affected files before writing a single | active |
| the-coder_recalibrate_thresholds_empirically_post_fix | general | pattern | Rule: After fixing a scoring/heuristic bug, recalibrate any dependent thresholds | active |
| the-coder_return_type_naming | general | pattern | Rule: Functions that change their return type (e.g. class → tuple) need a name t | active |
| the-coder_sentinel_migration_pattern | general | pattern | Rule: Use a sentinel file to gate one-time migrations in tools without a formal  | active |
| the-coder_stop_list_complete_both_directions | general | pattern | Rule: Instructions for an unattended agent (UPGRADING.md, runbooks) name every S | active |
| the-coder_transparent_wrapper | general | pattern | Rule: Transparent wrappers must carry scores through unchanged, as if the wrappe | active |
| the-coder_trust_domain_contract | general | pattern | Rule: Trust the domain contract — do not filter again what the repository layer  | active |
| the-coder_ucb_cold_start_pattern | general | pattern | UCB exploration bonus `c/sqrt(access_count)` is a clean, parameter-free cold-sta | active |
| todo_adr_migration_2026_09_25 | general | learning | RESULT (completed 2026-09-25): Switch to ADRs -- domain/pattern/anti-pattern ent | active |
| todo_after_confidence_drop_cleanup_2026_09_26 | general | learning | Cleanup after the confidence removal (b5e5d38), completed 2026-09-26 after the f | active |
| todo_ai_mem_violates_link_type | architecture | todo | TODO: In an ai-mem session, propose a new link type 'violates' (anti-pattern → p | active |
| todo_archivist_report_names_searched_areas_2026_10_11 | architecture | todo | TODO: The archivist report names the areas it searched. This is a lever from an  | active |
| todo_bibliothekar_haiku_retrieval_agent_2026_09_25 | general | learning | RESULT (closed 2026-09-26): 'The librarian' — originally a TODO/idea of 2026-09- | active |
| todo_check_no_private_records_before_push_2026_10_12 | workflow | todo | TODO: Before any push (main and tag v0-last-mcp), check that no internal or priv | active |
| todo_chunk4c_retro_log_dedupe_and_doctor_constant_2026_10_11 | plugin | todo | TODO: (1) Deduplicate retro_log.jsonl by agent_id, since a blocked agent logs tw | active |
| todo_confidence_decay_adsr_design | general | learning | Design and implement a confidence-decay mechanism modeled on an ADSR envelope (A | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| todo_detect_skipped_reflect_gate_2026_10_11 | architecture | todo | TODO: Make `mem doctor` detect a skipped reflect gate, e.g. commits on main sinc | active |
| todo_doctor_reads_environment_records_2026_10_11 | architecture | todo | TODO: make `mem doctor` (Wiring) read environment records (e.g. "external team,  | active |
| todo_doctor_retired_system_check_sidestepped_by_softer_wording_2026_10_12 | architecture | todo | TODO (user confirmed): The doctor's retired-system check can be sidestepped by s | active |
| todo_doctor_wiring_deferred_from_4c_2026_10_11 | plugin | todo | TODO (deferred from a /simplify review of the doctor): (1) hooks registered only | active |
| todo_dream_area_refs_refactor | workflow | todo | TODO (from the mem-dream area-mode review): replace AreaRefResolver.resolve(..., | active |
| todo_dream_guard_before_llm_calls | workflow | todo | TODO (from the mem-dream area-mode review): in mem-dream area mode the migration | active |
| todo_dream_maintenance_batch_2026_09_25 | general | learning | RESULT (worked off 2026-09-26): mem_dream maintenance batch of 2026-09-25 on rep | active |
| todo_dream_neighbourhood_unknown_id_message | workflow | todo | TODO (from the mem-dream area-mode review): with mem-dream --neighbourhood, a LI | active |
| todo_dream_trigger_candidates_not_count_2026_09_25 | general | learning | RESULT (implemented): Idea of 2026-09-25 -- the mem_dream trigger in /reflect co | superseded_by: domain_dream_after_every_reflect_2026_09_26 |
| todo_drop_chromadb_dependency | architecture | todo | TODO: Remove the Chroma rollback: chromadb dependency, chroma_repository, markdo | superseded_by: domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12 |
| todo_fix_broken_memPalace_link_in_epistemology_framework_2026_10_12 | architecture | todo | TODO: Fix the broken link to ai-mem-vs-memPalace.md in docs/epistemology-framewo | active |
| todo_frontmatter_value_injection | workflow | todo | TODO (push security review 2026-10-10): adr_markdown.serialize writes superseded | active |
| todo_holistic_opus_review_adr_migration_2026_09_25 | workflow | learning | Observed: The holistic Opus review of the ADR migration (b7548a1, carried out 20 | active |
| todo_librarian_hostile_input_test_2026_10_11 | evaluation | todo | TODO: Write a hostile-input test for the librarian, and decide whether to harden | active |
| todo_librarian_scope_and_relied_on_parser_2026_10_11 | evaluation | todo | TODO: Limit the librarian's search to docs/records, docs/reference and docs/sour | active |
| todo_mem_cli_simplify_deferred_from_1b4_2026_10_11 | plugin | todo | TODO (deferred from a /simplify review of the mem CLI): (1) a TargetNotFound exc | active |
| todo_mem_link_and_find_resolve_source_slugs_2026_10_12 | records | todo | TODO: Make `mem link` and `mem find` resolve source slugs (docs/sources/<slug>.m | active |
| todo_persona_finding_records_not_found_2026_10_11 | plugin | todo | TODO: The Mara/Rin/Clara `*-finding` entries that the persona skills reference w | active |
| todo_persona_skill_area_paths_are_guesses_2026_10_11 | plugin | todo | TODO: The area paths in the persona skills (a business area of another project,  | active |
| todo_plan_time_anti_pattern_query_and_retrieval_hypotheses_2026_10_12 | architecture | todo | TODO: Test three still-open ideas from the 2026-05-12 friction collection, one a | active |
| todo_policy_for_edges_to_reference_docs_and_sources_2026_10_12 | records | todo | TODO: Decide a policy for edges and Evidence paths that point at reference docs  | active |
| todo_pull_trigger_points_per_situation | architecture | todo | TODO: Define fixed pull trigger points per situation, one at a time, each tested | active |
| todo_reflect_reminder_rescans_transcript_2026_10_11 | plugin | todo | TODO: reflect_reminder rescans the whole transcript on every Stop in sessions wi | active |
| todo_retrieval_confidence_gradient | architecture | learning | Observed: Entries with a low access_count were not found despite targeted querie | superseded_by: domain_drop_confidence_for_evidence_and_librarian_2026_09_26 |
| todo_simplify_security_reviewer | workflow | todo | TODO: Add a fifth /simplify review perspective, security: hostile input from too | active |
| todo_split_manifest_and_name_framework | architecture | todo | TODO (with the user, not via dev-team): Split docs/epistemology-framework.md int | active |
| todo_state_dir_single_stdlib_definition_2026_10_11 | architecture | todo | TODO: Make ai_mem.hooks.state_dir the single stdlib-only definition of the $AI_M | active |
| todo_symlink_following_delete | workflow | todo | TODO (push security review 2026-10-10): adr_paths.iter_record_files uses rglob,  | active |
| todo_user_record_review_values | workflow | todo | TODO: Write a user record 'what I value in a review' (docs/records/<area>/user/) | active |
| todo_verify_local_skills_can_have_namespace_2026_10_12 | workflow | todo | TODO: Verify whether local (non-plugin) skills can have a namespace. The assumpt | active |
| todo_verify_retro_log_measurement_against_real_report_2026_10_12 | architecture | todo | TODO: Verify the retro-log measurement (retro_check and the doctor Effect sectio | active |
| todo_version_the_target_areas_2026_10_12 | records | todo | TODO: Put the unversioned target areas under version control (at least ai-archit | active |
| userprompt_hook_threshold_recalibration_2026_07_31 | architecture | learning | Observed: Off-topic prompts reached 0.45-0.60 as top hits against global/repo.ai | active |
| verify-expensive-call-cost-before-optimizing | general | pattern | Rule: Before implementing a caching/dedup optimization around an expensive third | active |
