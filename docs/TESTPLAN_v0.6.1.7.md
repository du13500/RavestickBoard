# RavestickBoard · Hardwaretest v0.6.1.7-dev (Rahmen auf dem iPhone, Hinweis nur bei Datenübertragungen, Neustart-Meldung)

**Stand: 12.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.6 (liegt in `archive/`). 0.6.1.6 lief auf der Hardware; der Stapel reichte während der Übertragung klar (4.472 Byte). Nicht in Ordnung waren der Rahmen auf dem echten iPhone (Seite zu hoch, federt) und der Hinweis „Übertragung läuft …“ (zu lange, auch bei Dock-Befehlen). Dazu kam ein Wächter-Neustart nach einem Bluetooth-Hänger. **Hauptfragen dieses Tests:** Sitzt der Rahmen jetzt auf dem iPhone (Abschnitt A), erscheint der Hinweis nur noch bei echten Übertragungen (B), und siehst du, wenn der ESP32 hängt und neu startet (C)? Die Tabelle gibt es auch als Excel-Datei; Ergebnis bitte dort eintragen.

## Vorbereitung

1. JSON-Backup ziehen, 0.6.1.6 als Rückfallversion aufbewahren.
2. `firmware/RavestickBoard_v0_6_1_7/RavestickBoard_v0_6_1_7.ino` öffnen, **alle sieben Dateien** im Sketch-Ordner lassen, Einstellungen unverändert. `RB_TEST_HANG` steht auf 1 (für Abschnitt C).
3. iPhone 13 Pro und iPhone SE bereitlegen, jeweils als Web-App (Homescreen) **und** in Safari. Laptop.
4. Nach dem Test Diagnose, `ram.txt` und `http.txt` exportieren; Seriallog mitlaufen lassen.

## A. Rahmen auf dem iPhone

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| A1 | Sketch kompilieren | kompiliert (neu: `esp_random.h`); Zeile „Globale Variablen …“ **notieren** (0.6.1.6: 83.504 Byte) | | |
| A2 | iPhone SE als Web-App: Kurzwahl, Bibliothek, Programme, Animationen, Ambiente öffnen | Kopfzeile ganz zu sehen, Bedienfeld ganz unten sichtbar, ohne zu scrollen | | |
| A3 | Auf diesen Seiten mit dem Finger außerhalb der Listen nach oben und unten ziehen | die Seite bewegt sich nicht (kein Federn) | | |
| A4 | In Bibliothek, Programmen und Animationen in der Liste scrollen | nur die Liste scrollt, Kopf und Bedienfeld bleiben stehen | | |
| A5 | iPhone SE in Safari: A2 bis A4 | wie A2 bis A4 (Safari-Leisten verschieben nichts) | | |
| A6 | iPhone 13 Pro als Web-App und in Safari: A2 bis A4 | wie oben, Kopf nicht unter der Kamera-Aussparung | | |
| A7 | Ambiente auf dem SE | alle sieben Farben inklusive Weiß sichtbar, Bedienfeld darunter | | |
| A8 | Texteditor, „Programm bearbeiten“, Einstellungen, Diagnose | scrollen normal wie bisher | | |
| A9 | Laptop: Kurzwahl, Bibliothek, Animationen | wie bei 0.6.1.6 (Seitenleiste links, Bedienfeld unten so breit wie die Fläche) | | |

## B. Hinweis „Übertragung läuft …“

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Zwei Geräte. Am Laptop Helligkeit und Tempo bewegen, Anzeige-Tasten tippen, Anzeige aus und an | auf **keinem** Gerät erscheint „Übertragung läuft …“ | | |
| B2 | Am Laptop eine große Animation senden, aufs iPhone schauen | Hinweis erscheint wie bei 0.6.1.6, Knöpfe gesperrt | | |
| B3 | Ende der Übertragung abwarten | Hinweis verschwindet auf beiden Geräten nach etwa **einer** Sekunde (0.6.1.6: etwa 3 s) | | |
| B4 | Dauer der Übertragung der großen Animation stoppen | Dauer **notieren** (0.6.1.5: 79 Bilder 52 s) | | |
| B5 | Lauftext und Blocktext senden | Hinweis bei beiden, verschwindet zügig | | |
| B6 | Diagnose: „Stapel vor der ersten Webantwort … \| danach …“ | Werte **notieren** (0.6.1.6: 4.744 / 4.472 Byte) | | |

## C. Wenn der ESP32 hängt

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | iPhone auf der Kurzwahl. Am Laptop im Browser `http://192.168.4.1/api/test/hang` aufrufen (absichtlicher Hänger zum Testen) | nach etwa 6 s auf dem iPhone rötlich „ESP32 antwortet nicht …“ auf dem Bedienfeld, Knöpfe gesperrt | | |
| C2 | Warten | nach etwa 25 s startet der ESP32 neu; das iPhone verbindet sich wieder mit dem WLAN (kann ein paar Sekunden dauern) | | |
| C3 | Sobald der ESP32 wieder antwortet | Hinweis verschwindet; **einmal** erscheint die Meldung „Der ESP32 hing (…) und hat sich neu gestartet. Der letzte Auftrag wurde nicht ausgeführt – bitte noch einmal senden.“ | | |
| C4 | Am Laptop die Oberfläche neu laden | auch dort einmal die Meldung; danach bei erneutem Laden keine weitere | | |
| C5 | Diagnose: „Absturzspur Vorlauf“ | Phase des Test-Hängers, „vom Hang-Waechter neu gestartet“ | | |
| C6 | Falls im Test ein echter Bluetooth-Hänger auftritt | Meldung nennt „Bluetooth hing beim Verbinden mit der Tafel“ und die Phase; Uhrzeit und was du gerade gemacht hast **notieren** (SYS-15) | | |

## D. Kleinigkeiten

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Bibliothek: „Backup exportieren“ (unten) | Knopf zeigt „Backup wird erstellt …“ (Icon pulsiert, Knopf gesperrt), danach kommt die Datei | | |
| D2 | Diagnose, `ram.txt` und `http.txt` nacheinander exportieren, danach `ram.txt` noch einmal | Inhalt wie bisher; im zweiten `ram.txt` oben „min=…“ **notieren** (0.6.1.6: fiel beim HTTP-Export auf 992 Byte) | | |
| D3 | Diagnose: Zeile „Exporte: auf freien Heap gewartet“ | Wert **notieren** | | |
| D4 | Einstellungen → LED-Tafel → Suchen | Knöpfe „Als meine Tafel speichern“ (Diskette), „Jetzt nutzen“ (zwei Kreise) bzw. „Meine Tafel nutzen“ (Tower) mit Icon und Text | | |
| D5 | Anzeige aus/ein im Texteditor (Bereich „LED-Anzeige“), „Auswahl aufheben“ (Laptop, zwei Einträge mit Strg-Klick), Symbolauswahl im Texteditor schließen | nur Icons (Auge, Auge zu, Kreuz), Tooltip am Laptop | | |
| D6 | Bibliothek | keine Kurzwahl-Zeile „Belegen/Freigeben“ (war ohnehin unsichtbar); Kurzwahlen im Dialog funktionieren wie bisher | | |
| D7 | Ein altes JSON-Backup mit Kurzwahlen importieren (optional) | Einträge und Kurzwahlen kommen zurück | | |

## E. Gesamt

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Diagnose: kleinster freier Stapel, minimal freier Heap | **notieren** | | |
| E2 | Neustarts außer C1 | keiner; sonst Phase und was du gerade gemacht hast | | |
| E3 | Gesamteindruck, Wünsche | frei | | |
