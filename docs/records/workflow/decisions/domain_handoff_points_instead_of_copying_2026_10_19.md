type: domain
topic: workflow
perspective: agent
created: 1792419304.17404
cue: I am writing a handoff or FOCUS.md at the end of a session
---

Decision: The /reflect handoff points instead of copying: anything already in a spec, plan, record, commit or source is named by path or id, not repeated. It also gets a "Start with" field naming the skill or command the next session loads first.
Why: Copies drift from their origin and bloat the handoff; a pointer stays true. Naming the first skill gets the next session to the right entry point. From Pocock's handoff skill ("suggested skills"); extends the carry-only-conclusions handoff.
Scope: skills/reflect/SKILL.md Step 5.

## Edges

- derived_from: [domain_reflect_yields_handoff_and_record_candidates_2026_10_10](../../architecture/decisions/domain_reflect_yields_handoff_and_record_candidates_2026_10_10.md)
- related: [pattern_handoff_is_overwritten_not_appended_2026_10_12](pattern_handoff_is_overwritten_not_appended_2026_10_12.md)
- related: [domain_handoffs_point_to_records_never_back_closed_and_deleted_2026_11_05](domain_handoffs_point_to_records_never_back_closed_and_deleted_2026_11_05.md)
- related: [domain_links_between_code_and_docs_go_from_docs_to_code_2026_11_05](domain_links_between_code_and_docs_go_from_docs_to_code_2026_11_05.md)
