---
name: handoff-protocol
description: "The ai-mem protocol at a boundary (chunk start, planning, review handoff, a skill's read/write of memory): ask the librarian with the concrete situation and the area path, check the work against the records it names, and report records_consulted and record_candidates in the [retro] block. Records are written by the archivist via /reflect, never by the team itself. Load it when a team file says 'follow the Fabrica handoff protocol'."
---

# Handoff protocol

A boundary is an observable moment where one role hands work to another or starts work whose files are known: a chunk starts, a plan is drafted, a diff goes to review, a skill is about to read or store what earlier sessions decided. At that moment, and not earlier or later, do the steps below. An agent does not ask on its own later (`eval_pull_gap_test_2026_09_20`), so the moment is the trigger.

## 1. Ask the librarian

Ask once, with the concrete situation, not with a topic. The librarian reads the record files by judgment and answers `Answer:` / `Relied on:`; "Not documented" is a valid result and means: go on.

```
Agent(subagent_type="fabrica:librarian", model="haiku", prompt="""
Area: <absolute path of the area, i.e. the folder that holds docs/records/>
Situation: <charter, changed or touched paths, symptom, chunk spec as far as it exists>
Questions:
1. <which decisions/learnings concern this situation, and does the work contradict one?>
2. <one concrete question about the spot where you would otherwise guess>
""")
```

- The area is the nearest ancestor of the working directory with `docs/records/` (`mem context` prints it). Name the path, not a collection. For work that crosses areas, name each.
- Perspective: a coder asks for experience of the-coder first, a reviewer for the reviewer's, a skill for its own role's.
- If your spawn cannot start another agent, the parent asks the librarian before spawning you and passes the answer in your prompt. A direct read of `<area>/docs/records/FOCUS.md` and `INDEX.md` is the fallback when no agent is available.
- Rely on a record only after reading it yourself (the `Relied on:` paths). A finding that rests on a record cites its path.

## 2. Check the work against what it names

Compare the diff, plan or answer with each named decision, invariant and learning. A contradiction is a finding (or a stop), not a footnote. The `user` records are the yardstick for what the user values; the reviewer reads them at review (`anchor-lint` does, see below).

## 3. Report in the `[retro]` block

Every subagent that ends a boundary adds, besides `learned:` / `blocked:` / `next:`:

```
records_consulted: <record paths relative to the area (`docs/records/<topic>/<kind>/<name>.md`; another area's as `../<area>/docs/records/...`) that carried a decision or a finding, or "none">
record_candidates: <plain text: what from this work should become a record, or which existing record it touches or refutes, or "none">
```

`none` is a valid value; an empty or absent field is not (`retro_check` blocks once). A candidate is plain text with its reason; the type, id, area and edges are the archivist's judgment (`docs/reference/hooks.md`, `domain_archivist_who_what_how_2026_10_10`).

## 4. Never write records yourself

Subagents deliver `record_candidates`. The orchestrator hands them to the archivist through `/reflect`. No role other than the archivist and the user writes record files, and nothing is promoted into an agent or skill definition.

If `records_consulted` stays `none` over many boundaries, the step has become ritual and should be re-examined (`mem doctor` shows the rates).

## Who calls when

| Boundary | Who asks | What it carries |
|---|---|---|
| `/dev-team:chunk-plan`, before decomposing | planner | task, the spot where it would guess; the answer's `Relied on:` paths go into each chunk spec as path plus one line of why (`domain_why_travels_with_chunk_spec_2026_10_10`) |
| chunk start | coder | only what the spec does not carry: experience with the files, libraries and tools the chunk touches, the-coder's perspective first |
| code to review | the caller asks first and passes the answer to `anchor-lint`, which asks again if it can spawn | changed paths against decisions/learnings and the chunk's anchors (`domain_librarian_at_review_handoff_2026_10_10`) |
| reflect gate | orchestrator | the coder's and reviewer's `record_candidates` are the first source for the archivist, then `learned:` |

## What a caller passes to `anchor-lint`

Used by the coder (or any caller) at the code-to-review boundary, for the anchors of its own chunk. The agent's fixed *how* (verdict per anchor, user records, librarian question, `[retro]`) lives in `examples/agents/anchor-lint.md`; the caller passes only the *what*:

```
chunk: <name of the chunk>
worktree: <absolute path>
diff: <output of git diff, as text>
anchors: <the chunk entry's Anchors list, verbatim>
area: <absolute path of the folder that holds docs/records/>
librarian answer: <the caller's Answer: / Relied on: for the changed paths>
```

The user records are a pull with a fixed trigger: they are not played into every session, they are read exactly when a role needs the user's view (`domain_user_records_as_role_perspective_2026_10_04`). Their kind stays `user`; every one also carries `perspective: user` (D6). `perspective: user` on another kind is a lens for answers, not part of the yardstick.

The reviewer has distance from the implementation and judges better than the coder what deserves to become a record, so the librarian is asked at the code-to-review boundary, where a concrete diff fixes the situation. A reviewer spawn may not be able to start another agent, so the caller asks first and passes the answer.
