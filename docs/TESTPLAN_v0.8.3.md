# RavestickBoard · Hardwaretest v0.8.3-dev (1:1, Bahn bewegen, Rückgängig im Import, Editor-Formen, Mischfarben)

**Stand: 27.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.8.2 (liegt in `archive/`). 0.8.3 enthält alles aus 0.8.2 und ändert **nur die Weboberfläche** (die Firmware nur in Versionsnummer und Kommentar-/Diagnosetexten). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.8.3.xlsx`.

**Zum Stand:** 0.7.2 ist auf der Hardware getestet (Rückfallversion). 0.8.2 war kompiliert (Programmspeicher 1.620.403 Byte = 77 %, globale Variablen 79.488 Byte) und wurde flüchtig getestet. 0.8.3 bringt den 1:1-Knopf, „Bahn bewegen“ im Schwenk, Rückgängig/Wiederherstellen in der Import-Maske, Duplizieren/Neu sowie Linie, Rechteck und Kreis im Editor und die sieben Mischfarben unter Ambiente (Abschnitt J).

**Am Rechner geprüft, nicht auf der Hardware:** alle Tests mit Endung `0803`. **Nicht geprüft:** Arduino-Compile, Hardware, Safari (iPhone und iPad), echter Apple Pencil, Zwei-Finger-Gesten auf echten Geräten.

**Wichtig zum Editor:** Er funktioniert **auf dem Handy nur im Querformat** und überall nur, wenn ein Tafelpixel mindestens sechs Bildschirmpixel groß wird. Sonst erscheint ein Hinweis, und nur der Editor ist gesperrt. Das ist so gewollt.

## Vorbereitung

1. Mit 0.7.2 ein JSON-Backup ziehen, 0.7.2 als Rückfallversion aufbewahren.
2. Arduino IDE wie bisher (Arduino-ESP32 3.3.12, NimBLE-Arduino 2.5.2, ESP32C3 Dev Module, USB CDC On Boot Enabled, Partition „No OTA (2MB APP/2MB SPIFFS)“). `firmware/RavestickBoard_v0_8_3/RavestickBoard_v0_8_3.ino` öffnen, **alle acht Dateien** im Sketch-Ordner lassen.
3. Geräte bereithalten: iPhone (die App vom Homebildschirm, später auch im Safari-Tab), iPad mit Apple Pencil, Laptop.
4. Testbilder: ein breites Bild (Panorama oder Foto, etwa 400 × 64 Pixel oder größer), ein hohes Bild (etwa 64 × 200 Pixel), ein Bild mit Kacheln nebeneinander (etwa 256 × 16) und ein sehr großes Foto direkt aus der Kamera (mehrere Megapixel).

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| A1 | Sketch kompilieren (Arduino-ESP32 3.3.12, Einstellungen wie bisher). Die beiden Zahlen am Ende (Programmspeicher, globale Variablen) in „Messwerte“ eintragen. | Kompiliert ohne Fehler. Zum Vergleich 0.8.2: Programmspeicher 1.620.403 Byte (77 %), globale Variablen 79.488 Byte; 0.7.2: Programmspeicher 1.600.665 Byte (76 %), globale Variablen 79.488 Byte. Erwartet: Programmspeicher rund 11 KB mehr (größere Oberfläche), globale Variablen unverändert. |
| A2 | Flashen, mit dem WLAN RavestickBoard verbinden, Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.8.3-dev. |
| A3 | Diagnose-Datei öffnen, Kopf ansehen. | „WLAN-Puffer“ und „WLAN-Sicherheit“ stehen wie eingestellt; Version 0.8.3-dev. |

## B. Schwenk / Einzelbilder (zuerst Laptop, dann iPhone)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| B1 | Animationen → + (Import). | Vier Kacheln: GIF, **Schwenk / Einzelbilder**, Text-Raster, Neu zeichnen. Am Laptop und iPad in einer Reihe, am iPhone 2 × 2. |
| B2 | Schwenk / Einzelbilder → das breite Bild wählen. | Das Bild liegt groß auf der Seite; darauf zwei Rahmen im Format 4 : 1: **Start gelb**, **Ende weiß gestrichelt**, dazwischen blasse Rahmen. Vorgabe „Ganzes Bild durchlaufen“; „Größe gleich“ ist angehakt; die Bildgröße steht unter dem Bild. |
| B3 | Den Start-Rahmen mit Finger oder Maus verschieben, dann den Ende-Rahmen. | Die Rahmen folgen dem Finger ohne Versatz; die Zahlenfelder (Start X/Y, Ende X/Y, Versatz) laufen mit; die Vorschau zeigt die Frames dazwischen. |
| B4 | Eine Ecke des Start-Rahmens ziehen; dann mit zwei Fingern (iPhone/iPad) beziehungsweise Mausrad (Laptop) die Größe ändern. | Der Rahmen bleibt im Format 4 : 1; bei angehaktem „Größe gleich“ ändert sich der Ende-Rahmen mit. |
| B5 | „Größe gleich“ abhaken, den Ende-Rahmen deutlich kleiner machen. | Es entsteht ein **Zoom**: „Größenänderung je Frame“ wird angezeigt, die Vorschau zoomt von groß auf klein; die Frames dazwischen haben stetig wechselnde Größe. Der Knopf für die nahtlose Schleife ist gesperrt und nennt den Grund. |
| B6 | Anker-Raster (3 × 3) für Start und Ende antippen; danach die Vorlagen durchgehen: Links → Rechts, Rechts → Links, Oben → Unten, Unten → Oben, Ganzes Bild durchlaufen, Rahmen 1:1, Höhe einpassen. | Die Rahmen springen an die gewählte Stelle beziehungsweise Richtung; die Zahlenfelder passen. |
| B7 | Rahmen über den Bildrand ziehen (zum Beispiel halb hinaus). | Außerhalb des Bildes ist die Vorschau (und später die Tafel) **schwarz**, nichts bricht ab. |
| B8 | „Anzahl Frames“ auf 5 stellen; „Versatz“ ändern. | Das Ende wandert beziehungsweise der Versatz passt sich an; die Vorschau zeigt die geänderte Zahl Frames. |
| B9 | Rand auf „Umlauf (nahtlos)“, gleich große Rahmen, Knopf „Versatz für eine nahtlose Schleife setzen“, senden. | Das Bild läuft auf der Tafel ohne sichtbaren Sprung von Ende zu Anfang; am Rand erscheint dasselbe Bild wieder auf der Gegenseite. |
| B10 | Das hohe Bild wählen. | Der Schwenk läuft von oben nach unten (oder die Vorlage setzt es so); Start Y und Ende Y sind belegt. |
| B11 | Das Kachelbild wählen, Haken **„Ohne Überlappung (Kachel für Kachel)“** setzen. | Der Versatz ist genau die Rahmenbreite, die Frames sind ganze Kacheln, Schnittlinien liegen auf dem Bild, die Rahmen bleiben gleich groß. Auf der Tafel erscheinen die Kacheln nacheinander. |
| B12 | Farbumsetzung wechseln (Schwelle, Floyd-Steinberg, Geordnet), Zeit je Bild 100 ms, Von/Bis/Schritt ändern, speichern und senden. | Die Vorschau folgt den Einstellungen; die Animation steht in der Liste und läuft auf der Tafel. |
| B13 | Ein sehr großes Kamerafoto als Quelle laden (auf dem iPhone). | Die Oberfläche bleibt bedienbar, keine Fehlermeldung, kein Neuladen der Seite. Ist das Bild länger als 4096 Pixel, erscheint ein Hinweis auf die Verkleinerung. |
| B14 | Import → GIF; ein GIF laden; Import → Neu zeichnen. | Beide Wege wie bisher erreichbar; der frühere Weg „Einzelbilder aus einem Bild“ gibt es nicht mehr (die Funktion steckt im Haken von B11). |

## C. Frame-Editor auf dem iPhone

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| C1 | iPhone **hochkant**: Import → „Neu zeichnen“. | Der Editor öffnet nicht zum Zeichnen, sondern zeigt „Bitte das Handy ins Querformat drehen …“; „Zurück“ (Pfeil oben links) führt zur Quellenwahl. Alles andere in der App bleibt benutzbar. |
| C2 | Handy drehen (Querformat), ohne die Seite neu zu laden. | Der Editor erscheint von selbst: Bildleiste und Knöpfe oben, Zeichenfeld in der Mitte, Werkzeuge und Farben unten. Nichts liegt unter der Kerbe oder dem Home-Balken, nichts ist abgeschnitten. |
| C3 | Mit dem Finger eine Linie in Rot ziehen und einzelne Punkte setzen. | Die Pixel erscheinen genau dort, wo der Finger ist (nicht versetzt); die Linie ist lückenlos. |
| C4 | Alle sieben Farben ansehen und benutzen; Radierer; Pipette auf ein farbiges Pixel. | Reihenfolge Rot, Gelb, Grün, Cyan, Blau, Magenta, Weiß; kein schwarzer Farbpunkt, stattdessen der Radierer. Die Pipette übernimmt die Farbe und wechselt zum Stift. |
| C5 | Füllen in eine umrandete und in eine leere Fläche; mehrfach Rückgängig und Wiederherstellen. | Die Fläche füllt sich; Rückgängig und Wiederherstellen gehen Schritt für Schritt. |
| C6 | Auswahl: ein Rechteck aufziehen, dann hineinfassen und verschieben; Mehr → Spiegeln. | Der Ausschnitt wandert mit dem Finger; Schwarz in der Auswahl überdeckt nichts. Spiegeln wirkt auf die Auswahl (ohne Auswahl auf das ganze Bild). Ein Rückgängig macht das ganze Verschieben rückgängig. |
| C7 | Bildleiste: + (neues Bild als Kopie des aktuellen); die Pfeile links/rechts; dann den Schalter **Verschieben** einschalten und die Pfeile erneut benutzen; Löschen, bis zwei Bilder übrig sind. | Ohne „Verschieben“ wählen die Pfeile das vorige/nächste Frame (die Leiste läuft mit; Wischen, Mausrad und Antippen scrollen/wählen ebenfalls). Mit „Verschieben“ sind die Pfeile gelb und schieben das Frame in der Reihenfolge. Das neue Frame ist eine Kopie; „Bild n/m“ stimmt; bei zwei Bildern ist Löschen gesperrt. |
| C8 | Mehr → Zwiebelschicht an und aus. | Das vorige Bild scheint blass durch; aus: weg. |
| C9 | **Zwei-Finger-Zoom im Zeichenfeld**, danach mit „Ansicht verschieben“ oder zwei Fingern wandern; Zoom-Knöpfe. | Nur das Zeichenfeld zoomt (Prozentanzeige ändert sich). **Die ganze Seite zoomt nicht und scrollt nicht**, auch nicht, wenn ein Finger neben dem Feld liegt. Nach dem Schließen des Editors hat die App ihre normale Größe. |
| C10 | Eine kleine Zeichnung aus zwei Bildern, Fertig (Haken), Name vergeben, Zeit je Bild wählen, speichern und senden. | Die Tafel zeigt die gezeichneten zwei Bilder abwechselnd; die Animation steht in der Liste. |
| C11 | Zeichnen, dann Zurück (Pfeil). | Rückfrage „Änderungen an dieser Animation sind nicht gespeichert. Verwerfen?“; Verwerfen schließt den Editor ohne Speichern, Abbrechen bleibt im Editor. |
| C12 | Eine gespeicherte Animation wählen → Bearbeiten → „Bilder bearbeiten“, ein Pixel ändern, Fertig, Speichern. | Der Editor zeigt die gespeicherten Bilder; nach dem Speichern liegt die Änderung unter **derselben Nummer** (eine Kurzwahl darauf bleibt gültig) und läuft auf der Tafel. |
| C13 | Dasselbe im **Safari-Tab** (nicht als Homebildschirm-App), Querformat. | Entweder benutzbar oder der Hinweis „Bildschirm ist zu klein“; bitte notieren, was erscheint (die Leiste von Safari nimmt Höhe weg). |
| C14 | iPhone quer (schmales Modell, unter 760 Pixeln Breite), Editor öffnen; Mehr antippen. | Kompaktleiste: kleinere Farbflächen; **Ansicht verschieben und Zoom (+/−) liegen unter „Mehr“** und funktionieren dort; nichts ist abgeschnitten. |

## D. Frame-Editor auf iPad und Laptop

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| D1 | iPad mit Apple Pencil: zeichnen, dabei die Hand aufs Display legen. | Der Pencil zeichnet; die aufgelegte Hand malt nichts. |
| D2 | iPad hochkant und quer. | Der Editor ist in beiden Richtungen offen; das Zeichenfeld nutzt die Breite; Zoom bis große Pixel. |
| D3 | iPad: Zwei-Finger-Zoom und Verschieben im Zeichenfeld. | Wie C9: nur das Feld zoomt, nicht die Seite. |
| D4 | Laptop: mit der Maus zeichnen, Mausrad zoomt das Feld, Rückgängig/Wiederherstellen mit den Knöpfen. | Das Mausrad zoomt nur im Feld; die Seite dahinter scrollt nicht. |
| D5 | Laptop: das Browserfenster auf etwa Handygröße ziehen, dann sehr schmal. | Bei kleinem Fenster erscheint der Hinweis („zu klein“ oder „Querformat“); beim Vergrößern verschwindet er von selbst. |

| D6 | Laptop oder iPad quer: Editor öffnen und die Leiste ansehen. | **Große, beschriftete Flächen** (Stift, Radierer, Füllen …), größere Farbflächen, untere Leiste umbricht; alles gut treffbar. |

## E. Kleinpaket (aus dem Test von 0.7.2)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| E1 | Ein Programm starten und den Tempo-Regler unten ansehen. | Statt der Tempozahl steht „fest 80“; der Regler ist gesperrt; die Zeile springt nicht in der Höhe. Nach dem Beenden des Programms steht wieder die Zahl. |
| E2 | Laptop: nacheinander Bibliothek, Programme, Animationen, Ambiente, Einstellungen, Diagnose öffnen und auf den linken Rand und die Breite achten. | Alle Seiten sitzen gleich breit und gleich weit links; beim Wechsel springt nichts um wenige Pixel. |
| E3 | Einstellungen → Backup exportieren und importieren; die Knöpfe beobachten. | Die Knöpfe behalten ihre gewohnte Farbe; der Laufbalken läuft während der Arbeit durch; danach alles wie vorher. |

## G. Rückfrage beim Verwerfen

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| G1 | Import → Schwenk, Bild laden, dann den Zurück-Pfeil. | Rückfrage „Änderungen an dieser Animation sind nicht gespeichert. Verwerfen?“. Abbrechen bleibt; Verwerfen führt zur Liste und gibt die Bilder frei. |
| G2 | Import öffnen, nichts laden, Zurück. | Keine Rückfrage. |
| G3 | Bild laden, dann über das Menü (zum Beispiel Bibliothek) weg. | Dieselbe Rückfrage; Abbrechen bleibt in der Import-Maske. |
| G4 | Etwas laden, „Nur senden“, dann Zurück. | Die Rückfrage erscheint noch (Senden zählt nicht als Speichern). |
| G5 | Etwas laden, speichern, dann Zurück. | Keine Rückfrage. |

## H. Fälle aus dem Code-Review (T01 bis T12)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| T01 | Editor: Auswahl teilweise über den Bildrand schieben, danach Leeren und Spiegeln (Mehr). | Es geht nichts kaputt und nichts bleibt außerhalb hängen; Rückgängig stellt zurück. |
| T02 | Eine Animation importieren, die Zeit je Bild ändern und **sofort** speichern. | Die gespeicherte Animation hat die gerade getippte Zeit. |
| T03 | Editor öffnen und ohne Änderung über den Haken verlassen; dann speichern. | Keine Rückfrage zu Änderungen im Editor; die Animation bleibt unverändert. |
| T04 | Etwas zeichnen, Rückgängig, einen unveränderten Pixel antippen, dann Wiederherstellen. | Wiederherstellen geht noch (ein Strich ohne Wirkung löscht die Wiederholung nicht). |
| T05 | Zeichnen, Rückgängig, Zwei-Finger-Zoom, dann Wiederherstellen. | Wiederherstellen geht noch; Zoomen ändert nichts am Bild. |
| T06 | Schwenk: Endposition außerhalb der Bildgröße in die Zahlenfelder eingeben. | Der Wert wird auf den zulässigen Bereich zurückgesetzt und im Feld angezeigt; der Rahmen darf über den Rand, die Mitte bleibt im Bild. |
| T07 | Schwenk: ein sehr großes und ein extrem breites Bild importieren. | Kein Absturz, kein Hänger; bei sehr großen Bildern der Hinweis auf Verkleinerung. |
| T08 | Laptop: Fenster auf 667, 740, 844 und 932 Pixel Breite ziehen (Höhe etwa 375 bis 400); Editor offen. | Bei 667 und 740 Kompaktleiste mit „Mehr“, ab 760 normale Leiste; nirgends flackert der Hinweis „zu klein“ hin und her. |
| T09 | Während der Import eines Bildes läuft (großes Bild), einen anderen Import starten. | Es erscheint nur die zuletzt gewählte Datei; keine Vermischung. |
| T10 | **Später (Firmware-Runde):** zwei Geräte gleichzeitig „Nur senden“. | Nicht in 0.8.3 behoben; nur beobachten und notieren. |
| T11 | **Später (Firmware-Runde):** dieselbe Animation auf zwei Geräten bearbeiten. | Nicht in 0.8.3 behoben; nur beobachten und notieren. |
| T12 | Mehrmals nacheinander große Bilder importieren und den Editor/Import wieder schließen. | Die Seite bleibt flüssig; der Heap-Wert in der Diagnose ändert sich nicht auffällig. |

## I. Neu in 0.8.2: Pixelgrafik, Zahlenfelder, Quellwechsel

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| I1 | Schwenk / Einzelbilder → ein Pixelbild nur aus den sieben Farben laden (zum Beispiel dein Saturn oder die zwei anderen). | **Bildart: Pixelgrafik** und Farbumsetzung **Mehrheitsfarbe** sind von selbst gewählt; der Rahmen steht auf 1:1 (64 × Vergrößerungsfaktor Bildpixel breit, bei Saturn etwa 128); Helligkeit der Schwelle und Kontrast sind ausgegraut. |
| I2 | Die Vorschau ansehen und auf der Tafel senden. | Scharfe Farbflächen ohne Rasterpunkte und ohne Fremdfarben; Pixel entsprechen dem Original. |
| I3 | Rahmen vergrößern oder verkleinern (Ecke ziehen, Mausrad). | Das Anpassen geht weiter; die Mehrheitsfarbe passt sich an. |
| I4 | Bildart auf „Foto oder Verlauf“ stellen und zurück auf „Pixelgrafik“. | Foto: Floyd-Steinberg, Regler aktiv. Zurück auf Pixelgrafik: Rahmen springt wieder auf 1:1. |
| I5 | Ein Foto laden. | Bildart Foto, Floyd-Steinberg (nicht Pixelgrafik). |
| I6 | Ein GIF mit wenigen Farben laden (GIF importieren). | Wie I1: Pixelgrafik erkannt, Rahmen 1:1. Ein GIF mit vielen Farben: Foto. |
| I7 | Bei Foto: neben „Helligkeit der Schwelle“ und „Kontrast“ eine Zahl eintippen; dann den Regler bewegen. | Zahlenfeld und Regler folgen einander; zu große Zahlen werden auf den Bereich begrenzt. |
| I8 | Schwenk: „Anker und Vorlagen“ ansehen, antippen. | Eingeklappt in der Designsprache der App (Titel mit Pfeil); ein Tipp klappt auf, Vorlagen und Anker funktionieren wie vorher. |
| I9 | Schwenk-Maske auf iPhone und Laptop ansehen. | Gleichmäßige Abstände zwischen Abschnitten, Feldern und Zahlenfeldern; nichts abgeschnitten (auch „Rand“). |
| I10 | Von/Bis/Schritt mit Kommazahl (1,5) füllen. | Kein Fehler; es wird mit ganzen Zahlen gerechnet. |
| I11 | Bild laden, ändern, dann ein anderes Bild/GIF wählen. | Rückfrage „Die ungespeicherte Animation verwerfen und eine neue beginnen?“; Abbrechen erhält den Entwurf, OK beginnt neu. |
| I12 | Mausrad am Schwenk-Rahmen drehen und **sofort** speichern. | Gespeichert ist der sichtbare Rahmenstand. |
| I13 | Während des Speicherns (großes Schwenk-Bild) Zurück oder einen anderen Quellknopf antippen. | Gesperrt; Hinweis „Die Animation wird gerade gespeichert …“. |
| I14 | Editor mit Änderung offen, Seite neu laden oder Tab schließen. | Der Browser warnt vor dem Verlassen. |
| I15 | Ein beschädigtes oder abgeschnittenes GIF laden. | Fehlermeldung „GIF-Datei unvollständig/beschädigt“, kein schwarzes Bild. |

## J. Neu in 0.8.3

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| J1 | Schwenk mit einem Foto: Knopf **1:1** antippen; die Zeile mit der Rahmengröße ansehen. | Der Rahmen springt auf Pixelgröße (bei Pixelgrafik mit Vergrößerungsfaktor); die Rahmengröße steht immer sichtbar daneben, auch ohne Antippen. |
| J2 | GIF-Import: 1:1 antippen. | Der Ausschnitt springt auf Pixelgröße. |
| J3 | Schwenk: Umschalter **Bahn bewegen**; den Griff in der Mitte der Bahn ziehen; zurück auf **Rahmen bewegen**. | Die Bahn biegt sich, die Vorschau folgt der Kurve; „Bahn begradigen“ macht sie wieder gerade; im Kachelmodus ist das Biegen gesperrt. |
| J4 | Import-Maske: mehrere Änderungen machen (Rahmen, Regler, Zuschnitt), dann **Rückgängig** und **Wiederherstellen** (Knöpfe, am Laptop auch Strg+Z / Strg+Y). | Jeder Schritt wird einzeln zurückgenommen; auch bei GIF-Zuschnitt und Schwenk. Nach einem neuen Bild beginnt der Verlauf neu. |
| J5 | Frame-Editor: **Duplizieren** und **Neu**. | Duplizieren kopiert das aktuelle Bild; Neu legt ein leeres Bild an. |
| J6 | Editor → Mehr: Linie, Rechteck, Kreis (je mit und ohne „Füllen“); mit dem Finger/Stift aufziehen, Rückgängig. | Die Form erscheint beim Ziehen und wird beim Loslassen gesetzt; Rückgängig nimmt die ganze Form zurück. |
| J7 | Ambiente: die sieben Mischfarben (Orange, Rot-Orange, Limette, Himmelblau, Hellblau, Hellrosa, Mint) antippen. | Die Tafel zeigt die Mischfarbe ohne sichtbares Flimmern; die Kacheln liegen sauber im Raster. Beim Wechsel zurück auf eine Grundfarbe wird sie normal dargestellt. |
| J8 | **Standbild nach Lauftext:** erst einen Lauftext senden, danach ein Bild, eine Blocktext-Seite oder eine Ambiente-Farbe. | Das Standbild steht still und läuft nicht mit. Falls doch: Reihenfolge und Art notieren. |
| J9 | **Messung (nur notieren):** so viele Animationen speichern, wie das Limit zulässt (bis 40), dabei Heap und freien Dateisystemplatz in der Diagnose festhalten. | Werte in „Messwerte“ eintragen; sie entscheiden, ob die 40er-Grenze angehoben wird. |

## F. Kurzer Gesamtlauf und Messung

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| F1 | Lauftext, Blocktext, Animation (aus dem Schwenk) und Ambiente-Farbe nacheinander senden. | Alles erscheint wie in 0.7.2. |
| F2 | Ein Programm starten und beenden; danach Kurzwahl antippen. | Programm läuft und endet; Kurzwahl wie gewohnt. |
| F3 | Möglichst viele Animationen speichern (Schwenk mit 79 Frames und Editor-Animationen), bis etwa 15 bis 20 in der Liste stehen; danach die Liste öffnen und zwischen Raster und Liste wechseln. | Die Liste lädt ohne Fehler; Vorschaubilder erscheinen nach und nach. Bitte den Heap-Wert nach dem Laden der Liste notieren (Messwerte). |
| F4 | Am Ende die Diagnose-Datei, die RAM-Datei und `http://192.168.4.1/api/http.txt` speichern; unter „Messwerte“ die beiden Heap-Werte eintragen. | Keine ungeplanten Neustarts, keine Fehler; der kleinste freie Heap liegt in der Größenordnung von 0.7.2 (22.028 Byte nach 28 min). |
| F5 | Noch offen aus 0.7.1, wenn Zeit bleibt: Kurzbefehl für Kurzwahl 1 und für eine Animation anlegen (ID unter `http://192.168.4.1/api/anim/list`); Kurzbefehl während einer Übertragung auslösen. | Die Kurzwahl startet, die Animation läuft; während der Übertragung kommt 409, kurz danach klappt es. |
| F6 | iPhone: Screenshots der richtigen Kurzbefehle-Konfiguration machen (Tafeltext, Kurzwahl, Animation) und mitschicken. | Die Bilder kommen in die Anleitung `docs/KURZBEFEHLE.md`. |

Ergebnisse, Messwerte und Bemerkungen gehören in die Excel-Datei; die Diagnose-Datei, die RAM-Datei und `http://192.168.4.1/api/http.txt` bitte wie bisher mitschicken. Bei Fehlern im Editor bitte Gerät, Ausrichtung (hoch/quer), App oder Safari-Tab und, wenn möglich, einen Bildschirmfoto-Hinweis dazuschreiben.
