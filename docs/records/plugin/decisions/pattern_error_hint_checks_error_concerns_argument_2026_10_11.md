id: pattern_error_hint_checks_error_concerns_argument_2026_10_11
type: pattern
topic: plugin
perspective: reviewer
created: 1791745726.944636
cue: I am adding a user-facing hint to an error that a use case raised
---

Rule: A hint attached to a use-case error must first check that the error concerns the hinted argument. Prefer a typed exception that carries the argument over matching the error text.
When: Adding user hints to errors in the CLI layer (mem_cli).
Why: mem_cli._link matched the error text to attach a "found at" hint; an error about a different argument with similar text got the wrong hint. Text matching also breaks silently when the message is reworded.
Evidence: review of mem_cli._link (ai_mem/mem_cli.py); follow-up todo_mem_cli_simplify_deferred_from_1b4_2026_10_11.
