id: learning_bang_commands_have_no_stdin_2026_10_12
type: learning
topic: plugin
perspective: agent
created: 1791821371.170303
edges: [{"target_id": "pattern_sync_commands_only_from_main_checkout_2026_10_11", "edge_type": "related"}]
cue: I am asking the user to run an interactive script such as install.py via a ! command
---

Observed: `!` commands in Claude Code get no stdin, so `input()` in install.py raises EOFError.
Cause: No tty or stdin is attached to `!` commands.
Evidence: install.py run via `!` during the plugin packaging. Workaround: pipe `echo y |`, or add a `--yes` flag.
