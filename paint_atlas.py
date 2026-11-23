#!/usr/bin/env python3
"""Paint "ONE DAY ON EARTH" — a world-atlas poster summing up 23 Nov 2026.

Draws a stylized equirectangular world map with ten numbered story pins and
a legend below. All geometry is baked in; output is deterministic.
"""
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (11, 22, 38)
NAVY_SOFT = (16, 32, 54)
TEAL = (46, 125, 123)
TEAL_EDGE = (111, 179, 168)
GOLD = (232, 184, 75)
GOLD_DIM = (201, 162, 39)
RED = (214, 69, 65)
WHITE = (245, 246, 248)
MIST = (178, 190, 205)
FAINT = (120, 135, 155)

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Equirectangular frame: lon -180..180, lat 72..-58, equal scale both axes.
SCALE = 2.6
MAP_X0, MAP_Y0 = 44, 150
LAT_TOP = 72.0


def project(lon, lat):
    """(lon, lat) -> pixel (x, y) on the poster."""
    return (MAP_X0 + (lon + 180.0) * SCALE,
            MAP_Y0 + (LAT_TOP - lat) * SCALE)


# Coarse hand-drawn coastlines, (lon, lat) rings. Simplified on purpose:
# recognizable silhouettes, not survey data.
CONTINENTS = [
    # North America
    [(-168, 66), (-161, 58), (-152, 60), (-140, 60), (-135, 57), (-130, 54),
     (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20),
     (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9), (-80, 8),
     (-77, 7), (-79, 9), (-83, 15), (-87, 13), (-90, 14), (-91, 19),
     (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 25), (-80, 32),
     (-76, 35), (-74, 40), (-70, 42), (-68, 44), (-66, 45), (-60, 47),
     (-55, 47), (-60, 52), (-64, 58), (-68, 58), (-78, 62), (-85, 66),
     (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71),
     (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
     (-20, 74), (-25, 76), (-35, 77), (-50, 76), (-58, 74), (-60, 70),
     (-58, 64)],
    # South America
    [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-65, -45), (-62, -41), (-58, -35), (-52, -32), (-48, -28),
     (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
     (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
     (-77, 8), (-80, 9)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (9, -1), (12, -5),
     (13, -10), (12, -17), (14, -22), (16, -28), (19, -34), (26, -34),
     (32, -29), (35, -24), (40, -16), (40, -10), (42, -4), (46, -1),
     (51, 2), (51, 11), (48, 11), (44, 11), (40, 15), (38, 18), (37, 22),
     (35, 28), (33, 31), (30, 31), (25, 32), (20, 32), (15, 32), (11, 34),
     (10, 37), (6, 37), (-6, 35)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -21), (44, -16)],
    # Eurasia (Europe + Asia, one landmass)
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49), (0, 51),
     (3, 53), (5, 53), (8, 57), (10, 59), (5, 60), (5, 62), (10, 64),
     (13, 66), (18, 69), (25, 71), (30, 70), (35, 68), (40, 68), (45, 68),
     (55, 68), (65, 69), (70, 72), (75, 73), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (158, 69),
     (162, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 58),
     (158, 52), (156, 51), (150, 59), (142, 54), (140, 50), (135, 44),
     (132, 43), (128, 38), (127, 35), (122, 38), (120, 34), (122, 31),
     (121, 28), (118, 25), (110, 21), (109, 18), (106, 10), (105, 9),
     (103, 7), (100, 8), (98, 10), (97, 16), (94, 17), (92, 21), (89, 22),
     (86, 20), (80, 13), (77, 8), (75, 15), (73, 20), (70, 23), (66, 25),
     (62, 25), (58, 26), (56, 27), (52, 28), (50, 30), (48, 30), (44, 29),
     (40, 31), (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (19, 40),
     (15, 44), (12, 44), (8, 44), (3, 43), (0, 39), (-2, 37), (-6, 36),
     (-9, 37), (-10, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-5, 50)],
    # Iceland
    [(-22, 64), (-15, 64), (-14, 66), (-18, 66), (-24, 66), (-22, 64)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 39),
     (141, 41), (141, 44), (143, 42), (145, 44), (142, 45), (140, 44),
     (139, 38), (137, 37), (133, 36), (131, 34), (130, 31)],
    # Sumatra
    [(95, 5), (98, 3), (100, 0), (102, -2), (104, -4), (106, -6), (104, -5),
     (102, -2), (100, 1), (97, 4), (95, 5)],
    # Java
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8),
     (106, -7), (105, -6)],
    # Borneo
    [(109, 1), (111, 2), (114, 4), (117, 6), (119, 5), (118, 2), (117, -1),
     (114, -3), (110, -3), (109, 0), (109, 1)],
    # New Guinea
    [(131, -1), (134, -3), (137, -4), (141, -6), (145, -7), (147, -9),
     (150, -10), (146, -8), (142, -8), (138, -7), (134, -4), (131, -1)],
    # Australia
    [(114, -22), (113, -26), (115, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
     (141, -13), (137, -12), (135, -12), (132, -11), (130, -13), (126, -14),
     (122, -17), (118, -20), (114, -22)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (178, -38), (176, -40),
     (174, -42), (171, -44), (167, -46), (167, -45)],
]

# (number, lon, lat, label-side offset for crowded pins)
# Offsets (dx, dy) in px move the drawn pin away from its true spot with a
# leader line; used only where three US pins would otherwise collide.
STORIES = [
    (1, 30.7, 36.9, (0, 0)),      # Antalya — COP31 collapses (LEAD)
    (2, 114.1, 22.5, (0, 0)),     # Shenzhen — Trump, Xi & Putin
    (3, 47.0, 25.0, (0, 0)),      # Gulf — Iran war widens
    (4, 23.0, 59.5, (0, 0)),      # Baltic — Russian cargo ship burns
    (5, -77.0, 38.9, (-30, 20)),  # Washington DC — Democrats 258 seats
    (6, 127.0, 37.5, (0, 0)),     # Seoul — minister quits
    (7, 106.8, -6.2, (0, 0)),     # Jakarta — factory fire
    (8, -74.0, 40.7, (0, 0)),     # New York — GTA VI launches
    (9, -87.6, 41.9, (-38, -18)), # Chicago — Thanksgiving travel chaos
    (10, 4.3, 52.1, (0, 0)),      # The Hague — ICJ Rohingya ruling
]

LEAD_LINES = [
    "1  COP31 COLLAPSES — Antalya",
    "Longest climate summit in history ends with NO deal;",
    "the final text never mentions fossil fuels.",
]
LEGEND = {
    2: "Trump, Xi & Putin meet in Shenzhen — deal to expand refined petroleum output",
    3: "Iran war widens — strikes reach Saudi Arabia and Bahrain",
    4: "Russian cargo ship burns in the Baltic off Finland",
    5: "Democrats win 258 House seats — historic majority",
    6: "Seoul education minister quits over AI-cheating scandal",
    7: "Factory fire in Indonesia",
    8: "GTA VI launches — $3.79B, biggest entertainment launch ever",
    9: "Thanksgiving travel chaos grips US airports",
    10: "ICJ rules in the Rohingya genocide case",
}

# Mediterranean sea, carved back out of the land after the continents are
# drawn so Europe and Africa read as separate landmasses.
MED_SEA = [(-6, 35), (0, 37), (6, 38), (12, 39), (18, 39.5), (23, 37),
           (28, 36.5), (33, 36.5), (36, 36), (36, 32.5), (32, 31.5),
           (27, 31.5), (22, 31.5), (17, 32), (12, 33), (7, 34.5), (2, 35),
           (-6, 35)]


def font(size, bold=False):
    return ImageFont.truetype(SANS_BOLD if bold else SANS, size)


def centered(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def starfield(draw):
    rng = random.Random(20261123)
    for _ in range(260):
        x = rng.randint(8, W - 8)
        y = rng.randint(8, H - 8)
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(28, 90)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(200, 210, 225, a))


def graticule(draw):
    for lon in range(-150, 181, 30):
        x = MAP_X0 + (lon + 180) * SCALE
        draw.line([(x, MAP_Y0), (x, MAP_Y0 + 130 * SCALE)],
                  fill=(255, 255, 255, 16), width=1)
    for lat in range(-30, 73, 30):
        y = MAP_Y0 + (LAT_TOP - lat) * SCALE
        draw.line([(MAP_X0, y), (MAP_X0 + 360 * SCALE, y)],
                  fill=(255, 255, 255, 16), width=1)


def draw_map(draw):
    for ring in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in ring]
        draw.polygon(pts, fill=TEAL, outline=TEAL_EDGE, width=2)
    sea = [project(lon, lat) for lon, lat in MED_SEA]
    draw.polygon(sea, fill=NAVY)


def wrap_text(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_pins(draw):
    f_num = font(20, bold=True)
    f_lead = font(24, bold=True)
    for num, lon, lat, (dx, dy) in STORIES:
        x, y = project(lon, lat)
        px, py = x + dx, y + dy
        if (dx, dy) != (0, 0):
            draw.line([(x, y), (px, py)], fill=GOLD, width=2)
            draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=GOLD)
        lead = num == 1
        r = 20 if lead else 13
        fill = RED if lead else GOLD
        fnt = f_lead if lead else f_num
        draw.ellipse([px - r, py - r, px + r, py + r], fill=fill,
                     outline=WHITE, width=2)
        label = str(num)
        tw = draw.textlength(label, font=fnt)
        th = fnt.size
        draw.text((px - tw / 2, py - th / 2 - 1), label, font=fnt, fill=WHITE)


def draw_legend(draw):
    # Lead story band
    y = 512
    draw.rounded_rectangle([44, y, 980, y + 96], radius=10,
                           fill=NAVY_SOFT, outline=GOLD_DIM, width=2)
    centered(draw, 512, y + 10, LEAD_LINES[0], font(26, bold=True), GOLD)
    centered(draw, 512, y + 42, LEAD_LINES[1], font(21, bold=True), WHITE)
    centered(draw, 512, y + 68, LEAD_LINES[2], font(21, bold=True), WHITE)

    # Two-column grid for stories 2-10, wrapped to the column width.
    entries = [(num, LEGEND[num]) for num in range(2, 11)]
    col_x = [44, 532]
    row_h = 56
    f_body = font(18)
    f_num = font(18, bold=True)
    for i, (num, text) in enumerate(entries):
        col = i % 2
        row = i // 2
        x0 = col_x[col]
        y0 = 626 + row * row_h
        # Number chip
        draw.ellipse([x0, y0 + 2, x0 + 30, y0 + 32], fill=GOLD)
        label = str(num)
        tw = draw.textlength(label, font=f_num)
        draw.text((x0 + 15 - tw / 2, y0 + 6), label, font=f_num, fill=(11, 22, 38))
        tx = x0 + 40
        max_w = 980 - tx if col == 1 else 512 - tx
        for j, line in enumerate(wrap_text(draw, text, f_body, max_w)):
            draw.text((tx, y0 + j * 23), line, font=f_body, fill=MIST)


def paint():
    img = Image.new("RGB", (W, H), NAVY)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    starfield(od)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Frame
    draw.rectangle([10, 10, W - 11, H - 11], outline=GOLD_DIM, width=2)

    # Header
    centered(draw, 512, 28, "ONE DAY ON EARTH", font(62, bold=True), WHITE)
    centered(draw, 512, 102, "MONDAY \u00b7 23 NOVEMBER 2026 \u2014 THE WORLD IN ONE IMAGE",
             font(21, bold=True), GOLD)
    draw.line([(180, 138), (844, 138)], fill=GOLD_DIM, width=2)

    graticule(draw)
    draw_map(draw)
    draw_pins(draw)

    draw.line([(44, 496), (980, 496)], fill=(255, 255, 255, 40), width=1)
    draw_legend(draw)

    # Strap line + footer
    centered(draw, 512, 918, "10 STORIES  \u00b7  5 CONTINENTS  \u00b7  1 DAY",
             font(20, bold=True), GOLD)
    centered(draw, 512, 958, "Headlines as reported on 23 November 2026",
             font(18), FAINT)
    return img


if __name__ == "__main__":
    paint().save("entry.png", optimize=True)
    print("wrote entry.png")
