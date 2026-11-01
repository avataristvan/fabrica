id: eval_pull_gap_test_2026_09_20
type: learning
topic: evaluation
perspective: agent
created: 1789925355.433306
edges: [{"target_id": "arch_decision_push_vs_pull_2026_07_31", "edge_type": "related"}, {"target_id": "pattern_gap_test_evaluation", "edge_type": "related"}, {"target_id": "eval_seniority_available_not_used_confirms_pull_gap_2026_10_18", "edge_type": "related"}, {"target_id": "eval_seniority_main_run_result_2026_10_18", "edge_type": "related"}, {"target_id": "pattern_status_markers_rot_in_memory", "edge_type": "related"}, {"target_id": "learning_recall_moment_missed_librarian_asked_only_at_start_2026_10_23", "edge_type": "related"}]
cue: I am about to claim that continuity or stored knowledge automatically saves tokens or gets used
---

Observed: In all 7 gap cases 0 mem_query calls; only the ID pointer in CLAUDE.md worked (3 solved cases via mem_get); replay cosine hit@1 3/7.
Cause: The trigger is missing, not the ranking (the agent does not ask when code/docs provide a plausible substitute answer).
Evidence: scripts/eval_pull/ (cases.json, replay.py); 7 cases + 2 controls, one run per arm; limits in the text.

# Pull gap test: result (2026-09-20)

Evidence for the open condition from arch_decision_push_vs_pull_2026_07_31 (do not delete push until it is proven that pull covers the gap of non-derivable knowledge). Method: pattern_gap_test_evaluation. Test set, answer key and replay script: scripts/eval_pull/ (cases.json, replay.py, README.md).

## Setup
7 gap cases + 2 controls (the answer exists nowhere). Fresh subagents, question only, no hint about memory. Two arms: mem (all tools) and nomem (mem_* forbidden). Controls only in mem. Tool log verified from the transcripts, not just self-reports.

## Result, mem arm
- ✓ g1 edit-push trigger, g3 dream history, g4 UserPromptSubmit trigger: all three directly via mem_get using an entry ID that is in CLAUDE.md (Critical Invariants). No mem_query.
- ✗ g2 origin, g5 review before commit, g6 status notes: not a single mem_* call. No CLAUDE.md pointer present. g2 honestly reported 'not found', g5 never mentioned /code-review, g6 recommended explicit status fields (the first instinct that pattern_status_markers_rot_in_memory refutes).
- Controls c1 (a phone's latency), c2 (PyPI): mem_query was called only after an unsuccessful repo search; correctly 'not documented'. Top scores in global < 0.17.
- nomem arm: gap confirmed for g1, g3, g4, g5 (generic or wrong answers with the predicted first instinct: cost story, outdated model tag), mostly marked as uncertain.

## Key findings
1. In all gap cases: 0 mem_query calls. mem_query ran only in the controls, where the answer does not exist. Trigger = 'repo search found nothing'. Where code/docs/git provide a plausible substitute answer (g2, g3, g6) or the question is behavioural (g5, g6), no agent asks memory.
2. What worked was the ID pointer in CLAUDE.md, not similarity search. Cosine/hybrid were never used in the agent run for gap cases.
3. Confirms the July diagnosis: the most valuable entries (deep, not obvious, no keyword) are the ones an agent does not ask for on its own.

## Confounds and errors in the setup
- The prompt wording 'no other saving' made two agents skip mem_* (mem_get increments access_count and was read as a write action). g3 after correction: ✓. g6 after correction still ✗ without a memory call, so not a prompt artifact.
- g7 (reviewer pull) invalid: the rationale is paraphrased in the Navigator's user-level agent definition the-coder.md, both arms answered correctly. The grep for 'blindtest' did not catch this.
- Questions were phrased after reading the entries (vocabulary overlap minimised, not zero).

## Retrieval stage (not tested by agents)
- Replay with the question verbatim as query, repo.ai-mem (55 entries): cosine hit@1 3/7, hit@8 4/7; hybrid hit@1 3/7, hit@3 4/7, hit@8 4/7. Missed: task questions without keyword overlap (g1, g2, g5, g6).
- Controls produce top-1 scores of 0.35/0.38 (cosine) — higher than some real hits; a threshold does not separate correct from noise (correct entry at 0.20 in one case, nonsense query at 0.26).
- On an earlier set of 11 self-written queries, hybrid was worse than plain cosine (reason not investigated). Confidence does not influence hit order (only cosine/BM25).

## Limits
7 cases, one model, one run per arm, questions phrased by an agent that knew the entries. A statement of direction, not percentages. Not tested: whether a pointer/[available] block replaces the trigger for cases without a CLAUDE.md reference (g2, g5, g6).

## Follow-up question
Which mechanism triggers retrieval when no ID is in context and the question has a plausible substitute answer from code/docs?
pseudonymised for publication, 2026-10-11
