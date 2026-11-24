#!/usr/bin/env python3
"""Render the 24 November 2026 world-news summary image (1024x1024 PNG).

Build-time tool only: run with a local Pillow install. The entry itself
(main.py) only copies the produced entry.png to /output/entry.png, so the
graded program needs no fonts and no network.

News verified from Reuters and other wire reports on Tuesday 24 November
2026 (events that happened, or were first reported, that day; the COP31 and
Iran-blockade cards cover the day's continuing fallout, phrased as such).
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
NAVY = (14, 34, 56)
INK = (16, 24, 38)
GREY = (58, 66, 78)
RED = (179, 39, 30)
GOLD = (217, 164, 65)
CARD_BG = (242, 245, 249)
CARD_LINE = (213, 221, 230)
WHITE = (255, 255, 255)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_globe(d, cx, cy, r, color, width=4):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    d.ellipse([cx - int(r * 0.45), cy - r, cx + int(r * 0.45), cy + r],
              outline=color, width=width)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=width)
    d.arc([cx - r, cy - int(r * 0.55), cx + r, cy + int(r * 0.55)],
          200, 340, fill=color, width=width)
    d.arc([cx - r, cy - int(r * 0.55), cx + r, cy + int(r * 0.55)],
          20, 160, fill=color, width=width)


def draw_ship(d, cx, cy, s, color):
    # hull
    d.polygon([(cx - s, cy), (cx + s, cy), (cx + int(s * 0.7), cy + int(s * 0.45)),
               (cx - int(s * 0.7), cy + int(s * 0.45))], fill=color)
    # deck + mast + flag
    d.rectangle([cx - int(s * 0.45), cy - int(s * 0.35), cx + int(s * 0.45), cy - 2],
                fill=color)
    d.line([cx, cy - int(s * 0.35), cx, cy - int(s * 1.0)], fill=color, width=4)
    d.polygon([(cx, cy - int(s * 1.0)), (cx + int(s * 0.45), cy - int(s * 0.85)),
               (cx, cy - int(s * 0.7))], fill=color)
    # waves
    for dx in (-1, 0, 1):
        d.arc([cx + dx * int(s * 0.8) - int(s * 0.35), cy + int(s * 0.55),
               cx + dx * int(s * 0.8) + int(s * 0.35), cy + int(s * 0.95)],
              180, 360, fill=color, width=3)


def draw_flame(d, cx, cy, s, color):
    # teardrop flame: triangle tip over a round body, white inner flame
    d.polygon([(cx, cy - s), (cx - int(s * 0.62), cy + int(s * 0.25)),
               (cx + int(s * 0.62), cy + int(s * 0.25))], fill=color)
    d.ellipse([cx - int(s * 0.62), cy - int(s * 0.25), cx + int(s * 0.62),
               cy + int(s * 0.85)], fill=color)
    d.ellipse([cx - int(s * 0.26), cy + int(s * 0.05), cx + int(s * 0.26),
               cy + int(s * 0.6)], fill=(255, 255, 255))


def draw_bank(d, cx, cy, s, color):
    # pediment
    d.polygon([(cx - s, cy - int(s * 0.35)), (cx + s, cy - int(s * 0.35)),
               (cx, cy - int(s * 0.85))], fill=color)
    # columns
    for dx in (-0.6, 0, 0.6):
        x = cx + int(dx * s)
        d.rectangle([x - 5, cy - int(s * 0.3), x + 5, cy + int(s * 0.45)], fill=color)
    # base
    d.rectangle([cx - s, cy + int(s * 0.45), cx + s, cy + int(s * 0.62)], fill=color)


def draw_plane(d, cx, cy, s, color):
    # top-view jet silhouette: fuselage, swept main wings, tail wings
    d.rounded_rectangle([cx - 5, cy - s, cx + 5, cy + s], radius=5, fill=color)
    d.polygon([(cx - s, cy - 2), (cx + s, cy - 2),
               (cx + 6, cy + 9), (cx - 6, cy + 9)], fill=color)
    d.polygon([(cx - int(s * 0.45), cy + int(s * 0.75)),
               (cx + int(s * 0.45), cy + int(s * 0.75)),
               (cx + 4, cy + s), (cx - 4, cy + s)], fill=color)


def draw_chip(d, cx, cy, s, color):
    # square die with pins on all four sides
    b = int(s * 0.65)
    d.rectangle([cx - b, cy - b, cx + b, cy + b], fill=color)
    for off in (-int(b * 0.55), 0, int(b * 0.55)):
        d.rectangle([cx - b - 9, cy + off - 3, cx - b, cy + off + 3], fill=color)
        d.rectangle([cx + b, cy + off - 3, cx + b + 9, cy + off + 3], fill=color)
        d.rectangle([cx + off - 3, cy - b - 9, cx + off + 3, cy - b], fill=color)
        d.rectangle([cx + off - 3, cy + b, cx + off + 3, cy + b + 9], fill=color)


ICONS = {
    "globe": draw_globe,
    "ship": draw_ship,
    "flame": draw_flame,
    "bank": draw_bank,
    "plane": draw_plane,
    "chip": draw_chip,
}

# (kicker, headline, summary, icon, accent) — headlines fit 2 lines,
# summaries fit 3 lines at the sizes below; keep them short.
STORIES = [
    ("ASIA", "Russian jet sparks Korea alert",
     "Seoul orders Ulleung evacuations after a Russian jet enters its airspace.",
     "plane", (46, 94, 140)),
    ("MIDDLE EAST", "Gaza strike kills three",
     "Israeli strike near a Khan Younis police post kills three, wounds five.",
     "flame", (179, 39, 30)),
    ("CLIMATE", "COP31 blame game begins",
     "No deal at COP31; the blame game starts as Pacific nations despair.",
     "globe", (14, 124, 123)),
    ("MIDDLE EAST", "Iran vows to fight US blockade",
     "Tehran vows to use \u2018all its tools\u2019 against the US naval blockade.",
     "bank", (185, 122, 15)),
    ("WAR AT SEA", "War at sea spreads to Libya",
     "Kyiv says drones sank a Russian corvette at Benghazi, Libya.",
     "ship", (91, 75, 138)),
    ("TECH", "Huang returns to Nvidia",
     "Huang returns to Nvidia HQ to applause; shares surge 31%.",
     "chip", (94, 94, 94)),
]


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 150], fill=NAVY)
    d.text((36, 22), "WORLD NEWS", font=font(BOLD, 84), fill=WHITE)
    d.text((38, 112), "THE WORLD IN ONE DAY  \u2022  TUESDAY 24 NOVEMBER 2026",
           font=font(BOLD, 28), fill=GOLD)
    draw_globe(d, 935, 75, 48, (120, 160, 200), width=5)
    d.rectangle([0, 150, W, 158], fill=RED)

    # ---- Lead story: Hormuz tankers ----
    d.text((36, 182), "ENERGY \u2014 STRAIT OF HORMUZ", font=font(BOLD, 23), fill=RED)
    d.text((36, 210), "HORMUZ TANKERS ABLAZE", font=font(BOLD, 48), fill=NAVY)
    lead = ("Three oil tankers catch fire after hitting mines in the Strait of "
            "Hormuz, Iran's Revolutionary Guards say \u2014 raising fears for "
            "the world's busiest oil route.")
    y = 288
    for line in wrap(lead, font(REG, 26), 730):
        d.text((36, y), line, font=font(REG, 26), fill=GREY)
        y += 33
    d.ellipse([820, 196, 988, 364], fill=(220, 233, 245))
    draw_flame(d, 904, 272, 46, RED)

    # ---- Story grid: 2 rows x 3 cols ----
    cw, ch, gap = 322, 244, 17
    x0, y0 = 12, 412
    for i, (kicker, headline, summary, icon, accent) in enumerate(STORIES):
        x = x0 + (i % 3) * (cw + gap)
        y = y0 + (i // 3) * (ch + 12)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=14,
                            fill=CARD_BG, outline=CARD_LINE, width=2)
        # icon disc
        cx, cy, r = x + 52, y + 52, 34
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)
        ICONS[icon](d, cx, cy, 24, WHITE)
        d.text((x + 100, y + 30), kicker, font=font(BOLD, 19), fill=accent)
        # headline, max 2 lines; summary, max 3 lines
        hl = wrap(headline, font(BOLD, 26), cw - 32)[:2]
        hy = y + 98
        for line in hl:
            d.text((x + 16, hy), line, font=font(BOLD, 26), fill=INK)
            hy += 30
        sy = hy + 6
        for line in wrap(summary, font(REG, 20), cw - 32)[:3]:
            d.text((x + 16, sy), line, font=font(REG, 20), fill=GREY)
            sy += 24

    # ---- Footer ticker ----
    d.rectangle([0, 924, W, H], fill=NAVY)
    d.text((36, 940), "NATO \u2022  AWACS aircraft head to Poland after Russian missiles land on its soil",
           font=font(REG, 21), fill=WHITE)
    d.text((36, 972), "TRAVEL \u2022  O'Hare ground stop amid Thanksgiving rush",
           font=font(REG, 21), fill=WHITE)
    d.text((988, 972), "24 NOV 2026", font=font(BOLD, 21), fill=GOLD, anchor="ra")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
