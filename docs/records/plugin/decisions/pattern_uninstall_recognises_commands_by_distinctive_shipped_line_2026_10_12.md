id: pattern_uninstall_recognises_commands_by_distinctive_shipped_line_2026_10_12
type: pattern
area: plugin
perspective: reviewer
created: 1791833918.658083
edges: [{"target_id": "pattern_uninstall_matches_hooks_by_module_marker_2026_10_11", "edge_type": "related"}]
cue: I am adding or changing an uninstall or cleanup path that deletes a deployed file
---

Rule: uninstall recognises an ai-mem-installed copy of a deployed file by a distinctive shipped line, not by generic words such as "ai-mem", "archivist" or "mem_add". mem-init.md: its first line, identical across all 33 historical install.py versions. reflect.md: the line `## [retro] convention for subagents`, carried by all 18 historical versions of skills/reflect.md and skills/examples/reflect.md (the two sources install.py ever copied from).
When: Adding or changing an uninstall/cleanup path for a deployed file.
Why: A user's own command that merely mentions ai-mem must survive; a user's own /reflect that mentions the old generic words is now kept.
Evidence: uninstall.py AI_MEM_COMMANDS, tests/test_uninstall.py, tests/test_install.py::test_plugin_switch_keeps_a_reflect_command_the_user_wrote.
