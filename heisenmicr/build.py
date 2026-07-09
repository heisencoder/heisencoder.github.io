#!/usr/bin/env python3
"""Compile HeisenMICR.ttf from the markdown spec.

Pipeline per glyph:
  1. Each solid cell -> rectangle, W=55 wide x cell-height tall (uppercase
     h=99, 1.8:1; lowercase h=55, 1:1 small caps in the bottom square)
  2. Each diagonal join pair -> parallelogram band across the shared corner
     (pure staircases, diagonals into stems, and outer corner bevels)
  3. skia-pathops simplify (union, fixed winding) -> clean non-overlapping outline
  4. Fillet every corner with a quadratic Bezier, radius 14 (~1/4 cell width)
  5. TTGlyphPen -> glyf

Lowercase is derived from the uppercase grids; only A-Z, the digits and the
punctuation are defined in HeisenMICR.md.
"""
import math
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.misc.timeTools import timestampNow
import pathops

from spec import (parse_spec, pure_diagonal_pairs, stem_junction_pairs,
                  corner_bevel_pairs, CODEPOINTS)

# ── Geometry constants ──────────────────────────────────────────
W, H = 55, 99            # uppercase cell, 1.8:1 exact
LOWER_H = 55             # lowercase cell, 1:1 (small caps in the bottom square)
XOFF = 55                # left side bearing = 1 cell (2-cell total gap)
ADV = 9 * W              # 495: 7-cell body + 2-cell gap
CAP = 7 * H              # 693 cap height
XHEIGHT = 7 * LOWER_H    # 385 small-cap height
R_FILLET = 14            # ~1/4 of cell width

OUT = str(Path(__file__).with_name("HeisenMICR.ttf"))
VERSION = "1.300"


def cell_rect(r, c, h=H):
    x0 = XOFF + c * W
    y0 = (6 - r) * h
    return [(x0, y0), (x0 + W, y0), (x0 + W, y0 + h), (x0, y0 + h)]


def join_band(a, b, h=H):
    """Parallelogram whose slanted edges (slope ±h/W) pass through the
    corners of the two diagonally adjacent cells. Consecutive chain
    segments share the same support lines, so long diagonals render as
    single straight strokes with no stepping. (Slope is ±1.8 for the
    uppercase cell, ±1 for the square lowercase cell.)"""
    (r, c), (r2, c2) = a, b            # r2 = r+1, c2 = c±1
    x0 = XOFF + c * W
    y0 = (6 - r) * h                   # bottom of upper cell a
    if c2 == c + 1:                    # "\" pair: A upper-left, B lower-right
        return [(x0, y0), (x0 + W, y0 - h),
                (x0 + 2 * W, y0), (x0 + W, y0 + h)]        # CCW
    else:                              # "/" pair: A upper-right, B lower-left
        return [(x0, y0 + h), (x0 - W, y0),
                (x0, y0 - h), (x0 + W, y0)]                # CCW


def union_contours(polys):
    """Union polygons via skia-pathops; return list of point-list contours."""
    path = pathops.Path()
    pen = path.getPen()
    for poly in polys:
        pen.moveTo(poly[0])
        for pt in poly[1:]:
            pen.lineTo(pt)
        pen.closePath()
    path.simplify(fix_winding=True)

    rec = RecordingPen()
    path.draw(rec)
    contours, cur = [], []
    for op, args in rec.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op == "lineTo":
            cur.append(args[0])
        elif op == "closePath":
            if len(cur) >= 3:
                # drop duplicated closing point if present
                if cur[0] == cur[-1]:
                    cur.pop()
                contours.append(cur)
            cur = []
        else:
            raise ValueError(f"unexpected segment {op}")
    return contours


def fillet_contour(pts, radius):
    """Round each corner with a quadratic Bezier (control at the vertex).

    Returns list of (point, on_curve) tuples for TTGlyphPen.
    Tangent offset t = radius / tan(theta/2), clamped to 40% of either edge.
    """
    n = len(pts)
    out = []
    for i in range(n):
        p0 = pts[(i - 1) % n]
        v = pts[i]
        p1 = pts[(i + 1) % n]
        e0 = (v[0] - p0[0], v[1] - p0[1])
        e1 = (p1[0] - v[0], p1[1] - v[1])
        l0 = math.hypot(*e0)
        l1 = math.hypot(*e1)
        if l0 < 1e-6 or l1 < 1e-6:
            out.append((v, True))
            continue
        u0 = (e0[0] / l0, e0[1] / l0)
        u1 = (e1[0] / l1, e1[1] / l1)
        # interior turn angle
        cosang = max(-1.0, min(1.0, -(u0[0] * u1[0] + u0[1] * u1[1])))
        theta = math.acos(cosang)
        if theta > math.pi - 0.05:     # nearly straight: keep as-is
            out.append((v, True))
            continue
        t = radius / math.tan(theta / 2)
        t = min(t, 0.4 * l0, 0.4 * l1)
        a = (v[0] - u0[0] * t, v[1] - u0[1] * t)   # entry tangent point
        b = (v[0] + u1[0] * t, v[1] + u1[1] * t)   # exit tangent point
        out.append((a, True))
        out.append((v, False))                      # off-curve control
        out.append((b, True))
    return [((round(x), round(y)), on) for ((x, y), on) in out]


def draw_glyph(pen, cells, h=H):
    polys = [cell_rect(r, c, h) for (r, c) in sorted(cells)]
    # diagonal join bands: isolated staircases (pure), diagonals running into a
    # stem (stem junction), and stair-stepped outer corners (corner bevel). The
    # rules can name the same pair, so dedupe before drawing.
    bands = (set(pure_diagonal_pairs(cells)) | set(stem_junction_pairs(cells))
             | set(corner_bevel_pairs(cells)))
    polys += [join_band(a, b, h) for a, b in sorted(bands)]
    if not polys:
        return
    for contour in union_contours(polys):
        seq = fillet_contour(contour, R_FILLET)
        # rotate so sequence starts on-curve
        start = next(i for i, (_, on) in enumerate(seq) if on)
        seq = seq[start:] + seq[:start]
        pen.moveTo(seq[0][0])
        i = 1
        while i < len(seq):
            pt, on = seq[i]
            if on:
                pen.lineTo(pt)
                i += 1
            else:
                pen.qCurveTo(pt, seq[(i + 1) % len(seq)][0])
                i += 2
        pen.closePath()


def build():
    grids = parse_spec()   # uppercase A-Z, digits, punctuation (from the spec)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    notdef_cells = ({(r, 0) for r in range(7)} | {(r, 6) for r in range(7)}
                    | {(0, c) for c in range(7)} | {(6, c) for c in range(7)})

    # render spec per glyph: (cells, cell_height). Lowercase reuses the
    # uppercase grid but with a 1:1 cell, so it sits as small caps in the
    # bottom square of the uppercase area.
    render = {".notdef": (notdef_cells, H), "space": (set(), H)}
    for name, cells in grids.items():
        render[name] = (cells, H)
    for ch in letters:
        render[ch.lower()] = (grids[ch], LOWER_H)

    order = [".notdef", "space"] + list(grids.keys()) + [c.lower() for c in letters]

    cmap = {0x20: "space"}
    for name in grids:
        cmap[CODEPOINTS[name]] = name
    for ch in letters:
        cmap[ord(ch.lower())] = ch.lower()

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)

    glyf = {}
    for name in order:
        pen = TTGlyphPen(None)
        cells, h = render[name]
        draw_glyph(pen, cells, h)
        glyf[name] = pen.glyph()
    fb.setupGlyf(glyf)

    metrics = {}
    for name in order:
        g = glyf[name]
        xmin = g.xMin if g.numberOfContours > 0 else 0
        metrics[name] = (ADV, xmin)
    fb.setupHorizontalMetrics(metrics)

    # line height = 8 blocks = 792, split 744 / -48
    fb.setupHorizontalHeader(ascent=744, descent=-48, lineGap=0)
    fb.setupNameTable({
        "familyName": "HeisenMICR",
        "styleName": "Regular",
        "uniqueFontIdentifier": f"HeisenMICR-Regular-{VERSION}",
        "fullName": "HeisenMICR Regular",
        "version": f"Version {VERSION}",
        "psName": "HeisenMICR-Regular",
        "manufacturer": "Heisencoder Consulting LLC",
        "description": "MICR-style display font built from a 7x7 grid spec. "
                       "Uppercase cell 1.8:1 h:w, lowercase small caps on a 1:1 "
                       "cell, diagonal joins, rounded corners.",
    })
    fb.setupOS2(
        sTypoAscender=744, sTypoDescender=-48, sTypoLineGap=0,
        usWinAscent=744, usWinDescent=48,
        sxHeight=XHEIGHT, sCapHeight=CAP,
        fsType=0, achVendID="HSNC", fsSelection=0x0040,
        ulUnicodeRange1=0x00000001, ulCodePageRange1=0x00000001,
        panose=dict(bFamilyType=2, bSerifStyle=0, bWeight=6, bProportion=9,
                    bContrast=0, bStrokeVariation=0, bArmStyle=0,
                    bLetterForm=0, bMidline=0, bXHeight=0),
    )
    fb.setupPost(isFixedPitch=1)

    font = fb.font
    now = timestampNow()
    font["head"].created = now
    font["head"].modified = now
    font.save(OUT)
    print(f"OK  {OUT}")
    print(f"    glyphs={len(order)} mapped={len(cmap)} "
          f"upper={W}x{H} lower={W}x{LOWER_H} cap={CAP} xheight={XHEIGHT} "
          f"adv={ADV} fillet={R_FILLET}")


if __name__ == "__main__":
    build()
