id: todo_frontmatter_value_injection
type: todo
area: workflow
created: 1791668867.25426
edges: [{"target_id": "learning_glob_id_injection_missed_by_review_2026_10_04", "edge_type": "related"}, {"target_id": "todo_simplify_security_reviewer", "edge_type": "related"}]
---

TODO (push security review 2026-10-10): adr_markdown.serialize writes superseded_by, valid_until, created and the extra frontmatter keys unvalidated as key: value lines, so a newline in such a value (e.g. via mem_add metadatas) injects frontmatter lines; only cue is collapsed. Validate or collapse every frontmatter value.
