# Hinweise für Audits und Reviews (RavestickBoard)

**Stand: 27.11.2026 (v0.8.3-dev; gegenüber 0.8.2 nur Weboberfläche: 1:1, Bahn, Verlauf, Formen, Mischfarben).** Diese Datei ist für Reviewer, menschliche wie KI-gestützte: Sie sagt, was bewusst so ist, was bekannt offen ist, was ein Review hier nicht ausführen kann und welche Befunde schon geprüft sind. Sie ersetzt keine Prüfung; wer etwas anders sieht, soll es melden. Aber bitte erst hier nachlesen, damit Zeit auf Neues geht. Wird bei jedem Build fortgeschrieben; Entscheidungen mit Begründung stehen in [ENTSCHEIDUNGEN.md](ENTSCHEIDUNGEN.md), Pläne in [ROADMAP.md](ROADMAP.md).

## 1. Bindende Entscheidungen (nicht als Fehler melden)

- **Das WLAN-Passwort ist im Quelltext als Standard hinterlegt** (`Banane1248!`), die Tafel ist ein Einzelgerät im eigenen WLAN-Netz (Access-Point) für einen Festivaltotem. Vor dem Einsatz unter Fremden soll in den Einstellungen ein eigenes Passwort gesetzt werden. Das ist Absicht (siehe ENTSCHEIDUNGEN, WLAN-Passwort) und kein Geheimnisleck.
- **Die Weboberfläche ist eine einzige Datei** (`web/index.html`, gepackt in `RavestickBoard_WebUI.h`). Die Aufteilung in Module ist verschoben (eigener Qualitätsstand nach dem Hardwaretest), kein Versehen.
- **„Frame/Frames“ bleibt in der Oberfläche** (ADR-2026-11-26-P); „Bild/Bilder“ steht für das große Ausgangsbild.
- **Ein Test-/Entwicklungsprofil hat bewusst einen Hang-Auslöser** (RB-002), den der Hardwaretest nutzt. Für ein Festival-Build gilt `RB_RELEASE 1`.
- **Das Limit von 40 Animationen** (`RB61_MAX_ANIMS`) und die Animationsgröße (64 × 16, höchstens 79 Frames, eine Zeit je Animation) sind Entscheidungen, keine Mängel; die Grenze wird nach dem Hardwaretest mit Messwerten neu bewertet.
- **Der Frame-Editor funktioniert auf dem Handy nur im Querformat** und nur bei ausreichend großem Zeichenfeld (ein Tafelpixel mindestens 6 Bildschirmpixel). Das ist gewollt (ADR zu Editor).
- **Rückfragen beim Verwerfen** nutzen den `confirm()`-Dialog des Browsers (ADR-2026-11-26-Q); ein eigener Dialog ist nicht vorgesehen.
- **Die Firmware ändert in 0.8.x nur die Versionsnummer und Kommentar-/Diagnosetexte** gegenüber 0.7.2; alle Änderungen liegen in der Weboberfläche. Ein Reviewer, der Firmwarefehler in 0.8.x sucht, findet sie im Stand 0.7.2.

## 2. Akzeptierte Risiken

- Kein Schutz gegen Zugriffe anderer Geräte im selben WLAN außer dem Passwort; keine Origin-/Host-Prüfung (RB-007). Eine kleine Prüfung ist Kandidat für die Firmware-Runde.
- Zwei Geräte gleichzeitig: „Nur senden“ und dasselbe Bearbeiten (F-009/F-010, RB-003/004/005/013) sind in der Firmware nicht abgesichert; kommen nach dem Hardwaretest.
- Ein Bluetooth-Befehl wird nicht einzeln quittiert und zugeordnet (RB-006); 0.7.2 lief ohne Fehler (1665 Schreibvorgänge).
- Safari/iOS-Verhalten (Gesten, Stift, Speicher) ist nicht automatisch prüfbar.

## 3. Bewusst offen (kommt, aber nicht in dieser Version)

- Firmware-Runde nach dem Hardwaretest: F-009/F-010 = RB-003/004/005/013, RB-006 (Quittungen), RB-008 (Journal), RB-012, RB-018 bis RB-020, Host-/Origin-Prüfung.
- Eigener Qualitätsstand: CI (RB-010), Modularisierung der `index.html`, CSS-Aufräumen (RB-022/023/025/027), Seitenzoom (RB-028, ADR-I), doppelter Uploader.
- Funktionen: Textwerkzeug und Formen im Editor, BDF-Schriftimport, Mehrsprachigkeit DE/EN (siehe Roadmap bis 1.0.0).
- Nicht entfernt, weil kompatibel/benutzt: `samplePage` (vom Test benutzt), `animPan.geoNow` (Test), Feld `libraryShortcuts` und `animImp.name` (Rückfrage offen; kein Schaden).

## 4. Was ein Review hier nicht ausführen kann

- **Arduino-Compile und ESP32-Hardware** (Speicher, Heap, WLAN-Neustart, BOOT-Taste, Bluetooth zur echten Tafel).
- **Safari auf iPhone/iPad**, echter Apple Pencil und Zwei-Finger-Gesten auf echten Geräten.
- Die **Browsertests brauchen Playwright mit Chromium** und die simulierte API in `tests/`; fehlt Chromium oder ist `rb.test` blockiert, laufen sie nicht (so bei den Audits zu 0.8.1). Der Build-Test (`tests/test_build_0802.py`) und die Hosttests laufen ohne Chromium. Ohne `firmware/RavestickBoard_v0_7_2` überspringt der Build-Test den Firmware-Vergleich und meldet das als SKIP.
- Das ZIP-Paket enthält nur versionierte Dateien; die Baseline v0_7_2 liegt nicht darin.

## 5. Bereits geprüfte Befunde (Audits zu 0.8.1)

| Befund | Einordnung | Stand |
|---|---|---|
| R81-01 Schwenk-Timer beim Speichern | bestätigt | behoben 0.8.2 (`animFlush`) |
| R81-02 ungespeicherter Editor / `beforeunload` | bestätigt | behoben 0.8.2 (`animHasUnsaved`) |
| R81-03 Quellwechsel ohne Rückfrage | bestätigt | behoben 0.8.2 (`animBeginSource`, Abbrechen erhält den Entwurf) |
| R81-04 Von/Bis/Schritt nicht ganzzahlig | bestätigt | behoben 0.8.2 (`animInt`, `plan` rundet) |
| R81-05 Upload gegen Bedienung | bestätigt | behoben 0.8.2 (Sperre `inert`, Generationsprüfung) |
| R81-06 späte Datei/Bearbeiten | bestätigt | behoben 0.8.2 (`animLoadSeq` auch für Raster und Bearbeiten) |
| R81-07 Versatzpfad umgeht Begrenzung | bestätigt | behoben 0.8.2 (`animPanLimitEnd`) |
| R81-08 Undo-Grenze | bestätigt | behoben 0.8.2 (`AD.hold.trimmed`) |
| R81-09 Tastatur bei gesperrtem Editor | bestätigt | behoben 0.8.2 |
| R81-10 Editor gibt Bilder nicht frei | bestätigt | behoben 0.8.2 (`adClose`) |
| R81-16 tote Altlasten | teilweise | entfernt 0.8.2 (siehe Abschnitt 3 für Ausnahmen) |
| R81-24/25 veraltete Doku | Fehler des Autors | behoben 0.8.2 |
| RB-009 Test meldet PASS ohne Baseline | bestätigt | behoben 0.8.2 (SKIP) |
| RB-014 GIF-Decoder nimmt unvollständige Daten an | bestätigt | behoben 0.8.2 (Fehlermeldung) |
| RB-001/RB-007 Passwort, Origin | bewusst / akzeptiert | siehe Abschnitte 1 und 2 |
| RB-002 Hang-Auslöser im Entwicklungsprofil | bewusst | siehe Abschnitt 1 |
| RB-003/004/005/013, RB-006, RB-008, RB-012, RB-018 bis RB-020 | Firmware | offen, Firmware-Runde |
| RB-010, RB-022/023/025/027, RB-028 | Qualitätsstand | offen, später |

Nicht genannte Nummern sind hier nicht einzeln eingeordnet; wer sie für wichtig hält, bitte mit Fundstelle melden.
