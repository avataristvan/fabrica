# Plan: a documentation map for Fabrica areas, and how a project gets there

> Plan, not current documentation. Pilot area: galaxy-tab-a-2016 (hardware bring-up, kernel drivers).

## Why

Handoffs in working projects mix eight kinds of content: state, conclusions, open points, experiments (hypotheses, runs, results), facts about the system, research on foreign code, procedures, and pointers to raw data. ai-mem has a place for some of them (FOCUS, BACKLOG, records, sources, Diátaxis docs) and none for experiments and raw data, so they stay in the handoff, and the handoff can never be dissolved. Debugging and driver work are measurement-heavy: learnings and decisions rest on data, so the data's condensed form needs a place a record can link to.

Goal: every kind of content has one place and one lifecycle; an agent can tell where something goes without asking; a handoff can be shortened by these rules and finally deleted.

## The map (what goes where)

| Content | Place | Lifecycle |
|---|---|---|
| Work in progress, device/system state now | `docs/records/FOCUS.md` | overwritten |
| Open points, ordered | `docs/records/BACKLOG.md` | lines move, finished lines are deleted |
| Decision, learning, pattern | `docs/records/<topic>/<kind>/<name>.md` | superseded, never edited away |
| Experiment or measurement: question, hypotheses with predictions, setup, runs, result | `docs/experiments/<slug>/README.md` | `planned` → `running` (grows) → `done` (frozen) |
| Plan of an undertaking: brief (what, why, user decisions) and chunks (how, status per chunk) | `docs/plans/<slug>/brief.md`, `chunks.md` | brief approved by the user, chunks carry the progress; deleted when done, its conclusions became records |
| Facts about the system, kept current (registers, pins, boot chain) | `docs/reference/` | edited in place |
| Procedure (flash, build, connect) | `docs/how-to/` | edited in place |
| Research on foreign material, dated (downstream code, mailing lists, papers) | `docs/sources/<slug>.md` (`type: research`) | frozen |
| Handoff to the next session | `docs/handoff-<date>.md` | triaged by this map, then deleted |
| Raw data (logs, dumps, CSV, captures) | the project's `data/` (git-ignored); recommended `data/runs/<experiment slug>/`, `data/captures/` | local, never referenced from docs |
| Build output | wherever the build tool puts it (e.g. `kernel/out/`) | regenerated |

Rules that come with it:
- Raw data is never committed and never referenced: a link to a file that exists on one machine is dead everywhere else. The experiment carries the numbers its conclusion rests on (run tables, counts, register diffs). Rule of thumb: what a reader reads to follow the conclusion is in the document; what only a tool reads is raw data.
- The experiment slug and its `data/runs/<slug>/` share a name: a convention that finds the raw data on the machine that has it, not a link.
- A record cites the experiment (relative link), never the handoff, never raw data. Reproducibility comes from setup and method; a doubt is answered by a new run, which is the stronger evidence anyway.

## Experiment format

```
---
question: <what should show>
status: planned | running | done
date: <YYYY-MM-DD started>
setup: <commit / build / device state the runs used>
---

## Hypotheses
- H1 <claim> — test: <what separates it> — predict: <outcome if H1>

## Runs
| # | change | result |

## Result
<which hypothesis held, which fell; the numbers it rests on>
```

A measurement without a hypothesis (a speed test, an audit) leaves Hypotheses out. Once `done`, the file is frozen like a source; a follow-up is a new experiment.

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

## Chunks

**P0 – Transition must not block.** `lint_after_write` treats migration findings (`legacy-refs`, `bare-id`) as a hint (exit 0 with `hookSpecificOutput.additionalContext`), not a block (`decision: "block"`; the write has happened either way, a block only adds pressure), so a project whose plugin was updated can still edit its old records until `mem lint --fix` runs there. Tests in `tests/hooks/`.

**P1 – The map as a shipped reference.** `reference/documentation_map.md` in the plugin (agents read it as `${CLAUDE_PLUGIN_ROOT}/reference/documentation_map.md`, substituted in skill and agent bodies wherever the plugin is installed, not in Bash; the path changes per plugin version, so it is never written into records or CLAUDE.md; check once whether reading it prompts for permission in a foreign project), the table and rules above plus the experiment format. `docs/reference/record-format.md` links to it instead of repeating it; `README.md` names it. Archivist, librarian and `reflect` point to it where they decide where something goes.

**P2 – Experiments as link targets and lint.** `record_links` and lint treat `docs/experiments/<slug>/README.md` as a link target of the area (like reference docs and sources); `mem lint` checks the experiment frontmatter (`question`, `status`, `date`; `setup` from `running` on) and that a record's link into experiments resolves; `lint_after_write` covers experiment files. A frozen (`done`) experiment changed later is a finding.

**P2b – Handoff shape at write time.** The cause of long handoffs is the handoff used as a lab notebook (dated "Update …", "Status …", "Result …" sections, run tables). `mem lint` checks `docs/handoff-*.md`: only the sections Charter, Conclusions, Open points, Start with; a dated section or a run table is a finding ("belongs in the experiment" / "belongs in the plan"). `lint_after_write` covers handoffs, so it shows while writing, not at cleanup. `reflect` and the handoff protocol get one sentence: during work, write into the experiment or the plan, never into the handoff; a handoff is often not needed at all when FOCUS, plan and experiment carry the state.

**P3 – `mem doctor`, section Docs.** Findings, each with what fixes it:
- area still in the old record format → `mem lint --fix --area <area>` (mechanical);
- handoffs present, with age → triage (P4);
- loose files in `docs/` that fit no place of the map (e.g. `*-plan-*.md`, `*-analysis-*.md`) → triage;
- section "Not concluded" (the detector for a skipped reflect; replaces the backlog item): `running` experiments with the age of their last commit, `done` experiments no record links to ("data without a conclusion"), handoffs not yet triaged, commits since the last change to FOCUS.md or the records. Ages, no threshold: a forgotten one is obvious in the list; a number only if the list gets long. The SessionStart doctor pointer keeps it visible weeks later;
- project-local agents and skills (`.claude/agents/`, `.claude/skills/`, CLAUDE.md) that name records by bare id → text update (P5);
- no ignore rule for raw data although a `data/` exists.

**P4 – Triage skill `/fabrica:tidy`.** For an existing project: walks the handoffs and the loose docs section by section and proposes for each a target from the map (FOCUS, BACKLOG, record candidate, experiment, plan, reference, how-to, source, `data/`, drop), as one list. On approval it writes the docs moves itself; record candidates go to the archivist; a handoff whose sections are all placed is deleted. Judgment stays with the session that knows the content; the skill only carries the map. `reflect` Step 5 uses the same triage when it closes the previous handoff.
Before proposing a record candidate, tidy checks it against the records (librarian), so content the archivist already recorded is not recorded twice. Records whose evidence points into a handoff: when the cited part moves to an experiment, the archivist repoints the evidence there; otherwise the evidence becomes a commit reference `<sha>:docs/handoff-<date>.md` (the last commit that holds the file), which stays valid after the handoff is deleted. Stale state in a handoff ("device runs kernel #4") is dropped; git keeps it.

**P5 – Install and update in a project (`/fabrica:setup`).** Setup gains two parts:
- Docs layout: propose the map's folders as they are needed (not empty scaffolding) and the `.gitignore` line for `data/`.
- Update: run `mem doctor`; mechanical findings get their command run on approval (`mem lint --fix`); text findings get a proposed diff for the project's own agents, skills and CLAUDE.md; content findings are handed to `/fabrica:tidy`.
No version stamp in the project: what is behind is detected from the files themselves, so the update works for any project in any state and can be run again.

**P5b – Plans as files: brief and chunks (dev-team and briefing-interviewer repos, plus one sentence in fabrica).** One folder per undertaking, `docs/plans/<slug>/`: `brief.md` is the domain part (what and why, scope, terms, the user's decisions), written by the briefing-interviewer with the user (today it writes `docs/handoff-<date>.md`, which is a brief, not a handoff); `chunks.md` is the technical part (chunks, anchors, exit criteria, and the status per chunk), written by `chunk-plan` from the brief and reviewed by the tech lead. `chunk-plan` returns only the path plus one line per chunk; the orchestrator reads the file and spawns each coder with "chunk N of `<absolute path in the main checkout>`" (an uncommitted plan is in no worktree. A worktree branches by default (`worktree.baseRef: "fresh"`) from the remote default branch, not from local HEAD: today's background worktrees came from `origin/main` = d91b3ef because main was 4 commits ahead and unpushed. dev-team sets `worktree.baseRef: "head"` or checks the base with `git merge-base` before it spawns; that is dev-team's, not Fabrica's). Progress lives in `chunks.md` only; FOCUS.md points to the plan and changes when the undertaking ends, so autonomous chunk progress never touches the focus gate. Autonomy stops at `blocked: contradicts <record>`. When done, its conclusions become records and the folder is deleted. The handoff protocol says: a team that keeps a plan keeps it there. Small work needs no plan: a task that fits one chunk runs from its BACKLOG line and the agent prompt; work running in parallel is listed in FOCUS.md ("in progress: …") so a crashed session leaves a trace. fabrica's own `docs/plan_*.md` move to `docs/plans/` as the first case.

**P5c – Focus gate.** Rule: changing the focus means a reflect, automatically and without exception. A PreToolUse hook (matcher `Write|Edit`, path filtered in the script on `tool_input.file_path`) denies writing `docs/records/FOCUS.md` (`permissionDecision: "deny"`, reason "A focus change goes through /fabrica:reflect") unless a reflect started in this session since FOCUS.md was last written. Detection by marker files keyed by session_id, not by parsing the transcript (its JSONL format is internal and changes between versions; it is also written asynchronously): a `UserPromptExpansion` hook marks a typed `/fabrica:reflect`, a PostToolUse hook with matcher `Skill` marks a model-invoked one. One debug run first confirms both payloads (`command_name` with or without plugin prefix, the Skill tool_input) and whether a subagent shares the session_id. `reflect_reminder` moves to the same markers. Accepted gap: writes through Bash bypass the gate; doctor's "Not concluded" finds them. No exception for small edits (a reflect with nothing new takes a minute; an exception dilutes the rule). Not covered: the user's own edits outside Claude Code (deliberately free) and a focus change only in conversation; for that, one sentence in `reflect` and the handoff protocol: "Before a new focus: /reflect." With P3's "Not concluded" this gives two stages: the gate prevents a skipped reflect at a focus change, doctor finds what slipped through anyway.

**P5d – Reflect runs by itself; the review comes at the push.** In about nine of ten cases the user has nothing to correct, so `reflect` runs without stopping: it skips the two questions and the backlog question unless it has a real question, writes FOCUS/BACKLOG, hands the candidates to the archivist and reports. Next-step suggestions go to the bottom of BACKLOG.md automatically (they are mostly out of scope for the active focus; the user reorders when picking work up together). The review moves to the push, the last good moment to fold in fix-ups and squash: `mem review` (or a skill) lists the records added, changed or superseded in `@{upstream}..HEAD` with the archivist's reports, the user corrects through the archivist, then squashes and pushes. The backlog item "a doctor/lint check before a push" (private names, machine paths, unknown SHAs) joins this step; Claude Code has no push event and the user pushes from the IDE, so the moment is git's own pre-push hook: one that reminds ("N records since the last push: mem review") is proposed by setup, never installed unasked.

**P6 – Pilot in galaxy-tab-a-2016.** Its own session runs setup (update), then tidy over its 8 handoffs and ~18 loose docs. Measured: how many handoffs are dissolved, what found no place in the map (→ the map grows or the content is dropped), which proposals the user corrected. Findings go back here as record candidates.

## Enablement principles (for foreign projects)

- Propose, apply only on approval; never overwrite a project's text unseen. External (third-party) agents are never edited (`domain_agents_learn_environment_never_edit_external_2026_10_11`); the project's own agents get a proposed diff.
- Mechanical versus judgment: what a tool can do exactly (`mem lint --fix`) runs as a command; what needs knowing the content is done by the project's own session with the map in hand.
- Detected, not declared: no version file to rot; `mem doctor` reads the state from the files every time.
- Every step can be run again and leaves the project working.
