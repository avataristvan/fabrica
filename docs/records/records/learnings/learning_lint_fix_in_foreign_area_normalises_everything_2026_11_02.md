id: learning_lint_fix_in_foreign_area_normalises_everything_2026_11_02
type: learning
topic: records
perspective: agent
created: 1793657748.052702
cue: I am about to run mem lint --fix in an area other than the one I work in.
---

Observed: mem lint --fix run in 13 foreign areas to regenerate INDEX.md also renamed the frontmatter key area: to topic: in every record (383 files in galaxy-tab-a-2016). Harmless here because the reader accepts both.
Cause: lint --fix normalises the whole area, so every pending normalisation comes along (inferred from the result).
Evidence: galaxy-tab-a-2016 592f1b2. Check git status afterwards and say so in the commit message.
