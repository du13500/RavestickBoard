# Symbol-Daten (ab 0.6.1.8)

`symbole_0618.txt` enthält die Symbol-Matrizen (Kopfzeile `@ <Nummer> <Name>`, darunter die Zeilen aus `. B G C R M Y W`; `.` = aus). Es sind eigene Pixelgrafiken, die Felix am 14.11.2026 geliefert hat. Nummern 0–63 behalten ihren Platz, 64 und höher sind neu. Mehr als 85 Nummern gibt es nicht; verworfene Nummern (48, 51–53, 56–58) bleiben leer.

Neu erzeugen (Repo-Wurzel):

```bash
python tools/generate_assets.py
python tools/sync_web.py
```

`generate_assets.py` schreibt die gepackten Sprites in `web/index.html` und in `RavestickBoard_Assets.h` (beide Kopien müssen gleich sein), danach erzeugt `sync_web.py` den gzip-Webheader. Die Schriftdaten (164 Zeichen Normal und Fett) werden nicht angefasst. Herkunft und Rechte: `docs/QUELLEN_UND_LIZENZEN.md`.

Weitere Dateien: `animationen/` (Beispiel-Animationen als Text-Raster, seit 0.6.1.6) und das Icon `lucide-banana-app-icon.svg`.
