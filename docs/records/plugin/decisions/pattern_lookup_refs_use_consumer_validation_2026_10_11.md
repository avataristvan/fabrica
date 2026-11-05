type: pattern
topic: plugin
perspective: the-coder
created: 1791745726.471122
cue: I am writing a "found at" or suggestion helper that prints refs another command will consume
---

Rule: A lookup that emits references for another command must use that command's validation and reader scope, not its own.
When: Writing a "found at" / hint / suggestion helper (e.g. mem find or the mem link hint) whose output the user pastes into another command.
Why: With its own looser scope the helper suggests refs the consumer then rejects, so the hint misleads exactly when it is needed. Found while building mem find and the mem link hint, fixed by qualifying refs through the consumer's own rules.
Evidence: ai_mem/mem_cli.py (_locate, _link).

## Edges

- related: [pattern_bubble_up_lookup_stops_at_root_2026_10_11](pattern_bubble_up_lookup_stops_at_root_2026_10_11.md)
- related: [pattern_error_hint_checks_error_concerns_argument_2026_10_11](pattern_error_hint_checks_error_concerns_argument_2026_10_11.md)
