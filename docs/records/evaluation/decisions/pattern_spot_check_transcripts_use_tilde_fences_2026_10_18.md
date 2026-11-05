type: pattern
topic: evaluation
perspective: agent
created: 1792360317.608234
cue: I am preparing a human spot-check file that embeds agent transcripts in Markdown.
---

Rule: In a spot-check file use ~~~~ fences for embedded transcripts, not ```. Draw the sample after grading and hide the arm; add a second blind grader on the same items.
When: The next LLM-graded eval with a human spot-check.
Why: Agent output containing ``` broke the outer code fences of the seniority spot-check file, which had to be repaired mid-check. Also, earlier "disagree" lines in the user's answers were lead-ins to comments, so confirm disagreement explicitly. Evidence: [eval_seniority_main_run_result_2026_10_18](../learnings/eval_seniority_main_run_result_2026_10_18.md) (20 of 96 drawn; 0/20 user disagreements; blind Opus 2/20).

## Edges

- related: [eval_seniority_main_run_result_2026_10_18](../learnings/eval_seniority_main_run_result_2026_10_18.md)
