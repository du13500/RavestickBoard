# RavestickBoard · Hardwaretest v0.6.1.6-dev (Antworten während der Übertragung, Rahmen, 40 Blocktext-Seiten, Beispiel-Animationen)

**Stand: 12.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.5 (liegt in `archive/`). 0.6.1.5 lief auf der Hardware 1:44 h ohne Neustart (44 Schritte in Ordnung, 1 nicht, 9 nicht getestet, 9 „siehe Log“). Offen war B5: Während einer Übertragung zur Tafel antwortete der ESP32 keinem Gerät. **Hauptfrage dieses Tests:** Reicht der Stapel, wenn der ESP32 jetzt *während* der Übertragung kurz antwortet? Dafür gibt es in der Diagnose die neue Zeile „Stapel vor der ersten Webantwort … / danach“ (Abschnitt B). Die Tabelle gibt es auch als Excel-Datei; Ergebnis bitte dort eintragen.

**So ist es gedacht:** Während die Tafel Daten bekommt, sind auf **allen** Geräten die Knöpfe gesperrt, die senden oder etwas ändern. Auf dem Bedienfeld unten liegt dann „● Übertragung läuft …“. Seiten wechseln und bereits geladene Listen ansehen geht weiter. Es gibt absichtlich keinen weiteren Hinweis, warum gesperrt ist.

## Vorbereitung

1. **JSON-Backup** der Bibliothek ziehen (Einstellungen) und 0.6.1.5 als Rückfallversion aufbewahren. Wichtig: Ein Blocktext, den du mit 0.6.1.6 speicherst, kann 0.6.1.5 nicht mehr lesen; zurück geht es nur über das Backup.
2. `firmware/RavestickBoard_v0_6_1_6/RavestickBoard_v0_6_1_6.ino` öffnen, **alle sieben Dateien** im Sketch-Ordner lassen, Einstellungen unverändert (ESP32C3 Dev Module, Core 3.3.12, USB CDC On Boot: Enabled, No OTA 2MB APP/2MB SPIFFS, Erase All Flash aus).
3. WLAN `RavestickBoard` wie bisher. Zwei Geräte bereitlegen: Laptop und iPhone (ideal zusätzlich das iPhone SE für Abschnitt C/F).
4. Testmaterial: eine **große Animation** (70–79 Bilder), eine kleine, ein gespeicherter **Blocktext aus 0.6.1.5**, die Textdateien aus `assets/animationen/` auf dem Laptop.
5. Nach Abschnitt B und am Ende Diagnose, `ram.txt` und `http.txt` exportieren; Seriallog mitlaufen lassen, wenn möglich.

## A. Start und Altes

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| A1 | Sketch kompilieren | kompiliert (die vier alten `-Wvolatile`-Warnungen sind harmlos). Zeile „Globale Variablen verwenden … Bytes“ **notieren**: etwa 3 KB mehr als bei 0.6.1.5 sind erwartet (40 statt 25 Blocktext-Seiten) | | |
| A2 | Oberfläche öffnen | Kopfzeile bzw. Seitenleiste zeigt „v0.6.1.6-dev“ | | |
| A3 | Lauftext senden, Ambiente, Kurzwahl, Helligkeit und Tempo bewegen, ein Programm abspielen | alles wie bei 0.6.1.5 | | |
| A4 | Den gespeicherten **Blocktext aus 0.6.1.5** in der Bibliothek öffnen und senden | öffnet ohne „beschädigt“, alle Seiten da, Tafel zeigt sie | | |
| A5 | Diesen Blocktext unverändert speichern (aktualisieren), danach erneut öffnen | gespeichert, öffnet wieder normal | | |

## B. Übertragung mit zwei Geräten (Hauptfrage)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Beide Geräte auf der Bibliothek. Am Laptop die **große Animation** senden und auf das iPhone schauen | spätestens nach etwa 3 s liegt auf dem iPhone unten „● Übertragung läuft …“ auf dem Bedienfeld (der Punkt pulsiert); das Bedienfeld wird dabei **nicht größer**; Knöpfe und Regler werden blass | | |
| B2 | Am Laptop selbst nachsehen | auch dort liegt „Übertragung läuft …“ auf dem Bedienfeld, Knöpfe blass | | |
| B3 | Am iPhone während der Übertragung auf „Senden“, eine Kurzwahl-Kachel, den Mülleimer und den Helligkeitsregler tippen | es passiert nichts (keine Fehlermeldung nötig) | | |
| B4 | Am iPhone während der Übertragung Seiten wechseln (Kurzwahl, Programme, Bibliothek) | Wechsel klappt; Listen, die schon einmal offen waren, sind sichtbar | | |
| B5 | Am iPhone während der Übertragung eine Seite öffnen, die noch nie offen war (z. B. Animationen nach frischem Laden), und eine Animation antippen | Liste erscheint erst nach der Übertragung bzw. bleibt bis dahin leer; Vorschau lädt erst danach – das ist so gewollt | | |
| B6 | Am iPhone während der Übertragung die Seite **neu laden** | kleine Seite „RavestickBoard – Übertragung läuft … Die Seite lädt von selbst …“; nach dem Ende kommt von allein die Oberfläche (kein weißer Bildschirm) | | |
| B7 | Übertragung zu Ende warten | auf beiden Geräten verschwindet der Hinweis innerhalb von etwa 3 s, alles ist wieder bedienbar; **nichts** von dem, was du in B3 getippt hast, wird nachträglich ausgeführt | | |
| B8 | Dauer der Übertragung der großen Animation stoppen | Dauer **notieren** (0.6.1.5: 79 Bilder 52 s; erwartet sind ein bis zwei Sekunden mehr) | | |
| B9 | Diagnose öffnen: Zeile „Webantworten in Übertragungen“ | steht auf „an“; Zahlen für Aufrufe, Status, Warteseite, 409 und „längster Aufruf … ms“ **notieren** | | |
| B10 | Diagnose: Zeile „Stapel vor der ersten Webantwort … \| danach …“ | **beide Werte notieren** (wichtigster Wert des Tests). Über 1.000 Byte bei „danach“ ist gut; darunter knapp | | |
| B11 | B1 bis B7 noch zweimal wiederholen, einmal mit dem iPhone als sendendem Gerät | jedes Mal gleiches Verhalten, **kein Neustart** | | |
| B12 | Helligkeitsregler am Laptop schnell hin und her bewegen (ohne Animation) | kein Aufblitzen von „Übertragung läuft …“ bei jedem kleinen Befehl (höchstens kurz, wenn ein Befehl länger dauert) | | |
| B13 | Ein Programm mit mehreren Einträgen abspielen und zusehen | während jeder Übertragung gesperrt, zwischen den Einträgen wieder frei; Programm läuft durch | | |
| B14 | Nur falls in B1–B13 etwas kracht (Neustart, Hänger): `RB_WEB_DURING_BLE` im Sketch auf 0 setzen, neu flashen, B1 wiederholen | Verhalten wie 0.6.1.5 (kein Hinweis, weißer Bildschirm auf dem zweiten Gerät); bitte vermerken, dass umgestellt wurde | | |

## C. Rahmen und kleine Displays

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | iPhone 13 Pro: Kurzwahl, Bibliothek, Programme, Animationen, Ambiente nacheinander öffnen | die Seite selbst scrollt nicht; das Bedienfeld sitzt **unten bündig** (oben rund, unten keine Linie, kein Abstand) und ist **genauso breit** wie die Flächen darüber | | |
| C2 | In Bibliothek, Programmen und Animationen in der Liste scrollen | nur die Liste scrollt, Kopf und Bedienfeld bleiben stehen | | |
| C3 | Texteditor (Lauftext und Blocktext) und „Programm bearbeiten“ | scrollen wie bisher; Bedienfeld am Ende der Seite | | |
| C4 | **iPhone SE:** dieselben Seiten wie C1 | wie C1; Kurzwahl-Kacheln teilen sich die Höhe | | |
| C5 | iPhone SE: Ambiente | alle sieben Farben sichtbar, **Weiß** unten ganz zu sehen; bei Platzmangel scrollen nur die Farben | | |
| C6 | iPhone SE: Tasten im Bedienfeld | kleiner (30 Pixel), alle in **einer** Reihe | | |
| C7 | Laptop (Vollbild) und ein schmales Fenster | wie C1; Bedienfeld so breit wie die Fläche, auch neben der Seitenleiste | | |
| C8 | Homescreen-Verknüpfung auf dem iPhone (falls genutzt) | Bedienfeld unten nicht vom Strich (Home-Indikator) verdeckt | | |

## D. Blocktext (40 Seiten)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Texteditor → Blocktext | Überschrift „Blocktext · Seite 1 von 40“; keine Hinweistexte mehr; Seitenknöpfe gleich groß; Scrollbalken der Seitenleiste schmal | | |
| D2 | Seiten hinzufügen bis 40, dann noch eine | 40 gehen; bei der 41. Meldung „Höchstens 40 Seiten möglich.“ | | |
| D3 | Den 40-Seiten-Blocktext speichern und an die Tafel senden | gespeichert; Tafel zeigt alle 40 Seiten nacheinander | | |
| D4 | Danach Diagnose: „Minimal freier Heap“ | Wert **notieren** (Vergleich zu 0.6.1.5) | | |
| D5 | Eine Seite mit „Mini einzeilig“ links, mittig und rechts ausrichten und senden | Vorschau und Tafel zeigen jeweils links/mittig/rechts | | |
| D6 | Überall auf „Blocktext“ achten (Bibliothek, Programme, Meldungen) | kein „Blockanzeige“ oder „Blockfolge“ mehr | | |

## E. Namen, Meldungen, Kleinigkeiten

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Einen Eintrag mit sehr langem Namen in der Liste ansehen | Name blendet am Ende weich aus (kein „…“) | | |
| E2 | Diesen Eintrag antippen | Name läuft **einmal** als Lauftext durch und bleibt dann stehen | | |
| E3 | Laptop: mit der Maus über den Namen fahren | voller Name als Tooltip | | |
| E4 | Animation importieren aus `party_time-loop.gif` (oder einer Datei mit `_`/`-` im Namen) und aus einer Datei wie `IMG_2041.gif` | Name „Party time loop“ bzw. „Animation TT.MM.“ (heutiges Datum) | | |
| E5 | Tafel kurz ausschalten und einen Lauftext senden; außerdem im ganzen Test auf Meldungen achten | Meldungen schreiben ä, ö, ü und ß (z. B. „Übertragung fehlgeschlagen“, „Datenlänge zu groß“), nirgends „ae“, „oe“, „ue“ | | |
| E6 | Kurzwahl-Dialog: Quelle „Programme“ öffnen (falls ein beschädigtes Programm existiert) | beschädigtes Programm grau mit „(beschädigt)“, nicht wählbar; sonst überspringen | | |
| E7 | Mülleimer in Bibliothek, Programmen, Animationen | überall rot | | |
| E8 | Animation bearbeiten → „Als Kopie speichern“ | Dialog fragt nach dem Namen, Vorschlag „… (Kopie)“; Abbrechen speichert nichts | | |

## F. Vorschau

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | **iPhone SE** als zweites Gerät verbinden, Texteditor öffnen, Lauftext tippen | Vorschau zeigt den Text (nicht mehr „aus“); falls sie kurz dunkel ist, kommt sie innerhalb weniger Sekunden | | |
| F2 | iPhone SE: Blocktext-Vorschau | zeigt die Seite | | |
| F3 | Animationen: zwischen zwei großen Animationen hin und her tippen | alte Vorschau stoppt sofort, „Vorschau wird geladen …“ steht fett, dann läuft die neue | | |
| F4 | Animationen: keine oder zwei (Laptop, Strg-Klick) markieren | Vorschaufeld bleibt sichtbar, ist aber leer | | |
| F5 | Import öffnen | Knöpfe „GIF importieren“ und „Einzelbilder aus einem Bild“ mit einem Satz Erklärung | | |

## G. Beispiel-Animationen

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| G1 | Animationen → + → Text-Raster (aus Excel) → **Textdatei laden** → `herzschlag.txt`, Zeit je Frame 45 ms, Speichern und senden | Name „Herzschlag“; Tafel zeigt Herz und EKG wie in `vorschau.gif` | | |
| G2 | Ebenso die übrigen acht (Zeiten siehe `assets/animationen/LIESMICH.md`) | alle lassen sich laden und senden | | |
| G3 | `pfeile_rechts.txt` und `pfeile_links.txt` mit 40 ms | laufen flüssig in die jeweilige Richtung? (sonst Zeit notieren, die gut aussieht) | | |
| G4 | Welche gefallen auf der echten Tafel, welche nicht? | frei beschreiben | | |

## H. Gesamt

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | Am Ende Diagnose: „Kleinster freier Stapel (Loop-Task)“ | Wert **notieren** (0.6.1.5: 3.656 Byte) | | |
| H2 | RAM-Spur: niedrigster System-Min-Heap und Phase | **notieren** (0.6.1.5: 2.632 Byte beim Einbuchen des ersten Geräts) | | |
| H3 | Neustarts im ganzen Test | keiner; sonst Phase aus „Absturzspur Vorlauf“ notieren (neue Phasen: `tx_wait_notify`, `tx_after_ack`, `ble_after_connect`, `job_end`, `job_retry`) | | |
| H4 | Gesamteindruck, Wünsche | frei | | |
