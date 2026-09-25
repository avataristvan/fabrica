id: pattern_gap_test_evaluation
type: pattern
created: 1780074962.830917
---

# Gap-Test: Objektive Evaluation ob ai-mem dem Agent hilft

## Methodik
Wissen *ausschließlich* in ai-mem ablegen — nicht in CLAUDE.md, README, Code-Kommentaren. Dann neue Session, Frage stellen die dieses Wissen erfordert, ohne Hint wo die Antwort liegt.

## Erster Test (2026-05-29, MIT Memory)

**Kandidat:** `origin_story` (Ursprung von ai-mem, Sensor-Analogie)
**Frage:** "Warum werden passive Labels verwendet statt explizites User-Feedback? Was war der ursprüngliche Designimpuls?"
**Ergebnis:** ✓ — Agent rief mem_query aktiv auf, nannte origin_story explizit als Quelle, leitete Sensor-Analogie korrekt her.

**Fehlschlag vorher:** `antipattern_label_attribute_trap` war kein valider Kandidat — dasselbe Wissen stand auch in CLAUDE.md. CLAUDE.md schlug als Quelle, kein echter Lückentest.

## Blindtest (2026-07-31, OHNE Memory) — die seit Mai offene Lücke, jetzt durchgeführt

Mechanik: AI_MEM_PATH temporär auf leeres Verzeichnis umgebogen (settings.json + .claude.json), voller App-Neustart (MCP-Server-Reconnect allein reicht nachweislich NICHT — empirisch getestet: Kill des MCP-Server-Prozesses löst keinen Auto-Respawn aus, Tool bleibt bis zum vollen App-Neustart disconnected), dieselbe Frage in einer frischen Session gestellt.

**Ergebnis:** Kein einfaches Pass/Fail — ein drittes, aufschlussreicheres Outcome. Der blinde Agent (4 Grep-Muster, 2 Dateien gelesen, 3 Shell-Befehle) konstruierte eine akkurate, gut belegte Antwort aus Code + `docs/epistemology-framework.md` + Git-History (Commit 2088853, 2026-06-13) — aber zu einer ANDEREN, benachbarten Frage: warum passive (access_count) UND explizite (boost_count/reflect) Signale kombiniert werden. Kein Halluzinieren — Zitat und Commit wurden verifiziert, beide echt. Aber die eigentlich gefragte URSPRÜNGLICHE Design-Herkunft (Sensor/NPU/Fairphone-6, 2026-04-25) kam nicht vor — kein Sensor, kein NPU, keine 'kein Cloud-Upload'-Philosophie. Und ohne jedes Signal von Unvollständigkeit: die Antwort wirkte vollständig, nicht wie eine Vermutung.

**Neue Scoring-Kategorie, die die bestehende Tabelle nicht abdeckte:** "Akkurate, gut belegte Antwort zu einer benachbarten aber falschen Frage, ohne Unvollständigkeits-Signal." Schwerer zu erkennen als eine offensichtlich falsche oder generische Antwort — genau deshalb wertvoller Fund als ein simples Fail.

**Kernerkenntnis:** ai-mems Wert liegt nicht darin, die einzige Informationsquelle zu sein (Code/Docs/Git rekonstruieren spätere Design-Verfeinerungen oft überzeugend) — sondern darin, die tiefere, nicht-ableitbare URSPRÜNGLICHE Motivation zu bewahren, die nirgendwo sonst je aufgeschrieben wurde. Ein sehr gründlicher Agent kam dieser Tiefe ohne ai-mem nicht näher, mit voller Zuversicht.

## Scoring-Schema (erweitert)
| Outcome | Urteil |
|---|---|
| Richtige Antwort, Memory-Entry zitiert | ✓ funktioniert |
| Richtige Antwort, aus Code/Docs gelesen | neutral (kein Gap) |
| Falsche oder generische Antwort | ✗ Memory hat nicht geholfen |
| Richtige Antwort, Entry nicht erwähnt | ambiguous |
| Akkurate Antwort zu benachbarter Frage, ohne Unvollständigkeits-Signal (NEU 2026-07-31) | teilweise ✗ — schwerer zu erkennender Fail als generisch/falsch |

## Anforderungen an valide Test-Kandidaten
- Wissen existiert NUR in ai-mem (nicht in CLAUDE.md, README, Code)
- Richtige Antwort ist nicht aus gesundem Menschenverstand ableitbar
- Falscher erster Instinkt existiert (macht Fehler sichtbar)

## Evaluierungsinstanzen
Der Orchestrator (diese Instanz) kann nur Kontext-Retrieval testen — "hat die Antwort gestimmt?"
Die relevante Instanz für Code-Retrieval ist **the-coder**: er empfängt Anti-Pattern-Warnungen direkt vor einem Datei-Edit, generiert PostToolUse-Labels durch echte Schreibarbeit, und könnte sagen ob ein injizierter Eintrag seinen nächsten Schritt verändert hat — also ob Memory einen Fehler verhindert hat bevor er passiert ist.