"""pnkit.pixelart.frames — checks on rendered frames of an integer-grid pixel-art film (Pillow, imported by the caller).

  flat_field(img, bg)       empty-background (the colour shown where nothing is drawn covers >= 15 % of the picture, or
                            >= 8 full-height columns in a row: a view past its set) and flat-field (one other colour
                            covers >= 75 %). From tools/flat_field.py; THRESHOLDS ARE NOT A PRECISION STUDY (judged by
                            eye on about 12 frames of Lula 3.0.0). Run it on the first frame of each shot.
  plate_visible(img, rect)  a plate card is in the frame: at least 35 % of the card's inner area has its fill colour and
                            60 % of its top border row the border colour (from Lula check_render_plates.py: a plate
                            added to the XML but drawn under a set or a zoom group is declared and never seen).
"""
from collections import Counter

EMPTY_FRAC = 0.15
STRIP_COLS = 8
FLAT_FRAC = 0.75
FILL_MIN, BORDER_MIN = 0.35, 0.60


def parse_rgb(text):
    """'#rrggbb' or 'r,g,b' -> (r, g, b)"""
    t = text.strip()
    if t.startswith("#") and len(t) == 7:
        return tuple(int(t[i:i + 2], 16) for i in (1, 3, 5))
    parts = [int(p) for p in t.split(",")]
    if len(parts) != 3 or not all(0 <= p <= 255 for p in parts):
        raise ValueError(f"not a colour: {text!r} (use #rrggbb or r,g,b)")
    return tuple(parts)


hex_rgb = parse_rgb


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


flat_field = analyse


def _near(px, rgb, tol):
    return all(abs(a - b) <= tol for a, b in zip(px[:3], rgb))


def plate_visible(img, rect, unit=6, fill="#000000", border="#000000", tol=10):
    """{visible, fill, border}: shares of the card's fill colour inside rect (logical x0, y0, x1, y1, two cells in from
    each edge, every third pixel) and of the border colour along its top row"""
    im = img.convert("RGB")
    fc, bc = parse_rgb(fill), parse_rgb(border)
    x0, y0, x1, y1 = (int(v) * unit for v in rect)
    tot = hit = 0
    for y in range(y0 + 2 * unit, y1 - 2 * unit, 3):
        for x in range(x0 + 2 * unit, x1 - 2 * unit, 3):
            tot += 1; hit += _near(im.getpixel((x, y)), fc, tol)
    top = [_near(im.getpixel((x, y0 + 2)), bc, tol) for x in range(x0 + unit, x1 - unit, 3)]
    ff, tf = hit / max(tot, 1), sum(top) / max(len(top), 1)
    return {"visible": ff >= FILL_MIN and tf >= BORDER_MIN, "fill": round(ff, 3), "border": round(tf, 3)}
