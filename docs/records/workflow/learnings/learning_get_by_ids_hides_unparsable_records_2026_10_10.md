id: learning_get_by_ids_hides_unparsable_records_2026_10_10
type: learning
area: workflow
created: 1791668231.552412
cue: when writing an exists-check before overwriting a record file
---

Observed: `FileMemoryRepository.get_by_ids` silently skips record files whose frontmatter does not parse. An "is this id already there?" check built only on it would let a write overwrite such a file.
Cause: get_by_ids treats unparsable files as absent (same as missing ids).
Evidence: reviewer finding (confidence 82) on the first mem CLI chunk. `mem add` now also looks for the file by stem (`find_adr_files`) and exits 1; merged in c5f630e.
