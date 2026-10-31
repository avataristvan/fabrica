# Records

This directory is the record of this area: decisions, learnings, todos and `user` records, one Markdown file per entry. The files are the store; there is no database behind them. Records are not limited to software architecture; any topic (marketing, pricing, ops, ...) fits.

- **Layout:** `<topic>/<kind>/<id>.md`, kind `decisions/` (domain, pattern, anti-pattern), `learnings/` (observed facts), `todos/`, `user/`. `FOCUS.md` holds the current focus as plain text and is overwritten.
- **Filename = record id** (e.g. `domain_area_path_is_the_address_of_knowledge_2026_10_10.md`).
- **Who writes:** the archivist agent (via `/reflect`) and the user, through the `mem` CLI. Other agents ask the librarian and hand over record candidates.
- **Edges:** a decision based on a learning carries a `derived_from` edge to it; other edge types and cross-area edges are in `docs/reference/record-format.md`, together with the frontmatter schema and its fixed field order.
- **Superseded, not deleted:** a replaced record gets `superseded_by: <id>` and stays as history (`mem link NEW OLD --type supersedes`).
- **`INDEX.md`** is the entry point: a compact `id | area | type | title | status` table of every record. Read it first instead of grepping every file. The `mem` write commands keep it current; `mem lint --fix` rebuilds it.
