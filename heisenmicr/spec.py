"""Parse HeisenMICR.md — the spec file is the source of truth for glyph grids."""
import re

SPEC = "/home/claude/heisenmicr/HeisenMICR.md"  # local copy, O corrected per review

DIGIT_NAMES = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
}


def parse_spec(path=SPEC):
    """Return {glyph_name: set of (row, col)} plus raw grids for reporting."""
    text = open(path).read()
    sections = re.findall(r"^## (\S+)\s*\n+```\n(.*?)```", text, re.M | re.S)
    glyphs = {}
    for key, block in sections:
        name = DIGIT_NAMES.get(key, key)
        rows = block.rstrip("\n").split("\n")
        cells = set()
        for r, line in enumerate(rows):
            for c, ch in enumerate(line):
                if ch == "#":
                    cells.add((r, c))
        assert len(rows) == 7, f"{key}: {len(rows)} rows (expected 7)"
        assert all(c <= 6 for _, c in cells), f"{key}: column beyond 6"
        glyphs[name] = cells
    assert len(glyphs) == 36, f"parsed {len(glyphs)} glyphs, expected 36"
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


if __name__ == "__main__":
    g = parse_spec()
    print(f"{'glyph':>6} {'cells':>5} {'diag':>4} {'comp':>4} {'holes':>5}")
    for name, cells in g.items():
        print(f"{name:>6} {len(cells):>5} {len(pure_diagonal_pairs(cells)):>4} "
              f"{solid_components(cells):>4} {expected_holes(cells):>5}")
