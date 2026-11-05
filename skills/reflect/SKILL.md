---
name: reflect
description: "Lightweight end-of-session standup at a context boundary. Run after completing a task. Writes the handoff (state) and hands record candidates to the archivist. Closes the Plan → Code → Reflect loop. Subagents: always append a [retro] block at the end of your response (learned: / blocked: / next:)."
---

Lightweight end-of-session standup. Run after completing a task, or at any other context boundary (chunk handoff, change of mode). Closes the Plan → Code → Reflect loop.

The subagent summary is already the "done" — this adds only what matters beyond the code. `/reflect` produces two things, and keeps them apart:

1. **A handoff** — state: charter, conclusions, open points, no history. You write it yourself, directly as files.
2. **Record candidates** — decisions and learnings worth keeping, as plain text. The **archivist** agent integrates them into the records. You do not write records yourself: no `mem_add`, `mem_link`, `mem_boost`, `mem_split`, `mem_dream`, `mem_delete`.

The area is the folder of the current work that holds `docs/records/` (nearest ancestor of the working directory; `mem context` prints it).

---

## Step 1 — Collect

At this boundary follow the Fabrica handoff protocol (skill `fabrica:handoff-protocol`).

Scan subagent return values for `[retro]` blocks (see convention below). Note any `learned:`, `blocked:`, `next:` and `record_candidates:` lines. No user input needed yet.

---

## Step 2 — My contributions first

Before asking the user, contribute your own observations:

- **Learned:** what was surprising, what assumption was wrong, what tool failed silently
- **Blocked:** what got in the way — missing tool, unclear requirement, wrong mental model
- **Next:** one or two next-step suggestions based on what you saw

Flag each as **"My observation:"** so the user knows it's from the agent side.

---

## Step 3 — Two questions

Ask both questions together:

> **"What did you learn, or what surprised you?"**
> **"What got in your way?"**

Wait for the user's answer. Skip if the user has nothing to add.

---

## Step 4 — Next steps

Aggregate next-step suggestions:
- Your own (from Step 2)
- Any `next:` lines from `[retro]` blocks
- The user's ideas (if any from Step 3)
- What still stands in `FOCUS.md` and `BACKLOG.md`

This is backlog refinement. Present them as a short list and ask where each one goes:

> **"Which of these are next, where do the others go in the backlog, and which are dropped?"**

Every item lives in exactly one place: `FOCUS.md` (now and next) or `BACKLOG.md` (ordered, the next candidate on top), written in Step 5. Moving an item between the two is a cut, never a copy. A finished item is deleted (the commit is the increment). A dropped item is deleted; when the "no" is worth knowing later — the idea could come back — its reason becomes a record candidate (Step 6). Next steps are never record candidates, and there are no todo records.

---

## Step 5 — Handoff (state)

Ask: **"What is your next focus?"** (or derive it from Step 4 if obvious).

Write the handoff yourself, as plain files in the area — this is state, overwritten each time; git keeps the history, so no dates or status words that will rot inside the text:

- `docs/records/FOCUS.md` — the work in progress: the goal, what is being worked on now and what comes next (a few lines, plain text, no frontmatter), ending with a pointer to `BACKLOG.md`. Always update it. It is a focus, not a diary: no list of what was done, no reasons.
- `docs/records/BACKLOG.md` — what is not in focus: one `- ` line per item, unnumbered; the order of the lines is the order of work, the next candidate on top, so a person reorders by moving a line. Plain text, no frontmatter. No sections and no "won't do" list: a dropped item leaves the backlog, and its reason, if worth keeping, is a decision record.
- `docs/handoff-<yyyy-mm-dd>.md` — only when the next session (or another agent) needs more than the focus: a carry-only-conclusions note with **Charter** (scope, terminology, mode), **Conclusions** (what holds now), **Open points** (what is unresolved; the next steps stand in `FOCUS.md`, the handoff points there), **Start with** (the skill or command the next session loads first, with the file it takes, e.g. your planning or coding skill on a plan path). No history of how you got there — the reasons go into record candidates, not into the handoff. No measurements, runs or dated updates either: during the work they are written into the experiment (`docs/experiments/<slug>/README.md`) or the plan (`docs/plans/<slug>/`), and the handoff links to them. Where each kind of content goes: `${CLAUDE_PLUGIN_ROOT}/reference/documentation_map.md`.
- The previous handoff, once this one replaces it or its work is done, is closed by the documentation map and deleted (skill `fabrica:tidy` on that one file): its open points go to `FOCUS.md` or `BACKLOG.md`, its conclusions are record candidates, runs and results go to an experiment, facts to `docs/reference/`, procedures to `docs/how-to/`, stale state is dropped. A handoff is never evidence: a record cites the experiment or source, or the commit that holds the handoff (`<sha>:docs/handoff-<date>.md`).
- Point, don't copy: what already stands in a spec, plan, record, commit or source is named by a relative link, not restated in the focus or the handoff. The pointing goes one way: the handoff links to records, plans, experiments and sources, never the other way round.
- No ids and no numbers on `FOCUS.md` and `BACKLOG.md` lines: the words of a line are enough to find it, and its history is `git log -S '<words of the line>'`.
- The glossary (`docs/reference/glossary.md` in the area, when it has one): when this session coined a term or changed what one means, edit its line now. It is state like the focus; the reason for the change is a record candidate.

---

## Step 6 — Record candidates

Collect the candidates as plain text, one per item. Sources:
- `learned:` and `record_candidates:` lines from `[retro]` blocks (Step 1)
- your observations (Step 2) and the user's answers (Step 3)
- a dropped item whose "no" is worth knowing later (Step 4): what is not done, and why
- records that made a difference this session: which ones (FOCUS.md, a record file, a librarian answer) changed a decision, prevented a mistake, or turned out wrong or outdated — say which record (its path), and whether it held again or misled

Each candidate is a short paragraph:

```
- <the claim: what was decided, observed, or is to be done; with its reason>
  who: <user | agent | the-coder | reviewer | ...>   (whose knowledge or experience it is)
  situation: <when someone would need this without knowing to ask>
  evidence: <test, commit sha, file path, record paths>   (if any)
  touches: <record paths it confirms, contradicts or replaces>   (if known)
```

Do not decide the record type, id, area, edges or supersede yourself — that is the archivist's judgment. Leave out what is state (it is in the handoff, `FOCUS.md` or `BACKLOG.md`; next steps included) and what carries nothing beyond this session.

Show the list to the user once:

> **"These candidates go to the archivist — is anything missing, or should something come out?"**

---

## Step 7 — Hand over to the archivist

Spawn the archivist with the candidates and the area:

```
Agent(subagent_type="fabrica:archivist", prompt="Area: <area path>.\nRecord candidates:\n<the list from Step 6>")
```

Skip this step silently when there are no candidates.

Show the user the archivist's **integration report** as it comes back: what went where, which edges, what was superseded, what was not written and why. If the user disagrees with a placement, pass the correction back to the archivist (`SendMessage` to the same agent) rather than editing records yourself.

---

## Close

One sentence: handoff written + what the archivist integrated or left open. Example: "FOCUS.md and BACKLOG.md updated, handoff written; archivist: 2 learnings, 1 supersede." Nothing else.

---

## [retro] convention for subagents

When spawning subagents for non-trivial tasks, add this to the end of their prompt:

> At the end of your answer, add a `[retro]` block:
> ```
> [retro]
> learned: <what was surprising or did not work — or "nothing">
> blocked: <what got in your way — or "nothing">
> next: <a suggestion for a next step — or "nothing">
> record_candidates: <decisions or learnings that should stay as a record, in plain text — or "none">
> ```

The main agent reads this block in Step 1; `learned:` and `record_candidates:` lines become record candidates in Step 6 and `next:` lines next-step suggestions in Step 4. Subagents never write records themselves — they deliver candidates. This makes subagent observations (silent fallbacks, tool failures, dead ends) visible without requiring transcript review.
