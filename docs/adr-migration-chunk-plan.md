# ADR-Umstieg für ai-mem: Chunk-Plan

Erstellt 2026-09-25 durch das `chunk-plan`-Skill, Tech-Lead-Review durchgeführt, Plan freigegeben. Hintergrund und Herleitung: `docs/epistemology-framework.md` (Abschnitt "Comparison: BMAD vs. ai-mem framework") und ai-mem-Eintrag `domain_bmad_vs_ai_mem_epistemology_2026_09_25` (Collection `repo.ai-mem`).

## Tech-Lead-Review — Ergebnis

Ursprünglicher Plan war **nicht** "umsetzbar wie geschrieben". 6 Findings, alle unten eingearbeitet:

1. `ai_mem/dream_cli.py` baut einen zweiten, unabhängigen Repository-Stack (`_build_repo()`), der von der ursprünglichen Chunk-4-Verdrahtung übersehen wurde — `mem-dream --auto_delete/--auto_link/--auto_supersede` hätte die Markdown-Dateien stumm umgangen. Jetzt Pflichtbestandteil von Chunk 4.
2. `AddMemoryUseCase`-Wiederverwendung in Chunk 3s `import` ist korrekt für confidence/access_count, hätte aber `created_at` bei einem echten Fresh-Clone-Rebuild stillschweigend verworfen. Jetzt: expliziter Korrektur-Upsert nach dem `AddMemoryUseCase`-Call, plus Metadaten-Gleichheitstest statt nur Text-Gleichheit.
3. Frontmatter-Feldreihenfolge war nicht als deterministisch spezifiziert — hätte die "nur bei Änderung schreiben"-Diff-Logik (Kern der Confidence-Lifecycle-Lösung) durch reine Dict-Key-Order-Churn brechen können. Jetzt: feste Feldreihenfolge + `edges` explizit als einzeilige JSON-Zeile, mit Byte-Identität-Test.
4. `ADR_TYPES`-Dopplung zwischen Chunk 0/1 (bewusst für Parallelstart) hatte keinen zugewiesenen Cleanup-Chunk — jetzt explizit Chunk 2s Scope.
5. Chunk 3 sagte nicht, welches Repository `import` benutzt — jetzt explizit: bare `ChromaMemoryRepository`, kein `MarkdownAdrRepository`-Wrapper (Begründung ergänzt).
6. Chunk 4s Smoke-Test hätte eine echte Datei im echten ai-mem-Arbeitsbaum hinterlassen — jetzt auf Wegwerf-Testverzeichnis umgestellt.

**Architektur-Kernentscheidung:** neuer Decorator `MarkdownAdrRepository` (`ai_mem/infrastructure/`), der das bestehende `MemoryRepository`-Protocol vollständig implementiert und zwischen `ChromaMemoryRepository` und dem optionalen `BM25MemoryRepository` sitzt — keine Use-Case- oder Hook-Datei wird angefasst.

**Confidence-Lifecycle-Antwort:** Markdown-Datei ist eine abgeleitete Projektion des Chroma-Zustands minus volatiler Felder (`confidence`/`access_count`/`boost_count`/`last_accessed_at`/`cue` nie in der Datei), mit Diff-vor-Schreiben-Logik.

**Retrieval-Trigger-Antwort:** bewusst nicht gelöst, nur begrenzt mitigiert (Dateien sind grep-/ls-/Read-sichtbar, CLAUDE.md bekommt einen entdeckbaren Pointer) — explizit als offen dokumentiert, nicht stillschweigend für gelöst erklärt.

---

## Scope Boundary / Non-Goals — Framework vs. Speicher-Backend

ai-mem zerfällt konzeptionell in zwei fast unabhängige Teile:

1. **Framework/Spezifikation** — wann `/reflect` läuft, wie Confidence sich bewegt (die Regeln, nicht der Speicherort), wie Collections sich schachteln (`global → workspace → repo.<name>`), Skill-Prompts (`skills/reflect.md`), Hook-Code (`hook.py`, `posttool_hook.py`, `userprompt_hook.py`, `pretool_hook.py`), Agentenkonventionen (Orchestrator-als-alleiniger-Schreiber, `[retro]`-Blöcke, Expert-Agent-Muster).
2. **Speicher-Backend** — aktuell ausschließlich ChromaDB.

**Diese Migration betrifft ausschließlich Teil (2).** Sie ändert nichts an Teil (1) — kein Chunk in diesem Plan darf `skills/*.md`, `hook.py`, `posttool_hook.py`, `userprompt_hook.py`, `pretool_hook.py`, `agent_context.py` oder Agentenkonventions-Text editieren. Das ist kein Zufall, sondern der Kern der Architektur-Entscheidung unten: der neue Layer dockt exakt an der `MemoryRepository`-Protocol-Grenze an (`ai_mem/domain/memory.py`), genau damit Hooks, Skills und Use-Case-Aufrufsignaturen unverändert bleiben — kein Chunk unten braucht eine Signaturänderung an einer dieser Stellen. Die einzigen berührten Dateien außerhalb von `ai_mem/infrastructure/`/neuen Modulen sind `ai_mem/server.py` (reine Repository-Verdrahtung — MCP-Adapter, nicht Framework-Verhalten), `ai_mem/dream_cli.py` (dieselbe Repository-Verdrahtung), `ai_mem/infrastructure/chroma_repository.py` (eine Zeile: `_PERMANENT_TYPES`), `pyproject.toml` (CLI-Registrierung), sowie `CLAUDE.md`/`docs/architecture.md`/`docs/decisions/` (Dokumentation, kein Code).

Sollte während der Umsetzung auffallen, dass eine Chunk-Aufgabe doch Hook- oder Skill-Code berühren müsste, ist das ein Zeichen von Scope-Creep in den Framework-Teil hinein — das gehört dann in eine separate, künftige Aufgabe, nicht in diesen Plan.

## Architektur-Entscheidung vorab (Ergebnis der Code-Exploration)

**Andockpunkt:** Neuer Decorator `MarkdownAdrRepository` in `ai_mem/infrastructure/`, der das bestehende `MemoryRepository`-Protocol (`ai_mem/domain/memory.py`) vollständig implementiert und einen inneren Repository wrapped — exakt das Muster, das `BM25MemoryRepository` bereits vorgibt (`ai_mem/infrastructure/bm25_repository.py`: dünner Wrapper, delegiert die meisten Methoden 1:1, überschreibt nur `query()`). Kein Protocol-Contract wird geändert, keine Use-Case-Datei in `ai_mem/application/` muss angefasst werden — der neue Layer ist für `AddMemoryUseCase`, `AddEdgeUseCase`, `BoostConfidenceUseCase` etc. unsichtbar, weil er nur an der Repository-Schnittstelle andockt.

**Wrapping-Reihenfolge in `server.py`:**
```python
_inner_repo = ChromaMemoryRepository(_db_path)
_adr_repo = MarkdownAdrRepository(_inner_repo)   # NEU
_repo = BM25MemoryRepository(_adr_repo)  # falls verfügbar, sonst _adr_repo direkt
```
Begründung: BM25 liest nur `query()`/`get_by_ids()` u.a. und reicht `upsert`/`delete`/`add_edge` unverändert durch (verifiziert in `bm25_repository.py` Zeilen 90-119) — es ist daher egal für BM25s Korrektheit, aber `MarkdownAdrRepository` muss näher an Chroma sitzen, damit sein `upsert()`/`delete()`/`add_edge()` die tatsächlichen Schreiboperationen sieht, bevor BM25 sie (nur lesend) umformt.

**Welche Repository-Methoden bekommen File-I/O, welche bleiben reiner Passthrough:**

| Methode | Verhalten |
|---|---|
| `upsert()` | Delegiert zuerst an inner. Für jeden Entry mit `metadata["type"] in {"domain","pattern","anti-pattern"}` und auflösbarem Repo-Root: Markdown-Datei schreiben/aktualisieren. |
| `delete(ids=[...])` | Typ der IDs **vor** dem Löschen aus inner abfragen (danach nicht mehr möglich), inner löschen, dann zugehörige Markdown-Dateien der ADR-Typen entfernen. |
| `delete(ids=None)` | **Löscht KEINE Markdown-Dateien** (explizite Sicherheitsentscheidung — ein versehentlicher `mem_delete()` ohne `ids` soll nicht rekursiv git-getrackte ADR-Files wegräumen). Nur der Chroma-Cache wird gedroppt. |
| `add_edge()` | Delegiert an inner, liest danach den Source-Entry neu (`inner.get_by_ids`) und resynct dessen Datei, falls ADR-Typ (für die `edges:`-Frontmatter-Zeile). Das Nachziehen der Target-Datei bei `supersedes` passiert automatisch **über den upsert()-Aufruf**, den `AddEdgeUseCase` selbst separat auf dem Target macht (siehe unten) — kein Sonderfall nötig. |
| `query()`, `get_by_ids()`, `list_collections()`, `delete_expired()`, `record_access()`, `get_all()`, `delete_stale()`, `get_edges()` | Reiner Passthrough an inner, **kein** File-I/O. Das ist die konkrete Umsetzung der Confidence-Lifecycle-Entscheidung (siehe unten) — `mem_boost`/`record_access` rühren die Dateien nie an. |

**Beleg für die `supersedes`-Automatik:** `AddEdgeUseCase.execute()` (`ai_mem/application/add_edge.py:43-51`) ruft `self._repo.add_edge(...)` (Source) UND separat `self._repo.upsert(collection, [target])` (Target, mit `superseded_by`/`valid_until` in `target.metadata`) auf. Da `MarkdownAdrRepository.upsert()` bei jedem Aufruf aus den aktuellen Metadaten neu serialisiert, wird die Target-Datei automatisch mit `superseded_by: <id>` aktualisiert, ohne dass `add_edge()` das Target selbst anfassen muss.

## Explizite Antwort auf Problem (b) — Confidence-Lifecycle-Mismatch

**Entscheidung:** Die Markdown-Datei ist eine **abgeleitete Projektion des aktuellen Chroma-Zustands, minus volatiler Felder**. Folgende Metadaten-Felder werden **niemals** in die Datei geschrieben (bleiben Chroma-only, nicht git-versioniert): `confidence`, `access_count`, `boost_count`, `last_accessed_at`, `cue`.

Folgende Felder **werden** in die Frontmatter geschrieben (strukturell, ADR-relevant): `id`, `type`, `created_at`, `superseded_by` (falls vorhanden), `valid_until` (falls vorhanden), `edges` (falls vorhanden, aus `get_edges()`/`metadata["edges"]`).

Konsequenz: `mem_boost` (egal wie oft — `current_focus` hat `access_count` 183) rührt nie eine Datei an, weil `record_access()` und der reine Confidence-Pfad in `boost_confidence.py` zwar durch `upsert()` laufen — **hier muss `MarkdownAdrRepository.upsert()` zusätzlich prüfen, ob sich außer den volatilen Feldern etwas geändert hat, bevor es die Datei neu schreibt** (Diff gegen den zuletzt geschriebenen Dateiinhalt, nicht nur "Typ passt"), sonst würde jeder `mem_boost` doch die Datei anfassen. Die Coder-Vorgabe für Chunk 2 verlangt deshalb explizit: **vor dem Schreiben den Ziel-Dateiinhalt mit dem neu berechneten vergleichen; nur bei tatsächlicher inhaltlicher Änderung schreiben.** Das ist das konkrete, prüfbare Kriterium, nicht nur eine Feld-Ausschlussliste.

Zusätzlich: `chroma_repository.py`s `_PERMANENT_TYPES = {"pattern", "anti-pattern"}` (Zeile 16) schließt `domain` **nicht** ein — `domain`-Einträge könnten heute durch `mem_cleanup`s Forgetting-Curve (`delete_stale`) automatisch gelöscht werden. Das widerspricht der ADR-Philosophie (Decision Records sind langlebig, werden durch `supersedes` ersetzt, nicht durch Inaktivität entsorgt). **Chunk 2 erweitert `_PERMANENT_TYPES` um `"domain"`.**

## Explizite Antwort auf Problem (a) — Retrieval-Trigger

**Nicht gelöst durch diese Migration, bewusst so behandelt:** `eval_pull_gap_test_2026_09_20` zeigt `mem_query` 0 Aufrufe in allen Gap-Fällen; nur ein CLAUDE.md-ID-Pointer funktionierte. Das Umstellen des Speicherformats ändert nichts daran, ob ein Agent von sich aus nachschlägt.

**Bewusst begrenzte Mitigation, die dieser Plan liefert (kein Vollfix):** ADR-Dateien sind gewöhnliche Repo-Dateien unter `docs/decisions/*.md` — ein Agent, der das Repo mit `grep`/`ls`/`Read` durchsucht (der Kanal, der im Gap-Test tatsächlich funktionierte: CLAUDE.md-Scan, Repo-Grep), stößt auf sie **ohne** `mem_query` aufzurufen. Chunk 5 macht das explizit nutzbar: ein neuer Abschnitt in CLAUDE.md verweist auf `docs/decisions/` als Pfad (analog zum ID-Pointer-Muster, das nachweislich funktioniert), UND es wird explizit dokumentiert, dass das generelle `mem_query`-Trigger-Problem damit **nicht** gelöst ist. Das ist die geforderte bewusste Chunk-Entscheidung, kein übersehener Punkt.

## Dateilayout

- Verzeichnis: `<repo_root>/docs/decisions/` (Default), override via `AI_MEM_ADR_DIR` (repo-root-relativer Pfad).
- Dateiname: `<id>.md` — ai-mem-IDs sind bereits eindeutig pro Collection und semantisch benannt (z.B. `domain_bmad_vs_ai_mem_epistemology_2026_09_25`), keine zusätzliche fortlaufende Nummerierung nötig.
- Flach, kein Unterordner pro Typ (Typ steht in der Frontmatter — einfacher, kein Move-Handling falls sich `type` mal ändert).
- `global`- und `workspace`-Collections bekommen **kein** File-Backing (kein 1:1-Repo-Root auflösbar) — bleiben Chroma-only. Explizit dokumentierte Scope-Grenze dieser Migration, keine Lücke, die versehentlich entsteht.

## Explizite Antwort: wo leben Kanten zwischen ADR-Files

**Entscheidung: Option A — Frontmatter-Edges in jeder ADR-Datei.** Typisierte Kanten (`contradicts`/`fixes`/`causes`/`related`/`supersedes`) werden als strukturelles Feld in der Frontmatter jeder Datei geschrieben (`edges`, einzeilige eingebettete JSON — siehe Chunk 1, Schritt 3), nicht als separater Graph-Index (Option B, verworfen — Drift-Risiko, passt konzeptionell schlecht, weil `supersedes`/`contradicts` bewusste Urteile sind, keine aus Text extrahierbaren Fakten wie bei graphifys Code-Kanten) und nicht als reine Prosa (Option C, verworfen — nicht maschinell abfragbar).

**Wichtigste Klarstellung:** die Frontmatter-`edges`-Zeile ist eine **git-durable Projektion**, nicht der zur Laufzeit befragte Graph — `mem_query`s Kanten-Traversal liest weiterhin über `MarkdownAdrRepository`s reinen Passthrough direkt aus Chroma; die Laufzeit-Semantik von `mem_link`/`mem_query` ändert sich durch die Migration nicht. Die Datei ist nur Transportweg (git clone/pull) und Fresh-Clone-Wiederherstellungsquelle (`mem-adr-sync import` ruft `repo.add_edge()` je geparster Kante, Chunk 3).

**Zwei Folgeprobleme, explizit adressiert statt übergangen:**

1. **`mem_dream`s `auto_link`/`auto_supersede` werden zu Datei-Mutationen:** bleiben bewusst automatisch anwendbar, ohne neue Freigabe-Logik im Code — der Review-Schritt existiert bereits kostenlos über den bestehenden Git-Workflow (kein Schritt in diesem Plan committet automatisch; ein Datei-Write bleibt eine sichtbare uncommitted Änderung, bis sie unter der bestehenden "kein `git commit` ohne explizite Anfrage"-Konvention committet wird). Pflicht-Satz dazu in Chunk 4s CLAUDE.md-Edit.
2. **Backlink-Integrität bei `mem_split`/Rename:** explizit als vorbestehende, durch diese Migration nicht neu verursachte Lücke benannt (CLAUDE.md dokumentiert dieselbe Dangling-Edge-Schwäche bereits für `mem_move`) — bewusst außerhalb des Scopes dieser Migration, als expliziter "ebenfalls offen"-Satz in Chunk 5s CLAUDE.md-Abschnitt verankert, analog zum Retrieval-Trigger-Nicht-Fix.

Der "elegante Nebeneffekt" (bedeutsame Urteile vs. Betriebs-Telemetrie unterschiedlich speichern) ist keine neue Kategorie, sondern bereits durch die Problem-(b)-Antwort oben abgedeckt: Kanten sind "seltene, bewusste Urteile" und fallen damit in dieselbe Kategorie wie Text/`superseded_by` (Datei), nicht in die Telemetrie-Kategorie (Chroma-only).

## Repo-Root-Auflösung pro Collection

`ai_mem/infrastructure/adr_paths.py` (Chunk 0) hält eine persistierte Mapping-Datei `<AI_MEM_PATH>/adr_collection_roots.json` (`{"repo.<name>": "/abs/path", ...}`), self-populating: bei jedem Server-Start (`server.py`, Chunk 4) wird `detect_repo_context(Path.cwd())` einmal aufgerufen und die eigene Collection→Root-Zuordnung eingetragen. Für `mem_add`-Aufrufe, die explizit eine **andere** Projekt-Collection ansprechen, wird die Datei geschrieben, sobald irgendeine Session schon einmal in diesem Zielrepo lief; vorher wird der Schreibversuch übersprungen und `mem_add`s Antworttext bekommt eine explizite Notiz ("not persisted as file — repo root for 'repo.my-app' not yet known"), damit das kein stiller Datenverlust ist.

---

### Chunk 0: Architecture Prep — Repo-Root-Auflösung & Pfad-Konventionen

**Scope:** Neu: `ai_mem/infrastructure/adr_paths.py`, `tests/infrastructure/test_adr_paths.py`, `docs/adr-format.md` (neu, dokumentiert Frontmatter-Schema + Verzeichniskonvention).

**Depends on:** none
**Parallelizable with:** Chunk 1

**Implementation steps:**
1. `ADR_TYPES = frozenset({"domain", "pattern", "anti-pattern"})` (single source of truth, von Chunk 1/2/4 importiert, nicht dupliziert).
2. `resolve_repo_root_for_collection(collection: str) -> Path | None`:
   - `collection in ("global", "workspace")` → `None`.
   - Sonst: Mapping-Datei `<db_path>/adr_collection_roots.json` lesen (Pfad-Parameter `db_path: Path`, vom Aufrufer übergeben — **kein** eigener Import von `server.py`s `AI_MEM_PATH`-Logik, um zirkuläre Imports zu vermeiden; `adr_paths`-Funktionen nehmen `db_path` explizit entgegen). Treffer → zurückgeben.
   - Sonst: `from ai_mem.repo_context import detect_repo_context`; `detect_repo_context(Path.cwd())` aufrufen; wenn `.collection == collection` und `.git_root` oder `.claude_md_dir` gesetzt ist (git_root bevorzugt, sonst claude_md_dir) → Root zurückgeben UND per `record_collection_root()` persistieren.
   - Sonst `None`.
3. `record_collection_root(db_path: Path, collection: str, root: Path) -> None` — liest/merged/schreibt die JSON-Mapping-Datei atomar (write-to-temp-then-rename).
4. `adr_dir_for(db_path: Path, collection: str) -> Path | None` = `resolve_repo_root_for_collection(...) / os.environ.get("AI_MEM_ADR_DIR", "docs/decisions")`, oder `None`.
5. `adr_file_path(db_path: Path, collection: str, entry_id: str) -> Path | None`.
6. `docs/adr-format.md`: dokumentiert Frontmatter-Keys (id, type, created, superseded_by, valid_until, edges), Dateiname-Konvention, Verzeichnis-Override via `AI_MEM_ADR_DIR`, und die explizite Liste der NICHT persistierten volatilen Felder (confidence/access_count/boost_count/last_accessed_at/cue) mit Verweis auf den Confidence-Lifecycle-Abschnitt oben.
7. Tests: Mapping-Datei-Roundtrip (schreiben, neu laden), `global`/`workspace` → immer `None`, Cache-Treffer vs. Fallback über `detect_repo_context` (gemockt), fehlende Mapping-Datei → kein Crash, sondern `None`/leeres Dict.

**Exit criterion:** `pytest tests/infrastructure/test_adr_paths.py -v` grün; `python -c "from ai_mem.infrastructure.adr_paths import ADR_TYPES, resolve_repo_root_for_collection, record_collection_root, adr_dir_for, adr_file_path"` läuft ohne Fehler.

**Coder prompt core:** This is Chunk 0 of a pre-approved plan. Implement exactly the scope above: a new pure-logic module `ai_mem/infrastructure/adr_paths.py` that resolves a filesystem root for a given ai-mem collection name (for `repo.<name>` collections only; `global`/`workspace` always resolve to `None`), using a self-populating JSON mapping file plus `ai_mem.repo_context.detect_repo_context()` as fallback, and write `docs/adr-format.md` documenting the frontmatter schema. Do not touch any other file, do not implement markdown serialization (that's Chunk 1) or the repository decorator (Chunk 2). Do not replan or expand scope.

---

### Chunk 1: ADR Markdown Serialization (pure text transform)

**Scope:** Neu: `ai_mem/infrastructure/adr_markdown.py`, `tests/infrastructure/test_adr_markdown.py`.

**Depends on:** none
**Parallelizable with:** Chunk 0

**Implementation steps:**
1. Import `ADR_TYPES` from `ai_mem.infrastructure.adr_paths` (leichte Kopplung — falls Chunk 0 noch nicht gemerged ist, lokal `frozenset({"domain", "pattern", "anti-pattern"})` definieren und in Chunk 2 auf den gemeinsamen Import umstellen; **kein Blocker für Parallel-Start**).
2. `@dataclass ParsedAdr: id: str; type: str; text: str; created_at: float | None; superseded_by: str | None; valid_until: float | None; edges: list[dict]`.
3. `serialize(entry_id: str, entry_type: str, text: str, metadata: dict) -> str` — rendert Frontmatter (nur die strukturellen Felder aus der Liste oben, volatile Felder werden ignoriert, falls versehentlich übergeben) + `\n---\n\n` + den rohen `text` (das bestehende `Decision:/Why:/Scope:`- bzw. `Rule:/When:/Why:`- bzw. `Tried:/Failed because:/Instead:`-Format bleibt unverändert im Body, keine Umformatierung in ADR-Sprache).
   **Determinismus ist ein hartes Muss, nicht nur ein Stilhinweis:** die Frontmatter-Felder werden in einer fest verdrahteten, literalen Reihenfolge geschrieben — `id, type, created, superseded_by (falls vorhanden), valid_until (falls vorhanden), edges (falls vorhanden)` — **niemals** durch Iteration über die Schlüssel des `metadata`-Dicts (dessen Reihenfolge durch `{**prior_meta, **user_meta}`-Merges anderswo im Code variieren kann). Ohne diese feste Reihenfolge würde die "nur bei inhaltlicher Änderung schreiben"-Logik aus Chunk 2 durch reine Key-Order-Churn ausgelöst werden, obwohl sich semantisch nichts geändert hat.
   `edges` wird als **einzeilige eingebettete JSON**-Zeile geschrieben (`edges: [{"target_id": "...", "edge_type": "..."}]`), exakt wie `chroma_repository.py`s `edges`-Metadatenfeld schon heute als JSON-String vorliegt — **kein** mehrzeiliges YAML-List-Format.
4. `parse(markdown_text: str) -> ParsedAdr` — robustes Frontmatter-Parsing (kein volles YAML nötig, einfaches `key: value`-Zeilen-Parsing reicht, weil `edges` als einzeilige JSON-Zeile vorliegt). `edges`-Wert wird mit `json.loads()` dekodiert, analog zu `_parse_edges` in `chroma_repository.py`. Bei Parse-Fehlern (kaputtes Frontmatter, ungültiges JSON in `edges`) eine `ValueError` mit klarer Meldung werfen, da eine kaputte ADR-Datei ein Team-sichtbarer Fehler sein soll, kein stilles Weiterlaufen.
5. Round-trip-Test: `parse(serialize(id, type, text, metadata))` liefert `id`/`type`/`text` identisch zurück; `superseded_by`/`edges` überleben den Roundtrip.
6. Test: `serialize()` mit `metadata` das `confidence`/`access_count` enthält → diese Keys tauchen NICHT in der Ausgabe auf.
7. Test: zwei `serialize()`-Aufrufe mit identischem `metadata`-Inhalt, aber unterschiedlicher Python-Dict-Insertionsreihenfolge liefern **byte-identische** Ausgabe.
8. Test: `metadata` mit `edges` als Liste von `{"target_id": ..., "edge_type": ...}`-Dicts → Frontmatter enthält eine einzeilige JSON-Zeile; `parse()` dekodiert sie wieder in dieselbe Liste.

**Exit criterion:** `pytest tests/infrastructure/test_adr_markdown.py -v` grün, inklusive des Tests, der volatile Felder ausschließt.

**Coder prompt core:** This is Chunk 1 of a pre-approved plan. Implement exactly the scope above: a new pure module `ai_mem/infrastructure/adr_markdown.py` with `serialize()`/`parse()` functions that convert between a `MemoryEntry`'s (id, type, text, metadata) and an ADR-style Markdown file (frontmatter with only structural fields — id/type/created_at/superseded_by/valid_until/edges — followed by the raw entry text unchanged). Volatile fields (confidence, access_count, boost_count, last_accessed_at, cue) must never appear in the frontmatter, even if present in the input metadata dict — verify with a dedicated test. Frontmatter fields MUST be emitted in a fixed literal order (id, type, created, superseded_by, valid_until, edges), never by iterating the metadata dict's own key order — verify with a byte-identical-output test across two differently-ordered input dicts. `edges` is a single embedded JSON line, not multi-line YAML. Do not touch server.py, chroma_repository.py, or any other file. Do not replan or expand scope.

---

### Chunk 2: MarkdownAdrRepository decorator + `_PERMANENT_TYPES` extension

**Scope:** Neu: `ai_mem/infrastructure/markdown_adr_repository.py`, `tests/infrastructure/test_markdown_adr_repository.py`. Edit: `ai_mem/infrastructure/chroma_repository.py` (Zeile 16: `_PERMANENT_TYPES = {"pattern", "anti-pattern"}` → `{"pattern", "anti-pattern", "domain"}`). Edit (klein, explizit erlaubt): `ai_mem/infrastructure/adr_markdown.py` — die dort in Chunk 1 übergangsweise lokal definierte `ADR_TYPES`-Konstante durch einen Import aus `ai_mem.infrastructure.adr_paths` ersetzen.

**Depends on:** Chunk 0, Chunk 1
**Parallelizable with:** Chunk 3

**Implementation steps:**
1. `class MarkdownAdrRepository:` Konstruktor `__init__(self, inner: MemoryRepository, db_path: Path)`.
2. `_sync_file(self, collection, entry) -> None`: löst Pfad via `adr_paths.adr_file_path()`; wenn `None` (Typ nicht ADR-relevant oder Root nicht auflösbar) → no-op. Sonst: neuen Inhalt via `adr_markdown.serialize()` berechnen; **falls Datei existiert, aktuellen Inhalt lesen und vergleichen — nur bei Unterschied schreiben**. Verzeichnis mit `parents=True, exist_ok=True` anlegen.
3. `upsert()`: `self._inner.upsert(collection, entries)`, dann für jeden Entry mit `entry.metadata.get("type") in ADR_TYPES`: `_sync_file(collection, entry)`.
4. `delete(collection, ids)`: wenn `ids` gesetzt: **vor** dem Löschen `self._inner.get_by_ids(collection, ids)` aufrufen, ADR-Typ-Einträge merken; `affected = self._inner.delete(collection, ids)`; danach für die gemerkten Einträge die Datei löschen (falls vorhanden, `missing_ok=True`); `affected` zurückgeben. Wenn `ids is None`: nur `self._inner.delete(collection, None)` — **keine Datei-Löschung**.
5. `add_edge()`: `self._inner.add_edge(collection, source_id, edge)`, danach `entries = self._inner.get_by_ids(collection, [source_id])`; wenn ADR-Typ → `_sync_file(collection, entries[0])`.
6. Restliche Protocol-Methoden: 1-Zeilen-Passthrough an `self._inner`, exakt im Stil von `bm25_repository.py` Zeilen 93-118 — **kein** File-I/O in diesen Methoden.
7. `chroma_repository.py` Zeile 16 anpassen: `domain` zu `_PERMANENT_TYPES` hinzufügen.
8. Tests (mit einem simplen In-Memory-Fake für `inner: MemoryRepository`, `tmp_path` als `db_path`): `upsert()` mit `type="domain"` schreibt Datei; `upsert()` mit `type="feedback"` schreibt keine Datei; zwei `upsert()`-Aufrufe mit nur geänderter `confidence` → Datei-Inhalt/mtime unverändert; `delete(ids=[...])` entfernt Datei; `delete(ids=None)` lässt Dateien unangetastet; `add_edge(edge_type="supersedes")`-Simulation aktualisiert Target-Datei; `chroma_repository.py`-Test bestätigt `domain` in `_PERMANENT_TYPES`.

**Exit criterion:** `pytest tests/infrastructure/ -v` komplett grün, inklusive der neuen Datei und der Erweiterung in `test_chroma_repository.py`.

**Coder prompt core:** This is Chunk 2 of a pre-approved plan. Implement exactly the scope above: a new `MarkdownAdrRepository` class in `ai_mem/infrastructure/markdown_adr_repository.py` implementing the full `MemoryRepository` Protocol by wrapping an inner repository, in the same thin-decorator style as `ai_mem/infrastructure/bm25_repository.py`. Only `upsert`, `delete`, and `add_edge` get real logic; every other Protocol method is a one-line passthrough with zero file I/O. Critical constraint: before writing a file, compare its would-be new content against the existing file content and skip the write if unchanged, so that confidence/access_count-only mutations never touch the file — this only works because Chunk 1's `serialize()` emits frontmatter fields in a fixed deterministic order. Also change `chroma_repository.py` line 16's `_PERMANENT_TYPES` to include `"domain"`, AND replace `adr_markdown.py`'s temporary local `ADR_TYPES` with an import from `adr_paths`. Do not touch `server.py` (Chunk 4) or `ai_mem/adr_cli.py` (Chunk 3, parallel). Do not replan or expand scope.

---

### Chunk 3: `mem-adr-sync` CLI (export/import round trip)

**Scope:** Neu: `ai_mem/adr_cli.py`, `tests/test_adr_cli.py`. Edit: `pyproject.toml` (`[project.scripts]`).

**Depends on:** Chunk 0, Chunk 1
**Parallelizable with:** Chunk 2

**Implementation steps:**
1. `argparse`-basierte CLI mit zwei Subcommands, analog zu `dream_cli.py`s Aufbau:
   - `mem-adr-sync export --collection repo.ai-mem [--db-path ...]`: instanziiert `ChromaMemoryRepository` direkt (reine Leseoperation), `repo.get_all(collection)`, filtert `ADR_TYPES`, schreibt für jeden Eintrag eine Datei via `adr_markdown.serialize()` + `adr_paths.adr_dir_for()`. Ohne `--collection`: iteriert über `repo.list_collections()`, für jede `repo.*`-Collection mit auflösbarem Root exportieren, `global`/`workspace` überspringen (mit Hinweis, kein stiller Skip).
   - `mem-adr-sync import --collection repo.ai-mem [--db-path ...]`: instanziiert eine **bare `ChromaMemoryRepository`** (kein `MarkdownAdrRepository`-Wrapper). Liest alle `*.md` unter `adr_paths.adr_dir_for(...)`, parsed jede Datei via `adr_markdown.parse()`. **Fehlerbehandlung:** `ValueError` → Datei überspringen, Name+Fehler ausgeben, mit den restlichen fortfahren, Exit-Code ≠ 0 falls etwas übersprungen wurde.
     Für jede erfolgreich geparste Datei: `AddMemoryUseCase.execute()` (aus `ai_mem.application.add_memory`) mit `metadatas` aus `type`/`superseded_by`/`valid_until` (NICHT `created_at`). Danach separat `repo.add_edge()` für jede geparste Edge.
     **`created_at`-Korrektur:** `AddMemoryUseCase.execute()` liest `created_at` ausschließlich aus bereits in Chroma vorhandenen Metadaten — nach dem Aufruf, wenn die Datei ein `created_at` trägt, den Entry per `get_by_ids()` erneut holen, `created_at` auf den geparsten Wert setzen, mit einem zweiten `repo.upsert()` korrigieren.
2. `main()`-Entry-Point, `pyproject.toml`: `mem-adr-sync = "ai_mem.adr_cli:main"`.
3. Tests: `export` nach `mem_add` → Datei mit korrektem Inhalt; `import` in frische Instanz → identischer Text UND `created_at`; Roundtrip export→delete→import stellt Eintrag wieder her; zweiter `import` nach `mem_boost` überschreibt Confidence nicht; kaputte `.md`-Datei neben gültigen → gültige werden importiert, kaputte gemeldet, Exit-Code ≠ 0.

**Exit criterion:** `pytest tests/test_adr_cli.py -v` grün; `mem-adr-sync --help` zeigt beide Subcommands.

**Coder prompt core:** This is Chunk 3 of a pre-approved plan. Implement a new CLI `ai_mem/adr_cli.py` with `export` and `import` subcommands, using `adr_paths` and `adr_markdown` (Chunks 0/1 — read both first). Both operate on a bare `ChromaMemoryRepository` — never `MarkdownAdrRepository` (Chunk 2, parallel, do not create/import it). `import` MUST reuse `AddMemoryUseCase.execute()` for confidence/access_count, but that path discards `created_at` from the file — re-fetch and correct it with a follow-up `upsert()`. On a malformed file, skip, report, continue, exit non-zero if anything skipped. Register `mem-adr-sync` in `pyproject.toml`. Do not touch `server.py` (Chunk 4). Do not replan or expand scope.

---

### Chunk 3b: `docs/decisions/INDEX.md` — kompakter Index gegen Retrieval-Rauschen

**Warum dieser Chunk existiert (Nutzer-Ergänzung):** sobald `docs/decisions/` viele Dateien hat, soll ein Agent nicht N einzelne ADR-Dateien lesen/greppen müssen, um zu sehen, was es gibt — eine kompakte Index-Datei mit einer Zeile pro Entscheidung senkt das Kontext-Rauschen. Gehört in diesen Plan, weil sie direkt zur Retrieval-Trigger-Mitigation aus Chunk 5 gehört (ein Agent liest eine Datei statt vieler).

**Bewusst NICHT Teil dieses Plans, mit Begründung (Nutzerfrage "Bibliothekar"-Subagent):** die Index-Generierung ist reines, deterministisches Datei-I/O + String-Formatierung — es gibt kein Urteil zu fällen, das ein LLM bräuchte. Ein fire-and-forget-Subagent wäre langsamer, nicht-deterministisch und teurer als eine Python-Funktion, die dasselbe in Millisekunden erledigt — und wäre zudem ein neues Skill-/Agenten-Konzept, nicht eine Repository-/Infrastructure-Schicht, also ohnehin außerhalb der "Scope Boundary" oben. Empfehlung: die Index-Datei selbst gehört in diesen Plan (dieser Chunk), das "Bibliothekar"-Subagent-Konzept ist ein eigenständiges, späteres Todo (`todo_bibliothekar_haiku_retrieval_agent_2026_09_25`) — und zwar nur für eine Aufgabe, die tatsächlich Urteilsvermögen braucht, nicht für das, was INDEX.md heute leistet.

**Scope:** Neu: `ai_mem/infrastructure/adr_index.py`, `tests/infrastructure/test_adr_index.py`. Edit (klein): `ai_mem/adr_cli.py` — neuer Subcommand `reindex`, plus ein Aufruf von `regenerate_index()` als letzter Schritt von `export` (Chunk 3). **Storage-layer only**.

**Depends on:** Chunk 1 (`adr_markdown.parse()`), Chunk 3 (`adr_cli.py` muss existieren)
**Parallelizable with:** Chunk 4 (vollständig disjunkte Dateien)

**Implementation steps:**
1. `regenerate_index(adr_dir: Path) -> None` in `ai_mem/infrastructure/adr_index.py`: listet alle `*.md`-Dateien in `adr_dir` außer `INDEX.md` selbst, parsed jede via `adr_markdown.parse()`, extrahiert den Titel via Wiederverwendung von `title_of()` aus `ai_mem.application.list_entries` (nicht neu implementieren; `infrastructure → application → domain` ist die zulässige Importrichtung laut `docs/architecture.md`). Status-Spalte: `active`, oder `superseded_by: <id>` falls gesetzt.
2. Ausgabeformat — Markdown-Tabelle, nach `id` sortiert (Determinismus wie in Chunk 1):
   ```markdown
   # Decision Records Index

   | id | title | status |
   |---|---|---|
   | domain_bmad_vs_ai_mem_epistemology_2026_09_25 | Decision: Der Vergleich BMAD vs. ai-mem... | active |
   | domain_some_old_entry | ... | superseded_by: domain_newer_entry |
   ```
   Kaputte `.md`-Datei: überspringen, Dateiname melden, mit Rest fortfahren (wie Chunk 3s `import`).
3. `ai_mem/adr_cli.py`: neuer Subcommand `mem-adr-sync reindex --collection ... [--db-path ...]`; `export` ruft `regenerate_index()` zusätzlich als letzten Schritt auf. Kein automatisches Nachziehen bei einzelnen `mem_add`-Aufrufen über `MarkdownAdrRepository` (Chunk 2) — bewusst periodisch regeneriertes Artefakt (wie `mem_dream`), keine übersehene Lücke: Frische zwischen zwei `export`/`reindex`-Läufen ist eine akzeptierte, dokumentierte Einschränkung, kein Live-Update, um eine Read-Modify-Write-Race auf eine gemeinsame Datei zu vermeiden.
4. Tests: 3 ADR-Dateien (eine mit `superseded_by`) → sortierte, korrekte `INDEX.md`; kaputte Datei dazwischen wird übersprungen und gemeldet; zwei Läufe ohne Quelländerung → byte-identische `INDEX.md`.

**Exit criterion:** `pytest tests/infrastructure/test_adr_index.py -v` grün; `mem-adr-sync reindex --help` funktioniert; nach `mem-adr-sync export` existiert `docs/decisions/INDEX.md` mit einer Zeile pro exportierter Datei.

**Coder prompt core:** This is Chunk 3b of a pre-approved plan, parallel to Chunk 4 (built by another coder — do not touch `server.py`, `dream_cli.py`, `docs/architecture.md`, or `CLAUDE.md`). Implement exactly the scope above: a new pure function `regenerate_index()` in `ai_mem/infrastructure/adr_index.py` that scans `docs/decisions/*.md`, parses each via `ai_mem.infrastructure.adr_markdown.parse()` (Chunk 1, read it first), and writes a single sorted-by-id Markdown table `INDEX.md` with columns id/title/status — reuse `title_of()` from `ai_mem.application.list_entries` rather than reimplementing title extraction (this infrastructure→application import is explicitly allowed per `docs/architecture.md`). Add a `reindex` subcommand to `ai_mem/adr_cli.py` (Chunk 3, read it first) that calls this function, and make `export` call it automatically as its final step. A malformed `.md` file must be skipped and reported by name, never crash the run. Output must be byte-identical across repeated runs with unchanged sources — verify with a test. Do not wire index regeneration into `MarkdownAdrRepository` (Chunk 2) or any per-`mem_add` write path. Do not replan or expand scope.

---

### Chunk 4: Server-Wiring + Selbst-Population der Root-Mapping

**Scope:** Edit: `ai_mem/server.py`, `ai_mem/dream_cli.py`, `docs/architecture.md`, `CLAUDE.md`. **Storage-layer only.**

**Wichtiger Fund aus dem Tech-Lead-Review:** `ai_mem/dream_cli.py` baut in `_build_repo()` einen **zweiten, unabhängigen** Repository-Stack für das `mem-dream`-Terminal-Kommando. `DreamMemoryUseCase` mutiert über diesen Stack echte Daten für genau die hier migrierten Typen. Ohne Anpassung würde `mem-dream --auto_delete` eine `domain`-Datei auf der Platte verwaisen lassen, und `--auto_link`/`--auto_supersede` würden Chromas `edges`/`superseded_by` ändern, ohne die `.md`-Datei nachzuziehen. Deshalb: **`dream_cli.py`'s `_build_repo()` wird genauso verdrahtet wie `server.py`'s Repository-Stack** — Pflichtbestandteil dieses Chunks.

**Depends on:** Chunk 2, Chunk 3
**Parallelizable with:** nothing

**Implementation steps:**
1. In `server.py`, nach `_inner_repo = ChromaMemoryRepository(_db_path)`:
   ```python
   from ai_mem.infrastructure.markdown_adr_repository import MarkdownAdrRepository
   from ai_mem.infrastructure.adr_paths import record_collection_root
   from ai_mem.repo_context import detect_repo_context

   _adr_repo = MarkdownAdrRepository(_inner_repo, _db_path)
   ctx = detect_repo_context()
   if ctx.git_root or ctx.claude_md_dir:
       record_collection_root(_db_path, ctx.collection, ctx.git_root or ctx.claude_md_dir)
   ```
   Danach `BM25MemoryRepository(_adr_repo)` statt `BM25MemoryRepository(_inner_repo)`, und den `except ImportError`-Fallback auf `_repo = _adr_repo`. Opt-out via `AI_MEM_ADR_DISABLED=1` (dann `_repo = _inner_repo` direkt).
2. `ai_mem/dream_cli.py` bekommt dieselbe Verdrahtung in `_build_repo()`, inklusive derselben Opt-out-Prüfung.
3. Im `mem_add`-Handler: wenn `type_tag in ADR_TYPES` und Root nicht auflösbar: Notiz an `base_text` anhängen ("not persisted as a Markdown file — could not resolve a repo root..."), sonst optional den geschriebenen Pfad nennen.
4. `docs/architecture.md`: neue Zeile in der Infrastructure-Tabelle für `MarkdownAdrRepository`.
5. `CLAUDE.md` Critical Invariants: neuer Punkt zur Confidence-Lifecycle-Grenze.
6. Voller Testlauf (`pytest tests/ -v`) — bestehende Server-Tests dürfen durch das geänderte Wiring nicht brechen.

**Exit criterion:** `pytest tests/ -v` vollständig grün; manueller Smoke-Test in einem **Wegwerf-Testverzeichnis** (z.B. `/tmp/adr-smoketest`), nicht im echten ai-mem-Repo.

**Coder prompt core:** This is Chunk 4 of a pre-approved plan. Wire `MarkdownAdrRepository` (Chunk 2) into `server.py`'s repository construction between `ChromaMemoryRepository` and the optional BM25 wrapper. Add repo-root self-population at startup. Apply the exact same wiring to `dream_cli.py`'s `_build_repo()` — required, not optional: `mem-dream`'s auto_delete/auto_link/auto_supersede flags mutate the migrated entry types. Add a note to `mem_add`'s response when a file couldn't be written. Update `docs/architecture.md` and `CLAUDE.md`. Run the full test suite and fix breakage via mocks/fixtures, not weakened assertions. Smoke-test only in a throwaway temp directory. Do not replan or expand scope beyond server.py + dream_cli.py wiring + the two doc files.

---

### Chunk 5: Backfill bestehender Einträge + Retrieval-Trigger-Mitigation (Doku)

**Scope:** Neu: `docs/decisions/README.md`, generierte Dateien unter `docs/decisions/*.md` (via CLI). Edit: `CLAUDE.md` (neuer Abschnitt "Decision Records"). **Storage-layer + Doku only.**

**Depends on:** Chunk 4, Chunk 3, und Chunk 3b (export erzeugt INDEX.md automatisch mit)
**Parallelizable with:** nothing

**Implementation steps:**
1. `mem-adr-sync export --collection repo.ai-mem` als einmaliger operativer Schritt (ruft die CLI auf, die dank Chunk 3b am Ende automatisch `docs/decisions/INDEX.md` mit erzeugt), um bestehende Einträge zu backfillen, u.a. `domain_bmad_vs_ai_mem_epistemology_2026_09_25`.
2. `docs/decisions/README.md`: Konvention erklären (ein File pro Entscheidung, Dateiname = ai-mem-ID, Frontmatter-Schema-Verweis auf `docs/adr-format.md`, "superseded by" als Frontmatter-Feld statt Löschung).
3. `CLAUDE.md`, neuer eigenständiger Abschnitt "Decision Records":
   ```markdown
   ## Decision Records

   `domain`/`pattern`/`anti-pattern`-Wissen ist git-nativ unter `docs/decisions/` (eine
   Markdown-Datei pro Entscheidung, Dateiname = ai-mem-Entry-ID) — direkt durchsuchbar mit
   grep/ls/Read, ohne ai-mem-Tools. ChromaDB ist ein lokal regenerierbarer Semantik-Index
   darüber (`mem-adr-sync import` baut ihn aus den Dateien neu auf), nicht die Wahrheitsquelle.

   **Offen, durch diese Migration NICHT gelöst:** das generelle mem_query-Retrieval-Trigger-
   Problem (`eval_pull_gap_test_2026_09_20`, Collection `repo.ai-mem`) — ein Agent, der eine
   Frage hat, ruft mem_query in den meisten Fällen nicht von sich aus auf. Dieser Abschnitt
   macht `docs/decisions/` nur über den Kanal auffindbar, der im Gap-Test nachweislich
   funktionierte (CLAUDE.md-Verweis + Repo-Grep), löst aber nicht das Trigger-Problem für
   ai-mems eigene Query-Tools.

   `docs/decisions/INDEX.md` listet alle Entscheidungen kompakt (id + Titel + Status) —
   bei vielen Dateien zuerst diese eine Datei lesen statt einzeln zu greppen;
   `mem-adr-sync reindex`/`export` hält sie aktuell.
   ```
4. Verifikation: `mem-adr-sync import` gegen frische Test-Chroma-Instanz liefert Eintrag identisch zum Original (manueller Diff-Check).

**Exit criterion:** `docs/decisions/domain_bmad_vs_ai_mem_epistemology_2026_09_25.md` existiert mit vollem Originaltext; `docs/decisions/INDEX.md` existiert und listet diesen Eintrag; `docs/decisions/README.md` existiert; `CLAUDE.md` enthält den neuen Abschnitt inkl. des expliziten "nicht gelöst"-Satzes.

**Coder prompt core:** This is Chunk 5 of a pre-approved plan — the final chunk. Run `mem-adr-sync export --collection repo.ai-mem` to backfill existing entries into `docs/decisions/*.md`. Write `docs/decisions/README.md`. Add a "Decision Records" section to `CLAUDE.md` (standalone, not under "Critical Invariants") pointing at `docs/decisions/`, including — hard requirement — an explicit sentence that the general `mem_query` retrieval-trigger problem is NOT solved by this migration. Verify the backfilled file for `domain_bmad_vs_ai_mem_epistemology_2026_09_25`. Do not replan or expand scope.

---

## Spawn Order

Sequential (dependencies):
- Chunk 0 + Chunk 1 (parallel) → /reflect → Chunk 2 + Chunk 3 (parallel) → /reflect → Chunk 3b + Chunk 4 (parallel) → /reflect → Chunk 5 → the-coder → /reflect

Parallel possible:
- **Chunk 0 + Chunk 1 simultaneously** (fully disjoint files) → spawn two `Agent` calls in the same message with `subagent_type="the-coder"`
- **Chunk 2 + Chunk 3 simultaneously**, after Chunk 0 + Chunk 1 have landed and reflected (disjoint files, both only read Chunk 0/1's modules) → spawn two `Agent` calls in the same message with `subagent_type="the-coder"`
- **Chunk 3b + Chunk 4 simultaneously**, after Chunk 2 + Chunk 3 have landed and reflected (disjoint files: `adr_index.py`+`adr_cli.py`-Ergänzung vs. `server.py`+`dream_cli.py`+die zwei Doku-Dateien) → spawn two `Agent` calls in the same message with `subagent_type="the-coder"`
- Chunk 5 is strictly sequential after both Chunk 3b and Chunk 4.

**Reflect gate:** Run /reflect between every chunk (or every parallel pair). The coder's `[retro]` surfaces path corrections, API surprises, and scope drift before they propagate into the next chunk — particularly important here because Chunk 2/3 both depend on Chunk 0/1's exact function signatures, Chunk 3b depends on Chunk 1's and Chunk 3's exact shape, and Chunk 4 depends on Chunk 2/3's exact class/CLI shape.
