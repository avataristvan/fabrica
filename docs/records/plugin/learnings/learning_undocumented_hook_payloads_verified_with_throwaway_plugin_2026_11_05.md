type: learning
topic: plugin
perspective: agent
created: 1793905709.089836
cue: You are writing a hook that reacts to a skill or command invocation and the payload shape is not documented.
---

Observed: Verified 2026-11-05 with a fresh `claude -p` run and a throwaway plugin that dumps stdin: a typed plugin skill fires UserPromptExpansion with command_name "<plugin>:<skill>" and command_source "plugin" (and no PostToolUse Skill); a model-invoked skill fires PostToolUse with tool_name "Skill" and tool_input.skill "<plugin>:<skill>".
Cause: The focus gate rests on these payloads; a transcript scan was rejected because the JSONL format is internal and written asynchronously.
Evidence: ai_mem/hooks/focus_gate.py; the focus_gate row in docs/reference/hooks.md. Rule drawn: verify an undocumented payload this way before building on it.

## Edges

- related: [learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12](learning_plugin_mechanics_verified_claude_2_1_296_2026_10_12.md)
