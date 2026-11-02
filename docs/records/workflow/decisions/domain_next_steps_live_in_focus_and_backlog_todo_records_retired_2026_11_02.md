id: domain_next_steps_live_in_focus_and_backlog_todo_records_retired_2026_11_02
type: domain
topic: workflow
perspective: user
created: 1793656212.46451
edges: [{"target_id": "domain_records_model_replaces_chroma_2026_10_04", "edge_type": "related"}, {"target_id": "domain_todo_prefix_ambiguity_2026_10_04", "edge_type": "related"}, {"target_id": "domain_three_kinds_of_knowledge_age_differently_2026_10_10", "edge_type": "related"}, {"target_id": "domain_reflect_yields_handoff_and_record_candidates_2026_10_10", "edge_type": "related"}]
cue: I want to note a next step, a todo or a "won't do", or wonder where open work is listed.
---

Decision: Next steps have a single place: FOCUS.md (the work in progress: goal, now, next; not a diary, no list of what was done, no reasons) and BACKLOG.md (ordered, next candidate on top, no sections, no won't-do list). An item lives in exactly one of them; moving is a cut, never a copy; a finished item is deleted (the commit is the increment). Todo records are retired and /reflect no longer produces todo candidates. Mapped onto Scrum: FOCUS.md = sprint goal + sprint backlog, BACKLOG.md = product backlog, /reflect Step 4 = backlog refinement. The name FOCUS.md stays: there is no timebox, so "sprint" would promise something that is not there, and the name is wired across all areas.
Why: Next steps stood in FOCUS.md, todos/ and the handoff, and nothing said which one wins; the duplicate drifted.
Scope: all areas; skills/reflect/SKILL.md Step 4/5, docs/reference/glossary.md (focus, backlog), ai_mem/infrastructure/adr_paths.py (BACKLOG reserved). Narrows domain_records_model_replaces_chroma_2026_10_04 (open todo = file under todos/) and makes domain_todo_prefix_ambiguity_2026_10_04 moot for new work.
