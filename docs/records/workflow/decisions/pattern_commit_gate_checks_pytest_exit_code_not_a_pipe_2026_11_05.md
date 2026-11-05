type: pattern
topic: workflow
perspective: agent
created: 1793905708.601873
cue: You are about to chain the test run and git commit in one shell command, e.g. pytest piped to tail then &&.
---

Rule: A commit gate checks pytest's own exit code. Run pytest into a file, keep `rc=$?`, and commit only on rc 0; never `pytest ... | tail -1 && git commit`.
When: Chaining tests and a commit in one shell command.
Why: In a pipe the chain sees tail's exit code, so the commit goes through on a red suite. It happened twice on 2026-11-05: one commit with a red test from uncommitted changes, one really red, fixed by the next commit; both were later squashed into cb0058f.
