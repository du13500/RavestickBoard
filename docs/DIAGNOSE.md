# RavestickBoard · Diagnose und Fehlerprotokoll

**Fortgeschrieben 12.11.2026 für v0.6.1.7-dev (neuester Abschnitt oben). Die älteren Abschnitte beschreiben den Stand ihrer Version.**

## Diagnose-Ergänzung v0.6.1.7 – Exporte, Neustart-Grund im Status (12.11.2026)

**Gemessen in 0.6.1.6:** Stapel vor der ersten Webantwort 4.744 Byte, danach mindestens 4.472 Byte; kleinster Loop-Stapel 4.136 Byte; 129 Aufrufe, längster 12 ms. Ruhe-Heap mit zwei Geräten etwa 28,8 KB. `GET /api/http.txt` dauerte 3.481 ms und senkte das System-Minimum von 2.660 auf 992 Byte (Heap min 2.004, Block min 820). Wächter-Neustart in `ble_regNotify` nach etwa 65 Minuten (SYS-15).

**Neu in 0.6.1.7:**
- Zeile „Exporte: auf freien Heap gewartet (0.6.1.7): n×“. Zählt, wie oft ein Export vor einem Stück auf freien Heap gewartet hat. Ein paar sind normal; der Wert zeigt, dass die Bremse greift.
- `http.txt` und `ram.txt` kommen in Stücken zu 512 Byte statt Zeile für Zeile; der Inhalt ist unverändert.
- `/api/status` enthält `boot`, `up`, `restart` (`hang`/`crash`/leer) und `restartPhase`. Die Oberfläche zeigt nach einem Neustart durch den Wächter einmal je Gerät eine Meldung; die ausführliche Spur steht weiter unter „Absturzspur Vorlauf“.
- Kurze Steuerbefehle (Helligkeit, Tempo, Anzeigemodus, an/aus) zählen nicht mehr als Übertragung: In „Webantworten in Übertragungen“ tauchen nur noch Datenübertragungen auf.

## Diagnose-Ergänzung v0.6.1.6 – Webantworten während einer Übertragung, Stapel (12.11.2026)

**Gemessen in 0.6.1.5:** 1:44 h, 96 Aufträge, zwei Geräte, kein Neustart. `/api/anim/get` senkte das System-Minimum nicht mehr (0 Abfälle in `/api/*`, 0.6.1.4: 6); 503 nur viermal. Das System-Minimum von 2.632 Byte entstand 20–23 s nach dem Start beim Einbuchen des ersten Geräts, noch vor jeder Anfrage. Während einer großen Übertragung mit zwei Geräten etwa 22 KB frei, größter Block 7–10 KB; kleinster freier Stapel 3.656 Byte. Im 52-s-Grenztest stand **keine einzige HTTP-Zeile** in der Spur: Während der Übertragung wurde nichts beantwortet (B5/F9).

**Neu in 0.6.1.6:**
- Zeile „Webantworten in Übertragungen: an | Aufrufe n | Status n | Warteseite n | 409 n | längster Aufruf n ms“ (bei `RB_WEB_DURING_BLE 0`: „aus (wie 0.6.1.5)“). *Aufrufe* zählt jedes `web.handleClient()` innerhalb eines Auftrags (auch ohne Anfrage), die anderen Zahlen die tatsächlich beantworteten Anfragen.
- Zeile „Stapel vor der ersten Webantwort in einer Übertragung: n Bytes | danach (kleinster Wert seit Start): n Bytes“. **So lesen:** Der zweite Wert ist der wichtige. Liegt er deutlich über 1.000 Byte, reicht der Stapel; unter etwa 1.000 Byte ist es knapp (dann melden); ein Absturz mit Stapelüberlauf zeigt sich als Neustart mit Grund „Panic“ und einer Absturzspur in einer `tx_…`-Phase. Zum Vergleich steht weiter der kleinste freie Stapel des ganzen Laufs in der Diagnose.
- JSON-Diagnose: Objekt `txWeb` mit `on`, `calls`, `status`, `wait`, `busy`, `maxMs`, `stackBefore`, `stackAfter`.
- In der HTTP-Spur erscheinen Antworten während einer Übertragung mit 200 (Status), 503 (Warteseite) oder 409; 409 zählt dort als Fehler, ist aber gewollt.
- Neue Phasen der Wächter-Spur: `tx_wait_notify`, `tx_after_ack`, `ble_after_connect`, `job_end`, `job_retry` (bleiben während der Webantwort stehen).

## Diagnose-Ergänzung v0.6.1.5 – Befunde aus dem Hardwaretest von 0.6.1.4, vertagte Anfragen, Modus nach Animation (12.11.2026)

**Gemessen in 0.6.1.4:** Jeder Abruf-Teil von 3000 Byte senkte den freien Heap kurzzeitig um 13 bis 23 KB; alle Stufen des System-Minimums (bis 400 Byte) fielen in `/api/anim/get`; direkt nach einem Animationsversand mit zwei Geräten startete der Wächter in der Phase `anim_get` neu (frei 5.224 Byte). So liest man das in den Exporten: In der HTTP-Spur zeigt die Spalte „Heap vor/min/nach“ den Abfall je Anfrage, die Worst Cases nennen „System-Min-Abfall in Anfrage“ mit Pfad; im Seriallog stehen die Zeilen `[HTTPTRACE] … sysMin=alt->neu`.

**Neu in 0.6.1.5:**
- Zeile „HTTP-Anfragen wegen knappem Heap vertagt (503): n“ in der Textdiagnose. Sie zählt jedes 503 aus Heap-Gründen: Abruf einer Animation, lesende Listen-Routen und die Warteseite. Einige nach einem großen Sendeauftrag mit zwei Geräten sind erwartet; die Oberfläche wiederholt unsichtbar. Sehr viele (über 100) oder eine dauerhaft angezeigte Warteseite deuten auf einen dauerhaft niedrigen Heap; dann Diagnose, RAM- und HTTP-Spur exportieren (Status und Exporte sind nie gesperrt).
- In der HTTP-Spur erscheinen vertagte Anfragen mit Status 503 (sie zählen als Fehler).
- Ereignis (Kategorie `BLE`) „Anzeigemodus nach den Daten erneut gesetzt (vorher Animation oder unbekannt)“ beim ersten Text-, Seiten-, Block- oder Ambiente-Auftrag nach einer Animation oder nach dem Start; „… erneutes Setzen nicht bestaetigt“ ist als Fehler markiert, der Auftrag gilt trotzdem als gesendet.
- Ereignis (Kategorie `ANIM`) „Reihenfolge der Animationen konnte nicht gespeichert werden“, falls `order.bin` nicht geschrieben werden kann (die Liste fällt dann auf „aufsteigend nach Nummer“ zurück).
- Die Diagnose beginnt mit „RavestickBoard | Diagnose“; das WLAN heißt `RavestickBoard`.

## Diagnose-Ergänzung v0.6.1.4 – Befunde aus dem Hardwaretest von 0.6.1.3 und Abruf in Teilen (4.11.2026)

**Gemessen in 0.6.1.3 (Hardwaretest):** (1) Beim Abruf einer großen Animation (`/api/anim/get`) fiel der freie Heap von etwa 31 KB auf 1.640 Byte, der größte Block auf 820 Byte, das System-Minimum auf 352 Byte; eine Anfrage dauerte 5,5 s; in einem Lauf startete der Wächter das Board in der Phase `anim_get` neu (frei 3.120 Byte, System-Minimum 1.312 Byte). (2) Zwei weitere Wächter-Neustarts: Phase `ble_regNotify` und Phase `ble_connect` (BLE-Hänger; im Export vom 4.11.2026: Phase `ble_connect` bei 74.211 ms, Auftrag 3, frei 28.720 Byte, System-Minimum 9.464 Byte, die Geräte wurden vorher abgemeldet). (3) Im RAM-Verlauf eines späteren Exports (Laufzeit 5:43) sank das System-Minimum bei der **WLAN-Anmeldung** des ersten Geräts von 57.808 auf 41.656 Byte und bei der IP-Vergabe auf 9.984 Byte; später auf 7.400 und 3.920 Byte, davon einmal während `GET /api/anim/list` (459 ms, 7.400 auf 3.920). Bei einem BLE-Verbindungsaufbau fiel das System-Minimum auf 12.568 Byte (`BLE_LINK`). (4) Kleinster freier Stapel 4.856 Byte von 8 KB; Compiler: globale Variablen 79.452 Byte (24 %), Sketch 1.583.589 Byte (75 %); die Diagnose eines späteren Exports nennt 1.599.248 Byte (Abweichung vermutlich andere IDE-Einstellung, nicht geklärt).

**Neues Verhalten in 0.6.1.4:** `GET /api/anim/get` liefert höchstens 3000 Byte je Antwort; liegt der freie Heap bei Beginn unter 16.000 Byte, kommt 503 „Speicher knapp“ (die Weboberfläche wiederholt nach 300 ms, höchstens 30-mal). Das 503 erscheint **nicht** im Ereignisprotokoll; in der HTTP-Spur (`/api/http.txt`) steht es als Statuscode der Anfrage (503 zählt als Fehler). Zum Prüfen: nach einem Durchgang „große Animation auswählen, bearbeiten, speichern, löschen“ das Heap-Minimum, das System-Minimum und die Zeile „Worst Cases“ (Kleinster Heap in Anfrage, Pfad `/api/anim/get`) der HTTP-Spur mit dem Wert aus 0.6.1.3 vergleichen. Wiederholt die Oberfläche häufig, ist die Schwelle 16.000 Byte zu hoch oder der Heap bleibt dauerhaft knapp; beides wäre ein Messbefund, kein Fehler des Ablaufs.

## Diagnose-Ergänzung v0.6.1.3 – Prüfsumme, Lesefehler, Stapel (4.11.2026)

Neue Ereignisse (Kategorie `ANIM`; Fehler sind markiert): „Upload verworfen: Pruefsumme stimmt nicht“ (die Weboberfläche zeigt „Pruefsumme stimmt nicht …“, HTTP 422), „Upload verworfen: Datei beim Pruefen nicht lesbar“, „Senden abgebrochen: Pruefsumme der Animationsdatei stimmt nicht“ (beschädigte Datei, der Auftrag startet nicht), „Lesefehler bei der Vorabpruefung, Auftrag abgebrochen“ und die Statusmeldung „Animation: Lesefehler beim Senden (Paket n von m). Uebertragung abgebrochen.“, „Alte Animation nach unterbrochenem Ersetzen wiederhergestellt“ (beim Start, wenn nach einem Stromausfall nur `…rba.bak` da war), „Ersetzen fehlgeschlagen und die alte Animation liegt noch als .bak da (wird beim Start zurueckgeholt)“. Das Senden einer gespeicherten Animation heißt im Protokoll jetzt „Animation startet“; der Animationstest bleibt „Animationstest startet“.

**Stapel:** Die Textdiagnose enthält die Zeile „Kleinster freier Stapel (Loop-Task): … Bytes“, das JSON das Feld `minStack`, `ram.txt` „Stapel min=…“. Es ist der kleinste freie Stapel seit dem Start, gemessen am Arduino-Loop-Task, in dem die Webhandler laufen. Werte nahe 0 bedeuten Überlaufgefahr; ein Wert unter etwa 1000 Byte wäre ein Grund, Puffer von `onAnimPut` und Verwandten ins statische RAM zu legen. Zum Messen einmal alle Animationsaktionen durchspielen (speichern, bearbeiten, senden, löschen, Liste laden) und danach exportieren. Der Compiler gibt beim Bauen „Globale Variablen verwenden … Bytes“ aus; bitte mit notieren (Befund M4).

## Diagnose-Ergänzung v0.6.1.0 – Animationen (3.11.2026)

Neue Ereignisse (Kategorie `ANIM`) im Diagnoseprotokoll: „Unfertiger Animations-Upload entfernt“ (beim Start, wenn `up.tmp` übrig war), „Animation gespeichert“ (ID, Bildzahl, Dateigröße) und beim Senden aus einer Datei (ID, Name, Bildzahl, Zeit je Bild). Umbenennen, Duplizieren und Löschen schreiben kein eigenes Ereignis. Seit 0.6.1.2: „Nur senden“ schreibt beim Abschluss des Uploads ein Ereignis (ID 60000, Bildzahl) und löscht `send.rba` nach dem Auftrag ohne Ereignis; das Bearbeiten (Überschreiben) schreibt „Animation ersetzt, ID=…“; eine Kurzwahl vom Typ 4 schreibt dasselbe Ereignis wie „Senden“ in der Liste. Ein Senden aus der Datei erscheint wie der Animationstest als Auftrag `ANIM` mit den Phasen der Übertragung; die Antwortzähler (`ackOk`, `ackNak`, `ackFatal`, `ackOther`) zählen dieselben Pakete. Bei einer Störung zuerst nachsehen: (1) meldet `GET /api/anim/list` `ready:false` (Dateisystem nicht eingerichtet), (2) steht in der Liste ein Eintrag mit `broken` (Datei beschädigt), (3) letzte Phase und Paketnummer des Wächter-Neustarts, falls das Senden hing (79 Bilder brauchen etwa 55 s, der Wächter wird je Paket gefüttert), (4) Heap-Minimum während des Hochladens und Sendens, besonders mit zwei Geräten. `animActive` im Status zeigt, was zuletzt gesendet wurde.

## Diagnose-Ergänzung v0.6.0.0/0.6.0.1 – Antwortcodes der Tafel und Animationstest (3.11.2026)

Die Tafel bestätigt jedes Datenpaket mit einer Antwort (`01 | Länge | Befehl 00 Nr. Status | 03`). Seit 0.6.0.0 liest die Firmware den Status und zählt ihn: im JSON `ackOk` (Status 0), `ackNak` (6, Prüfsummenfehler), `ackFatal` (1–5) und `ackOther` (nicht lesbar oder fehlend), im Textbericht als Zeile „Antwortcodes der Tafel“. Zeigt `ackOther` bei allen Aufträgen hohe Werte, liefert die Tafel die Antworten nicht in der erwarteten Form oder zu spät; das ist ein Befund, kein Fehler des Auftrags.

Beim **Animationstest** (Ereignis `ANIM`) steht im Protokoll zuerst die Anfrage („Test Balken, 16 Frames, 60 ms, Modus danach: keep“). Lehnt die Tafel ein Paket ab, steht die Meldung „Tafel lehnt Paket n von m ab: Code 0x04 (Datenlänge)“ in der Statusanzeige und im Protokoll; bei Status 6 steht „Paket n wird nach Pruefsummenfehler erneut gesendet“. Der absichtliche 80-Frame-Test soll genau die Ablehnung mit Code 0x04 zeigen, nach Adams Erfahrung schon beim ersten Paket („Paket 1 von …“). **Bestehende Aufträge** (Text, Seiten, Blockfolge, Ambiente) werten die Codes nicht aus, ein Status ungleich 0 ändert dort nichts am Ablauf.

Für den Fehlerbericht nach einem Animationstest bitte angeben: Muster, Frameanzahl, Zeit je Frame, Modus danach, die Zähler der Antwortcodes vor und nach dem Test, was die Tafel zeigt (nichts / Standbild / Animation / ERROR) und was nach dem Aus- und Einschalten der Tafel zu sehen ist.

## Diagnose-Ergänzung v0.3.4 – Testbare Moduswerte (25.10.2026)

Der neue Modus-Dropdownwert wird vor dem BLE-Auftrag auf genau `0x01` bis `0x08` geprüft und als **Modusparameter des Steuerbefehls `0x06`** im Diagnose-Log festgehalten. Vor einem Auftrag melden Start- und `Auftrag:`-Zeile jetzt Moduswechsel statt „Helligkeit“; der TXT-Export erhält einen aus `FW_VERSION` gebildeten Dateinamen. Bei Safari-Refresh soll `Cache-Control: no-store` die aktuelle v0.3.4-Oberfläche ausliefern. **Noch keine Hardwarebestätigung für die sechs neuen Effekte**; sichtbaren Anzeigemodus getrennt von `JOB OK` notieren. Vorherige v0.3.3 bleibt Rückfallversion.

## Diagnose-Ergänzung v0.3.3 (25.10.2026)

Der seriellen HTTP-Logzeile für Lauftextaufträge werden **dekodierte Zeichen, Bildspalten und Datenbytes** hinzugefügt. Bei zu großer berechneter Datenmenge erfolgt ein HTTP-400-Abbruch **vor dem BLE-Auftrag**; der Text bleibt im Browser bestehen. Das Webinterface zeigt eine rote/fette Byte-Auslastung und deaktiviert „Lauftext senden“. Eine spätere dynamische RAM-Allokation kann trotzdem scheitern und erscheint wie bisher als `[RAM] Bildpuffer ... fehlgeschlagen` sowie `JOB FEHLER`. Eine `JOB OK`-Meldung beweist lediglich erfolgreiche Paketübertragung und Benachrichtigungen, **nicht** die Bildübernahme durch die Tafel. Den tatsächlich sichtbaren Effekt stets getrennt protokollieren. **Hardware-Nachtrag:** v0.3.3 wurde am 25.10.2026 erfolgreich getestet; 240 BLE-Pakete und 30.695 B über 52.937 ms mit `JOB OK`, tatsächlich auf der Tafel angezeigt.

## Neuer Diagnosebefund: Bildtransfer ≠ Bildanzeige (25.10.2026)

Beim v0.3.2-Korrektur-2-Praxistest wurden teilweise alle BLE-Pakete quittiert und `JOB OK` gemeldet, obwohl die CoolLEDX-Tafel keine neue Grafik anzeigte (etwa 320 gemischte Symbole, 31.853 B / 249 Pakete). Deshalb den Status **„vollständig gesendet“** nicht mit **„Tafel zeigt neue Grafik“** gleichsetzen. Ein wirkliches Display-Abschluss-ACK ist bislang nicht nachgewiesen. Gleichzeitig können sehr lange Symbolfolgen auf dem Controller bereits an einer fehlgeschlagenen zusammenhängenden RAM-Allokation scheitern. Für vollständige Messwerte und Grenzideen siehe [`archive/ENTWICKLUNGSSTAND_v0.3.2_2026-10-25.md`](archive/ENTWICKLUNGSSTAND_v0.3.2_2026-10-25.md).

## Aufrufen und Exportieren

1. Mit `RavestickBoard` verbinden (bis 0.6.1.4 `CoolLED1248`) und `http://192.168.4.1` öffnen.
2. Bereich **Diagnose / Log** aufklappen und bei Bedarf aktualisieren.
3. **„Log kopieren“**: seit v0.1.2 bevorzugt. Wegen unverschlüsseltem HTTP kann die Clipboard-API auf iPhone/Safari eingeschränkt sein; der Browser versucht Fallback bzw. bietet manuellen Text. **Der Safari-Fallback ist nicht in sämtlichen Konstellationen abgenommen.**
4. Alternativ **TXT herunterladen**. Dieser Weg wurde bereits mit v0.1.1 auf dem iPhone bestätigt.

| Schnittstelle | Inhalt |
| --- | --- |
| `GET /api/diagnostics` | Kleine JSON-Übersicht mit jüngsten Ereignissen |
| `GET /api/diagnostics.txt` | Vollständiger TXT-Bericht mit bis zu **56** RAM-Ereignissen |
| `GET /api/status` | Status laufender bzw. beendeter Aufträge |

## Erfasste Informationen

- Firmware-/Buildstand, Resetgrund (einschließlich Klartext für **USB-Reset**), Laufzeit und `millis()`-Zeitbasis.
- Freier/minimal freier Heap, größter allokierbarer RAM-Block, Sketchgröße, laufende **App-Partitionsgröße** und rechnerisch freie App-Bytes.
- WLAN-AP-Adresse und Zahl der Clients, nicht jedoch WLAN-Passwort.
- BLE-Verbindungsversuche, Erfolge, Trennungen, Schreiben, Notifications, Timeout- und Fehlerzähler.
- Transferstatistik (Pakete/Bytes, Dauer, Erfolg/Fehlschlag), HTTP-Aufträge und abgewiesene Aufträge.
- Seit **v0.2.0**: gespeicherte Seiten, Playerstatus, Seitenübertragungen OK, NVS-Seitenspeicherungen und automatische Seitenwechsel.
- Begrenzt gespeicherte Ereignisse als relativer Zeitverlauf seit Boot; jeweils mit Kategorie und Beschreibung.

## Interpretation und bekannte Grenzen

- **RAM-only:** Neustart und Stromausfall löschen den Diagnose-Ringpuffer und die laufenden Fehlerzähler. **NVS-Blockseiten bleiben hingegen erhalten.**
- **Schreiben ≠ Anzeigen:** Ein akzeptierter `write-without-response`-Auftrag beweist noch keine Bilddarstellung. Notification-Empfang, Transfer-Ende und sichtbares Display separat prüfen.
- **Blockierende BLE-Übertragung:** Während eines synchronen Transfers kann der Webserver für einige Sekunden verzögert reagieren.
- **Kein eingebundenes SPIFFS/LittleFS:** Die Anzeige kann den tatsächlichen belegten Dateisystemspeicher nicht bestimmen. Angaben zur App-Partition sind keine freien RAM-Bytes.
- **Keine Echtzeituhr:** Ereignisse nutzen Millisekunden seit Boot, nicht Uhrzeiten. `millis()` läuft als 32-Bit-Zähler nach rund 49,7 Tagen über.
- **Verbindungskonflikt:** Eine Fehlermeldung kann auf die Original-App als mögliche Ursache hinweisen, aber der ESP32 kann deren aktive Verbindung aus einem Timeout nicht sicher nachweisen.
- **Datensparsamkeit:** TXT-Export enthält absichtlich keine Anzeigeinhalte, Passwörter oder BLE-MAC-Adressen. Trotzdem Fehlerberichte vor öffentlichem Teilen kurz prüfen.

## Praktisch beobachteter Stand

**v0.1.1:** Der Nutzer testete u. a. fünf erfolgreiche Textaufträge, fünf Verbindungen, 20 BLE-Notifications, keine Schreib-/Timeoutfehler; nach Trennung der konkurrierenden Original-App war der Controller ohne Neustart wieder einsatzbereit. Diagnose und TXT-Export funktionierten auf dem iPhone.

**v0.2.0 Korrektur 1:** Seitenplayer, NVS-Blockseiten und reale mehrfache Uploads sind vom Nutzer bestätigt. Eine gesonderte Abnahme **sämtlicher neuer v0.2.0-Diagnosefelder** wurde noch nicht dokumentiert.

## Empfohlener Fehlerbericht

1. Firmwareversion, Gerät, Uhrzeit/Situation, Betriebsdauer notieren.
2. **Vor dem Reset** Diagnose kopieren oder TXT speichern.
3. Betroffene Seite/Programm, gewünschtes vs. tatsächliches Verhalten und Foto/Screenshot angeben.
4. Bei BLE-Fehlern festhalten, ob die Original-App gleichzeitig verbunden war.
5. Bei reproduzierbarem Fehler eine Testfolge mit möglichst wenigen Schritten dokumentieren.

**Offen für später:** persistenter kritischer letzter Fehler (nur nach Flashverschleiß-Abwägung), weitere Timeout-/NAK-/ACK-Diagnose, Langzeit-/Heap-Test, laufende Grafikanimationen und deren Speicher-/Transferstatistik.

## 24.10.2026 · Entwicklungszusatz v0.3.0

Separate Steuerjobs `BRIGHTNESS`, `SPEED`, `MODE` verwenden kurze BLE-Kommandos und für ca. 2,5 Sekunden nach dem letzten Kommando eine bestehende Verbindung. Die eigentliche Wirkung auf der Original-Tafel, konkurrierende App-Verbindungen und der BLE-Timeoutpfad müssen erneut auf Hardware getestet werden. Die Diagnose bleibt RAM-only. Dieser Abschnitt ist noch kein Hardwaretestbericht.


## Für den 600-Zeichen-Versuch unter v0.3.2

Bei jeder Teststufe 80, 100, 150, 200, 300, 400, 500, 600 bitte erfassen: (1) Anzahl Zeichen laut Editor, (2) angegebene Text-Payload-Bytes, (3) BLE-Paketzahl, (4) `JOB OK` bzw. Fehler, (5) tatsächliche sichtbare Darstellung auf der LED-Tafel. Ein `JOB OK` besagt, dass die Paketkommunikation erfolgreich verlief, nicht zwingend, dass das Board den Text vollständig anzeigt.

**Auffälligkeiten aus v0.3.1:** Einzelne BLE-Verbindungsfehler konnten durch den nächsten Verbindungsversuch überwunden werden; beim automatischen Seitenplayer stoppte ein Verbindungsfehler hingegen die Wiedergabe. Begrenzte Auto-Retry-Strategie bleibt auf später verschoben.

## WLAN-Startfehler unter v0.3.2 Korrektur 1 (25.10.2026)

Nutzerlog: Nach `Seiten geladen: 10` scheiterte der AP-Start mit `wifi:alloc pp wdev funcs fail`; anschließend meldete der Treiber beim Aufräumen `0x3001`. Diese Zeilen sind mit **zu wenig freiem Arbeitsspeicher beim Initialisieren des WLAN-Treibers** vereinbar. In Korrektur 1 waren allein die beiden globalen Bild-/Payload-Puffer mit zusammen 122.507 Bytes reserviert.

Korrektur 2 vermeidet diese globale Vorbelegung. Im seriellen Monitor erscheinen vor BLE, nach BLE/NVS und nach WLAN jetzt `[RAM]`-Zeilen mit freiem Heap und größtem allokierbaren Block sowie beim Senden Puffergröße und Rest-Heap. Bei fehlgeschlagenem WLAN-Start wird der HTTP-Webserver nicht als bereit gemeldet.

**NVS-Warnung:** Zur Diagnose **keinen Flash-Erase** und kein NVS-Reset ausführen. Das Firmwareupdate mit der üblichen Partitionseinstellung bewahrt das Seitenformat, sofern die IDE nicht auf `Erase All Flash` gestellt wurde. Bei weiterer Störung v0.3.1 als funktionierenden Rückfallstand verwenden.
