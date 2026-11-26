# Mischfarben (FRC)

Text-Raster mit je zwei oder drei Bildern (64 × 16, Bilder durch `---` getrennt). Jedes Bild ist eine Vollfarbe; das Auge mischt beim schnellen Wechsel eine Zwischenfarbe. Die Tafel kennt je Pixel nur Rot, Grün und Blau an oder aus, die Mischung entsteht also über den Anteil der Bilder, in denen ein Kanal leuchtet.

Import: Animationen, Plus, Text-Raster, Textdatei laden, Zeit je Frame 1 ms. Mischfarben wirken dunkler als die reinen Farben.

Diese sieben Farben hat Felix auf der Hardware getestet und für gut befunden (0.7.0 und 0.7.1):

| Datei | Bilder | Farbe |
|---|---|---|
| `orange_rot_gelb.txt` | Rot, Gelb | Orange |
| `orange_rotlastig_rot_rot_gelb.txt` | Rot, Rot, Gelb | Rot-Orange (die gewählte Orange-Variante) |
| `limette_gruen_gelb.txt` | Grün, Gelb | Limette |
| `himmelblau_blau_cyan.txt` | Blau, Cyan | Himmelblau |
| `hellblau_blau_weiss.txt` | Blau, Weiß | Hellblau |
| `pastellrot_rot_weiss.txt` | Rot, Weiß | sehr helles Rosa |
| `pastellgruen_gruen_weiss.txt` | Grün, Weiß | Pastellgrün (entspricht dem Mint der Oberfläche) |

## Flimmern

Bei 1 ms je Bild (Standard) ist nichts zu sehen. Ab 8 ms je Bild flimmert die Mischung leicht (Felix, 26.11.2026). Das passt zur Rechnung: zwei Bilder bei 8 ms ergeben 62,5 Hz, die Flimmergrenze liegt bei etwa 62 Hz. Für Mischfarben also höchstens 5 bis 7 ms je Bild verwenden; 1 ms bleibt der Standard.

## Aussortiert

Getestet und verworfen: Mint aus Grün und Cyan (Pastellgrün ist besser), Violett aus Blau und Magenta, Rosa aus Rot und Magenta (sieht wie Magenta aus), Pastellgelb (das reine Gelb wirkt ähnlich), die drei Graumischungen und die gelblastige Orange-Variante (wirkt wie ein schöneres Gelb, weil das reine Gelb einen leichten Grünstich hat).
