"""pnkit.pixel — build-time checks for integer-grid pixel-art films (stdlib only, no render needed).

A pixel-art film draws on a small logical grid (Lula 3.0.0: 320 x 180 cells, each 6 x 6 output pixels) and shows
it through zoom/pan groups. Four defects survived human review of that film and are cheap to catch while the scene
is being built, before any frame exists. Each function returns a finding (a string, a list of strings, or a
ViewOutside) and never raises on a finding; the caller decides whether a finding fails the build or is waived with
a reason. Arguments that cannot describe a picture at all (zero sizes) raise ValueError.

  view_outside     a zoom/pan view that shows area beyond the set: the rest is the flat background colour
                   (Lula scene 11a: zoom(2, 276, 76) on a 320-column set showed x 196..356, 22 % outside).
  figure_cut       a sprite cropped through its torso or thighs with nothing drawn over the cut (11a: crop at row
                   30 of a 51-row woman, 59 %).
  plate_line_breaks  a wrapped text plate that ends a line in ":" or an arrow, or leaves a value alone on its own
                   line ("2003: 12,4% → 2010:" / "6,7%").
  scale_off_grid   a scale that is not a positive whole number resamples cells and breaks the pixel grid.

Thresholds (CUT_LO, CUT_HI, TOL) are judgement calls from one film, not measured constants; waive a finding that
is intended and say why.
"""
import math
import re
from collections import namedtuple

__all__ = ["view_outside", "ViewOutside", "figure_cut", "plate_line_breaks", "scale_off_grid", "CUT_LO", "CUT_HI", "TOL"]

CUT_LO, CUT_HI = 0.35, 0.85    # a crop between these fractions of the sprite height (exclusive) goes through the body
TOL = 0.5                      # cells of overshoot ignored at each edge (rounding of a half-cell pan)
ARROWS = ("→", "->", ">")
_VALUE = re.compile(r"[\d.,]+\s*%?")


class ViewOutside(namedtuple("ViewOutside", "x0 y0 x1 y1 cols rows fraction")):
    """The region (x0, y0, x1, y1) a view shows, in set cells; the columns and rows of it beyond the set; and the
    fraction of the view's area that lies outside the set (0..1)."""
    __slots__ = ()

    @property
    def outside(self):
        """True when the view overshoots the set by more than the tolerance on any edge"""
        return self.cols > 0 or self.rows > 0

    def describe(self):
        return (f"view shows set x {self.x0:g}..{self.x1:g}, y {self.y0:g}..{self.y1:g}: "
                f"{self.cols:g} columns / {self.rows:g} rows outside ({self.fraction:.0%} of the picture is background)")


def view_outside(set_w, set_h, grid_w, grid_h, zoom, cx, cy, anchor=None, tol=TOL):
    """What a zoom/pan view shows and how much of it lies outside the set.

    The set is the drawn area, x 0..set_w, y 0..set_h (the set's own bg, wider or taller than the grid for a pan).
    The grid is the picture, grid_w x grid_h cells. A zoom group puts the set point (cx, cy) at `anchor`, a point of
    the picture (default its centre), and magnifies by `zoom`, so the view is
    x cx - ax/zoom .. cx + (grid_w - ax)/zoom, y cy - ay/zoom .. cy + (grid_h - ay)/zoom.
    Lula 3.0.0 anchors at (160, 73) of 320 x 180, leaving the bottom rows for plates: pass anchor=(160, 73).
    `tol` cells of overshoot per edge are ignored.
    Lula 11a: view_outside(320, 180, 320, 180, 2, 276, 76, anchor=(160, 73)) -> 36 columns, 22.5 % outside;
    cx=240 is clean."""
    if min(set_w, set_h, grid_w, grid_h) <= 0 or zoom <= 0:
        raise ValueError("view_outside: set and grid sizes and zoom must be positive")
    ax, ay = anchor if anchor is not None else (grid_w / 2, grid_h / 2)
    x0, x1 = cx - ax / zoom, cx + (grid_w - ax) / zoom
    y0, y1 = cy - ay / zoom, cy + (grid_h - ay) / zoom
    out_l, out_r = max(0.0, -x0), max(0.0, x1 - set_w)
    out_t, out_b = max(0.0, -y0), max(0.0, y1 - set_h)
    cols = (out_l if out_l > tol else 0.0) + (out_r if out_r > tol else 0.0)    # overshoot within tol is ignored
    rows = (out_t if out_t > tol else 0.0) + (out_b if out_b > tol else 0.0)
    w, h = x1 - x0, y1 - y0
    inside_w = max(0.0, min(x1, set_w) - max(x0, 0.0))
    inside_h = max(0.0, min(y1, set_h) - max(y0, 0.0))
    fraction = 1.0 - (inside_w * inside_h) / (w * h)
    return ViewOutside(x0, y0, x1, y1, cols, rows, 0.0 if fraction < 1e-12 else fraction)


def figure_cut(sprite_h, crop_row, occluded=False):
    """A finding string when a sprite cropped at `crop_row` (of `sprite_h` rows, after scaling) is cut through the
    torso or thighs with nothing covering the cut, else None. Crops under 35 % (head and shoulders) and over 85 %
    (feet only) are allowed, as is any crop whose cut line is hidden by something drawn over it (`occluded`: a
    table, a counter; the caller decides, pnkit knows nothing of draw order)."""
    if sprite_h <= 0:
        raise ValueError("figure_cut: sprite_h must be positive")
    frac = crop_row / sprite_h
    if CUT_LO < frac < CUT_HI and not occluded:
        return (f"cropped at row {crop_row:g} of {sprite_h:g} ({frac:.0%}) and nothing covers the cut: "
                f"the torso or thighs end in mid-air")
    return None


def plate_line_breaks(lines):
    """Reasons (strings, empty when the break is fine) why a plate's wrapped lines break meaning: a line ending in
    ":" or an arrow (a label parted from what it labels), or, after the first line, a short line that is only a
    number or a percentage (a value parted from its label). Lula 09: ["2003: 12,4% → 2010:", "6,7%"]."""
    out = []
    for i, ln in enumerate(lines):
        t = ln.strip()
        if t.endswith(":") or any(t.endswith(a) for a in ARROWS):
            out.append(f"line {i + 1} {t!r} ends in a label colon or an arrow")
        elif i > 0 and len(t) <= 8 and _VALUE.fullmatch(t):
            out.append(f"line {i + 1} {t!r} is a lone value orphaned from its label")
    return out


def scale_off_grid(scale, tol=1e-6):
    """None when `scale` keeps the integer grid (a positive whole number, up to float noise), else a finding
    string. A scale of 1.5 or 0.5 resamples each logical cell to unequal pixel counts and smears the pixel art."""
    if isinstance(scale, bool) or not isinstance(scale, (int, float)) or math.isnan(scale) or math.isinf(scale):
        return f"scale {scale!r} is not a finite number"
    if scale <= 0 or abs(scale - round(scale)) > tol:
        return f"scale {scale:g} is not a positive whole number: cells would be resampled and the pixel grid broken"
    return None
