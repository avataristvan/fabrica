type: learning
topic: architecture
perspective: agent
created: 1793524157.191136
cue: You are about to show a repo to outsiders and have only reviewed it from inside the authoring sessions.
---

Observed: A first-visitor review by a fresh agent (git-tracked files only, role "hiring manager with 2-10 minutes") found two things the author's sessions missed: the quick start failed in a plain terminal (mem is only on Claude Code's PATH), and the public FOCUS.md read as a diary of the cleanup itself.
Cause: Not tested; plausibly the authors' sessions always ran inside Claude Code and knew the history. The fresh agent saw only tracked files.
Evidence: d2afcf4, 4592514
