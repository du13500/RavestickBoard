# RavestickBoard · Hardwaretest v0.6.1.9-dev (Stabilität der Animationsliste, Raster als Schnellmenü, „auf der Tafel“, Texteditor, Symbole)

**Stand: 14.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.8 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.6.1.9.xlsx` bereit (zum Ausfüllen am Handy oder Laptop). **Am Rechner geprüft (nicht auf der Hardware):** Zeichen-Parität Web ↔ Firmware, Hosttests mit dem echten Sketch-Code (u. a. Animationsliste und Vorschau-Route), Browsertests in Chromium. **Arduino-Compile, Tafel, iPhone und Safari sind noch nicht geprüft.** *Hauptfrage dieses Tests:* Bleibt das System-Minimum beim Öffnen der Animationen hoch und startet das Board nicht mehr neu (Abschnitt B)?

## Vorbereitung

1. JSON-Backup ziehen, 0.6.1.8 als Rückfallversion aufbewahren.
2. `firmware/RavestickBoard_v0_6_1_9/RavestickBoard_v0_6_1_9.ino` öffnen, **alle sieben Dateien** im Sketch-Ordner lassen, Einstellungen unverändert. `RB_TEST_HANG` steht auf 1 (für Schritt K1).
3. iPhone 13 Pro und iPhone SE bereitlegen, jeweils als Web-App (Homescreen) und in Safari; Laptop. Für Abschnitt J: alle anderen Geräte mit gespeichertem WLAN `RavestickBoard` (iPad, Watch, weiteres Handy) im Blick behalten.
4. Nach dem Test Diagnose, `ram.txt` und `http.txt` exportieren; Seriallog mitlaufen lassen.
5. Schritte mit der Frage „Gefällt mir so / lieber anders“ sind **Regelfragen**: Hier geht es nicht um richtig oder falsch, sondern darum, ob dir das Verhalten gefällt. Bitte ehrlich antworten; danach entscheidet sich, was geändert wird.

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| A1 | Sketch `RavestickBoard_v0_6_1_9.ino` öffnen (alle sieben Dateien im Ordner lassen), kompilieren. | Kompiliert. Neu im Code: Route `/api/anim/thumb`, schlanke Animationsliste, Merkblock für abgebrochene Übertragungen, MAC-Endungen in der Diagnose. Die Zeilen „Der Sketch verwendet …“ und „Globale Variablen …“ **notieren** (0.6.1.8: 1.636.691 Byte, 78 %). | | |
| A2 | Flashen, mit dem WLAN `RavestickBoard` verbinden, die Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.6.1.9-dev (Diagnose). | | |

## B. Stabilität: Animationsliste und Vorschaubilder (Hauptfrage dieses Tests)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Menü → Animationen öffnen (mit möglichst 20 oder mehr gespeicherten Animationen, in 0.6.1.8 waren es 22). | Die Kacheln stehen sofort da (Name, „n Frames · x,y s“); die Vorschaubilder erscheinen danach nach und nach (zuerst ein Platzhalter). Kein Ruckeln, keine Neustarts. Zeit bis alle Bilder da sind **notieren**. | | |
| B2 | Das Raster scrollen (iPhone Web-App und Safari, SE, Laptop). | Es scrollt ruhig innerhalb des Rahmens; die Kopfzeile bleibt stehen. (In 0.6.1.8 scrollte das Raster nicht.) | | |
| B3 | Die Seite verlassen und Animationen noch einmal öffnen. | Die Vorschaubilder sind sofort da (Zwischenspeicher im Browser). In `http.txt` kommt dabei kein `/api/anim/thumb` mehr vor. | | |
| B4 | Zehnmal zwischen Animationen und einer anderen Seite wechseln, danach Diagnose öffnen. | Kleinster freier Heap und System-Minimum **notieren** (0.6.1.8: System-Minimum fiel auf 176 Byte, RAM-Datei „min“ 2.280 Byte). Erwartung: deutlich höher, kein Absturz. | | |
| B5 | Eine Animation umbenennen oder ihre Zeit ändern und speichern, dann das Raster ansehen. | Die Kachel zeigt den neuen Namen bzw. die neue Zeit; das Vorschaubild wird neu geladen, wenn sich die Animation geändert hat. | | |
| B6 | `http.txt` exportieren und die Dauer von `/api/anim/list` und `/api/anim/thumb` ansehen. | Die Liste braucht jetzt nur noch einen Bruchteil der früheren 850 bis 950 ms; die Vorschau-Pakete (höchstens 3 Bilder je Anfrage) sind kurz. Beide Werte **notieren**. Außerdem die Dauer von `/api/library` **notieren** (0.6.1.8: etwa 1,7 s). | | |
| B7 | Etwa 30 Minuten mit zwei Geräten abwechselnd Animationen, Bibliothek und Texteditor benutzen. | Kein ungeplanter Neustart. Wenn doch: Diagnose → Absturzspur, Phase **notieren**. | | |

## C. Animationen: Raster als Schnellmenü, Liste als Editor

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | Menü → Animationen öffnen (auch nach der Liste noch einmal über das Menü). | Immer das Raster, nie die Liste. | | |
| C2 | Eine Kachel antippen. | Die Kachel wird markiert, es wird nichts nachgeladen (in `http.txt` kein `/api/anim/get`). Oben rechts stehen Senden (mint, Flugzeug) und der Stift. | | |
| C3 | Oben auf Senden tippen. | Die markierte Animation wird gesendet (Hinweis „Übertragung läuft …“, alle Geräte gesperrt); danach „auf der Tafel“ an dieser Kachel. | | |
| C4 | Den Stift antippen. | Die Liste öffnet sich als Editor: Zurück-Pfeil oben rechts, „n von 40 Animationen · frei …“, Leiste (Plus, Senden, Stift, Umbenennen, Löschen), große Vorschau, darunter die Liste mit Pfeilen. Erst hier läuft die Vorschau. | | |
| C5 | In der Liste eine Animation wählen und beobachten, solange sie lädt. | Solange sie lädt, sind alle Schaltflächen gesperrt (sichtbar abgeblendet); danach wieder frei. | | |
| C6 | Im Raster nach einem Import-Knopf suchen; in der Liste das Plus antippen. | Im Raster gibt es keinen Import; das Plus der Liste öffnet die Import-Seite. | | |
| C7 | Import-Seite → Text-Raster (Datei laden, übernehmen). | Keine Rahmenwahl, keine Voreinstellungen (Original, Füllen, Strecken …), keine Farbumsetzung (Schwelle, Floyd-Steinberg …), keine Regler für Helligkeit und Kontrast. | | |
| C8 | Import-Seite → GIF und Einzelbilder aus einem Bild. | Wie in 0.6.1.8: mit Rahmen, Voreinstellungen, Farbumsetzung und Reglern. | | |
| C9 | In der Liste den Zurück-Pfeil antippen. | Zurück im Raster; die zuletzt markierte Kachel ist weiter markiert. | | |
| C10 | Das Raster und die Bedienung ansehen. | Gefällt dir der Ablauf Raster → Senden oder Stift → Editor so? *(Regelfrage)* | | |

## D. Abgebrochene Übertragung und „auf der Tafel“

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Eine Animation erfolgreich senden (Markierung erscheint). Dann eine andere senden und mitten in der Übertragung die Tafel ausschalten oder aus der Reichweite nehmen. | Die Übertragung bricht mit Meldung ab; die Tafel zeigt das Herstellerbild „CoolLED“. Die Markierung „auf der Tafel“ ist **weg** (nirgends mehr gesetzt). | | |
| D2 | Die Tafel ausgeschaltet lassen und etwas senden (Verbindung kommt gar nicht zustande). | Meldung, dass die Tafel nicht erreichbar ist. Die Markierung des letzten erfolgreichen Eintrags bleibt, weil die Tafel noch den alten Inhalt zeigt (es wurde nichts übertragen). | | |
| D3 | Tafel wieder einschalten, denselben Eintrag senden. | Läuft durch; die Markierung erscheint wieder. | | |

## E. „Auf der Tafel“: neue Darstellung

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Bibliothek: einen Eintrag senden. | Ein kleiner mintfarbener Punkt mit Flugzeug-Symbol steht an dem Eintrag (in 0.6.1.8 zeigte die Bibliothek gar nichts). | | |
| E2 | Programme: ein Programm senden. | Das Flugzeug-Symbol steht direkt links neben den Pfeilen. | | |
| E3 | Animationen: Liste und Raster nach dem Senden ansehen. | Liste: Symbol an der Zeile; Raster: Punkt in der Kachel. | | |
| E4 | Kurzwahl: die gesendete Taste ansehen. | Punkt oben rechts in der Kachel. | | |
| E5 | Ambiente: eine Farbe senden. | Punkt oben rechts an der Farbfläche (bisher mittig rechts). | | |
| E6 | Hinweise unten (z. B. Übertragung, Speichern) beobachten. | Sie blenden weich ein und aus, kein hartes Springen. | | |
| E7 | Einen Blocktext senden, während ein Programm läuft (oder ein Programm, das einen Blocktext enthält). | Markierung beobachten: Wird der Blocktext in der Bibliothek markiert? **Bemerkung:** Bei der Frage aus 0.6.1.8 („Marker nicht sichtbar“) ist unklar, ob es an Blocktexten im Programm liegt. | | |
| E8 | Die neue Darstellung ansehen. | Gefällt dir der ruhigere Punkt mit Flugzeug? *(Regelfrage)* | | |

## F. Texteditor

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | Texteditor mit leerem Eingabefeld öffnen (Lauftext und Blocktext). | „Lauftext senden“, „Diese Seite senden“, „Alle Seiten senden“ und „Speichern“ sind inaktiv; sobald Text drinsteht, sind sie aktiv; wieder leer, wieder inaktiv. | | |
| F2 | „Speichern“ ansehen. | Im selben Farbdesign wie die anderen Speichern-Knöpfe. | | |
| F3 | Unter Speichern und Senden nach Hinweistexten schauen („Ungespeicherter Entwurf …“, „Bearbeite … Du kannst diesen Blocktext aktualisieren …“). | Sie sind weg; die Kopfanzeige genügt. | | |
| F4 | „Zeichen gestalten“ öffnen. | Der Hinweis lautet „Färbt Buchstaben und färbbare Symbole.“; im Dialog gibt es kein „Senden“, nur „Fertig“. Das Palette-Symbol am Computer ist gut erkennbar (nicht winzig). | | |
| F5 | Nach „Umkehren“ suchen (Schalter im Editor, Bibliothek-Vorschau). | Es gibt die Funktion nicht mehr (verworfen). Ein in 0.6.1.8 gespeicherter Text mit Umkehren zeigt sich normal, ohne Fehler und ohne gefüllte Fläche. | | |

## G. Symbole

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| G1 | Symbol-Menü: nach „Ballon“ suchen; ein altes Fächer-Symbol (falls in einem Eintrag vorhanden) ansehen. | Nr. 59 ist ein Heißluftballon (nicht mehr „Fächer“), in einer passenden Kategorie. Ein alter Text mit dem Fächer zeigt jetzt den Ballon. | | |
| G2 | Äffchen und Schwein ansehen, beide senden. | Neue Entwürfe wie abgestimmt; auf der Tafel gut erkennbar. Gefallen sie dir? *(Regelfrage)* | | |
| G3 | Nach „Schneeflocke“ suchen. | Es gibt „Schneeflocke weiß“, „Schneeflocke gelb“ und „Schneeflocke blau“ (keine ohne Farbangabe). | | |
| G4 | Die Reiterzeile am Laptop ansehen und mit der Maus bzw. dem Trackpad wischen; dasselbe am Handy. | Scrollt oder bricht um, wird nicht hart abgeschnitten; links und rechts weicher Verlauf. | | |
| G5 | Reiter „Alle Symbole“ antippen. | Er steht zwischen „Zuletzt benutzt“ und „Liebe“ und zeigt alle Symbole (78 Kacheln). | | |

## H. Bibliothek mit Vorschau (Laptop, mindestens 1000 px breit)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | Einen Lauftext wählen; den Tempo-Bereich der Vorschau ansehen. | Statt des Reglers ein Stufenknopf wie in der Vorschau des Texteditors (Schnecke, Vogel, Hase); er wirkt nur auf die Vorschau, nicht auf die Tafel. | | |
| H2 | Einen Blocktext wählen. | Auch hier der Stufenknopf, dort ohne Pause/Play; die Seiten wechseln der Reihe nach. | | |
| H3 | Den Vorschaukasten unten ansehen. | Er endet auf der Höhe des Listenkastens links. | | |
| H4 | Das Fenster schmaler ziehen oder die Bibliothek am Handy öffnen. | Der Kasten ist weg, die Liste wie vorher. | | |

## I. Ambiente (Computer)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| I1 | Ambiente am Laptop öffnen. | Die sieben Farben stehen in der aktuellen (kleineren) Größe alle untereinander wie am Telefon (nicht 4 + 3). | | |
| I2 | Ambiente am Handy öffnen. | Unverändert. | | |

## J. WLAN-Clients (zwei angezeigt, ein Gerät?)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| J1 | Diagnose öffnen, Zeile „WLAN Clients“ ansehen. | Sie zeigt die Zahl und in eckigen Klammern die Endungen der Stationen (die letzten drei Bytes). Endungen und Zahl **notieren**. | | |
| J2 | Alle anderen Geräte (iPad, Watch, zweites Handy, Laptop) vom WLAN `RavestickBoard` trennen bzw. dessen WLAN ausschalten; nur ein Gerät verbunden lassen. Diagnose ansehen. | Zahl und Endungen **notieren**. Steht trotzdem 2 da: Welche Endung gehört zu welchem Gerät? (iPhone: Einstellungen → WLAN → Netzwerk → Adresse.) | | |
| J3 | Mit dem Laptop verbinden, während das iPhone verbunden ist. | Klappt (Limit sind zwei Geräte). Wenn nicht: Endungen der zwei belegten Plätze **notieren**. | | |
| J4 | Eine halbe Stunde nebenbei die Zeile „WLAN Clients“ ab und zu ansehen. | Wechselt eine Endung (Station verbindet neu), **notieren** wann. | | |

## K. Regressionsschritte aus 0.6.1.8

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| K1 | Am Laptop `http://192.168.4.1/api/test/hang` aufrufen; iPhone beobachten. | Hinweis „ESP32 antwortet nicht …“ nach etwa 5 bis 8 s; nach dem Wächter-Neustart die Meldung „Der ESP32 hat sich neu gestartet …“. Sekunden **notieren**. | | |
| K2 | Eine Datei JSON-Backup exportieren und wieder importieren. | Einträge, Programme und Kurzwahlen kommen zurück; Symbole stehen richtig. | | |
| K3 | Die DVD-Logo-Animation (`DVD_Logo_Animation.txt`) importieren und senden (die Datei liegt bei). | Läuft auf der Tafel wie in der Vorschau; Gefällt sie dir? *(Rückmeldung für die Beispiel-Animationen)* | | |

## L. Gesamt

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| L1 | Diagnose: kleinster freier Stapel und minimal freier Heap. | **Notieren.** (0.6.1.8: Stapel min 4.524 Byte, Heap-Minimum RAM-Datei 2.280 Byte.) | | |
| L2 | Neustarts außer dem Test-Hänger K1. | Keiner; sonst Phase und was du gerade getan hast notieren. | | |
| L3 | Gesamteindruck, Wünsche. | Frei. | | |
