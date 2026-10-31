# Result: archivist acceptance run (2026-10-11)

Runs 1-2: chunk 2v, old archivist definition. Run 3: chunk 2a-2, reworked definition (`examples/agents/archivist.md`
of that chunk, loaded as a project agent; its tool calls in `results/run3_sonnet/transcript.jsonl` show the new steps:
`mem context --map --root <workspace>`, back-reference `mem link --area ...`, `mem-dream --neighbourhood`).
Pass rule since 2a-2: the 2v rule plus every edge to an existing record has its back-reference.

| | run 1 (2v) | run 2 (2v) | run 3 (2a-2) |
|---|---|---|---|
| model | sonnet (agent default) | opus (override) | sonnet (agent default) |
| recall of hand-set edges | 6/33 = 18% | 13/33 = 39% | 11/33 = 33% |
| predecessors, strict (expected source -> predecessor, qualified) | 0/4 | 0/4 | 0/4 |
| predecessors, any candidate | 0/4 | 2/4 (see below) | 0/4 |
| duplicate `user_interaction_style` flagged | no | no | no |
| back-references on existing records | not measured | 6/37 | 26/26 |
| perspective / cue on written records | 18/18, 18/18 | 18/18, 18/18 | 18/18, 18/18 |
| outside-scratch check (both `find`s, and run.sh's real-area hash) | empty | empty | empty, hash unchanged |
| cost | $0.69 | $1.62 (508 s) | $1.45 (606 s) |
| baseline records changed | 0 | 6 (reverse `related` edges added to home records; no text changed) | 18 (back-references only, bodies unchanged; 3 in other areas) |
| raw outputs | lost in reboot | `results/run2_opus/` | `results/run3_sonnet/` (+ `written/`: new and changed record files) |
| verdict | FAIL | FAIL | FAIL |

Run 4 (opus fallback) was started and stopped by the orchestrator (usage budget) before it finished; its
outside-scratch check is empty. No opus number for the reworked definition.

## Gaps of runs 1-2 (2v; the archivist was not edited then)

- Run 1 never looked outside the home area (no cross-area edge at all); it wrote 18 new records, invented a topic
  folder, ran no mem-dream.
- Run 2 did cross areas, but linked two predecessors on an adjacent candidate rather than the expected one:
  `pattern_convention_enforcement_gap` on candidate 05 (expected 09; 09 got `anti_pattern_convention_fragility_ai_mem_2026_10_04`
  in `workspace`) and `pattern_retrieval_needs_fixed_trigger_in_role_prompt` on 17 (expected 14). Scored leniently
  (predecessor linked from any candidate) that is 2/4; still short of 4/4. `pattern_mixed_context_focus_degradation`
  and `knowledge_architecture_framework` were not linked at all.
- Run 2 replaced "(id withheld)" placeholders by guessed ids and declared two of them as inference
  (`domain_direction_judgment_over_scores_2026_09_20`, `anti_pattern_convention_fragility_ai_mem_2026_10_04`); these
  guesses account for part of the 13 hits, and some correct hits are by body-content similarity of neighbours.
- Neither run flagged the `user_interaction_style` duplicate (it sits in `global` and `workspace`, which neither
  run searched by that name), and neither used `confirms` (expected: candidate 14 -confirms-> 18's `librarian_at_review_handoff`;
  opus linked the pair as `related`).
- Even opus misses 61% of hand-set edges: most expected edges join candidates to each other, and the archivist
  linked to older existing records instead.

## Gaps of run 3 (reworked definition, sonnet)

- What the rework fixed: it mapped every area (`--map --root`), wrote all back-references (26/26, incl. three in
  ai-architecture and interview-notes), linked siblings first (23 sibling edges by its report), used `contradicts` once, ran
  mem-dream on the 18 new ids and judged its proposals, and listed open questions instead of guessing.
- Recall did not improve (11/33): the sibling edges it set are mostly not the hand-set ones (e.g. 01 -> 03, 05, 13, 18
  where the real records point the other way: 03, 05, 09, 12, 13 -> 01). Expected edges run from the later/derived
  record to the one it rests on; the archivist often set the reverse direction or a different sibling. compare.py
  counts direction (an edge is stored on its source), so a reversed sibling edge is a miss.
- The records home was mapped but not searched: no Glob/Grep/INDEX read in `ai-mem-records/global` or `workspace`
  beyond one file, and no `user/` Glob, so no predecessor (0/4) and no duplicate flag. Step 3 and step 6 are in the
  definition; sonnet skipped them.
- No supersede: it judged the scratch ai-mem "unversioned" (`mem doctor`, the copy has no git) and declined, so the
  hand-set `fabrica_records_public -supersedes-> ai_mem_records_private_gitignored` became `related`.
- Ids: five candidate ids were recovered from dangling edges in existing records (a lookup, declared in the report);
  in candidate 14 it named Evidence ids itself and flagged that for checking.
