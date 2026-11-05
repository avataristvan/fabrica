type: learning
topic: plugin
perspective: the-coder
created: 1791833918.376278
cue: I am writing a mechanical eval that grades the output of claude -p runs of a skill that spawns agents
---

Observed: `claude -p --output-format json` `result` holds only the last assistant message. When a skill spawns a background agent, that agent's real output sits in an earlier message, so an eval must grade every assistant text from stream-json. eval1 had 3 false failures; eval2 passed 18/18 after the change.
Cause: The final message is a wrap-up; the substantive output was emitted earlier.
Evidence: scripts/eval_setup/run.py.
