# RavestickBoard: Web Installer und Firmware-Veröffentlichung

**Stand:** 27.11.2026  
**Status:** Konzept für eine zukünftige stabile Version  
**Projekt:** [RavestickBoard](https://github.com/du13500/RavestickBoard)

## 1. Zielsetzung

RavestickBoard soll auch von Menschen ohne Programmierkenntnisse auf einem ESP32 installiert werden können. Anwender sollen weder Arduino IDE noch Python, Bibliotheken oder eine lokale Entwicklungsumgebung benötigen.

Die Firmware wird zentral kompiliert und als fertige Binärdatei bereitgestellt. Die Installation erfolgt direkt über den USB-Anschluss des Computers und eine Webseite. Die eigentliche Bedienung von RavestickBoard bleibt anschließend lokal über das WLAN des ESP32 möglich. Es entsteht keine Cloudpflicht für den Betrieb der Firmware.

## 2. Bevorzugte Lösung: ESP Web Tools

[ESP Web Tools](https://esphome.github.io/esp-web-tools/) ist ein Open-Source-Projekt, das ESP-Mikrocontroller über die Web Serial API direkt aus dem Browser flashen kann. Die Chipfamilie ESP32-C3 wird unterstützt. Die konkrete Kompatibilität mit dem verwendeten ESP32-C3 Super Mini und dessen USB-Anbindung muss praktisch getestet werden.

Die Installationsseite kann kostenlos über GitHub Pages veröffentlicht werden, beispielsweise unter:

`https://du13500.github.io/RavestickBoard/`

Diese Adresse ist ein Vorschlag, keine bereits eingerichtete Installationsseite.

### Vorteile

- Keine Installation zusätzlicher Flash-Software oder Entwicklungswerkzeuge.
- Nutzbar unter Windows, macOS und Linux mit einem kompatiblen Browser und USB-Zugriff.
- Chrome und Edge auf dem Desktop als primär unterstützte Browser.
- Kein eigener Server und kein Backend erforderlich.
- Einbindung in das bestehende GitHub-Projekt möglich.
- Gestaltung passend zum RavestickBoard-Design, einschließlich deutscher und englischer Installationsanleitung.
- Keine zusätzliche Smartphone-App für die spätere Bedienung notwendig.

### Voraussetzungen und Einschränkungen

- HTTPS beziehungsweise ein sicherer Browserkontext für Web Serial.
- USB-Datenkabel, nicht lediglich ein Ladekabel.
- Unterstützter Browser und erforderliche Betriebssystemberechtigungen; gegebenenfalls USB-Treiber.
- Safari auf iPhone und iPad nicht als primärer Installationsweg vorsehen. Die spätere WLAN-basierte Bedienung ist davon unabhängig.
- Bei Problemen mit der automatischen Bootloader-Aktivierung eine bebilderte Anleitung für BOOT und RESET bereitstellen.
- Für die Installation ist normalerweise ein Internetzugang erforderlich; für den anschließenden lokalen Betrieb nicht.

## 3. Anwenderablauf

1. RavestickBoard-Installationsseite in Chrome oder Edge öffnen.
2. ESP32-C3 Super Mini per USB-Datenkabel mit dem Computer verbinden.
3. Stabile Firmwareversion auswählen beziehungsweise die vorgeschlagene aktuelle Version verwenden.
4. Auf „RavestickBoard installieren“ klicken.
5. Den seriellen USB-Port auswählen und die Installation bestätigen.
6. Installation und Neustart abwarten.
7. Mit dem RavestickBoard-WLAN verbinden und die lokale Benutzeroberfläche öffnen.
8. LED-Tafel verbinden und RavestickBoard einrichten.

Der Anwender benötigt keine Kenntnis über Flash-Adressen, Partitionstabellen oder Compiler-Einstellungen.

## 4. Technische Umsetzung

### 4.1 Firmware-Artefakte

Der bestehende Build-Prozess soll reproduzierbar die für die Zielhardware notwendigen Dateien erzeugen. Je nach tatsächlicher Projektkonfiguration gehören dazu:

- Bootloader
- Partitionstabelle
- Anwendungs-Firmware
- gegebenenfalls weitere Boot- oder Initialisierungsdateien
- gegebenenfalls ein LittleFS-Abbild für mitgelieferte Ressourcen

Für die Erstinstallation kann daraus mit `esptool` ein zusammengeführtes Factory-Image erstellt werden. Alternativ kann das Manifest einzelne Binärdateien mit ihren jeweiligen Flash-Adressen auflisten.

Die Flash-Adressen, Flash-Größe, Partitionen und erforderlichen Artefakte müssen aus dem realen Build von RavestickBoard übernommen werden. Keine ungeprüften Standardadressen anderer ESP32-Projekte verwenden.

### 4.2 Manifest

ESP Web Tools benötigt ein JSON-Manifest, welches Firmwareversion, Chipfamilie und die zu flashenden Dateien beschreibt.

Beispiel für eine zukünftige Erstinstallation mit einem korrekt erzeugten Factory-Image:

```json
{
  "name": "RavestickBoard",
  "version": "1.0.0",
  "builds": [
    {
      "chipFamily": "ESP32-C3",
      "parts": [
        {
          "path": "ravestickboard-v1.0.0-esp32c3-factory.bin",
          "offset": 0
        }
      ]
    }
  ]
}
```

Das Beispiel setzt ein für die Basisadresse 0 erzeugtes Factory-Image voraus. Version und Dateiname sind Platzhalter; es handelt sich nicht um eine existierende Firmware.

### 4.3 Installationsseite

ESP Web Tools stellt eine fertige Webkomponente für den Installationsdialog bereit. Die eigene Webseite muss diese Komponente und das Manifest einbinden. Der eigentliche Flash-Vorgang muss nicht selbst programmiert werden.

Konzeptioneller HTML-Ausschnitt nach Einbindung des ESP-Web-Tools-Moduls:

```html
<esp-web-install-button manifest="./firmware/manifest.json">
  <button slot="activate">RavestickBoard installieren</button>
  <span slot="unsupported">Bitte Chrome oder Edge verwenden.</span>
</esp-web-install-button>
```

Für die produktive Veröffentlichung eine geprüfte Version der Bibliothek festschreiben und die Lizenzhinweise berücksichtigen. Abhängigkeiten möglichst lokal auf der Projektseite bereitstellen. Eine selbst entwickelte Web-Serial-Implementierung ist zunächst nicht erforderlich.

## 5. Erstinstallation, Updates und Datenintegrität

Die folgenden Installationsarten sollen logisch voneinander getrennt werden:

| Installationsart | Ziel |
| --- | --- |
| Erstinstallation | Vollständige Einrichtung eines neuen ESP32 |
| Firmware-Update | Neue Firmware unter möglichst vollständigem Erhalt der Nutzerdaten |
| Neuinstallation / Recovery | Wiederherstellung bei beschädigter Firmware; Datenverlust ausdrücklich ankündigen |
| Downgrade (optional) | Rückkehr zu einer getesteten älteren Version |

Besonders zu beachten sind NVS und LittleFS. Dort gespeicherte Einstellungen und Inhalte dürfen bei einem gewöhnlichen Update nicht unbeabsichtigt überschrieben werden. Die tatsächlichen Speicherorte und Datenformate sind anhand des Quellcodes zu prüfen.

Ein zusammengeführtes Factory-Image ist nicht automatisch für ein datenerhaltendes Update geeignet. Auch ohne vollständiges Löschen des Flash-Speichers können enthaltene Datenbereiche oder Füllbytes bestehende Daten überschreiben. Für Updates deshalb separate, validierte Artefakte und einen explizit getesteten Installationsablauf vorsehen. Bei Bedarf kann ESP Web Tools durch eine eigene Update-Funktion ergänzt werden.

Weitere Anforderungen:

- Keine stillschweigende Löschung des gesamten Flash-Speichers.
- Klare Bestätigung vor destruktiven Aktionen.
- Prüfen, ob bei Versionswechseln Datenmigrationen notwendig sind.
- Sicherstellen, dass die Weboberfläche und Firmware zueinander passen.
- Optional Export und Import von Einstellungen sowie Nutzerinhalten vorsehen.
- Improv Serial ist eine mögliche spätere Erweiterung für die Firmwareerkennung durch ESP Web Tools, aber keine Voraussetzung für die Erstinstallation. Eine automatische Erkennung der installierten RavestickBoard-Version ist ohne passende Implementierung nicht garantiert.

## 6. Automatisierte Veröffentlichung über GitHub Actions

Ein zukünftiger Release-Workflow könnte folgendermaßen aufgebaut sein:

```text
Stabiler Git-Tag / freigegebenes Release
    -> reproduzierbarer Firmware-Build
    -> automatisierte Prüfungen
    -> Factory-Image und geprüfte Update-Artefakte
    -> SHA-256-Prüfsummen
    -> GitHub Release
    -> Manifest und Firmware auf GitHub Pages veröffentlichen
    -> Web Installer stellt neue stabile Version bereit
```

Empfehlungen:

- Build-Konfiguration, Boarddefinitionen und Bibliotheksversionen festschreiben.
- Stabile Releases und Entwicklungsversionen getrennt behandeln.
- Keine automatische öffentliche Installation eines beliebigen Entwicklungsstands.
- Veröffentlichung erst nach erfolgreichem Build und Freigabe der getesteten Version.
- Versionsgebundene Binärdateien nutzen; Manifest erst nach erfolgreicher Bereitstellung aktualisieren.
- Frühere stabile Releases für manuelle Wiederherstellung verfügbar halten.
- Quellcode, Binärdateien und Versionsinformationen eindeutig einander zuordnen.
- Schreibberechtigungen der CI-Workflows auf das notwendige Minimum begrenzen.

GitHub Pages kann sowohl die Installationsseite als auch Manifest und Binärdateien bereitstellen. GitHub Releases dienen zusätzlich als Downloadarchiv. Eine gemeinsame, statische Bereitstellung vermeidet unnötige CORS-Probleme.

## 7. Vorschlag für die Projektstruktur

```text
RavestickBoard/
├── ...                          # bestehende Firmware und Dokumentation
├── installer/                   # neue Quelldateien der Installationsseite
│   ├── index.html
│   ├── assets/
│   └── firmware/                # generierte Dateien im Deployment
│       ├── manifest.json
│       └── ravestickboard-...-factory.bin
└── .github/
    └── workflows/
        └── release.yml
```

Dies ist eine konzeptionelle Ergänzung, keine Darstellung des aktuellen Repositorys. Generierte Firmwaredateien müssen nicht dauerhaft im Entwicklungsbranch eingecheckt werden; sie können aus dem Release-Workflow stammen.

## 8. Alternative: Windows-Flasher

Eine eigene portable `RavestickBoard-Flasher.exe` wäre weiterhin möglich. Sie könnte Espressifs `esptool` intern verwenden und eine einfache grafische Oberfläche für Portauswahl, Geräteprüfung, Versionsauswahl, Flash-Vorgang und Recovery bieten.

| Kriterium | Web Installer | Windows-EXE |
| --- | --- | --- |
| Arduino IDE erforderlich | Nein | Nein |
| Zusätzlicher Download | Nein | Ja |
| Windows, macOS und Linux | Mit kompatiblem Browser | Separate Builds erforderlich |
| Offline-Installation | Nicht standardmäßig | Möglich |
| Entwicklungs- und Wartungsaufwand | Vergleichsweise gering | Höher |
| Windows SmartScreen-Warnungen | Keine EXE erforderlich | Bei unsignierter EXE möglich |
| Hosting | GitHub Pages | GitHub Releases |

Empfehlung: Zunächst keine eigene EXE entwickeln. Für spezielle Offline- oder Recovery-Anforderungen können die fertigen Binärdateien und eine dokumentierte esptool-Anleitung genügen. Eine EXE erst bei erkennbarem Bedarf nachrüsten.

## 9. Roadmap und Abnahmekriterien

### Phase 1: Technischer Machbarkeitsnachweis

- [ ] Bestehenden Build und tatsächliches Flash-Layout dokumentieren.
- [ ] Factory-Image für ESP32-C3 Super Mini erzeugen.
- [ ] Minimale ESP-Web-Tools-Testseite und Manifest erstellen.
- [ ] Installation auf einem unbespielten beziehungsweise bewusst gelöschten Testgerät erfolgreich durchführen.
- [ ] Neustart, WLAN-Zugang, Weboberfläche und LED-Anbindung prüfen.

### Phase 2: Sicherer Update- und Recovery-Prozess

- [ ] Update ohne Verlust vorhandener Einstellungen und Inhalte testen.
- [ ] Unterbrochenen Flash-Vorgang und Wiederherstellung testen.
- [ ] Falsche Chipfamilie beziehungsweise nicht unterstützte Hardware abweisen.
- [ ] USB-Port-, Treiber- und Bootloader-Probleme dokumentieren.
- [ ] Speicherlayout, Datenmigration und mögliche Downgrades prüfen.

### Phase 3: Öffentliche Bereitstellung

- [ ] Installationsseite im RavestickBoard-Design gestalten.
- [ ] Deutsche und englische Anleitung, Hardwareliste und FAQ ergänzen.
- [ ] GitHub Pages einrichten.
- [ ] Release-Workflow mit automatisierten Prüfungen und Prüfsummen erstellen.
- [ ] Installation unter Windows, macOS und Linux mit kompatiblen Browsern erproben.
- [ ] Test durch eine Person ohne Arduino- oder ESP32-Erfahrung durchführen.

## 10. Fazit

Der Web Installer ist ein sinnvoller Baustein auf dem Weg von RavestickBoard als Entwicklerprojekt zu einer für normale Anwender zugänglichen Open-Source-Anwendung. Er reduziert die Einstiegshürde erheblich, ohne eine zusätzliche Desktop-Anwendung oder eine Cloud-Infrastruktur für den Betrieb der LED-Steuerung zu erzwingen.

Der Machbarkeitsnachweis kann bereits vor Version 1.0.0 auf einer separaten Testseite stattfinden. Die öffentliche Bereitstellung sollte erst erfolgen, wenn Erstinstallation, Updates und Recovery ausreichend auf der echten Hardware getestet worden sind.

## 11. Technische Referenzen

- ESP Web Tools: https://esphome.github.io/esp-web-tools/
- ESP Web Tools, Quellcode und Manifest-Dokumentation: https://github.com/esphome/esp-web-tools
- Espressif esptool für ESP32-C3: https://docs.espressif.com/projects/esptool/en/latest/esp32c3/
- GitHub Pages: https://docs.github.com/en/pages
- GitHub Actions: https://docs.github.com/en/actions
- Web Serial API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API

**Abgrenzung:** Dieses Dokument beschreibt eine vorgeschlagene Architektur. Das aktuelle RavestickBoard-Repository wurde für dieses Konzept nicht erneut auditiert; es wurde weder Firmware gebaut noch ein ESP32 geflasht oder eine Website veröffentlicht. Konkrete Build-Befehle, Flash-Adressen und der datenerhaltende Update-Weg sind daher bewusst noch nicht abschließend festgelegt.
