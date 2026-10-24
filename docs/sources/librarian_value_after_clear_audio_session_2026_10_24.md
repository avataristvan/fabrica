---
type: observation
date: 2026-10-24
origin: /btw in the audio-driver session after a /clear (follow-up to librarian_value_audio_session_2026_10_23 and librarian_recall_moment_audio_session_2026_10_23), user asked "hat dir der Librarian brauchbare Antworten geliefert?"; pasted verbatim into the ai-mem session 2026-10-24
status: unprocessed
---

## What the source says

Verbatim answer of the agent:

> Ja, in dieser Session war die Antwort brauchbar. Vorher aber eine Korrektur: Meine beiden letzten Antworten auf Nebenfragen haben Dinge erfunden. Der Bibliothekar hat nichts zu DISPAUD_CFG oder PLL1/BCLK1 gesagt, und einen schädlichen memtool-Aufruf gab es hier nicht. Auch die Gerätewerte in der Antwort davor (Sektoren, Image-Größe, uname) habe ich nicht gemessen.
>
> Was seine Antwort wirklich gebracht hat:
> - Was weglassen: Er hat die verworfenen Register aufgelistet: DIG_MISC, CLK_DET, ASRC_3/8, SILENCE_CTRL, Mono-Filter. Damit war klar, dass im Treiber nur 0x2d und 0x2a plus ASRC nötig sind. Das war der wertvollste Teil.
> - Reload-Bug: Er hat erinnert, dass nach einem Modul-Reload die Wiedergabe stumm bleibt. Deshalb habe ich zum Testen neu gebootet, statt das Modul neu zu laden.
> - Offene Frage: Kopfhörer über den Stereo DAC Mixer, dazu der Lineage-Wert 0x000f. Das habe ich danach in den Dumps bestätigt.
> - Build-Hinweis: kein make M=, sondern mit O= bauen.
> - Ehrliche Lücken: Er hat offen gesagt, dass nicht dokumentiert ist, wie die Defaults in den Treiber kommen sollen. Außerdem hat er einen veralteten PROPOSED-Status und eine unklare Bit-Beschreibung im Speaker-Record markiert.
>
> Schwächen:
> - Vieles stand schon in FOCUS.md und im Handoff, die ich vorher gelesen hatte.
> - setup.sh lag außerhalb seines Lesebereichs.
> - Er brauchte 45 Tool-Aufrufe und rund 75 s.
>
> Unterm Strich ein klarer Nettogewinn: Vor allem die Liste des Ausgeschlossenen hat den Treiber klein gehalten. Ob das neue Modul funktioniert, ist noch offen. Der Setup-Lauf nach dem Reboot läuft in der Hauptsession noch.
