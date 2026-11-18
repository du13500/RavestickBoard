# Sicherheitsrichtlinie

RavestickBoard ist ein experimenteller, offline nutzbarer Webcontroller mit WLAN-Access-Point und Bluetooth Low Energy. **Wir geben keine Zusicherung, dass die Steuerung sicherheitsgehärtet, für öffentliche Netze geeignet oder für kritische Einsätze zertifiziert ist.**

## Unterstützung

Gepflegt wird nur der **jeweils neueste Entwicklungsstand im Hauptzweig** (zurzeit die Version oben in der [README](README.md)). Eine Sicherheitswartung ist nicht zugesagt, auch nicht für ältere Stände unter `firmware/`; sie bleiben nur zum Nachvollziehen und als Rückfallversion im Repository.

## Sicherheitslücke melden

Für vertrauliche Hinweise nutze die Funktion **„Report a vulnerability“** unter dem GitHub-Tab **Security**, **sofern der Repositoryinhaber private Vulnerability Reports aktiviert hat**. Falls diese Funktion nicht verfügbar ist, bitte **keine Zugangsdaten oder ausnutzbaren Details in einem öffentlichen Issue** veröffentlichen; zunächst über einen verfügbaren privaten Kanal an den Repositoryinhaber wenden. Es gibt derzeit keine garantierte Bearbeitungsfrist.

Sinnvolle Angaben sind Firmwareversion, Bedrohungsszenario, reproduzierbare Schritte, Auswirkungen und eine möglichst datenarme Diagnose. Keine Zugangsdaten, privaten BLE-Adressen oder fremden personenbezogenen Daten senden.

## Sicherheitsgrenzen

- **Das Standardpasswort des WLANs ist öffentlich.** Es steht im Quelltext (`WIFI_PASSWORD`) und damit in diesem Repository. Bis es geändert wird, kann sich jeder verbinden, der es kennt; mit höchstens zwei gleichzeitigen Geräten kann ein Fremder so auch den zweiten Platz belegen.
- **Seit v0.6.1.11 lässt sich das Passwort ändern** (Einstellungen → WLAN-Passwort, 8 bis 63 Zeichen ohne Umlaute). Es liegt im NVS des ESP32 und steht nie in Status, Diagnose, Exporten oder im JSON-Backup. Wer im WLAN ist, darf es ändern; es gibt kein zweites Login. Vergessen? BOOT-Taste im laufenden Betrieb 5 Sekunden halten, dann gilt wieder das Standardpasswort (wer das Board in der Hand hat, kann es also zurücksetzen).
- Websteuerung und BLE-Befehle sind nicht Ende-zu-Ende-authentifiziert. Die Webrouten prüfen keine Herkunft (Origin); der ESP32 ist **nicht** als Netzwerk-Gateway für andere Geräte vorgesehen.
- Der Entwicklungsstand enthält einen Test-Auslöser (`/api/test/hang`, `RB_TEST_HANG`), der das Board absichtlich hängen lässt. Für eine Freigabe `RB_RELEASE 1` setzen; das schaltet ihn ab (der Hänger-Wächter bleibt).
- Firmwareupdates werden nur über USB durchgeführt. **Kein OTA**, kein Ferneingriff in die Herstellerfirmware.
- Neue Abhängigkeiten und Drittanbieterdaten müssen getrennt geprüft werden.
