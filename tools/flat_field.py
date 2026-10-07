#!/usr/bin/env python3
"""flat_field.py — flat or empty picture check on rendered frames of an integer-grid pixel-art film.

    python3 tools/flat_field.py --bg '#0b1020' FRAME.png [FRAME.png ...]
        [--grid 320x180] [--rows N] [--empty-frac 0.15] [--strip-cols 8] [--flat-frac 0.75] [--json]

Each frame is reduced to the film's logical grid (one sample, the centre pixel, per cell; the frame size must be a
whole multiple of the grid) and the first --rows rows (default: all) are examined. Two findings:

  empty-background  the cells equal to --bg (the colour the engine shows where nothing is drawn) cover at least
                    --empty-frac of the picture, or --strip-cols or more full-height columns in a row are all --bg.
                    This is what a zoom/pan view running past the set looks like (Lula 3.0.0, scene 11a: 36 columns
                    past the set, 22 % of the picture flat background; pnkit.pixel.view_outside finds it at build
                    time, this finds it in a frame that exists).
  flat-field        one colour other than --bg covers at least --flat-frac of the picture: an icon or a card on a
                    flat field, where the style wants every shot to be a place with light and props. Infographics
                    that are meant to be flat are waived by the caller.

THRESHOLDS ARE NOT A PRECISION STUDY. The defaults were judged by eye on about 12 real frames of one film: at a
flat fraction of 0.55, plain-wall rooms with figures were flagged too, so 0.75 was kept. There is no measured
false-positive or false-negative rate. Tune them per film and read the frames flagged; do not treat a pass as proof.
Run it on the first rendered frame of each shot (a still is enough), after the build-time checks in pnkit.pixel.

Prints one line per frame: the findings (or "ok"), the frame path and the measures. --json prints a list of
{path, flags, empty_frac, empty_strip_cols, dominant_frac, dominant_rgb}. Exit status 0 when no frame is flagged, 1
when any is, 2 when Pillow is missing. Needs Pillow, imported inside the function; nothing is rendered here.
"""
import argparse, json, sys
from collections import Counter

EMPTY_FRAC = 0.15
STRIP_COLS = 8
FLAT_FRAC = 0.75


def parse_rgb(text):
    """'#rrggbb' or 'r,g,b' -> (r, g, b)"""
    t = text.strip()
    if t.startswith("#") and len(t) == 7:
        return tuple(int(t[i:i + 2], 16) for i in (1, 3, 5))
    parts = [int(p) for p in t.split(",")]
    if len(parts) != 3 or not all(0 <= p <= 255 for p in parts):
        raise ValueError(f"not a colour: {text!r} (use #rrggbb or r,g,b)")
    return tuple(parts)


def _pillow():
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("flat_field: Pillow is required to read frames (pip install pillow)")
    return Image


def to_grid(img, grid=(320, 180), rows=None):
    """the picture as rows of RGB tuples on the logical grid (centre pixel of each cell); raises ValueError when
    the frame is not a whole multiple of the grid"""
    gw, gh = grid
    im = img.convert("RGB")
    w, h = im.size
    if w % gw or h % gh or w // gw != h // gh:
        raise ValueError(f"expected a whole multiple of the {gw}x{gh} grid, got {w}x{h}")
    k = w // gw
    px = im.load()
    n = gh if rows is None else min(rows, gh)
    return [[px[x * k + k // 2, y * k + k // 2] for x in range(gw)] for y in range(n)]


def analyse(img, bg, grid=(320, 180), rows=None, empty_frac=EMPTY_FRAC, strip_cols=STRIP_COLS, flat_frac=FLAT_FRAC):
    """measures and flags of one frame (a Pillow image); bg is an (r, g, b) tuple"""
    bg = tuple(bg)
    g = to_grid(img, grid, rows)
    gw, nrows = grid[0], len(g)
    n = gw * nrows
    counts = Counter(c for row in g for c in row)
    out = {"empty_frac": counts.get(bg, 0) / n}
    best = run = 0
    for x in range(gw):
        if all(g[y][x] == bg for y in range(nrows)):
            run += 1
            best = max(best, run)
        else:
            run = 0
    out["empty_strip_cols"] = best
    dom, cnt = counts.most_common(1)[0]
    out["dominant_frac"] = cnt / n
    out["dominant_rgb"] = tuple(int(v) for v in dom)
    flags = []
    if out["empty_frac"] >= empty_frac or best >= strip_cols:
        flags.append("empty-background")
    if out["dominant_frac"] >= flat_frac and out["dominant_rgb"] != bg:
        flags.append("flat-field")
    out["flags"] = flags
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("frames", nargs="+")
    ap.add_argument("--bg", required=True, help="the colour shown where nothing is drawn: #rrggbb or r,g,b")
    ap.add_argument("--grid", default="320x180", help="logical grid WxH (default 320x180)")
    ap.add_argument("--rows", type=int, help="examine only the first N grid rows (default all; Lula used 146 to leave the plate band out)")
    ap.add_argument("--empty-frac", type=float, default=EMPTY_FRAC)
    ap.add_argument("--strip-cols", type=int, default=STRIP_COLS)
    ap.add_argument("--flat-frac", type=float, default=FLAT_FRAC)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    Image = _pillow()
    gw, gh = (int(v) for v in a.grid.lower().split("x"))
    bg = parse_rgb(a.bg)
    results, bad = [], 0
    for p in a.frames:
        try:
            with Image.open(p) as im:
                r = analyse(im, bg, (gw, gh), a.rows, a.empty_frac, a.strip_cols, a.flat_frac)
        except (ValueError, OSError) as e:
            print("SKIP", p, e, file=sys.stderr)
            continue
        r["path"] = p
        results.append(r)
        bad += bool(r["flags"])
        if not a.json:
            print(f"{','.join(r['flags']) or 'ok':20s} {p}  empty {r['empty_frac']:.1%}, strip {r['empty_strip_cols']} cols, "
                  f"dominant {r['dominant_frac']:.0%} rgb{r['dominant_rgb']}")
    if a.json:
        print(json.dumps(results, indent=1))
    else:
        print(f"{len(results)} frame(s), {bad} flagged")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
