id: todo_state_dir_single_stdlib_definition_2026_10_11
type: todo
area: architecture
perspective: user
created: 1791738308.131693
cue: I am reading or changing the default of $AI_MEM_PATH (the default store directory) in any module
---

TODO: Make ai_mem.hooks.state_dir the single stdlib-only definition of the $AI_MEM_PATH default (a directory under ~/.local/share). It is now computed in about 12 places (hook.py, doctor.py, mem_cli.py, records_lint.py, server.py, ...).
