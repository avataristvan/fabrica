type: learning
topic: workflow
created: 1791668231.552412
cue: when validating ids or names that end up in frontmatter, INDEX.md or a filename
---

Observed: `is_safe_entry_id` only rejects path and glob metacharacters. Ids with newlines, tabs, other control characters or leading/trailing spaces pass and can corrupt frontmatter and INDEX.md.
Cause: the validator was written against path and glob injection only ([learning_glob_id_injection_missed_by_review_2026_10_04](../../architecture/learnings/learning_glob_id_injection_missed_by_review_2026_10_04.md)), not against format injection.
Evidence: reviewer finding (confidence 85) on the first mem CLI chunk. `mem_cli._bare_id` adds isprintable and strip checks (c5f630e). The MCP server's mem_add, which lacked them, is gone since the cutover.

## Edges

- related: [learning_glob_id_injection_missed_by_review_2026_10_04](../../architecture/learnings/learning_glob_id_injection_missed_by_review_2026_10_04.md)
- related: [learning_symlink_following_walk_fixed_python_312_2026_10_15](learning_symlink_following_walk_fixed_python_312_2026_10_15.md)
