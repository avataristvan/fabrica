# Areas and kinds of knowledge

Where knowledge lives and how it ages. This page replaces the earlier description of collections and automatic scoping; the retired model is covered in the history at the end. Exact syntax is in the [record format](../reference/record-format.md).

## Areas: the folder is the address

Knowledge is addressed by the folder of its **area**: the nearest ancestor of the work that has `docs/records/`. `mem context` prints it. A `CLAUDE.md` is not required (it helps where sessions start: charter, routing), a git repository is not required, and moving an area needs no migration, because nothing refers to it by name or by absolute path.

- **No catch-all level, no personal area.** Every record goes to the area of its topic. Cross-cutting topics get an area of their own, for example one for how you work with AI in general and one for machine and tooling facts. Whose knowledge a record is goes into its `perspective:` field, which is a lens for answers, not a location and not a filter.
- **A context map, not a hierarchy.** How areas relate is a map of who hands what to whom. Edges between records point across areas as `<relative-area-path>:<id>`, never as absolute paths; `mem context --map` prints the areas and the edges between them.
- **A record is stored once**, in the area where its topic belongs. Other areas reach it through an edge or by asking the librarian, which follows edges one hop, also across areas.

## Three kinds of knowledge

They age differently and are never mixed:

| Kind | Where | How it changes |
|---|---|---|
| **State** | `FOCUS.md`, `docs/handoff-<date>.md` | overwritten |
| **Decisions and learnings** | `docs/records/` | only added to; outdated ones are superseded, not deleted |
| **Evidence** | `docs/sources/<slug>.md`, raw material in `docs/sources/<slug>/` | never changed |

- **State** says where the work stands. It is rewritten at each boundary and git keeps the history.
- **Records** are the reasons: a decision (`domain`, `pattern`, `anti-pattern`), a learning (what was observed), a todo, or a `user` record (a role's yardstick). A decision links back to the learning it rests on. A record that is outdated is superseded, and the old one keeps its reasoning and is flagged, because the reason it was wrong is itself knowledge.
- **Evidence** is a talk, a paper, a measurement, a past design document or the documentation of a retired system. Its claims are frozen; a learning that rests on it names it. Internal sources count as much as external ones.

`docs/reference/` and the rest of `docs/` are documentation of the current system, rewritten when the system changes. Anything that only describes a system that is gone belongs in `docs/sources/` instead: it is neither deleted nor left misleading as current documentation (`domain_docs_split_into_documentation_and_sources_2026_10_10`). `mem doctor` checks this split.

## Record types

| Type | Shape | Use for |
|---|---|---|
| `pattern` | `Rule: / When: / Why:` | a reusable technique or best practice |
| `anti-pattern` | `Tried: / Failed because: / Instead:` | a documented failure mode |
| `domain` | `Decision: / Why: / Scope:` | business or domain knowledge: why a rule exists, a constraint, as opposed to a coding technique |
| `learning` | `Observed: / Cause: / Evidence:` | what was seen, with its proof |
| `todo` | free-form | open work; a closed todo becomes a result record |
| `user` | free-form | what the user values, pulled at review as the yardstick |

Write a `domain` record the moment the knowledge surfaces, not at the end of a session. No hook forces this, because recognising a domain decision takes judgment a deterministic check cannot make.

## Setting a first focus

Write the first records yourself ([tutorial](../tutorial/first-records.md)), or let them come from work: `/ai-mem:reflect` hands what a session decided and learned to the archivist, which writes the records. Records written from work are better scoped than records split out of a CLAUDE.md by heading, which an earlier automatic seeder did and which was removed. `/ai-mem:setup` wires your teams and CLAUDE.md so that sessions ask the librarian and deliver record candidates ([how-to](../how-to/set-up.md)).

## History: collections

Before areas, records were grouped into named collections (`repo.<name>`, `workspace`, `global`, `subagent.*`), detected from the working directory and passed explicitly to every tool call. Naming by directory regressed once on a reinstall and left a catch-all that dumped unrelated entries into sessions, which is why the folder became the address. The model, its detection table and its lifecycle features (expiry, forgetting curve) are kept as evidence: [sources/key_invariants.md](../sources/key_invariants.md) and the records `arch_workspace_root_collection_naming` and `fix_workspace_collection_catchall_2026_07_31`. The upgrade path from collections to areas is in `UPGRADING.md` ("Collections -> areas").
