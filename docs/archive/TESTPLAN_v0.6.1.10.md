# RavestickBoard · Hardwaretest v0.6.1.10-dev (Bluetooth-Unterbau NimBLE statt Bluedroid)

> **Archiviert (17.11.2026).** Ergebnis: von Felix kompiliert (15.11.) und am 16.11.2026 auf der Hardware getestet, keine ungeplanten Fehler; getestet mit NimBLE-Arduino 2.5.2 (die Angabe „Stand der Entwicklung: 2.6.0“ unten war eine Annahme). Der Text darunter ist der Stand vor dem Test. Nachfolger: `docs/TESTPLAN_v0.6.1.11.md`.

**Stand: 15.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.9 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.6.1.10.xlsx` bereit (zum Ausfüllen am Handy oder Laptop). **In 0.6.1.10 ändert sich nur der Bluetooth-Unterbau**, nichts an Oberfläche, Bedienung oder Ablauf. **Am Rechner geprüft (nicht auf der Hardware):** Entscheidungslogik von Vor-Scan, Tafelsuche und Hilfsdatei mit Attrappen der NimBLE-Klassen, statische Prüfungen des Sketches, Browsertests unverändert. **Arduino-Compile gegen die echte NimBLE-Bibliothek, Tafel, iPhone und Safari sind noch nicht geprüft.** *Hauptfragen:* Verbindet und sendet das Board wie bisher (Abschnitte C bis E), und wie viel Speicher ist jetzt frei (Abschnitt B)?

## Vorbereitung

1. JSON-Backup ziehen, 0.6.1.9 als Rückfallversion aufbewahren (sie läuft ohne die neue Bibliothek).
2. Arduino IDE → Bibliotheksverwalter → **NimBLE-Arduino** (h2zero) installieren; Versionsnummer notieren. Dann `firmware/RavestickBoard_v0_6_1_10/RavestickBoard_v0_6_1_10.ino` öffnen, **alle acht Dateien** im Sketch-Ordner lassen, Einstellungen unverändert. `RB_TEST_HANG` steht auf 1 (für Schritt G1).
3. iPhone 13 Pro und Laptop bereitlegen, dazu die Tafel (mit Reichweite); die Original-App für Schritt C3 bereithalten.
4. Nach dem Test Diagnose, `ram.txt` und `http.txt` exportieren; Seriallog mitlaufen lassen.
5. Schritte mit „notieren“: den Wert in die Bemerkung schreiben; die Vergleichszahlen aus 0.6.1.9 stehen jeweils dabei.

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| A1 | In der Arduino IDE die Bibliothek **NimBLE-Arduino** (von h2zero) über den Bibliotheksverwalter installieren und die **Versionsnummer notieren**. Neueste Version 2.x nehmen. | Bibliothek ist installiert. Version **notieren** (Stand der Entwicklung: 2.6.0; getestet wurde dieser Sketch am Rechner nicht gegen die echte Bibliothek). | | |
| A2 | Sketch `RavestickBoard_v0_6_1_10.ino` öffnen (alle **acht** Dateien im Ordner lassen, neu ist `RavestickBoard_Ble.h`), kompilieren. | Kompiliert. Falls eine Fehlermeldung mit „NimBLE“, „onResult“, „connect“ oder „subscribe“ kommt: **komplett kopieren** (das wäre ein Unterschied zwischen Bibliotheksversionen; Notausgang: `#define RB_NIMBLE_V1 1` ganz oben in den Sketch, dann Bibliothek 1.4.x). Die Zeilen „Der Sketch verwendet …“ und „Globale Variablen …“ **notieren** (0.6.1.9: 1.638.885 Byte, 84.016 Byte). | | |
| A3 | Flashen, mit dem WLAN `RavestickBoard` verbinden, die Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.6.1.10-dev (Diagnose). | | |

## B. Speicher (Hauptfrage dieses Tests: Wie viel ist frei, seit der Bluetooth-Unterbau gewechselt hat?)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | Diagnose öffnen, Abschnitt „START-AUFTEILUNG“ ansehen. Die Werte „Vor BLE-Init“ bzw. „Start“ und „Nach BLE-Init“ **notieren**. | Bluetooth braucht deutlich weniger als bisher. (0.6.1.9: 187.180 → 114.348 Byte, also etwa 73 KB für Bluetooth.) Die Zeile „BLE-Stack=NimBLE“ steht in der Diagnose. | | |
| B2 | In der START-AUFTEILUNG den Wert „Nach WLAN-AP“ ablesen. | **Notieren** (0.6.1.9: 54.444 Byte frei). Erwartung: deutlich mehr. | | |
| B3 | Mit einem Gerät verbunden, einige Sekunden nichts tun, dann Diagnose: freier Heap. Danach mit zwei Geräten verbunden dasselbe. | Beide Werte **notieren** (0.6.1.9: etwa 33 KB mit einem, etwa 28 KB mit zwei Geräten). Erwartung: mehr. | | |
| B4 | Zehnmal zwischen Animationen, Bibliothek und Texteditor wechseln, dann Diagnose: kleinster freier Heap und System-Minimum. | **Notieren** (0.6.1.9: System-Minimum nur **160 Byte**). Erwartung: deutlich höher; kein Neustart. | | |

## C. Verbinden und Vor-Scan (soll sich genau wie bisher anfühlen)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | Tafel einschalten (nicht mit der Original-App verbunden), Lauftext senden. Danach Diagnose-Log ansehen. | Text läuft. Im Log: „Vor-Scan: Tafel gesehen nach … ms, … Geräte gehört, Signal … dBm“, „Verbindung hergestellt“, „MTU=… Text-Payload=… Pakete=…“, „Verbindung getrennt“. Alle Zahlen **notieren** (Vor-Scan-Zeit, Geräte, dBm, MTU; MTU war bisher 247 oder knapp darunter). | | |
| C2 | Tafel ausschalten, etwas senden. | Meldung „LED-Tafel nicht gefunden …“, im Log „Tafel im Vor-Scan nicht gesehen“, **kein** Verbindungsversuch. Dauer bis zur Meldung **notieren** (etwa 3 s). | | |
| C3 | Tafel einschalten, mit der Original-App verbinden, dann vom Board aus senden. | Meldung, dass die Tafel nicht erreichbar bzw. nicht gefunden ist; kein Hänger, kein Neustart. Dauer **notieren**. | | |
| C4 | Tafel wieder frei machen und sofort noch einmal senden. | Läuft durch. | | |
| C5 | Zehn Lauftexte direkt hintereinander senden (immer sofort nach dem Ende des vorherigen). | Alle zehn kommen an. Wenn einer mit „Verbindungsversuch fehlgeschlagen“ endet: Log-Zeilen davor **notieren** (Beobachtung SYS-15: Verbindungsfehler direkt nach dem Vor-Scan). | | |
| C6 | Menü → Meine Tafel → „Tafel suchen“ (mit eingeschalteter Tafel in der Nähe). | Die Tafel erscheint mit Name und Signalstärke; fremde Bluetooth-Geräte nur, wenn der Schalter für alle Geräte gesetzt ist. Die Suche dauert etwa 4 s. | | |
| C7 | Eine andere Tafel (falls vorhanden) einrichten und darauf senden; danach wieder auf die eigene umstellen. | Verbinden klappt mit beiden. (Nur testen, wenn eine zweite Tafel greifbar ist; sonst „Nicht getestet“.) | | |

## D. Senden: jede Auftragsart einmal (Ergebnis wie in 0.6.1.9)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Einen kurzen Lauftext senden, danach einen sehr langen (über eine Bildschirmbreite hinaus). | Beide laufen. Beim langen: Dauer **notieren**. | | |
| D2 | Einen Blocktext mit mehreren Seiten senden. | Alle Seiten kommen in der richtigen Reihenfolge an. | | |
| D3 | Einen langen Blocktext mit Symbolen und Farben senden (sodass das Bildband in Kacheln gesendet wird). | Kommt vollständig und unverfälscht an. | | |
| D4 | Animation „Taxi long“ (11 Frames) senden. | Läuft. Dauer **notieren** (0.6.1.9: 9,3 s). | | |
| D5 | Animation „flame“ (30 Frames) senden. | Läuft. Dauer **notieren** (0.6.1.9: 20,7 s). | | |
| D6 | Ambiente: eine Farbe senden. | Tafel zeigt die Farbe. | | |
| D7 | Ein-/Ausschalten senden, beide Richtungen. | Tafel geht aus und wieder an. | | |
| D8 | Anzeigemodus wechseln; Helligkeit ändern; Tempo ändern. | Alles wirkt sofort wie bisher. | | |
| D9 | Ein Programm senden. | Läuft in der richtigen Reihenfolge durch. | | |
| D10 | Eine Kurzwahltaste drücken. | Wie bisher. | | |

## E. Abbruch mitten in der Übertragung

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Die „flame“-Animation senden und nach etwa 5 s die Tafel ausschalten oder aus der Reichweite nehmen. | Nach kurzer Zeit eine Meldung; im Log „keine Notification zum Paket …“ o. ä. Kein Neustart. Die Markierung „auf der Tafel“ ist danach gelöscht, die Tafel zeigt das Herstellerbild „CoolLED“. Dauer bis zur Meldung **notieren**. | | |
| E2 | Tafel wieder einschalten und denselben Eintrag senden. | Läuft durch. | | |
| E3 | Während einer Übertragung am zweiten Gerät die Webseite bedienen. | Wie in 0.6.1.9: Antworten kommen, Sendeknöpfe sind gesperrt, es gibt keinen Neustart. | | |

## F. Speicher unter Last und Dauerlauf

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | Nach den Sendeschritten oben Diagnose öffnen: kleinster freier Heap und System-Minimum. | **Notieren** (0.6.1.9: System-Minimum 160 Byte). | | |
| F2 | Etwa 30 Minuten mit zwei Geräten abwechselnd senden, Bibliothek, Animationen und Texteditor benutzen. | Kein ungeplanter Neustart. Wenn doch: Diagnose → Absturzspur, Phase **notieren**. | | |

## G. Offene Punkte aus 0.6.1.9

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| G1 | Am Laptop `http://192.168.4.1/api/test/hang` aufrufen; iPhone beobachten. | Hinweis „ESP32 antwortet nicht …“ nach etwa 5 bis 8 s; nach dem Wächter-Neustart die Meldung „Der ESP32 hat sich neu gestartet …“. Sekunden **notieren**. (K1 aus 0.6.1.9.) | | |
| G2 | Eine Datei JSON-Backup exportieren und wieder importieren. | Einträge, Programme und Kurzwahlen kommen zurück; Symbole stehen richtig. (K2 aus 0.6.1.9, dort noch nicht getestet.) | | |
| G3 | Mit dem Laptop verbinden, während das iPhone verbunden ist; danach Diagnose-Zeile „WLAN Clients“ ansehen. | Klappt (Limit sind zwei Geräte). Zahl und Endungen **notieren**. (J3 aus 0.6.1.9.) | | |
| G4 | Eine halbe Stunde nebenbei die Zeile „WLAN Clients“ ab und zu ansehen. | Wechselt eine Endung (Station verbindet neu), **notieren** wann. (J4 aus 0.6.1.9.) | | |

## H. Gesamt

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | Neustarts außer dem Test-Hänger G1. | Keiner; sonst Phase und was du gerade getan hast notieren. | | |
| H2 | Gesamteindruck: fühlt sich Verbinden und Senden schneller, langsamer oder gleich an? | Frei. | | |
