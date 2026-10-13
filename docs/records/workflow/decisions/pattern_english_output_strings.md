id: pattern_english_output_strings
type: pattern
area: workflow
created: 1779055358.898205
cue: I am about to write user-visible strings or error messages in ai-mem code.
---

Rule: Keep all user-facing strings in ai-mem code in English.
When: Writing output strings in hooks, server tools, or any code that produces text shown to users.
Why: ai-mem is an international tool — German strings limit its audience and break the convention.