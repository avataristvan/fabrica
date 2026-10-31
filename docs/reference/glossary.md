# Glossary

The words ai-mem and Fabrica use, in the sense they carry now. One line per term, no implementation details: how a term is built lives in the [record format](record-format.md) and the [architecture](architecture.md), why it is so lives in the records.

This page is state, like `FOCUS.md`: a session that coins a term or changes what one means edits this page directly, in the same session (`/reflect`, Step 5). The reasons behind a change go to the archivist as a record candidate.

| Term | Means | Not to be confused with |
|---|---|---|
| **Fabrica** | The method: conventions, roles, rituals and artifacts for working with agents. ai-mem is its memory. | |
| **area** | A folder that holds `docs/records/`. It is the address of knowledge; areas can nest. | a git repo; a collection; the frontmatter key `area:` (that one names the topic) |
| **topic** | The subfolder inside an area's records that a record sits in (`architecture`, `workflow`, ...). | area |
| **collection** | The old name for a store of records (`repo.<x>`, `global`, `workspace`, `subagent.*`). Nothing uses it any more. | area |
| **record** | One decision, learning, todo or user yardstick, as one file. Added to or superseded, rarely edited. | a handoff; a source |
| **decision** | What was chosen and why: domain, pattern or anti-pattern. | a learning |
| **learning** | What was observed, and its cause. Decisions rest on learnings. | a decision |
| **state / decision / evidence** | The three kinds of knowledge. State (focus, handoffs, this glossary) is overwritten, records are added to, evidence never changes. | |
| **source** | Frozen, dated evidence: a talk, a paper, a measurement, a retired design. Learnings point to it. | documentation |
| **focus** | A few lines on what is being worked on now and what comes next. | a todo |
| **handoff** | Conclusions carried across a boundary: charter, conclusions, open points, where to start. No history. | a record |
| **charter** | Scope, terminology and mode at the start of a conversation. It is the question to the librarian. | |
| **context boundary** | A session start, chunk handoff, review or change of mode. Knowledge is read there and written there. | |
| **record candidate** | A plain-text claim a session hands to the archivist. Only the archivist and the user turn it into a record. | a record |
| **write threshold** | What makes a candidate worth a record: it is not derivable from code or docs, and it would surprise someone without its context. | |
| **cue** | One sentence naming the situation in which someone would need a record without knowing to ask. | a keyword; a summary |
| **perspective** | Whose knowledge or experience a record is: the user, an agent, a role. | |
| **librarian** | The read-only agent that answers 1–3 questions by judgment over the records. | a search index |
| **archivist** | The default writer: integrates candidates on write (edges, supersede, area). | the only writer |
| **orchestrator** | The main session. It runs `/reflect` and writes state directly. | |
| **retro** | The block a subagent ends with: learned, blocked, next, record candidates, records consulted. | `/reflect` |
