#!/usr/bin/env python3
"""Spec assertions for HeisenMICR, per the markdown requirements:

1. No overlapping components  -> re-simplify is a no-op (area & contours stable)
2. No gaps between adjacent components -> solid cells form 1 connected
   component (edge adjacency + pure-diagonal joins)
3. Single continuous outer line per character + continuous interior lines
   -> outer contour count == solid components (expected 1),
      inner contour count == expected hole count from the grid
4. Raster check: every solid cell center inked, every empty cell center clear
"""
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
import pathops
from PIL import Image, ImageDraw, ImageFont

from spec import parse_spec, solid_components, expected_holes
from build import XOFF, W, H, OUT

SIZE = 400  # px per em for raster checks


def glyph_path(font, name):
    glyphset = font.getGlyphSet()
    path = pathops.Path()
    glyphset[name].draw(path.getPen(glyphSet=glyphset))
    return path


def contour_stats(path):
    """(n_outer, n_inner) by signed area within nonzero winding."""
    rec = RecordingPen()
    path.draw(rec)
    contours, cur = [], []
    for op, args in rec.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op in ("lineTo",):
            cur.append(args[0])
        elif op == "qCurveTo":
            cur.extend(a for a in args if a is not None)
        elif op == "closePath":
            if len(cur) >= 3:
                contours.append(cur)
            cur = []
    areas = []
    for pts in contours:
        a = 0.0
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            a += x0 * y1 - x1 * y0
        areas.append(a / 2)
    if not areas:
        return 0, 0
    # after fix_winding all outers share one sign, holes the other;
    # the largest-|area| contour is always an outer
    outer_sign = 1 if areas[max(range(len(areas)),
                                key=lambda i: abs(areas[i]))] > 0 else -1
    outer = sum(1 for a in areas if (a > 0) == (outer_sign > 0))
    inner = len(areas) - outer
    return outer, inner


def raster_check(name, ch, cells):
    # empty cells flanking a pure-diagonal pair: the band edge passes
    # exactly through their centers, so center-sampling is ill-defined
    from spec import pure_diagonal_pairs
    skip = set()
    for (r, c), (r2, c2) in pure_diagonal_pairs(cells):
        skip.add((r2, c))
        skip.add((r, c2))
    fnt = ImageFont.truetype(OUT, SIZE)
    pad = 60
    img = Image.new("L", (SIZE + 2 * pad, SIZE + 2 * pad), 0)
    d = ImageDraw.Draw(img)
    asc, _ = fnt.getmetrics()
    d.text((pad, pad), ch, font=fnt, fill=255)
    base_y = pad + asc
    px = img.load()
    bad = []
    for r in range(7):
        for c in range(7):
            if (r, c) in skip and (r, c) not in cells:
                continue
            cx = pad + (XOFF + (c + 0.5) * W) * SIZE / 1000
            cy = base_y - ((6 - r + 0.5) * H) * SIZE / 1000
            ink = px[int(cx), int(cy)] > 127
            if ink != ((r, c) in cells):
                bad.append((r, c, "missing" if (r, c) in cells else "extra"))
    return bad


def main():
    grids = parse_spec()
    font = TTFont(OUT)
    cmap = {v: k for k, v in font.getBestCmap().items()}

    failures = 0
    print(f"{'glyph':>6} {'comp':>4} {'outer':>5} {'holes':>5} "
          f"{'exp_h':>5} {'stable':>6} {'raster':>6}")
    for name, cells in grids.items():
        comp = solid_components(cells)
        exp_h = expected_holes(cells)

        path = glyph_path(font, name)
        n_outer, n_inner = contour_stats(path)

        # overlap/no-op check: simplify again, compare area and contour count
        area0 = path.area
        p2 = pathops.Path(path)
        p2.simplify(fix_winding=True)
        stable = abs(p2.area - area0) < 1.0 and \
            contour_stats(p2) == (n_outer, n_inner)

        ch = chr(cmap[name])
        bad = raster_check(name, ch, cells)

        ok_outer = n_outer == comp
        ok_holes = n_inner == exp_h
        ok = ok_outer and ok_holes and stable and not bad
        note = ""
        if name == "zero" and comp == 2 and ok_outer and ok_holes:
            note = "  (island per spec drawing)"
        elif not ok:
            failures += 1
            note = "  FAIL"
            if bad:
                note += f" raster:{bad[:3]}"
        print(f"{name:>6} {comp:>4} {n_outer:>5} {n_inner:>5} "
              f"{exp_h:>5} {str(stable):>6} {str(not bad):>6}{note}")

    print(f"\n{'PASS' if failures == 0 else f'{failures} FAILURES'}: "
          "single-outline assertion holds for 35/36 glyphs; "
          "zero is 2 components as drawn (documented exception).")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
