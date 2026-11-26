# RavestickBoard · Hardwaretest v0.8.0-dev (Schwenk über große Bilder, Frame-Editor, Kleinpaket)

**Stand: 26.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.7.2 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.8.0.xlsx` (dort mit Auswahlliste und Zusammenfassung).

**Zum Stand:** 0.7.2 ist auf der Hardware getestet und läuft stabil (28 min, 19 Aufträge, 1665 BLE-Schreibvorgänge, keine Fehler, kein Neustart); es dient als Rückfallversion. 0.8.0 ändert an der Firmware nur die Versionsnummer, bringt aber eine größere Weboberfläche (gepackt rund 11 KB mehr) mit zwei neuen Funktionen: dem **Schwenk über ein großes Bild** und dem **Frame-Editor**.

**Am Rechner geprüft, nicht auf der Hardware:** alle Tests mit Endung `0800`. **Nicht geprüft:** Arduino-Compile, Hardware, Safari (iPhone und iPad), echter Apple Pencil, Zwei-Finger-Gesten auf echten Geräten.

**Wichtig zum Editor:** Er funktioniert **auf dem Handy nur im Querformat** und überall nur, wenn ein Tafelpixel mindestens sechs Bildschirmpixel groß wird. Sonst erscheint ein Hinweis, und nur der Editor ist gesperrt. Das ist so gewollt und gehört zu den Prüfpunkten.

## Vorbereitung

1. Mit 0.7.2 ein JSON-Backup ziehen, 0.7.2 als Rückfallversion aufbewahren.
2. Arduino IDE wie bisher (Arduino-ESP32 3.3.12, NimBLE-Arduino 2.5.2, ESP32C3 Dev Module, USB CDC On Boot Enabled, Partition „No OTA (2MB APP/2MB SPIFFS)“). `firmware/RavestickBoard_v0_8_0/RavestickBoard_v0_8_0.ino` öffnen, **alle acht Dateien** im Sketch-Ordner lassen.
3. Geräte bereithalten: iPhone (die App vom Homebildschirm, später auch im Safari-Tab), iPad mit Apple Pencil, Laptop.
4. Testbilder: ein breites Bild (Panorama oder Foto, etwa 400 × 64 Pixel oder größer), ein hohes Bild (etwa 64 × 200 Pixel) und ein sehr großes Foto direkt aus der Kamera (mehrere Megapixel).

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| A1 | Sketch kompilieren (Arduino-ESP32 3.3.12, Einstellungen wie bisher). Die beiden Zahlen am Ende (Programmspeicher, globale Variablen) in „Messwerte“ eintragen. | Kompiliert ohne Fehler. Zum Vergleich 0.7.2: Programmspeicher 1.600.665 Byte (76 %), globale Variablen 79.488 Byte. Erwartet: Programmspeicher rund 11 KB mehr (größere Oberfläche), globale Variablen unverändert. |
| A2 | Flashen, mit dem WLAN RavestickBoard verbinden, Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.8.0-dev. |
| A3 | Diagnose-Datei öffnen, Kopf ansehen. | „WLAN-Puffer“ und „WLAN-Sicherheit“ stehen wie eingestellt; Version 0.8.0-dev. |

## B. Schwenk über ein großes Bild (zuerst Laptop, dann iPhone)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| B1 | Animationen → + (Import). | Die Quellen GIF, Einzelbilder, **Schwenk über großes Bild**, Text-Raster und **Neu zeichnen** stehen nebeneinander. |
| B2 | Schwenk → das breite Bild wählen. | Das Quellbild erscheint mit Fenster: gelb am Anfang, weiß gestrichelt am Ende, blass dazwischen. Vorgeschlagen sind viele Frames (bis 79) von links nach rechts; die Bildgröße steht unter dem Bild. Ausschnitt-Rahmen und „Voreinstellung“ fehlen bei dieser Quelle. |
| B3 | „Anzahl Frames“ auf 5 stellen. | Das Ende bleibt, der **Versatz je Frame wird größer und steht im Feld**; die Vorschau zeigt fünf Fenster. |
| B4 | „Versatz X je Frame“ ändern. | Das Ende wandert mit; Frames bleiben fünf. |
| B5 | Ende weit hinter den Bildrand setzen („Stoppen am Rand“). | Das Ende wird auf den Bildrand begrenzt; der Versatz wird neu gerechnet. |
| B6 | Rand auf „Umlauf (nahtlos)“, Knopf „Versatz für eine nahtlose Schleife setzen“ drücken, senden. | Das Bild läuft auf der Tafel ohne sichtbaren Sprung von Ende zu Anfang durch; am Rand erscheint dasselbe Bild wieder auf der Gegenseite. |
| B7 | Das hohe Bild wählen. | Der Schwenk läuft von oben nach unten; Start Y und Ende Y sind belegt. |
| B8 | „Bildgröße“ wechseln (Original, Höhe 16, 32, 64) mit dem breiten Bild. | Die Vorschau passt zur Wahl; bei „Original“ entspricht ein Bildpixel einem Tafelpixel. Das Fenster zeigt auf der Tafel dasselbe wie in der Vorschau. |
| B9 | Farbumsetzung wechseln (Schwelle, Floyd-Steinberg, Geordnet), Zeit je Bild 100 ms, Von/Bis/Schritt ändern, speichern und senden. | Die Vorschau folgt den Einstellungen; die Animation steht in der Liste und läuft auf der Tafel. |
| B10 | Das sehr große Kamerafoto als Schwenkquelle laden (auf dem iPhone). | Die Oberfläche bleibt bedienbar, es gibt keine Fehlermeldung oder Neuladung der Seite. Wenn es zu groß ist: bitte die Meldung und das Gerät notieren. |

## C. Frame-Editor auf dem iPhone

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| C1 | iPhone **hochkant**: Import → „Neu zeichnen“. | Der Editor öffnet nicht zum Zeichnen, sondern zeigt „Bitte das Handy ins Querformat drehen …“; „Zurück“ (Pfeil oben links) führt zur Quellenwahl. Alles andere in der App bleibt benutzbar. |
| C2 | Handy drehen (Querformat), ohne die Seite neu zu laden. | Der Editor erscheint von selbst: Bildleiste und Knöpfe oben, Zeichenfeld in der Mitte, Werkzeuge und Farben unten. Nichts liegt unter der Kerbe oder dem Home-Balken, nichts ist abgeschnitten. |
| C3 | Mit dem Finger eine Linie in Rot ziehen und einzelne Punkte setzen. | Die Pixel erscheinen genau dort, wo der Finger ist (nicht versetzt); die Linie ist lückenlos. |
| C4 | Alle sieben Farben ansehen und benutzen; Radierer; Pipette auf ein farbiges Pixel. | Reihenfolge Rot, Gelb, Grün, Cyan, Blau, Magenta, Weiß; kein schwarzer Farbpunkt, stattdessen der Radierer. Die Pipette übernimmt die Farbe und wechselt zum Stift. |
| C5 | Füllen in eine umrandete und in eine leere Fläche; mehrfach Rückgängig und Wiederherstellen. | Die Fläche füllt sich; Rückgängig und Wiederherstellen gehen Schritt für Schritt. |
| C6 | Auswahl: ein Rechteck aufziehen, dann hineinfassen und verschieben; Mehr → Spiegeln. | Der Ausschnitt wandert mit dem Finger; Schwarz in der Auswahl überdeckt nichts. Spiegeln wirkt auf die Auswahl (ohne Auswahl auf das ganze Bild). Ein Rückgängig macht das ganze Verschieben rückgängig. |
| C7 | Bildleiste: + (neues Bild als Kopie des aktuellen), Bild nach links/rechts schieben, Löschen, bis zwei Bilder übrig sind. | Das neue Bild ist eine Kopie; die Reihenfolge ändert sich in der Leiste; „Bild n/m“ stimmt; bei zwei Bildern ist Löschen gesperrt. |
| C8 | Mehr → Zwiebelschicht an und aus. | Das vorige Bild scheint blass durch; aus: weg. |
| C9 | **Zwei-Finger-Zoom im Zeichenfeld**, danach mit „Ansicht verschieben“ oder zwei Fingern wandern; Zoom-Knöpfe. | Nur das Zeichenfeld zoomt (Prozentanzeige ändert sich). **Die ganze Seite zoomt nicht und scrollt nicht**, auch nicht, wenn ein Finger neben dem Feld liegt. Nach dem Schließen des Editors hat die App ihre normale Größe. |
| C10 | Eine kleine Zeichnung aus zwei Bildern, Fertig (Haken), Name vergeben, Zeit je Bild wählen, speichern und senden. | Die Tafel zeigt die gezeichneten zwei Bilder abwechselnd; die Animation steht in der Liste. |
| C11 | Zeichnen, dann Zurück (Pfeil). | Rückfrage „Änderungen verwerfen?“; Verwerfen schließt den Editor ohne Speichern. |
| C12 | Eine gespeicherte Animation wählen → Bearbeiten → „Bilder bearbeiten“, ein Pixel ändern, Fertig, Speichern. | Der Editor zeigt die gespeicherten Bilder; nach dem Speichern liegt die Änderung unter **derselben Nummer** (eine Kurzwahl darauf bleibt gültig) und läuft auf der Tafel. |
| C13 | Dasselbe im **Safari-Tab** (nicht als Homebildschirm-App), Querformat. | Entweder benutzbar oder der Hinweis „Bildschirm ist zu klein“; bitte notieren, was erscheint (die Leiste von Safari nimmt Höhe weg). |

## D. Frame-Editor auf iPad und Laptop

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| D1 | iPad mit Apple Pencil: zeichnen, dabei die Hand aufs Display legen. | Der Pencil zeichnet; die aufgelegte Hand malt nichts. |
| D2 | iPad hochkant und quer. | Der Editor ist in beiden Richtungen offen; das Zeichenfeld nutzt die Breite; Zoom bis große Pixel. |
| D3 | iPad: Zwei-Finger-Zoom und Verschieben im Zeichenfeld. | Wie C9: nur das Feld zoomt, nicht die Seite. |
| D4 | Laptop: mit der Maus zeichnen, Mausrad zoomt das Feld, Rückgängig/Wiederherstellen mit den Knöpfen. | Das Mausrad zoomt nur im Feld; die Seite dahinter scrollt nicht. |
| D5 | Laptop: das Browserfenster auf etwa Handygröße ziehen, dann sehr schmal. | Bei kleinem Fenster erscheint der Hinweis („zu klein“ oder „Querformat“); beim Vergrößern verschwindet er von selbst. |

## E. Kleinpaket (aus dem Test von 0.7.2)

| Nr. | Was du tust | Was du siehst (Erwartung) |
|---|---|---|
| E1 | Ein Programm starten und den Tempo-Regler unten ansehen. | Statt der Tempozahl steht „fest 80“; der Regler ist gesperrt; die Zeile springt nicht in der Höhe. Nach dem Beenden des Programms steht wieder die Zahl. |
| E2 | Laptop: nacheinander Bibliothek, Programme, Animationen, Ambiente, Einstellungen, Diagnose öffnen und auf den linken Rand und die Breite achten. | Alle Seiten sitzen gleich breit und gleich weit links; beim Wechsel springt nichts um wenige Pixel. |
| E3 | Einstellungen → Backup exportieren und importieren; die Knöpfe beobachten. | Die Knöpfe behalten ihre gewohnte Farbe; der Laufbalken läuft während der Arbeit durch; danach alles wie vorher. |

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
