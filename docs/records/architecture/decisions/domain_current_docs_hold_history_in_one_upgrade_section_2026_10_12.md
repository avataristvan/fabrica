id: domain_current_docs_hold_history_in_one_upgrade_section_2026_10_12
type: domain
area: architecture
perspective: the-coder
created: 1791786665.196913
superseded_by: domain_current_docs_may_carry_one_short_history_section_2026_10_12
valid_until: 1791839311.652372
edges: [{"target_id": "domain_docs_split_into_documentation_and_sources_2026_10_10", "edge_type": "derived_from"}, {"target_id": "domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12", "edge_type": "related"}]
cue: Writing or rewriting a current doc that has to mention how the system used to work
---

Decision: Current docs describe history only in one upgrade section (README.md "Upgrading from the earlier versions") and link docs/sources/ and UPGRADING.md for detail. Current docs carry no history banners; they are rewritten instead.
Why: A banner on a current doc leaves the retired description in place for the reader to misread; rewriting keeps current docs current while the evidence stays in docs/sources/. This applies the classification of domain_docs_split_into_documentation_and_sources_2026_10_10 and keeps the doctor's retired-system check quiet without banners.
Scope: Current documentation (README.md, docs/tutorial, how-to, reference, explanation). Plan and rollback docs that stay alive carry a marker, see todo_decide_plan_and_rollback_docs_banner_or_sources_2026_10_12. Evidence: README.md "Upgrading from the earlier versions".
