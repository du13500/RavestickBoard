# RavestickBoard · Quellen, Lizenzumfang und Rechte

**Aktueller Stand: 14.11.2026 (v0.6.1.8-dev) · Seit 0.6.1.8 sind die Symbole eigene Pixelgrafiken (siehe Abschnitt „Symbole ab 0.6.1.8“). Projektcode unter MIT. Die neun Beispiel-Animationen unter `assets/animationen/` (seit 0.6.1.6) sind eigene Gestaltung, mit `tools/beispiel_animationen.py` erzeugt, ebenfalls MIT. Seit 0.6.1.0 enthält die Weboberfläche einen **selbst geschriebenen GIF-Decoder** und Bildumwandlungen (kein Fremdcode; als Prüfreferenz dienen Pillow und der `ImageDecoder` von Chromium nur im Test, nicht im Produkt).** Diese Übersicht trennt von uns lizenzierbare Bestandteile, fremde Werke und technische Gerätefakten. Sie ersetzt keine individuelle rechtliche Prüfung.

## MIT ab v0.4.0-dev

Wir geben den **eigenständig erstellten Programmcode für Firmware und Webinterface** und unsere eigenen Dokumentationstexte unter der [MIT-Lizenz](../LICENSE) frei. Die vormalige Einstellung **„All Rights Reserved“** war eine frühere, bewusst gewählte Projektphase und ist für die nun unter MIT veröffentlichten eigenen Codebestandteile nicht mehr der geltende Lizenzstatus.

MIT gestattet ausdrücklich auch kommerzielle Nutzung. Dass wir RavestickBoard als privates und überwiegend nichtkommerzielles Festivalprojekt betreiben, ist **keine weitere Lizenzbedingung**.

## Symbole ab 0.6.1.8

Seit 0.6.1.8 liegen die 85 Symbole (Nummern 0–84, je 16 × 16 Pixel, sieben Farben) als Daten in `assets/symbole_0618.txt` und werden mit `tools/generate_assets.py` in `web/index.html` und `RavestickBoard_Assets.h` übernommen. Die ersetzten und neuen Matrizen hat Felix am 14.11.2026 als eigene Pixelgrafiken geliefert; sie werden wie die übrigen eigenen Motive des Projekts geführt (Lizenzfrage für diese Dateien bitte bei Gelegenheit ausdrücklich bestätigen): 4, 5, 9, 10, 12, 15–20, 22, 23, 25, 26, 27, 29, 30, 35, 59, 60 und 64–84. Die Flaggen (74–79) folgen den bekannten Farbfolgen; die Vorlage war das Flaggenlexikon des CSD Deutschland (https://csd-deutschland.de/flaggenlexikon/), übernommen wurden nur die Farbfolgen als Pixelraster.

**Bestand, der unverändert bleibt:** 13 (Trauben) und 14 (Banane) warten auf Ersatz. Die Nummern 0, 1, 2, 3, 6, 7, 8, 11 und 21 stammen aus der früheren Rekonstruktion; Felix stuft sie als verändert bzw. nicht schutzwürdig (einfache Formen) ein, sie gelten daher nicht mehr als „Original“. Für die übrigen unveränderten Nummern gilt die Herkunftsangabe früherer Stände (eigene Excel-Motive ab Nummer 36, früher rekonstruierte Herstellersymbole darunter); eine Einzelprüfung dieser Nummern steht aus. Die verworfenen Nummern 48, 51–53, 56–58 sind leer.

**Was damit nicht entschieden ist:** Eine rechtliche Prüfung der rekonstruierten Reste ersetzt das nicht. Die 164 Schriftzeichen (Normal und Fett) sind der Hersteller-App nachgebaut und bleiben ein eigenes Thema.

## Nicht von unserer MIT-Erlaubnis umfasst

Wir können nur Rechte vergeben, die wir selbst besitzen oder wirksam weiterlizenzieren dürfen. Unsere MIT-Lizenz verleiht daher keine Rechte an:

- **Hersteller-App und daraus rekonstruierten Symbolgrafiken oder Schriftzeichen.** Einzelne 16×16-Matrizen wurden nach Screenshots der Original-App rekonstruiert und liegen als Daten in `RavestickBoard_Assets.h` sowie den Webassets. Wir beanspruchen daran keine originären Herstellerrechte und sagen keine MIT-Lizenz für diese fremden Gestaltungen zu.
- **Herstellerlogos, Namen und Marken.** Die Nennung von CoolLED1248/CoolLEDX dient der Kompatibilitätsbeschreibung und bedeutet keine Zusammenarbeit oder Freigabe durch den Hersteller.
- **Fremdcode**, für den uns keine passende Lizenz oder ausdrückliche Erlaubnis vorliegt.
- **Fotos, GIFs und andere externe Materialien**, soweit ihre Rechte nicht ausdrücklich uns gehören. Ein öffentlich sichtbares Bild wird dadurch nicht gemeinfrei.
- **Plattform-Abhängigkeiten** (Arduino-ESP32, BLE, WebServer usw.); deren eigene Lizenzen bleiben wirksam.

Die von uns selbst entwickelten Pixelmotive sind eigenständig erstellte Inhalte; wir führen die Herkunft der Sammlungen getrennt von rekonstruierten Herstellermotiven nach. Dass Web-Buttons die Herkunft der Motive **nicht mehr unterscheiden**, ändert an diesen Rechtevorbehalten nichts.

## Externe technische Referenzen

| Projekt | Bekannter Lizenzstatus / Nutzung | Umgang |
| --- | --- | --- |
| [UpDryTwist/coolledx-driver](https://github.com/UpDryTwist/coolledx-driver) | MIT, Copyright © 2025 Greg Tatham; technische BLE-Protokollreferenz | Bei konkreter Übernahme urheberrechtlich geschützter Codeanteile Attribution und Lizenz erhalten |
| [ohtaras/led](https://github.com/ohtaras/led) | Zum früheren Prüfzeitpunkt keine allgemeine Wiederverwendungslizenz gesichert | Nur technische Fakten untersuchen, keinen unlizenzierbaren Code übernehmen |
| [schulzad/coolled-sign-controller (OpenSign)](https://github.com/schulzad/coolled-sign-controller) | **MIT, Copyright © 2026 Adam Schulz** (geprüft am 3.11.2026 an einer Kopie vom 30.10.2026; zum früheren Prüfzeitpunkt noch „All rights reserved“) | Protokollfakten (Befehl `0x04`, Antwortcodes) als Grundlage des Animationstests; eigenständig geschriebener Code, **kein Quelltext übernommen**. Bei einer späteren Übernahme von Codeanteilen Lizenztext und Urheberhinweis beibehalten (siehe `THIRD_PARTY_NOTICES.md`) |

Wir haben Adam Schulz am 23.10.2026 um eine Erlaubnis zur Einbeziehung geeigneter OpenSign-Teile gebeten. Inzwischen steht OpenSign unter der MIT-Lizenz, und Adam Schulz hat uns per E-Mail ausdrücklich erlaubt, seine Arbeit zu nutzen, zu verändern und zu portieren (die Mail wird hier nicht wiedergegeben). Eine weitere Erlaubnis ist nicht nötig. **Tatsächlich übernommen wurde bisher nur Wissen über das Geräteprotokoll** (Aufbau der Animationsdaten, Paketantworten, Datenlimit), kein Quelltext. Der Animationstest in 0.6.0.0 wurde lokal gegen OpenSigns Kodierer abgeglichen (nur als Prüfwerkzeug, nicht im Repository). Danksagung an Adam Schulz im README.

**Historische Einordnung:** Ältere Entwicklungsberichte in `docs/` können weiterhin den früheren Lizenzstand „All Rights Reserved“ nennen. Sie dokumentieren ihren damaligen Zustand; für neu veröffentlichte eigene Codebestandteile gilt die aktuelle [`LICENSE`](../LICENSE) mit diesen Grenzen.

## Rechteprüfung bei neuen Beiträgen

Wir dokumentieren für zusätzliche Quellen künftig URL/Urheber/Lizenzstand, konkrete Verwendung und ggf. abweichende Nutzungsbedingungen. Externe Beiträge nehmen wir erst dann unter MIT an, wenn deren Weiterlizenzierung geklärt ist. Bei eigenen Copyright-Hinweisen und der Verteilung der Software erhalten wir die MIT-Hinweise.

Unsere Diagnoseexports enthalten bewusst keine persönlichen Texte, WLAN-Zugangsdaten oder Bluetooth-Geräteadressen. Das derzeit im Quelltext enthaltene Standard-WLAN-Passwort gilt als öffentliche Beispielkonfiguration und sollte vor einem breiteren Einsatz angepasst werden.
