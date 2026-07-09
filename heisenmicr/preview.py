#!/usr/bin/env python3
"""Proof sheets for HeisenMICR: labeled glyph grid with guides, text sheet, close-ups."""
import sys
from PIL import Image, ImageDraw, ImageFont

TTF = "/home/claude/heisenmicr/HeisenMICR.ttf"
LABEL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

BG, FG, GUIDE, LBL = "#101010", "#E8E2D5", "#3A5A3A", "#707070"
UPM, CAP = 1000, 693


def grid():
    size = 150
    fnt = ImageFont.truetype(TTF, size)
    lbl = ImageFont.truetype(LABEL, 16)
    cols, cw, ch = 9, 130, 190
    rows = (len(CHARS) + cols - 1) // cols
    img = Image.new("RGB", (cols * cw + 20, rows * ch + 20), BG)
    d = ImageDraw.Draw(img)
    asc, _ = fnt.getmetrics()
    for i, c in enumerate(CHARS):
        col, row = i % cols, i // cols
        x0, y0 = 10 + col * cw, 10 + row * ch
        base_y = y0 + 15 + asc
        cap_y = base_y - CAP * size / UPM
        d.line([(x0 + 5, base_y), (x0 + cw - 10, base_y)], fill=GUIDE)
        d.line([(x0 + 5, cap_y), (x0 + cw - 10, cap_y)], fill=GUIDE)
        d.text((x0 + 30, y0 + 15), c, font=fnt, fill=FG)
        d.text((x0 + 5, y0 + ch - 24), c, font=lbl, fill=LBL)
    img.save("/home/claude/heisenmicr/proof_grid.png")
    print("proof_grid.png")


def text_sheet():
    img = Image.new("RGB", (1750, 800), BG)
    d = ImageDraw.Draw(img)
    y = 30
    for size, color, s in [
        (96, "#CC4E00", "HEISENMICR 0123456789"),
        (56, FG, "THE QUICK BROWN FOX JUMPS"),
        (56, FG, "OVER THE LAZY DOG"),
        (40, "#8A9A4B", "PACK MY BOX WITH FIVE DOZEN LIQUOR JUGS"),
        (40, "#8A9A4B", "SPHINX OF BLACK QUARTZ JUDGE MY VOW"),
        (28, "#CC4E00", "HEISENCODER CONSULTING LLC 2026"),
        (20, LBL, "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG 0123456789"),
        (14, LBL, "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG 0123456789"),
    ]:
        fnt = ImageFont.truetype(TTF, size)
        d.text((40, y), s, font=fnt, fill=color)
        y += int(size * 1.6)
    img.save("/home/claude/heisenmicr/proof_text.png")
    print("proof_text.png")


def close(chars):
    size = 340
    fnt = ImageFont.truetype(TTF, size)
    lbl = ImageFont.truetype(LABEL, 20)
    cw, ch = 240, 440
    cols = min(len(chars), 6)
    rows = (len(chars) + cols - 1) // cols
    img = Image.new("RGB", (cols * cw + 20, rows * ch + 20), BG)
    d = ImageDraw.Draw(img)
    asc, _ = fnt.getmetrics()
    for i, c in enumerate(chars):
        col, row = i % cols, i // cols
        x0, y0 = 10 + col * cw, 10 + row * ch
        base_y = y0 + 30 + asc
        cap_y = base_y - CAP * size / UPM
        d.line([(x0, base_y), (x0 + cw - 10, base_y)], fill=GUIDE)
        d.line([(x0, cap_y), (x0 + cw - 10, cap_y)], fill=GUIDE)
        d.text((x0 + 30, y0 + 30), c, font=fnt, fill=FG)
        d.text((x0 + 8, y0 + ch - 28), c, font=lbl, fill=LBL)
    img.save("/home/claude/heisenmicr/proof_close.png")
    print("proof_close.png")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        close(sys.argv[1])
    else:
        grid()
        text_sheet()
