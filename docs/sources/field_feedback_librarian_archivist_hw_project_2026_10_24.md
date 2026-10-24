---
type: observation
date: 2026-10-24
origin: Feld-Feedback des Agenten aus einem Hardware-Projekt (Pseudonym "hw-projekt-T", Mainline-Kernel für ein Tablet), vom User wörtlich in die ai-mem-Session 2026-10-24 kopiert; dazu die Antwort derselben Session auf eine Rückfrage aus ai-mem (Cross-Session-Nachricht, gleicher Tag)
status: processed
---

## What the source says

Pseudonymisiert vor der Ablage: Projektname → `hw-projekt-T`, Gerätekennung in Record-ids → `<dev>`, PMIC-Typ → `<pmic>`. Sonst wörtlich.

### Teil 1: Feedback, auf die Frage des Users, ob Docs und Bibliothekar geholfen haben

> Ja, beides hat geholfen, in unterschiedlichem Maß.
>
> Docs im Repo (FOCUS.md und Handoff): sehr. Auf dein „weiter" konnte ich sofort loslegen, ohne irgendetwas neu herauszufinden. Die Reihenfolge der Aufgaben, der Pfad zu devsh.py, der HTTP-Server, das Flash-Verfahren, der Modul-Swap ohne Flash und der Hinweis „die erste Ausgabe nach dem Neu-Anstecken ist verstümmelt" standen alle drin. Das hat mehrere Testrunden gespart.
>
> Bibliothekar: zweimal gefragt, gemischtes Ergebnis.
> - dtbs_check: Nützlich war die Auskunft „Upstream wird nicht verfolgt". Damit war klar, dass schlanke Bindings nur für unseren Fork reichen, und ich habe nicht auf Upstream-Niveau gebaut. Zur ADC-Versorgung war nichts dokumentiert. Das war korrekt so, ich musste es selbst herleiten.
> - Power-Button:
>   - Hilfreich: Dass poweroff -f funktioniert, musste ich nicht mehr testen. Dass es keine Backlight-Steuerung gibt, hat meine Suche gleich in die richtige Richtung gelenkt.
>   - Irreführend: Er hat die Aussage „Langdruck = PMIC-Reset" weitergegeben. Ich habe sie ungeprüft in meine Frage an dich übernommen, und erst dein Nachhaken hat gezeigt, dass die Register eher auf den 2-Tasten-Modus deuten. Das lag nicht am Bibliothekar: Der Record selbst hat eine Vermutung wie einen Fakt formuliert, und der Bibliothekar hat ihn nur richtig zitiert.
>
> Was die Records nicht verhindern konnten: die ADC-mV-Falle. Darüber stand nirgends etwas, und jetzt ist sie als Pattern festgehalten.
>
> Kosten: Die Antworten des Archivars kamen oft und waren lang. Für die Qualität der Records war das gut, als Zwischenmeldungen für dich war es eher viel.

### Teil 2: Antwort auf die Rückfrage aus ai-mem (Herkunftsmarken [Datei]/[Kontext]/[Erinnerung] vom Agenten selbst)

> 1. Record: learning_<dev>_poweroff_f_works_stage1_2026_10_23 in hw-projekt-T/docs/records/mainline/learnings/ (perspective: user).
>    [Datei, git show e203e1b] Der ursprüngliche Satz lautet wörtlich: "A long press of the power key reboots the device instead; the PMIC manual reset causes that reboot."
>    [Datei, aktueller Stand] Der Archivar hat den Record in place korrigiert, nicht abgelöst. Observed heißt jetzt "A long press of the power key was seen to reboot the device instead." Die Cause-Zeile beginnt jetzt mit "The reboot on long press was first attributed to the PMIC manual reset. The <pmic> registers do not back that for Power alone (see learning_<dev>_<pmic>_manual_reset_regs_2key_2026_10_24); the cause is open."
>    Dazu ist der neue Record learning_<dev>_<pmic>_manual_reset_regs_2key_2026_10_24 entstanden. Ein Test, der die Frage entscheidet, steht als Todo im Record todo_<dev>_pmic_reset_test_numbered_images_flash_panfrost_2026_10_24.
>
> 2. [Datei, Fassung e203e1b] Die Herkunft fehlte ganz. Die PMIC-Ursache stand als Behauptung im Observed-Teil. Die Cause-Zeile war "Not investigated" und bezog sich nur auf den poweroff-Pfad (PS_HOLD). Evidence nannte nur "user test report 2026-10-23 20:05 ... no source file".
>    Nirgends stand, ob die PMIC-Zuordnung vom User kam oder vom Agenten erschlossen war. Durch perspective: user wirkte der ganze Satz wie eine Beobachtung des Users.
>    [Erinnerung] Der Bibliothekar hat das korrekt weitergegeben: "the PMIC manual reset causes it". Ich habe es ungeprüft übernommen, und erst die Rückfrage des Users hat zur Prüfung der Register geführt.
>
> 3. [Kontext] /reflect lief einmal. Der Archivar lief 5-mal:
>    - dtbs_check-Fixes
>    - Ladezonen + Teardown-Race
>    - DCP-Grenzen
>    - ADC-mV-Falle + pwrkeyd
>    - der /reflect selbst
>    [Kontext, geschätzt] Ein typischer Report hatte etwa 12–25 Zeilen.
>    Hat gezählt:
>    - die erste Zeile pro Kandidat (wohin, neu/Update/supersede)
>    - "not written" bzw. die Hinweise auf veraltete Stellen, z. B. "Handoff listet die Findings noch als offen", "zwei alte Records sagen noch X", "CLAUDE.md-Zeile veraltet". Das waren konkrete Aufträge an mich.
>    Für einen Zwischenstand überflüssig:
>    - die vollständigen Edge- und Back-Reference-Listen
>    - "back-references not written: none", "merge candidates: none", "third-time: none", "mem-dream: not needed"
>    - die Liste der Dateipfade
>    Ein Vorschlag: Leerzeilen der Form "none" weglassen, und die Edges nur als Zahl angeben, solange keiner widerspricht.
>
> 4. [Datei] Pattern: pattern_check_iio_consumer_values_after_provider_dt_change_2026_10_24 in docs/records/mainline/decisions/. Die zugehörige Ursache steht in learning_<dev>_adc_vdd_supply_switches_consumers_to_mv_2026_10_24 in docs/records/mainline/learnings/.

## Caveat

Teil 1 ist ein Selbstbericht des Agenten (schwache Evidenz, `learning_agent_selfreport_about_subagent_output_can_be_confabulated_2026_10_23`). Teil 2 ist nach Herkunft markiert: Die [Datei]-Angaben sind nachprüfbar, die Power-Button-Episode hat der User selbst erlebt.
