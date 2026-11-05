type: domain
topic: records
perspective: user
created: 1793524621.468228
cue: You are reading old records that still say `area:` in frontmatter, or writing a reader or writer for the record format.
---

Decision: the record frontmatter key `topic:` replaces `area:`. The reader accepts both, the writer writes `topic:`, the INDEX.md column is `topic`. Lint codes: `legacy-topic-key` (fixable; `mem lint --fix` renames the key byte-exactly) and `topic-conflict` (both keys with different values; not fixable, --fix skips the file). Internals (`ParsedAdr.area`, `metadata["area"]`) keep their names.
Why: `area:` names the topic folder and was confused with an area (a folder holding docs/records/), flagged by the first-visitor review. All 24 areas of the workspace were migrated (1273 records, every area lint clean afterwards; backup taken first).
Scope: record format, reader, writer, lint. Evidence: commits f5ac1f9, 0ef014d; tests/test_records_lint.py. Decided by the user (todo), implemented by the-coder.

## Edges

- related: [domain_glossary_is_state_per_area_2026_10_19](../../architecture/decisions/domain_glossary_is_state_per_area_2026_10_19.md)
- related: [domain_records_model_replaces_chroma_2026_10_04](domain_records_model_replaces_chroma_2026_10_04.md)
