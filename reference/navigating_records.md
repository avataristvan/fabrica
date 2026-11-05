# Navigating records

The shared reading guide for every role that reads ai-mem records: the librarian (which
answers questions) and the archivist (which integrates new records). Both read the same
way, so that they judge in the same way what belongs together. Each agent's own
definition adds only its rules for answering or for writing.

## Areas: where knowledge lives

An **area** is a folder that holds `docs/records/`. Knowledge is addressed by that folder,
not by a collection name, a git repo or a CLAUDE.md.

- **Finding the area of a path:** walk up from the path to the nearest ancestor
  (inclusive) that has a `docs/records/` directory. A path inside `docs/records/` belongs to
  the folder that holds it. A git worktree counts as its main checkout. An area need not
  be a git repo and need not have a CLAUDE.md.
- **Nested areas** are separate areas. A folder with its own `docs/records/` below another
  area is not part of the outer one; its records are not the outer area's records.
- **The caller names the area** as a path. A collection name (`repo.<name>`, `global`,
  `workspace`, `subagent.<name>`) is not an address any more: records that lived there now sit in
  the area of the topic they describe. Workspace-wide tooling and environment knowledge sits in the
  root area `<workspace root>/docs/records/`.
- **Looking up an id:** `mem find <id>` (read-only) lists every area that holds a record or
  `docs/reference/` doc with that id, as the reference `mem link` accepts from your area. Use it
  before concluding that an id does not exist.
- **Cross-project knowledge:** general practice sits in the area of the topic (for example
  `ai-architecture`) or in the root area `<workspace root>/docs/records/`; check the root area too
  when the question is about the workspace as a whole.

## Three kinds of knowledge

They age differently and are never mixed:

| Kind | Where | How it changes |
|---|---|---|
| **State** | `docs/records/FOCUS.md`, `docs/handoff-<date>.md` | overwritten; git keeps the history |
| **Decisions and learnings** (records) | `docs/records/<topic>/<kind>/<id>.md` | only added to; outdated ones are superseded, not deleted |
| **Evidence** (sources) | `docs/sources/<slug>.md`, raw material in `docs/sources/<slug>/` | never changed |

- State says what is going on now. It is the place for "what next", never for "why".
- A record carries a decision or a lesson together with its reason.
- A source says what was observed or said. A record that rests on a source names it,
  with an `Evidence:` line (a path) or a `derived_from` edge when the source is a record.
- `docs/reference/` holds background documentation of how the system is built today.
  It is neither a record nor evidence.

## A record file

Layout: `docs/records/<topic>/<kind>/<id>.md`. `<kind>` follows from the type:
`decisions/` (`domain`, `pattern`, `anti-pattern`), `learnings/` (`learning`), `user/`
(`user`). The topic is a plain subfolder such as `architecture`; its
frontmatter key is `topic:` (old records may still say `area:`, the same thing).

Each file starts with `key: value` lines, then `---`, then the text, then (when it has
edges) a closing `## Edges` section. The file name without `.md` is the record's name; there is
no separate id.

| Key | Meaning |
|---|---|
| `type` | `domain`, `pattern`, `anti-pattern`, `learning`, `user` |
| `topic` | the topic folder (old records may still say `area:`) |
| `perspective` | optional: whose knowledge or experience it is (`user`, `agent`, or a role such as `coder`, `reviewer`). A lens, not a location: it never decides where the file lives. Records of kind `user` also carry `perspective: user`. |
| `created` | when the record was first written |
| other keys | kept as written (hand-written records may carry some) |
| `cue` | optional, always last: one sentence naming the situation in which the record helps |

Bodies have a shape by type: `Decision: / Why: / Scope:` (domain), `Rule: / When: / Why:`
(pattern), `Tried: / Failed because: / Instead:` (anti-pattern),
`Observed: / Cause: / Evidence:` (learning). Hand-written records may deviate (bold labels,
headings); read them for meaning, not for form.

### Edges

Edge types: `derived_from` (the source rests on the target, e.g. a decision on a
learning), `causes`, `fixes`, `contradicts`, `confirms` (a later record shows the target
held again), `supersedes`, `related`; `superseded_by` marks the record as overtaken. An edge
is stored on its source record only, as one line of its `## Edges` section:

```
- derived_from: [learning_x](../../search/learnings/learning_x.md)
```

- The link is relative to the record file. Resolve it from the record's folder and `Read`
  the file it names; a link that leaves `docs/records/` leads into another area (or to a
  source in `docs/sources/`, a plain doc in `docs/reference/`).
- The text names records the same way, as links (`Evidence: [learning_x](...)`). Older
  records may still name them bare, or as `<rel>:<name>`; then `Glob` `**/<name>.md`.
- `supersedes` never crosses areas. Across areas, records relate by `related` or
  `derived_from`.

## The catalogue files

- `docs/records/INDEX.md`: one row per record (`record | topic | type | title | status`);
  the record column is a link to the file.
  Hand-kept areas may have a different INDEX or none; then `Glob` the folder.
- `docs/records/FOCUS.md`: what is being worked on right now (plain text, state).
- `cue:` lines: the index of "situation -> record". A cue is written from the point of view
  of someone who does not yet know the answer: what they are doing or about to do.

## Reading procedure

Work from cheap and broad to expensive and narrow. Judgment happens at every step: you
choose candidates because their *meaning* plausibly bears on the question, not because a
string matched.

1. **Catalogue.** Read the area's `INDEX.md`. If the question is about the current state
   or what comes next, read `FOCUS.md` and `BACKLOG.md` (and the newest `docs/handoff-*.md`
   if there is one).
2. **Situation cues.** `Grep` for `^cue:` under the area's `docs/records/` (and `global`
   when relevant). If the situation at hand matches a cue, it points straight at the
   record to read.
3. **Pick candidates by judgment.** From titles and cues, decide which records could
   plausibly bear on the question. Prefer records whose title *means* the same thing over
   ones that merely share a keyword. Zero candidates is a valid outcome.
4. **Read the candidates** (the INDEX row links the file; `Glob` `**/<name>.md` if unsure). Does the text actually bear on the question, or
   did the title mislead you? Drop what does not hold up. Note each record's
   `perspective:` when it has one.
5. **Follow edges, one hop.** `superseded_by` -> read the successor; that is the current
   answer. But if the older record carries the "Why" the successor dropped, keep the
   older record too. Superseded does not mean discard. The other `## Edges` links
   (`derived_from`, `causes`, `fixes`, `contradicts`, `confirms`, `related`) may point at a
   better answer: follow one hop when it looks relevant, then stop. A link into another
   area is followed the same way. An `Evidence:` path leads to the source, when proof
   is asked for.
6. **Background.** `Glob` `docs/reference/*.md` and read a reference doc when the question
   is about how the system is built rather than about a decision.
7. **Fallback.** `Grep` the question's key terms across `docs/records/` and
   `docs/reference/`.
