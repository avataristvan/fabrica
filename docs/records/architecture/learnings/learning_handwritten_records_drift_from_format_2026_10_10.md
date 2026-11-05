type: learning
topic: architecture
perspective: agent
created: 1791629940.055744
cue: I find records in an area that were written by hand and do not match the generated format
---

Observed: Areas where sessions wrote records by hand, without ai-mem tools, follow the record format only loosely: Markdown headings and bold labels in the body, an INDEX.md with Markdown links written by hand, no reindex. Their READMEs say the archivist will adopt them later.
Cause: Sessions in a fresh area write records the moment insight arises, with nothing at hand but Write. The format stays readable to humans and to the librarian, but drifts from what the tooling generates.
Evidence: observed 2026-10-10 in three areas of the user's environment; `mem lint --fix` normalises such records and INDEX.md.
