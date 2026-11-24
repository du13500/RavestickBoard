# RavestickBoard · Funktionen nach Themen

**Stand: 23.11.2026 (v0.7.1-dev).** Programme laufen fest mit Tempo 80 (der Regler springt beim Start auf 80); die Kurzwahl meldet beim Antippen nur Fehler; Animationen zeigen keine ID mehr (für Kurzbefehle `/api/anim/list`). Diese Datei beschreibt, was die Oberfläche und die Firmware können, nach Themen geordnet (nicht nach Versionen). Die Geschichte steht in der [Versionsgeschichte](../VERSIONSGESCHICHTE.md) und im [CHANGELOG](../CHANGELOG.md), technische Formate in [`TECHNIK.md`](TECHNIK.md), Messen und Fehlersuche in [`DIAGNOSE.md`](DIAGNOSE.md), Entscheidungen in [`ENTSCHEIDUNGEN.md`](ENTSCHEIDUNGEN.md). Alles hier ist am Rechner geprüft; was auf der Hardware bestätigt ist, steht in den Testplänen und im CHANGELOG.

## Inhalt

1. [So arbeitet das System](#1-so-arbeitet-das-system)
2. [Bedienung](#2-bedienung)
3. [Kurzwahl](#3-kurzwahl)
4. [Lauftext](#4-lauftext)
5. [Blocktext](#5-blocktext)
6. [Symbole](#6-symbole)
7. [Animationen](#7-animationen)
8. [Ambiente und Tafelsteuerung](#8-ambiente-und-tafelsteuerung)
9. [Bibliothek und Programme](#9-bibliothek-und-programme)
10. [Tafelverwaltung und Bluetooth](#10-tafelverwaltung-und-bluetooth)
11. [Stabilität und Speicher](#11-stabilität-und-speicher)
12. [Diagnose](#12-diagnose)
13. [Datensicherung und mehrere Geräte](#13-datensicherung-und-mehrere-geräte)
14. [Grenzen](#14-grenzen)

## 1. So arbeitet das System

- Ein **ESP32-C3 Super Mini** öffnet das WLAN `RavestickBoard` (bis 0.6.1.4 `CoolLED1248`; das Passwort lässt sich seit 0.6.1.11 in den Einstellungen ändern). Handy oder Laptop rufen **http://192.168.4.1** auf. Die Oberfläche ist eine einzige, komprimiert ausgelieferte Webseite (gzip, ETag); sie braucht **kein Internet** und **keine App**.
- Der ESP32 spricht per **Bluetooth Low Energy** (Dienst `FFF0`, Merkmal `FFF1`) mit der **CoolLEDX-Tafel**. Die Tafel braucht keine veränderte Herstellerfirmware und wiederholt einmal hochgeladene Inhalte selbstständig. Das Handy selbst braucht kein Bluetooth.
- Der ESP32 verbindet sich nur für einen Auftrag, sendet und trennt wieder. Seit 0.6.1.10 nutzt er dafür **NimBLE** (Bibliothek NimBLE-Arduino von h2zero) statt des Bluedroid-Stacks der Arduino-Boardpakete.
- Texte, Bibliothek, Programme, Kurzwahlen und Animationen liegen **im ESP32** (NVS und LittleFS), nicht im Browser. Deshalb sehen alle verbundenen Geräte dasselbe.
- Firmware-Updates nur per USB, **kein OTA**.

## 2. Bedienung

- **Navigation:** am Handy über die Banane (Menü), am Laptop (ab etwa 1000 Pixel Fensterbreite) über eine feste Seitenleiste mit Logo, Version und allen Seiten.
- **Rahmen:** Die Seiten hängen an den echten Fensterkanten (auch in der iPhone-Web-App); nur Listen scrollen. Kurzwahl, Bibliothek, Programme, Animationen und Ambiente sind fensterhoch, das Bedienfeld sitzt unten bündig. Angepasst für kleine Displays (iPhone SE).
- **Bedienfeld unten:** Helligkeit, Tempo, Anzeige an/aus und die Tasten zum Erzwingen eines Anzeigeverhaltens (Linkslauf, Standbild usw.). Auf der Kurzwahl bleiben nur Linkslauf, Standbild und der Stift zum Bearbeiten. Bei laufender Animation sind die Anzeige-Tasten gesperrt (die Tafel spielt die Animation selbst).
- **Während einer Übertragung** (Lauftext, Blocktext, Seite, Ambiente, Animation) sind auf **allen** Geräten alle Knöpfe gesperrt, die senden oder etwas ändern; auf dem Bedienfeld steht „Übertragung läuft …“. Seitenwechsel und bereits geladene Listen gehen weiter. Der ESP32 antwortet in dieser Zeit nur mit einem kleinen Status, einer Warteseite oder „409 Übertragung läuft“. Helligkeit, Tempo, Modus und an/aus (etwa 1,3 s) sperren nicht.
- **Wenn der ESP32 hängt:** Kommt etwa 5 s keine Antwort, steht „ESP32 antwortet nicht …“ auf dem Bedienfeld. Nach einem Wächter-Neustart meldet jedes Gerät einmal „Der ESP32 hat sich neu gestartet … bitte noch einmal senden“, mit der Phase, in der es hing. Ohne WLAN steht stattdessen „Keine Verbindung zum ESP32 – bist du im WLAN „RavestickBoard“?“.
- **„Auf der Tafel“:** Ein kleiner mintfarbener Punkt mit Flugzeug markiert, was zuletzt erfolgreich gesendet wurde (Bibliothek, Programme, Animationen, Kurzwahl, Ambiente). Der ESP32 merkt es sich (NVS) und meldet es im Status. Scheitert ein Auftrag nach dem Beginn der Datenpakete, wird die Markierung gelöscht (die Tafel zeigt dann das Herstellerbild „CoolLED“).
- **Vorschau:** Lauftext, Blocktext, Animationen und die Bibliothek (am Laptop als Kasten rechts) zeigen die 64 × 16-LED-Matrix; Tempo-Stufenknopf (Schnecke, Vogel, Hase) wirkt nur auf die Vorschau.
- **Sprache und Meldungen:** Deutsch, mit Umlauten in allen Meldungen der Firmware und der Oberfläche. Fehler der Tafel erscheinen im Klartext (z. B. „Tafel lehnt Paket 1 von 241 ab …“).

## 3. Kurzwahl

Acht frei belegbare Kacheln (4 × 2 am Laptop) für schnellen Zugriff bei einer Veranstaltung. Belegbar mit Bibliothekseinträgen (Lauftext, Blocktext), Programmen, Animationen und Ambiente-Farben. Zuweisen über den Stift auf der Kurzwahl. Beschädigte Einträge stehen ausgegraut mit „(beschädigt)“ und sind nicht wählbar; fehlt ein Ziel, zeigt die Kachel „Animation fehlt“ und sendet nichts.

## 4. Lauftext

- **Schriften:** Original (Normal, Fett, im Original-Zeichensatz nachgebaut), Engschrift und **Mini** (ein- oder zweizeilig; einzeilig links, mittig oder rechts ausrichtbar; zweizeilig mit zwei Zeilenfarben).
- **Zeichen gestalten:** Farbe und Schrift lassen sich **pro Zeichen** wählen (Markieren, Farbe, Rückgängig/Wiederherstellen; Wischen und Doppeltipp-Wort am Handy). Gespeichert wird das als unsichtbare Steuerzeichen im Text (U+0090 bis U+009D; Format in [`TECHNIK.md`](TECHNIK.md)); die Firmware wertet sie beim Zeichnen aus, daher wirken sie auch in Bibliothek, Programmen und Kurzwahl. Texte ohne Marken bleiben unverändert gültig.
- **Datenbudget:** Die Oberfläche zeigt, wie viel von der Tafel-Obergrenze (30 KiB je Übertragung) der Text belegt. Große Texte werden in 384-Byte-Kacheln gestreamt statt in einem Vollbildpuffer gerendert; so bleibt der Heap klein.
- **Editor:** Senden und Speichern sind gesperrt, solange das Eingabefeld leer ist. „Speichern“ aktualisiert einen Bibliothekseintrag oder legt ihn als neue Variante mit eigener ID an; Vorlage, Kurzwahlen und Programme bleiben dabei unberührt. Ein Entwurf bleibt im Browser erhalten.

## 5. Blocktext

Bis zu **40 feste Seiten** mit Ausrichtung und Anzeigedauer je Seite, als Ganzes (ein Bildband) sendbar, mit Seitenwerkzeugen und Seitenplayer in der Vorschau. Zeichen gestalten, alle Schriften und Symbole wie beim Lauftext. Seiten ohne Marken werden wie früher gezeichnet; Seiten mit Farb- und Schriftmarken zeichnet die Firmware pixelgleich zur Vorschau (am Rechner Zeichen für Zeichen verglichen). Gespeicherte Blocktexte aus Ständen vor 0.6.1.6 (25 Plätze) werden weiter gelesen.

## 6. Symbole

- **85 eigene 16 × 16-Pixelgrafiken** in sieben Farben (Flaggen 16 × 12), im Text wie Buchstaben einsetzbar (Pixelart des Entwicklers; Lizenzlage in [`QUELLEN_UND_LIZENZEN.md`](QUELLEN_UND_LIZENZEN.md)).
- **Symbol-Menü** (Fenster von unten): feste Reiter (Zuletzt benutzt, **Alle Symbole**, Kategorien), Suche auf Deutsch und Englisch, Kacheln in echter LED-Optik; ein Tipp fügt ein, das Menü bleibt offen.
- **Umfärben:** Herz, Augen (nur die Iris), Auto, Zapfsäule, die vier Pfeile und der Strohhalm lassen sich im erweiterten Editor pro Zeichen umfärben; Zeilen- und Gesamtfarbe färben Symbole nie um. Der Farbwechsel fragt „Symbole mitfärben?“, wenn die Auswahl färbbare Symbole enthält.

## 7. Animationen

Ein eigener Bereich, getrennt von Lauftext, Blocktext und Programmen. Die Tafel speichert die Animation und spielt sie **selbst in Dauerschleife**, auch nach dem Ausschalten, bis etwas anderes gesendet wird.

- **Import:** drei gleichberechtigte Wege auf der Import-Seite: **GIF**, **Einzelbilder aus einem Bild** (früher „Bildstreifen“) und **Text-Raster** (`.RGBCMYW`, ein Zeichen je Pixel; zwölf fertige Beispiele, darunter das DVD-Logo in drei Fassungen, in [`assets/animationen/`](../assets/animationen/LIESMICH.md)).
- **Anpassen:** Ausschnitt-Rahmen im festen Seitenverhältnis 4 : 1 auf dem Quellbild (verschieben, Ecken ziehen, Mausrad, Zwei-Finger-Zoom; Voreinstellungen Einpassen, Füllen, Strecken, Original), Farbreduktion auf die sieben LED-Farben, Bildbereich, jedes n-te Bild, „Hin und zurück“, **Rückwärts abspielen**, Zeit je Bild, Name. Text-Raster sind 1 : 1 (kein Rahmen, keine Farbumsetzung).
- **Speichern und senden:** bis zu **40 Animationen** im ESP32, je höchstens **79 Bilder** (80 lehnt die Tafel ab). Senden aus der Datei, auch „Nur senden“ ohne Speichern; „Speichern“ überschreibt unter derselben Nummer (Kurzwahlen bleiben gültig), „Als Kopie speichern“ legt eine neue an. Dateien tragen eine CRC-32-Prüfsumme; beim Ersetzen bleibt die alte Datei erhalten, bis die neue vollständig ist. Neue Animationen bekommen die kleinste freie Nummer, Löschen lässt Kurzwahlen unberührt.
- **Oberfläche:** Das **Raster** ist die Standardansicht und ein Schnellmenü: Kachel markieren (lädt nichts), oben **Senden** oder **Stift**. Der Stift öffnet die **Liste als Editor** (große Vorschau, Leiste mit Plus für den Import, Senden, Bearbeiten, Umbenennen, Löschen; Sortieren mit Pfeilen, die Reihenfolge liegt im ESP32). Die Liste ist schlank; Vorschaubilder werden einzeln nachgeladen und im Browser gemerkt. Während eine Animation lädt, sind alle Schaltflächen gesperrt. **Seit 0.6.1.11** lädt das Antippen einer Zeile in der Liste nichts: die Vorschau zeigt das Standbild, die **Play-Taste** daneben lädt die Animation einmal und spielt sie, bis eine andere Zeile gewählt wird.
- **Verhalten auf der Tafel:** Tempo-Regler und Anzeigemodus wirken bei Animationen nicht (die Geschwindigkeit steckt in der Zeit je Bild). Das Senden dauert je nach Länge bis etwa eine Minute (79 Bilder: 52 s). Nach einer Animation setzt der erste Text-, Block- oder Ambiente-Auftrag den Modus hinter den Daten noch einmal.
- **Animationstest** (Einstellungen): sendet eingebaute Testmuster (Frame-Nummern, Vollbildfarben, Balken) als gespeicherte Animation und zeigt die Antwortcodes der Tafel in der Diagnose.

## 8. Ambiente und Tafelsteuerung

- **Ambiente:** sieben Farben als Kacheln, eine Antippen sendet sie als Vollbild; am Handy wie am Laptop untereinander.
- **Helligkeit, Tempo, Anzeige an/aus, Anzeigemodus** wirken sofort über eigene kurze Befehle, ohne den Inhalt neu zu senden.

## 9. Bibliothek und Programme

- **Bibliothek:** Lauftexte und Blocktexte speichern, benennen, sortieren, löschen (am Laptop auch mehrere markieren: Strg-/Cmd-Klick, Umschalt-Klick für Bereiche, Strg+A, Esc, Entf, mit Rückfrage und Verwendung). Lange Namen blenden weich aus, laufen beim Auswählen einmal durch und zeigen am Laptop den vollen Namen als Hinweis.
- **Programme:** Einträge nacheinander abspielen, entweder jeden im Original oder als gemeinsames **Laufband**; mit Pfeilen sortierbar, die Reihenfolge liegt im ESP32 und gilt für alle Geräte. Gemischte Programme laufen mit Gruppenwechsel per Timer.
- **Importname:** Beim Import entsteht der Name aus dem Dateinamen (Endung weg, `_`/`-` zu Leerzeichen, großer Anfangsbuchstabe).

## 10. Tafelverwaltung und Bluetooth

- **Meine Tafel:** Die Tafeladresse steht **nicht** im Code, sondern im ESP32 (NVS). Einstellungen: Tafel suchen (Trefferliste mit Name und Signalstärke), als „Meine Tafel“ speichern, eine **fremde Tafel** vorübergehend nutzen und per Knopf zurückwechseln, „Meine Tafel entfernen“.
- **Vor-Scan:** Vor jedem *neuen* Verbindungsaufbau lauscht der ESP bis zu 3 s passiv nach der Tafel und beendet den Scan beim Treffer. Wird die Tafel nicht gehört, aber andere Bluetooth-Geräte, gibt es keinen Verbindungsversuch und die Meldung „LED-Tafel nicht gefunden …“ (so hängt das Board nicht bei ausgeschalteter Tafel). Das Bluetooth-Zeichen im Seitenkopf zeigt den Zustand.
- **Senden:** Verbinden, MTU aushandeln (Meldung „MTU=… Text-Payload=… Pakete“), je Paket schreiben und auf die **Bestätigung der Tafel** warten, danach trennen. Bleibt die Bestätigung aus, wird eine Lauftext-Gruppe einmal nach einer Neuverbindung wiederholt. Ist die MTU zu klein, gibt es einmalig eine Neuverbindung.
- **Konkurrenz:** Die Original-App und der ESP32 können nicht gleichzeitig mit der Tafel verbunden sein; die App muss vorher getrennt werden.

## 11. Stabilität und Speicher

Der ESP32-C3 hat wenig Arbeitsspeicher; vieles in der Firmware dient dem Schutz davor, dass ein Gerät beim Bedienen den Controller zum Absturz bringt.

- **Wächter:** Kommt etwa 25 s kein Lebenszeichen aus dem Hauptlauf oder den Bluetooth-Schritten, startet der Wächter das Board neu (und meldet vorher alle WLAN-Geräte ab, damit sie sich wieder verbinden). **Absturzspur:** Die letzte Phase steht im RTC-Speicher und erscheint nach dem Neustart in Diagnose und Seriallog.
- **Heap-Schutz:** Lesende Listen antworten bei knappem freiem Heap mit **503** (der Browser wiederholt unsichtbar, schreibende Anfragen nie); die Startseite zeigt dann eine kleine Warteseite, die sich selbst neu lädt. Große Antworten (Animationsabruf in 1200-Byte-Stücken, Vorschaubilder zu je drei) prüfen freien Heap und größten freien Block vor dem Antworten.
- **Höchstens zwei WLAN-Geräte** gleichzeitig (Firmware-Konstante), damit der Speicher reicht.
- **Sparsame Exporte:** `http.txt`, `ram.txt` und der Diagnosebericht werden in kleinen Stücken ausgegeben und warten bei knappem Heap.
- **Bluetooth-Unterbau:** NimBLE belegt beim Start rund 64 KB statt 73 KB wie Bluedroid (gemessen im Hardwaretest 0.6.1.10).
- **Speicher sparen (seit 0.6.1.11):** Das Seitenband für Blocktexte entsteht erst beim Senden; Listenantworten gehen in Stücken bis 1 KB; die Oberfläche holt jede Liste beim Start nur einmal; bei knappem Speicher antworten Listen mit „bitte gleich noch einmal“, die Oberfläche fragt selbst erneut.

## 12. Diagnose

Menü → Diagnose, Export als Textdatei: Ereignisprotokoll (Aufträge, Bluetooth-Schritte, Fehler), Zähler (Versuche, Verbindungen, Pakete, Bestätigungen, Fehler), RAM-Messung (Start-Aufteilung vor und nach den Bausteinen, WLAN-Ereignisse, kleinster freier Heap und Stapel, System-Minimum), HTTP-Spur der langsamsten Anfragen mit Pfad, Absturzspur nach Hänger, WLAN-Clients mit den letzten drei Adressbytes und Signal, Größe des Sketches. Zusätzliche Exporte `ram.txt` und `http.txt`. Hilfe beim Deuten: [`DIAGNOSE.md`](DIAGNOSE.md).

## 13. Datensicherung und mehrere Geräte

- **JSON-Backup:** Backup exportieren (ganz oder nach Auswahl: Bibliothek, Programme, Animationen, Kurzwahlen; was Programme und Kurzwahlen brauchen, kommt automatisch mit) und wieder importieren (mit Fortschritt im Knopf): Einträge, Blocktexte, Programme, **Animationen** und Kurzwahlen kommen zurück; Symbole stehen richtig. Der Import legt nichts doppelt an (gleiche Namen und Inhalte werden erkannt) und verknüpft Kurzwahlen mit den neuen Nummern. Das WLAN-Passwort ist nie im Backup. Vor jedem Firmware-Wechsel ein Backup ziehen.
- **WLAN-Passwort (seit 0.6.1.11):** Einstellungen → WLAN-Passwort, 8 bis 63 Zeichen ohne Umlaute; danach startet das WLAN neu. Vergessen: BOOT-Taste am ESP32 im laufenden Betrieb 5 Sekunden halten (nicht beim Einstecken), dann gilt wieder das Standardpasswort.
- **WLAN-Puffer und Sicherheit:** Einstellungen → „WLAN-Puffer und Sicherheit“: Empfangspuffer „begrenzt“ (weniger Speicher, Voreinstellung) oder „Arduino-Standard“, wirkt nach einem Neustart; WPA2/WPA3 gemischt (fällt bei Problemen auf WPA2 zurück). Das Standardpasswort steht in den Einstellungen im Klartext.
- **Kurzbefehle:** Lauftext (nur Text), Kurzwahl 1 bis 8 oder eine Animation per ID ohne Browser auslösen, mit der Kurzbefehle-App/Siri am iPhone oder der App „HTTP Shortcuts“ unter Android. Anleitung: [KURZBEFEHLE.md](KURZBEFEHLE.md).
- **Programm und Senden:** Wer während eines laufenden Programms etwas sendet, beendet das Programm nach dem aktuellen Schritt; der neue Inhalt kommt danach von selbst.
- **Mehrere Geräte:** Änderungen eines Geräts erscheinen auf den anderen nach „Menü → Webinterface neu laden“; Bibliothek und Programme werden beim Seitenwechsel außerdem im Hintergrund aufgefrischt, wenn sie älter als 60 s sind. Gleichzeitiges Bearbeiten desselben Eintrags kann Änderungen überschreiben.
- **Blocktext-Format:** Seit 0.6.1.6 speichert die Firmware Blocktexte mit 40 Seitenplätzen; Stände bis 0.6.1.5 lesen sie danach nicht mehr (darum vorher ein Backup ziehen).

## 14. Grenzen

- Kein OTA; USB bleibt der Updateweg. Nur eine Tafel gleichzeitig, nur ein Bluetooth-Verbindungspartner (nicht zusammen mit der Original-App).
- Höchstens 79 Bilder je Animation, 40 Animationen, 40 Blocktext-Seiten, 30 KiB je Übertragung, zwei WLAN-Geräte.
- Ein Bluetooth-Hänger (SYS-15) ist bekannt, selten und wird vom Wächter abgefangen; die Ursache ist offen.
- Offene Ideen (Zeichen-Editor mit Stift, Komfortfunktionen, Uhr- und Zähleranzeigen) stehen in der [Roadmap](ROADMAP.md) und im [Themenspeicher](THEMENSPEICHER.md).
