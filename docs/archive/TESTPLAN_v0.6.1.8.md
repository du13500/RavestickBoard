# RavestickBoard · Hardwaretest v0.6.1.8-dev (Symbole, Symbol-Menü, Umkehren, Animations-Raster, „auf der Tafel“, Vorschau)

**Stand: 14.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.7 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.6.1.8.xlsx` bereit (zum Ausfüllen am Handy oder Laptop). **Am Rechner geprüft, aber nicht auf der Hardware:** Zeichen-Parität Web ↔ Firmware, Hosttests mit dem echten Sketch-Code, Browsertests in Chromium. **Offen:** Arduino-Compile, Tafel, iPhone, Safari.

## Vorbereitung

1. JSON-Backup ziehen, 0.6.1.7 als Rückfallversion aufbewahren.
2. `firmware/RavestickBoard_v0_6_1_8/RavestickBoard_v0_6_1_8.ino` öffnen, **alle sieben Dateien** im Sketch-Ordner lassen, Einstellungen unverändert. `RB_TEST_HANG` steht auf 1 (für Abschnitt H).
3. iPhone 13 Pro und iPhone SE bereitlegen, jeweils als Web-App (Homescreen) und in Safari; Laptop.
4. Nach dem Test Diagnose, `ram.txt` und `http.txt` exportieren; Seriallog mitlaufen lassen.
5. Schritte mit der Frage „Gefällt mir so / lieber anders“ sind **Regelfragen**: Hier geht es nicht um richtig oder falsch, sondern darum, ob dir das Verhalten gefällt. Bitte ehrlich antworten; danach entscheidet sich, was geändert wird.

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| A1 | Sketch `RavestickBoard_v0_6_1_8.ino` öffnen (alle sieben Dateien im Ordner lassen), kompilieren. | Kompiliert. Neu im Code: Merkblock „auf der Tafel“, Route „Meine Tafel entfernen“. Die Zeilen „Der Sketch verwendet …“ und „Globale Variablen …“ **notieren** (0.6.1.7: 1.617.975 / 83.552 Byte). | | |
| A2 | Flashen, mit dem WLAN `RavestickBoard` verbinden, die Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.6.1.8-dev (Diagnose). | | |

## B. Symbole und Symbol-Menü

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Texteditor: Symbol-Knopf antippen (iPhone). | Ein Fenster fährt von unten ein (etwa 60 % der Höhe). Oben „Symbol einfügen“ mit Kreuz, darunter die Reiter, ein Suchfeld „Suchen …“ und Kacheln aus LED-Punkten ohne Beschriftung. Eingabefeld und Vorschau darüber bleiben sichtbar. | | |
| B2 | Drei Symbole nacheinander antippen. | Jedes wird sofort eingefügt, das Fenster bleibt offen. Neben dem Titel blendet kurz der Name des eben getippten Symbols ein und wieder aus. | | |
| B3 | Das Fenster schließen: Kreuz, nach unten wischen, am Laptop Esc. | Es geht jedes Mal zu; der Text bleibt. | | |
| B4 | Die Reiter durchtippen, auch den mit der Uhr („Zuletzt benutzt“); die Reiterzeile seitlich wischen. | Jeder Reiter zeigt seine Symbole; „Zuletzt benutzt“ zeigt die eben getippten; der gelbe Rahmen einer gewählten Kachel ist am Rand nicht abgeschnitten. | | |
| B5 | In die Suche tippen: „Zigarette“, „Kippe“, „cigarette“, „heart“, „Hund“, „Ecke“. | Passende Symbole erscheinen (zweisprachig); kein Erklärtext unter den Treffern. | | |
| B6 | Das Fenster auf einem kleinen Handy (SE) und am Laptop ansehen. | Kleines Handy 4 Spalten, Laptop 10 Spalten; sauberer Umbruch, letzte Zeile linksbündig. | | |
| B7 | Die Kacheln genau ansehen. | Das Palette-Zeichen oben rechts steht nur an färbbaren Symbolen (Herz, Augen, Auto, Zapfsäule, vier Pfeile, Strohhalm). Ein feiner Umriss steht nur an den Flaggen Polyamore und Straight Ally. | | |
| B8 | Herz im Menü suchen; über die Tastatur ein gelbes Herz 💛 in den Text schreiben. | Im Menü gibt es nur ein rotes Herz. Das gelbe Herz aus der Tastatur wird in Vorschau und auf der Tafel weiter als gelbes Herz gezeigt. | | |
| B9 | Auto, Bus, Blitz, Telefon, Augen, Hund, Küken und Bier senden und auf der Tafel ansehen. | Aussehen wie in der Vorschau; die Symbole stehen senkrecht mittig; schmale Symbole nehmen nur ihre eigene Breite (wie schmale Buchstaben). | | |
| B10 | Die sechs Flaggen senden: Polysexual, Trans, Polyamore, Pansexual, Straight Ally, Pride. | Alle sind gleich hoch und länger als hoch (16 × 12). Polyamore und Straight Ally zeigen den dunklen Streifen unten (LEDs aus). Trans: Cyan, Magenta, Weiß, Magenta, Cyan. | | |
| B11 | Im Menü nach den umbenannten Einträgen schauen: Huhn rot, Huhn gelb, Küken, Schneeflocke gelb / Schneeflocke / Schneeflocke blau, Ecke, Brunnen. | Alle vorhanden. Es gibt nur noch eine Warnung in Gelb und keine bunten Warnungs-Varianten mehr. | | |
| B12 | Die gelbe Warnung ansehen. | Sie hat einen blauen Rand (so war sie schon in der Hersteller-App). Gefällt dir der blaue Rand? *(Regelfrage)* | | |
| B13 | Die Zuordnung zu den Reitern ansehen: Nase bei Liebe; UFO und Alien bei Fahrzeuge & Weltall; Banane bei Essen; Musiknote, Ecke und Pokal bei Festival; Telefon bei Hinweisen. | Alles dort zu finden. Passt die Zuordnung? *(Regelfrage)* | | |

## C. Symbole färben und Farbwechsel

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | Text mit Buchstaben, einem Auto und einem Herz schreiben. „Zeichen gestalten“ öffnen, alles auswählen, Farbwechsel mit Rot, Gelb, Grün anwenden. | Es erscheint die Frage „Symbole mitfärben?“ mit „Mit Symbolen“, „Ohne Symbole“ und „Abbrechen“. | | |
| C2 | „Ohne Symbole“ wählen. | Auto und Herz bleiben in ihrer Standardfarbe. Die Buchstaben laufen durch die Farben, als stünden die Symbole nicht da (sie verbrauchen keinen Farbschritt). Gefällt dir das so? *(Regelfrage)* | | |
| C3 | Rückgängig, dann dasselbe mit „Mit Symbolen“. | Jedes färbbare Symbol bekommt eine Farbe aus der Reihe wie ein Buchstabe. Gefällt dir die Reihenfolge? *(Regelfrage)* | | |
| C4 | Dasselbe im Wortmodus (ein Symbol steht mitten in einem Wort). | „Ohne Symbole“: das Symbol wird übersprungen, die Wortfarbe läuft weiter. „Mit Symbolen“: das Symbol bekommt die Farbe seines Wortes. Gefällt dir das so? *(Regelfrage)* | | |
| C5 | Eine Auswahl nur mit Buchstaben, und eine mit einem Stern oder Kussmund dazwischen, farbwechseln. | Keine Frage. Stern und Kussmund (nicht färbbar) zwischen Buchstaben verbrauchen keine Farbe. Gefällt dir das so? *(Regelfrage)* | | |
| C6 | Eine einzelne Zelle mit einem nicht färbbaren Symbol (z. B. Stern) auswählen. | Die Farbknöpfe sind ausgegraut; ein kurzer Hinweis steht darunter. | | |
| C7 | Eine Zelle mit Herz, dann eine mit Auto, dann eine mit Augen auswählen und je eine Farbe tippen. | Herz und Auto färben sich ganz um. Bei den Augen wird nur die Iris (der blaue Teil) umgefärbt. | | |
| C8 | Die Gesamtfarbe des Textes ändern (z. B. auf Gelb). | Die Buchstaben werden gelb. Die Symbole färben sich nicht von allein um; vorher gesetzte Symbolfarben bleiben. Gefällt dir das so? *(Regelfrage)* | | |
| C9 | Gefärbtes Herz, Auto und Augen senden. | Die Farben auf der Tafel sehen aus wie in der Vorschau. | | |
| C10 | Einen alten Eintrag aus der Bibliothek mit Augen, Pfeilen oder Strohhalm ansehen und senden. | Unverändert wie früher gezeichnet (nichts wurde von allein umgefärbt). | | |

## D. Umkehren

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Im Texteditor „RAVE“ in Weiß schreiben, ganz unten den Schalter „Umkehren“ einschalten. | Die Vorschau zeigt eine weiße Fläche mit dunklen Buchstaben. Der Symbol-Knopf und „Zeichen gestalten“ sind gesperrt und nennen kurz den Grund. | | |
| D2 | Als Standbild und als Lauftext (Gelb) senden. | Die Tafel leuchtet in der gewählten Farbe, die Buchstaben sind aus. Beim Lauftext leuchtet die Fläche durchgehend, ohne Lücken zwischen den Wiederholungen. | | |
| D3 | Dasselbe in zweizeilig, Fett, Eng und Mini. | Tafel entspricht der Vorschau. | | |
| D4 | Einen Text mit Symbol oder Einzelfarben schreiben und dann „Umkehren“ einschalten. | Der Schalter lässt sich nicht einschalten und nennt kurz den Grund (erst Symbole oder Zeichen-Gestaltung entfernen). Gefällt dir das, oder soll er den Text lieber still umbauen? *(Regelfrage)* | | |
| D5 | Blocktext mit zwei Seiten: Seite 1 umgekehrt, Seite 2 normal. | Jede Seite hat ihren eigenen Zustand; die Tafel zeigt es entsprechend. | | |
| D6 | Einen umgekehrten Text in der Bibliothek speichern und wieder öffnen. | Er bleibt umgekehrt (in der Bibliothek-Vorschau „· umgekehrt“). Alte Einträge bleiben normal. | | |
| D7 | Eine weiße, umgekehrte Fläche einige Minuten laufen lassen (Powerbank beobachten, Tafel fühlen). | Wärme und Stromverbrauch **notieren**. Brauchst du einen Hinweis oder eine Helligkeitsbegrenzung? *(Regelfrage)* | | |

## E. Animationen: Raster und Import-Seite

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Animationen öffnen (Handy). | Kopf „Animationen“ mit „Import“ und „Liste“; darunter „n von 40 Animationen · frei …“; zwei Spalten mit Karten: Vorschau, Name, „n Frames · x,y s“, „Senden“ in Mint und Stift. | | |
| E2 | Den Abstand zwischen Kopf und den Karten ansehen. | Kein auffälliger Leerraum mehr (war in 0.6.1.7 A4). | | |
| E3 | Auf einer Karte „Senden“ tippen. | Die Animation läuft auf der Tafel; während der Übertragung sind alle Knöpfe grau und gesperrt. | | |
| E4 | „Liste“ antippen, neu laden, dann „Raster“ tippen. | Die alte Listenansicht mit Bedienfeld erscheint; die Wahl bleibt nach dem Neuladen. | | |
| E5 | Am Laptop: Raster ansehen. | Mehr Spalten, Bedienfeld unten, Seite im Rahmen. | | |
| E6 | „Import“ antippen. | Eigene Seite ohne Bedienfeld unten; drei gleichberechtigte Wege nebeneinander, je Icon über dem Text: GIF importieren, Einzelbilder aus einem Bild, Text-Raster. | | |
| E7 | Ein GIF importieren und speichern. | Wie bisher; der Name ist vorbelegt; die Animation erscheint im Raster. | | |
| E8 | Einzelbilder aus einem Bild importieren. | Wie bisher. | | |
| E9 | Text-Raster antippen. Bei leerem Feld „Textdatei laden“ (z. B. eine Datei aus `assets/animationen/`), danach „Text-Raster übernehmen“. | „Textdatei laden“ ist nur bei leerem Feld klickbar, „Text-Raster übernehmen“ nur mit Inhalt. Die Animation wird übernommen. | | |
| E10 | Auf der Anpassen-Seite „Rahmen kleiner/größer“ und „Auf n Bilder verteilen“ ansehen. | Rahmen-Knöpfe nur als Icons; „Auf n Bilder verteilen“ in voller Breite mit Abstand über „Name“. Gefällt dir die Seite so? *(Regelfrage)* | | |

## F. „Auf der Tafel“

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | Einen Bibliothekseintrag senden. | Nach dem erfolgreichen Senden trägt der Eintrag einen grünen Rand und rechts ein Schild „auf der Tafel“. Liegt er auf einer Kurzwahltaste, trägt die Taste die Markierung. | | |
| F2 | Ein Programm starten. | Die Markierung wandert zum Programm; der Bibliothekseintrag verliert sie. | | |
| F3 | Eine Animation senden. | Plakette „auf der Tafel“ oben rechts im Vorschaubild der Karte (und in der Liste am Zeilenende). | | |
| F4 | Eine Ambientefarbe senden. | Der Farbknopf trägt die Markierung. | | |
| F5 | Eine Kurzwahltaste antippen. | Die Markierung steht an der Taste, deren Ziel läuft. | | |
| F6 | Mit einem zweiten Gerät dieselbe Oberfläche öffnen. | Die Markierung steht dort ebenfalls (sie kommt aus dem Status des ESP32). | | |
| F7 | Den ESP32 vom Strom nehmen und wieder anstecken. | Die Markierung ist nach dem Start wieder da (im ESP32 gemerkt). | | |
| F8 | Das Markierte bearbeiten, überschreiben oder löschen; die Tafel im ESP32 wechseln. | Die Markierung verschwindet. | | |
| F9 | Eine Übertragung absichtlich abbrechen (z. B. Tafel ausschalten) und senden. | Es entsteht keine Markierung. | | |

## G. Bibliothek mit Vorschau (Laptop, mindestens 1000 px breit)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| G1 | Bibliothek öffnen, einen Eintrag antippen. | Rechts steht der Kasten „VORSCHAU“ mit LED-Vorschau und Name, Art, Farbe, Kurzwahl. | | |
| G2 | Einen Lauftext wählen. | Er läuft in der Vorschau; ein Tempo-Regler ist da und wirkt auf die Vorschau. | | |
| G3 | Einen Blocktext wählen. | Die Seiten wechseln der Reihe nach; die Art zeigt „Blocktext · n Seiten“. | | |
| G4 | Einen umgekehrten und einen Text mit Zeichenfarben wählen. | Gefüllte Fläche; in der Farbzeile „· umgekehrt“ bzw. „(mit Zeichenfarben)“. | | |
| G5 | Das Fenster schmaler ziehen oder die Bibliothek am Handy öffnen. | Der Kasten ist weg, die Liste wie vorher. | | |

## H. Korrekturen aus dem Test von 0.6.1.7

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | (C1) iPhone auf der Kurzwahl, am Laptop `http://192.168.4.1/api/test/hang` aufrufen. Zeit bis zum Hinweis stoppen. | Der Hinweis „ESP32 antwortet nicht …“ kommt nach etwa 5 bis 8 Sekunden, ohne langen Versatz. Sekunden **notieren**. | | |
| H2 | (Z3) iPhone nicht im WLAN des ESP32 (z. B. Mobilfunk), die Web-App öffnen. | Statt „ESP32 antwortet nicht …“ steht „Keine Verbindung zum ESP32 – bist du im WLAN „RavestickBoard“?“. | | |
| H3 | (C4) Nach dem Neustart des Hängers warten, ohne am Handy das WLAN anzufassen. | Nach etwa 22 s ohne Antwort erscheint einmal der Hinweis, das WLAN kurz aus- und wieder einzuschalten. Hilft das? Ist der Hinweis verständlich? *(Regelfrage)* | | |
| H4 | (Z4) Nach dem Test-Hänger Diagnose → „Absturzspur“ ansehen. | Die Phase nennt die Route des Web-Handlers (`web:/api/…`). Phase **notieren**. | | |
| H5 | (Z5) Einstellungen öffnen und schließen (mehrmals), „Tafel auswählen“ ansehen. | Der Tafel-Status lädt (kurz „wird geladen …“) ohne Darstellungsfehler. Sonst Screenshot an die Bemerkung hängen. | | |
| H6 | (Z1/Z2) Am Computer Texteditor und Ambiente ansehen. | Kompakter; keine Zeilen ohne Beschreibung. Das ist eine Vermutung nach dem Befundtext – bitte Screenshot anhängen, wenn etwas fehlt. Gefällt dir die Ansicht so? *(Regelfrage)* | | |
| H7 | (D4) Einstellungen → „Meine Tafel entfernen“. | Rückfrage; danach ist keine Tafel gespeichert und „Meine Tafel nutzen“ wird nicht mehr angeboten. War „meine Tafel“ gerade aktiv, steht die Auswahl auf „keine“. Danach wieder als meine Tafel speichern. | | |

## I. Offene Schritte aus 0.6.1.7

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| I1 | (B4) Eine große Animation senden und die Dauer stoppen. | Dauer **notieren** (0.6.1.7: Regenbogenwelle 32 Bilder in 22,2 s). | | |
| I2 | (B6) Diagnose: „Stapel vor der ersten Webantwort … | danach …“. | Werte **notieren** (0.6.1.7: 4.840 / 4.552 Byte). | | |
| I3 | (D2) Diagnose: `ram.txt` und `http.txt` exportieren, dann `ram.txt` noch einmal. | Im zweiten `ram.txt` oben „min=…“ **notieren** (0.6.1.7: 5.192 Byte). | | |
| I4 | (D3) Diagnose: Zeile „Exporte: auf freien Heap gewartet“. | Wert **notieren** (0.6.1.7: 0×). | | |
| I5 | (D5) Anzeige aus/ein, „Auswahl aufheben“ (Laptop, Strg-Klick) und Symbolauswahl schließen. | Nur Icons (Auge, Auge zu, Kreuz); Tooltips am Laptop. | | |
| I6 | (D6) Bibliothek ansehen. | Keine Zeile „Belegen/Freigeben“; die Kurzwahlen im Dialog funktionieren. | | |
| I7 | (D7) Ein altes JSON-Backup (mit Kurzwahlen, wenn möglich mit Herz in anderer Farbe) importieren. | Einträge und Kurzwahlen kommen zurück; Symbole stehen richtig. | | |

## J. Gesamt

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| J1 | Diagnose: kleinster freier Stapel und minimal freier Heap. | **Notieren.** | | |
| J2 | Neustarts außer dem Test-Hänger H1. | Keiner; sonst Phase und was du gerade getan hast notieren. | | |
| J3 | Gesamteindruck, Wünsche. | Frei. | | |
