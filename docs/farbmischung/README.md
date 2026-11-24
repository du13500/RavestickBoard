# Testdateien Farbmischung (FRC)

Text-Raster mit je zwei Bildern (64 × 16, Bilder durch `---` getrennt). Jedes Bild ist eine Vollfarbe; das Auge mischt beim schnellen Wechsel eine Zwischenfarbe. Die Tafel kennt je Pixel nur Rot, Grün und Blau an oder aus, die Mischung entsteht also über den Anteil der Bilder, in denen ein Kanal leuchtet.

Import: Animationen, Plus, Text-Raster, Textdatei laden, Zeit je Frame 1 ms (danach 5 und 10 ms zum Vergleich). Mischfarben wirken dunkler als die reinen Farben.

| Datei | Bilder | erwartete Farbe |
|---|---|---|
| `orange_rot_gelb.txt` | Rot, Gelb | Orange (in 0.7.0 bestätigt) |
| `orange_rotlastig_rot_rot_gelb.txt` | Rot, Rot, Gelb | Rot-Orange |
| `orange_gelblastig_rot_gelb_gelb.txt` | Rot, Gelb, Gelb | Gelb-Orange |
| `limette_gruen_gelb.txt` | Grün, Gelb | Limette |
| `mint_gruen_cyan.txt` | Grün, Cyan | Mint |
| `himmelblau_blau_cyan.txt` | Blau, Cyan | Himmelblau |
| `violett_blau_magenta.txt` | Blau, Magenta | Violett |
| `rosa_rot_magenta.txt` | Rot, Magenta | Rosa |
| `hellblau_blau_weiss.txt` | Blau, Weiß | Hellblau |
| `pastellrot_rot_weiss.txt` | Rot, Weiß | Hellrot / Rosa |
| `pastellgruen_gruen_weiss.txt` | Grün, Weiß | Hellgrün |
| `pastellgelb_gelb_weiss.txt` | Gelb, Weiß | Hellgelb |
| `grau_rot_cyan.txt` | Rot, Cyan | Grau (Komplementärpaar) |
| `grau_gruen_magenta.txt` | Grün, Magenta | Grau |
| `grau_blau_gelb.txt` | Blau, Gelb | Grau |

Die Erwartungen sind Rechnung, keine Messung; Grün plus Blau ergibt wie bekannt nur ein dunkleres Cyan. Ergebnisse bitte im Testplan unter Abschnitt K eintragen.
