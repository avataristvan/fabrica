# Documentation map: what goes where

The shared map for every role that writes into an area: where each kind of content lives and how long it lives. Agents read it as `${CLAUDE_PLUGIN_ROOT}/reference/documentation_map.md`; the record format itself is in `navigating_records.md` next to it and in the plugin's `docs/reference/record-format.md`.

The rule behind it: every kind of content has one place and one lifecycle. When a piece of text has no place here, it is either state (it belongs in FOCUS.md and rots there on purpose) or it is not worth keeping.

## The map

All paths are relative to the area (the folder that holds `docs/records/`).

| Content | Place | Lifecycle |
|---|---|---|
| Work in progress; the system's state now; work running in parallel | `docs/records/FOCUS.md` | overwritten; changed through `/reflect` |
| Open points, ordered, the next candidate on top | `docs/records/BACKLOG.md` | lines move; a finished line is deleted |
| Decision, learning, pattern | `docs/records/<topic>/<kind>/<name>.md` | superseded, never edited away; written by the archivist and the user |
| Experiment or measurement: question, hypotheses, setup, runs, result | `docs/experiments/<slug>/README.md` | `planned` → `running` (grows) → `done` (frozen) |
| Plan of an undertaking: the brief (what, why, the user's decisions) and the chunks (how, status per chunk) | `docs/plans/<slug>/brief.md`, `docs/plans/<slug>/chunks.md` | the brief is approved by the user; progress lives in the chunks file; deleted when done, after its conclusions became records |
| Facts about the system, kept current (interfaces, registers, pins, boot chain, configuration) | `docs/reference/` | edited in place |
| Procedure (build, flash, deploy, connect) | `docs/how-to/` | edited in place |
| Explanation (why the system is shaped this way, concepts) and tutorials | `docs/explanation/`, `docs/tutorial/` | edited in place |
| Research on foreign material, dated (other code, mailing lists, papers, talks) and past documents | `docs/sources/<slug>.md` | frozen |
| Handoff to the next session | `docs/handoff-<yyyy-mm-dd>.md` | short-lived: closed by this map, then deleted |
| Raw data (logs, dumps, CSV, captures) | outside `docs/`, not in git (a convention: the project's `data/runs/<experiment slug>/`, `data/captures/`) | local; never referenced from docs |
| Build output | wherever the build puts it | regenerated |

## Rules that come with it

- **Point, don't copy.** What stands in one place is linked from the others, never restated. The pointing goes one way: a handoff links to records, plans and experiments; a record links to experiments and sources; nothing links to a handoff. One exception: a `done` experiment whose cause was only found later may end with a line `Concluded in: <link to the record>`.
- **Write during the work into the experiment or the plan, never into the handoff.** A handoff holds only Charter (scope, terms, mode), Conclusions (what holds now), Open points, Start with. A dated section ("Update …", "Status …", "Result …") or a table of runs in a handoff belongs in an experiment. When FOCUS.md, the plan and the experiments carry the state, no handoff is needed.
- **Closing a handoff:** each of its parts goes to its place in the map (open points to FOCUS/BACKLOG, conclusions as record candidates to the archivist, runs and results to an experiment, facts to reference, procedures to how-to); stale state is dropped (git keeps it); then the file is deleted. A record that cited the handoff cites the experiment instead, or, if the content did not move, the commit: `<sha>:docs/handoff-<date>.md`.
- **Raw data is never committed and never referenced.** A link to a file on one machine is dead on every other. The experiment carries the numbers its result rests on: what a reader reads to follow the conclusion is in the document, what only a tool reads is raw data. Reproducibility comes from setup and method; a doubt is answered by a new run. Sharing a name (`docs/experiments/<slug>/`, `data/runs/<slug>/`) finds the raw data on the machine that has it, without a link.
- **Frozen means frozen.** A `done` experiment and a source are not edited. A follow-up is a new experiment, and a correction is a record. Only two additions are allowed: a source's `status:` line, and the `Concluded in:` line of an experiment.
- **One question, one experiment.** A test plan and its results belong together, even when the results came a day later in a handoff. The plan's hypotheses and the runs are merged into one experiment.
- **A procedure has one current home, `docs/how-to/`.** An experiment keeps only the steps of its runs, as they were done, and links to the how-to for the current way.
- **`docs/reference/` holds what is true now.** A fact whose currency nobody can re-check right now (taken from an old handoff) goes in with its origin, like this: `<fact> (as of <date>, from <experiment or source>)`, or it stays in the experiment or source it came from. The next one who verifies it drops the note.
- **Names are fixed once code points at them.** A doc that code, a build file or a package source links to (and that a checksum may cover) keeps its path. Code links only stable places (`docs/reference/`, `docs/how-to/`), never an experiment, a plan or a handoff. Check `git grep <path>` before you move a doc.
- **Plans are files when a team keeps a plan.** Who writes them and how is the team's business; the place is `docs/plans/<slug>/`.

## Source format

```
---
type: <research | measurement | design-doc | retired-system | origin | config-note | talk | paper | ...>
date: <YYYY-MM-DD the evidence dates from, not the day it was filed>
origin: <where it came from: former path, URL, session>
status: <unprocessed | processed>
---
```

`unprocessed` means not yet worked through by the archivist; `processed` means every conclusion that still holds is a record (`mem source <slug> --status processed`). `mem doctor` (Sources) reports a source with a missing field. More: `docs/reference/record-format.md`, section "Sources", in the plugin.

## Experiment format

```
---
question: <what should show>
status: planned | running | done
date: <YYYY-MM-DD started>
setup: <commit, build, device or environment state the runs used>
---

## Hypotheses
- H1 <claim>. Test: <what separates it>. Predict: <the outcome if H1 holds>.

## Runs
| # | change | result |
|---|---|---|

## Result
<which hypothesis held, which fell; the numbers it rests on>
```

`question`, `status` and `date` are required from `planned` on, `setup` from `running` on, a `## Result` section at `done`. The hypothesis template is a working practice, not a rule: a measurement without a hypothesis (a speed test, an audit) leaves that section out.
