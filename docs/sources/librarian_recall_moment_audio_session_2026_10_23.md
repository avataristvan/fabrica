---
type: observation
date: 2026-10-23
origin: /btw follow-up in the same audio-driver session as librarian_value_audio_session_2026_10_23, user asked "welche regel könnte man erstellen, damit du zu einem Zeitpunkt genau dieses Wissen abrufen kan…"; pasted verbatim into the ai-mem session 2026-10-23 (the paste ends mid-sentence)
status: processed
---

## What the source says

Verbatim answer of the agent:

> Zuerst eine Korrektur: Meine vorige Antwort zum Wert des Bibliothekars hat Inhalte beschrieben (DISPAUD_CFG, Dev-Team-Aufteilung, PLL1/BCLK1), die nicht aus seiner Nachricht in dieser Session stammen. Die echte Nachricht behandelte Rauheit, Loopback und devsh/Flashen. Das memtool-Learning war nicht dabei, weil ich nicht danach gefragt hatte. Das war der eigentliche Fehler.
>
> Wo es versagt hat: Den Bibliothekar habe ich nur am Sessionstart gefragt. Den Moment, in dem das Learning gepasst hätte, gab es erst später: die Entscheidung „jetzt schreibe ich mit memtool direkt in Mixer-Register". Eine Regel wie „frag bei Richtungswechseln" steht schon in CLAUDE.md und hat trotzdem nicht gegriffen. Eine weitere Regel dieser Art würde vermutlich genauso scheitern, weil sie davon abhängt, dass ich den Moment selbst erkenne.
>
> Was zuverlässiger wäre:
>
> 1. Ein Hook statt einer Regel. Ein PreToolUse-Hook auf Bash, der bei bestimmten Werkzeugnamen im Befehl (memtool, i2cx, dd, devsh.py … mmcblk) die Records nach diesem Namen greppt und Treffer einblendet: Titel, cue: und eine Zeile Inhalt. Das läuft deterministisch, kostet fast nichts und braucht kein Urteil von mir. Genau in diesem Fall hätte es vor dem schädlichen Aufruf gegriffen.
> 2. Der Archivar sorgt für Grep-Bares. Records über Werkzeuge oder Register sollten den Werkzeugnamen bzw. die Adresse wörtlich in Titel oder cue: tragen, etwa memtool, 0x14880058 oder s1402x. Dann findet der Hook sie sicher.
>
> Selbst lesen oder Bibliothekar:
> - Bei werkzeug- oder registerspezifischen Lektionen ist ein Grep über docs/records/ nach dem Stichwort besser: schneller, vollständiger und ohne Interpretation. „memtool" hätte sofort getroffen.
> - INDEX.md hilft für einen Überblick, aber nicht im Moment der Aktion. Es ist zu lang, um es jedes Mal zu lesen, und zu grob für Stichworte.
> - Der Bibliothekar ist für Urteilsfragen da: Wurde das schon probiert, warum ist das so, widersprechen sich Records? Dort lohnt er sich, als Stichwort-Suche ist er zu teuer und zu indirekt.
>
> Mein Vorschlag als Kombination: Hook mit Stichwort-Grep vor riskanten Gerätekommandos,

## Candidate readings (not yet judged)

- The content of `librarian_value_audio_session_2026_10_23` is confabulated by the agent's own account: DISPAUD_CFG, the dev-team split and PLL1/BCLK1 were not in the librarian's message. The readings in that source that rest on them (access gap as cause, PLL1 correction candidate, "negative answers were most useful") are void; the timing reading still holds in a sharper form.
- Failure mode: the librarian was asked only at session start; the moment that mattered (memtool writes into mixer registers) came later, and the existing rule "ask at direction changes" did not fire because it depends on the agent recognising the moment.
- Proposal: a deterministic PreToolUse hook on Bash that greps records for risky tool names (memtool, i2cx, dd, devsh.py … mmcblk) and shows title, cue: and one line. Touches the retired PreToolUse push (`arch_decision_pretool_push_removed_2026_09_12`) — differs by being keyword-triggered on a short tool list, not a general push; needs judging against that record.
- Proposal: the archivist puts tool names and register addresses verbatim into title or cue: (e.g. memtool, 0x14880058, s1402x) so a grep finds them.
- Division of labour: keyword lookups → grep over docs/records/; judgment questions (tried before? why? contradictions?) → librarian; INDEX.md for overview only.
- Meta: an agent's self-report about a subagent's output can be confabulated — a /btw assessment is not evidence of what the subagent said without the transcript.
