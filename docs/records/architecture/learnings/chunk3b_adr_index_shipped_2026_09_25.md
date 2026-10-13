id: chunk3b_adr_index_shipped_2026_09_25
type: learning
area: architecture
created: 1790370744.828019
---

Observed: A second .md file (INDEX.md) in a directory that another command globs as 'all *.md are ADR entries' made `mem-adr-sync import` fail: adr_markdown.parse() received INDEX.md without a frontmatter separator, every import test failed with 'skipped 1: INDEX.md' and exit != 0.
Cause: implicit assumption 'every .md in the directory is an entry'. Fixed with an explicit skip in _cmd_import (adr_cli.py). The same class of bug occurred again later with README.md (f7d802c). Lesson: whoever places a new artifact file in a directory that another command globs as 'all entries' must exclude it there.
Evidence: b7548a1 (ai_mem/infrastructure/adr_index.py with regenerate_index(adr_dir), adr_cli.py `reindex` and export final step, tests/infrastructure/test_adr_index.py, tests/test_adr_cli.py); f7d802c; today docs/records/INDEX.md.

Design: regenerate_index() uses title_of() from ai_mem.application.list_entries (the only permitted infrastructure -> application dependency), sorted by id, fixed field order, byte-identical across repetitions (proven by test); defective files are skipped and reported on stderr, never abort the run.
