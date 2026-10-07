---
disclaimer:
  notice: >-
    No information within this document should be taken for granted.
    Any statement or premise not backed by a real logical definition
    or verifiable reference may be invalid, erroneous, or a hallucination.
  generated_by: "Claude Sonnet 5.5 via Claude Code"
  date: "2026-10-07"
---

# Release notes: picture checks (branch `feat/picture-checks`)

Not released: `__version__`, `kit.json` and `CHANGELOG.md` are untouched. The change is additive (a new module, two new
tools, one added check in gate.py that prints nothing for a clean scene), so by the CHANGELOG's own rule it is a minor
release: 0.7.0. The maintainer applies the entries below when releasing.

## CHANGELOG entry (proposed, for the top of CHANGELOG.md)

```markdown
## 0.7.0 — 2026-10-07 — picture checks for integer-grid pixel-art films

Adds checks that need no render, from the Lula 3.0.0 reviews (a framing defect in scene 11a survived four human reads).
Additive: no existing default's output changes; the golden tests are unaffected.

Added
- `pnkit.pixel` (standard library only): `view_outside(set_w, set_h, grid_w, grid_h, zoom, cx, cy, anchor=None)` returns
  the region a zoom/pan view shows and how much of it lies outside the set (Lula 11a: `zoom(2, 276, 76)` on a 320-column
  set, 22.5 % outside; `zoom(2, 240, 76)` clean); `figure_cut(sprite_h, crop_row, occluded=False)` finds a crop between
  35 % and 85 % of the sprite height with nothing over the cut; `plate_line_breaks(lines)` finds a line ending in ":" or
  an arrow and a value orphaned from its label ("2003: 12,4% → 2010:" / "6,7%"); `scale_off_grid(scale)` finds a scale
  that is not a positive whole number.
- `tools/flat_field.py`: empty-background and flat-field findings on rendered frames, with the frame paths. Thresholds
  (`--empty-frac`, `--strip-cols`, `--flat-frac`) are parameters whose defaults were judged by eye on about 12 frames of
  one film; this is not a precision study. Needs Pillow, imported at run time with a clear message when missing.
- `tools/instance_clock.py`: flags an `<instance>` with no `start` whose symbol reads `time` in a `condition` (its first
  frame is on the absolute clock). `tools/gate.py` runs it and fails on a finding; a scene without the problem gets the
  same output as before.
- Tests: `tests/test_pixel.py`, `tests/test_picture_tools.py`, with the Lula 11a cases and the fixture
  `tests/fixtures/lula_11a_instance_clock.scene.xml`.

Checked against: the unit tests. The v013 golden project is not present on the host that built this change, and no file
under `pnkit/` that the golden build uses was edited (only `pnkit/pixel.py` was added), so its output cannot differ.
```

## kit.json (proposed)

Add to `components`:

```json
[
  {"name": "pixel.view_outside / pixel.ViewOutside / pixel.figure_cut / pixel.plate_line_breaks / pixel.scale_off_grid", "module": "pnkit.pixel",
   "summary": "Build-time checks for integer-grid pixel-art films: the region a zoom/pan view shows and how much lies outside the set; a sprite crop through the torso with nothing over the cut; a plate line that ends in a colon or arrow or leaves a value alone; a scale that breaks the pixel grid.",
   "params": ["view_outside(set_w, set_h, grid_w, grid_h, zoom, cx, cy, anchor=None, tol=0.5) -> ViewOutside(x0, y0, x1, y1, cols, rows, fraction; .outside, .describe())", "figure_cut(sprite_h, crop_row, occluded=False) -> finding string or None", "plate_line_breaks(lines) -> [reason]", "scale_off_grid(scale) -> finding string or None"],
   "rules": ["a zoom/pan view must stay inside the set: the rest renders as flat background (Lula 3.0.0 scene 11a)", "a sprite is not cropped between 35 % and 85 % of its height unless something covers the cut", "a plate line does not end in ':' or an arrow and a label is not parted from its value", "scales keep the integer grid"]}
]
```

Add to `tools`:

```json
{
  "tools/flat_field.py --bg COLOUR FRAME.png ... [--grid WxH] [--rows N] [--empty-frac F] [--strip-cols N] [--flat-frac F] [--json]": "report frames whose picture is mostly the background colour (empty-background) or one flat colour (flat-field) on the film's logical grid; thresholds judged by eye on about 12 frames, not a precision study; needs Pillow; run on the first rendered frame of each shot",
  "tools/instance_clock.py SCENE ...": "flag an <instance> with no start whose symbol reads time in a condition (arbitrary first frame); gate.py runs it and prints a line only on a finding"
}
```

The `tools/gate.py` entry's text could gain "; instance-clock lint".

Note: `tests/test_tools.py::Catalog` imports each `components` module and checks each dotted name exists; all names above exist in `pnkit.pixel`.
