id: pattern_retrieval_needs_fixed_trigger_in_role_prompt
type: pattern
area: general
perspective: agent
created: 1791140685.017904
---

Rule: A retrieval aid (records, the librarian, user records) only gets used when the prompt of the role that needs it names the trigger: a fixed call point such as 'before reviewing, read the user records' or '/chunk-plan asks the librarian'.
When: Adding memory or knowledge that an agent role should consult.
Why: Agents rarely query memory on their own (ai-mem eval_pull_gap_test_2026_09_20); pushed content brought noise. The working pattern is pull with a fixed trigger: the reviewer template in dev-team.md and the librarian section in the workspace CLAUDE.md.