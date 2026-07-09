"""Parse HeisenMICR.md — the spec file is the source of truth for glyph grids."""
import re
import string
from pathlib import Path

SPEC = str(Path(__file__).with_name("HeisenMICR.md"))  # spec lives beside this module

# The ``## <char>`` heading in the spec is the literal character; this maps the
# ones that need a PostScript-safe glyph name (letters A-Z name themselves).
GLYPH_NAMES = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
    "!": "exclam", '"': "quotedbl", "#": "numbersign", "$": "dollar",
    "%": "percent", "&": "ampersand", "'": "quotesingle", "(": "parenleft",
    ")": "parenright", "*": "asterisk", "+": "plus", ",": "comma",
    "-": "hyphen", ".": "period", "/": "slash", ":": "colon",
    ";": "semicolon", "<": "less", "=": "equal", ">": "greater",
    "?": "question", "@": "at", "[": "bracketleft", "\\": "backslash",
    "]": "bracketright", "^": "asciicircum", "_": "underscore",
    "`": "grave", "{": "braceleft", "|": "bar", "}": "braceright",
    "~": "asciitilde",
}

# glyph name -> Unicode code point (letters + everything in GLYPH_NAMES)
CODEPOINTS = {ch: ord(ch) for ch in string.ascii_uppercase}
CODEPOINTS.update({name: ord(ch) for ch, name in GLYPH_NAMES.items()})

# how many ``## <char>`` sections the spec is expected to define
EXPECTED_GLYPHS = len(string.ascii_uppercase) + len(GLYPH_NAMES)


def parse_spec(path=SPEC):
    """Return {glyph_name: set of (row, col)} parsed from the ASCII-art grids."""
    text = open(path).read()
    sections = re.findall(r"^## (\S+)[^\n]*\n+```\n(.*?)```", text, re.M | re.S)
    glyphs = {}
    for key, block in sections:
        name = GLYPH_NAMES.get(key, key)
        # split into rows without eating legitimately-empty trailing rows: the
        # capture ends just before the closing fence, so drop only that one
        # newline, then pad short grids (omitted trailing blank rows) up to 7.
        rows = [line.rstrip("\r") for line in block.split("\n")]
        if rows and rows[-1] == "":
            rows.pop()
        assert len(rows) <= 7, f"{key}: {len(rows)} rows (expected <= 7)"
        rows += [""] * (7 - len(rows))
        cells = set()
        for r, line in enumerate(rows):
            for c, ch in enumerate(line):
                if ch == "#":
                    cells.add((r, c))
        assert all(c <= 6 for _, c in cells), f"{key}: column beyond 6"
        glyphs[name] = cells
    assert len(glyphs) == EXPECTED_GLYPHS, \
        f"parsed {len(glyphs)} glyphs, expected {EXPECTED_GLYPHS}"
    return glyphs


def pure_diagonal_pairs(cells):
    """Diagonal pairs whose two mutual orthogonal cells are both empty."""
    pairs = []
    for (r, c) in cells:
        for dc in (+1, -1):
            b = (r + 1, c + dc)
            if b in cells and (r + 1, c) not in cells and (r, c + dc) not in cells:
                pairs.append(((r, c), b))
    return pairs


def stem_junction_pairs(cells):
    """Diagonal pairs where a diagonal stroke runs into a stem.

    A ``pure_diagonal_pair`` renders as a smooth slanted stroke only when it is
    isolated (both mutual-orthogonal "notch" cells empty). Where such a stroke
    terminates against a stem, the terminating step has exactly one notch cell
    filled (the stem), so it is not "pure" and the stroke would stair-step into
    the stem. This returns those terminating steps — the diagonal pairs that
    continue an existing pure stroke by one cell into a stem — so the build can
    add a join band there and let the diagonal run cleanly into the stem.
    """
    pure = set(pure_diagonal_pairs(cells))
    out = []
    for (r, c) in cells:
        for dc in (+1, -1):
            b = (r + 1, c + dc)
            if b not in cells:
                continue
            below_a = (r + 1, c) in cells
            beside_a = (r, c + dc) in cells
            if below_a + beside_a != 1:        # 0 = pure, 2 = solid interior
                continue
            # continues a pure stroke of the same direction from either end
            predecessor = ((r - 1, c - dc), (r, c))
            successor = (b, (r + 2, c + 2 * dc))
            if predecessor in pure or successor in pure:
                out.append(((r, c), b))
    return out


def corner_bevel_pairs(cells):
    """Diagonal pairs that bevel a stair-stepped corner on the glyph's outer edge.

    A junction with exactly one filled notch is a unit stair-step where two
    strokes meet. We bevel it into a single diagonal when both of these hold:

      * the empty (clipped) notch lies on the outer boundary of the 7x7 grid, so
        the step is a corner of the letterform rather than an interior detail; and
      * the stroke running through ``A`` does not continue straight past the
        junction — the cell opposite the filled notch is empty — so it is a
        genuine corner/reversal, not a branch that keeps going.

    This captures the prominent "the corner should be diagonal" cases (B
    lower-right, Q upper-left, U lower-left, the top-left/bottom-right of S) plus
    S's two mid-height reversal curves, while leaving branch shoulders (A, H) and
    stubs (J, 4) as crisp steps. Diagonal strokes that simply run out to a
    bounding-box corner (M, N, W, X, Z, 1) also qualify, matching what
    ``stem_junction_pairs`` already does for those.
    """
    out = []
    for (r, c) in cells:
        for dc in (+1, -1):
            b = (r + 1, c + dc)
            if b not in cells:
                continue
            below_a = (r + 1, c) in cells
            beside_a = (r, c + dc) in cells
            if below_a + beside_a != 1:
                continue
            empty_notch = (r + 1, c) if not below_a else (r, c + dc)
            if empty_notch[0] not in (0, 6) and empty_notch[1] not in (0, 6):
                continue
            # opposite the filled notch across A: filled => stroke runs straight on
            if below_a:                       # filled notch below A -> check above
                runs_through = (r - 1, c) in cells
            else:                             # filled notch beside A -> check behind
                runs_through = (r, c - dc) in cells
            if not runs_through:
                out.append(((r, c), b))
    return out


def solid_components(cells):
    """Connected components: edge adjacency + pure-diagonal joins."""
    pairs = set()
    for (r, c) in cells:
        for (nr, nc) in ((r + 1, c), (r, c + 1)):
            if (nr, nc) in cells:
                pairs.add(((r, c), (nr, nc)))
    pairs.update(pure_diagonal_pairs(cells))
    parent = {cell: cell for cell in cells}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        parent[find(a)] = find(b)
    return len({find(x) for x in cells})


def expected_holes(cells):
    """Empty-cell components (4-conn) not reaching the border of a padded grid."""
    empties = {(r, c) for r in range(-1, 8) for c in range(-1, 8)} - cells
    seen, holes = set(), 0
    for start in empties:
        if start in seen:
            continue
        stack, comp, touches_border = [start], [], False
        seen.add(start)
        while stack:
            r, c = stack.pop()
            comp.append((r, c))
            if r in (-1, 7) or c in (-1, 7):
                touches_border = True
            for nr, nc in ((r+1, c), (r-1, c), (r, c+1), (r, c-1)):
                if (nr, nc) in empties and (nr, nc) not in seen:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        if not touches_border:
            holes += 1
    return holes


def main():
    g = parse_spec()
    print(f"{'glyph':>6} {'cells':>5} {'diag':>4} {'comp':>4} {'holes':>5}")
    for name, cells in g.items():
        print(f"{name:>6} {len(cells):>5} {len(pure_diagonal_pairs(cells)):>4} "
              f"{solid_components(cells):>4} {expected_holes(cells):>5}")


if __name__ == "__main__":
    main()
