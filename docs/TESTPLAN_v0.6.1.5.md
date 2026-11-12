# RavestickBoard · Hardwaretest v0.6.1.5-dev (Heap-Schutz, Modus nach Animation, Mehrfachauswahl, Sortieren, Laptop-Ansicht, WLAN-Name)

**Stand: 12.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.4 (liegt in `archive/`). 0.6.1.4 lief auf der Hardware (70 Schritte in Ordnung, 13 nicht getestet, 9 ohne Eintrag). **Hauptbefund:** Der Abruf in Teilen zu 3000 Byte löste den Heap-Engpass nicht; jeder Teil senkte den freien Heap kurzzeitig um 13 bis 23 KB, das System-Minimum fiel auf 400 Byte, und nach einem Animationsversand mit zwei Geräten startete der Wächter das Board in der Phase `anim_get` neu. 0.6.1.5 holt 1200 Byte je Anfrage in einer Antwort mit bekannter Länge, prüft freien Heap **und** größten Block, vertagt lesende Listen-Anfragen bei knappem Heap mit 503 (der Browser wiederholt) und liefert bei knappem Heap eine kleine Warteseite statt der Oberfläche. **Die Hauptfrage dieses Tests ist wieder der Heap (Abschnitt B).** Außerdem neu: Anzeigemodus nach einer Animation, Fehlermeldung bei Ablehnung durch die Tafel, Rückwärts abspielen, Sortieren der Animationen, Mehrfachauswahl zum Löschen (Laptop), Seitenleiste am Laptop, WLAN `RavestickBoard`.

## Vorbereitung

1. JSON-Backup der Bibliothek sichern (Einstellungen), bisherige Firmware (0.6.1.4) als Rückfallversion aufbewahren.
2. `firmware/RavestickBoard_v0_6_1_5/RavestickBoard_v0_6_1_5.ino` öffnen, **alle sieben Dateien** im Sketch-Ordner lassen, Einstellungen unverändert (ESP32C3 Dev Module, Core 3.3.12, USB CDC On Boot: Enabled, No OTA 2MB APP/2MB SPIFFS, Erase All Flash aus). „Meine Tafel“, Bibliothek, Programme, Kurzwahlen und Animationen bleiben erhalten.
3. **Neuer WLAN-Name:** Nach dem Flashen heißt das WLAN `RavestickBoard` (Passwort unverändert). Laptop und iPhone müssen sich einmal neu verbinden; das alte Netz `CoolLED1248` kann in den WLAN-Einstellungen vergessen werden. Ein Homescreen-Icon auf dem iPhone funktioniert weiter (gleiche Adresse 192.168.4.1).
4. Original-App der Tafel vom Handy trennen. Tafel einschalten, in Reichweite aufstellen. Testmaterial: mindestens eine **große Animation** (z. B. „Slots“ oder „Dance Pooh 2“, 40 bis 79 Bilder), eine kleine, drei Wegwerf-Einträge in der Bibliothek und zwei Wegwerf-Programme für die Mehrfachauswahl.
5. Für die Heap-Tests nach jedem Abschnitt Diagnose, RAM-Spur (`ram.txt`) und HTTP-Spur (`http.txt`) exportieren; das Seriallog mitlaufen lassen, wenn möglich.

## A. Start und Regression

| Nr. | Bereich | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|---|
| A1 | Build | Sketch kompiliert ohne Fehler (die vier alten `-Wvolatile`-Warnungen sind harmlos). Neu genutzt: `ESP.getMaxAllocHeap()`, `String::reserve`, `web.send` mit `String`. Zeile „Globale Variablen verwenden … Bytes“ notieren (0.6.1.4: 80.408 Byte, 24 %) | kompiliert; Werte notiert | | |
| A2 | WLAN | WLAN-Liste am Laptop und iPhone ansehen, mit `RavestickBoard` verbinden (bisheriges Passwort) | Netz heißt `RavestickBoard`, Passwort wie bisher, `http://192.168.4.1` öffnet die Oberfläche | | |
| A3 | Titel | Kopfzeile (Handy) bzw. Seitenleiste (Laptop) und Diagnose-Export ansehen | „RavestickBoard v0.6.1.5-dev“, Untertitel „CoolLEDX · ESP32-C3“; Diagnose beginnt mit „RavestickBoard \| Diagnose“ (ohne „for CoolLED1248“) | | |
| A4 | Regression | Lauftext senden, Blockseite senden, Helligkeit, Tempo, Programm abspielen, Ambiente, Kurzwahl | wie bei 0.6.1.4; kein Auftrag bricht ab | | |
| A5 | Animation | Eine kleine und eine große Animation aus der Liste senden | Tafel zeigt sie wie in der Vorschau; Dauer wie bisher (79 Bilder etwa 52 s) | | |

## B. Heap beim Abruf großer Animationen (Hauptfrage)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Ein Gerät: Animationen öffnen, die größte Animation antippen | unter der Vorschau „Vorschau wird geladen … n %“, danach läuft die Vorschau; Ladedauer in Sekunden **notieren** (es sind jetzt mehr, kleinere Anfragen mit kurzen Pausen) | | |
| B2 | Nacheinander fünf verschiedene große Animationen antippen | jedes Mal Vorschau, kein Wächter-Neustart | | |
| B3 | Danach Diagnose und HTTP-Spur exportieren | „Minimal freier Heap“ und „System-Min“ **notieren** (0.6.1.4: 1.900 / 1.800 Byte, vor dem Absturz 400 Byte); in der HTTP-Spur „Kleinster Heap in Anfrage“ bei `/api/anim/get` notieren (0.6.1.4: 8.148 Byte) | | |
| B4 | Eine große Animation bearbeiten (Stift), ohne zu speichern zurück | Bearbeitungsansicht lädt vollständig, Vorschau läuft | | |
| B5 | **Zwei Geräte:** Laptop sendet eine große Animation an die Tafel; währenddessen auf dem iPhone die Seite neu laden und Animationen öffnen | iPhone: entweder die Oberfläche oder kurz die Warteseite „Der Controller hat gerade wenig freien Speicher …“, die sich nach zwei Sekunden selbst neu lädt; **kein weißer Bildschirm** (D9 aus 0.6.1.4), kein Neustart | | |
| B6 | Direkt nach dem Versand aus B5 auf beiden Geräten eine große Animation antippen | Vorschau kommt, notfalls mit etwas Wartezeit; kein Wächter-Neustart (0.6.1.4: Neustart in `anim_get` genau in dieser Lage) | | |
| B7 | Diagnose: Zeile „HTTP-Anfragen wegen knappem Heap vertagt (503): …“ | Wert **notieren**; ein paar sind in B5/B6 normal, sehr viele (über 100) wären ein Befund | | |
| B8 | Wenn die Warteseite dauerhaft erscheint: auf „Trotzdem laden“ tippen | Oberfläche lädt (Notausgang `/?force=1`); Beobachtung notieren | | |
| B9 | Liste der Animationen, Bibliothek und Programme mit zwei Geräten wechselnd öffnen | alles lädt, ggf. mit kurzer Verzögerung; keine Fehlermeldung „Speicher knapp“ in der Oberfläche (die Wiederholung läuft unsichtbar) | | |

## C. Anzeigemodus nach einer Animation (H2, J14 aus 0.6.1.4)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | Animation senden, danach **Ambiente aus der Kurzwahl** | Ambiente steht als Standbild (0.6.1.4: lief mit Linkslauf) | | |
| C2 | Animation senden, danach einen **Block-Text** aus der Kurzwahl oder Bibliothek | Blockseite steht (0.6.1.4: Linkslauf, erst der zweite Klick half) | | |
| C3 | Animation senden, danach einen **Lauftext** | läuft wie eingestellt | | |
| C4 | Diagnoseprotokoll nach C1 bis C3 | Ereignis „Anzeigemodus nach den Daten erneut gesetzt (vorher Animation oder unbekannt)“ je einmal nach der Animation; danach bei weiteren Texten nicht mehr | | |
| C5 | Direkt nach dem Einschalten des Boards als Erstes eine Blockseite senden | steht als Standbild; Ereignis aus C4 erscheint (Zustand nach dem Start unbekannt) | | |

## D. Meldungen und gesperrte Regler

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Animationstest „80 Bilder“ (Einstellungen) senden | Tafel lehnt ab (Code 0x04); **die Oberfläche zeigt jetzt eine Meldung** „Fehler: Tafel lehnt Paket 1 von 241 ab …“ (0.6.1.4: keine Meldung, D10) | | |
| D2 | Tafel ausschalten, einen Text senden | Meldung „Fehler: LED-Tafel nicht gefunden …“ | | |
| D3 | Animation senden und den Tempo-Regler im Bedienfeld ansehen | Regler sichtbar ausgegraut (blasser) und nicht bedienbar (0.6.1.4: gesperrt, aber optisch unverändert, A4/D5) | | |
| D4 | Programm abspielen, Tempo-Regler ansehen | ebenfalls sichtbar gesperrt | | |
| D5 | Ausschnitt-Rahmen beim GIF-Import ansehen (F1 aus 0.6.1.4) | Bild unter dem Rahmen wirkt nicht mehr weichgezeichnet, Pixel scharf | | |

## E. Animationen: Rückwärts, Eingabefeld, Sortieren

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | GIF importieren, „Rückwärts abspielen“ anhaken | Vorschau läuft rückwärts | | |
| E2 | Zusätzlich „Hin und zurück“ anhaken | Vorschau läuft rückwärts und wieder vorwärts; Bildzahl wie bei „Hin und zurück“ allein | | |
| E3 | Speichern und senden | Tafel zeigt die Animation rückwärts | | |
| E4 | Gespeicherte Animation bearbeiten, „Rückwärts abspielen“ anhaken, speichern | gespeicherte Animation läuft danach rückwärts; Häkchen ist beim nächsten Öffnen wieder aus | | |
| E5 | Text-Raster einfügen, speichern; danach erneut „Importieren“ öffnen | Eingabefeld für das Text-Raster ist leer und zugeklappt | | |
| E6 | In der Animationsliste eine Animation mit den Pfeilen nach oben und unten verschieben | Reihenfolge ändert sich sofort | | |
| E7 | Seite neu laden (oder am anderen Gerät öffnen) | Reihenfolge aus E6 bleibt (liegt im ESP32) | | |
| E8 | Neue Animation speichern | erscheint **am Ende** der Liste, auch wenn sie eine kleine (wiederverwendete) Nummer bekommt | | |
| E9 | Eine Animation in der Mitte löschen | übrige Reihenfolge bleibt erhalten | | |
| E10 | Kurzwahl mit einer Animation nach dem Sortieren antippen | sendet weiterhin dieselbe Animation (Sortieren ändert keine Nummern) | | |

## F. Mehrfachauswahl zum Löschen (Laptop, Maus und Tastatur)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | Bibliothek: einen Eintrag anklicken, dann Strg-Klick (Mac: Cmd-Klick) auf einen zweiten | beide markiert (gelber Rahmen); Zeile „2 Einträge ausgewählt. Nur „Löschen“ ist möglich …“; Stift, Senden, Duplizieren, Umbenennen und die Pfeile ausgegraut, Löschen aktiv | | |
| F2 | Umschalt-Klick auf einen weiter unten stehenden Eintrag | Bereich vom ersten bis zu diesem Eintrag markiert | | |
| F3 | Strg-Klick auf einen markierten Eintrag | wird wieder abgewählt | | |
| F4 | Esc, danach Strg+A | Esc hebt die Auswahl auf; Strg+A markiert alle Einträge | | |
| F5 | Drei Wegwerf-Einträge markieren, „Löschen“ (oder Entf) | **eine** Rückfrage mit Anzahl, Namen und ggf. „Verwendet von: Programme …/Kurzwahlen …“; nach „OK“ alle drei weg, Meldung „3 Bibliothekseinträge gelöscht.“ | | |
| F6 | Mehrfachauswahl mit einem Block-Eintrag (Blockfolge) und einem Text | beide lassen sich gemeinsam löschen | | |
| F7 | Programme: zwei Wegwerf-Programme mit Strg-Klick markieren, löschen | eine Rückfrage, beide gelöscht; „Neu“, „Bearbeiten“ und „Starten“ waren während der Auswahl gesperrt | | |
| F8 | Animationen: zwei Animationen markieren | Senden, Umbenennen, Bearbeiten, Importieren und Pfeile gesperrt; Vorschau ausgeblendet; Löschen aktiv | | |
| F9 | Animationen: zwei Wegwerf-Animationen markieren und löschen, **während** eine große Animation an die Tafel gesendet wird | Meldung „0 von 2 gelöscht. Fehler bei: … (Der Controller ist beschaeftigt.)“; beide bleiben in der Liste; nach dem Versand lassen sie sich löschen | | |
| F10 | iPhone/iPad: in denselben Listen antippen | Einzelauswahl wie bisher, keine Kästchen, kein Auswahl-Knopf | | |

## G. Laptop-Ansicht (ab 1000 Pixel Fensterbreite)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| G1 | Laptop, Browser im Vollbild | links feste Seitenleiste mit Banane, Name, Version und allen Seiten; „Webinterface neu laden“ unten; keine Banane-Taste oben | | |
| G2 | Seiten über die Seitenleiste wechseln | aktuelle Seite in der Leiste markiert; jede Seite mit einem Klick | | |
| G3 | Kurzwahl | vier Kacheln pro Zeile, zwei Reihen; Seite passt ohne Scrollen | | |
| G4 | Bedienfeld unten (Helligkeit, Tempo, Tasten) auf allen Seiten | so breit wie der Inhalt darüber; gleiche Flächenfarbe wie die Karten | | |
| G5 | Fenster schmaler ziehen (unter 1000 Pixel, z. B. halbe Bildschirmbreite) | Seitenleiste verschwindet, Banane erscheint; das Menü öffnet **unter der Banane** (linksbündig zum Inhalt), nicht am Bildschirmrand | | |
| G6 | Texteditor am Laptop | Vorschau oben bleibt beim Scrollen sichtbar; nichts von der Seitenleiste verdeckt | | |
| G7 | iPhone hochkant | Ansicht wie bisher (Banane, Menü, Kacheln 2 × 4) | | |

## H. Offen aus 0.6.1.4 (nicht getestet)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | Animation so groß, dass der Platz nicht reicht (B7 alt) | klare Meldung statt Absturz; Reserve von 24 KiB bleibt frei | | |
| H2 | Kurzwahl mit Animation, Animation löschen (H3 alt) | Rückfrage nennt die Kurzwahl; Kachel zeigt danach „Animation fehlt“ und sendet nichts | | |
| H3 | „Nur senden“: danach Liste und „frei“ ansehen (G4 alt) | keine Reste, Speicher wie vorher | | |
| H4 | Speichern gesperrt bei voller Liste (40), „Nur senden“ geht (G5 alt) | wie beschrieben | | |
| H5 | Drei Animationen speichern, die mittlere löschen, eine vierte speichern (J8 alt) | die vierte bekommt die Nummer der gelöschten (Diagnose „Animation gespeichert, ID=…“), steht aber am Ende der Liste (E8) | | |
| H6 | Tasten zum Erzwingen nach einer Animation, dann Lauftext (J15 alt) | Tasten wieder frei | | |
| H7 | Bearbeiten und überschreiben, 5× hintereinander (K5 alt) | jedes Mal „gespeichert“, keine `.bak`-Meldung | | |
| H8 | 79 Bilder speichern und senden; 80 Bilder im Import versuchen (K9 alt) | 79 geht; bei 80 nennt die Oberfläche die Grenze | | |

## I. Diagnosewerte

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| I1 | Diagnose: „Kleinster freier Stapel (Loop-Task)“ | Wert **notieren** (0.6.1.4: 3.788 Byte; die Lesepuffer im Abruf sind jetzt kleiner) | | |
| I2 | RAM-Spur: „Niedrigster beobachteter System-Min-Heap“ und Phase | Wert und Phase **notieren** | | |
| I3 | HTTP-Spur: Worst Cases (Pfad, Heap niedrig) | Werte **notieren**; 503-Antworten erscheinen hier als Status | | |
| I4 | Wächter-Neustarts im ganzen Test | falls einer auftritt: Phase, Auftrag und freien Heap aus „Absturzspur Vorlauf“ notieren (offen: SYS-15, `ble_connect`/`ble_regNotify`) | | |

## Was zurückmelden

Pro Punkt „ok“, „nicht ok“ oder die Beobachtung in Worten; besonders **B1 bis B9 (Heap, Hauptfrage)**, C1 bis C5 (Modus), D1, D3, E6 bis E9 (Sortieren), F1 bis F9 (Mehrfachauswahl), G1 bis G5 (Laptop), A1 und A2. Dazu Diagnose-Export, RAM-Spur, HTTP-Spur und, wenn möglich, das Seriallog. Zusätzliche Beobachtungen gern in eigenen Zeilen unten in der Excel-Datei („Zusatz“); sie werden beim nächsten Build gelesen.
