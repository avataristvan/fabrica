id: learning_handwritten_records_drift_from_format_2026_10_10
type: learning
area: architecture
created: 1791629940.055744
---

Observed: On 2026-10-10 three areas (~/workspace/ai-architecture, ~/workspace/interview-notes, ~/workspace/ai-architecture/software-architecture-gathering) wrote records by hand, without ai-mem tools. They follow docs/reference/record-format.md (then docs/adr-format.md) only loosely: Markdown headings and bold labels in the body, an INDEX.md with Markdown links written by hand, no reindex. Two of the areas are not git repos (ai-architecture; interview-notes has `git init` pending). Their READMEs say the archivist will adopt them later.
Cause: Sessions in a fresh area write records the moment insight arises, with nothing at hand but Write. The format stays readable to humans and to the librarian, but drifts from what the tooling generates.
Evidence: the docs/records/ folders of those three areas.
