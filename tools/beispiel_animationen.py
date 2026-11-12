"""Beispiel-Animationen (64 x 16, 7 Farben) als Text-Raster + bewegte Vorschau. Aufruf: python tools/beispiel_animationen.py assets/animationen"""
import math, sys, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H = 64, 16
CH = '.BGCRMYW'          # 0 aus, 1 blau, 2 gruen, 3 cyan, 4 rot, 5 magenta, 6 gelb, 7 weiss
B, G, C, R, M, Y, Wt = 1, 2, 3, 4, 5, 6, 7

def blank(): return [[0] * W for _ in range(H)]
def put(f, x, y, c):
    if 0 <= x < W and 0 <= y < H: f[y][x] = c
def line(f, x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for t in range(n + 1): put(f, round(x0 + (x1 - x0) * t / n), round(y0 + (y1 - y0) * t / n), c)
def bitmap(f, rows, x0, y0, c, sc=1):
    for y, r in enumerate(rows):
        for x, b in enumerate(r):
            if b not in '. ':
                cc = c if b == '#' else CH.index(b)
                for a in range(sc):
                    for d in range(sc): put(f, x0 + x * sc + a, y0 + y * sc + d, cc)

anims = []   # (dateiname, titel, frames, ms, beschreibung)

# 1 Herzschlag ---------------------------------------------------------------------------------
HEART_BIG = ['.##...##.', '####.####', '#########', '#########', '.#######.', '..#####..', '...###...', '....#....']
HEART_SMALL = ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...']
def ecg(u):     # Hoehe des EKG an Phase u (0..24), Grundlinie 9
    pts = [(0, 9), (3, 9), (4, 8), (5, 9), (8, 9), (9, 10), (10, 3), (11, 0), (12, 15), (13, 11), (14, 9), (17, 9), (18, 7), (20, 7), (21, 9), (24, 9)]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if a <= u <= b: return ya + (yb - ya) * (u - a) / max(b - a, 1e-9)
    return 9
fr = []
N = 24
for t in range(N):
    f = blank()
    # Herz: kurz gross, wenn der Ausschlag am linken Rand ankommt
    big = t in (11, 12, 13)
    if big: bitmap(f, HEART_BIG, 2, 4, R, 1); bitmap(f, [r for r in HEART_BIG], 2, 4, R)
    else: bitmap(f, HEART_SMALL, 3, 5, R)
    # Zeile aus zwei Pixeln Hoehe? nein: duennes EKG, laeuft nach links
    prev = None
    for x in range(14, 64):
        y = round(ecg(((x - 14) + t) % 24))
        if prev is not None: line(f, x - 1, prev, x, y, G)
        prev = y
    fr.append(f)
# grosses Herz in Groesse 2 waere 18 x 16 - zu breit; stattdessen Rand weiss beim Schlag
for t in (11, 12, 13):
    f = fr[t]
    for y in range(H):
        for x in range(13):
            if f[y][x] == 0 and any(0 <= x + dx < 13 and 0 <= y + dy < H and f[y + dy][x + dx] == R for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                f[y][x] = M if t == 12 else 0
anims.append(('herzschlag', 'Herzschlag', fr, 45, 'Herz pocht, EKG-Linie läuft nach links; ein Schlag pro Durchlauf (~1,1 s)'))

# 2 Equalizer ----------------------------------------------------------------------------------
N = 32; rnd = random.Random(4)
ph = [(rnd.random(), rnd.random(), rnd.choice((1, 2, 3)), rnd.choice((2, 3, 4, 5))) for _ in range(16)]
def eqh(i, t):
    a, b, k1, k2 = ph[i]
    v = 8 + 4.2 * math.sin(2 * math.pi * (k1 * t / N + a)) + 3.2 * math.sin(2 * math.pi * (k2 * t / N + b))
    return max(1, min(15, round(v)))
fr = []
for t in range(N):
    f = blank()
    for i in range(16):
        h = eqh(i, t); peak = max(eqh(i, (t - k) % N) for k in range(4))
        for y in range(h):
            c = R if y >= 12 else Y if y >= 8 else G
            for k in range(3): put(f, i * 4 + k, 15 - y, c)
        if peak > h:
            for k in range(3): put(f, i * 4 + k, 15 - peak, Wt)
    fr.append(f)
anims.append(('equalizer', 'Equalizer bunt', fr, 60, '16 hüpfende Balken grün/gelb/rot mit fallenden weißen Spitzen'))

# 3 Regenbogenwelle ----------------------------------------------------------------------------
N = 32; RAIN = [R, Y, G, C, B, M]
fr = []
for t in range(N):
    f = blank()
    prev = None
    for x in range(W):
        y = 7.5 + 5.8 * math.sin(2 * math.pi * (x + t) / 32)
        c = RAIN[int(((x + 2 * t) % 64) * 6 / 64)]
        yi = round(y)
        for d in (-1, 0, 1): put(f, x, yi + d, c)
        if prev is not None and abs(prev - yi) > 1: line(f, x, prev, x, yi, c)
        prev = yi
    fr.append(f)
anims.append(('regenbogenwelle', 'Regenbogenwelle', fr, 50, 'dicke Sinuswelle zieht nach links, Farben wandern doppelt so schnell'))

# 4 Sternenhimmel ------------------------------------------------------------------------------
N = 40; rnd = random.Random(11)
stars = [(rnd.randrange(W), rnd.randrange(14), rnd.randrange(N), rnd.choice((Wt, Wt, Y, C))) for _ in range(46)]
fr = []
for t in range(N):
    f = blank()
    for x, y, p, c in stars:
        u = (t - p) % N
        col = c if u < 14 else B if u < 18 or u >= N - 3 else 0
        if u in (5, 6) and c == Wt:   # kurzes Funkeln als Kreuz
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(f, x + dx, y + dy, B)
        if col: put(f, x, y, col)
    # Sternschnuppe Frame 8..23
    if 8 <= t < 24:
        k = t - 8; hx, hy = 70 - k * 5, 1 + k * 0.5
        for j in range(9):
            put(f, round(hx + j * 1.6), round(hy - j * 0.16), Wt if j == 0 else Y if j < 3 else R if j < 6 else M)
    fr.append(f)
anims.append(('sternenhimmel', 'Sternenhimmel', fr, 90, 'Sterne glimmen auf und verlöschen, einmal pro Durchlauf eine Sternschnuppe'))

# 5 RAVE blinkt --------------------------------------------------------------------------------
GL = {'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
      'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
      'V': ['#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
      'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####']}
N = 12; PAL = [M, C, Y, R, G, B]; rnd = random.Random(5)
spark = [[(rnd.randrange(W), rnd.randrange(H)) for _ in range(5)] for _ in range(N)]
fr = []
for t in range(N):
    f = blank()
    strobe = t in (5, 11)
    for x, y in spark[t]:
        if x < 7 or x > 56: put(f, x, y, Wt)
    for i, ch in enumerate('RAVE'):
        bitmap(f, GL[ch], 8 + i * 12, 1, Wt if strobe else PAL[(i + t) % 6], 2)
    fr.append(f)
anims.append(('rave_blinkt', 'RAVE blinkt', fr, 140, 'Buchstaben wechseln reihum die Farbe, zweimal pro Durchlauf weißer Blitz, Funken am Rand'))

# 6 Pfeile nach rechts -------------------------------------------------------------------------
N = 11
fr = []
for t in range(N):
    f = blank()
    for k in range(-1, 7):
        x0 = k * 11 + t - 3
        c = B if x0 < 18 else C if x0 < 40 else Wt
        for d in range(7):
            for w in (0, 1, 2):
                put(f, x0 + d + w, 1 + d, c); put(f, x0 + d + w, 14 - d, c)
    fr.append(f)
anims.append(('pfeile_rechts', 'Pfeile nach rechts', fr, 40, 'Winkel laufen nach rechts, nach rechts heller (blau → cyan → weiß)'))
# 6b Pfeile nach links (Spiegelbild: Winkel zeigen und laufen nach links, nach links heller)
fr = [[list(reversed(row)) for row in f] for f in fr]
anims.append(('pfeile_links', 'Pfeile nach links', fr, 40, 'Winkel laufen nach links, nach links heller (blau → cyan → weiß)'))

# 7 Lagerfeuer ---------------------------------------------------------------------------------
N = 24; rnd = random.Random(8)
fp = [(rnd.random(), rnd.random(), rnd.choice((1, 2, 3)), rnd.choice((3, 4, 5))) for _ in range(W)]
sparks = [(rnd.randrange(W), rnd.randrange(N), rnd.choice((Y, R, Wt))) for _ in range(14)]
fr = []
for t in range(N):
    f = blank()
    for x in range(W):
        a, b, k1, k2 = fp[x]
        base = 7 + 3 * math.sin(math.pi * x / 21) ** 2
        h = base + 2.2 * math.sin(2 * math.pi * (k1 * t / N + a)) + 1.6 * math.sin(2 * math.pi * (k2 * t / N + b + x / 7))
        h = max(3, min(14, round(h)))
        for y in range(h):
            c = Wt if y < 2 else Y if y < h * 0.55 else R
            put(f, x, 15 - y, c)
    for x, p, c in sparks:
        u = (t - p) % N
        if u < 8: put(f, x + (1 if u > 4 else 0), 15 - 11 - u // 2 + 4 - u, c) if False else put(f, x + (u // 4), 6 - u, c)
    fr.append(f)
anims.append(('lagerfeuer', 'Lagerfeuer', fr, 70, 'Flammen flackern (weiß/gelb/rot), Funken steigen auf'))

# 8 Smileys ------------------------------------------------------------------------------------
N = 16
def smiley(f, cx, wink, grin):
    for x in range(-7, 8):
        for y in range(-8, 8):
            if math.hypot(x, y + 0.5) <= 7.3: put(f, cx + x, 8 + y, Y)
    put(f, cx - 3, 5, 0); put(f, cx - 3, 6, 0)
    if wink: put(f, cx + 1, 6, 0); put(f, cx + 2, 6, 0); put(f, cx + 3, 6, 0)
    else: put(f, cx + 2, 5, 0); put(f, cx + 2, 6, 0)
    mouth = [(-4, 9), (-3, 10), (-2, 11), (-1, 11), (0, 11), (1, 11), (2, 10), (3, 9)]
    for x, y in mouth: put(f, cx + x, y, 0)
    if grin:
        for x in range(-3, 3): put(f, cx + x, 10, 0)
        for x in range(-1, 2): put(f, cx + x, 12, R)
fr = []
for t in range(N):
    f = blank()
    for k in range(4):
        s = (t // 4)
        smiley(f, 8 + k * 16, wink=(k == s and t % 4 in (1, 2)), grin=(k == s and t % 4 == 2))
    fr.append(f)
anims.append(('smileys', 'Smileys', fr, 130, 'vier Smileys, reihum zwinkert einer und streckt kurz die Zunge raus'))

# ---- Ausgabe: Text-Raster -------------------------------------------------------------------
for name, title, frames, ms, desc in anims:
    assert 2 <= len(frames) <= 79, name
    txt = '\n---\n'.join('\n'.join(''.join(CH[c] for c in row) for row in f) for f in frames) + '\n'
    (OUT / f'{name}.txt').write_text(txt, encoding='utf8')

# ---- Vorschau: ein GIF mit allen acht, gemeinsamer Takt 10 ms -----------------------------
RGB = [(24, 28, 38), (60, 110, 255), (50, 225, 95), (50, 225, 225), (255, 60, 50), (255, 60, 240), (255, 218, 50), (255, 255, 255)]
P = 5; CW, CHh = W * P, H * P; LAB = 22; PAD = 14
cols, rows = 2, 5
SW = cols * CW + (cols + 1) * PAD; SH = rows * (CHh + LAB) + (rows + 1) * PAD
font = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', 14) if Path('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf').exists() else ImageFont.load_default()
STEP = 20; TOTAL = 4800
cols_needed = [(17, 20, 28), (5, 8, 13)] + RGB + [(int(17 + (230 - 17) * k / 15), int(20 + (234 - 20) * k / 15), int(28 + (242 - 28) * k / 15)) for k in range(16)]
PALIMG = Image.new('P', (1, 1)); flat = [v for c in cols_needed for v in c]; PALIMG.putpalette(flat + [0] * (768 - len(flat)))
out = []
for tt in range(0, TOTAL, STEP * 2):
    im = Image.new('RGB', (SW, SH), (17, 20, 28)); d = ImageDraw.Draw(im)
    for i, (name, title, frames, ms, desc) in enumerate(anims):
        cx = PAD + (i % cols) * (CW + PAD); cy = PAD + (i // cols) * (CHh + LAB + PAD)
        d.text((cx, cy), f'{title}  ·  {len(frames)} Frames · {ms} ms', fill=(230, 234, 242), font=font)
        y0 = cy + LAB
        d.rounded_rectangle((cx - 3, y0 - 3, cx + CW + 2, y0 + CHh + 2), 6, fill=(5, 8, 13))
        f = frames[(tt // ms) % len(frames)]
        for y in range(H):
            for x in range(W):
                c = RGB[f[y][x]]
                d.ellipse((cx + x * P + 0.6, y0 + y * P + 0.6, cx + x * P + P - 1.2, y0 + y * P + P - 1.2), fill=c)
    out.append(im.quantize(palette=PALIMG, dither=Image.Dither.NONE))

out[0].save(OUT / 'vorschau.gif', save_all=True, append_images=out[1:], duration=STEP * 2, loop=0, optimize=True)
for name, title, frames, ms, desc in anims:
    print(f'{name:16} {len(frames):3} Frames {ms:4} ms  Schleife {len(frames)*ms/1000:.1f} s  – {desc}')
