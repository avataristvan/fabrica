type: domain
topic: records
perspective: user
created: 1793885900.173261
cue: You are designing a reference between records, or wonder why records have no id line.
---

Decision: Records carry no id. The file name is the record's name, and every reference between records is a relative Markdown link: edges and superseded_by in a closing `## Edges` section, mentions in the body, rows in INDEX.md.
Why: Ids were a ChromaDB legacy; links are clickable, readable without the librarian, and checkable by lint. Broken links on a move are handled by tooling: `mem move` relinks what it wrote, a retype relinks referrers in the same area, `mem lint` link-stale / `--fix` heals the rest, legacy-refs and bare-id migrate old records. An ordinal in a list ("Step 5") is not an id; an id in the DB sense is an (alpha)numeric reference to an entry elsewhere.
Scope: All record files, INDEX.md, docs/reference/record-format.md.
Evidence: ai_mem/infrastructure/record_links.py, ai_mem/infrastructure/adr_markdown.py, ai_mem/records_lint.py, tests/infrastructure/test_record_links.py; 282 records migrated and checked semantically against git HEAD (no loss).

## Edges

- supersedes: [domain_record_edges_single_line_json_with_ids_2026_10_23](domain_record_edges_single_line_json_with_ids_2026_10_23.md)
