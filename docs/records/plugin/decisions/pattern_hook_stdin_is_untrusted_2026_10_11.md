id: pattern_hook_stdin_is_untrusted_2026_10_11
type: pattern
topic: plugin
perspective: the-coder
created: 1791738295.910154
edges: [{"target_id": "pattern_lint_hook_reports_codes_only_2026_10_11", "edge_type": "related"}, {"target_id": "learning_glob_id_injection_missed_by_review_2026_10_04", "edge_type": "related"}, {"target_id": "pattern_untrusted_json_catch_recursionerror_2026_10_11", "edge_type": "related"}, {"target_id": "domain_hooks_enforce_that_roles_decide_how_2026_10_10", "edge_type": "related"}]
cue: I am writing a Claude Code hook or doctor check that writes state files, opens a transcript path, reads a state file, or can block
---

Rule: Treat hook stdin and state paths as untrusted. (1) Accept session_id and other ids only as [A-Za-z0-9_-]{1,128} before they become file names. (2) Claim once-per-session markers with O_CREAT|O_EXCL. (3) Open any path from stdin or from a state directory (transcript, state files that hooks and doctor read) only if is_file(): a FIFO or device at that path blocks the reader. (4) A blocking hook needs a once-only guard via stop_hook_active so it never loops.
When: Whenever a hook or doctor check writes state, reads a state file, or can block (Stop, SubagentStop).
Why: The payload comes from the harness but carries model-influenced values (paths, ids); a hostile id becomes a path or glob, a FIFO hangs the session, and a blocking hook without a guard loops forever. Same class as the glob-id injection that review missed. The FIFO case hit again in doctor's state-file reads.
Evidence: ai_mem/hooks/{__init__,reflect_reminder,retro_check}.py and the doctor's state reads.
