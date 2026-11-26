# RavestickBoard · Hardwaretest v0.7.2-dev (Aufräumer aus dem Test von 0.7.1)

**Stand: 26.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.7.1 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.7.2.xlsx` (dort mit Auswahlliste und Zusammenfassung).

**Zum Stand:** 0.7.1 ist auf der Hardware getestet und läuft stabil (73 min, 67 Aufträge, mehr als 3000 BLE-Pakete, keine Fehler, kein Neustart). Es dient als Rückfallversion. 0.7.2 ändert nur Kleinigkeiten an der Oberfläche und räumt die Mischfarben-Dateien auf; an der Firmware ändert sich nur die Versionszeile.

**Am Rechner geprüft, nicht auf der Hardware:** alle Tests mit Endung `0702`. **Nicht geprüft:** Arduino-Compile, Hardware, Safari.

## Vorbereitung

1. Mit 0.7.1 ein JSON-Backup ziehen, 0.7.1 als Rückfallversion aufbewahren.
2. Arduino IDE wie bisher (Arduino-ESP32 3.3.12, NimBLE-Arduino 2.5.2, ESP32C3 Dev Module, USB CDC On Boot Enabled, Partition „No OTA (2MB APP/2MB SPIFFS)“). `firmware/RavestickBoard_v0_7_2/RavestickBoard_v0_7_2.ino` öffnen, **alle acht Dateien** im Sketch-Ordner lassen.
3. Für Abschnitt D die sieben Dateien aus `docs/farbmischung/` aufs iPhone oder den Laptop legen.

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| A1 | Sketch kompilieren (Arduino-ESP32 3.3.12, Einstellungen wie bisher). Die beiden Zahlen am Ende (Programmspeicher, globale Variablen) in „Messwerte“ eintragen. | Kompiliert ohne Fehler. Zum Vergleich 0.7.1: Programmspeicher 1.600.577 Byte (76 %), globale Variablen 79.488 Byte. Der Programmspeicher sollte nur wenig abweichen (die Oberfläche ist kleiner geworden). |
| A2 | Flashen, mit dem WLAN RavestickBoard verbinden, Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.7.2-dev. |
| A3 | Diagnose-Datei öffnen, Kopf ansehen. | „WLAN-Puffer“ und „WLAN-Sicherheit“ stehen wie eingestellt; Version 0.7.2-dev. |

## B. Neu in 0.7.2 (Oberfläche)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| B1 | Ambiente öffnen und die Überschrift oben links mit „Bibliothek“, „Programme“ und „Animationen“ vergleichen (erst Handy, dann Laptop). | Die Überschrift „Ambiente“ steht an derselben Stelle und in derselben Größe wie in den anderen Masken; das Feld darunter beginnt auf gleicher Höhe. |
| B2 | Programme → ein Programm bearbeiten (oder neu anlegen) und die Maske von oben bis unten ansehen. | Der Hinweis „Blocktexte sind bei Tempo 60–90 kalibriert …“ steht nicht mehr da; sonst ist die Maske wie bisher. |
| B3 | Einstellungen → Backup exportieren (Auswahl wie gewünscht) und währenddessen den Export-Knopf beobachten. | Der Knopf ist während der Arbeit gelb mit einem durchlaufenden Balken; zum Schluss ist er wieder normal und die Meldung nennt die Zahlen. |
| B4 | Dasselbe mit dem Import (Backup zusammenführen). | Der Import-Knopf zeigt während der Arbeit den gelben Balken; danach wieder normal; nichts doppelt. |
| B5 | Import starten und die Dateiauswahl abbrechen; danach einen Export mit Fehler provozieren ist nicht nötig. | Es bleibt kein Knopf gelb zurück; die Oberfläche ist normal bedienbar. |

## C. Dauer von Programmen (Messung mit der Stoppuhr)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| C1 | Ein Programm mit einem Blocktext aus 40 Seiten anlegen (Tempo ist fest 80) und starten. Stoppuhr starten, sobald die Tafel den Block beginnt zu zeigen, und anhalten, wenn er zum zweiten Mal anfängt. Wert in „Messwerte“ eintragen. | Die Rechnung der Software sagt rund 63,6 s je Durchlauf. Weicht die Stoppuhr deutlich ab, bitte die Sekunden notieren; daran wird die Formel später angepasst. |
| C2 | Ein Programm mit zwei Blocktexten (je 10 Seiten) und Anzeigedauer 30 s je Eintrag starten und einen ganzen Durchlauf mit der Uhr verfolgen. | Die Wechsel passen zur eingestellten Dauer; kein Eintrag wird abgeschnitten oder zu lange gezeigt. Abweichungen in Sekunden in die Bemerkung. |

## D. Mischfarben (7 Dateien in docs/farbmischung/)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| D1 | Animationen → + → Text-Raster → „Textdatei laden“ → `limette_gruen_gelb.txt`, `himmelblau_blau_cyan.txt` und `hellblau_blau_weiss.txt`, je 1 ms je Frame, senden. Ein Ergebnis je Datei in die Bemerkung. | Limette: gelbliches Grün. Himmelblau: Blau mit Cyan-Anteil. Hellblau: helles Blau. Mischfarben wirken dunkler als reine Farben. |
| D2 | Wie D1 mit `orange_rot_gelb.txt` und `orange_rotlastig_rot_rot_gelb.txt` (je 1 ms). | Orange und ein tieferes, rötliches Orange. |
| D3 | Wie D1 mit `pastellrot_rot_weiss.txt` und `pastellgruen_gruen_weiss.txt` (je 1 ms). | Sehr helles Rosa und ein Pastellgrün (wie das Mint der Oberfläche). |
| D4 | Eine Datei (zum Beispiel Limette) mit 5 ms, 7 ms und 8 ms je Frame senden. | Bei 5 und 7 ms kein Flimmern, bei 8 ms leichtes Flimmern (62,5 Hz an der Grenze). Bitte beschreiben, wo es anfängt. |

## E. Kurzer Gesamtlauf

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| E1 | Lauftext, Blocktext, Animation und Ambiente-Farbe nacheinander senden. | Alles erscheint wie in 0.7.1. |
| E2 | Ein Programm starten und beenden; danach Kurzwahl antippen. | Programm läuft und endet; Kurzwahl wie gewohnt ohne Erfolgsmeldung. |
| E3 | Am Ende die Diagnose-Datei, die RAM-Datei und `http://192.168.4.1/api/http.txt` speichern; unter „Messwerte“ die beiden Heap-Werte eintragen. | Keine ungeplanten Neustarts, keine Fehler; der kleinste freie Heap liegt in der Größenordnung von 0.7.1 (19.560 Byte). |

## F. Noch offen aus 0.7.1

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| F1 | Diagnose-Datei, Abschnitt „ZÄHLER SEIT BOOT“: Zeile „Programm durch Senden beendet“ (nach einem Test wie in 0.7.1 D1). | Zählt nur Fälle mit Meldung, nicht die stillen Fälle in der Anzeigedauer. |
| F2 | Backup aus 0.6.1.11 einspielen (falls vorhanden). | Wie B4: nichts doppelt. |
| F3 | Kurzbefehl für Kurzwahl 1 und für eine Animation anlegen (ID unter http://192.168.4.1/api/anim/list nachsehen). | Kurzwahl startet; die Animation läuft. |
| F4 | Kurzbefehl auslösen, während gerade übertragen wird. | Antwort 409; nach ein paar Sekunden erneut auslösen klappt. |
| F5 | Optional: Speichern einer Animation starten und die Seite schließen. | „Letzte Ereignisse“ nennt nach 60 s den verlassenen Upload; sonst auslassen. |
| F6 | iPhone: Screenshots der richtigen Kurzbefehle-Konfiguration machen (Tafeltext, Kurzwahl, Animation) und mitschicken. | Die Bilder kommen in die Anleitung `docs/KURZBEFEHLE.md`. |

Ergebnisse, Messwerte und Bemerkungen gehören in die Excel-Datei; die Diagnose-Datei, die RAM-Datei und `http://192.168.4.1/api/http.txt` bitte wie bisher mitschicken.
