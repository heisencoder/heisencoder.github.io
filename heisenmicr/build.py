#!/usr/bin/env python3
"""Compile HeisenMICR.ttf from the markdown spec.

Pipeline per glyph:
  1. Each solid cell -> rectangle (w=55 x h=99 units, 1.8:1 exact)
  2. Each pure-diagonal pair -> rhombus at shared corner
     (half-diagonals k=31 -> perpendicular waist ~= 1 block width)
  3. skia-pathops simplify (union, fixed winding) -> clean non-overlapping outline
  4. Fillet every corner: radius 7 (= w/8), quadratic approximation
  5. TTGlyphPen -> glyf
"""
import math

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.misc.timeTools import timestampNow
import pathops

from spec import parse_spec, pure_diagonal_pairs

# ── Geometry constants ──────────────────────────────────────────
W, H = 55, 99            # block size, 1.8:1 exact
XOFF = 55                # left side bearing = 1 block (2-block total gap)
ADV = 9 * W              # 495: 7-block body + 2-block gap
CAP = 7 * H              # 693
R_FILLET = 14            # 1/4 of block width

OUT = "/home/claude/heisenmicr/HeisenMICR.ttf"
VERSION = "1.100"


def cell_rect(r, c):
    x0 = XOFF + c * W
    y0 = (6 - r) * H
    return [(x0, y0), (x0 + W, y0), (x0 + W, y0 + H), (x0, y0 + H)]


def join_band(a, b):
    """Parallelogram whose slanted edges (slope ±1.8) pass through the
    corners of the two diagonally adjacent blocks. Consecutive chain
    segments share the same support lines, so long diagonals render as
    single straight strokes with no stepping."""
    (r, c), (r2, c2) = a, b            # r2 = r+1, c2 = c±1
    x0 = XOFF + c * W
    y0 = (6 - r) * H                   # bottom of upper cell a
    if c2 == c + 1:                    # "\" pair: A upper-left, B lower-right
        return [(x0, y0), (x0 + W, y0 - H),
                (x0 + 2 * W, y0), (x0 + W, y0 + H)]        # CCW
    else:                              # "/" pair: A upper-right, B lower-left
        return [(x0, y0 + H), (x0 - W, y0),
                (x0, y0 - H), (x0 + W, y0)]                # CCW


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


def draw_glyph(pen, cells):
    polys = [cell_rect(r, c) for (r, c) in sorted(cells)]
    polys += [join_band(a, b) for a, b in pure_diagonal_pairs(cells)]
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
    grids = parse_spec()
    order = [".notdef", "space"] + list(grids.keys())

    cmap = {0x20: "space"}
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        cmap[0x41 + i] = ch
    for i, name in enumerate(
        ["zero", "one", "two", "three", "four",
         "five", "six", "seven", "eight", "nine"]):
        cmap[0x30 + i] = name

    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)

    notdef_cells = ({(r, 0) for r in range(7)} | {(r, 6) for r in range(7)}
                    | {(0, c) for c in range(7)} | {(6, c) for c in range(7)})
    all_grids = {".notdef": notdef_cells, "space": set(), **grids}

    glyf = {}
    for name in order:
        pen = TTGlyphPen(None)
        draw_glyph(pen, all_grids[name])
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
                       "Blocks 1.8:1 h:w, diagonal joins, 1/8-block corner radius.",
    })
    fb.setupOS2(
        sTypoAscender=744, sTypoDescender=-48, sTypoLineGap=0,
        usWinAscent=744, usWinDescent=48,
        sxHeight=495, sCapHeight=CAP,
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
          f"block={W}x{H} cap={CAP} adv={ADV} fillet={R_FILLET} band=corner-joined slope 1.8")


if __name__ == "__main__":
    build()
