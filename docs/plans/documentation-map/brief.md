# Brief: a documentation map for Fabrica areas, and how a project gets there

> What and why; the user's decisions. The how and the progress: [chunks.md](chunks.md). Pilot area: galaxy-tab-a-2016 (hardware bring-up, kernel drivers).

## Why

Handoffs in working projects mix eight kinds of content: state, conclusions, open points, experiments (hypotheses, runs, results), facts about the system, research on foreign code, procedures, and pointers to raw data. ai-mem has a place for some of them (FOCUS, BACKLOG, records, sources, Diátaxis docs) and none for experiments and raw data, so they stay in the handoff, and the handoff can never be dissolved. Debugging and driver work are measurement-heavy: learnings and decisions rest on data, so the data's condensed form needs a place a record can link to.

Goal: every kind of content has one place and one lifecycle; an agent can tell where something goes without asking; a handoff can be shortened by these rules and finally deleted.

## The map

Implemented as [`reference/documentation_map.md`](../../../reference/documentation_map.md) (places, lifecycles, rules, experiment format). Decisions taken with the user while planning:

- Experiments get their own place (`docs/experiments/<slug>/`), hypothesis-driven; a measurement without a hypothesis is the special case.
- Raw data is neither committed nor referenced and does not live under `docs/`; the project's git-ignored `data/` (`runs/<slug>/`, `captures/`) is a recommended convention.
- Plans are files: `docs/plans/<slug>/brief.md` (briefing-interviewer, with the user) and `chunks.md` (chunk-plan; status per chunk). The orchestrator reads the file rather than receiving the plan as a reply.
- Reflect runs by itself in most cases; suggestions go to the bottom of BACKLOG.md; the user reviews the records at the push.
- Changing the focus means a reflect (focus gate).
- Agents get guidance through lint at write time, not through pushed context.

## What belongs to Fabrica, and what does not

Fabrica owns where knowledge lives and how long it lives, and the memory that keeps it (ai-mem); it does not own how a team works or how a project is laid out beyond that. Each part of the plan sits on one side:

| Fabrica / ai-mem (built here) | Not Fabrica (owner) — Fabrica only names the place or the contract |
|---|---|
| The map: places and lifecycles of records, FOCUS, BACKLOG, handoffs, sources, experiments, plans (P1) | How a plan is made: brief by the briefing-interviewer, chunks, chunk status, spawning by path (briefing-interviewer, dev-team) |
| Experiments as evidence: the place, the minimal frontmatter lint and doctor need (`question`, `status`, `date`, a Result), link targets (P2) | The experimental method (hypotheses with predictions, one variable per run): a working practice of the team or project; the map shows it as a template, not a rule |
| Handoff shape lint (P2b), doctor "Docs" and "Not concluded" (P3), `/fabrica:tidy` (P4) | Raw data layout (`data/runs/`, `data/captures/`) and build output: the project's convention; Fabrica's rule is only "never in docs, never referenced" |
| `/fabrica:setup` install/update for Fabrica's own parts: record format, the map's folders, texts that name records (P5) | Worktree base (`worktree.baseRef`), the base check before spawning: the team that uses worktrees (dev-team) |
| Reflect: focus gate (P5c), automatic reflect, BACKLOG suggestions, record review at the push (P5d) | git hooks and push practice: the user's; setup may only propose the reminder |
| The handoff protocol sentence "a team that keeps a plan keeps it at `docs/plans/<slug>/`" | Parallel work orchestration; Fabrica only says it is listed in FOCUS.md |

## Enablement principles (for foreign projects)

- Propose, apply only on approval; never overwrite a project's text unseen. External (third-party) agents are never edited (`domain_agents_learn_environment_never_edit_external_2026_10_11`); the project's own agents get a proposed diff.
- Mechanical versus judgment: what a tool can do exactly (`mem lint --fix`) runs as a command; what needs knowing the content is done by the project's own session with the map in hand.
- Detected, not declared: no version file to rot; `mem doctor` reads the state from the files every time.
- Every step can be run again and leaves the project working.
