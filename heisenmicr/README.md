# HeisenMICR

A monospaced MICR-style display font built programmatically from an ASCII-art
spec, plus the tooling that compiles and verifies it.

The spec ([`HeisenMICR.md`](HeisenMICR.md)) is the source of truth: each glyph is
a 7×7 grid of `#` modules. The build pipeline turns each module into a rectangle
(uppercase 1.8∶1, lowercase 1∶1 small caps), joins diagonally-adjacent modules
with slanted bands, unions everything with skia-pathops, and rounds every corner
with a fillet. It covers A–Z, digits, and ASCII punctuation; lowercase is derived
from the capitals as small caps set in the bottom square. See the spec's
top-matter for the full metrics and rendering rules.

## Layout

| File | Purpose |
| --- | --- |
| `HeisenMICR.md` | Glyph spec (7×7 ASCII grids) — the source of truth |
| `spec.py` | Parse the spec; connectivity / hole analysis helpers |
| `build.py` | Compile `HeisenMICR.ttf` from the spec |
| `test.py` | Assertions against the built font (contours, holes, raster) |
| `preview.py` | Render proof sheets (`proof_*.png`) |
| `specimen.py` | Render the specimen sheet |
| `HeisenMICR.ttf` | The compiled font (committed artifact) |
| `specimen_heisenmicr.png` | Specimen sheet (committed artifact) |

## Requirements

[uv](https://docs.astral.sh/uv/) manages the Python version and dependencies
(`fonttools`, `skia-pathops`, `pillow`).

## Usage

```sh
uv sync                 # create .venv and install dependencies

uv run build.py         # compile HeisenMICR.ttf from the spec
uv run test.py          # detailed per-glyph assertion report
uv run pytest           # build + run the assertions as a test suite
uv run spec.py          # print the grid connectivity/hole report
uv run preview.py       # render proof_grid.png + proof_text.png
uv run preview.py ABC   # render a close-up sheet for specific characters
uv run specimen.py      # regenerate specimen_heisenmicr.png
```

`uv run test.py` and `uv run pytest` both exit non-zero if any glyph fails its
assertions, so either works in CI.
