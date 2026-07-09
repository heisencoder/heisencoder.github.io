"""End-to-end checks: parse the spec, build the TTF, and run the glyph assertions.

Run with `uv run pytest` (or `uv run test.py` for the detailed report)."""
from pathlib import Path

import build
import spec
import test as micr_test


def test_spec_parses_36_glyphs():
    glyphs = spec.parse_spec()
    assert len(glyphs) == 36
    # every glyph is a 7x7 grid, columns 0..6
    for name, cells in glyphs.items():
        assert all(0 <= r <= 6 and 0 <= c <= 6 for (r, c) in cells), name


def test_build_produces_ttf():
    build.build()
    assert Path(build.OUT).exists()
    assert Path(build.OUT).stat().st_size > 0


def test_glyph_assertions_pass():
    # build first so the TTF matches the current spec/geometry
    build.build()
    failures = micr_test.main()
    assert failures == 0
