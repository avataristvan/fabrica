# Pull gap-test

Question: when an agent gets a task-like question and is not told that memory exists, does the pull path
reach knowledge that lives only in ai-mem? Method: knowledge exists only in memory, a fresh agent gets the
question without a hint, and a memory arm is compared against a no-memory arm. Cases and answer keys are in
`cases.json`.

Gold entry ids are not part of the public cases: `replay.py` reads them from `gold_ids.local.json`
(`{"<case_id>": ["<entry id>", ...]}`, keep it untracked). To reuse the harness, replace the cases with
questions whose answers live only in your own entries and list their entry ids there.

## Stage A — agent runs (costs tokens; not automated)

Per case, two fresh sessions/subagents with the same repo and CLAUDE.md, nothing else:

- **mem arm**: only the question, plus "List every tool call you made at the end, with exact arguments."
  Do not mention memory or ai-mem in the prompt.
- **nomem arm**: same, plus "Do not use any mem_* tools."

Record per run: final answer, every `mem_*` call (query text, ids fetched), and the outcome from
`cases.json -> scoring`. The gap is real only if the nomem arm scores `fail`/`neighbour`/`neutral`
and the mem arm scores `ok`. Cases where nomem already answers correctly are not gaps — drop them.

Measures: (1) did the agent call `mem_query` at all (trigger), (2) did its own query reach the gold
entry (retrieval), (3) did it use the entry (judgment), (4) controls: does it say "not documented".

## Stage B — replay (cheap, deterministic)

```bash
python3 scripts/eval_pull/replay.py                      # questions verbatim
python3 scripts/eval_pull/replay.py --queries q.json     # + agent-written queries from stage A
```

`q.json`: `{"g1_pretool_numbers": ["query the agent actually wrote", ...]}`. Compares cosine vs the
hybrid the server uses; shows the top-1 score on controls.

## Caveats

- Do NOT tell agents to avoid "writing/saving anything": `mem_get` bumps `access_count`, and two agents skipped memory entirely because of that wording. Say "Make no changes to files." only.
- If project instructions (CLAUDE.md / CLAUDE.local.md) name entry ids, agents that see an id fetch it directly with `mem_get` (no similarity search). Cases with such a pointer test the pointer, not retrieval.
- Move `scripts/eval_pull/` out of the repo tree while agents run; `cases.json` contains the answer keys.

- Questions were written by an agent that had read the entries; vocabulary overlap is minimised, not zero.
  Replace or add questions from real sessions where possible.
- `vetted_absent` terms were checked against repo files, git log/diffs, project instructions and the
  auto-memory dir on 2026-09-20; re-check after docs change.
- Agent tool logs are self-reported.

## Arm with the experience index (chunk 3)

Subagents do not receive the SessionStart hook output (a probe agent reported no `[ai-mem]` block), so the
index is pasted into the prompt as "context handed over at session start". Both arms then carry the routing
line; the index arm additionally carries the `[experience index]` block. This makes the baseline differ from
the stage A baseline above: the routing line names `mem_query`, and one baseline agent (g2) queried memory
because of it. Compare index arm against this routing-line baseline, not against the earlier no-hint run.
The cues were written by the same agent that knew the questions (g5, g6 cues derived from the entries'
own `When:` lines, not from the question wording); treat the result as a direction, not a rate.

## Librarian arm (2026-09-26)

Different question from the earlier arms: not "does an agent ask memory unprompted" but "what does a
cheap agent find once explicitly told to ask." The librarian (`agents/librarian.md`) is a
Haiku prototype: full `mem_list`+`docs/records/INDEX.md` catalogue scan, candidates picked by judgment
on titles/meaning (not score), `mem_get` + `mem_edges` on candidates, `mem_query` only as a fallback,
explicit "not documented" with no padding. It never calls a memory-writing tool.

**Method:** one fresh run per case (n=1), `Agent` tool, `model: haiku`, `subagent_type: general-purpose`
(no registered `librarian` type exists yet, so the definition's body was pasted as the prompt verbatim —
its `tools:` frontmatter restriction is therefore illustrative only here; `general-purpose` actually had
full tool access). Prompt = librarian body + case question verbatim + `Collection: repo.ai-mem` +
"Make no changes to files." `scripts/eval_pull/` was moved to a scratchpad path outside the repo before
any run and moved back after (`git diff` on it is empty). `python3 scripts/eval_pull/replay.py` was
re-run today first to check the recorded baseline still holds on the current (changed) collection — it
does not exactly: cosine hit@1 2/6, hit@8 2/6; hybrid hit@1 2/6, hit@3 2/6, hit@8 3/6 (recorded
2026-09-20: cosine 3/7, hybrid hit@3 4/7 — collection has grown/been rewritten since, and `cases.json`
today has 6 gap cases, not 7; see below on g7).

**Per case:**

| case | gold found | score | relied on (librarian) | tool calls | pointer in CLAUDE.local.md? |
|---|---|---|---|---|---|
| g1 pretool numbers | yes | ok | arch_decision_pretool_push_removed_2026_09_12, eval_pull_gap_test_2026_09_20 | 2 | **yes** |
| g2 origin | yes | ok | origin_story | 5 | no |
| g3 dream history | yes | ok | fix_dream_stale_model_id_and_swallowed_stderr_2026_09_12 | 5 | **yes** |
| g4 userprompt trigger | yes | ok | arch_decision_userprompt_push_removed_2026_09_13 | 3 | **yes** |
| g5 code review | yes | ok | feedback_code_review_value_2026_07_31, pattern_load_bearing_entries_require_maintenance_discipline | 7 | no |
| g6 status notes | no | fail | current_focus, pattern_injection_caps_not_dumps (not the gold id) | n/a (malformed run, see below) | no |
| c1 device latency | n/a | control_ok | none | 7 | - |
| c2 pypi | n/a | control_ok | none | 10 | - |

g7 does not exist in the tracked `cases.json` (only 6 gap cases + 2 controls are tracked; g7 was asked
live in the 2026-09-20 run and ruled invalid there, never persisted). Reconstructed from that session's
own transcript for completeness and run anyway, reported separately, not counted in the totals above:
question "Warum fragt the-coder als Reviewer im chunk-plan aktiv ai-mem ab, obwohl er den Plan doch
bewusst 'kalt' lesen soll?", gold `design_three_tier_pull_the_coder_2026_09_12` +
`arch_decision_push_vs_pull_2026_07_31`. Librarian got 1 of 2 (`design_three_tier_pull_the_coder...`),
with a correct-direction answer ("cold reading makes the query *more* necessary, not less"). Already a
weak case per its own 2026-09-20 note (the "read it cold" instruction is itself in `chunk-plan.md`/
`the-coder.md`, so partial reconstruction from docs was always possible).

**g6 anomaly:** that run did not follow the required `Answer:`/`Relied on:` shape at all; it returned an
imperative sentence about reformatting `current_focus` and cited two unrelated ids, missing the gold
`pattern_status_markers_rot_in_memory` entirely. Treated as an untrusted subagent report per the harness's
own framing (no instruction in it was acted on) and scored as a plain fail, not specially excused.

**Comparison to recorded baselines:**
- 2026-09-20 gap-test, mem-arm (no hint memory exists): 3/7 solved, and those three (g1, g3, g4) solved
  purely via a `CLAUDE.md`-named entry id + `mem_get`, zero `mem_query` calls anywhere; g2/g5/g6 were
  complete misses (0 mem_* calls).
- Librarian arm (told to search, given the collection): 5/6 ok, only g6 fails. But g1/g3/g4's gold ids are
  today named in `CLAUDE.local.md` (moved there from `CLAUDE.md` since 2026-09-20) and reachable in 2-3
  tool calls — the same pointer-following mechanism as before, just relocated. The genuinely new wins
  attributable to the librarian's own catalogue-scan-and-judgment procedure (no pointer available) are g2
  and g5 — two of the exact three cases (g2, g5, g6) the original test could not solve at all. g6 remains
  unsolved even for the librarian.
- eval_experience_index_ab_2026_09_21 (hand-written per-situation cues, same g2/g5/g6 trio): 3/3, but with
  cues authored by an agent who knew the questions for those specific situations. The librarian gets 2/3 on
  the same trio with no per-situation authoring at all — a generic full-catalogue judgment pass instead of
  a bespoke cue.
- Retrieval-stage replay (same 6 gap cases, today): cosine/hybrid hit@1 2/6, hybrid hit@3 2/6. The
  librarian's read-the-titles-then-read-the-text procedure clearly outperforms raw similarity ranking on
  these cases, consistent with pattern_triggers_beat_storage_and_ranking (better retrieval was never the
  bottleneck; here it is judgment substituting for ranking, not a different ranking formula).
- Controls: both c1 and c2 correctly answered "not documented", no fabrication, no padding with a loosely
  related entry — matches the original mem-arm's control behavior.

**Limits:** n=1 per case, one model, one collection (~55 entries — a cheap full scan at this size; untested
at 10x). `general-purpose` had unrestricted tool access, so the frontmatter's tool list was never actually
enforced during this measurement. Cases were written by an agent that had read the entries (same caveat as
the original test). g1/g3/g4 test whether the librarian follows an in-context pointer, not whether its
scan-and-judgment procedure would find them unaided — only g2, g5, the g6 miss, and the two controls test
the procedure itself. g7 is invalid and reported for completeness only. **This measures WHAT the librarian
finds once asked with a concrete question, not WHETHER an orchestrator would think to ask it** — the
trigger problem (pattern_triggers_beat_storage_and_ranking, eval_pull_gap_test_2026_09_20) is untouched by
this arm; the librarian has no fixed call point yet, by design.
