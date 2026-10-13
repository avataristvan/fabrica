id: pattern_gap_test_evaluation
type: pattern
area: evaluation
created: 1780074962.830917
edges: [{"target_id": "learning_gap_test_first_run_and_blindtest_2026_07_31", "edge_type": "derived_from"}, {"target_id": "pattern_eval_artifacts_outside_agent_readable_corpus", "edge_type": "related"}]
---

# Gap test: objective evaluation of whether ai-mem helps the agent

## Methodology
Store knowledge *exclusively* in ai-mem -- not in CLAUDE.md, README, code comments. Then new session, ask a question that requires this knowledge, without a hint where the answer lies. For the blind-test arm (WITHOUT memory) see pattern_blindtest_methodik.

## Scoring scheme (extended)
| Outcome | Verdict |
|---|---|
| Correct answer, memory entry cited | ✓ works |
| Correct answer, read from code/docs | neutral (no gap) |
| Wrong or generic answer | ✗ memory did not help |
| Correct answer, entry not mentioned | ambiguous |
| Accurate answer to a neighbouring question, without an incompleteness signal (NEW 2026-07-31) | partial ✗ -- a fail that is harder to recognise than generic/wrong |

## Requirements for valid test candidates
- The knowledge exists ONLY in ai-mem (not in CLAUDE.md, README, code)
- The correct answer is not derivable by common sense
- A wrong first instinct exists (makes errors visible)
- Case and gold-ID descriptions do NOT lie in a catalog that the tested subject can read (leak validity; pattern_eval_artifacts_outside_agent_readable_corpus)

## Evaluation instances
The orchestrator (this instance) can only test context retrieval -- "was the answer right?"
The relevant instance for code retrieval is **the-coder**: it writes real code and could say whether an entry changed its next step -- i.e. whether memory prevented an error before it happened. (Until 2026-09-12 it received anti-pattern warnings for this directly before a file edit; the PreToolUse push is retired, arch_decision_pretool_push_removed_2026_09_12. Today memory reaches it only through its own explicit mem_query pulls.)

Results of the first test (2026-05-29) and the blind test (2026-07-31): see learning_gap_test_first_run_and_blindtest_2026_07_31.

Later runs: eval_pull_gap_test_2026_09_20 (gap test: agents do not query memory on their own), eval_librarian_2026_09_26 (librarian arm), eval_librarian_rerun_records_layout_2026_09_29 (repetition with the registered type after the records layout). The librarian arm measures 'finds when asked', not 'asks on its own' -- the trigger problem remains untouched by this.
