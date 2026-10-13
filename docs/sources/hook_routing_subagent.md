---
type: retired-system
date: 2026-10-04
origin: memory entry hook_routing_subagent, exported to docs/reference/ on 2026-10-04 (last status line 2026-10-04)
status: processed
---

## What the source says

# Subagent Hook Routing

`ai_mem/agent_context.py` detects session type at hook time to route context injection correctly.

**Detection modules:**
- `detect_for_session_start(stdin_json)` — parses transcript; ignores inherited env type
- `detect_for_hook(stdin_json)` — tries CLAUDE_ENV_FILE first; falls back to transcript parsing
- `write_to_env_file(ctx)` — appends AI_MEM_HOOK_DEPTH + AI_MEM_AGENT_TYPE for downstream hooks

**Routing table (d = nesting depth), updated 2026-09-13 -- UserPromptSubmit column removed, hook retired (see arch_decision_userprompt_push_removed_2026_09_13); PreToolUse was already removed 2026-09-12:**

| Session | SessionStart |
|---------|:---:|
| d=0 main | ✓ |
| the-coder (d≥1) | ✓ |
| Explore/Plan/reviewers (d≥1) | ✗ |
| unknown subagent | ✗ |

SessionStart is now the only automatic injection point left; `detect_for_hook` (the fast-path env-based detector used by non-SessionStart hooks) has no remaining caller of its own now that both PreToolUse and UserPromptSubmit are retired -- it stays in the codebase for any future hook that needs it, and PostToolUse's own gating is separate (access-tracking, not context injection, so it isn't part of this routing table at all). the-coder does its own explicit task-scoped `mem_query` pulls instead (agent-level `subagent.the-coder` + project-level active collection) from within its own prompt -- see the-coder.md's "Session Start — Query Prior Experience" section. Global-level relies on SessionStart's `[available: global]` block rather than a query.

Note: Stop hook not wired — replaced by /reflect skill (manual).

**Context injection whitelist:** `INJECT_CONTEXT_AGENTS = _BUILTIN_INJECT_AGENTS | _user_inject` (agent_context.py, computed at import time). The built-in set is a fixed `frozenset({"general-purpose"})` only -- it is NOT `{"the-coder", "general-purpose"}` as a constant. `the-coder` and any other extra agents are config-dependent: they come from `~/.config/ai-mem/agents.yaml`'s `inject_agents` list and get merged into the whitelist at import. Membership in the merged set no longer implies that an agent receives ai-mem content: since arch_decision_sessionstart_pull_based_2026_09_16 SessionStart prints only a one-line routing hint by default, and subagents get no SessionStart output at all (limitation 5); whether an agent uses ai-mem is decided in its own prompt (explicit mem_query/mem_add). The set differs by machine/config.

**Known limitations:**
1. CLAUDE_ENV_FILE propagation uncertain: env vars may not reach subagent subprocess envs → d≥1 hooks fall back to transcript parsing. (Lower-stakes now that only SessionStart, which always runs detect_for_session_start's full transcript parse rather than the env fast-path, depends on this.)
2. Signature brittleness: agent type detection matches fixed phrases; upstream description changes make signatures stale. Update `_SIGNATURES` in agent_context.py.
3. Unknown subagents skipped: custom agents with no matching signature receive no context. Workaround: add to `_SIGNATURES` or `INJECT_CONTEXT_AGENTS` (i.e. to agents.yaml's inject_agents). Note: pr-review-toolkit:code-reviewer (the code-level, not chunk-plan-level, reviewer) is NOT in this whitelist -- it gets zero ai-mem context by design, unchanged by this update.
4. No production validation: all tests are unit-only with mocked transcripts.
5. Caveat confirmed by real usage, not just limitation #4: eval_experience_index_ab_2026_09_21 found subagents receive no SessionStart output at all in practice -- the ✓ marks in the routing table above describe this module's routing logic, not what the harness actually delivers to a subagent session. This contradicts the assumption behind design_three_tier_pull_the_coder_2026_09_12 that a SessionStart hook fires for the-coder; the-coder's own explicit mem_query pulls (noted above) exist because of this gap, not in addition to a working hook.

Status 2026-10-04: PostToolUse access tracking is retired; nothing tracks access anymore (domain_file_backend_replaces_chroma_2026_10_04).

## Our notes

