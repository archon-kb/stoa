#!/usr/bin/env python3
"""
Генератор обложки og.png (1200×630) для Telegram-превью.

Требует ttf-файлы кириллических и латинских сабсетов в FONT_DIR.
Получить их так:

    npm pack @fontsource/unbounded @fontsource/golos-text @fontsource/jetbrains-mono
    # распаковать, затем из каждого files/*-{cyrillic,latin}-*.woff2:
    python3 -c "from fontTools.ttLib import TTFont; f=TTFont('X.woff2'); f.flavor=None; f.save('Y.ttf')"

Фон — подлинные строки Шеннона: приближения первого и второго порядка
из «A Mathematical Theory of Communication», 1948, раздел 3.
"""

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
import random, os

FONT_DIR = os.environ.get("FONT_DIR", "/tmp/ttf")
OUT = os.path.join(os.path.dirname(__file__), "..", "og.png")

W, H = 1200, 630
BLACK, PAPER, YELLOW, BLUE = "#0B0B0B", "#F2F1EC", "#FFD400", "#5C74FF"

FONTS = {
    "disp_c": "ub900-cyr.ttf",   "disp_l": "ub900-lat.ttf",
    "text_c": "golos500-cyr.ttf", "text_l": "golos500-lat.ttf",
    "mono_c": "jb700-cyr.ttf",   "mono_l": "jb700-lat.ttf",
}

img = Image.new("RGB", (W, H), BLACK)
d = ImageDraw.Draw(img)
T = lambda name, size: ImageFont.truetype(os.path.join(FONT_DIR, name), size)

# какой сабсет содержит какой символ
COV = {f: set(TTFont(os.path.join(FONT_DIR, f)).getBestCmap().keys()) for f in set(FONTS.values())}


def runs(text, primary, fallback):
    """каждый символ рисуем тем сабсетом, где он есть; приоритет — primary"""
    out, cur, curf = [], "", None
    for ch in text:
        f = primary if ord(ch) in COV[primary] else fallback
        if curf is None or f == curf:
            cur, curf = cur + ch, f
        else:
            out.append((cur, curf)); cur, curf = ch, f
    if cur:
        out.append((cur, curf))
    return out


def measure(text, prim, fall, size):
    return sum(d.textlength(t, font=T(f, size)) for t, f in runs(text, prim, fall))


def draw_mixed(xy, text, prim, fall, size, fill):
    x, y = xy
    for t, f in runs(text, prim, fall):
        ft = T(f, size)
        d.text((x, y), t, font=ft, fill=fill)
        x += d.textlength(t, font=ft)
    return x


# ---------- фон: подлинный шум Шеннона ----------
random.seed(1948)
SHANNON = ("XFOML RXKHRJFFJUJ ZLPWCFWKCYJ FFJEYVKCQSGHYD QPAAMKBZAACIBZLHJQD "
           "OCRO HLI RGWR NMIELWIS EU LL NBNESEBYA TH EEI ALHENHTTPA OOBTTVA NAH BRL ")
fn = T(FONTS["mono_l"], 19)
i = 0
for y in range(-4, H + 23, 23):
    dist = abs(y - H * 0.47) / (H * 0.5)
    g = int(20 + min(1, dist) * 14)          # к центру глуше, чтобы заголовок дышал
    line = "".join(SHANNON[(i + k) % len(SHANNON)] for k in range(110))
    d.text((-random.randint(0, 14), y), line, font=fn, fill=(g, g + 1, g + 1))
    i += random.randint(7, 41)

# ---------- плашка ветки ----------
tag = "КАК РАБОТАЕТ AI / 01"
tw = measure(tag, FONTS["mono_c"], FONTS["mono_l"], 21)
d.rectangle([56, 52, 56 + tw + 34, 104], fill=YELLOW)
draw_mixed((73, 63), tag, FONTS["mono_c"], FONTS["mono_l"], 21, BLACK)

# ---------- заголовок ----------
L1, L2a, L2b = "ЧТО ПРОИСХОДИТ", "ПОСЛЕ ", "ENTER"
size = 108
while size > 50:
    w1 = measure(L1, FONTS["disp_c"], FONTS["disp_l"], size)
    w2 = measure(L2a, FONTS["disp_c"], FONTS["disp_l"], size) + \
         d.textlength(L2b, font=T(FONTS["disp_l"], size))
    if max(w1, w2) <= W - 112:
        break
    size -= 2

y, lh = 228, int(size * 0.98)
draw_mixed((56, y), L1, FONTS["disp_c"], FONTS["disp_l"], size, PAPER)
y += lh
x = draw_mixed((56, y), L2a, FONTS["disp_c"], FONTS["disp_l"], size, PAPER)
ul = T(FONTS["disp_l"], size)
wb = d.textlength(L2b, font=ul)
d.rectangle([x - 8, y - int(size * 0.05), x + wb + 10, y + int(size * 1.03)], fill=YELLOW)
d.text((x, y), L2b, font=ul, fill=BLACK)

# ---------- нижняя полоса ----------
d.rectangle([8, H - 150, W - 8, H - 8], fill=(11, 11, 11))
draw_mixed((56, H - 118), "Ответа не существовало нигде,",
           FONTS["text_c"], FONTS["text_l"], 28, "#C7C9C6")
draw_mixed((56, H - 78), "пока вы не нажали Enter.",
           FONTS["text_c"], FONTS["text_l"], 28, "#C7C9C6")

fb = T(FONTS["disp_l"], 30)
d.text((W - 56 - d.textlength("STOA", font=fb), H - 86), "STOA", font=fb, fill=PAPER)
fy = T(FONTS["mono_l"], 18)
d.text((W - 56 - d.textlength("SHANNON 1948", font=fy), H - 116),
       "SHANNON 1948", font=fy, fill=BLUE)

d.rectangle([0, 0, W - 1, H - 1], outline=PAPER, width=8)
img.save(os.path.abspath(OUT), "PNG")
print("готово:", os.path.abspath(OUT))
