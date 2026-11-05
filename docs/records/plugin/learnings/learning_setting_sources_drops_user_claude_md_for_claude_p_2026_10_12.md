type: learning
topic: plugin
perspective: the-coder
created: 1791833917.812942
cue: I am designing a fresh-process claude -p test on the real HOME and need to know which user instructions it still sees
---

Observed: `claude -p --setting-sources project,local` also drops the user's `~/.claude/CLAUDE.md` and user commands. Exit runs on the real HOME therefore see no standing user instruction (e.g. the global "auto-apply CLAUDE.md changes" rule), which is what makes "unchanged until approval" testable there.
Cause: User-level settings sources are excluded together with the user's CLAUDE.md and commands.
Evidence: setup exit/eval runs (scripts/eval_setup/); record [learning_temp_home_cannot_run_claude_p_2026_10_12](learning_temp_home_cannot_run_claude_p_2026_10_12.md).

## Edges

- related: [learning_claude_p_json_result_is_last_message_grade_stream_json_2026_10_12](learning_claude_p_json_result_is_last_message_grade_stream_json_2026_10_12.md)
- related: [learning_temp_home_cannot_run_claude_p_2026_10_12](learning_temp_home_cannot_run_claude_p_2026_10_12.md)
