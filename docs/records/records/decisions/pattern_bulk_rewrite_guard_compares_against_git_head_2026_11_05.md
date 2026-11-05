type: pattern
topic: records
perspective: agent
created: 1793885902.077812
cue: You are writing or verifying a bulk rewrite or migration of records.
---

Rule: A migration guard compares against the committed state (git HEAD), not only the file before the rewrite.
When: Writing or verifying any bulk rewrite of records.
Why: Uncommitted user edits otherwise look like migration loss or hide it. In the 282-record migration, 2 differences were the user's own uncommitted edge edits, preserved.

## Edges

- related: [domain_records_have_no_id_links_by_file_name_2026_11_05](domain_records_have_no_id_links_by_file_name_2026_11_05.md)
