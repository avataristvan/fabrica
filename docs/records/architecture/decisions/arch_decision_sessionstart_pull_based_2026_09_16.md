id: arch_decision_sessionstart_pull_based_2026_09_16
type: domain
area: architecture
perspective: agent
created: 1791758069.215956
edges: [{"target_id": "arch_decision_pretool_push_removed_2026_09_12", "edge_type": "related"}, {"target_id": "arch_decision_userprompt_push_removed_2026_09_13", "edge_type": "related"}, {"target_id": "design_three_tier_pull_the_coder_2026_09_12", "edge_type": "contradicts"}]
cue: Someone proposes that SessionStart deliver the old push scope again (current_focus, [available], git commits)
---

# SessionStart becomes pull-based by default (2026-09-16)

Decision: SessionStart was the last hook that still pushed memory *content* (PreToolUse retired 2026-09-12, UserPromptSubmit retired 2026-09-13). Commit 7a4796a reduces the default output of hook.py to a one-line routing hint (active collection, where applicable the registered subagent's own subagent.<name> collection) -- no current_focus text, no [available] list, no expired-entry warnings, no session delta, no git commits automatically any more. `session_start_verbose: true` in agents.yaml is the opt-in that restores the old push scope for workflows that want it. Chroma repo construction is deferred in the non-verbose path, so the DB is not opened at all.

Further changes in this commit: agents.yaml's `inject_agents` no longer automatically implies 'this agent gets ai-mem content' -- whether an agent uses ai-mem at all is now decided per agent in its own prompt. New examples/agents/example-agent-with-memory.md as a copy-paste template (explicit mem_query at the start / mem_add at the end), replaces the registry approach as the documented way. docs/reference/hooks.md (then docs/hooks.md), docs/sources/automation.md (formerly docs/automation.md), README.md, docs/how-to/wire-skills-and-agents.md (then docs/skill-agent-integration.md), skills/README.md were revised accordingly: only SessionStart + PostToolUse are registered, UserPromptSubmit/PreToolUse/repo_seeder/stop_hook are documented as retired or never wired instead of being described as active.

Addendum: The [experience index] block (cue-based 'situation -> entry' lines from mem_boost during /reflect) was added to SessionStart only later (commit c8dbf6a) -- independent of session_start_verbose, gated via its own session_start_index setting (default true).

See also: arch_decision_pretool_push_removed_2026_09_12, arch_decision_userprompt_push_removed_2026_09_13, docs/reference/hooks.md (holds the former reference doc hook_system, merged into it).

Addendum 2026-10-04: The core still holds (pull by default, routing line). Overtaken: the session_start_index setting (removed with the experience index, domain_librarian_replaces_experience_index_2026_10_04); 'only SessionStart + PostToolUse registered' (PostToolUse retired, domain_file_backend_replaces_chroma_2026_10_04); session_start_verbose remains an opt-in that reads little beyond FOCUS.md on the file backend.

Evidence: docs/sources/automation.md (push-based automation retired in favour of pull; MEMORY.md auto-demotion has no trigger); docs/sources/automation_pipeline.md (index of the automation subsystems: two active, two retired, superseded by the pull decisions).
