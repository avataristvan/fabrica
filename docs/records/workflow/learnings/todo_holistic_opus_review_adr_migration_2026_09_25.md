id: todo_holistic_opus_review_adr_migration_2026_09_25
type: learning
area: workflow
created: 1790371769.29916
---

Observed: The holistic Opus review of the ADR migration (b7548a1, carried out 2026-09-26) found 3 real bugs that 7 per-chunk reviews had let through: (1) un-supersede via the documented {"superseded_by": "", "valid_until": ""} wrote an empty `valid_until: ` into the file, parse() raised ValueError, import/reindex skipped them; (2) a type change away from domain/pattern/anti-pattern left the .md file orphaned; (3) entry IDs were used unchecked as file names -- `../` and `/` could break out of the ADR directory, an id `INDEX`/`README` would have overwritten generated files. In addition, an integration test on the real stack was missing, and the server.py import built a Chroma on the real AI_MEM_PATH on every pytest run.
Cause: Per-chunk reviews check against fakes and miss exactly the paths that only arise in interplay (un-supersede via the use case, type change via mem_add).
Evidence: Fixes in 12aac54; tests/test_markdown_adr_integration.py (Chroma -> ADR -> BM25); conftest.py isolates via temp dir and AI_MEM_ADR_DISABLED=1.

Further findings: `domain` in _PERMANENT_TYPES is a lifecycle change (framework, layer 3), although the plan treated it as a pure backend change -- correct in substance, wrongly classified; the question 'does this change the framework or only the backend?' would have revealed it. Originally created as a todo with 5 check items (fresh Opus view across all 7 chunks); check items 4 and 5 were fine, a suspected chunk inconsistency (import loses created_at) turned out to be wrong.
