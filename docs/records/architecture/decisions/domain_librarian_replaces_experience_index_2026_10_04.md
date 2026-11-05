type: domain
topic: architecture
created: 1791109782.687738
cue: I am about to push records, an index or cue lines into SessionStart (or other always-loaded context) instead of a pointer to the librarian
---

Decision: SessionStart pushes no memory content anymore. The experience index block (situation -> entry lines from cues) is removed; instead the hook prints one line pointing at <repo>/docs/records/ (FOCUS.md, INDEX.md) and the librarian agent. The librarian reads the record files by judgment, including each record's `cue:` frontmatter line (cues persisted to files since 2026-10-04), and only falls back to mem_* tools for collections without record files.
Why: The user measured ai-mem at ~5% context load on the first prompt of a session and switched hard from push to pull. The index alone was ~3,700 chars (~900 tokens) per session; the pointer is ~340 chars. A pointer keeps the trigger that eval_pull showed is necessary (agents don't pull unless something in context points at memory) without pushing content. Measured hook output alone does not explain 5% -- MCP tool schemas are the likely remainder (unverified, check with /context).
Scope: hook.py default path (never opens the DB), examples/agents/librarian.md (file-first procedure), README/docs/reference/hooks.md. session_start_index setting removed; verbose mode unchanged until [available] is retired.

Addendum 2026-10-04: The 'MCP schemas are the likely remainder' guess is answered by [learning_context_load_after_pull_switch_2026_10_04](../../evaluation/learnings/learning_context_load_after_pull_switch_2026_10_04.md) -- the schemas are deferred, so the original ~5% stays unexplained (window size unknown). Open risk: a pointer line may behave like the baseline arm of [eval_experience_index_ab_2026_09_21](../../evaluation/learnings/eval_experience_index_ab_2026_09_21.md) (1/3) rather than the index arm (3/3); the librarian scored 5/6 and 4/6 only when asked. Untested; see todo_pull_trigger_points_per_situation.

## Edges

- related: [eval_experience_index_ab_2026_09_21](../../evaluation/learnings/eval_experience_index_ab_2026_09_21.md)
- related: [arch_decision_sessionstart_pull_based_2026_09_16](arch_decision_sessionstart_pull_based_2026_09_16.md)
- derived_from: [domain_records_model_replaces_chroma_2026_10_04](../../records/decisions/domain_records_model_replaces_chroma_2026_10_04.md)
- related: [learning_librarian_scope_was_the_game_changer_2026_10_11](../learnings/learning_librarian_scope_was_the_game_changer_2026_10_11.md)
