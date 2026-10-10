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
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit.pixelart.frames import EMPTY_FRAC, STRIP_COLS, FLAT_FRAC, parse_rgb, to_grid, analyse   # noqa: E402  (the library holds the check)


def _pillow():
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("flat_field: Pillow is required to read frames (pip install pillow)")
    return Image


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
