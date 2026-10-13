id: arch_expert_agent_collections
type: domain
area: architecture
created: 1778534874.026325
edges: [{"target_id": "arch_decision_sessionstart_pull_based_2026_09_16", "edge_type": "related"}]
---

Decision: subagent.<name> collections serve as a cross-project experience layer (expert agent collections). Status 2026-05-29: fully implemented.

Why: Cold start in new projects arises not because retrieval is bad, but because prior experience lives only in project collections. Epistemologically: cold start is fine (no false trust); a problem arises only when an agent COULD HAVE prior experience but does not have it.

Scope: All subagent.* collections. Reflect routing: /reflect step 4.5 + negative_ids in step 3.5. mem_dream --expert iterates over all subagent.* collections with an expert focus hint. Reading is pull-based: agents explicitly query their subagent.<name> collection from their own prompt, SessionStart names it only in the routing hint (docs/reference/hooks.md, arch_decision_sessionstart_pull_based_2026_09_16); subagents receive no SessionStart output (learning_subagents_no_sessionstart_output_2026_10_04, docs/sources/hook_routing_subagent.md).
