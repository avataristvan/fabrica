type: pattern
topic: plugin
perspective: reviewer
created: 1791745727.181161
cue: I am parsing JSON or frontmatter edges from a file or payload I do not control
---

Rule: For untrusted JSON, catch RecursionError as well as ValueError around json.loads.
When: Parsing untrusted JSON, frontmatter or edge lists (hooks, doctor, lint).
Why: Deeply nested input raises RecursionError, which is not a ValueError and escapes `except ValueError`; in a hook or doctor that is a crash on hostile input (hooks must not raise).
Evidence: parse_edges / edge_targets in ai_mem (the record-edge parsing helpers).

## Edges

- related: [pattern_hook_stdin_is_untrusted_2026_10_11](pattern_hook_stdin_is_untrusted_2026_10_11.md)
- related: [pattern_tool_argument_ids_are_hostile_input](../../../../../docs/records/general/decisions/pattern_tool_argument_ids_are_hostile_input.md)
