#!/usr/bin/env python3
"""THE WORLD TODAY - a one-day newspaper front page for 19 November 2026.

Draws a 1024x1024 newspaper front page summing up the world news of
Thursday 19 November 2026 (stories reported 18-19 Nov 2026) and writes
exactly one PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Pure Python 3.13 standard library. No network, no randomness, no time:
two runs produce byte-identical output. The 5x7 pixel font, the PNG
encoder and every illustration below were written for this entry.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (24, 24, 30)
RED = (178, 34, 34)
BLUE = (28, 58, 112)
NAVY = (16, 26, 54)
GOLD = (214, 164, 32)
TEAL = (18, 110, 105)
SKY = (140, 190, 220)
NIGHT = (14, 18, 44)
NEON = (255, 64, 170)
ORANGE = (232, 110, 24)
GREEN = (34, 120, 60)
GREY = (110, 108, 100)
LIGHT = (228, 222, 208)
WHITE = (255, 255, 255)
BLACK = (8, 8, 12)
YELLOW = (240, 210, 60)
SAND = (226, 205, 160)

# ------------------------------------------------------------------ image
PIX = bytearray(bytes(PAPER) * (W * H))
CLIP = None  # optional (x0, y0, x1, y1) device-space clip for artwork


def px(x, y, c):
    if CLIP is not None:
        if not (CLIP[0] <= x <= CLIP[2] and CLIP[1] <= y <= CLIP[3]):
            return
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def hline(x0, x1, y, c, t=1):
    for yy in range(y, y + t):
        for xx in range(x0, x1 + 1):
            px(xx, yy, c)


def vline(x, y0, y1, c, t=1):
    for xx in range(x, x + t):
        for yy in range(y0, y1 + 1):
            px(xx, yy, c)


def line(x0, y0, x1, y1, c):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= r * r:
                px(xx, yy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
    for yy in range(ymin, ymax + 1):
        xs = []
        for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
            if ay == by:
                continue
            if min(ay, by) <= yy <= max(ay, by):
                xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
        if len(xs) >= 2:
            for xx in range(int(min(xs)), int(max(xs)) + 1):
                px(xx, yy, c)


# ------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
G = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}

CW = 6  # advance per glyph in font units (5 + 1 space)


def text_w(s, scale):
    return (len(s) * CW - 1) * scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = G.get(ch, G[' '])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '1':
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += CW * scale
    return cx


def draw_centred(cx, y, s, scale, c):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap(s, scale, maxw):
    words = s.upper().split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ------------------------------------------------------------ illustrations
def art_gta(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    disc(x + w // 2, y + h - 26, 34, ORANGE)
    disc(x + w // 2, y + h - 26, 26, YELLOW)
    # skyline
    base = y + h - 26
    towers = [(0, 52, 44), (46, 78, 38), (86, 60, 46), (134, 92, 40),
              (176, 66, 44), (222, 84, 38), (262, 58, 46), (308, 76, 42),
              (352, 62, 44), (398, 88, 38), (442, 70, 46), (488, 80, 40)]
    for dx, th, tw in towers:
        tx = x + dx
        rect(tx, base - th, tw, th, (26, 30, 66))
        for wy in range(base - th + 6, base - 6, 12):
            for wx in range(tx + 5, tx + tw - 5, 11):
                if (wx * 7 + wy * 3) % 5 == 0:
                    rect(wx, wy, 4, 5, GOLD)
    # neon sign band
    rect(x, base - 8, w, 8, NEON)
    # palms
    for px0 in (x + 30, x + w - 46):
        line(px0, base, px0 + 8, base - 34, GREEN)
        for a in (-22, -10, 2, 14):
            line(px0 + 8, base - 34, px0 + 8 + a, base - 44, GREEN)
    # car
    cx0 = x + w // 2 - 46
    rect(cx0, base - 22, 92, 16, RED)
    rect(cx0 + 18, base - 34, 52, 14, RED)
    rect(cx0 + 24, base - 32, 40, 10, SKY)
    disc(cx0 + 20, base - 4, 8, BLACK)
    disc(cx0 + 72, base - 4, 8, BLACK)
    disc(cx0 + 20, base - 4, 3, GREY)
    disc(cx0 + 72, base - 4, 3, GREY)
    # big VI
    draw_text(x + w - 92, y + 8, "VI", 6, WHITE)
    draw_text(x + 10, y + 8, "GTA", 4, NEON)


def art_summit(x, y, w, h):
    rect(x, y, w, h, SKY)
    # Shenzhen towers
    base = y + h
    for dx, th, tw in [(8, 62, 34), (48, 96, 30), (84, 74, 36), (126, 108, 30),
                       (162, 82, 34), (202, 100, 30), (238, 68, 34), (278, 90, 30)]:
        rect(x + dx, base - th, tw, th, BLUE)
        rect(x + dx + 4, base - th - 8, tw - 8, 8, BLUE)
    # table + three leaders
    rect(x + 40, base - 34, w - 80, 10, (120, 72, 40))
    rect(x + 52, base - 24, 8, 24, (90, 54, 28))
    rect(x + w - 60, base - 24, 8, 24, (90, 54, 28))
    for i, c in enumerate((RED, GOLD, BLUE)):
        fx = x + 66 + i * 86
        rect(fx, base - 66, 34, 32, c)          # suit
        disc(fx + 17, base - 78, 13, (238, 205, 170))  # head
        rect(fx + 10, base - 74, 14, 4, INK)   # hair
    # flags
    rect(x + 60, y + 8, 52, 30, WHITE)
    for r in range(3):
        rect(x + 60, y + 8 + r * 10, 52, 5, (180, 30, 30) if r % 2 == 0 else WHITE)
    rect(x + 60, y + 8, 22, 16, BLUE)
    rect(x + w - 112, y + 8, 52, 30, RED)
    disc(x + w - 100, y + 18, 4, GOLD)
    disc(x + w - 84, y + 14, 2, GOLD)
    disc(x + w - 84, y + 26, 2, GOLD)
    rect(x + w // 2 - 26, y + 8, 52, 30, WHITE)
    rect(x + w // 2 - 26, y + 8, 52, 10, WHITE)
    rect(x + w // 2 - 26, y + 18, 52, 10, BLUE)
    rect(x + w // 2 - 26, y + 28, 52, 10, RED)


def art_voyager(x, y, w, h):
    rect(x, y, w, h, BLACK)
    for i in range(46):
        sx = x + (i * 53 + 11) % w
        sy = y + (i * 37 + 7) % h
        px(sx, sy, WHITE)
        if i % 7 == 0:
            px(sx + 1, sy, WHITE)
    # Earth
    disc(x + 44, y + h - 34, 24, BLUE)
    rect(x + 24, y + h - 40, 40, 10, GREEN)
    rect(x + 30, y + h - 26, 28, 8, GREEN)
    # spacecraft: gold dish + body + boom
    cx, cy = x + w - 120, y + 62
    tri(cx - 34, cy - 26, cx + 34, cy - 26, cx, cy + 6, GOLD)
    rect(cx - 16, cy + 6, 32, 18, (200, 200, 210))
    line(cx + 16, cy + 12, cx + 62, cy + 30, WHITE)
    disc(cx + 62, cy + 30, 4, RED)
    line(cx - 16, cy + 16, cx - 58, cy + 34, WHITE)
    disc(cx - 58, cy + 34, 3, YELLOW)
    # signal arc
    ring(x + 44, y + h - 34, 62, TEAL, 2)
    ring(x + 44, y + h - 34, 82, TEAL, 2)
    draw_text(x + 12, y + 8, "1 LIGHT-DAY", 3, YELLOW)


def art_summit_s(x, y, w, h):
    # Short-box version: flags row + three leaders, for a ~46px tall box.
    rect(x, y, w, h, SKY)
    base = y + h
    for dx, th, tw in [(8, 22, 30), (44, 30, 26), (76, 20, 30), (112, 26, 26),
                       (144, 20, 30), (180, 28, 26), (212, 22, 30), (248, 26, 26),
                       (284, 20, 30), (316, 24, 26)]:
        rect(x + dx, base - th, tw, th, BLUE)
    rect(x + 30, base - 16, w - 60, 6, (120, 72, 40))
    for i, c in enumerate((RED, GOLD, BLUE)):
        fx = x + 60 + i * 96
        rect(fx, base - 34, 30, 18, c)
        disc(fx + 15, base - 40, 10, (238, 205, 170))
    rect(x + 8, y + 4, 34, 14, WHITE)
    rect(x + 8, y + 4, 34, 5, (180, 30, 30))
    rect(x + 8, y + 13, 34, 5, (180, 30, 30))
    rect(x + w - 42, y + 4, 34, 14, RED)
    disc(x + w - 34, y + 9, 3, GOLD)


def art_voyager_s(x, y, w, h):
    # Short-box version: starfield + dish + Earth, for a ~46px tall box.
    rect(x, y, w, h, BLACK)
    for i in range(40):
        sx = x + (i * 53 + 11) % w
        sy = y + (i * 29 + 5) % h
        px(sx, sy, WHITE)
    disc(x + 34, y + h - 12, 14, BLUE)
    rect(x + 24, y + h - 16, 20, 6, GREEN)
    cx, cy = x + w - 90, y + 18
    tri(cx - 26, cy - 12, cx + 26, cy - 12, cx, cy + 8, GOLD)
    rect(cx - 12, cy + 8, 24, 10, (200, 200, 210))
    line(cx + 12, cy + 10, cx + 44, cy + 20, WHITE)
    disc(cx + 44, cy + 20, 3, RED)
    draw_text(x + w // 2 - 66, y + 4, "1 LIGHT-DAY", 2, YELLOW)


def art_iran(x, y, w, h):
    rect(x, y, w, h, (232, 196, 140))
    rect(x, y + h - 26, w, 26, (30, 90, 130))
    for i in range(4):
        hline(x + (i * 57) % w, x + ((i * 57) % w) + 24, y + h - 18 + (i % 2) * 7, WHITE)
    # base on shore
    rect(x + 14, y + h - 48, 62, 22, GREY)
    rect(x + 22, y + h - 58, 10, 12, GREY)
    rect(x + 58, y + h - 58, 10, 12, GREY)
    # missile trails + bursts
    line(x + 90, y + 8, x + 150, y + 28, RED)
    line(x + 190, y + 6, x + 150, y + 28, RED)
    disc(x + 150, y + 30, 12, ORANGE)
    disc(x + 150, y + 30, 6, YELLOW)
    disc(x + 60, y + 22, 8, ORANGE)
    disc(x + 60, y + 22, 4, YELLOW)
    disc(x + 210, y + 26, 8, ORANGE)
    # ship
    rect(x + w - 96, y + h - 22, 80, 12, INK)
    rect(x + w - 80, y + h - 34, 26, 12, INK)
    rect(x + w - 74, y + h - 42, 6, 8, INK)


def art_eu(x, y, w, h):
    rect(x, y, w, h, BLUE)
    cx, cy = x + w // 2, y + h // 2 - 4
    for i in range(12):
        import math
        a = i * math.pi / 6
        sx = int(cx + 58 * math.cos(a))
        sy = int(cy + 22 * math.sin(a))
        disc(sx, sy, 4, GOLD)
    draw_text(x + w // 2 - 48, cy - 14, "45BN", 4, WHITE)
    draw_text(x + 8, y + 6, "EU", 3, GOLD)


def art_gaza(x, y, w, h):
    rect(x, y, w, h, SAND)
    rect(x, y + h - 30, w, 30, (190, 160, 110))
    # yellow line
    hline(x, x + w, y + h - 28, YELLOW, 6)
    # tank
    tx, ty = x + 52, y + h - 40
    rect(tx, ty, 84, 18, (90, 92, 70))
    rect(tx + 22, ty - 12, 40, 12, (90, 92, 70))
    line(tx + 58, ty - 8, tx + 104, ty - 14, (70, 72, 54))
    for i in range(5):
        disc(tx + 10 + i * 16, ty + 18, 6, INK)
    # tents
    for i in range(3):
        bx = x + w - 118 + i * 36
        tri(bx, y + h - 30, bx + 16, y + h - 44, bx + 32, y + h - 30, WHITE)


def art_anthropic(x, y, w, h):
    rect(x, y, w, h, (240, 232, 214))
    base = y + h - 10
    bars = [int(h * f) for f in (0.22, 0.32, 0.28, 0.46, 0.38, 0.62)]
    for i, bh in enumerate(bars):
        bx = x + 12 + i * 34
        rect(bx, base - bh, 24, bh, TEAL if i < 5 else ORANGE)
    line(x + 110, y + 12, x + w - 14, base - 6, RED)
    disc(x + w - 16, base - 8, 5, RED)
    draw_text(x + 10, y + 6, "$83", 5, INK)


def art_australia(x, y, w, h):
    rect(x, y, w, h, (200, 225, 235))
    # parliament-ish building + flag pole
    rect(x + 30, y + h - 48, 110, 32, WHITE)
    for i in range(5):
        rect(x + 40 + i * 20, y + h - 42, 8, 26, BLUE)
    tri(x + 30, y + h - 48, x + 85, y + h - 58, x + 140, y + h - 48, RED)
    line(x + w - 40, y + 10, x + w - 40, y + h - 20, INK)
    rect(x + w - 40, y + 10, 34, 22, BLUE)
    disc(x + w - 30, y + 21, 5, WHITE)
    # gavel
    line(x + w - 96, y + h - 34, x + w - 60, y + h - 52, (120, 72, 40))
    rect(x + w - 104, y + h - 40, 22, 12, (120, 72, 40))


def art_lpg(x, y, w, h):
    rect(x, y, w, h, (210, 226, 238))
    rect(x, y + h - 24, w, 24, (26, 80, 120))
    # tanker, funnels clear of the name text
    rect(x + 34, y + h - 38, 130, 18, (200, 60, 40))
    rect(x + 120, y + h - 52, 20, 14, WHITE)
    rect(x + 145, y + h - 52, 20, 14, WHITE)
    disc(x + 178, y + h - 52, 12, ORANGE)
    disc(x + 178, y + h - 52, 6, YELLOW)
    disc(x + 196, y + 16, 10, GREY)
    disc(x + 208, y + 8, 8, GREY)
    disc(x + 184, y + 6, 7, GREY)
    draw_text(x + 8, y + 4, "GAS HUSKY", 2, INK)


def art_peltola(x, y, w, h):
    rect(x, y, w, h, (226, 232, 244))
    # ballot paper + box, clear of the big number
    rect(x + w - 100, y + 6, 20, 24, WHITE)
    frame(x + w - 100, y + 6, 20, 24, RED, 2)
    rect(x + w - 78, y + h - 46, 64, 34, BLUE)
    rect(x + w - 84, y + h - 52, 76, 8, BLUE)
    rect(x + w - 52, y + h - 52, 24, 5, WHITE)
    draw_text(x + 8, y + 4, "56-44", 4, RED)


def art_measles(x, y, w, h):
    rect(x, y, w, h, (250, 238, 226))
    # virus circles with spikes
    for (cx, cy, r, c) in ((48, 18, 12, RED), (115, 14, 9, ORANGE),
                           (185, 26, 11, RED), (150, 46, 8, ORANGE)):
        for a in range(0, 360, 45):
            import math
            ex = int(cx + (r + 8) * math.cos(a * math.pi / 180))
            ey = int(cy + (r + 8) * math.sin(a * math.pi / 180))
            line(x + cx, y + cy, x + ex, y + ey, c)
        disc(x + cx, y + cy, r, c)
        disc(x + cx - 5, y + cy - 5, 4, (250, 200, 180))
        disc(x + cx + 6, y + cy + 4, 3, (250, 200, 180))
    draw_text(x + 8, y + h - 22, "5,400", 3, INK)


# ------------------------------------------------------------- page layout
def kicker(x, y, s, c=RED):
    draw_text(x, y, s, 2, c)


def panel(x, y, w, h, kick, head, cap, art, head_scale=2, art_h=74):
    global CLIP
    frame(x, y, w, h, INK, 2)
    ax, ay, aw = x + 6, y + 6, w - 12
    kicker(ax, ay, kick)
    CLIP = (ax, ay + 16, ax + aw, ay + 16 + art_h)
    art(ax, ay + 16, aw, art_h)
    CLIP = None
    hy = ay + 16 + art_h + 8
    lines = wrap(head, head_scale, aw)
    for i, ln in enumerate(lines[:2]):
        draw_text(ax, hy + i * (head_scale * 8 + 2), ln, head_scale, INK)
    cy = hy + len(lines[:2]) * (head_scale * 8 + 2) + 4
    for i, ln in enumerate(wrap(cap, 2, aw)):
        if cy + i * 16 > y + h - 8:
            break
        draw_text(ax, cy + i * 16, ln, 2, (64, 62, 58))


def masthead():
    rect(0, 0, W, 116, INK)
    draw_centred(W // 2, 10, "THE WORLD TODAY", 8, PAPER)
    hline(24, W - 24, 76, GOLD, 3)
    draw_centred(W // 2, 86, "THURSDAY 19 NOVEMBER 2026", 3, GOLD)


def footer():
    hline(16, W - 16, 970, INK, 3)
    draw_centred(W // 2, 978, "ALL STORIES REPORTED 18-19 NOV 2026", 3, RED)
    draw_centred(W // 2, 1002,
                 "ONE DAY IN PICTURES - DRAWN FROM REPORTS BY REUTERS, BBC, AP, NASA, CNN AND OTHERS",
                 2, (64, 62, 58))


BRIEFS = [
    "DEUTSCHE BANK FLAGGED $582M IN EPSTEIN-LINKED DEALS, LEAKED FILES SHOW",
    "NSA SECRET NETWORK DOWN FOR A SECOND DAY; OFFICIALS RULE OUT CYBERATTACK",
    "FED MINUTES: ALMOST ALL OFFICIALS EXPECT MORE RATE HIKES AHEAD",
    "BAYESIAN CREW 'UNAWARE' OF WIND RISK, UK REPORT FINDS",
    "HAALAND PENALTY SENDS NORWAY TO NATIONS LEAGUE LAST EIGHT",
    "CYCLONE AKVAN NEARS ANDHRA COAST; LANDFALL DUE FRIDAY",
    "NVIDIA'S KRESS PROMISES EARLY PAY RISES; H200 SALES TO CHINA END",
    "CARNEY: CANADA REBUILDS CHINA TIES, SEEKS 'RIGHT DEAL' WITH US",
]


def brief_strip(x, y, w, h):
    frame(x, y, w, h, INK, 2)
    draw_text(x + 10, y + 8, "WORLD IN BRIEF", 3, RED)
    hline(x + 10, x + w - 10, y + 34, INK, 2)
    for i, b in enumerate(BRIEFS):
        yy = y + 42 + i * 15
        disc(x + 16, yy + 5, 3, RED)
        draw_text(x + 26, yy, b, 2, INK)


def build():
    masthead()
    # lead: GTA VI
    panel(16, 124, 624, 300, "CULTURE - GAMES", "VICE CITY OPENS ITS DOORS",
          "GTA VI ROLLS OUT WORLDWIDE AT MIDNIGHT, 13 YEARS AFTER GTA V",
          art_gta, head_scale=4, art_h=160)
    # right column
    panel(652, 124, 356, 150, "DIPLOMACY - SHENZHEN", "THREE LEADERS, ONE TABLE",
          "TRUMP, XI AND PUTIN MEET TODAY AT APEC IN SHENZHEN", art_summit_s,
          head_scale=2, art_h=46)
    panel(652, 278, 356, 150, "SPACE - NASA", "VOYAGER 1: 1 LIGHT-DAY OUT",
          "16 BILLION MILES FROM EARTH, 49 YEARS AFTER LAUNCH", art_voyager_s,
          head_scale=2, art_h=46)
    # row B
    bw, gap = 242, 8
    bx = 16
    panel(bx, 432, bw, 182, "GULF - CONFLICT", "US AND IRAN TRADE FIRE AGAIN",
          "IRAN HITS US BASES IN KUWAIT, BAHRAIN", art_iran, art_h=72)
    bx += bw + gap
    panel(bx, 432, bw, 182, "EUROPE - UKRAINE", "EU OFFERS KYIV EUR 45BN LOAN",
          "KYIV PAYS ONLY IF RUSSIA PAYS", art_eu, art_h=72)
    bx += bw + gap
    panel(bx, 432, bw, 182, "GAZA - CEASEFIRE", "TANKS CROSS THE YELLOW LINE",
          "FIRST PUSH PAST LINE SINCE TRUCE", art_gaza, art_h=72)
    bx += bw + gap
    panel(bx, 432, bw, 182, "TECH - MARKETS", "ANTHROPIC IPO: $81.3BN",
          "SHARES AT $83, DEBUT TODAY AS ANT", art_anthropic, art_h=72)
    # row C
    bx = 16
    panel(bx, 622, bw, 170, "AUSTRALIA", "CANBERRA SANCTIONS SETTLERS",
          "3 PEOPLE, 4 GROUPS HIT OVER WEST BANK", art_australia, art_h=62)
    bx += bw + gap
    panel(bx, 622, bw, 170, "BLACK SEA", "TANKER SANK AFTER 4 HITS",
          "ALL 19 CREW RESCUED OFF BULGARIA", art_lpg, art_h=62)
    bx += bw + gap
    panel(bx, 622, bw, 170, "USA - SENATE", "PELTOLA WINS ALASKA: 56-44",
          "SENATE NOW 56-44 TO DEMOCRATS", art_peltola, art_h=62)
    bx += bw + gap
    panel(bx, 622, bw, 170, "HEALTH - USA", "US LOSES MEASLES-FREE STATUS",
          "5,400 CASES, WORST SINCE 1991", art_measles, art_h=62)
    # briefs + footer
    brief_strip(16, 800, 992, 162)
    footer()


# ------------------------------------------------------------- PNG encoder
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png():
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += PIX[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    build()
    data = encode_png()
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
