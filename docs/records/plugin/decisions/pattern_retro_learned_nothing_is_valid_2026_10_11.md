id: pattern_retro_learned_nothing_is_valid_2026_10_11
type: pattern
topic: plugin
perspective: agent
created: 1791725661.852841
edges: [{"target_id": "domain_hooks_enforce_that_roles_decide_how_2026_10_10", "edge_type": "related"}]
cue: I am designing or checking the [retro] block rule, or a trivial subagent task has nothing to report as learned
---

Rule: `learned: nothing` is a valid retro answer. retro_check must block a missing `learned` field but accept an explicit "nothing".
When: Designing retro_check; trivial subagent tasks.
Why: An invented learning adds noise to the records. A deliberate "nothing" is a statement, a missing field is an omission, and only the omission is a ritual failure. Raised by the user as a question; the agent agreed.
