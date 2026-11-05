type: domain
topic: workflow
created: 1790440444.53689
---

Decision: mem_dream runs after every /reflect (step 6), limited to the active area, mode=hier (Haiku pre-pass, Sonnet synthesis), auto_link and auto_supersede on, auto_delete off. focus_hint names the IDs that were written, cited or linked in the session. DELETE and MERGE need a single collected follow-up question; mechanical UPDATE/SPLIT application goes to a Haiku subagent.
Why: The entry count (>30) is unsuitable as a trigger, a project collection legitimately stays large (user, 2026-09-26). What was marked during a session is thereby placed at the latest at reflect. Small, frequent dream runs instead of rare huge ones (an unscoped hier run blew the CLI limit with 205k tokens). Delegate work to Sonnet and Haiku as far as possible (user's wish). Known price: Dream's own mem_get read calls (INDEX scan, candidate full text) count as deliberate use according to [key_invariants](../../../sources/key_invariants.md) and nudge last_accessed_at — the same definition that mem_cleanup's forgetting curve (stale_after_days) reads as 'was used'. After every /reflect this now runs at least once per session, i.e. more often than before this decision: an entry can look 'fresh' purely through Dream's own maintenance read accesses, without any agent ever having needed it in substance. Alternative not chosen: counting dream candidates instead of the raw count as the trigger (see the superseded [todo_dream_trigger_candidates_not_count_2026_09_25](../../general/learnings/todo_dream_trigger_candidates_not_count_2026_09_25.md)) — would have made the trigger more precise, but would not have addressed the last_accessed_at problem, since Dream reads either way once it runs.
Scope: skills/examples/reflect.md step 6, applies to all collections. Once the MCP server is gone, /reflect Step 6 calls the mem-dream CLI (mem-dream --area) instead of the mem_dream tool.

Addendum 2026-10-04: The 'known price' (mem_get bumping last_accessed_at) no longer exists -- no counters are stored on the file backend.

## Edges

- supersedes: [todo_dream_trigger_candidates_not_count_2026_09_25](../../general/learnings/todo_dream_trigger_candidates_not_count_2026_09_25.md)
- related: [feedback_install_py_user_only](../../general/decisions/feedback_install_py_user_only.md)
- related: [domain_dream_proposes_never_applies_2026_10_13](domain_dream_proposes_never_applies_2026_10_13.md)
- related: [domain_area_path_is_the_address_of_knowledge_2026_10_10](../../architecture/decisions/domain_area_path_is_the_address_of_knowledge_2026_10_10.md)
