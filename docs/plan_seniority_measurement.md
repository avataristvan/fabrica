# Plan: measuring "Seniority lives in the record"

> Rewritten 2026-10-15. Replaces the quiz draft of 2026-10-14: questions drawn from the record, graded against the record, mostly measure that the record contains itself. This version measures behaviour in tasks. Pattern: `docs/fabrica/patterns/seniority-lives-in-the-record.md`, status hypothesis.

**The claim being tested:** a fresh session with the record does not walk into a dead end that was already tried. It pushes back with the recorded reason, unasked, and still does ordinary work without inventing objections. With decisions only it avoids fewer dead ends; with no record it avoids few.

**Not tested:** growth over time (no usable time curve: the history starts 2026-10-13 and older bodies were edited later), generalisation to other projects (one project, the one the method was built on), long sessions.

**Against testing the test:** everything below is frozen before the first run. The preregistration is the commit that adds this file; its sha256 also stands in FOCUS.md, and the runner refuses to start if the hash differs. Afterwards only the mechanics may change, once, after the pilot. A disappointing result is recorded, never a reason for a v2.

## Tasks (frozen)

Six dead ends. The task is phrased as a plain request; the senior reaction is to stop before building and name the reason.

| # | Task as given to the agent | Senior reaction | Reason lives in |
|---|---|---|---|
| D1 | Add a PreToolUse hook that injects the relevant records before every Edit/Write, so agents never miss them. | Stop: push per edit was removed after measurement; pull at boundaries instead. | decision `arch_decision_pretool_push_removed_2026_09_12` |
| D2 | Add a `confidence` field to records and rank `mem query` and INDEX.md by it. | Stop: confidence was dropped for evidence edges and librarian judgment. | decision `domain_drop_confidence_for_evidence_and_librarian_2026_09_26` |
| D3 | Add `mem prune`, which deletes superseded records to keep the store lean. | Stop: superseded records are flagged, never hidden or deleted; they carry the why. | decision `domain_superseded_flag_not_hide_2026_09_20` |
| D4 | Add `mem-dream --apply`, so consolidation proposals are applied automatically. | Stop: Dream proposes, the archivist applies; no third writer. | decision `domain_dream_proposes_never_applies_2026_10_13` |
| D5 | Simplify the record walk: skip symlinked files entirely, so they can never cause trouble. | Stop: hiding them lets `mem move` write through the link; lint must report them. | learning `learning_symlink_following_walk_fixed_python_312_2026_10_15` |
| D6 | Reword step 3 ("Dry run") of the records_v1 section in UPGRADING.md so it reads more clearly. Small change, just make it. | Do it, and rerun (or explicitly call for) the upgrade acceptance. | learning `learning_rerun_upgrade_acceptance_after_every_upgrading_md_edit_2026_10_12` |

Two controls, where the senior reaction is simply to do the work (checked at freeze, 2026-10-15: no record rejects or covers them, and neither exists in the code; the first C2 candidate, `mem context --json`, already existed and was replaced):

| # | Task | Senior reaction |
|---|---|---|
| C1 | Add `repository` and `homepage` to `.claude-plugin/plugin.json`, pointing to https://github.com/avataristvan/fabrica. | Do it. |
| C2 | Add a `--version` flag to `mem` that prints the version from `.claude-plugin/plugin.json`. | Do it, with a test. |

D5 and D6 are the A1/A2 split: their reason is in learnings, which A1 does not get. D5 and its record are from 2026-10-15, so no model can know them from training.

## Arms (frozen)

Every arm is a fresh copy of the repo at the frozen commit, in its own scratch dir, with `docs/` and `scripts/eval_*` removed except what the arm gets, and the same minimal CLAUDE.md (only the Dev Commands block), so the only variable is the record.

| Arm | Gets | Stands for |
|---|---|---|
| A0 | code, tests, minimal CLAUDE.md | the junior |
| A1 | A0 + `docs/records/*/decisions/` without superseded records, plus INDEX.md filtered to them | ADR practice |
| A2 | A0 + all of `docs/records/` | Fabrica |
| A3 | A2 + the plugin (librarian) and one CLAUDE.md line: ask the librarian before a direction decision | Fabrica in use |

Fixed for all arms: `claude -p`, model `sonnet`, tools Bash/Read/Edit/Write/Glob/Grep (A3 also Agent), no web tools, `--setting-sources project,local`, hooks off except in A3. Prompt = the task text only, plus: "Work in this repository. Finish with a short report of what you did or why you did not."

`docs/records/FOCUS.md` is removed from every arm: it names this measurement and its hash.

Leakage check before the run: grep each arm for key phrases of the six reasons. Hits in A0 or A1 outside code and tests are removed; hits in code comments stay (a junior can read code; that is the realistic baseline) and are listed in the report.

Repeats: 3. Runs: 8 tasks × 4 arms × 3 = 96, plus 96 gradings.

## Grading (frozen)

Blind grader (`sonnet`, fresh process): sees the task, the senior reaction, the source record, the agent's final report and its diff. It does not see the arm; paths are normalised. Score 0–2:

- Dead ends: 2 = stops before building and names the recorded reason (D6: makes the edit and reruns or calls for the acceptance); 1 = builds but flags a concern, or stops with a reason that is not the recorded one; 0 = builds without concern.
- Controls: 2 = does it; 1 = does it with an objection the record does not support; 0 = refuses or stalls.

Secondary, not part of the decision: whether the agent read `docs/records/` (from the tool trace), and in A3 whether it asked the librarian.

The user spot-checks 20 % of the gradings, chosen at random after grading. If the user disagrees on more than 1 in 5, the result is marked uncertain.

## Decision rule (frozen)

"Avoided" = score 2.

- **Probation** for pattern 9 if, in each of the 3 repeats, A2 avoids ≥ 5 of 6 dead ends, A0 avoids ≤ 2 of 6, and A2 scores 2 on both controls in at least 2 of 3 repeats.
- **The record carries more than decisions** (separate claim) if A2 avoids D5 and D6 in ≥ 2 of 3 repeats and A1 in ≤ 1 of 3.
- Otherwise the pattern stays a hypothesis, and the record says what was seen, including A0 doing as well as A2, or A2 refusing the controls.
- A3 is reported, not part of the rule.

Expectation, written down before the run: A0 avoids D1–D4 rarely, D5 sometimes (it looks risky on its face). A2 avoids most. A1 ≈ A2 on D1–D4 and behind on D5/D6.

## Pilot (mechanics only)

One run: D3 × A2 × 1. Checks only that the arm builds, `claude -p` runs, the report and diff arrive and the grader returns a score. The content is not read for judgment. One fix round at most; if the mechanics still fail, the measurement stops and that is the recorded result.

## Build

Reuse `scripts/eval_setup/run.py` (fresh `claude -p`, scratch dirs, parallel runs) as the template for `scripts/eval_seniority/run.py`: arm builder, leakage grep, runner, grader, report. No new framework. Raw transcripts and results stay local (`.git/info/exclude`), this plan is public; the earlier librarian eval was inflated because eval files were readable.

## Steps

1. Freeze: recheck the controls against the record; the user reviews; this file and its sha256 in FOCUS.md are committed together. The runner refuses to start if the hash differs.
2. Build the harness and run the pilot.
3. Main run, grading, the user's spot-check.
4. Result to the archivist as a candidate; the pattern's status changes only after that.
