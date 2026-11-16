<p align="center"><img src="docs/assets/board-gif.gif" alt="CoolLEDX mit LED-Motiven" /></p>
<p align="center"><img src="docs/assets/totem.jpg" width="420" alt="RavestickBoard Festival-Totem mit Neonbanane" /></p>
<h1 align="center">🍌 RavestickBoard</h1>
<p align="center"><strong>Offline-Webcontroller für die 64 × 16-Pixel-LED-Tafel CoolLEDX / CoolLED1248 mit ESP32-C3.</strong><br>
Entstanden aus einer Festival-Banane und dem Wunsch, mehr aus der ursprünglichen CoolLED1248-App herauszuholen.</p>
<p align="center">
<img alt="Version" src="https://img.shields.io/badge/version-v0.6.1.10--dev-7056d8">
<img alt="Hardware" src="https://img.shields.io/badge/hardware-ESP32--C3-007c91">
<img alt="Status" src="https://img.shields.io/badge/status-dev%20hardware%20test%20pending-f3b653">
<img alt="Lizenz" src="https://img.shields.io/badge/license-MIT-brightgreen">
<img alt="Mission" src="https://img.shields.io/badge/mission-hugs%20and%20love-ff69b4">
</p>

> **Aktueller Entwicklungskandidat: v0.6.1.10-dev (15.11.2026).** *Neu gegenüber 0.6.1.9:* **nur der Bluetooth-Unterbau.** Die Firmware spricht jetzt per **NimBLE** (Bibliothek *NimBLE-Arduino* von h2zero) mit der Tafel statt per Bluedroid, um Arbeitsspeicher zu sparen. Oberfläche, Bedienung und Abläufe bleiben unverändert. **Kompiliert** (1.578.171 Byte, 75 %; globale Variablen 88.800 Byte, 27 %); der Hardwaretest (iPhone, Safari, echte Tafel) ist bestanden, siehe unten. *Vor dem Flashen:* Bibliothek NimBLE-Arduino installieren (siehe Installation). 0.6.1.9 bleibt die Rückfallversion.

## Was ist RavestickBoard?

Das iPhone oder ein anderer Browser verbindet sich mit dem WLAN `RavestickBoard` des **ESP32-C3 Super Mini**. Das lokale Webinterface unter **http://192.168.4.1** überträgt die Darstellung per Bluetooth Low Energy an die **CoolLEDX-Tafel**. Die Tafel braucht keine modifizierte Herstellerfirmware und wiederholt einmal hochgeladene Inhalte selbstständig. Die Oberfläche läuft ohne Internet und ohne App; USB bleibt der einzige Firmware-Updateweg (**kein OTA**).

## Warum RavestickBoard?

Die Hersteller-App läuft auf einem Handy und hält die Bluetooth-Verbindung selbst. RavestickBoard verlegt das auf einen kleinen ESP32 an der Tafel und bietet dafür mehr:

- **Keine App, kein Bluetooth am Handy:** Jeder Browser im WLAN `RavestickBoard` genügt, auch der Laptop; zwei Geräte gleichzeitig. Alles läuft offline.
- **Deine Inhalte liegen im Gerät:** Bibliothek, Programme, Kurzwahlen und Animationen stehen im ESP32 und sind auf allen Geräten gleich; ein JSON-Backup sichert Bibliothek, Programme und Kurzwahlen (Animationen sind darin noch nicht enthalten).
- **Schnell bei der Veranstaltung:** acht Kurzwahl-Kacheln, Programme, die Einträge nacheinander oder als Laufband abspielen, Ambiente-Farben auf Fingertipp.
- **Mehr Gestaltung:** Farbe und Schrift **pro Zeichen**, Original-Schriften, Engschrift und Mini (ein- oder zweizeilig), **85 eigene Symbole** mit Suche, Blocktexte mit bis zu 40 Seiten.
- **Eigene Animationen:** GIF, Einzelbilder aus einem Bild oder Text-Raster importieren, zuschneiden, auf die sieben LED-Farben bringen, speichern und senden.
- **Sehen, was ankommt:** Live-Vorschau der 64 × 16-Matrix mit Datenbudget vor dem Senden.
- **Robust und nachvollziehbar:** Wächter gegen Hänger, Absturzspur, Heap-Schutz, Diagnose mit Export als Textdatei.
- **Offen:** MIT-Lizenz, Quelltext und Tests im Repository.

Die Hersteller-App bleibt daneben nutzbar, darf aber nicht gleichzeitig mit der Tafel verbunden sein.

## Funktionen auf einen Blick

Ausführlich nach Themen: **[docs/FUNKTIONEN.md](docs/FUNKTIONEN.md)**.

- **Kurzwahl:** acht Kacheln für Texte, Programme, Animationen und Ambiente.
- **Lauftext:** Schriften, Zeichen gestalten, Symbole, Vorschau, Datenbudget.
- **Blocktext:** bis zu 40 Seiten mit Ausrichtung und Anzeigedauer.
- **Animationen:** Import, Ausschnitt-Rahmen, Raster als Schnellmenü, Liste als Editor, bis zu 40 Animationen à 79 Bilder.
- **Bibliothek und Programme:** speichern, sortieren, Mehrfachauswahl am Laptop, Vorschau.
- **Tafelverwaltung:** „Meine Tafel“, Suche mit Signalstärke, fremde Tafel mit Rückweg, Vor-Scan.
- **Tafelsteuerung:** Helligkeit, Tempo, an/aus, Anzeigeverhalten; Sperre aller Geräte während einer Übertragung.
- **Diagnose:** RAM-Messung, HTTP-Spur, Absturzspur, Export als Textdatei.

## Aktuell: v0.6.1.10-dev – Bluetooth-Unterbau NimBLE statt Bluedroid

- **Neu:** Scannen, Verbinden, MTU, Schreiben und die Bestätigung je Paket laufen über **NimBLE-Arduino** (h2zero, Apache-2.0). Alles Versionsabhängige steht in der neuen Datei `RavestickBoard_Ble.h` (acht Dateien im Sketch-Ordner). Reihenfolge, Zeiten und Meldungen des Sendens bleiben wie in 0.6.1.9.
- **Anlass:** Bluedroid belegte nach dem Start etwa 73 KB; im Test von 0.6.1.9 lag das System-Minimum bei nur 160 Byte. Gemessen im Hardwaretest: Der Bluetooth-Start kostet jetzt rund 64 KB statt 73 KB, es werden also nur etwa 9 KB frei. Das System-Minimum fiel im Test mit zwei Geräten trotzdem bis auf rund 3 KB; das eigentliche Speicherproblem liegt bei großen Antworten und WLAN-Puffern und wird in 0.6.1.11 angegangen.
- **Kompiliert:** 1.578.171 Byte (75 %, 0.6.1.9: 1.638.885), globale Variablen 88.800 Byte (27 %, 0.6.1.9: 84.016).
- **Kleine Anpassungen:** Adressart der Tafel aus dem Scan, MTU wird abgewartet, Verbindungs-Timeout 7 s (NimBLE ab 2.5 wiederholt Verbindungen selbst), kein `stop()` im Scan-Rückruf. Details in [`docs/TECHNIK.md`](docs/TECHNIK.md).
- **Notausgang:** `#define RB_NIMBLE_V1 1` vor dem Include schaltet auf NimBLE-Arduino 1.4.x.
- **Nicht in diesem Stand:** Play-Taste, Heap-Schutz für große Antworten, Kleinkram (kommen mit 0.6.1.11, siehe [Roadmap](docs/ROADMAP.md)).
- **Entwicklungsschalter:** `RB_TEST_HANG` steht noch auf 1 (Test-Auslöser `/api/test/hang`); für eine Freigabe auf 0 setzen.
- **Hardwaretest bestanden (16.11.):** 37 von 37 Verbindungen gelungen (Aufbau meist unter 0,5 s), alle Auftragsarten gesendet, Zeiten wie in 0.6.1.9, 23 Minuten Dauerlauf ohne ungeplanten Neustart, Hänger-Wächter greift sauber, JSON-Backup (K2) in Ordnung. Getestet mit NimBLE-Arduino 2.5.2 und Arduino-ESP32 3.3.12.
- **Offen:** zweite Tafel (C7), Programm-Synchronisation (D9), WLAN-Beobachtung, SYS-15 (Bluetooth-Hänger). Die Reviews zu diesem Stand (zwei KI-gestützte Audits) sind ausgewertet und fließen in 0.6.1.11 ein.

## Frühere Versionen im Überblick

Vollständige Tabelle: [VERSIONSGESCHICHTE.md](VERSIONSGESCHICHTE.md) · Einzelheiten: [CHANGELOG.md](CHANGELOG.md) · die frühere lange README: [docs/archive/README_Langfassung_v0.6.1.10.md](docs/archive/README_Langfassung_v0.6.1.10.md).

| Version | Datum | Stichworte |
|---|---|---|
| 0.6.1.9 | 14.11. | Schlanke Animationsliste mit nachgeladenen Vorschaubildern (Anlass: Wächter-Neustart in `/api/anim/list`), Raster als Schnellmenü, „auf der Tafel“ als Punkt mit Flugzeug, Texteditor sperrt bei leerem Feld, Heißluftballon/Äffchen/Schwein, WLAN-Endungen in der Diagnose; Umkehren verworfen |
| 0.6.1.8 | 14.11. | 85 eigene Symbole und neues Symbol-Menü, Symbole umfärben, Animations-Raster, Import-Seite, „auf der Tafel“, Bibliotheks-Vorschau |
| 0.6.1.7 | 12.11. | Rahmen an den echten Fensterkanten (iPhone), Hinweis nur bei Datenübertragungen, Neustart-Meldung, Backup-Signal, sparsamere Exporte |
| 0.6.1.6 | 12.11. | Antworten und Sperre während einer Übertragung, fensterhohe Seiten, 40 Blocktext-Seiten, Umlaute, neun Beispiel-Animationen |
| 0.6.1.5 | 12.11. | Heap-Schutz (503, Warteseite), Modus nach Animation, Mehrfachauswahl, Rückwärts abspielen, Seitenleiste am Laptop, WLAN `RavestickBoard` |
| 0.6.1.3 bis 0.6.1.4 | 4.11. | CRC-32 für Animationsdateien, sicheres Ersetzen, Abruf in Teilen mit Heap-Schutz, kleinste freie Animations-Nummer |
| 0.6.0.0 bis 0.6.1.2 | 3.11. | Animationen: Test mit Befehl `0x04`, Import (GIF, Einzelbilder, Text-Raster), Liste, Ausschnitt-Rahmen, „Nur senden“, Kurzwahl; 0.6.0.2 und 0.6.1.1 sind Compile-Fixes |
| 0.5.0.0 bis 0.5.0.1 | 3.11. | Tafelverwaltung: „Meine Tafel“ im ESP32, Suche, fremde Tafel, keine Adresse mehr im Code |
| 0.4.4.0 bis 0.4.6.0 | 31.10. bis 3.11. | „Zeichen gestalten“ (Farbe/Schrift pro Zeichen, auch für Blockseiten), sortierbare Programme, höchstens zwei WLAN-Geräte, Vor-Scan der Tafel |
| 0.4.3.x | 30. bis 31.10. | Stabilitätsarbeit nach Hängern: Wächter, Absturzspur, RAM-Messung; Oberfläche konsolidiert, Programme im Bibliotheksstil |
| 0.4.2.x | 28. bis 30.10. | HTTP- und RAM-Stabilisierung (gzip, ETag, kleine JSON-Stücke), Blocktext als ein Bildband, Programme, acht Kurzwahlen, Bibliothek im LittleFS |
| 0.4.0 bis 0.4.1 | 26. bis 27.10. | Neue Oberfläche (Menü über die Banane), Ambiente, Bibliothek im Flash, JSON-Backup, MIT-Lizenz |
| 0.1.0 bis 0.3.5.1 | 22. bis 25.10. | Erster Webcontroller, deutsche Oberfläche, Blockseiten, 82 Original-Glyphen, Symbole, Anzeigemodi, Diagnose |

## Installation und Datensicherheit

1. Vorab ein JSON-Backup aus der aktuell laufenden Firmware erstellen und lokal aufbewahren. Die bisherige Firmware als Rückfallversion sichern.
2. In der Arduino IDE über **Sketch → Bibliothek einbinden → Bibliotheken verwalten** die Bibliothek **NimBLE-Arduino** (h2zero, Version 2.x; Apache-2.0) installieren und die Versionsnummer notieren (neu seit 0.6.1.10). Dann `firmware/RavestickBoard_v0_6_1_10/RavestickBoard_v0_6_1_10.ino` öffnen. **Alle acht Dateien** im selben Sketch-Ordner belassen: `.ino`, `RavestickBoard_WebUI.h`, `RavestickBoard_Assets.h`, `RavestickBoard_Library.h`, `RavestickBoard_Anim.h` (neu in 0.6.1.0), `RavestickBoard_v042.h`, `RavestickBoard_Icon.h` und `RavestickBoard_Ble.h` (neu in 0.6.1.10).
3. Arduino IDE: **ESP32C3 Dev Module**, Espressif **3.3.12**, **USB CDC On Boot: Enabled**, **No OTA (2MB APP/2MB SPIFFS)**. Bestehendes Partitionsschema **nicht ändern**, **Erase All Flash deaktiviert** lassen.
4. Nach dem Flashen mit WLAN `RavestickBoard` verbinden (seit 0.6.1.5; bis 0.6.1.4 `CoolLED1248`, Passwort unverändert), `http://192.168.4.1` aufrufen. Bibliothek nicht neu formatieren; das Bibliotheksformat ist unverändert. Ausnahme seit 0.6.1.6: Blocktexte werden beim nächsten Speichern mit 40 Seitenplätzen abgelegt und sind danach für 0.6.1.5 und älter nicht mehr lesbar (JSON-Backup!). Für Animationen muss das Dateisystem eingerichtet sein (wie für die Bibliothek); der Ordner `/rb-anim` wird beim Start angelegt. Falls das Homescreen-Icon nicht übernommen wird, die Verknüpfung über Safari erneut hinzufügen.
5. Nach Änderungen an `web/index.html`: `python tools/sync_web.py` erzeugt den gzip-Webheader neu.

## Dokumentation

- **Funktionen nach Themen:** [docs/FUNKTIONEN.md](docs/FUNKTIONEN.md)
- **Technik und Formate:** [docs/TECHNIK.md](docs/TECHNIK.md) · **Diagnose:** [docs/DIAGNOSE.md](docs/DIAGNOSE.md) · **Entscheidungen:** [docs/ENTSCHEIDUNGEN.md](docs/ENTSCHEIDUNGEN.md)
- **Roadmap und Themenspeicher:** [docs/ROADMAP.md](docs/ROADMAP.md), [docs/THEMENSPEICHER.md](docs/THEMENSPEICHER.md) · **Quellen und Lizenzen:** [docs/QUELLEN_UND_LIZENZEN.md](docs/QUELLEN_UND_LIZENZEN.md)
- **Hardwaretest 0.6.1.10:** [Testplan](docs/TESTPLAN_v0.6.1.10.md) (dieselben Schritte als Excel-Datei `RavestickBoard_Hardwaretest_v0.6.1.10.xlsx`); ältere Pläne in [docs/archive/](docs/archive/)
- **Älter:** [Bibliotheksformat](docs/archive/BIBLIOTHEK_v0.4.1.md), [letzte ausführliche Installationsanleitung](docs/archive/INSTALLATION_v0.4.2.4.1.md)

**Teststand v0.6.1.10 (Tests mit Endung `06110`):** Entscheidungslogik von Vor-Scan und Tafelsuche läuft mit dem echten Sketch-Code und der echten Hilfsdatei `RavestickBoard_Ble.h` gegen eine Attrappe der NimBLE-Klassen; dazu Build-, Browser-, Parität- und Hosttests wie in 0.6.1.9 (Einzelheiten und frühere Stände: [tests/README.md](tests/README.md)). Der Sketch **kompiliert** mit NimBLE-Arduino und wurde auf echter Hardware mit iPhone, Safari und Tafel getestet (siehe oben).

## Mitmachen und Sicherheit

Siehe [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) und unsere [Issue-Vorlagen](.github/ISSUE_TEMPLATE/).

## Wie wir entwickeln

Wir entwickeln RavestickBoard gemeinsam: Wir entwerfen, programmieren, dokumentieren und testen die Software im engen Austausch. Die realen ESP32-/CoolLEDX-Hardwaretests führen wir vor Ort durch; dabei unterstützen KI-gestützte Werkzeuge wie **ChatGPT und Claude** die Konzeption, Fehlersuche, Implementierung und Dokumentation. Wir unterscheiden ausdrücklich zwischen lokal geprüftem Code und hardwarebestätigten Funktionen.

## Entwicklung, Quellen und Lizenz

RavestickBoard ist eine eigenständige C++-/HTML-/JavaScript-Implementierung. Die Referenzen für die Animationsforschung sind [schulzad/coolled-sign-controller (OpenSign)](https://github.com/schulzad/coolled-sign-controller) (Protokoll und Kodierung des Befehls `0x04`), [jean-santos/coolled1248-rs](https://github.com/jean-santos/coolled1248-rs) und [zackmcmurrin-dev/coolledux-linux-uploader](https://github.com/zackmcmurrin-dev/coolledux-linux-uploader). Ergänzend dokumentieren wir den früh untersuchten [UpDryTwist/coolledx-driver](https://github.com/UpDryTwist/coolledx-driver) und [ohtaras/led](https://github.com/ohtaras/led). Die technischen Protokollfakten wurden für unsere Firmware eigenständig umgesetzt. Ob eine Datenformatvariante des anderen Panels auf unserer eigenen CoolLEDX funktioniert, ist separat zu prüfen.

**Danksagung:** Besonderer Dank an **Adam Schulz**, [OpenSign](https://github.com/schulzad/coolled-sign-controller), für den freundlichen Austausch und die technischen Hinweise zu nativer Animation (`0x04`) und BLE-Bestätigungen. Adam hat uns per E-Mail ausdrücklich erlaubt, seine Arbeit zu nutzen, zu verändern und zu portieren, und weitere Hinweise gegeben (Datenlimit, Ablauf der Bestätigungen, Zeit je Frame). Auf diesen Erkenntnissen und dem dokumentierten Format beruht der Animationstest ab 0.6.0.0. Der Code dafür ist **eigenständig geschrieben, kein OpenSign-Code wurde übernommen**; Nutzdaten und Paketierung wurden lokal gegen OpenSigns Kodierer abgeglichen (byte-identisch). OpenSign steht inzwischen unter der MIT-Lizenz (Copyright © 2026 Adam Schulz); bei einer späteren Codeübernahme bleibt der Hinweis zu erhalten, siehe [`docs/QUELLEN_UND_LIZENZEN.md`](docs/QUELLEN_UND_LIZENZEN.md).

Ebenfalls herzlichen Dank an **h2zero** und alle Mitwirkenden von **[NimBLE-Arduino](https://github.com/h2zero/NimBLE-Arduino)**, die den schlanken Bluetooth-Stack der Apache-**[Mynewt-NimBLE](https://github.com/apache/mynewt-nimble)**-Bibliothek für Arduino nutzbar machen. Seit 0.6.1.10 steckt unsere gesamte Bluetooth-Verbindung zur Tafel darauf; sie schafft im knappen Arbeitsspeicher des ESP32-C3 den Platz, den das Projekt dringend braucht. NimBLE-Arduino steht unter der Apache-Lizenz 2.0 und wird **nicht** mit diesem Repository ausgeliefert, sondern über den Arduino-Bibliotheksverwalter installiert.

**Bausteine von anderen, die RavestickBoard nutzt:**

| Baustein | Wofür | Lizenz / Hinweis |
|---|---|---|
| [Arduino-ESP32](https://github.com/espressif/arduino-esp32) (Espressif) | Boardpaket mit WLAN, Webserver, Dateisystem und Preferences | wird in der Arduino IDE installiert, nicht mitgeliefert |
| [NimBLE-Arduino](https://github.com/h2zero/NimBLE-Arduino) (h2zero) auf Basis von [Apache Mynewt NimBLE](https://github.com/apache/mynewt-nimble) | Bluetooth Low Energy zur Tafel (seit 0.6.1.10) | Apache-2.0, nicht mitgeliefert |
| [Lucide](https://lucide.dev/) (teils von Feather abgeleitet) | Icons der Oberfläche | ISC bzw. MIT, Hinweise in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) |
| [OpenSign](https://github.com/schulzad/coolled-sign-controller) (Adam Schulz) und weitere oben genannte Projekte | Protokollwissen zur CoolLEDX (Animation `0x04`, Bestätigungen) | nur als Referenz; kein Code übernommen |

**Lizenz und Drittmaterialien:** Unser selbst entwickelter RavestickBoard-Code steht unter der **[MIT-Lizenz](LICENSE)** (Copyright © 2026 du13500). Die Lizenz erlaubt ausdrücklich auch kommerzielle Nutzung, Bearbeitung und Weitergabe unter ihren Bedingungen. Das Projekt wird derzeit als privates Hobbyprojekt entwickelt; das schränkt die MIT-Rechte nicht ein. Eingebettete **Lucide-Icons** stehen unter ISC, ausgewählte von Feather abgeleitete Icons zusätzlich unter MIT. Ihre erforderlichen Copyright- und Lizenzhinweise stehen in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Fremde Originalmotive, Marken und sonstige Drittmaterialien werden durch unsere MIT-Lizenz nicht automatisch mitlizenziert.

<p align="center"><strong>Made for the rave, powered by a banana. 🍌</strong><br><sub>Independent project, not affiliated with the CoolLED1248/CoolLEDX manufacturer.</sub></p>
