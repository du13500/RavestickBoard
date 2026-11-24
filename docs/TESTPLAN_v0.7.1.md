# RavestickBoard · Hardwaretest v0.7.1-dev (Programmtempo 80, Kurzwahl, Aufräumer, Mischfarben)

**Stand: 23.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.7.0 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.7.1.xlsx` (dort mit Auswahlliste und Zusammenfassung).

**Am Rechner geprüft, nicht auf der Hardware:** alle Tests mit Endung `0701`. **Nicht geprüft:** Arduino-Compile, Hardware, Safari.

**Was an D1 bis D3 und D5 klargestellt ist:** Die Meldung „Das Programm wird beendet“ erscheint nur, solange gerade ein Programmschritt übertragen wird. Wartet das Programm in seiner Anzeigedauer, geht dein Inhalt sofort hinaus und das Programm endet still. Das war im Test von 0.7.0 kein Fehler, sondern die Erwartung war zu eng.

## Vorbereitung

1. Mit 0.7.0 ein JSON-Backup ziehen, 0.7.0 als Rückfallversion aufbewahren.
2. Arduino IDE wie bisher (Arduino-ESP32 3.3.12, NimBLE-Arduino 2.5.2, ESP32C3 Dev Module, USB CDC On Boot Enabled, Partition „No OTA (2MB APP/2MB SPIFFS)“). `firmware/RavestickBoard_v0_7_1/RavestickBoard_v0_7_1.ino` öffnen, **alle acht Dateien** im Sketch-Ordner lassen.
3. Für Abschnitt K die Dateien aus `docs/farbmischung/` aufs iPhone oder den Laptop legen.

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| A1 | Sketch kompilieren (Arduino-ESP32 3.3.12, Einstellungen wie bisher). Die beiden Zahlen am Ende (Programmspeicher, globale Variablen) in „Messwerte“ eintragen. | Kompiliert ohne Fehler. Zum Vergleich 0.7.0: Programmspeicher 1.600.313 Byte (76 %), globale Variablen 79.488 Byte. |
| A2 | Flashen, mit dem WLAN RavestickBoard verbinden, Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.7.1-dev. |
| A3 | Diagnose-Datei öffnen, Kopf ansehen. | „WLAN-Puffer“ und „WLAN-Sicherheit“ stehen wie eingestellt (Voreinstellung begrenzt, WPA2); Version 0.7.1-dev. |

## B. Programme mit festem Tempo 80

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| B1 | Tempo-Regler auf einen anderen Wert stellen (zum Beispiel 40), dann ein Programm mit mindestens drei Einträgen starten. | Der Regler springt auf 80 und ist gesperrt, solange das Programm läuft. |
| B2 | Programm bis zum Ende laufen lassen oder beenden. | Der Regler bleibt auf 80 stehen und lässt sich wieder verstellen. |
| B3 | Ein Programm mit Blocktexten starten und die Anzeigedauer mit der Uhr gegen die eingestellte Dauer prüfen. | Dauer stimmt (Tempo 80 ist die gemessene Stufe). |
| B4 | Regler auf 40 stellen, danach einen Blocktext aus der Bibliothek einzeln senden. | Der Blocktext läuft mit 40; das feste Tempo 80 gilt nur für Programme. |
| B5 | Kurzwahl mit einem Programm belegen und antippen. | Programm startet, Regler zeigt 80. |

## C. Kurzwahl ohne Erfolgsmeldung

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| C1 | Kurzwahl mit Text oder Block antippen. | Keine Meldung „wird an die Tafel übertragen“; die Pille „Übertragung läuft“ zeigt den Ablauf; die Tafel zeigt den Inhalt. |
| C2 | Kurzwahl mit Animation und Kurzwahl mit Ambiente antippen. | Keine Erfolgsmeldung („gestartet“); Tafel reagiert. |
| C3 | Kurzwahl mit Programm antippen. | Keine Meldung „gestartet“; das Programm läuft. |
| C4 | Eine leere Kurzwahl antippen und eine Kurzwahl antippen, während gerade übertragen wird. | Fehler und Hinweise erscheinen weiterhin (leer: Fenster zum Belegen; Übertragung: Hinweis). |

## D. Senden während ein Programm läuft (Erwartung präzisiert)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| D1 | Programm mit mindestens drei Einträgen starten. **Während ein Programmschritt übertragen wird** (Pille „Übertragung läuft“ sichtbar), einen Blocktext aus der Bibliothek senden. | Meldung „Das Programm wird beendet. Dein Inhalt folgt gleich …“; danach läuft dein Inhalt. |
| D2 | Programm starten, **in der Anzeigedauer** (Pille aus) einen Blocktext senden. | Der Inhalt wird sofort übertragen, das Programm endet ohne Meldung. So ist es gewollt. |
| D3 | Wie D2 mit einer Kurzwahl mit Text und mit einer Ambiente-Farbe. | Wie D2. |
| D4 | Programm starten; Helligkeit verändern. | Programm läuft weiter, Helligkeit ändert sich. (Tempo ist während eines Programms gesperrt.) |
| D5 | Diagnose-Datei, Abschnitt „ZÄHLER SEIT BOOT“: Zeile „Programm durch Senden beendet“. | Zählt nur Fälle wie D1 (Meldung gezeigt), nicht die stillen Fälle aus D2 und D3. |

## E. Animationen

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| E1 | Animationen → Liste, eine Animation auswählen. | Unter der Vorschau steht Bildzahl, Zeit je Frame und Schleifenzeit, **ohne** „Play spielt sie ab“ und **ohne** ID. |
| E2 | Play drücken, danach Stop. | Animation spielt; die Taste wird zum Quadrat und wieder zum Dreieck. |
| E3 | Eine Animation an die Tafel senden; während „Übertragung läuft“ zu sehen ist, die Play-Taste ansehen und antippen. | Play ist gesperrt (ausgegraut), solange übertragen wird; danach wieder bedienbar. |
| E4 | Die Seitenüberschrift „Animationen“ mit „Bibliothek“ und „Programme“ vergleichen (Handy). | Alle drei Überschriften stehen auf gleicher Höhe. |
| E5 | Animation umbenennen und verschieben. | Funktioniert; es erscheint keine ID. |

## F. Backup und Export

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| F1 | Einstellungen → Backup exportieren (Auswahl wie gewünscht). | Die Knopfbeschriftung zeigt „Backup: …“ ohne Auslassungspunkte am Ende; die Meldung zum Schluss nennt die Zahlen. |
| F2 | Das Backup wieder einspielen (Backup zusammenführen). | Knopf zeigt „Import: …“ ohne Auslassungspunkte; Zahlen am Ende; nichts doppelt. |
| F3 | Das Symbol am Import- und Export-Knopf während der Arbeit beobachten. | Das Symbol pulsiert nicht (nur die Pille „Übertragung läuft“ pulsiert). |
| F4 | Backup aus 0.6.1.11 einspielen (falls vorhanden). | Wie F2: nichts doppelt. |

## G. Design

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| G1 | Editor → Lauftext → „Mini - Zweizeilig“. Farbzeilen ansehen (Handy). | Beide Zeilen haben acht Plätze; die Farbpunkte stehen genau untereinander; der Palettenknopf ist der letzte Platz in Zeile 1, in Zeile 2 bleibt der letzte Platz leer. |
| G2 | Auf „Mini - Einzeilig“ zurückschalten; Palettenknopf antippen. | Einzeilig wie bisher; der Knopf öffnet das Fenster „Zeichen gestalten“. |
| G3 | Editor, Lauftext zweizeilig: „Text · Zeile 1“ und „Text · Zeile 2“ vergleichen. Bitte genau beschreiben, was abweicht (Größe, Farbe, Abstand, Ausrichtung) oder ein Foto schicken. | Beide Beschriftungen gleich. (In der Messung am Rechner sind Größe, Farbe und Ausrichtung gleich; falls es auf dem iPhone abweicht, bitte Foto.) |
| G4 | Programme → ein Programm bearbeiten (Maske „Programm bearbeiten“) ansehen. | Unten steht kein Bedienfeld (Regler, Modusknöpfe) mehr; nach Speichern oder Zurück ist es wieder da. |
| G5 | Auf dem iPhone durch alle Seiten blättern. | Nichts verrutscht oder abgeschnitten. |

## H. Kleinigkeiten

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| H1 | Laptop: Kurzwahl-Stift antippen, eine Kurzwahl wählen (Fenster „Kurzwahl belegen“), Escape drücken. | Das Fenster schließt; der Fokus springt zurück auf die Kurzwahl. |
| H2 | Dasselbe mit Abbrechen statt Escape; mit Tab durch das Fenster gehen. | Fokus bleibt im Fenster; nach dem Schließen wieder bei der Kurzwahl. |

## K. Mischfarben (Dateien in docs/farbmischung/)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| K1 | Animationen → + → Text-Raster → „Textdatei laden“ → `limette_gruen_gelb.txt`, Zeit je Frame 1 ms, speichern und senden. | Ein gelbliches Grün (Limette). Mischfarben wirken dunkler als reine Farben. |
| K2 | Wie K1 mit `mint_gruen_cyan.txt`. | Ein helles bläuliches Grün (Mint). |
| K3 | Wie K1 mit `himmelblau_blau_cyan.txt`. | Ein Blau mit Cyan-Anteil (Himmelblau). |
| K4 | Wie K1 mit `violett_blau_magenta.txt`. | Ein Violett. |
| K5 | Wie K1 mit `rosa_rot_magenta.txt`. | Ein Rosa. |
| K6 | Wie K1 mit `hellblau_blau_weiss.txt`. | Ein helles Blau. |
| K7 | Wie K1 mit `pastellrot_rot_weiss.txt`, `pastellgruen_gruen_weiss.txt` und `pastellgelb_gelb_weiss.txt` (drei Dateien, ein Ergebnis je Datei in die Bemerkung). | Hellere Töne der jeweiligen Farbe. |
| K8 | Wie K1 mit `grau_rot_cyan.txt`, `grau_gruen_magenta.txt` und `grau_blau_gelb.txt` (ein Ergebnis je Datei). | Ein Weiß-Grau oder ein Farbstich; bitte beschreiben. |
| K9 | `orange_rotlastig_rot_rot_gelb.txt` und `orange_gelblastig_rot_gelb_gelb.txt` mit 1 ms. | Rotlastig: tieferes Orange (Rot-Orange); gelblastig: helleres Orange. |
| K10 | Eine Mischung (zum Beispiel Limette) mit 5 ms und mit 10 ms. | Rechnung: zwei Bilder bei 5 ms ergeben 100 Hz (über der Flimmergrenze von etwa 62 Hz), bei 10 ms 50 Hz (darunter). Bei 10 ms ist Flimmern zu erwarten; bitte beschreiben, ab wann es sichtbar wird. |

## L. Offen aus 0.7.0

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| L1 | Kurzbefehle (docs/KURZBEFEHLE.md): iPhone-Kurzbefehl „Tafeltext“ anlegen und per Siri auslösen. | Siri fragt nach dem Text; er erscheint als Lauftext. |
| L2 | iPhone-Kurzbefehl für Kurzwahl 1; danach für eine Animation: die ID im Browser unter http://192.168.4.1/api/anim/list nachsehen. | Kurzwahl startet; die Liste zeigt `id` und `name`; die Animation läuft. |
| L3 | Kurzbefehl auslösen, während gerade übertragen wird. | Antwort 409; nach ein paar Sekunden erneut auslösen klappt. |
| L4 | War die Anleitung verständlich? Wo hast du gehakt? | Kurz notieren. |
| L5 | Verlassener Upload (0.7.0 E4, nicht reproduzierbar): optional erneut versuchen, Speichern starten und die Seite schließen. | „Letzte Ereignisse“ nennt nach 60 s den verlassenen Upload; sonst auslassen (am Rechner im Hosttest geprüft). |

Ergebnisse, Messwerte und Bemerkungen gehören in die Excel-Datei; die Diagnose-Datei, die RAM-Datei und `http://192.168.4.1/api/http.txt` bitte wie bisher mitschicken.
