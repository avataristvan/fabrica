type: learning
topic: architecture
perspective: reviewer
created: 1791821372.207719
cue: I am judging whether the doctor retired-system check or a rollback-doc marker really enforces the docs rule
---

Observed: (1) The README label "retired, kept until removal" for the rollback doc acts as a de-facto marker. (2) The rewritten docs of the docs-rewrite pass satisfy the retired-system check partly through paraphrase ("vector database store", "tool server").
Cause: The check is a keyword heuristic, so softer wording and a label both satisfy it.
Evidence: anchor-lint review of the docs-rewrite pass. Bears on todo_decide_plan_and_rollback_docs_banner_or_sources_2026_10_12 and todo_doctor_retired_system_check_sidestepped_by_softer_wording_2026_10_12.

## Edges

- related: [domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12](../decisions/domain_cutover_removed_mcp_server_and_chroma_stack_2026_10_12.md)
- related: [domain_current_docs_may_carry_one_short_history_section_2026_10_12](../decisions/domain_current_docs_may_carry_one_short_history_section_2026_10_12.md)
- related: [domain_doctor_retired_system_check_is_retired_migration_is_tagged_2026_11_02](../decisions/domain_doctor_retired_system_check_is_retired_migration_is_tagged_2026_11_02.md)
