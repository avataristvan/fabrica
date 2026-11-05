type: learning
topic: architecture
created: 1790678548.382843
---

Observed: The user noticed that a deactivation of ai-mem's 'auto-inject' that they had made took effect nowhere -- SessionStart/UserPromptSubmit kept firing in every session (verified live: both blocks appeared throughout the running session despite the user's expectation to the contrary). Audit: no layer (~/.claude/settings.json, the workspace root's .claude/settings.json, both settings.local.json, ~/.claude.json's disabledMcpServers) had deactivated ai-mem anywhere -- the deactivation had taken effect nowhere, regardless of where/how the user had tried it. In addition: UserPromptSubmit fires on EVERY single message (not only once per session like SessionStart) -- per call up to 4 parallel semantic queries (dilemma warning, anti-pattern warning, context injection, pull-through logging), matching the user's description 'actions that were triggered on every chat -- which is too much'.
Cause: not investigated further why the deactivation took effect nowhere; the audit merely found no layer in which ai-mem was actually deactivated.
Evidence: Audit of the named settings files and ~/.claude.json on 2026-09-13; live observation in the running session.

pseudonymised for publication, 2026-10-31
