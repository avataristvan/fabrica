id: learning_dream_failure_hid_cause_stale_model_tag_2026_09_12
type: learning
topic: architecture
created: 1790678547.177738
---

Observed: `mem_dream(collection="repo.ai-mem")` failed with only: "Task failed: Command '['claude', '--print', '--model', 'claude-sonnet-4-6']' returned non-zero exit status 1." -- no information about why. On manual reproduction, `claude --print --model claude-sonnet-4-6` with a trivial prompt actually still ran through (exit 0): the CLI evidently still resolves old tags.
Cause 1 (real and stale, not proven to be THE trigger of this particular failure): `dream_memory.py`'s `MODELS` dict had `"sonnet": "claude-sonnet-4-6"` hard-wired -- an outdated, versioned model tag (current Sonnet according to the environment info is `claude-sonnet-5`). Bit-rot risk: every time Anthropic removes a model tag, mem_dream breaks silently.
Cause 2 (the actual diagnostic blocker): `_call()` in `dream_memory.py` called `subprocess.run(..., capture_output=True, check=True)`. On failure `check=True` raises `subprocess.CalledProcessError`, whose `str()` is ONLY "Command '[...]' returned non-zero exit status N." -- stderr/stdout (where the real error message of the claude CLI lives, e.g. auth error, rate limit, prompt too large) was never read. No try/except around `_dream.execute(...)` in server.py's mem_dream handler -- the exception ran through to the generic MCP task-error wrapper, which shows only `str(exc)`.
Evidence: manual reproduction with exit 0 (both aliases verified live against the real CLI); grep confirmed that no tests depended on the old MODELS values or on `check=True` behaviour.
