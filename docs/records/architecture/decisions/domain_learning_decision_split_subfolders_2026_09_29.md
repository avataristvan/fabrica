type: domain
topic: architecture
created: 1790673307.427194
---

Decision: Decision records are not limited to software architecture (ADR, marketing DR, arbitrary areas) -- each with its learnings. Learnings and decisions are separate entries with a stable type: a learning (observation, measurement, cause) remains a learning; if something is decided from it, a separate decision entry (domain/pattern/anti-pattern) is created, which points to its rationale via a new edge `derived_from` (decision -> learning, outgoing from the decision). New type `learning`, likewise persisted as a file. Storage: docs/records/<area>/decisions/ and docs/records/<area>/learnings/ (folder axis = area, kind below; chosen by the user 2026-09-29). `area` is freely selectable (new areas arise through use) and is a frontmatter field; pattern/anti-pattern/domain remain `type` in the frontmatter and lie under decisions/. INDEX.md lies centrally in docs/records/. Mixed entries (e.g. fix_* typed as domain that contain cause + decision) are split into learning + decision.
Why: (1) The argument for a flat directory (docs/reference/record-format.md, then docs/adr-format.md: 'a type change must not require moving a file') falls away when the type is stable. (2) Today edges from decision files point into the void, because the entries providing the rationale (eval_*, fix_*, arch_decision_*) exist only in ChromaDB -- whoever reads only files (librarian, grep) loses the why. (3) The existing types do not separate learning vs. decision. (4) The rationale belongs in the decision file, hence an outgoing edge from the decision. (5) Area first, because one searches by area (whoever looks for marketing finds decisions and learnings in one place).
Scope: ai-mem record layer (adr_paths.py, markdown_adr_repository.py, adr_index.py, adr_cli.py, adr_markdown.py), EdgeType in domain/memory.py, server.py, docs/reference/record-format.md, docs/decisions -> docs/records, CLAUDE.md references, migration of the existing files in repo.ai-mem.

Addendum 2026-10-04: The kinds now also include todos/ and user/ (KIND_BY_TYPE).

## Edges

- supersedes: [chunk5_adr_backfill_shipped_2026_09_25](../../general/learnings/chunk5_adr_backfill_shipped_2026_09_25.md)
