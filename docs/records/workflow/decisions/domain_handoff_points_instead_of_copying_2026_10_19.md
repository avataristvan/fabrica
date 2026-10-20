id: domain_handoff_points_instead_of_copying_2026_10_19
type: domain
area: workflow
perspective: agent
created: 1792419304.17404
edges: [{"target_id": "domain_reflect_yields_handoff_and_record_candidates_2026_10_10", "edge_type": "derived_from"}, {"target_id": "pattern_handoff_is_overwritten_not_appended_2026_10_12", "edge_type": "related"}]
cue: I am writing a handoff or FOCUS.md at the end of a session
---

Decision: The /reflect handoff points instead of copying: anything already in a spec, plan, record, commit or source is named by path or id, not repeated. It also gets a "Start with" field naming the skill or command the next session loads first.
Why: Copies drift from their origin and bloat the handoff; a pointer stays true. Naming the first skill gets the next session to the right entry point. From Pocock's handoff skill ("suggested skills"); extends the carry-only-conclusions handoff.
Scope: skills/reflect/SKILL.md Step 5.
