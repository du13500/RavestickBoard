## Entscheidungen v0.6.0.0-dev bis v0.6.1.8-dev · 3.11.2026 bis 14.11.2026 (Animationen, Symbole)

| ID | Entscheidung | Begründung |
|---|---|---|
| ADR-2026-11-03-A | **Animationen sind ein eigener Bereich**, losgelöst von Lauftext, Seiten, Programmen, Effekten und Diashow. | Absprache vom 3.11.2026. Animation heißt hier GIF und gezeichnete Bildfolge, die die Tafel selbst abspielt; eine Diashow aus bestehenden Funktionen (Stufe 1 der Recherche) entfällt. |
| ADR-2026-11-03-B | **Import ist der Hauptweg, Zeichnen der Weg zum Nachbessern und zum vollständigen Erstellen.** Importquellen: GIF, Bildstreifen, Text-Raster mit Buchstaben `.RGBCMYW`. | Pixelweise Frames in Excel gehen für eine Animation, nicht für viele; Frame für Frame auf dem Handy ist sehr fummelig. Der Editor muss trotzdem auch iPad mit Stift tragen (Zeigerereignisse). |
| ADR-2026-11-03-C | **Erst Hardwaretest, dann Funktion.** 0.6.0.0 baut nur den Animationstest; 0.6.1.0 (Import/Liste), 0.6.2.0 (Editor), 0.6.3.0 (Komfort) folgen erst nach dem Ergebnis. | Ob die eigene Tafel `0x04` annimmt, wie sie es abspielt und was nach dem Ausschalten bleibt, ist ungeprüft. Alle Formatfakten stammen von einem anderen Gerät. |
| ADR-2026-11-03-D | **Obergrenze 79 Frames, ein globales Tempo je Animation, ein Inhalt auf der Tafel.** Halten durch wiederholte Frames. | 27 + 79 × 384 = 30 363 B passen in 30 KiB, 80 Frames nicht. Das Protokoll kennt keinen Zeitwert pro Frame. |
| ADR-2026-11-03-E | **Antwortcodes strikt nur im Animationstest.** Andere Aufträge zählen und protokollieren sie nur. | Verhalten bestehender, hardwaregeprüfter Aufträge soll nicht unbemerkt ändern. Ob Status ≠ 0 dort bisher still auftrat, ist unbekannt. |
| ADR-2026-11-03-H | **Reihenfolge im Sketch ist Teil der Prüfung:** Typen vor der ersten Funktion; automatische Prüfung der Prototyp-Regel im Build-Test. | Der Compile von 0.6.0.1 scheiterte, weil Animationsfunktionen vor `enum RamStage` standen. Rechnertests mit g++ auf Ausschnitten erkennen das nicht. |
| ADR-2026-11-03-G | **Jedes Frame der Testmuster trägt seine Nummer; eigene Ziffern; Grenztest 300 ms.** | Vorschlag des Nutzers beim Planen des Tests: Bei 79 gleichartigen Frames sieht man sonst nicht, wie viele ankommen und wo die Schleife endet. Eigene 3×5-Ziffern halten den Animationsweg vom Text-Renderer getrennt und am Rechner exakt prüfbar. 40 ms sind zum Lesen zu schnell. Ersetzt 0.6.0.0 (nicht geflasht). |
| ADR-2026-11-03-I | **Animationen liegen als Dateien im ESP32 (LittleFS), die Nutzlast unverändert.** Kopf 448 Byte mit Name, Zeit, Bildzahl und Vorschau. | Senden braucht keine Umrechnung und keinen Gesamtpuffer (Lesen ab Dateiposition 448); die Liste zeigt Vorschauen ohne Abruf der Nutzlast. Die Tafel speichert zwar die Animation selbst, hat aber keine auslesbare Liste. Alternative (Browser-Speicher) verworfen: nicht gerätübergreifend. |
| ADR-2026-11-03-J | **Alles Umwandeln im Browser, der ESP32 speichert und sendet nur.** Eigener GIF-Decoder statt Browser-Decoder. | Rechenleistung und Speicher des ESP32-C3 reichen nicht; der Decoder von Chromium (`ImageDecoder`) fehlt in älteren Safari-Versionen, Canvas gibt bei Animationen nur das erste Bild. Der eigene Decoder ist am Rechner gegen Chromium geprüft; Safari ungeprüft. |
| ADR-2026-11-03-K | **Anzeigemodus-Auswahl nach Animationen entfällt.** | Hardwaretest 0.6.0.2: `0x06` danach ohne Wirkung. Weniger Bedienung, ein Befehl weniger im Auftrag. |
| ADR-2026-11-03-L | **Tempo-Regler bei Animationen sperren (`animActive`).** | Hardwaretest 0.6.0.2: wirkt nicht; die Zeit je Bild steckt in der Animation. Zustand aus dem zuletzt gesendeten Inhalt (nach Neustart unbekannt, Regler dann frei). Umgesetzt wie bei Programmen mit Eigenzeit. |
| ADR-2026-11-03-M | **Beschädigte Dateien bleiben in der Liste sichtbar (`broken`) und zählen mit.** | Unsichtbare, aber mitzählende Dateien würden das Limit und den Speicher verbrauchen, ohne dass der Nutzer sie löschen kann. |
| ADR-2026-11-03-N | **Die Testmuster und der Animationstest bleiben.** | Wunsch des Nutzers: Nummern, Vollbildfarbe mit Nummer und Balken sind gelungen und vielleicht später für Zähler oder Uhrzeit nutzbar. |
| ADR-2026-11-03-O | **Neue Firmwareteile in eine `.h`-Datei (`RavestickBoard_Anim.h`).** | Eine `.h` bekommt keine automatischen Prototypen und kann die Regel aus 0.6.0.2 nicht verletzen; der Sketch bleibt überschaubar. Preis: Sketch-Ordner mit sieben Dateien. |
| ADR-2026-11-03-Q | **Der Ausschnitt ist ein Rahmen im Quellbild (4 : 1), die Voreinstellungen setzen nur den Rahmen; „Nur senden“ nutzt eine temporäre Datei; Kurzwahlen verweisen auf die Animations-ID.** | Wunsch des Nutzers (3.11.2026): Ausschnitt sichtbar und direkt greifbar statt Schieberegler; Rahmen bleibt 4 : 1. Der Sendeweg liest ohnehin aus einer Datei, eine temporäre Datei vermeidet einen zweiten Weg und das Halten von 30 KB im Heap. Die ID statt einer Kopie des Namens: Umbenennen wirkt sofort in der Kachel; gelöschte Animation → „fehlt“, kein stilles Senden von etwas anderem. | Bearbeiten (Nutzer, 3.11.2026): überschreibt unter derselben ID, weil Kurzwahlen auf die ID verweisen; änderbar nur, was ohne Original geht (Zeit, Bildbereich, Reihenfolge, Name); Kopie als Alternative. Rahmen nur auf Mobilgeräten testbar (Touch); ID-Verweis geht verloren, wenn Animationen exportiert/wieder importiert würden (es gibt noch keinen Export). |
| ADR-2026-11-03-P | **Auch die Include-Reihenfolge und die Deklarationsreihenfolge des zusammengesetzten Sketchs werden automatisch geprüft** (`tests/decl_order.py`). | Zweiter Compile-Fehler (0.6.0.1: Typ vor Prototyp, 0.6.1.0: Variable vor Deklaration), den die Ausschnitt-Tests am Rechner nicht sehen. Näherung, kein Ersatz für den Compile; nach jedem Firmware-Build zusammen mit `arduino_prototypes.py` laufen lassen. |
| ADR-2026-11-03-F | **Kein OpenSign-Quelltext übernommen**; Format und Paketierung eigenständig umgesetzt und lokal gegen OpenSign abgeglichen. | Klare Rechtslage (siehe `QUELLEN_UND_LIZENZEN.md`): MIT-Lizenz, dazu ausdrückliche Erlaubnis von Adam Schulz per E-Mail. MIT-Hinweis nur bei tatsächlicher Übernahme nötig, steht aber vorsorglich in `THIRD_PARTY_NOTICES.md`. |
| ADR-2026-11-04-A | *Abgelöst durch ADR-2026-11-04-J (0.6.1.4).* **Kurzwahlen werden beim Löschen geleert, statt einen dauerhaften ID-Zähler zu führen (Befund M2).** | Der Bericht nannte beides. Das Leeren braucht keine neue Datei und kein neues Format und deckt auch beschädigte Kurzwahl-Dateien ab (dann wird nichts gelöscht). Bibliothekseinträge machen es genauso (`v042DetachLibraryShortcuts`). |
| ADR-2026-11-04-B | **Prüfsumme im Kopf der Animationsdatei (CRC-32), Flag Bit 0; alte Dateien bleiben gültig (Befund M1).** | Die Nutzlast hatte keinen Schutz außer LittleFS-Metadaten. Der Kopf hatte freie Füllbytes (9), das Format bleibt 448 Byte. Alte Dateien ohne Flag werden akzeptiert, damit nichts neu gespeichert werden muss. Der Browser rechnet, der ESP32 prüft nach dem Schreiben und vor dem Senden. |
| ADR-2026-11-04-C | **Die MTU-Vorprüfung vor dem Senden bleibt (Befund N2 nicht umgesetzt).** | Sie baut jedes Paket probeweise und verhindert, dass ein zu langer Rahmen die Tafel erreicht. Ein Rechnen der größten Rahmenlänge wäre eine Verhaltensänderung im hardwaregeprüften Sendepfad ohne belegten Nutzen (Zeitgewinn ungemessen). |
| ADR-2026-11-04-D | **Das Ersetzen einer Animation löscht das Original nie vor dem Erfolg (Befund M3); ein Rest `.bak` wird beim Start aufgelöst.** | Ob `rename` auf ein vorhandenes Ziel in LittleFS ersetzt, ist hier nicht prüfbar; der Zweig mit `.bak` deckt beide Fälle ab und ist am Rechner mit einer Attrappe geprüft. |
| ADR-2026-11-04-E | **Route `/api/anim/duplicate` entfällt (Befund N6).** | Seit 0.6.1.2 von der Oberfläche nicht mehr benutzt; weniger Fläche, weniger Tests. |
| ADR-2026-11-04-F | **WLAN-Passwort ändern bleibt SYS-13 (Befund N14).** | Bewusst entschieden (ADR-004, ADR-031); wird vor dem ersten Einsatz mit fremden Geräten im Umfeld neu bewertet. |
| ADR-2026-11-04-G | **M4 und M5 werden zuerst gemessen, nicht umgebaut.** | Der Stapelwert kommt in die Diagnose, die Compilerzeile „Globale Variablen“ wird festgehalten. Ein gemeinsamer Header-Puffer geht nicht einfach: `onAnimPut` baut den Kopf und ruft dann `rb61AnimExists`. |
| ADR-2026-11-04-H | **Alte Tests nach `tests/legacy/`, alte Dokumente nach `docs/archive/` (Befunde N12, N13).** | Das Repository soll zeigen, was wirklich läuft. Der bestehende Ordner heißt `archive`, deshalb nicht `archiv` wie im Bericht. Der Git-Verlauf bleibt. |
| ADR-2026-11-04-I | **`RB_TEST_HANG` bleibt in Entwicklungsbuilds auf 1 (Befund V1); Release-Checkliste: auf 0 setzen und `test_build` den ausgelieferten Stand prüfen lassen.** | Für den Wiederanlauftest so vereinbart. |

## Entscheidung v0.4.0-dev · 26.10.2026

Wir wechseln von einer Editor-zentrierten Oberfläche zu sieben Bereichen mit festem Header und Menü über den Bananen-Button. Die Startseite besitzt sechs Kurzwahlen statt der früheren acht. Bibliothek und Programme sind getrennte Datenebenen, Programmzeilen referenzieren Bibliothekseinträge und übernehmen spätere Textänderungen. Globale Helligkeit und Geschwindigkeit bleiben bei Inhaltswechseln unverändert; ein manueller Modus-Override gilt nur bis zum nächsten Inhalt, dessen gespeicherter Modus wieder gilt. Einzelheiten dokumentiert `archive/ENTWICKLUNGSSTAND_v0.4.0_2026-10-26.md`. Unsere **eigenen Codebestandteile** veröffentlichen wir ab dieser Version unter MIT; Herstellerpixel und andere Fremdmaterialien sind davon ausgenommen.

---

## Ergänzung v0.3.5

### 2026-10-25: Umfang v0.3.5

Auf der stabilen v0.3.4 aufbauen; neue Komfortfunktionen und Symbole als v0.3.5 statt v0.3.4-Korrektur. Die erweiterten Modi bleiben manuell; keine Laufzeitkalibrierung für Sonderanimationen. Horizontale Textlaufzeit später für Playlist/Programmwechsel. LED Ein/Aus kurz und ohne Pixelupload, Wirkung auf realem Board noch zu testen. NVS-Schema bleibt unverändert. Symbole der zwei Mini-Zeilen dürfen sich absichtlich überlagern.

---

# Entscheidungen und Designprinzipien

**Stand 23.10.2026.** Entscheidungslog (ADR = Architecture Decision Record). Bestehende IDs bleiben stabil; historische Entscheidungen und spätere Präzisierungen werden getrennt dokumentiert. Eine Entscheidung ist nicht automatisch bereits implementiert.

| ID | Datum | Entscheidung | Grund / Auswirkung |
| --- | --- | --- | --- |
| ADR-001 | 2026-10 | **Original-LED-Tafel bleibt unangetastet**; ESP32-C3 steuert über BLE | Kein Löten/Umbau an der Anzeige nötig. |
| ADR-002 | 2026-10-22 | **Eigenes ESP32-WLAN**, kein notwendiges Heimnetz/Internet | Festivalbetrieb mit dem Smartphone möglich. |
| ADR-003 | 2026-10-22 | **Firmware nur per USB-C**, keine OTA-Funktion | Einfache Wartung, geringere Angriffsfläche und mehr Flash-Spielraum. |
| ADR-004 | 2026-10-22 | Passwortgeschütztes WLAN, **kein zweites Webinterface-Login** | Möglichst unkomplizierte Bedienung; direkte Fremdsteuerung der Originaltafel über BLE wird dadurch ohnehin nicht verhindert. |
| ADR-005 | 2026-10-22 | **Textlänge bestimmt nicht den Wiedergabemodus** | Lauftext oder statische Seiten werden immer explizit ausgewählt. Die v0.1.0-Längenautomatik ist nur ein Prototyp. |
| ADR-006 | 2026-10-22 | **Statische Anzeigen als individuell gestaltbare Seiten**, nicht über Leerzeichen simuliert | Pro Seite eigene Inhalte, Farben, Schriftwahl, Dauer; manuelle oder automatische Navigation. |
| ADR-007 | 2026-10-22 | **Zeichenweise bzw. bereichsweise Farben und Schriftarten** | Texteditor soll nicht an ein einheitliches Format gebunden sein. |
| ADR-008 | 2026-10-22 | **Vorschau zeigt echte LED-Punkte in festem 64×16-Raster** | Kein Schrumpfen langer Texte; Animation nur im festen Anzeigefenster. |
| ADR-009 | 2026-10-22 | **Vorschau mit Fast Forward** | Lange Laufschriften schnell prüfen; **1×/2×/4×**, **kein 8×** (am 23.10. endgültig entschieden). |
| ADR-010 | 2026-10-22 | **Normal und Bold als Originalschrift separat rekonstruieren** | Pixelgenaue Aufnahme der beiden Original-Modi, nicht versehentlich vermischen. |
| ADR-011 | 2026-10-22 | **Hersteller-Unregelmäßigkeiten einzeln diskutieren** | Originalreferenz bewahren; nicht pauschal übernehmen oder automatisch „verbessern“. |
| ADR-012 | 2026-10-22 | **Mini-Font selbst entwickeln**, Engschrift behalten | Mini ist kein Originalfont; Engschrift bereits erfolgreich ausprobiert. |
| ADR-013 | 2026-10-22 | **Zweizeilig ohne künstlich erzwungenen Leerabstand** | 16 verfügbare Pixel sinnvoll nutzen, Lesbarkeit praktisch prüfen. |
| ADR-014 | 2026-10-22 | **Versionierte Dokumentation + Diagnose von Anfang an** | Aus SmallTV-Erfahrungen lernen; sporadische Probleme nachvollziehbar machen. |
| ADR-015 | 2026-10 | **Webinterface gestalterisch von SmallTV unterscheiden** | An vertraute CoolLED1248-App angelehnt, aber moderner und besser bedienbar; nicht SmallTV-grau/gelb. |
| ADR-016 | 2026-10-22 | **Keine automatische Überschreibung beim Booten** | Bereits gespeicherte Anzeige unangetastet lassen, bis Nutzer aktiv sendet oder ein bewusst aktiviertes Programm läuft. |
| ADR-017 | 2026-10-22 | **Lizenz-/Provenienzprüfung vor der Entscheidung über öffentliche Sichtbarkeit** | Initiale technische Prüfung 23.10.2026 dokumentiert; keine pauschale Freigabe fremden Codes. |
| ADR-018 | 2026-10-22 | *Abgelöst durch ADR-2026-11-12-A (Name „RavestickBoard“).* **Projektname „RavestickBoard for CoolLED1248“**, GitHub-Repository | Unterscheidung vom Original-App-Namen; Rechte anderer Projekte bleiben zu beachten; Public-Sichtbarkeit ist kein Firmwareziel. |
| ADR-019 | 2026-10-22 | **Diagnose-Ringpuffer nur im RAM, TXT-Export auf Anfrage** | Weniger Flash-Verschleiß, keine zusätzliche Anmeldung, keine gespeicherten Textinhalte oder Kennwörter im Log. |
| ADR-020 | 2026-10-22 | **Firmwareversion im Header sichtbar und im Diagnosebericht** | Direkt erkennbare Softwareversion bei Screenshots und Support; Versionsstand passt zum Git-Commit. |

## Entscheidung 25.10.2026 – v0.3.4 als eigenständiges Feature-Release

v0.3.3 wurde bereits auf echter Hardware erfolgreich geprüft (u. a. 650 Zeichen/30.689 B, 2-Farben-Mini-Lauftext). Die zusätzlichen Werte `0x03`–`0x08` für **einen** BLE-Anzeigemodusbefehl `0x06` werden deshalb **nicht** als „v0.3.3 Korrektur 1“ bezeichnet, sondern als **v0.3.4** mit eigenem Sketchordner veröffentlicht. `0x01`/`0x02` bestätigt, weitere Werte noch ungetestet. Die ursprüngliche v0.3.3 bleibt unverändert. NVS-Datenformat und Bildrenderer ebenfalls unverändert. Getestete Grundlagen nicht mit neuen unbestätigten Modi vermischen.

## Entscheidung 25.10.2026 – v0.3.3: Datenbudget statt Zeichenzählerlimit

Die 600-Zeichen-Grenze wird **nicht** als Produktspezifikation behandelt. Der Editor berechnet die Bytegröße aus Originalglyphen, tatsächlichen Symbolbreiten und `107 + 6 × max(64, gerenderte Spalten)`. Der Zeichenzähler bleibt rein informativ. Bei Überschreitung erscheint die Auslastung **rot und fett**, ohne Textverlust; Senden wird blockiert. **30 KiB sind vorläufig**, die Hardwaregrenze bleibt unbekannt (29.837 B funktionierten, 31.853 B wurden gesendet, aber nicht dargestellt). Der Firmwarecode dekodiert lange Lauftexte iterativ, um beim Start keinen großen statischen Bild-/Zeichenpuffer zu reservieren.

Als kleine Zusatzfunktion erlaubt Mini Zweizeilig als **Lauftext** getrennte Farben pro Zeile; die zwei Zeilen scrollen synchron. Andere Layouts bleiben gleich. Bibliothek und Verkettung mehrerer Nachrichten sind **noch nicht implementiert**; sie gehören in einen späteren Release nach Hardwarevalidierung.

## Noch nicht technisch geklärt

- Ob **native Blockseiten** oder **gespeicherte Animationen `0x04`** auf unserer konkreten Tafel mit **einem** Upload autonom laufen; weitere Details in ADR-021/022.
- Ob die Original-Tafel pro Bild individuelle Haltezeiten beherrscht; wenn nicht, ob wiederholte Frames eine ausreichend gute Lösung darstellen.
- Wie Original-App-Geschwindigkeitsanzeige (~80) in BLE-Rohwerte übersetzt wird.
- Welche Speicherkapazitäten/Kompressionsstrategien für Bibliothek und Animationen realistisch sind.
- Ob eine optionale native App/Watch/Widget-Oberfläche später einen Mehrwert bietet.
- GitHub ist inzwischen **Public**, unabhängig bestätigt am 24.10.2026; die Lizenz bleibt All Rights Reserved.

## 22.10.2026 · v0.1.2: deutsche Sprache, Pixelvorschau und Modi

- Die Benutzeroberfläche schreibt Deutsch mit **Ä, Ö, Ü, ä, ö, ü und ß**. Keine pauschale Umschrift in `ae/oe/ue/ss`.
- Der Engschrift-Font bekommt echte Kleinbuchstaben; der Browser erhält seine Glyphen aus der ESP32-Tabelle über `/api/font`. Keine zweite manuell gepflegte Fonttabelle in JavaScript.
- Statischer Text und Lauftext werden **manuell gewählt**, unabhängig von Länge. Vorerst kein automatischer Seitenwechsel und kein generischer Auto-Umbruch. Zu breite Standbilder werden ausdrücklich gekennzeichnet.
- Die LED-Vorschau benutzt einzelne **runde** Punkte in fester 64×16-Matrix und bietet schnellen Vorlauf **1×/2×/4×**; **8× wurde ausdrücklich gestrichen**.
- Der Geschwindigkeitsregler für die LED-Tafel und die Vorschau-Fast-Forward-Funktion sind unabhängig voneinander. Geschwindigkeit bleibt bis zur Kalibrierung experimentell.
- Kopieren in die Zwischenablage wird zum bevorzugten Diagnose-Export, TXT bleibt als Alternative.

## Entscheidung 22.10.2026: v0.2.0-Blockeditor
- Seiten sind eigenständige Design-Objekte, nicht automatisch abgeschnittene Textstücke.
- Keine erzwungenen Zeilenumbrüche und kein automatisches Nachrücken von Seiten.
- Jede Seite hat eigenes Layout, Texte, Zeilenfarben, Ausrichtung und Anzeigedauer.
- 12 Seiten zunächst als pragmatisches Limit. Die gespeicherten Seiten bleiben nach Neustart erhalten; der konkrete v0.2.0-Test bestätigt das. NVS schreibt nicht pro laufendem Vorschauframe.
- Seitenplayer sendet vollständig über BLE; das ist ausdrücklich ein Experiment bis zur Klärung der Board-internen Mehrseitenfähigkeit.
- Firmware bleibt USB-only ohne OTA. Webinterface benötigt kein gesondertes Login.
- Typografische Detailkorrekturen g/p/q/y/Ä/Ö/Ü bleiben separate Entscheidungen anhand der Referenzen.


## Architektur-, Forschungs- und Dokumentationsentscheidungen (23.10.2026)

| ID | Datum | Entscheidung / Designvorgabe | Begründung / Einschränkung |
| --- | --- | --- | --- |
| ADR-021 | 2026-10-23 | **Seite → Programm → Playlist** als drei getrennte Ebenen | Keine ständigen Uploads zwischen Seiten eines Programms; bewusste neue Uploads zwischen Programmen erlaubt. |
| ADR-022 | 2026-10-23 | **`0x04`-Animation als Untersuchungspriorität** | OpenSign meldet autonome gespeicherte Animation, aber nur auf Referenzpanel; bei unserer Tafel erst isoliert nachweisen. |
| ADR-023 | 2026-10-23 | **Mini zweizeilig unverändert als Ausgangsbasis; zusätzlich Mini einzeilig; Mini-Ausgabe in Versalien** | Echte Nutzerfotos überzeugen für Großbuchstaben; Kleinbuchstaben in Mini unleserlich; ß-Pixelkorrektur als Detail. |
| ADR-024 | 2026-10-23 | **Entwurf, Bibliothek, aktives Programm trennen** | Lauftexteditor verliert Entwurf nach Reload, gespeicherte Blockseiten bleiben jedoch in NVS. Browser-Entwurf später wiederherstellen. |
| ADR-025 | 2026-10-23 | **Bibliothek zuerst im ESP32-Flash (LittleFS), microSD optional** | Wenig Zusatzhardware; einheitlich von verschiedenen Browsern erreichbar, Ex-/Import als Backup. |
| ADR-026 | 2026-10-23 | **OpenSign keine Codequelle ohne Erlaubnis** | Repo enthält ausdrücklich keine Lizenz; Eigenimplementierung aus Protokollfakten und eigenen Tests bzw. explizite Freigabe erforderlich. |
| ADR-027 | 2026-10-23 | **Live-Steuerbefehle ohne Neu-Upload** | `0x08` Helligkeit, `0x07` Geschwindigkeit, `0x06` Modus getrennt nutzen. |
| ADR-028 | 2026-10-23 | **Excel-kopierbare Testtabelle zu jedem Firmware-Updatepaket ausschließlich im Chat** | Unabhängiges manuelles Testprotokoll mit Ergebnis und Bemerkungen; keine zusätzliche Test-Datei. |
| ADR-029 | 2026-10-23 | **Firmware v0.2.0 vorerst nicht verändern** | Erst aktuelles Hardwareverhalten systematisch testen, dann Änderungen gebündelt umsetzen. |


## Weitere Entscheidungen vom 23.10.2026

| ID | Datum | Entscheidung | Grund / Auswirkung |
| --- | --- | --- | --- |
| ADR-030 | 2026-10-23 | **Eigenen Code öffentlich sichtbar zeigen ist keine Open-Source-Lizenz** | `LICENSE` bleibt „All Rights Reserved“, Rechte Dritter und GitHub-Plattformrechte bleiben bestehen. Keine neue Firmwarefunktion. |
| ADR-031 | 2026-10-23 | **Festes Testpasswort und BLE-MAC bewusst dokumentiert** | AP-Passwort `Banane1248!` darf im öffentlichen Quelltext bleiben; individuelles WLAN-Passwort per UI später optional. Die MAC gilt nur für die Testtafel. |
| ADR-032 | 2026-10-23 | **Titelbild im README zentriert und ohne Größenattribut** | `docs/assets/totem.jpg` soll in natürlicher Größe erscheinen; kein `width`/CSS-Zwang. |
| ADR-033 | 2026-10-23 | **README: Badges in Englisch, Beschreibung in Deutsch** | `status: hardware testing`, `mission: hugs and love`, außerdem Version/Hardware/Projekt/Lizenz. Kein gesonderter Abschnitt „Projektstruktur“ mehr. |
| ADR-034 | 2026-10-23 | **README als Nutzer-Vorlage bewahren** | Nicht bei Dokumentationspflege die Nutzeranpassungen durch ältere generierte README-Fassungen ersetzen. Bei nächster inhaltlicher Änderung eigene Minischrift klar benennen. |
| ADR-035 | 2026-10-23 | **v0.2.0 als erfolgreich hardwaregetesteter Prototyp** | Nutzer hat 13 von 14 Testpunkten mit Ja bewertet, ein Punkt unbewertet; konkrete Mängel (Kleinbuchstaben-Mini, ß, Prozentanzeige) bleiben offen. |
| ADR-036 | 2026-10-23 | **Schrift-Feinschliff gezielt und nicht pauschal** | Großbuchstaben-Mini zweizeilig beibehalten; Mini-Text in Versalien; zusätzliche einzeilige Mini; g/p/q/y mit gemeinsamer x-Höhe und Unterlängen; ß/ẞ nur minimal unterschiedlich, markierter Pixel aus. |
| ADR-037 | 2026-10-23 | **OpenSign-Kontakt per E-Mail statt öffentlichem Issue** | Die englische Lizenzanfrage an Adam wurde **am 23.10.2026 per E-Mail versendet**. **Antwort und Erlaubnis ausstehend**; kein OpenSign-Quellcode übernommen. |
| ADR-038 | 2026-10-23 | **Dokumente regelmäßig gegen aktuellen Firmwarestand abgleichen** | Jede neue Firmware erhält im Chat eine direkt nach Excel kopierbare Testtabelle; `docs/TESTPLAN.md` dient für historische Befunde und spezifische Regressionstests. |

## Designentscheidungen v0.3.0 (24.10.2026)

| ID | Datum | Entscheidung | Grund / Auswirkung |
| --- | --- | --- | --- |
| ADR-039 | 2026-10-24 | **Mini, eine Zeile: horizontal und vertikal zentriert** | Unabhängig vom bisherigen links/mitte/rechts-Wert; 7 Pixel Schrift hoch. |
| ADR-040 | 2026-10-24 | **16×16-Symbole inline als Emoji in Textfeldern** | Kein separater „Symbol statt Text“-Modus; bei zwei Zeilen sind überlappende Bereiche zu prüfen. |
| ADR-041 | 2026-10-24 | **Herz-Silhouette in allen sieben Farben** | Gewählte Emoji-Variante bestimmt die LED-Herzfarbe, unabhängig von der Textfarbe. |
| ADR-042 | 2026-10-24 | **Vorläufig effektive Symbolbreite plus 1 px Abstand** | Hersteller-App-Abstände später anhand Original-App messen und bei Bedarf korrigieren. |
| ADR-043 | 2026-10-24 | **Getrennte Hersteller- und RavestickBoard-Symbole** | 24 Originalsymbole mit kurzer Quellenangabe; selbst gestaltete, vertikal gespiegelte Ravestick-Banane separat. |
| ADR-044 | 2026-10-24 | **Neue Fontrenderpfade erhalten altes NVS-Seitenformat** | Bestehende bis zu 12 Seiten bleiben lesbar; Layout-ID 2/3/4 ergänzen. |
| ADR-045 | 2026-10-24 | **v0.3.0 ist bis zum Boardtest nur Entwicklungskandidat** | Browser-Simulation bestätigt nicht Arduino-Kompilierung, BLE-Funktion oder Pixelabstände auf der Tafel. |


## Ergänzungen vom 25.10.2026 (v0.3.2 Testkandidat)

- **ADR-2026-10-25-A · Testweise Langtexte:** Die alte 80-Zeichen-Softwaregrenze wird zur Messung vorläufig auf 600 Zeichen erhöht. Dies bestätigt **keine** korrekte Hardware- oder Protokollunterstützung. Der bisher rekonstruierte Header bleibt mit 80 Format-Slots unverändert und begrenzt den darin übermittelten Zeichenwert auf 80. Einzelne BLE-Erfolge und sichtbare Korrektheit getrennt bewerten.
- **ADR-2026-10-25-B · Dezentes Überlängenfeedback:** Bei mehr als 600 Codepoints wird lediglich der Live-Zähler rot und fett. Bereits getippter Text wird nicht gekürzt; ungültige Überlängen werden nicht übertragen. Kein neues Popup. Für zweizeiligen Lauftext zählen beide Zeilen zusammen.
- **ADR-2026-10-25-C · Mobil-Symbolauswahl:** Die Symbolpalette bleibt während mehrerer Einfügungen offen und fokussiert das iPhone-Textfeld beim Einfügen nicht automatisch. Diagnosestatus und Fußbereich gehören ausdrücklich **nicht** zum Overlay-DOM.
- **ADR-2026-10-25-D · Einheitliche Fontnamen:** Sichtbare Namen und Reihenfolge: Standard, Standard Bold, Engschrift, Mini Einzeilig, Mini Zweizeilig. Interne numerische Layout-IDs und gespeicherte NVS-Daten bleiben erhalten.
- **ADR-2026-10-25-E · Leere neue Eingaben:** Neue Texte und neue Blockseiten starten ohne Demo-Inhalte. Bereits gespeicherte Seiten/Browserentwürfe werden nicht stillschweigend gelöscht.
- **ADR-2026-10-25-F · Repository-Bereinigung:** Keine Datei automatisiert entfernen; die im Cleanup-Bericht vorgeschlagenen Löschungen/Verschiebungen erst nach Hardwaretest in einem separaten GitHub-Desktop-Commit.


## Architekturentscheidungen und Hypothesen nach dem v0.3.2-Hardwaretest (25.10.2026)

| ID | Status | Festlegung bzw. Untersuchung |
| --- | --- | --- |
| ADR-2026-10-25-G | **Entwicklungsrichtung beschlossen, noch nicht implementiert** | Starres 600-Zeichenlimit später durch **live berechnetes Pixel-/Datenbudget** ersetzen; bei Überlauf fett/rot markieren, nicht still kürzen, kein Popup. Der Controller validiert dieselben Renderingdaten. |
| ADR-2026-10-25-H | **Hardwaregrenze unbestätigt** | Erfolgreiche 29.837 B und fehlgeschlagene 31.853 B begrenzen den bisher beobachteten Bereich, beweisen aber weder 30 KiB noch 5.120 Spalten. Gezielter Test mit 300/301/302 Warnsymbolen geplant. |
| ADR-2026-10-25-I | **Diagnoseanforderung** | BLE-Paketquittung/`JOB OK` darf ohne weiteres Protokollwissen nicht als sichtbare LED-Bildübernahme bezeichnet werden. |
| ADR-2026-10-25-J | **Konzept, noch nicht implementiert** | Mehrere eigenständige **Lauftexte** aus einer späteren Bibliothek mit frei definierten Abständen zu einem einzigen Pixelstreifen und einem BLE-Upload verketten. Dadurch nur einmal Fortschrittsanzeige für den gesamten Inhalt. |
| ADR-2026-10-25-K | **Separate Forschungsaufgabe** | Echte Blockseitenprogramme mit Standzeiten/Moduswechseln nicht mit einem einzelnen gleichmäßig scrollenden Bildstreifen verwechseln; native Board-Fähigkeit noch ungeklärt. |
| ADR-2026-10-25-L | **Offener UI-Fix** | Mini Zweizeilig als Lauftext erhält später zwei unabhängig wählbare Textfarben; synchroner Scroll bleibt. |

Aktueller Teststand und Primärbeobachtungen: [`archive/ENTWICKLUNGSSTAND_v0.3.2_2026-10-25.md`](archive/ENTWICKLUNGSSTAND_v0.3.2_2026-10-25.md).
| ADR-2026-11-04-J | **Neue Animationen bekommen die kleinste freie Nummer; das Löschen fasst Kurzwahlen nicht an (ersetzt ADR-2026-11-04-A).** Frei heißt: keine Datei und keine Kurzwahl vom Typ 4 mit dieser Nummer; bei beschädigter Kurzwahl-Datei höchste Nummer + 1. | Rückfrage des Nutzers zu J4 (Hardwaretest 0.6.1.3): ein dauerhafter Zähler hätte eine Grenze, die sich nicht zurücksetzen lässt (es gibt keine Werkseinstellung), und die Bibliothek benutzt zwar einen Zähler, hat aber bis zu 192 Einträge und 64 KiB Reserve. Die Regel „nie eine Nummer vergeben, auf die eine Kurzwahl zeigt“ löst das Problem, das 0.6.1.3 durch das Leeren lösen wollte (Kachel startet versehentlich eine fremde Animation), ohne Zähler, ohne neues Format und ohne dass das Löschen an der Kurzwahl-Datei scheitert. Preis: eine Kachel kann auf eine fehlende Animation zeigen („Animation fehlt“), bis sie neu belegt oder geleert wird. |
| ADR-2026-11-04-K | *Abgelöst durch ADR-2026-11-12-B (0.6.1.5).* **Der Abruf einer Animation geschieht in Teilen zu höchstens 3000 Byte; unter 16.000 Byte freiem Heap antwortet die Firmware mit 503, der Browser wiederholt.** | Hardwaretest 0.6.1.3: Eine Antwort mit der ganzen Nutzlast brachte den Heap auf 1.640 Byte und löste einen Wächter-Neustart aus. Teile begrenzen den Bedarf je Antwort; die Schwelle schützt, wenn der Heap schon knapp ist. Die Werte 3000 und 16.000 sind Schätzungen aus den Messreihen, nicht aus Versuchen am Gerät abgeleitet; der nächste Hardwaretest soll sie bestätigen oder korrigieren. |
| ADR-2026-11-04-L | **Die Tasten zum Erzwingen des Anzeigeverhaltens sind bei laufender Animation gesperrt (nur Anzeige an/aus bleibt).** | Wunsch des Nutzers; wie beim Tempo-Regler (ADR-2026-11-03-L) wirken sie auf Animationen nicht (Hardwaretest 0.6.0.2). Zustand aus `animActive`; nach einem Neustart der Firmware unbekannt, dann sind die Tasten frei. |
| ADR-2026-11-12-A | **WLAN und Titel heißen „RavestickBoard“; das Passwort bleibt.** Löst ADR-018 („RavestickBoard for CoolLED1248“) ab und ersetzt den Kommentar „SSID unchanged for compatible setup“. | Wunsch vom 12.11.2026; das Repository heißt künftig `RavestickBoard`, der Zusatz für CoolLEDX/CoolLED1248 steht in README und Repo-Beschreibung. Jedes Gerät muss sich einmal mit dem neuen WLAN verbinden; Adresse 192.168.4.1 und Homescreen-Icon bleiben. |
| ADR-2026-11-12-B | **Heap-Schutz statt Hoffnung auf kleine Antworten: Abruf 1200 Byte in einer Antwort mit bekannter Länge; 503 bei freiem Heap unter 24.000 Byte oder größtem Block unter 10.000 Byte; lesende Listen-Routen 503 unter 20.000 Byte; Startseite Warteseite unter 22.000 Byte; Status, Diagnose und Exporte nie gesperrt.** Löst ADR-2026-11-04-K ab. | Hardwaretest 0.6.1.4: Teile zu 3000 Byte senkten den Heap um bis zu 23 KB, die Prüfung auf 16.000 Byte schützte nicht; Ruhe-Heap mit zwei Geräten nur etwa 31 KB. Die Schwellen sind aus den Messungen geschätzt und werden nach dem nächsten Test angepasst. Ein Wechsel auf NimBLE (deutlich weniger RAM als Bluedroid) wäre der größere Hebel, ist aber ein Umbau und eine eigene Entscheidung (Themenspeicher SYS-16). |
| ADR-2026-11-12-C | **Nach einer Animation (oder nach dem Start) wird der Anzeigemodus hinter den Daten noch einmal gesetzt.** | Im Test lief der erste Inhalt nach einer Animation mit Linkslauf, obwohl der Modus vorher gesetzt war (H2, J14). Ein zusätzlicher Befehl kostet etwa 0,2 s nur in diesem Fall. Versuch: Bestätigt der Hardwaretest die Wirkung nicht, wird er zurückgenommen. |
| ADR-2026-11-12-D | **Die Reihenfolge der Animationen liegt in `order.bin`; neue Animationen kommen ans Ende.** | Seit 0.6.1.4 werden Nummern wiederverwendet; die Nummer taugt nicht mehr als Reihenfolge. Eine eigene kleine Datei ändert das Dateiformat der Animationen nicht; fehlt sie, gilt aufsteigend nach Nummer. |
| ADR-2026-11-12-E | **Mehrfachauswahl nur mit Maus und Tastatur; ab zwei markierten Einträgen ist nur „Löschen“ bedienbar; gilt für Bibliothek, Programme und Animationen; kein Auswahl-Knopf für Touch.** | Wunsch vom 12.11.2026 („kein Extra-Knopf“, „gern für alles“). Mehrere Einträge zu senden ist Aufgabe der Programme. Eine gemeinsame Rückfrage, gelöscht wird nacheinander mit Schlussbericht. |
| ADR-2026-11-12-F | **Ab 1000 Pixel Fensterbreite eine feste Seitenleiste statt Bananen-Menü und breiterer Inhalt; darunter bleibt die Banane, das Menü öffnet unter ihr. Bedienfeld und Menü haben die Flächenfarbe der Karten.** | Am Laptop lag das Menü am Bildschirmrand, der Inhalt war auf 720 Pixel begrenzt, das Bedienfeld war 694 Pixel breit und hatte einen anderen Grauton. Die Entwürfe vom 12.11.2026 haben dir gefallen; Kontrast und Bibliotheks-Vorschau bleiben offen. |
| ADR-2026-11-12-G | **Die geplanten Stufen 0.6.1.5 (Stabilität), 0.6.1.6 (Bedienung) und 0.6.1.7 (Laptop-Ansicht) sind in einer Version 0.6.1.5 gebaut.** | Dein Wunsch, „direkt mehr in den Build“ zu nehmen. Nachteil: Ein Fehler im Test lässt sich schwerer einer Änderung zuordnen; deshalb trennt der Testplan die Abschnitte und nennt den Heap als Hauptfrage. |
| ADR-2026-11-12-H | **Während einer Übertragung antwortet der ESP32 – aber nur mit Status (busy), einer kleinen Warteseite oder 409; alle Geräte sperren in dieser Zeit Senden und Ändern. Schalter `RB_WEB_DURING_BLE` (Standard 1).** Variante (c) vom 12.11.2026: Hinweis „Übertragung läuft …“ ohne Prozent, auf dem Bedienfeld statt darüber; keine extra Erklärung in der Oberfläche, sie steht in der Doku. | Befund B5/F9 aus dem Test von 0.6.1.5: ohne Antworten sah das zweite Gerät eine weiße Seite und tippte Aufträge „ins Leere“, die danach nachgeholt wurden. Die Sperre selbst ist billig; teuer ist, dass der ESP32 überhaupt antwortet (Stapel des laufenden Auftrags, gemessen 3.656 Byte frei). Deshalb kein normaler Handler innerhalb des Auftrags, Aufruf höchstens alle 250 ms, Abfragen des Browsers nur etwa alle 2,4 s, keine Prozentzahl (weniger Abfragen), Messung des Stapels in der Diagnose und ein Schalter für den Rückweg. Folge: Listen, die ein Gerät noch nicht geladen hat, erscheinen erst nach der Übertragung. |
| ADR-2026-11-12-I | **Blocktext mit 40 Seiten (Test); Blockdateien aus 0.6.1.5 (25 Plätze) werden gelesen und beim nächsten Speichern im neuen Format abgelegt.** | Dein Wunsch („lass uns das mal mit 40 testen, herunterkorrigieren können wir immer“). Kosten: zwei feste Seitenfelder (Editor und Blockdatei) zu je 15 × 102 Byte mehr, zusammen etwa 3,1 KB RAM (im Gespräch vorher mit 1,6 KB zu niedrig geschätzt, weil nur ein Feld gezählt). 79 Seiten hätten etwa 5,6 KB gekostet. Rückweg zu 0.6.1.5 nur über das JSON-Backup, weil alte Firmware die größeren Dateien als beschädigt ansieht. |
| ADR-2026-11-12-J | **„Blocktext“ ist der einzige Name für feste Seiten (statt „Blockanzeige“, „Blockfolge“, „Blockseiten“) in Oberfläche und Meldungen; die gespeicherte Markierung `[Blockfolge]` in Bibliothekseinträgen bleibt.** | Einheitliche Sprache (Wunsch); die Markierung ist Teil gespeicherter Daten und darf sich nicht ändern. |
| ADR-2026-11-12-K | **Seiten mit Liste sind genau fensterhoch, das Bedienfeld sitzt unten bündig und ist so breit wie die Flächen; Texteditor und Bearbeitungsansichten scrollen normal.** | Entwurf vom 12.11.2026 (gefiel); auf dem iPhone SE verschwanden sonst Weiß in Ambiente und Teile der Listen unter dem Bedienfeld. |
| ADR-2026-11-12-L | **Die Vorschau-Schrift wird bis zum Erfolg im Hintergrund nachgeladen; ein älteres iOS ist nicht die Ursache für „Vorschau aus“.** | Befund iPhone SE (iOS 18.7.8) im Test von 0.6.1.5. Die Prüfung des Codes fand keine Funktion, die erst Safari 26 kann; die Schrift kam per einmaligem `fetch` und blieb nach einer 503-Antwort für immer aus. |
| ADR-2026-11-12-M | **Beispiel-Animationen liegen als Text-Raster im Repo (`assets/animationen/`), nicht in der Firmware.** | Kostet keinen Flash und keinen Heap, prüft den Import mit, lässt sich in Excel bearbeiten. In der Firmware wären acht bis neun bewegte Animationen 60–100 KB Flash und zusätzlicher Code. |
| ADR-2026-11-12-N | **„Übertragung“ heißt nur noch Datenübertragung (Lauftext, Seite, Blocktext, Ambiente, Animation); kurze Steuerbefehle sperren nichts und zeigen keinen Hinweis. Während einer Übertragung fragt jedes Gerät etwa jede Sekunde.** | Wunsch aus dem Test von 0.6.1.6 (B1, B12). Steuerbefehle dauern etwa 1,3 s; dass Anfragen in dieser Zeit warten, merkt man nicht. Die schnellere Abfrage ist möglich, weil der Stapel während der Übertragung reichlich Reserve zeigte (4.472 Byte). |
| ADR-2026-11-12-O | **Der Rahmen hängt mit `position:fixed` an den echten Fensterkanten, Dokument und Body scrollen im Rahmen nicht.** Ersetzt die Höhe `100dvh` aus ADR-2026-11-12-K. | Auf dem echten iPhone (Web-App und Safari) war die Seite um die Statusleiste zu hoch und federte; Chromium zeigte das nicht. Feste Kanten hängen nicht davon ab, wie ein Browser `dvh` rechnet. |
| ADR-2026-11-12-P | **Die Oberfläche meldet einen hängenden ESP32 (keine Antwort seit 6 s) und einmal je Gerät einen Neustart durch den Wächter; dafür trägt der Status eine Startkennung und den Grund des letzten Neustarts.** | Wunsch nach dem Absturz vom 12.11.2026: man soll sehen, warum gerade nichts reagiert. Vor dem Neustart kann das hängende Board selbst nichts mehr senden; deshalb erkennt die Oberfläche das Schweigen (seit 0.6.1.6 antwortet das Board sonst auch während Übertragungen) und das Board liefert die Erklärung nach dem Start. |
| ADR-2026-11-12-Q | **Exporte sammeln in 512-Byte-Stücken auf dem Stapel und warten bei weniger als 14.000 Byte freiem Heap kurz.** Kein fester Puffer im RAM. | Im Test drückte `http.txt` das System-Minimum auf 992 Byte (eine HTTP-Stück je Zeile). Ein globaler Puffer hätte dauerhaft Heap gekostet. |
| ADR-2026-11-14-A | **Symbole sind eigene Pixelgrafiken aus `assets/symbole_0618.txt`; `tools/generate_assets.py` baut sie in Web und Firmware.** 85 Nummern (0–84), verworfene Nummern (48, 51–53, 56–58) bleiben leer reserviert, neue Symbole bekommen Nummern ab 64. | Felix liefert die Matrizen selbst; die Nummern der Bestandssymbole bleiben stabil, damit gespeicherte Texte (Emoji-Ersatzzeichen) weiter passen. Eine Textdatei als Quelle ist in Excel pflegbar und prüfbar. |
| ADR-2026-11-14-B | **Waagerecht zählt nur die belegte Breite (`bounds` / `symbolBounds()`), senkrecht die Lage in den 16 Zeilen; niedrigere Matrizen stehen senkrecht mittig.** Flaggen einheitlich 16 × 12. | Schmale Symbole sollen sich wie schmale Buchstaben verhalten; Excel schneidet leere Ränder ab, einzelne Matrizen enthalten aber bewusst leere Zeilen, die zum Bild gehören. |
| ADR-2026-11-14-C | **Symbole färben nur über eine ausdrücklich gesetzte Zeichenfarbe, nie über Zeilen- oder Gesamtfarbe; die Farbe reist als Stilzeichen U+009D (gilt für das nächste Zeichen) mit Farbmarke.** Färbekanal je Sprite (Herz, Auto, Zapfsäule, Pfeile, Strohhalm: alles; Augen: Kanal 1). | Symbole sollen nicht gelb werden, nur weil der Text gelb wird. Text ohne U+009D bleibt Byte für Byte wie bisher gültig. |
| ADR-2026-11-14-D | **Umkehren ist ein Stilzeichen U+009E am Zeilenanfang; Schalter im Texteditor (Blocktext je Seite), sperrt Symbole und „Zeichen gestalten“.** Eine Farbe für die ganze Fläche; Lauftext füllt mindestens 64 Spalten durchgehend. | Ganz einfach gehalten (Felix 14.11.2026). Die Firmware zeichnet den Text in den Puffer, der zuvor in der Zeilenfarbe gefüllt wird; Buchstabenpixel werden gelöscht. Web und Firmware sind per Paritätstest gleich. Strom und Wärme bei weißer Fläche sind höher. |
| ADR-2026-11-14-E | **„Auf der Tafel“ merkt sich die Firmware im NVS (Namensraum `rbon`, Schlüssel `k` und `i`) und meldet es im Status (`onKind`, `onId`); gesetzt wird erst nach erfolgreichem Auftrag, gelöscht beim Bearbeiten, Löschen, Überschreiben und Tafelwechsel.** | Alle Geräte sollen dieselbe Markierung zeigen und sie nach einem Neustart behalten; ein reiner Browser-Merker würde das nicht leisten. |
| ADR-2026-11-14-F | **Animationen zeigen sich standardmäßig als Raster; die bisherige Liste bleibt als Ansicht erhalten.** Die Import-Seite hat kein Dock. | Wunsch aus dem Test von 0.6.1.7 (viel Leere, Seite wirkte verloren). Die Listenansicht bleibt für Mehrfachauswahl und Sortieren. |
| ADR-2026-11-14-G | **Die Absturzspur trägt in der Phase `web_handler` die Route (`web:<uri>`); „Meine Tafel entfernen“ löscht die gespeicherte Tafel über `/api/sign/forget`.** | Der Hänger bei 209.799 ms im Test von 0.6.1.7 lag in einem Web-Handler, nicht in BLE; ohne Route bleibt der Ort unbekannt. D4: die eigene Tafel ließ sich bisher nicht abwählen. |
| ADR-2026-11-14-H | **Namen von Zusatzmotiven mit Anklang an eine Zigarettenmarke stehen nirgends mehr** (nicht im Menü, nicht als Suchbegriff, nicht in Doku, Code und Tests). Symbol 63 heißt „Ecke“; der Eintrag 48 entfällt. | Wunsch von Felix am 14.11.2026. |
