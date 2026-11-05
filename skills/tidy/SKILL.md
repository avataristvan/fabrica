---
name: tidy
description: "Bring an area's documents into the Fabrica documentation map: close open handoffs and place loose docs, section by section (FOCUS/BACKLOG, record candidate, experiment, plan, reference, how-to, source, raw data, drop), repoint records that cite a handoff, then delete what is fully placed. Proposes per file, applies docs moves only on approval, hands record candidates to the archivist, never writes records or FOCUS.md. Run it when `mem doctor` (Docs / Not concluded) lists handoffs or loose docs, when /reflect closes a handoff, or after installing Fabrica into an existing project."
---

# Tidy

You bring the documents of one area into the documentation map, `${CLAUDE_PLUGIN_ROOT}/reference/documentation_map.md`. Read it first; if it cannot be read, stop and say so. The map says where each kind of content lives and how long; your job is to apply it to what the area has, with the user's judgment where the content needs it. Arguments (`$ARGUMENTS`) may name an area path or files; then work only on those.

At this boundary follow the Fabrica handoff protocol (skill `fabrica:handoff-protocol`). Ask the librarian once, before the first proposal, with the area path and the topics of the files you are about to place: which of their conclusions are already records? A conclusion that already stands is not proposed again (the archivist recorded much of it the first time).

## Rules

- **Propose, then apply on approval.** For a few files, propose one file at a time, the oldest handoff first, then the loose docs. For many files (more than about five), show one overview table for all of them, with file, its parts, and their targets. The user approves that table once, or says which rows change. A standing approval the user gave in this session also counts. Never change a file that was in no proposal.
- **Delegate per file when the run is large.** Spawn one agent per file or per group of related files, and hand each one the map, the approved targets and the slugs. Collect their record candidates and evidence repoints, and hand those to the archivist once at the end.
- **Never write records, never write FOCUS.md.** Record candidates and evidence repoints go to the archivist. What belongs in FOCUS.md is named in your report for the next `/reflect` (the focus gate); next steps go to the bottom of BACKLOG.md.
- **Never invent content.** An experiment carries only the question, setup, runs and result that the text gives. Where a number or a result is missing, the experiment says so; it does not get one.
- **Keep history.** Move a doc with `git mv` when it moves whole; a frozen file (a `done` experiment, a source) is never edited. No commits: the user commits.
- **Stale state is dropped**, not moved ("device runs kernel #4", "tablet has the test kernel"): git keeps it.
- **Raw data is never referenced.** A path to a log or dump in a handoff is dropped; the numbers the result rests on go into the experiment.

## Steps

1. **See the area.** Run `mem doctor` (from the area) and read its Docs and Not-concluded sections, and `mem lint` for `handoff-cited` and `handoff-shape`. That is the work list. If `mem lint` reports the older record format (`legacy-refs`, `bare-id`), name `mem lint --fix --area <area>` first and do it only on approval: links make the later repoints simpler.

2. **Per file, a proposal.** Read the whole file. Split it into its parts (sections, and inside a section the paragraphs that differ in kind). For each part give one target from the map:

   | part | target |
   |---|---|
   | what is being worked on now, the system's state now | FOCUS.md (named for the next /reflect, not written) or dropped when stale |
   | an open point, a next step | BACKLOG.md, bottom, one `- ` line |
   | a decision or a learning with its reason | record candidate (plain text, for the archivist) |
   | hypotheses, runs, measurements, a result | an experiment `docs/experiments/<slug>/README.md` (new, or an existing slug), status `done` when the result is in the text, `running` when not |
   | a plan with steps or chunks | `docs/plans/<slug>/brief.md` (what, why, decisions) or `chunks.md` (how) |
   | a fact about the system that stays true | `docs/reference/<page>.md` (existing page, or new) |
   | a procedure | `docs/how-to/<page>.md` |
   | research on foreign material, dated | `docs/sources/<slug>.md` (frozen; with the source frontmatter from the map: `type`, `date`, `origin`, `status: unprocessed`) |
   | a path to raw data, history of how it went, stale state | drop |

   A test plan whose results stand in a later handoff becomes one experiment: merge the hypotheses and the runs. A procedure goes to `docs/how-to/`, and the experiment links to it. A fact for `docs/reference/` whose currency you cannot check gets `(as of <date>, from <experiment>)`. Before you move a doc, run `git grep` for its path. Code that still links it does not stop the move, because code does not link docs (see the map). Name each hit in the report as "clean up the comment the next time this file is touched". The experiment or record names that code path from the doc side.

   Show the proposal as one table per file: part (its heading or first words), target, and for experiments the slug and status. Below it: the records that cite this file (`handoff-cited`) and what their evidence becomes (the experiment's path, or the commit `<sha>:docs/handoff-<date>.md` from `git log -1 --format=%h -- <file>` when the content does not move). Ask: "Apply, change, or skip this file?"

3. **Apply what was approved.**
   - Write or extend the docs (experiments with the frontmatter from the map; reference and how-to pages edited in place). `mem lint` must stay clean for them (`lint_after_write` checks experiments and handoffs as you write).
   - Append the BACKLOG lines.
   - Collect the record candidates and the evidence repoints of this file.
   - When every part of the file has a place, delete it (`git rm`, or plain delete when the area is not versioned). A loose doc that moves whole is moved with `git mv`.

4. **Hand over to the archivist** once per run, with all candidates and repoints:

   ```
   Agent(subagent_type="fabrica:archivist", prompt="Area: <area path>.\nRecord candidates:\n<candidates>\nEvidence repoints (records that cite a handoff):\n<record path>: <old evidence> -> <new evidence>")
   ```

   Show the user its integration report.

5. **Check and report.** Run `mem lint` and `mem doctor` again, after the archivist has repointed. Before that, "no record links to it" and "processed source no record points to" are expected for what you just placed. Report in a few lines: files closed, files moved, experiments created (and their status), BACKLOG lines added, what belongs in FOCUS.md for the next `/reflect`, what the archivist did, what is still open and why.

## In a reflect

When `/reflect` closes the previous handoff, it runs this skill on that one file; the user's answer to the proposal is the only question.
