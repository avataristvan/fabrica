id: eval_experience_index_ab_2026_09_21
type: learning
area: evaluation
created: 1789969006.311655
edges: [{"target_id": "../fabrica:eval_pull_gap_test_2026_09_20", "edge_type": "related"}, {"target_id": "design_three_tier_pull_the_coder_2026_09_12", "edge_type": "contradicts"}]
---

Observed: With the SessionStart cue block, 3/3 gap cases went directly to the gold entry, baseline 1/3; subagents receive no SessionStart output.
Cause: The index supplies the trigger 'my situation matches line X'.
Evidence: scripts/eval_pull, cases g2/g5/g6 + c1/c2; n=1 per cell, self-reports of the tool calls.

# Experience index A/B test: result (2026-09-21)

Follows from eval_pull_gap_test_2026_09_20 (follow-up question: which mechanism triggers retrieval when no ID is in context). Chunk 3 of the direction domain_direction_judgment_over_scores_2026_09_20: SessionStart prints a small block 'situation -> entry' from entries with a cue metadatum (mem_boost(cue=...), written in /reflect). Test set: scripts/eval_pull, cases g2, g5, g6 plus controls c1, c2.

## Setup
- Subagents do not receive the SessionStart output (probe: 'no block'). The index was therefore placed in the prompt as 'context at start'. Both arms carry the routing line, the index arm additionally the block (13 cues).
- Baseline = routing line, no index. Not identical to the baseline of 2026-09-20 (no routing line there).
- One run per case and arm, tool calls from the self-reports.

## Result
- g2 origin: the baseline found origin_story via its own mem_query (5 tool calls, broad search), the index arm via mem_get directly (3 calls). Both correct.
- g5 review before commit: baseline 0 mem calls, /code-review only as 'a matter of taste, not a must'. The index arm fetched feedback_code_review_value..., recommended the review with reasons.
- g6 status notes: baseline 0 mem calls, recommended explicit status fields ('in progress (uncommitted)', 'not started'), i.e. the refuted first instinct. The index arm fetched pattern_status_markers_rot_in_memory, advised SHA and goal instead of a status word.
- c1 (no answer in memory): no index retrieval, correctly 'not documented'.
- c2 (no answer in memory): correctly 'not documented', but with a misstep: origin_story was fetched because of the loose match with 'origin/motivation'. Cost one call, no wrong answer.

## Reading
In the index arm, 3/3 gap cases went directly to the gold entry, in the baseline 1/3. The trigger was the index, not the similarity search. The index supplies the trigger 'my situation matches line X', which no agent has on its own when code/docs offer a plausible substitute answer.

## Limits
- n=1 per cell, one model, self-report of the tool calls. Direction, not a rate.
- The cues were written by the same agent that knew the questions. The g5/g6 cues come from the When: lines of the entries, not from the questions, but a residual bias remains. Real test: write cues in real /reflect runs, then observe in foreign situations.
- Embedding in the prompt is not the same as the hook context of a top-level agent.
- Over-retrieval (c2) and scaling are not measured: 13 lines are small, the frame is capped at 20. How does it behave with 20 lines with similarities, and who maintains cues in the long run?

## Open
Cue proposal from When: lines (many entries already carry them) in the dream instead of by hand; chunk 4 (event-bound cues via hooks) for situations where the agent does read the index but the situation only occurs later.

Status 2026-10-04: The mechanism validated here (the pushed cue index) was removed (domain_librarian_replaces_experience_index_2026_10_04).

