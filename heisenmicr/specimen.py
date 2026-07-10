#!/usr/bin/env python3
"""Render specimen_heisenmicr.png — the one-page HeisenMICR specimen sheet.

Regenerate after rebuilding the font: `uv run build.py && uv run specimen.py`.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
TTF = str(HERE / "HeisenMICR.ttf")
OUT = str(HERE / "specimen_heisenmicr.png")

W, H = 1850, 1180
BG = "#15110C"
ORANGE = "#CC4E00"
CREAM = "#E8E2D5"
GREEN = "#8A9A4B"
GRAY = "#6E6A62"
DIM = "#4A4640"

SUBTITLE = "V140  ROUNDED CORNERS  5:7 SMALL CAPS"
PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"


def label_font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def font(size):
    return ImageFont.truetype(TTF, size)


def render():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # accent bar down the left edge
    d.rectangle([0, 0, 10, H], fill=ORANGE)

    left = 70
    d.text((left, 55), "HEISENMICR", font=font(118), fill=ORANGE)
    d.text((left + 4, 205), SUBTITLE, font=label_font(24), fill=GREEN)

    d.line([(left, 262), (760, 262)], fill=ORANGE, width=3)

    y = 285
    for line in ("ABCDEFGHIJKLM", "NOPQRSTUVWXYZ"):
        d.text((left, y), line, font=font(94), fill=CREAM)
        y += 114
    # lowercase small caps + digits
    d.text((left, y), "abcdefghijklmnopqrstuvwxyz", font=font(64), fill=GREEN)
    y += 84
    d.text((left, y), "0123456789", font=font(64), fill=CREAM)
    y += 84
    d.text((left, y), PUNCT, font=font(46), fill=GRAY)
    y += 74

    d.line([(left, y), (470, y)], fill=GREEN, width=2)
    y += 26
    # mixed case shows the small-cap lowercase against the capitals
    d.text((left, y), "The quick brown fox jumps over the lazy dog",
           font=font(40), fill=CREAM)
    y += 66
    d.text((left, y), "Sphinx of black quartz, judge my vow!",
           font=font(40), fill=GRAY)
    y += 86

    d.line([(left, y), (470, y)], fill=GREEN, width=2)
    y += 26
    d.text((left, y), "Heisencoder Consulting LLC", font=font(46), fill=ORANGE)
    y += 78
    d.text((left, y), "AI-Assisted Software Engineering 2026",
           font=font(28), fill=GREEN)

    # size ramp on the right
    rx = 1240
    d.text((rx, 205), "SIZE RAMP", font=label_font(22), fill=GRAY)
    ry = 250
    for size in (120, 88, 64, 44, 30, 20):
        d.text((rx, ry), "XRO", font=font(size), fill=CREAM)
        num = label_font(20)
        d.text((W - 110, ry + size * 0.55), str(size), font=num, fill=DIM)
        ry += int(size * 1.35) + 26

    img.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    render()
