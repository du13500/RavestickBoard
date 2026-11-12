# RavestickBoard · Hardwaretest v0.6.1.4-dev (Abruf in Teilen, freie Nummern, Löschen mit Kurzwahl, gesperrte Tasten, Regression)

**Stand: 4.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.3 (liegt in `archive/`). 0.6.1.3 lief auf der Hardware (54 Schritte in Ordnung, 1 nicht, 5 nicht getestet, 18 offen). **Hauptbefund:** Das Auswählen einer großen Animation holte die ganze Nutzlast in einer Antwort und leerte den Heap bis auf wenige hundert Byte (Wächter-Neustart in der Phase `anim_get`). 0.6.1.4 ruft die Animation in Teilen ab (3000 Byte, bei Heap unter 16.000 Byte antwortet die Firmware mit „Speicher knapp“ und die Oberfläche wartet kurz und fragt erneut), vergibt die **kleinste freie Nummer** (eine Nummer, auf die noch eine Kurzwahl zeigt, wird nicht vergeben), **lässt beim Löschen die Kurzwahlen unberührt** (Kachel: „Animation fehlt“) und **sperrt die Tasten zum Erzwingen des Anzeigeverhaltens**, solange eine Animation läuft. **Die wichtigste Messung dieses Tests ist der Heap beim Auswählen großer Animationen (Abschnitt J).** Die Abschnitte A bis I sind die Regression aus 0.6.1.2, Abschnitt K enthält die weiter gültigen Prüfungen aus 0.6.1.3. Was am Rechner geprüft ist und was nicht, steht im Changelog (v0.6.1.4).

## Vorbereitung

1. JSON-Backup der Bibliothek sichern (Einstellungen), bisherige Firmware (0.6.1.3) als Rückfallversion aufbewahren.
2. `firmware/RavestickBoard_v0_6_1_4/RavestickBoard_v0_6_1_4.ino` öffnen, **alle sieben Dateien** im Sketch-Ordner lassen (unverändert seit 0.6.1.0), Einstellungen unverändert (ESP32C3 Dev Module, Core 3.3.12, USB CDC On Boot: Enabled, No OTA 2MB APP/2MB SPIFFS, Erase All Flash aus). „Meine Tafel“ bleibt erhalten.
3. Original-App der Tafel vom Handy trennen. Tafel einschalten, in Reichweite aufstellen.
4. Testmaterial bereithalten: ein kleines GIF (wenige Bilder), ein größeres GIF (mehr als 79 Bilder, möglichst mit Transparenz), ein Bildstreifen, ein Text-Raster aus Excel (16 Zeilen × 64 Spalten, Buchstaben `.RGBCMYW`).
5. Animationsversand und Animationstest **ersetzen den Inhalt der Tafel**. Für jeden Test notieren, was die Tafel zeigt (nichts / Standbild / Animation / ERROR), und danach das Diagnoseprotokoll exportieren.

## A. Start und Regression

| Nr. | Bereich | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|---|
| A1 | Build | Sketch kompiliert ohne Fehler (die `-Wvolatile`-Warnungen zu `++notifyCount` usw. sind alt und harmlos); in 0.6.1.0 war `rb42ProgramPlaying` in `RavestickBoard_Anim.h` der einzige Fehler. Danach können noch Meldungen des Linkers kommen; besonders auf `RavestickBoard_Anim.h`, `File`, `openNextFile`, `rename` achten | kompiliert | | |
| A2 | Start | WLAN `CoolLED1248`, Weboberfläche, Version | 0.6.1.4-dev; „Meine Tafel“ aktiv | | |
| A3 | Menü | Hauptmenü öffnen | Punkt „Animationen“ mit dem Symbol Bild mit Wiedergabepfeil (`image-play`), Reihenfolge der übrigen Punkte unverändert | | |
| A4 | Regression | Lauftext senden, Blockseite senden, Helligkeit, Tempo, Programm abspielen | wie bei 0.6.0.2; kein Auftrag bricht ab | | |
| A5 | Einstellungen | Abschnitt „Animationstest“ | vier Tasten und „Zeit je Frame“; **keine** Auswahl „Anzeigemodus danach“ | | |

## B. Speichern und Liste

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Animationen öffnen (Dateisystem eingerichtet) | leere Liste mit Hinweis; kein Fehler | | |
| B2 | Dateisystem nicht eingerichtet (falls es sich nachstellen lässt) | verständliche Meldung statt Fehler | | |
| B3 | Kleines GIF importieren, Standardwerte, speichern | Vorschau läuft, Speichern meldet Erfolg, Eintrag erscheint mit Vorschaubild, Name, Bildzahl, Zeit | | |
| B4 | Seite neu laden (Menü), Liste erneut öffnen | Eintrag bleibt; Vorschau stimmt | | |
| B5 | ESP32 neu starten (Strom), Liste öffnen | Eintrag bleibt (LittleFS) | | |
| B6 | Umbenennen, Löschen (Duplizieren gibt es in der Oberfläche nicht mehr) | wie angezeigt; Löschen entfernt den Eintrag; die Symbolleiste zeigt Importieren, Senden (mint), Umbenennen, Löschen | | |
| B7 | Mehrere Animationen anlegen, bis Speicher oder Limit (40) erreicht | klare Meldung statt Absturz; Reserve von 24 KiB bleibt frei; **Heap-Minimum in der Diagnose notieren** (in 0.6.1.3 hier ein Fehler) | | |
| B8 | Während des Hochladens zweites Gerät im WLAN | Hochladen läuft durch; Heap-Minimum in der Diagnose notieren | | |

## C. Import und Anpassen (iPhone/iPad-Safari und Desktop)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | GIF mit Transparenz und Teilbildern | Vorschau sieht aus wie das Original (Farben auf sieben reduziert) | | |
| C2 | Großes GIF (> 79 Bilder) | Hinweis auf die Grenze; „Auf 79 Bilder verteilen“ wählt gleichmäßig; Zeit pro Bild notieren (Decoder-Dauer, Absturz?) | | |
| C3 | Voreinstellungen Einpassen, Füllen, Strecken, Original (setzen nur den Rahmen, Details in Abschnitt F) | Vorschau folgt | | |
| C4 | Farbreduktion: Schwelle, Floyd-Steinberg, Bayer, Schwellwert, Kontrast | Vorschau folgt; Bayer/Floyd gut bei Verläufen | | |
| C5 | Bildstreifen importieren | Bilder in richtiger Reihenfolge | | |
| C6 | Text-Raster aus Excel einfügen (Tabulator-getrennt), mit zwei Bildern getrennt durch Leerzeile oder `---` | zwei Bilder, Farben passen zu den Buchstaben | | |
| C7 | Bildbereich, Schrittweite, Hin und Zurück, wiederholte Bilder | Bildzahl und Dauer in der Anzeige stimmen | | |
| C8 | Eingabefelder (iPhone) | kein Zoomen beim Antippen | | |

## D. Senden an die Tafel

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Animation mit 16 Bildern senden | Meldung „gesendet“; Tafel zeigt die Animation wie in der Vorschau (Farben, Richtung); Dauer notieren | | |
| D2 | Animation mit 79 Bildern senden | wird angenommen (30 363 B); **Dauer notieren** (in 0.6.1.3 gemessen: rund 53 s; Oberfläche zeigt eine Schätzung); Wächter-Neustart? Letzte Phase notieren | | |
| D3 | Tafel aus- und einschalten | Animation bleibt (bei 0.6.0.2 bestätigt) | | |
| D4 | Danach Lauftext senden | Text ersetzt die Animation sauber | | |
| D5 | Tempo-Regler nach dem Senden einer Animation | gesperrt mit Hinweis; nach einem Lauftext wieder frei | | |
| D6 | ESP32 neu starten, Tempo-Regler | bedienbar (Zustand unbekannt) | | |
| D7 | Helligkeit ändern, nachdem eine Animation läuft | **notieren, ob die Helligkeit wirkt** (offen aus 0.6.0.2) | | |
| D8 | Tafel ausschalten, Animation senden | Meldung „LED-Tafel nicht gefunden“, kein Hänger | | |
| D9 | Während des Sendens einen anderen Befehl (zweites Gerät) | Antwort „beschäftigt“ (409) oder Wartezeit; kein Neustart | | |
| D10 | 80 Bilder: Animationstest „80 Frames“ wiederholen | Tafel lehnt schon das erste Paket ab (Code 0x04); Oberfläche meldet es; danach ist alles weiter bedienbar | | |

## E. Diagnose

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Diagnose exportieren | Ereignisse `ANIM` plausibel; `ackOk` steigt mit den Paketen; `ackNak`/`ackFatal` nur bei echten Fehlern | | |
| E2 | Heap-Tiefstwert nach den Tests | deutlich besser als bei 0.6.1.3 (dort 352 Byte System-Minimum nach dem Abruf einer großen Animation); Wert notieren | | |
| E3 | Hänger mit Wächter-Neustart | falls aufgetreten: Phase und Paketnummer notieren | | |

## F. Ausschnitt-Rahmen (aus 0.6.1.2)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | GIF importieren, großes Bild (mindestens 2× so groß wie die Tafel) | über dem Bild liegt ein gelber Rahmen im Seitenverhältnis 4 : 1, außerhalb abgedunkelt; die Vorschau darunter zeigt genau den Rahmeninhalt | | |
| F2 | Rahmen mit dem Finger (iPhone/iPad), Stift (Apple Pencil) bzw. Maus verschieben | folgt dem Finger, die Vorschau folgt verzögert (bis etwa 0,2 s); die Seite scrollt dabei **nicht** mit | | |
| F3 | An einer Ecke ziehen | Rahmen wird größer/kleiner, die gegenüberliegende Ecke bleibt stehen, Verhältnis bleibt 4 : 1 | | |
| F4 | Mit zwei Fingern auf dem Bild spreizen/zusammenziehen (nur Touch), Mausrad (Desktop) | Rahmen wird kleiner/größer; Safari zoomt dabei nicht die ganze Seite | | |
| F5 | „Rahmen kleiner“ / „Rahmen größer“ | in Schritten; für Geräte ohne Zwei-Finger-Bedienung | | |
| F6 | Voreinstellung Einpassen, Füllen, Original, Strecken durchschalten | Rahmen springt passend (Einpassen: ganzes Bild, ggf. mit schwarzen Rändern; Füllen: Bild füllt die Tafel; Strecken: ganzes Bild, Rahmen gestrichelt); nach dem Verschieben steht „Eigener Ausschnitt“ | | |
| F7 | Rahmen teilweise über den Bildrand schieben | außerhalb des Bildes ist die Tafel schwarz | | |
| F8 | GIF mit mehreren Bildern, Feld „Von Bild“ ändern | die Rahmenansicht zeigt das gewählte Bild | | |
| F9 | Gespeicherte Animation senden | Tafel zeigt denselben Ausschnitt wie die Vorschau | | |

## G. Speichern, Speichern und senden, Nur senden (aus 0.6.1.2)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| G1 | „Speichern“ | Eintrag in der Liste, nichts wird gesendet | | |
| G2 | „Speichern und senden“ | Eintrag in der Liste und Tafel zeigt die Animation; beide Senden-Knöpfe mint | | |
| G3 | „Nur senden (nicht speichern)“ | Tafel zeigt die Animation; **kein** neuer Listeneintrag; Speicher (Liste, „frei“) danach wie vorher | | |
| G4 | Nach G3 ESP32 neu starten, Liste und Diagnose ansehen | keine Reste (die temporäre Datei `send.rba` wird nach dem Senden gelöscht, `up.tmp` beim Start) | | |
| G5 | Nur senden mit 40 gespeicherten Animationen | Speichern gesperrt mit Hinweis, „Nur senden“ geht | | |
| G6 | Nur senden während ein anderer Auftrag läuft | Meldung „beschäftigt“ statt Hänger | | |

## H. Animationen als Kurzwahl (aus 0.6.1.2)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | Kurzwahl belegen: Quelle „Animationen“ (Symbol `image-play`) | Liste der gespeicherten Animationen, Beschriftung vorbelegt | | |
| H2 | Kachel antippen | Tafel zeigt die Animation (Dauer wie beim Senden aus der Liste, bei 79 Bildern etwa 55 s) | | |
| H3 | Animation löschen, die einer Kurzwahl zugeordnet ist | Rückfrage nennt die Kurzwahl und sagt, dass die Kachel danach „Animation fehlt“ zeigt; nach dem Löschen zeigt sie das und sendet nichts (Meldung); die Kurzwahl bleibt belegt | | |
| H4 | Neustart des ESP32 | Zuordnung bleibt (Kurzwahlen liegen im NVS) | | |
| H5 | Backup der Bibliothek (Einstellungen) | enthält die Animationen **nicht** (Dateien liegen im LittleFS, nicht im JSON-Backup) | | |

## I. Bestehende Animation bearbeiten (aus 0.6.1.2)

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| I1 | Animation in der Liste wählen, Knopf „Bearbeiten“ (Stift) | Ansicht „Animation bearbeiten“ ohne Quelle und Ausschnitt; Name, Zeit und Bildbereich vorbelegt; Vorschau läuft | | |
| I2 | Zeit je Frame ändern (z. B. halbieren), Bildbereich kürzen | Anzeige „n Frames · x ms“ und Vorschau folgen | | |
| I3 | „Speichern“ | Liste zeigt dieselbe Animation (gleiche Stelle, neuer Name/Zeit); kein zusätzlicher Eintrag | | |
| I4 | Animation senden | Tafel zeigt die geänderte Zeit/Bilder | | |
| I5 | Einer Kurzwahl zugeordnete Animation bearbeiten und speichern | Kurzwahl zeigt weiter auf sie und sendet die neue Fassung | | |
| I6 | „Als Kopie speichern“ | neuer Eintrag, Original unverändert | | |
| I7 | „Speichern und senden“ und „Nur senden“ im Bearbeiten | wie beschriftet; Nur senden legt nichts in der Liste an | | |
| I8 | Mit 40 Animationen: Bearbeiten, „Speichern“ | geht; „Als Kopie speichern“ gesperrt | | |
| I9 | ESP32 während des Überschreibens vom Strom trennen (nur wenn du es testen magst) | nach dem Start: Original oder neue Fassung vorhanden, keine halbe Datei in der Liste; Diagnose zeigt ggf. „Unfertiger Animations-Upload entfernt“ | | |
| I10 | Prüfen, ob das Überschreiben auch bei knappem Speicher klappt (ein sehr großes Original, danach Bearbeiten) | entweder erfolgreich oder verständliche Meldung „Nicht genug freier Speicher“ | | |

## J. Neu in 0.6.1.4: Abruf in Teilen, freie Nummern, Löschen mit Kurzwahl, gesperrte Tasten

*Zum Notieren der Nummern:* Die Oberfläche zeigt die Nummer einer Animation nicht an. Nach jedem Speichern steht im Diagnoseprotokoll „Animation gespeichert, ID=…“; Diagnose exportieren und dort nachsehen.

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| J1 | Eine Animation mit **79 Bildern** speichern (oder eine vorhandene große nehmen), in der Liste **auswählen** | Vorschau erscheint ohne Fehler; Ladedauer in Sekunden notieren (in 0.6.1.3 bis 5,5 s); kein Neustart | | |
| J2 | Direkt danach Diagnose und HTTP-Spur exportieren | Heap-Minimum, System-Minimum und „Kleinster Heap in Anfrage“ (Pfad `/api/anim/get`) **notieren**; zum Vergleich: in 0.6.1.3 Heap 1.640 Byte, System-Minimum 352 Byte | | |
| J3 | Zwischen zwei großen Animationen fünfmal hin und her wechseln | jedes Mal Vorschau, kein Wächter-Neustart; Heap-Minimum danach notieren | | |
| J4 | Eine große Animation **bearbeiten** (Stift) | Ansicht lädt vollständig, Vorschau läuft; „Speichern“ funktioniert | | |
| J5 | Zwei Geräte: Gerät A wählt eine große Animation, Gerät B lädt gleichzeitig Startseite oder Liste | beide Geräte bekommen ihre Daten; kurze Wartezeit ist erlaubt; kein Neustart. Falls eine Meldung „Speicher knapp“ erscheint: notieren, wie oft und ob es am Ende durchlief | | |
| J6 | Beobachten, ob die Vorschau beim Auswählen einmal kurz „hängt“ | eine Wartezeit von wenigen Sekunden ist die Wiederholung bei „Speicher knapp“; Dauerfehler wäre ein Befund | | |
| J7 | Liste mit möglichst **vielen Animationen (20 bis 40)** öffnen | Liste lädt; Dauer und, falls möglich, den Eintrag `/api/anim/list` unter „Worst Cases“ der HTTP-Spur **notieren** (Beobachtung ANM-22: in 0.6.1.3 sank das System-Minimum während dieser Anfrage von 7.400 auf 3.920 Byte) | | |
| J8 | Eine Animation speichern, eine zweite, eine dritte; Nummern aus dem Protokoll notieren; die **mittlere löschen**; eine vierte speichern | die vierte bekommt die Nummer der gelöschten (kleinste freie), sofern keine Kurzwahl auf sie zeigte | | |
| J9 | Eine Animation einer Kurzwahl zuordnen, dann **löschen** (Rückfrage lesen) | Rückfrage nennt die Kurzwahl und „Die Kachel zeigt danach „Animation fehlt““, **kein** „geleert“; nach dem Löschen zeigt die Kachel „Animation fehlt“, sendet nichts | | |
| J10 | Danach eine **neue** Animation speichern (Nummer im Protokoll notieren) | sie bekommt **nicht** die Nummer der gelöschten (die Kurzwahl reserviert sie); die Kachel startet die neue Animation **nicht** | | |
| J11 | Die Kachel leeren oder neu belegen (Stift, Kurzwahl-Dialog) | Kachel wieder normal; eine weitere neue Animation kann jetzt die freie Nummer bekommen | | |
| J12 | Animation löschen, die **keiner** Kurzwahl zugeordnet ist | normaler Text ohne Hinweis auf Kurzwahlen | | |
| J13 | Eine Animation senden; während sie läuft die Tasten zum Erzwingen des Anzeigeverhaltens ansehen (Startseite, Lauftext, Seiten, Programme, Bibliothek, Kurzwahl) | alle diese Tasten ausgegraut und nicht bedienbar; Titel (Desktop: Mauszeiger) nennt den Grund; **Anzeige an/aus** und der Stift der Kurzwahl bleiben bedienbar; Tempo-Regler gesperrt (wie D5) | | |
| J14 | Danach einen Lauftext senden | Tasten wieder frei, Titel wieder wie vorher | | |
| J15 | ESP32 neu starten, Seite neu laden | Tasten frei (Zustand unbekannt, wie beim Tempo-Regler) | | |
| J16 | BLE-Hänger beobachten (Aufträge senden wie sonst) | falls ein Wächter-Neustart auftritt: Phase, Auftrag und freien Heap aus der Diagnose notieren (Phasen `ble_connect` und `ble_regNotify` waren in 0.6.1.3 dreimal betroffen) | | |
| J17 | Eine Animation bearbeiten (Stift) und die Ansicht unter den Knöpfen ansehen (Zusatzzeile Z2 deines Tests) | die zwei Hinweisabsätze („Speichern überschreibt diese Animation …“ und „Nur senden legt die Animation nur vorübergehend …“) sind **nicht mehr da**; „Speichern“, „Als Kopie speichern“, „Speichern und senden“, „Nur senden“ funktionieren wie zuvor | | |

## K. Weiter gültig aus 0.6.1.3: Prüfsumme, Bearbeiten, Stapelwert

| Nr. | Schritt | Erwartung | Ergebnis | Bemerkung |
|---|---|---|---|---|
| K1 | Eine Animation normal speichern und senden | wie bisher; kein neuer Hinweis | | |
| K2 | Eine **alte** Animation aus 0.6.1.2 (ohne Prüfsumme) in der Liste wählen und senden | wird angezeigt und gesendet wie zuvor (keine Prüfsummenmeldung) | | |
| K3 | Diese alte Animation bearbeiten und speichern, danach senden | gespeichert (jetzt mit Prüfsumme), sendet; Liste zeigt weiter einen Eintrag | | |
| K4 | Animation mit Kurzwahl bearbeiten und speichern (Überschreiben) | Kurzwahl zeigt weiter auf sie (wie I5) | | |
| K5 | Mehrfach hintereinander bearbeiten und überschreiben (5×) | jedes Mal „gespeichert“, Liste unverändert groß, keine Meldung zu `.bak` im Diagnoseprotokoll | | |
| K6 | Diagnose: nach „Animation senden“ das Protokoll ansehen | Ereignis „Animation startet“ (beim Animationstest „Animationstest startet“) | | |
| K7 | Diagnose exportieren | Zeile „Kleinster freier Stapel (Loop-Task): … Bytes“; Wert **notieren** (in 0.6.1.3: 4.856 Byte) | | |
| K8 | Beim Arduino-Compile die Zeile „Globale Variablen verwenden … Bytes“ | Wert **notieren** (in 0.6.1.3: 79.452 Byte, 24 %) | | |
| K9 | Grenzfälle: Animation mit **79** Bildern speichern und senden, danach **80** versuchen | 79 geht; bei 80 meldet die Oberfläche die Grenze (die Tafel lehnt 80 Bilder mit Code 0x04 ab, in 0.6.1.3 bestätigt) | | |
| K10 | Helligkeit: Regler bewegen, Animation senden, Tafel aus und wieder ein | beobachten, ob die Helligkeit der Animation zum Regler passt (Befund N3); Beobachtung in Worten | | |
| K11 | (nur wenn du magst) Nach dem Speichern einer Animation den Strom trennen, neu starten | Animation ist da oder nicht da, keine halbe Datei in der Liste; Diagnose ggf. „Unfertiger Animations-Upload entfernt“ oder „Alte Animation … wiederhergestellt“ | | |

*Nicht am Gerät provozierbar:* ein echter Prüfsummenfehler (Meldung „Pruefsumme stimmt nicht …“) und ein Lesefehler beim Senden lassen sich ohne beschädigten Speicher nicht auslösen; sie sind am Rechner mit Attrappen geprüft. Falls einer auftritt: Meldung, Diagnose-Export und was die Tafel zeigt zurückmelden.

## Was zurückmelden

Pro Punkt „ok“, „nicht ok“ oder die Beobachtung in Worten; besonders **J1 bis J7 (Heap und Dauer)**, J8 bis J12 (Nummern und Kurzwahl), J13 bis J15 (Tasten), A1, A2, B3–B5, D1–D2, D5, D7, D10, F2–F4 (Touch-Bedienung), G3, H2–H3, I3–I5, K7 und K8. Dazu den Diagnose-Export (Text), die HTTP-Spur und die RAM-Messung. Aus den Ergebnissen folgt (mit deinem Go) der Zeichen-Editor (0.6.2.0) oder zuerst eine Korrektur.
