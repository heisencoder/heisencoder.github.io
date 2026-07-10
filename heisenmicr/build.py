#!/usr/bin/env python3
"""Compile HeisenMICR.ttf from the markdown spec.

Pipeline per glyph:
  1. Each solid cell -> rectangle, W=55 wide x cell-height tall (uppercase
     h=99, 1.8:1; lowercase h=55, 1:1 small caps in the bottom square)
  2. Each diagonal join pair -> parallelogram band across the shared corner
     (pure staircases, diagonals into stems, and outer corner bevels)
  3. skia-pathops simplify (union, fixed winding) -> clean non-overlapping outline
  4. Round every corner with a circular-arc fillet of radius W/4 (a quarter cell
     width), rendered as two quadratic Beziers per corner
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
XOFF = 55                # left side bearing = 1 cell (2-cell total gap)
ADV = 9 * W              # 495: 7-cell body + 2-cell gap
CAP = 7 * H              # 693 cap height
XHEIGHT = 5 * H          # 495 small-cap height = 5/7 of the cap height
LOWER_H = XHEIGHT / 7    # lowercase cell height (width stays W)
R_FILLET = W / 4         # corner radius = 1/4 of a cell width

OUT = str(Path(__file__).with_name("HeisenMICR.ttf"))
VERSION = "1.400"


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


def _line_intersect(p1, d1, p2, d2):
    """Intersection of line (p1, dir d1) with line (p2, dir d2)."""
    denom = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(denom) < 1e-9:                         # parallel: midpoint fallback
        return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
    s = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / denom
    return (p1[0] + s * d1[0], p1[1] + s * d1[1])


def fillet_contour(pts, radius):
    """Round each corner with a true circular arc of the given radius.

    The arc is rendered as two quadratic Beziers (an accurate approximation of a
    circular arc up to ~180 degrees, unlike a single control-at-the-vertex
    quadratic, which is noticeably tighter than the nominal radius). Returns a
    list of (point, on_curve) tuples for a TrueType quadratic pen. The tangent
    length is radius / tan(interior_angle / 2), clamped to half of either edge.
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
        u0 = (e0[0] / l0, e0[1] / l0)              # unit incoming edge
        u1 = (e1[0] / l1, e1[1] / l1)              # unit outgoing edge
        cosang = max(-1.0, min(1.0, -(u0[0] * u1[0] + u0[1] * u1[1])))
        theta = math.acos(cosang)                  # interior angle at the corner
        if theta > math.pi - 0.05:                 # nearly straight: keep vertex
            out.append((v, True))
            continue
        half = theta / 2.0
        t = min(radius / math.tan(half), 0.5 * l0, 0.5 * l1)  # tangent length
        r = t * math.tan(half)                     # radius after any clamp
        a = (v[0] - u0[0] * t, v[1] - u0[1] * t)   # arc entry, on incoming edge
        b = (v[0] + u1[0] * t, v[1] + u1[1] * t)   # arc exit, on outgoing edge
        # arc centre: radius r inward of the incoming edge at a
        cross = u0[0] * u1[1] - u0[1] * u1[0]
        nrm = (-u0[1], u0[0]) if cross >= 0 else (u0[1], -u0[0])
        o = (a[0] + r * nrm[0], a[1] + r * nrm[1])
        bis = (a[0] + b[0] - 2 * o[0], a[1] + b[1] - 2 * o[1])  # toward arc mid
        blen = math.hypot(*bis)
        if blen < 1e-6:                            # ~180 deg: single quadratic
            out += [(a, True), (v, False), (b, True)]
            continue
        m = (o[0] + r * bis[0] / blen, o[1] + r * bis[1] / blen)  # arc midpoint
        tm = (-(m[1] - o[1]), m[0] - o[0])         # tangent at m (perp to radius)
        c1 = _line_intersect(a, u0, m, tm)
        c2 = _line_intersect(m, tm, b, u1)
        out += [(a, True), (c1, False), (m, True), (c2, False), (b, True)]
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
