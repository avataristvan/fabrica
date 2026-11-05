type: anti-pattern
topic: general
perspective: the-coder
created: 1790370754.111794
---

Tried: Adding a new sibling artifact file (e.g. INDEX.md) into a directory that an earlier, already-shipped chunk treats wholesale as 'every *.md file here is a typed record to parse' (a `glob("*.md")` + strict parse loop).
Failed because: the new file has no frontmatter/expected shape, so the earlier chunk's parse loop chokes on it and reports it as a malformed/skipped record — a regression in already-green tests for a file this chunk never touched, discovered only by running the full existing test suite, not just the new tests.
Instead: whenever a new chunk writes a new well-known filename into a directory another component globs recursively, grep that other component for its glob pattern and add an explicit filename exclusion (e.g. `if file_path.name == "INDEX.md": continue`) as part of the same chunk, and always run the full test suite (not just the new tests) before reporting a chunk done — a chunk-plan's declared 'disjoint files' can still collide at the directory-listing level even when no source file overlaps.