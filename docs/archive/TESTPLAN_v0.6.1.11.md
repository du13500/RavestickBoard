# RavestickBoard · Hardwaretest v0.6.1.11-dev (Stabilität, Korrekturen, Backup mit Animationen, WLAN-Passwort)

**Stand: 17.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.10 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.6.1.11.xlsx` bereit. **Hauptfrage:** Bleibt der Speicher mit **einem Gerät** (Normalfall auf dem Festival) auch unter Last deutlich über 10 KB System-Minimum, und läuft der Betrieb mit **zwei Geräten** ohne Neustart (notfalls mit „Speicher knapp, bitte gleich noch einmal“)? Dazu die neuen Funktionen (WLAN-Passwort, Backup mit Animationen, Play-Taste) und die Korrekturen aus den Reviews.

**Am Rechner geprüft, nicht auf der Hardware:** alle Tests mit Endung `06111` (Host-, Browser-, Build- und Paritätstests), darunter die Markierung „auf der Tafel“ bei Fehlern, Backup mit Animationen und WLAN-Passwort in einer simulierten Umgebung. **Nicht geprüft:** Arduino-Compile, Hardware, Safari, das echte Neustarten des WLANs und die BOOT-Taste.

## Vorbereitung

1. JSON-Backup aus 0.6.1.10 ziehen (es enthält noch keine Animationen), 0.6.1.10 als Rückfallversion aufbewahren.
2. Arduino IDE wie bisher (NimBLE-Arduino 2.5.2 ist installiert). `firmware/RavestickBoard_v0_6_1_11/RavestickBoard_v0_6_1_11.ino` öffnen, **alle acht Dateien** im Sketch-Ordner lassen. `RB_TEST_HANG` und die Messungen sind im Entwicklungsstand an (`RB_RELEASE 0`).
3. iPhone und Laptop bereitlegen, die Tafel in Reichweite. Für Abschnitt B ist **nur das iPhone** im WLAN (am Laptop WLAN aus).
4. Nach dem Test Diagnose, `ram.txt` und `http.txt` exportieren; Seriallog mitlaufen lassen.
5. Das WLAN-Passwort, das du in Abschnitt E vergibst, **aufschreiben**.

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| A1 | Sketch kompilieren. Die beiden Zahlen am Ende (Programmspeicher, globale Variablen) **notieren**. | Kompiliert. Globale Variablen etwa **9 KB weniger** als 0.6.1.10 (88.800 Byte), weil das Seitenband für Blocktexte nicht mehr fest im RAM liegt (Rechnung, nicht gemessen). Bei einer Fehlermeldung: komplett kopieren. | | |
| A2 | Flashen, mit dem WLAN `RavestickBoard` verbinden (Standardpasswort wie bisher), Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.6.1.11-dev. | | |
| A3 | Diagnose öffnen und die neuen Zeilen ansehen: „WLAN-Passwort“, „Build“, „NimBLE-Arduino“, „Seitenband“. | „Standardpasswort (oeffentlich)“, „Entwicklung“, eine Versionsnummer oder „nicht abfragbar“, Seitenband „frei“. Was bei NimBLE steht, **notieren**. | | |

## B. Speicher mit einem Gerät (Hauptfrage, Normalfall)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Diagnose: START-AUFTEILUNG, Wert „Nach WLAN-AP“ **notieren**. | Mehr als in 0.6.1.10 (59.148 Byte), erwartet etwa 68 KB (Rechnung). | | |
| B2 | Nur das iPhone ist verbunden. Einige Sekunden nichts tun, dann Diagnose: freier Heap **notieren**. | 0.6.1.10 mit einem Gerät: etwa 35 bis 37 KB. Erwartung: mehr. | | |
| B3 | Nur mit dem iPhone: Seite neu laden, Bibliothek öffnen, einen Blocktext auswählen (Vorschau), einen Blocktext senden, eine Animation abspielen (Play) und senden, ein Programm starten und stoppen, eine Kurzwahl drücken. Dann Diagnose: **System-Minimum** und kleinster freier Heap **notieren**. | Kein Neustart. System-Minimum **deutlich über 10 KB** (Ziel aus der Roadmap). | | |

## C. Speicher mit zwei Geräten (Ausnahme)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | Laptop dazu verbinden. Auf beiden Geräten abwechselnd die Abläufe aus B3, etwa 15 Minuten. | Kein Neustart. Ein kurzes „Speicher knapp, bitte gleich noch einmal versuchen“ ist erlaubt; die Seite holt sich die Daten danach selbst. | | |
| C2 | Danach Diagnose: System-Minimum, kleinster freier Heap und „HTTP-Anfragen wegen knappem Heap vertagt (503)“ **notieren**. | 0.6.1.10: System-Minimum bis 2.012 Byte. Erwartung: höher. | | |

## D. Senden und Programme

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Bibliothek → einen **Blocktext** senden. | Kommt an; in der Bibliothek erscheint bei diesem Blocktext der Punkt „auf der Tafel“ (war in 0.6.1.9/0.6.1.10 nicht so, E7). | | |
| D2 | Ein Programm mit **mehreren Gruppen** starten. Während es läuft, in der Bibliothek einen **Lauftext** senden. Eine Minute warten. | Das Programm hört auf; der Lauftext bleibt auf der Tafel und wird **nicht** vom nächsten Programmschritt überschrieben. „Auf der Tafel“ steht beim Lauftext. | | |
| D3 | Programm wieder starten. Im Texteditor bei Blocktext „Diese Seite senden“. Eine Minute warten. | Wie D2: Programm aus, die Seite bleibt. | | |
| D4 | Texteditor → Blocktext mit mehreren Seiten → „Alle Seiten senden“. Danach Diagnose, Zeile „Seitenband“. | Kommt an; danach steht „Seitenband … frei“ und „zu wenig Speicher seit Start: 0“. | | |
| D5 | Eine Animation senden und nach etwa 5 s die Tafel ausschalten. | Meldung „**Animationsübertragung** abgebrochen: Paket … nicht bestätigt.“ (vorher stand „Text…“). Kein Neustart. | | |
| D6 | Während eine Animation gesendet wird, die Helligkeit ändern. | Hinweis „Controller beschäftigt: Die Einstellung wird nachgeholt.“; nach der Übertragung hat die Tafel die neue Helligkeit. | | |
| D7 | Lauftext senden, Kurzwahl drücken, Ambiente senden (Gegenprobe). | Wie bisher. | | |

## E. WLAN-Passwort

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Einstellungen → WLAN-Passwort. | „Das öffentliche Standardpasswort ist aktiv …“, kein Knopf „Standardpasswort wiederherstellen“. | | |
| E2 | Ein zu kurzes Passwort (z. B. 5 Zeichen) speichern. | Fehlermeldung, nichts passiert. | | |
| E3 | Ein neues Passwort (8 bis 63 Zeichen, ohne Umlaute) eingeben, **aufschreiben**, speichern, Rückfrage bestätigen. | Meldung „Passwort gespeichert …“; nach etwa 2 s trennt das WLAN alle Geräte. | | |
| E4 | iPhone und Laptop mit dem **neuen** Passwort verbinden (am iPhone: Netzwerk ignorieren und neu verbinden). | Beide kommen rein; das alte Passwort geht nicht mehr. Diagnose: „eigenes Passwort aktiv“. | | |
| E5 | ESP32 kurz vom Strom nehmen und wieder anschließen. | Das neue Passwort gilt weiter. | | |
| E6 | Die BOOT-Taste am ESP32 **im laufenden Betrieb** nur kurz (1 s) drücken. | Nichts passiert. | | |
| E7 | Die BOOT-Taste **im laufenden Betrieb 5 Sekunden halten** (nicht beim Einstecken drücken!). | Das WLAN startet neu; verbinden geht jetzt wieder mit dem **Standardpasswort**. Diagnose: „Standardpasswort“, „per BOOT-Taste zurückgesetzt: 1“. | | |
| E8 | In den Einstellungen ein eigenes Passwort setzen und danach mit „Standardpasswort wiederherstellen“ zurück. | Beides wirkt wie beschrieben. Am Ende wieder Standard oder das Passwort, das du behalten möchtest (**notieren**, welches). | | |

## F. Backup mit Animationen

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | Einstellungen → Backup exportieren. Dauer und Dateigröße **notieren**. | Der Knopf zeigt „Backup: Animation … von …“; danach „Backup erstellt: … Bibliothekseinträge, … Programme, … Animationen, Kurzwahlen.“ | | |
| F2 | Die Datei am Laptop in einem Texteditor öffnen und nach dem WLAN-Passwort suchen. | Das Passwort steht nicht in der Datei. | | |
| F3 | Dieselbe Datei wieder importieren. | „0 neue Einträge, … vorhandene erkannt; …; 0 neue Animationen, … vorhandene“. Nichts ist doppelt. | | |
| F4 | Eine **nicht** benötigte Animation löschen, dann das Backup importieren. | Sie ist wieder da (neue Nummer); eine Kurzwahl, die auf sie zeigte, funktioniert wieder. | | |

## G. Oberfläche und Wünsche aus 0.6.1.9

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Gefällt mir so / lieber anders | Bemerkung |
|---|---|---|---|---|---|
| G1 | Animationen → Stift (Liste). Eine Zeile antippen. | Die große Vorschau zeigt sofort das Standbild, **lädt nichts**; daneben (nicht darüber) eine kleine Play-Taste. | | | |
| G2 | Play drücken; dann eine andere Zeile wählen; dann zurück und wieder Play. | Play lädt einmal und spielt durch; andere Zeile stoppt; beim zweiten Mal startet sie ohne Laden. „Bearbeiten“ danach öffnet ohne Ladebalken. | | | |
| G3 | Symbol Äffchen in einen Text setzen und senden. | Keine Nasenlöcher mehr (wirkt nicht mehr wie vier Augen). | | | |
| G4 | Die zwei neuen Dateien `assets/animationen/dvd_logo_ecke_unten_rechts.txt` und `dvd_logo_ohne_ecke.txt` importieren (Text-Raster, Zeit **60 ms** wie beim Original), senden. | Beide laufen wie das Original über die ganze Tafel als nahtlose Schleife (78 Bilder). „Ecke unten rechts“: einmal pro Runde der Eckentreffer unten rechts. „Ohne Ecke“: verfehlt die Ecke oben links jedes Mal um 1 Pixel. | | | |
| G5 | Texteditor → Blocktext, Seite 1 auswählen, „Seite duplizieren“. | Die Kopie steht als Seite 2 direkt hinter dem Original und ist ausgewählt. | | | |
| G6 | Mehrmals schnell zwischen Bibliothek, Programmen und Animationen wechseln, gleich nach dem Laden der Seite. | Listen erscheinen wie gewohnt; im `http.txt` steht `/api/library` beim Start nur einmal. | | | |

## H. Gesamt

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | Neustarts außer dem geplanten WLAN-Neustart (E3, E7). | Keiner; sonst Phase und was du gerade getan hast **notieren**. | | |
| H2 | Gesamteindruck: Laden der Seite, Wechsel zwischen den Bereichen, Senden. | Frei. | | |
| H3 | Nur falls Zeit: am iPhone (Einstellungen → WLAN → (i) neben `RavestickBoard`) und an weiteren eigenen Geräten die „WLAN-Adresse“ ansehen und mit der unbekannten Endung aus dem letzten Log vergleichen. | Notieren, zu welchem Gerät sie gehört oder dass sie zu keinem passt. | | |
