type: anti-pattern
topic: plugin
perspective: agent
created: 1791821370.63955
cue: I am writing a CLI shim or launcher that runs from arbitrary working directories
---

Tried: A shim that starts the CLI with `python3 -m <pkg>`.
Failed because: `-m` puts the caller's cwd first on sys.path; a foreign `ai_mem/` in the cwd was executed (reproduced).
Instead: The shims run `bin/run_cli.py` as a script, with the plugin root first on sys.path.
Evidence: bin/run_cli.py and the shims bin/mem, bin/mem-dream.

## Edges

- related: [learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12](../../workflow/learnings/learning_editable_install_python_i_resolves_main_checkout_not_worktree_2026_10_12.md)
