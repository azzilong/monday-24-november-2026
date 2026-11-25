#!/usr/bin/env python3
"""Tuesday 24 November 2026 — The World in One Page.

Draws a dense newspaper front page (1024x1024) that sums up the day's
world news in one image, for make.fun bounty news-image-20261124.

Everything on the page is original flat vector art drawn in code with
Pillow: no photographs, no copied images, no network. The program is
fully deterministic — same input, same bytes out.

Layout (own grid): kicker + masthead date, subhead, story-count line,
stat strip of 6 numbers, region bar of 7 regions, 3 lead stories with
drawn scenes, a "Tuesday in UTC" daypart strip, 10 pictured mid stories,
a numbered world map, 22 more briefs, a DATE CHECK box, source footer.
35 stories, 7 regions.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 26
CONTENT = W - 2 * MARGIN

# Palette: cream paper, ink navy, brick red, deep teal, muted gold.
PAPER = (246, 241, 227)
INK = (23, 35, 59)
RED = (169, 50, 38)
TEAL = (14, 107, 92)
GOLD = (185, 138, 31)
GOLD_LIGHT = (232, 185, 60)
SLATE = (90, 104, 128)
LINE = (201, 191, 166)
NAVY_MAP = (27, 42, 69)
LAND = (217, 200, 154)
CREAM_DIM = (238, 231, 214)
WHITE = (250, 248, 240)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def wrap(text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width` px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(d, xy, text, fnt, fill, tracking=2):
    """Draw text with extra space between letters; returns total width."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += fnt.getlength(ch) + tracking
    return x - xy[0]


def text_w(text, fnt):
    return fnt.getlength(text)


def hrule(d, y, x0=MARGIN, x1=W - MARGIN, width=1, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def badge(d, x, y, label, fill=RED):
    """Small filled status badge; returns width used."""
    fnt = font(SANS_B, 8)
    w = int(fnt.getlength(label)) + 10
    d.rounded_rectangle([x, y, x + w, y + 12], radius=2, fill=fill)
    d.text((x + 5, y + 2), label, font=fnt, fill=WHITE)
    return w


def stat_cell(d, x, y, w, number, caption):
    f_big = font(SERIF_B, 25)
    f_cap = font(SANS, 8)
    nw = f_big.getlength(number)
    d.text((x + (w - nw) / 2, y), number, font=f_big, fill=INK)
    for i, ln in enumerate(wrap(caption, f_cap, w - 6)):
        lw = f_cap.getlength(ln)
        d.text((x + (w - lw) / 2, y + 30 + i * 10), ln, font=f_cap, fill=SLATE)


def region_bar(d, y, counts):
    """Proportional colour segments, one per region, with count labels.
    Segments too narrow for a label get a 66 px floor, paid for by the
    two widest segments, so every region stays named."""
    colours = [INK, RED, TEAL, GOLD, (96, 74, 120), (46, 92, 60), SLATE]
    total = sum(c for _, c in counts)
    widths = [max(24, int(CONTENT * n / total)) for _, n in counts]
    floor = 66
    extra = 0
    for i, w in enumerate(widths):
        if w < floor:
            extra += floor - w
            widths[i] = floor
    if extra:
        wide = sorted(range(len(widths)), key=lambda i: -widths[i])
        per = extra // 2
        for i in wide[:2]:
            widths[i] -= per
    widths[-1] += CONTENT - sum(widths) - 2 * (len(widths) - 1)
    x = MARGIN
    fnt = font(SANS_B, 9)
    for (name, n), col, w in zip(counts, colours, widths):
        d.rectangle([x, y, x + w - 2, y + 22], fill=col)
        label = f"{name} {n}"
        tw = fnt.getlength(label)
        if tw < w - 6:
            d.text((x + (w - tw) / 2, y + 6), label, font=fnt, fill=WHITE)
        x += w

# ---------------------------------------------------------------------------
# Story data: 35 stories, 7 regions. Every story happened, or was first
# reported, on Tuesday 24 November 2026. Sources are named beside each
# story on the page and listed in full in SOURCES.md.
# Regions: EUROPE 7, MIDDLE EAST 5, ASIA 8, AMERICAS 8, AFRICA 3,
# OCEANIA 1, GLOBAL 3.
# ---------------------------------------------------------------------------

LEADS = [
    {
        "n": 1, "place": "SANTA CLARA · TECH", "region": "AMERICAS",
        "headline": "NVIDIA BRINGS BACK HUANG",
        "deck": "Jensen Huang is chief executive again, under two weeks "
                "after quitting — Trump says he talked the board round.",
        "source": "AP · Reuters", "badge": "CONFIRMED",
        "lonlat": (-122.0, 37.4), "art": "chip",
    },
    {
        "n": 2, "place": "BRUSSELS · SPACE", "region": "EUROPE",
        "headline": "ALLIES WARN OF A WEAPON IN SPACE",
        "deck": "NATO chief vows the alliance will defend space after "
                "reports Russia is readying a nuclear-armed satellite.",
        "source": "BBC · Reuters", "badge": "REPORTED",
        "lonlat": (4.4, 50.8), "art": "satellite",
    },
    {
        "n": 3, "place": "STRAIT OF HORMUZ · IRAN WAR", "region": "MIDDLE EAST",
        "headline": "IRAN DEFIES THE BLOCKADE AS TANKERS BURN",
        "deck": "Tehran vows \u201call available means\u201d against the US "
                "naval blockade; three tankers hit mines in Hormuz.",
        "source": "Reuters · AP", "badge": "REPORTED",
        "lonlat": (56.5, 26.5), "art": "tankers",
    },
]

MIDS = [
    {"n": 4, "place": "OFF BENGHAZI · WAR AT SEA",
     "headline": "UKRAINE OWNS THE LIBYA SHIP STRIKES",
     "deck": "Kyiv confirms it hit two Russian vessels off Benghazi on "
             "Sunday; Tripoli demands answers.",
     "source": "Reuters · AP", "badge": "CONFIRMED", "region": "AFRICA",
     "lonlat": (20.1, 32.1), "art": "ship"},
    {"n": 5, "place": "GAZA CITY · WAR",
     "headline": "GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
     "deck": "Naeem Abu Nahel and six others die in Israeli strikes, "
             "among them two police officers.",
     "source": "Reuters · AP", "badge": "CONFIRMED", "region": "MIDDLE EAST",
     "lonlat": (34.5, 31.5), "art": "blast"},
    {"n": 6, "place": "ZAPORIZHZHIA · WAR",
     "headline": "TWO DEAD IN ZAPORIZHZHIA NIGHT ATTACK",
     "deck": "A Russian overnight strike hits flats; 40 wounded, four "
             "of them children.",
     "source": "AP · Reuters", "badge": "CONFIRMED", "region": "EUROPE",
     "lonlat": (35.2, 47.8), "art": "flats"},
    {"n": 7, "place": "THE HAGUE · JUSTICE",
     "headline": "FOURTEEN NATIONS BACK THE ROHINGYA RULING",
     "deck": "Britain, Spain, Canada, Australia and ten more recognise "
             "the ICJ genocide finding on Myanmar.",
     "source": "Reuters · AP", "badge": "CONFIRMED", "region": "GLOBAL",
     "lonlat": (4.3, 52.1), "art": "scales"},
    {"n": 8, "place": "KOSHI · QUAKE",
     "headline": "MAGNITUDE 5.6 QUAKE SHAKES NEPAL",
     "deck": "A 5.6 tremor strikes Koshi province near the China "
             "border; no deaths reported.",
     "source": "AP · Reuters", "badge": "REPORTED", "region": "ASIA",
     "lonlat": (85.3, 27.9), "art": "quake"},
    {"n": 9, "place": "HONIARA · PACIFIC",
     "headline": "SOLOMONS TO END CHINA SECURITY PACT",
     "deck": "The Pacific nation says it will let its security deal "
             "with Beijing lapse.",
     "source": "AP · Reuters", "badge": "REPORTED", "region": "OCEANIA",
     "lonlat": (160.0, -9.6), "art": "island"},
    {"n": 10, "place": "TALLINN · EUROPE",
     "headline": "RUSSIA WARNS ESTONIA OF OPEN WAR",
     "deck": "Moscow says Tallinn's border closure risks open war; "
             "seven states back EU visa curbs on Russians.",
     "source": "Reuters · AP", "badge": "REPORTED", "region": "EUROPE",
     "lonlat": (24.7, 59.4), "art": "fence"},
    {"n": 11, "place": "WASHINGTON · IRAN WAR",
     "headline": "NETANYAHU PRESSES TRUMP ON IRAN",
     "deck": "Israel's PM urges the US president to resume strikes on "
             "Iran as talks stall.",
     "source": "AP · Reuters", "badge": "REPORTED", "region": "MIDDLE EAST",
     "lonlat": (-77.0, 38.9), "art": "flags"},
    {"n": 12, "place": "MEXICO CITY · CRIME",
     "headline": "MEXICO TO TRY \u2018EL CHAPO ISIDRO\u2019 ITSELF",
     "deck": "Mexico will prosecute the captured kingpin at home "
             "despite a US extradition request.",
     "source": "Reuters · AP", "badge": "CONFIRMED", "region": "AMERICAS",
     "lonlat": (-99.1, 19.4), "art": "gavel"},
    {"n": 13, "place": "NEW YORK · AI",
     "headline": "UN CHIEF WANTS AI RULES IN A YEAR",
     "deck": "Guterres calls for a multilateral framework to limit AI "
             "risks before his term ends.",
     "source": "AP · UN News", "badge": "CONFIRMED", "region": "GLOBAL",
     "lonlat": (-74.0, 40.7), "art": "globe"},
]

BRIEFS = [
    (14, "DRC", "Fighting near an Ituri hospital traps Ebola teams for a day.", "UN News", "AFRICA"),
    (15, "EU VISAS", "Seven states back curbs on Russian tourist visas.", "Kyiv Independent", "EUROPE"),
    (16, "DELTA SYSTEM", "Germany first to access Ukraine's Delta net.", "Kyiv Independent", "EUROPE"),
    (17, "IRAQ OIL", "Baghdad orders oil ministry to run Kurdish-held fields.", "Reuters", "MIDDLE EAST"),
    (18, "MEGASPEED", "US blacklists Singapore cloud firm Megaspeed.", "AP", "ASIA"),
    (19, "CANADA", "Pentagon says Ottawa falls short as a defence partner.", "AP", "AMERICAS"),
    (20, "DEATH ROW", "Trump to order federal death sentences expedited.", "AP", "AMERICAS"),
    (21, "EXAM CHEATS", "Seoul offers $375,000 to catch AI exam cheats.", "AP", "ASIA"),
    (22, "ADIZ", "Russian jets enter South Korea's air defence zone over the sea.", "AP", "ASIA"),
    (23, "TIANGONG", "China hosts a first foreign astronaut, from Pakistan.", "Straits Times", "ASIA"),
    (24, "COLOMBIA", "Car bomb wrecks buildings in Villavicencio.", "The Hindu", "AMERICAS"),
    (25, "ROHINGYA", "Malaysia to send 6,500 Rohingya refugees back to Myanmar.", "AP", "ASIA"),
    (26, "HOUTHIS", "Dozens reported dead in Saudi airstrikes on Yemen.", "AP", "MIDDLE EAST"),
    (27, "LIBYA PROBE", "UN mission urges an inquiry into the Benghazi port attacks.", "UN News", "AFRICA"),
    (28, "NEPAL AID", "India pledges a $1.62bn package for flood-hit Nepal.", "Reuters", "ASIA"),
    (29, "MYANMAR", "Britain sanctions generals after the ICJ genocide ruling.", "Reuters", "ASIA"),
    (30, "BREXIT", "Burnham: rejoining the EU 'unthinkable' without a vote.", "AP", "EUROPE"),
    (31, "MARKETS", "Nasdaq jumps 6.51% and the S&P 500 4.73% on the Nvidia bounce.", "Reuters", "GLOBAL"),
    (32, "ANDREW", "Ex-prince Andrew 'took a bribe', a court hears.", "Reuters", "EUROPE"),
    (33, "MEME GALA", "Trump hosts a gala for meme-coin backers as his token hits lows.", "AP", "AMERICAS"),
    (34, "CUBA", "WHO chief tours a health system in deep trouble.", "AP", "AMERICAS"),
    (35, "MEASLES", "Pennsylvania records a ninth measles death; 46 counties hit.", "AP", "AMERICAS"),
]

STATS = [
    ("2", "RUSSIAN SHIPS HIT OFF LIBYA"),
    ("40", "WOUNDED IN ZAPORIZHZHIA"),
    ("5.6", "NEPAL QUAKE MAGNITUDE"),
    ("6,500", "ROHINGYA TO BE RETURNED"),
    ("14", "NATIONS BACK ICJ RULING"),
    ("+6.51%", "NASDAQ ON THE DAY"),
]

REGIONS = [("EUROPE", 7), ("MIDDLE EAST", 5), ("ASIA", 8), ("AMERICAS", 8),
           ("AFRICA", 3), ("OCEANIA", 1), ("GLOBAL", 3)]

UTC_STRIP = [
    ("OVERNIGHT", "Zaporizhzhia hit"),
    ("MORNING", "NATO space alert"),
    ("MIDDAY", "14 back ICJ ruling"),
    ("AFTERNOON", "Huang back at Nvidia"),
]

DATE_CHECK = (
    "Left out — other days' news: COP31 close (23 Nov) · Bahrain strikes "
    "(21–22 Nov) · Peru quake (20 Nov) · Sparta II fire (21 Nov) · Las "
    "Vegas GP (22 Nov) · ICJ ruling itself (19 Nov) — only the 14-nation "
    "recognition is today's news. Wires read up to 02:00 UTC 25 Nov 2026."
)


# ---------------------------------------------------------------------------
# Lead illustrations (flat vector scenes, drawn in code).
# ---------------------------------------------------------------------------

def art_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 58, 52))
    # circuit traces
    for i in range(5):
        yy = y + 10 + i * 14
        d.line([(x + 8, yy), (x + w - 8, yy)], fill=(46, 110, 96), width=1)
        d.ellipse([x + w - 14, yy - 3, x + w - 8, yy + 3], fill=GOLD_LIGHT)
    for i in range(4):
        xx = x + 22 + i * 30
        d.line([(xx, y + 6), (xx, y + h - 6)], fill=(46, 110, 96), width=1)
    # central chip
    cx, cy, cs = x + w // 2, y + h // 2, 34
    d.rectangle([cx - cs, cy - cs, cx + cs, cy + cs], fill=(24, 35, 59),
                outline=GOLD_LIGHT, width=2)
    for i in range(-1, 2):
        d.line([(cx + i * 20, cy - cs - 8), (cx + i * 20, cy - cs)], fill=GOLD_LIGHT, width=3)
        d.line([(cx + i * 20, cy + cs), (cx + i * 20, cy + cs + 8)], fill=GOLD_LIGHT, width=3)
        d.line([(cx - cs - 8, cy + i * 20), (cx - cs, cy + i * 20)], fill=GOLD_LIGHT, width=3)
        d.line([(cx + cs, cy + i * 20), (cx + cs + 8, cy + i * 20)], fill=GOLD_LIGHT, width=3)
    d.text((cx - 13, cy - 11), "NV", font=font(SANS_B, 20), fill=GOLD_LIGHT)
    # rising arrow
    d.polygon([(x + w - 34, y + h - 12), (x + w - 16, y + 14), (x + w - 22, y + 14),
               (x + w - 22, y + h - 12)], fill=RED)
    d.polygon([(x + w - 40, y + 22), (x + w - 10, y + 22), (x + w - 25, y + 6)], fill=RED)


def art_satellite(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(13, 22, 44))
    for sx, sy in [(18, 12), (52, 26), (96, 10), (150, 30), (200, 14), (250, 24),
                   (280, 10), (120, 40), (220, 44), (30, 48)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=WHITE)
    # earth arc at the bottom
    d.ellipse([x - 60, y + h - 26, x + w + 60, y + h + 90], fill=(28, 84, 120))
    d.ellipse([x - 60, y + h - 26, x + w + 60, y + h + 90], outline=(90, 160, 190), width=2)
    # satellite body + panels
    cx, cy = x + w // 2, y + h // 2 + 2
    d.rectangle([cx - 70, cy - 7, cx - 22, cy + 7], fill=(90, 120, 160))
    d.rectangle([cx + 22, cy - 7, cx + 70, cy + 7], fill=(90, 120, 160))
    d.line([(cx - 70, cy), (cx - 22, cy)], fill=(140, 170, 210), width=1)
    d.line([(cx + 22, cy), (cx + 70, cy)], fill=(140, 170, 210), width=1)
    d.rectangle([cx - 20, cy - 12, cx + 20, cy + 12], fill=GOLD_LIGHT)
    d.rectangle([cx - 20, cy - 12, cx + 20, cy + 12], outline=INK, width=1)
    # warning ring
    d.ellipse([cx - 48, cy - 34, cx + 48, cy + 34], outline=RED, width=3)
    d.text((cx - 4, cy - 30), "!", font=font(SANS_B, 18), fill=RED)


def art_tankers(d, x, y, w, h):
    # dusk sky bands
    d.rectangle([x, y, x + w, y + 34], fill=(214, 138, 74))
    d.rectangle([x, y + 34, x + w, y + 52], fill=(190, 110, 70))
    d.ellipse([x + w - 52, y + 8, x + w - 20, y + 40], fill=(250, 220, 150))
    # sea
    d.rectangle([x, y + 52, x + w, y + h], fill=(30, 68, 96))
    d.line([(x, y + 56), (x + w, y + 56)], fill=(90, 150, 180), width=1)
    # three tankers with smoke
    for i, tx in enumerate([14, 108, 202]):
        ty = y + 58 + (i % 2) * 4
        d.rectangle([x + tx, ty, x + tx + 84, ty + 12], fill=(24, 35, 59))
        d.rectangle([x + tx + 56, ty - 10, x + tx + 70, ty], fill=(24, 35, 59))
        d.rectangle([x + tx + 12, ty - 8, x + tx + 20, ty], fill=RED)
        for s, (sx, sy, sr) in enumerate([(tx + 16, ty - 22, 7), (tx + 22, ty - 32, 9),
                                          (tx + 30, ty - 42, 6)]):
            d.ellipse([x + sx - sr, sy - sr, x + sx + sr, sy + sr],
                      fill=(120, 120, 118))
        d.ellipse([x + tx + 66, ty - 16, x + tx + 74, ty - 8], fill=(255, 120, 40))


# ---------------------------------------------------------------------------
# Mid-story mini scenes (small flat panels, one per story).
# ---------------------------------------------------------------------------

def art_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 214, 224))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(30, 68, 96))
    d.polygon([(x + 30, y + h - 14), (x + 70, y + h - 14), (x + 62, y + h - 26),
               (x + 38, y + h - 26)], fill=(24, 35, 59))
    d.rectangle([x + 52, y + h - 36, x + w - 40, y + h - 26], fill=(24, 35, 59))
    for dx, dy in [(120, 8), (132, 16), (112, 20)]:
        d.polygon([(x + dx, y + dy), (x + dx + 10, y + dy + 4), (x + dx, y + dy + 8),
                   (x + dx - 10, y + dy + 4)], fill=(255, 120, 40))


def art_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 205, 170))
    d.rectangle([x + 8, y + 18, x + 34, y + h - 8], fill=(120, 110, 96))
    d.rectangle([x + 40, y + 26, x + 62, y + h - 8], fill=(96, 88, 76))
    d.rectangle([x + 68, y + 14, x + 96, y + h - 8], fill=(120, 110, 96))
    cx, cy = x + w - 42, y + 16
    for dx, dy in [(0, -12), (10, -6), (12, 6), (0, 12), (-12, 6), (-10, -6)]:
        d.polygon([(cx, cy), (cx + dx, cy + dy), (cx + dx // 2 + 4, cy + dy // 2 + 8)],
                  fill=(255, 140, 40))
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 190, 60))


def art_flats(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 206, 214))
    d.rectangle([x + 14, y + 12, x + 66, y + h - 6], fill=(90, 100, 118))
    for r in range(3):
        for c in range(3):
            d.rectangle([x + 20 + c * 15, y + 18 + r * 12, x + 28 + c * 15, y + 26 + r * 12],
                        fill=(250, 220, 120))
    for sx, sy, sr in [(86, 14, 8), (96, 6, 10), (108, 14, 7)]:
        d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr], fill=(110, 110, 108))
    d.polygon([(x + 96, y + 30), (x + 116, y + 30), (x + 106, y + 44)], fill=RED)


def art_scales(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    cx = x + w // 2
    d.line([(cx, y + 6), (cx, y + h - 12)], fill=INK, width=3)
    d.line([(cx - 34, y + 12), (cx + 34, y + 12)], fill=INK, width=3)
    for sgn in (-1, 1):
        px = cx + sgn * 34
        d.line([(px, y + 12), (px, y + 22)], fill=INK, width=2)
        d.polygon([(px - 14, y + 22), (px + 14, y + 22), (px, y + 36)], fill=GOLD)
    d.ellipse([cx - 5, y + 2, cx + 5, y + 12], fill=RED)


def art_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 220))
    for gy in (12, 24, 36):
        d.line([(x + 4, y + gy), (x + w - 4, y + gy)], fill=(210, 204, 186), width=1)
    pts = [(x + 4, y + 24), (x + 24, y + 24), (x + 30, y + 10), (x + 36, y + 38),
           (x + 44, y + 16), (x + 52, y + 30), (x + 62, y + 6), (x + 70, y + 40),
           (x + 78, y + 22), (x + 92, y + 24), (x + 116, y + 24)]
    d.line(pts, fill=RED, width=2)
    d.text((x + w - 34, y + 4), "5.6", font=font(SANS_B, 11), fill=RED)


def art_island(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(150, 200, 220))
    d.ellipse([x + 18, y + 26, x + w - 18, y + h - 4], fill=(232, 214, 150))
    d.ellipse([x + 34, y + 22, x + w - 30, y + 34], fill=(96, 160, 90))
    d.line([(x + w // 2, y + 8), (x + w // 2, y + 26)], fill=INK, width=2)
    d.polygon([(x + w // 2, y + 8), (x + w // 2 + 16, y + 13), (x + w // 2, y + 18)],
              fill=RED)
    d.ellipse([x + 8, y + 6, x + 26, y + 20], fill=(250, 240, 200))


def art_fence(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 208, 190))
    for i in range(9):
        bx = x + 8 + i * 13
        d.rectangle([bx, y + 8, bx + 5, y + h - 8], fill=(70, 78, 92))
    d.rectangle([x + 6, y + 12, x + w - 6, y + 16], fill=(70, 78, 92))
    d.rectangle([x + 6, y + h - 14, x + w - 6, y + h - 10], fill=(70, 78, 92))
    d.rectangle([x + w - 44, y + 4, x + w - 8, y + 20], fill=RED)
    d.text((x + w - 40, y + 7), "STOP", font=font(SANS_B, 9), fill=WHITE)


def art_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    for fx, col1, col2 in [(26, (60, 90, 170), WHITE), (66, WHITE, (60, 90, 170))]:
        d.line([(x + fx, y + 8), (x + fx, y + h - 6)], fill=INK, width=2)
        d.rectangle([x + fx, y + 8, x + fx + 34, y + 22], fill=col1)
        d.rectangle([x + fx, y + 15, x + fx + 34, y + 22], fill=col2)
    d.text((x + w - 30, y + h - 18), "DC", font=font(SANS_B, 11), fill=SLATE)


def art_gavel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    d.rectangle([x + 18, y + 10, x + 62, y + 20], fill=(120, 82, 44))
    d.line([(x + 40, y + 20), (x + 40, y + h - 14)], fill=(120, 82, 44), width=5)
    d.rectangle([x + 22, y + h - 16, x + 58, y + h - 10], fill=(90, 60, 32))
    d.text((x + w - 34, y + 6), "MX", font=font(SANS_B, 11), fill=SLATE)


def art_globe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 224, 232))
    cx, cy, r = x + w // 2, y + h // 2, 17
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 130, 180))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=1)
    d.ellipse([cx - 7, cy - r, cx + 7, cy + r], outline=(200, 230, 240), width=1)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(200, 230, 240), width=1)
    for px, py in [(cx - 12, cy - 8), (cx + 10, cy + 6), (cx + 2, cy - 12)]:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=GOLD_LIGHT)
    d.text((x + w - 26, y + 4), "AI", font=font(SANS_B, 10), fill=INK)


MID_ART = {"ship": art_ship, "blast": art_blast, "flats": art_flats,
           "scales": art_scales, "quake": art_quake, "island": art_island,
           "fence": art_fence, "flags": art_flags, "gavel": art_gavel,
           "globe": art_globe}
LEAD_ART = {"chip": art_chip, "satellite": art_satellite, "tankers": art_tankers}


# ---------------------------------------------------------------------------
# World map (stylised equirectangular, coarse hand-drawn continents).
# ---------------------------------------------------------------------------

# (lon, lat) polygons, deliberately coarse — a schematic, not a survey.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-60, 62),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-117, 33), (-125, 40), (-125, 49), (-150, 60), (-168, 66)],
    # South America
    [(-78, 7), (-60, 10), (-50, 0), (-35, -8), (-40, -22), (-48, -28),
     (-58, -38), (-65, -45), (-70, -54), (-73, -37), (-70, -18), (-78, 7)],
    # Africa
    [(-17, 15), (-10, 30), (10, 37), (20, 32), (32, 31), (43, 12),
     (51, 11), (40, -5), (35, -18), (28, -33), (18, -35), (12, -18),
     (9, 4), (-8, 5), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 43), (0, 48), (5, 58), (18, 56), (28, 71), (45, 68),
     (68, 73), (100, 77), (130, 72), (160, 70), (178, 65), (162, 60),
     (140, 40), (127, 33), (120, 23), (105, 9), (95, 16), (80, 8),
     (72, 20), (60, 25), (48, 29), (35, 36), (27, 40), (20, 40),
     (12, 44), (3, 43), (-2, 37), (-10, 36)],
    # Australia
    [(114, -22), (122, -14), (132, -12), (142, -11), (150, -23), (153, -27),
     (146, -39), (140, -38), (132, -32), (124, -33), (114, -30), (114, -22)],
]

PIN_LABELS = {1: "SANTA CLARA", 2: "BRUSSELS", 3: "HORMUZ", 4: "BENGHAZI",
              7: "THE HAGUE", 10: "TALLINN", 12: "MEXICO CITY", 13: "NEW YORK"}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_MAP)
    # faint graticule
    for lon in range(-150, 181, 30):
        gx = x + (lon + 170) / 360 * w
        d.line([(gx, y), (gx, y + h)], fill=(38, 56, 86), width=1)
    for lat in (-30, 0, 30, 60):
        gy = y + (85 - lat) / 145 * h
        d.line([(x, gy), (x + w, gy)], fill=(38, 56, 86), width=1)

    def proj(lon, lat):
        return (x + (lon + 170) / 360 * w, y + (85 - lat) / 145 * h)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    # a few big islands as dots
    for lon, lat in [(139, 36), (104, 1), (18, -29), (100, -2), (147, -42)]:
        px, py = proj(lon, lat)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=LAND)
    # pins 1-13
    f_num = font(SANS_B, 9)
    f_lab = font(SANS, 8)
    for s in LEADS + MIDS:
        px, py = proj(*s["lonlat"])
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=GOLD_LIGHT, outline=INK, width=1)
        tw = f_num.getlength(str(s["n"]))
        d.text((px - tw / 2, py - 6), str(s["n"]), font=f_num, fill=INK)
        if s["n"] in PIN_LABELS:
            lab = PIN_LABELS[s["n"]]
            d.text((px + 10, py - 5), lab, font=f_lab, fill=WHITE)


# ---------------------------------------------------------------------------
# Page composition.
# ---------------------------------------------------------------------------

def draw_lead(img, d, s, x, y, w):
    art_y, art_h = y, 76
    # Render the scene on its own layer so nothing can spill past the
    # art box into the headline below it.
    layer = Image.new("RGB", (w, art_h), PAPER)
    ld = ImageDraw.Draw(layer)
    LEAD_ART[s["art"]](ld, 0, 0, w, art_h)
    img.paste(layer, (x, art_y))
    d.rectangle([x, art_y, x + w, art_y + art_h], outline=INK, width=1)
    ky = art_y + art_h + 4
    d.text((x, ky), s["place"], font=font(SANS_B, 10), fill=RED)
    hy = ky + 14
    hl = wrap(s["headline"], font(SERIF_B, 16), w)
    for i, ln in enumerate(hl[:2]):
        d.text((x, hy + i * 18), ln, font=font(SERIF_B, 16), fill=INK)
    dy = hy + len(hl[:2]) * 18 + 2
    for i, ln in enumerate(wrap(s["deck"], font(SERIF, 11), w)[:2]):
        d.text((x, dy + i * 13), ln, font=font(SERIF, 11), fill=INK)
    sy = dy + 2 * 13 + 3
    d.text((x, sy), s["source"], font=font(SANS, 9), fill=SLATE)
    bcol = TEAL if s["badge"] == "CONFIRMED" else SLATE
    bw = int(font(SANS_B, 8).getlength(s["badge"])) + 10
    badge(d, x + w - bw, sy - 1, s["badge"], fill=bcol)


def draw_mid(d, s, x, y, w):
    art_y, art_h = y, 42
    MID_ART[s["art"]](d, x, art_y, w, art_h)
    d.rectangle([x, art_y, x + w, art_y + art_h], outline=INK, width=1)
    # numbered circle, top-left of the art
    d.ellipse([x + 3, art_y + 3, x + 19, art_y + 19], fill=RED)
    f_n = font(SANS_B, 10)
    tw = f_n.getlength(str(s["n"]))
    d.text((x + 11 - tw / 2, art_y + 5), str(s["n"]), font=f_n, fill=WHITE)
    hy = art_y + art_h + 3
    hl = wrap(s["headline"], font(SANS_B, 11), w)
    for i, ln in enumerate(hl[:2]):
        d.text((x, hy + i * 13), ln, font=font(SANS_B, 11), fill=INK)
    dy = hy + len(hl[:2]) * 13 + 2
    for i, ln in enumerate(wrap(s["deck"], font(SERIF, 10), w)[:3]):
        d.text((x, dy + i * 12), ln, font=font(SERIF, 10), fill=INK)
    sy = dy + 3 * 12 + 1
    d.text((x, sy), s["place"] + " · " + s["source"], font=font(SANS, 8), fill=SLATE)


def draw_briefs(d, y0):
    col_w = (CONTENT - 20) // 2
    f_b = font(SANS_B, 9)
    f_t = font(SANS, 9)
    pitch = 10.4
    for i, (n, place, text, source, _reg) in enumerate(BRIEFS):
        col = i // 11
        row = i % 11
        x = MARGIN + col * (col_w + 20)
        y = y0 + row * pitch
        head = f"{n} {place} — "
        d.text((x, y), head, font=f_b, fill=INK)
        d.text((x + f_b.getlength(head), y),
               f"{text} ({source})", font=f_t, fill=INK)


def compose():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Top rules + kicker + masthead
    d.rectangle([MARGIN, 10, W - MARGIN, 13], fill=RED)
    hrule(d, 16)
    kicker = "THE WORLD IN ONE DAY"
    kf = font(SANS_B, 12)
    kw = sum(kf.getlength(c) + 2 for c in kicker) - 2
    draw_tracked(d, ((W - kw) / 2, 22), kicker, kf, INK, tracking=2)
    mast = "Tuesday 24 November 2026"
    mf = font(SERIF_B, 44)
    d.text(((W - mf.getlength(mast)) / 2, 36), mast, font=mf, fill=INK)
    hrule(d, 86, width=2)
    sub = ("Nvidia brings back Huang  ·  Allies warn of a weapon in space  ·  "
           "Iran defies the blockade")
    sf = font(SERIF, 13)
    d.text(((W - sf.getlength(sub)) / 2, 90), sub, font=sf, fill=INK)
    cnt = "35 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
    cf = font(SANS_B, 11)
    d.text(((W - cf.getlength(cnt)) / 2, 106), cnt, font=cf, fill=RED)
    hrule(d, 120)

    # Stat strip
    cell_w = CONTENT / 6
    for i, (num, cap) in enumerate(STATS):
        stat_cell(d, MARGIN + i * cell_w, 124, cell_w, num, cap)
        if i:
            d.line([(MARGIN + i * cell_w, 126), (MARGIN + i * cell_w, 160)],
                   fill=LINE, width=1)

    # Region bar
    region_bar(d, 168, REGIONS)
    hrule(d, 194)

    # Leads
    lead_w = (CONTENT - 24) // 3
    for i, s in enumerate(LEADS):
        draw_lead(img, d, s, MARGIN + i * (lead_w + 12), 198, lead_w)
    hrule(d, 366)

    # Tuesday in UTC strip
    uf = font(SANS_B, 10)
    ux = MARGIN
    d.text((ux, 370), "TUESDAY IN UTC", font=uf, fill=RED)
    ux += uf.getlength("TUESDAY IN UTC") + 14
    it_f = font(SANS, 10)
    parts = []
    for tag, what in UTC_STRIP:
        parts.append((tag, what))
    for j, (tag, what) in enumerate(parts):
        seg = f"{tag} — {what}"
        if j:
            d.text((ux, 370), "·", font=it_f, fill=SLATE)
            ux += it_f.getlength("·") + 8
        d.text((ux, 370), tag, font=uf, fill=INK)
        ux += uf.getlength(tag) + 4
        d.text((ux, 370), "— " + what, font=it_f, fill=INK)
        ux += it_f.getlength("— " + what) + 10
    hrule(d, 390)

    # Mids: 2 rows x 5
    mid_w = (CONTENT - 48) // 5
    for r in range(2):
        y0 = 394 + r * 118
        for c in range(5):
            s = MIDS[r * 5 + c]
            draw_mid(d, s, MARGIN + c * (mid_w + 12), y0, mid_w)
    hrule(d, 630)

    # Map
    tf = font(SANS_B, 11)
    d.text((MARGIN, 634), "WHERE IT HAPPENED — 13 PLACES, NUMBERED AS THE STORIES",
           font=tf, fill=INK)
    lg = "GOLD PIN = A PICTURED STORY"
    d.text((W - MARGIN - font(SANS, 9).getlength(lg), 635), lg,
           font=font(SANS, 9), fill=SLATE)
    draw_map(d, MARGIN, 648, CONTENT, 146)
    hrule(d, 798)

    # Also on...
    d.text((MARGIN, 802), "ALSO ON TUESDAY 24 NOVEMBER 2026 — 22 MORE STORIES",
           font=tf, fill=INK)
    draw_briefs(d, 818)
    hrule(d, 936)

    # DATE CHECK box
    d.rectangle([MARGIN, 940, W - MARGIN, 984], outline=RED, width=2)
    d.text((MARGIN + 8, 944), "DATE CHECK — WHAT WE LEFT OUT",
           font=font(SANS_B, 10), fill=RED)
    for i, ln in enumerate(wrap(DATE_CHECK, font(SANS, 9), CONTENT - 16)):
        d.text((MARGIN + 8, 958 + i * 11), ln, font=font(SANS, 9), fill=INK)

    # Footer
    ff = font(SANS, 9)
    f1 = ("Every story here happened, or was first reported, on Tuesday "
          "24 November 2026. Sources named beside each story · Original drawings.")
    d.text(((W - ff.getlength(f1)) / 2, 990), f1, font=ff, fill=SLATE)
    f2 = "Drawn in code · No photographs · Tuesday 24 November 2026"
    d.text(((W - ff.getlength(f2)) / 2, 1002), f2, font=ff, fill=SLATE)
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = compose()
    img.save(out, "PNG")
    print(f"wrote {out} {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
