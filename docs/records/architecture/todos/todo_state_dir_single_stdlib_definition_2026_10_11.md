id: todo_state_dir_single_stdlib_definition_2026_10_11
type: todo
area: architecture
perspective: user
created: 1791738308.131693
cue: I am reading or changing the default of $AI_MEM_PATH (the default store directory) in any module
---

TODO: Make ai_mem.hooks.state_dir the single stdlib-only definition of the $AI_MEM_PATH default (a directory under ~/.local/share). It is still computed separately in hook.py, mem_cli.py, dream_cli.py, adr_cli.py and records_lint.py; only ai_mem/hooks/__init__.py and doctor.py use state_dir.
