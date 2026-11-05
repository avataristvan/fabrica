type: learning
topic: workflow
perspective: agent
created: 1793905719.19148
cue: You are running /fabrica:tidy on an area with many handoffs and docs, or estimating what a tidy run costs.
---

Observed: Pilot P6 in galaxy-tab-a-2016: the format migration was lossless at scale (385 records, 1033 edges incl. cross-area, 39 superseded_by became edges, checked against HEAD). But /fabrica:tidy over 8 handoffs and 17 docs cost about 245k tokens and 10 minutes, plus about 154k for the archivist's 71 repoints; a proposal per file with a wait for approval was impractical at that size (the user gave standing approval).
Cause: Per-file proposals multiply both tokens and waits with the number of files.
Evidence: galaxy pilot feedback (galaxy-tab-a-2016 session and user); commit aee0f7c, after which tidy takes one overview approval for many files and delegates per file.
