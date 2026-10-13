id: the-coder_grep_single_char_false_positives
type: pattern
area: general
perspective: the-coder
created: 1781436537.220146
---

Rule: When grepping for single-character variable names to rename, always visually confirm matches before acting — grep patterns like \b[a-z]\b produce many false positives from string literals (e.g. 'a memory entry', 'b for bm25').
When: Any rename/refactor pass targeting short variable names.
Why: Automated grep cannot distinguish variable occurrences from word fragments in string literals — acting on unconfirmed matches breaks unrelated code.