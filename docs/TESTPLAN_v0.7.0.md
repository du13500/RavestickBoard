# RavestickBoard · Hardwaretest v0.7.0-dev (WLAN-Puffer, Senden während Programm, Design, Export-Auswahl, Kurzbefehle)

**Stand: 21.11.2026 · vor dem Flashen geschrieben.** Ersetzt den Testplan von 0.6.1.11 (liegt in `archive/`). Dieselben Schritte stehen als Excel-Datei `RavestickBoard_Hardwaretest_v0.7.0.xlsx` bereit. **Hauptfrage:** Bringen die begrenzten WLAN-Puffer mehr freien Speicher, mit einem und mit zwei Geräten, ohne dass das WLAN spürbar langsamer wird? Dafür gibt es in den Einstellungen einen Umschalter („begrenzt“ gegen „Arduino-Standard“), damit beide Fälle im selben Build gemessen werden.

**Am Rechner geprüft, nicht auf der Hardware:** alle Tests mit Endung `0700` (Host-, Browser-, Build- und Paritätstests), darunter neue Hosttests für WLAN-Einstellungen, Upload von zwei Geräten, verlassenen Upload, sicheres Umbenennen und die festen Kurzbefehl-Routen. **Nicht geprüft:** Arduino-Compile, Hardware, Safari, echte Kurzbefehle auf iPhone oder Android. **Der erste Compile kann scheitern**; dann die Fehlermeldung schicken.

## Vorbereitung

1. Mit 0.6.1.11 ein JSON-Backup ziehen (Einstellungen → Backup exportieren). 0.6.1.11 als Rückfallversion aufbewahren.
2. Arduino IDE wie bisher (NimBLE-Arduino 2.5.2). `firmware/RavestickBoard_v0_7_0/RavestickBoard_v0_7_0.ino` öffnen, **alle acht Dateien** im Sketch-Ordner lassen.
3. iPhone und Laptop bereitlegen, die Tafel in Reichweite. In Abschnitt B ist **nur das iPhone** im WLAN (am Laptop WLAN aus).
4. Wo eine Zeile aus der Diagnose gefragt ist, steht dabei, wo sie zu finden ist. „Diagnose-Datei“ heißt: Menü → **Diagnose** → **TXT herunterladen** und die Datei öffnen. „RAM-Datei“ heißt: dort **RAM-Verlauf TXT**.
5. Nach dem Test Diagnose-Datei, RAM-Datei und `http://192.168.4.1/api/http.txt` exportieren; Seriallog mitlaufen lassen.

## A. Aufspielen und Start

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| A1 | Sketch kompilieren. Die beiden Zahlen am Ende (Programmspeicher, globale Variablen) **notieren**. | Kompiliert. Globale Variablen ungefähr wie 0.6.1.11 (die neuen Einstellungen brauchen nur wenige Byte). Bei einer Fehlermeldung: abbrechen und die Meldung schicken. | | |
| A2 | Flashen, mit dem WLAN `RavestickBoard` verbinden, Oberfläche öffnen. | Startseite wie gewohnt; Bibliothek, Programme, Animationen und Kurzwahlen sind noch da; Version 0.7.0-dev oben neben dem Namen. | | |
| A3 | Diagnose-Datei öffnen. Ganz oben im Kopf, direkt unter „WLAN-Passwort“, stehen zwei neue Zeilen: „WLAN-Puffer“ und „WLAN-Sicherheit“. | „WLAN-Puffer: begrenzt (4 statisch, 8 dynamisch)“ und „WLAN-Sicherheit: WPA2“. Umlaute in der Datei sind echte Umlaute (zum Beispiel „öffentlich“, „Wächter“). | | |
| A4 | Menü → Einstellungen → Abschnitt „WLAN-Passwort“. | Der Hinweis nennt das Standardpasswort im Klartext und fett: „Das Standardpasswort **Banane1248!** ist aktiv“. | | |
| A5 | In der Diagnose **TXT herunterladen** und **RAM-Verlauf TXT** antippen; Dateinamen ansehen. | Die Dateien heißen `RavestickBoard_Diagnose_v0.7.0-dev.txt` und `RavestickBoard_RAM_v0.7.0-dev.txt` (nicht mehr „v0.6.1.4“). | | |

## B. Test mit 1 Gerät (nur iPhone im WLAN)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| B1 | **Puffer „begrenzt“ (Voreinstellung).** Diagnose-Datei, Abschnitt „START-AUFTEILUNG“: Wert „Nach WLAN-AP“ **notieren**. | Mehr als in 0.6.1.11. Wie viel, ist die Frage dieses Tests. | | |
| B2 | Einige Sekunden nichts tun. Diagnose-Seite: Kachel „Freier Heap“ **notieren**. | Höher als mit 0.6.1.11 (dort mit einem Gerät etwa 35 bis 37 KB). | | |
| B3 | Ablauf „Last“: Seite neu laden, Bibliothek öffnen, einen Blocktext auswählen, einen Blocktext senden, eine Animation abspielen (Play) und senden, ein Programm starten und stoppen, eine Kurzwahl drücken. | Alles funktioniert wie gewohnt, kein Neustart. | | |
| B4 | Diagnose-Datei: „Minimal freier Heap“ (Kopf, unter „Freier Heap“) und „RAMTRACE niedrigstes System-Minimum beobachtet“ (darunter) **notieren**. | Deutlich über 10 KB. 0.6.1.11 als Vergleich: Werte aus der letzten Rückmeldung. | | |
| B5 | Eine GIF-Animation importieren und speichern; Zeit vom Antippen bis „Animation gespeichert“ **notieren**. | Läuft durch; die Zeit dient als Vergleich für B10. | | |
| B6 | **Umschalten auf „Arduino-Standard“:** Einstellungen → „WLAN-Puffer und Sicherheit“ → WLAN-Puffer „Arduino-Standard“ → Speichern. Rückfrage „ESP32 jetzt neu starten?“ mit OK bestätigen, danach wieder verbinden. | Das Board startet neu; nach dem Verbinden steht unter dem Umschalter „Aktiv: Arduino-Standard (32 Empfangspuffer)“. | | |
| B7 | Diagnose-Datei, Kopf: Zeile „WLAN-Puffer“. | „WLAN-Puffer: Arduino-Standard (4 statisch, 32 dynamisch)“. Die zweite Zeile der RAM-Datei nennt dieselbe Einstellung. | | |
| B8 | Wie B1 und B2: „Nach WLAN-AP“ und „Freier Heap“ **notieren**. | Werte wie in 0.6.1.11 (zum Vergleich mit B1 und B2). | | |
| B9 | Wie B3 und B4: Ablauf „Last“, danach „Minimal freier Heap“ und „RAMTRACE niedrigstes System-Minimum beobachtet“ **notieren**. | Kein Neustart. | | |
| B10 | Wie B5: dieselbe GIF importieren, Zeit **notieren**. | Vergleich mit B5: Ist „begrenzt“ spürbar langsamer? | | |

## C. Test mit 2 Geräten (iPhone und Laptop)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| C1 | **Puffer „Arduino-Standard“ (noch eingestellt aus B6).** Laptop dazu verbinden. Auf beiden Geräten abwechselnd den Ablauf „Last“ aus B3, etwa 10 Minuten. | Kein Neustart. Ein kurzes „Speicher knapp, bitte gleich noch einmal versuchen“ ist erlaubt. | | |
| C2 | Diagnose-Datei: „Minimal freier Heap“, „RAMTRACE niedrigstes System-Minimum beobachtet“ und im Abschnitt „ZÄHLER SEIT BOOT“ die Zeile „HTTP-Anfragen wegen knappem Heap vertagt (503)“ **notieren**. | 0.6.1.11 mit zwei Geräten als Vergleich. | | |
| C3 | Während das iPhone eine Animation speichert (Import, Speichern), am Laptop ebenfalls eine Animation speichern. | Der Laptop meldet „Gerade lädt ein anderes Gerät eine Animation hoch. Bitte kurz warten.“; das iPhone speichert ohne Abbruch zu Ende. | | |
| C4 | **Umschalten auf „begrenzt“** wie in B6 (WLAN-Puffer „begrenzt“, Neustart bestätigen). Beide Geräte wieder verbinden. | Unter dem Umschalter steht „Aktiv: begrenzte Puffer (8 Empfangspuffer)“; Diagnose-Datei: „WLAN-Puffer: begrenzt (4 statisch, 8 dynamisch)“. | | |
| C5 | Wie C1: beide Geräte abwechselnd, etwa 10 Minuten. | Kein Neustart. Seiten laden nicht spürbar langsamer als in C1. | | |
| C6 | Wie C2: dieselben drei Werte **notieren**. | Besser als in C2. | | |
| C7 | Wie C3 (gleichzeitig speichern) mit „begrenzt“. | Wie C3. | | |

## D. Senden während ein Programm läuft

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| D1 | Ein Programm mit mindestens drei Einträgen starten. Während es läuft, im Editor einen Lauftext senden. | Meldung „Das Programm wird beendet. Dein Inhalt folgt gleich …“. Nach dem laufenden Schritt endet das Programm und dein Lauftext erscheint, ohne dass du noch einmal tippen musst. | | |
| D2 | Programm wieder starten; jetzt eine Kurzwahl mit einem Text drücken. | Wie D1: Programm endet nach dem laufenden Schritt, dann kommt die Kurzwahl. | | |
| D3 | Programm wieder starten; eine Ambiente-Farbe antippen. | Wie D1. | | |
| D4 | Programm wieder starten; Helligkeit und Tempo verändern. | Das Programm läuft weiter, Helligkeit und Tempo ändern sich wie gewohnt. | | |
| D5 | Diagnose-Datei, Abschnitt „ZÄHLER SEIT BOOT“: Zeile „Programm durch Senden beendet (Anfragen)“. | Zählt die Fälle aus D1 bis D3 (mindestens 3). | | |

## E. Animationen

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| E1 | Animationen → Liste. Eine Animation auswählen, Play drücken. | Die Animation spielt; die Taste zeigt jetzt ein Quadrat (Stop). Nochmal drücken hält an, die Taste zeigt wieder Play. | | |
| E2 | In der Zeile und unter der Vorschau steht die ID („· ID 3“). Animation umbenennen und in der Liste verschieben. | Die ID bleibt gleich; Name und Reihenfolge ändern sich. | | |
| E3 | Beispiel-Animation „DVD-Logo ohne Ecke“ importieren (aus `assets/animationen`) und abspielen. | Das Logo verfehlt die Ecke jetzt um 5 Pixel. | | |
| E4 | Einen Import starten und während des Speicherns die Seite schließen. Danach 70 Sekunden warten und die Diagnose-Seite öffnen. | Bei „Letzte Ereignisse“ steht „Verlassener Animations-Upload nach 60 s ohne Daten verworfen“. Der nächste Import klappt normal. | | |

## F. Backup und Export

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| F1 | Einstellungen → Backup exportieren. | Ein Fenster „Backup exportieren“ mit vier Häkchen (Bibliothek, Programme, Animationen, Kurzwahlen), alle gesetzt. Exportieren erstellt das Backup wie bisher. | | |
| F2 | Nochmal exportieren, nur „Programme“ angehakt. | Die Meldung nennt nur die Bibliothekseinträge, die die Programme brauchen, die Programme und keine Animationen, „ohne Kurzwahlen“. | | |
| F3 | Backup aus F1 wieder einspielen (Backup zusammenführen). | Der Knopf zeigt den Fortschritt („Import: Eintrag 3 von 12 …“). Am Ende: „Import fertig: 0 neue Einträge, … vorhandene …; 0 neue Animationen, … vorhandene“. **Keine Animation doppelt** in der Liste. | | |
| F4 | Backup aus 0.6.1.11 (Vorbereitung) einspielen. | Wie F3: nichts doppelt. | | |

## G. WLAN-Sicherheit (WPA2/WPA3)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| G1 | Einstellungen → „WLAN-Puffer und Sicherheit“ → WLAN-Sicherheit „WPA2/WPA3“ → Speichern, Rückfrage bestätigen. | Das WLAN startet neu, alle Geräte verlieren kurz die Verbindung. | | |
| G2 | iPhone und Laptop wieder verbinden. | Beide kommen rein (gleiches Passwort). Diagnose-Datei, Kopf: „WLAN-Sicherheit: WPA2/WPA3“. Falls dort „(WPA2/WPA3 eingestellt, Start fehlgeschlagen)“ steht: notieren, das Board läuft dann mit WPA2 weiter. | | |
| G3 | Wie B2 (Freier Heap) **notieren**, mit WPA2/WPA3. | Vergleich mit B2: WPA3 braucht etwas mehr Speicher. | | |
| G4 | BOOT-Taste im laufenden Betrieb 5 Sekunden halten. | Standardpasswort aktiv **und** WLAN-Sicherheit wieder „WPA2“. | | |

## H. Kurzbefehle (Anleitung `docs/KURZBEFEHLE.md`)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| H1 | iPhone: Kurzbefehl „Tafeltext“ nach der Anleitung anlegen und per Siri auslösen. | Siri fragt nach dem Text; er erscheint weiß als Lauftext auf der Tafel. | | |
| H2 | iPhone: Kurzbefehl für Kurzwahl 1 anlegen und vom Home-Bildschirm auslösen. | Kurzwahl 1 startet. | | |
| H3 | iPhone: Kurzbefehl für eine Animation (ID aus E2) anlegen und auslösen. | Die Animation läuft auf der Tafel. | | |
| H4 | Kurzbefehl auslösen, während gerade etwas übertragen wird. | Das Board antwortet mit 409; nach ein paar Sekunden erneut auslösen klappt. | | |
| H5 | Optional, falls ein Android-Handy da ist: App „HTTP Shortcuts“, Kurzwahl 1 nach Anleitung. | Kurzwahl 1 startet vom Startbildschirm. | | |
| H6 | War die Anleitung verständlich? Wo hast du gehakt? | Kurz notieren. | | |

## I. Design (gleiche Funktion = gleiche Farbe)

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Gefällt mir so / lieber anders | Bemerkung |
|---|---|---|---|---|---|
| I1 | Editor, Einstellungen: Eingabefelder ansehen. | Der Rand der Felder ist heller und gut zu sehen (#66748a). | | | |
| I2 | Bibliothek, Programme, Animationen, Ambiente, Einstellungen, Diagnose nacheinander öffnen. | Die Seitenüberschriften sind überall gleich groß und stehen bündig mit dem Inhalt darunter. | | | |
| I3 | Editor (Lauftext und Blocktext), Einstellungen: Beschriftungen über den Feldern. | Gleiche Größe, Farbe und Ausrichtung (z. B. „Text · Datenverbrauch …“, „Schriftart“, „Text · Zeile 1“). | | | |
| I4 | Senden-Knöpfe und den Punkt „auf der Tafel“ vergleichen. | Beide im selben Grün. | | | |
| I5 | Gelbe Knöpfe und markierte Tabs vergleichen (Lauftext/Blocktext, Speichern, aktive Taste). | Ein einheitliches Gelb. | | | |
| I6 | Auf dem iPhone durch alle Seiten blättern. | Nichts verrutscht oder abgeschnitten. | | | |

## J. Kleinigkeiten und Audit-Reste

| Nr. | Was du tust | Was du siehst (Erwartung) | Ergebnis | Bemerkung |
|---|---|---|---|---|
| J1 | Startseite: unten den Stift (Kurzwahlen bearbeiten) antippen, dann eine Kurzwahl antippen. | Erscheint das Fenster nicht sofort, steht kurz „Kurzwahl n wird geladen …“. | | |
| J2 | Laptop: ein Fenster öffnen (z. B. Name beim Speichern, Export-Auswahl) und Escape drücken. | Das Fenster schließt; der Fokus springt zurück auf den Knopf, mit dem es geöffnet wurde. | | |
| J3 | Während einer Übertragung am Laptop mit der Tastatur (Tab, Enter) auf einen gesperrten Knopf gehen. | Nichts passiert; der Knopf ist gesperrt, nicht nur ausgegraut. | | |
| J4 | Symbole in Menü und Knöpfen ansehen (Sprühdose, Stern mit Plus, Achteck, Textausrichtung, Warnung). | Alle Symbole sind klar erkennbar. | | |
