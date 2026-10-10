"""Reusable sets for 3.0.0 (shared between scene modules). Everything is drawn on the 320x180 logical grid.

Rule for new sets: draw them once here, never copy them into a scene module, and keep every sign's rectangle
as a module constant so the scene module can declare it with `ctx.sign(...)`.
"""
import random
from .ctx import (Geometry, P, r, poly, line, ellipse, lettering, tree, barrel, text_width, sky_gradient)

PF_PLAQUE_TEXT = 'POLÍCIA FEDERAL'
PF_PLAQUE_RECT = (118, 20, 202, 29)        # text rect (plan: x 118-202, y 20-28)
PF_DOOR = (124, 46, 196, 116)              # frame x0, y0, x1, y1
PF_HANDLES = ((156, 80), (162, 80))        # two handles, one per leaf (2.0.0 shot 0 had none, shot 49 had two)


def pf_facade():
    """PF-FACADE: Polícia Federal, Curitiba, dawn; the camera is outside facing the glass double door.
    The same function is the callback anchor for 17d/17f/20a: the frame must come back identical."""
    g = Geometry(); rng = random.Random(2018)
    sky_gradient(g, '#4a6a8c', '#e8a778', 0, 62, 7)
    r(g, 0, 62, 320, 118, 'plaster3')
    # building wall with joints
    r(g, 40, 0, 280, 116, 'plaster1'); r(g, 44, 0, 272, 114, 'plaster2')
    for yy in (21, 43, 66, 90, 112):
        r(g, 44, yy, 272, 1, 'plaster0'); r(g, 44, yy + 1, 272, 1, 'plaster3')
    for xx in (100, 152, 204, 256):
        r(g, xx, 0, 1, 112, 'plaster0')
    # plaque board and the door frame
    r(g, 114, 15, 92, 17, 'wood0'); r(g, 116, 17, 88, 13, 'blue0')
    q, _w = lettering(PF_PLAQUE_TEXT, 'steel3'); g.paste(q, PF_PLAQUE_RECT[0] + 1, 22)       # the sign is part of the set
    x0, y0, x1, y1 = PF_DOOR
    r(g, x0 - 4, y0 - 4, x1 - x0 + 8, y1 - y0 + 4, 'metal0')
    r(g, x0, y0, x1 - x0, y1 - y0, 'black')                        # dark interior
    # barred windows
    for x in (62, 228):
        r(g, x, 43, 30, 42, 'steel0'); r(g, x + 3, 46, 24, 36, 'glass0')
        for xx in range(x + 6, x + 27, 6):
            r(g, xx, 44, 1, 40, 'steel2')
        r(g, x, 64, 30, 2, 'steel1')
    # steps and pavement
    r(g, 116, 116, 88, 3, 'steel1'); r(g, 112, 119, 96, 3, 'steel0'); r(g, 108, 122, 104, 3, 'steel1')
    r(g, 117, 116, 86, 1, 'steel2'); r(g, 109, 122, 102, 1, 'steel2')
    poly(g, [(0, 112), (320, 112), (320, 180), (0, 180)], 'steel0')
    r(g, 108, 122, 104, 3, 'steel1'); r(g, 109, 122, 102, 1, 'steel2')
    for i in range(110):
        r(g, rng.randrange(320), rng.randrange(126, 176), rng.randrange(1, 5), 1, rng.choice(['steel0', 'steel1', 'glass0']))
    for x in (-30, 68, 166, 273, 383):
        line(g, (160 + (x - 160) * .2, 126), (x, 179), .6, 'trouser0')
    # tree, fence, barrel (as in 2.0.0 prison())
    tree(g, 22, 107, 101, 3)
    for x in range(0, 50, 8):
        r(g, x, 78, 2, 40, 'metal0'); r(g, x, 78, 1, 39, 'steel1')
    r(g, 0, 85, 50, 2, 'steel0'); r(g, 0, 113, 50, 2, 'steel0')
    g.paste(barrel(17, 24, 'metal0'), 284, 113)
    return g


def pf_leaf(side):
    """One glass leaf of the double door (side 0 = left, 1 = right), with its handle. Placed over the dark interior."""
    x0, y0, x1, y1 = PF_DOOR
    w = (x1 - x0) // 2
    g = Geometry()
    r(g, 0, 0, w, y1 - y0, 'steel0'); r(g, 2, 2, w - 4, y1 - y0 - 4, 'glass0')
    r(g, 4, 4, w - 8, 20, 'glass1')
    poly(g, [(5, 5), (14, 5), (6, 22)], 'glass2')
    r(g, 2, 44, w - 4, 2, 'steel1')
    hx = (PF_HANDLES[side][0] - x0) - side * w
    r(g, hx, 34, 2, 10, 'steel3'); r(g, hx, 34, 2, 1, 'ivory')
    return g, x0 + side * w, y0


def officer_silhouette():
    g = Geometry()
    poly(g, [(2, 8), (8, 8), (10, 14), (10, 40), (0, 40), (0, 14)], 'blue0')
    ellipse(g, 5, 4, 3, 4, 'metal0'); r(g, 1, 0, 8, 2, 'black')
    return g


# =====================================================================================================================
# 3.0.0 shared sets (gothan-city, art lead): recurring house, BAIRRO street, office, table, school street.
# Every function is pure and deterministic (seeded). Companion `*_fg` / `*_pieces` functions return overlays on the same
# 320x180 canvas (origin 0,0) so that figures can stand BETWEEN the background and the foreground piece (desk front, counter front).
# Signs: module constants `*_SIGN` = (text, rect) with rect = (x0, y0, x1, y1), exclusive x1/y1, in the coordinates of the
# Geometry the function returns (for the wide BAIRRO street that is the unpanned 620 px wide background).
# See SETS.md for what each parameter means and which shot uses which variant.
# =====================================================================================================================
from .ctx import crate, chair, resize, flip                                                  # noqa: E402
from .scene_art import shelf                                                                  # noqa: E402

_PAL_CACHE = {}
_PAL_KEY = -1
_PAL_LIST = []


def _complete_palette():
    """Load every module that adds colours to P (f2_, f3_, f4_), so that P is the same whichever scene is built first or alone."""
    import importlib
    for m in ('figures_v2', 'figures_v3_pose', 'figures_v3_cast', 'figures_v3_extra'):
        importlib.import_module('.' + m, __package__)


_complete_palette()


def _rgb(h):
    h = P.get(h, h)
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _snap(rgb):
    """Nearest colour of the shared palette P (the f2_/f3_/f4_/v3_ additions included).

    Deterministic by construction (a scene's bytes must not depend on the process): the candidates are the sorted distinct hex values of
    P, ties go to the smaller hex, and the cache is dropped whenever P grows. P is completed before any snap by _complete_palette()."""
    global _PAL_KEY, _PAL_LIST
    if _PAL_KEY != len(P):
        _PAL_LIST = sorted(set(P.values())); _PAL_KEY = len(P); _PAL_CACHE.clear()
    key = tuple(rgb)
    if key not in _PAL_CACHE:
        _PAL_CACHE[key] = min(_PAL_LIST, key=lambda hx: (sum((a - b) ** 2 for a, b in zip(_rgb(hx), key)), hx))
    return _PAL_CACHE[key]


def _grade(g, mul=(1, 1, 1), add=(0, 0, 0)):
    """Colour-grade a finished Geometry (time of day) and snap every colour back to the palette P. Returns g."""
    out = {}
    cache = {}
    for xy, c in g.cells.items():
        if c not in cache:
            v = _rgb(c)
            cache[c] = _snap(tuple(max(0, min(255, round(v[i] * mul[i] + add[i]))) for i in range(3)))
        out[xy] = cache[c]
    g.cells = out
    return g


GRADES = {                                    # time of day -> (multiplier, offset)
    'day': None,
    'morning': None,
    'golden': ((1.12, .90, .68), (14, 0, -8)),
    'dusk': ((.88, .70, .66), (10, -2, 6)),
    'night': ((.36, .42, .62), (0, 6, 22)),
}


def _timegrade(g, time):
    gr = GRADES[time]
    if gr:
        _grade(g, *gr)
    return g


def _sign_text(g, text, rect, color):
    """Draw sign text centred in rect (text is 7 rows high, no accents in the signs of these sets)."""
    q, w = lettering(text, color)
    x0, y0, x1, y1 = rect
    assert w <= x1 - x0, (text, w, rect)
    g.paste(q, x0 + (x1 - x0 - w) // 2, y0 + (y1 - y0 - 7) // 2)


def _noise(g, rng, n, x0, y0, x1, y1, cols, wmax=4):
    for _ in range(n):
        r(g, rng.randrange(x0, x1), rng.randrange(y0, y1), rng.randrange(1, wmax), 1, rng.choice(cols))


# ------------------------------------------------------------------------------------------------------------ BAIRRO
# Declared signs of the BAIRRO street (coordinates of the unpanned 620 px wide background; plan SHOTS-3.0.0 08a/08g/30c).
OFICINA_SIGN = ('OFICINA', (4, 40, 98, 50))
MERCEARIA_SIGN = ('MERCEARIA', (137, 40, 198, 50))
ESCOLA_BAIRRO_SIGN = ('ESCOLA', (352, 40, 420, 50))
BAIRRO_W = 620
BAIRRO_BASE = 118                   # ground line of the buildings; the sidewalk runs y 118-146 (figures' soles 121-145)
BAIRRO_X = dict(oficina=(0, 103), mercearia=(108, 227), escola=(336, 436), casa=(446, 576))
BAIRRO_ANCHORS = dict(                  # door positions (x0, y0, x1, y1) in the 620 wide background, for figures and shutter
    oficina_door=(14, 56, 42, 118), shop_door=(118, 64, 150, 118), shop_window=(158, 68, 222, 104),
    school_door=(370, 56, 402, 118), casa_door=(446 + 60, 54, 446 + 104, 118),
    bus_stop=(262, 100, 326, 118), tree=(298, 118), lamp=(240, 118), crate=(88, 118))
SHOP_SHUTTER_RECT = (118, 64, 150, 118)  # the doorway the roll-up shutter closes (see `bairro_shutter`)

CASA_W = 130                             # width of the recurring house's facade (same drawing in BAIRRO and in the exterior views)
CASA_X_EXT = 78                          # facade left edge in `house_exterior`


def casa_rects(fx):
    """Rectangles of the recurring house's facade when its left edge is at x = fx (base line y 118)."""
    return dict(window=(fx + 10, 62, fx + 44, 92), door=(fx + 60, 54, fx + 104, 118), step=(fx + 54, 118, fx + 110, 124),
                roof=(fx - 2, 36, fx + CASA_W + 2, 46), threshold=(fx + 62, 117))


def _casa_facade(g, fx, light='day', door='closed', curtain='open', window_lit=None, lamp_on=False):
    """The recurring house's street front, drawn once and used everywhere (BAIRRO CASA, 09h, 25a, 30g2, 32l, 32m).
    Pale sage wall, tile roof strip, blue two-leaf door, window with blue curtains, a plant by the door."""
    rc = casa_rects(fx)
    lit = (light in ('night', 'dusk')) if window_lit is None else window_lit
    r(g, fx - 2, 36, CASA_W + 4, 9, 'red1')                                                   # tile roof strip
    for xx in range(fx - 2, fx + CASA_W + 2, 5):
        r(g, xx, 36, 1, 9, 'red0'); r(g, xx + 2, 37, 2, 1, 'red2')
    r(g, fx - 3, 44, CASA_W + 6, 2, 'wood0'); r(g, fx - 3, 44, CASA_W + 6, 1, 'wood2')       # eave
    r(g, fx, 46, CASA_W, 72, 'glass2')                                                         # wall
    r(g, fx, 98, CASA_W, 20, 'glass1'); r(g, fx, 98, CASA_W, 1, 'ivory')                       # painted dado
    r(g, fx, 114, CASA_W, 4, 'plaster0')
    rng = random.Random(1946)
    for _ in range(26):
        r(g, fx + rng.randrange(CASA_W - 3), rng.randrange(48, 96), rng.randrange(1, 3), 1, 'plaster3')
    # window
    x0, y0, x1, y1 = rc['window']
    r(g, x0 - 2, y0 - 2, x1 - x0 + 4, y1 - y0 + 4, 'blue1'); r(g, x0, y0, x1 - x0, y1 - y0, 'blue0')
    if lit:
        r(g, x0, y0, x1 - x0, y1 - y0, 'gold'); r(g, x0, y0, x1 - x0, 7, 'cream')
    else:
        r(g, x0, y0, x1 - x0, y1 - y0, 'glass0'); r(g, x0, y0, x1 - x0, 9, 'glass1'); poly(g, [(x0 + 2, y0 + 1), (x0 + 10, y0 + 1), (x0 + 3, y0 + 14)], 'glass2')
    r(g, (x0 + x1) // 2, y0, 1, y1 - y0, 'blue1')                                              # mullion
    cw = {'open': 4, 'half': 12, 'closed': (x1 - x0)}[curtain]
    for side in (0, 1):
        cx = x0 if side == 0 else x1 - cw
        if curtain == 'closed' and side == 1:
            break
        r(g, cx, y0, cw, y1 - y0, 'blue2'); r(g, cx, y0, cw, 1, 'blue3')
        for k in range(cx + 1, cx + cw, 3):
            r(g, k, y0 + 1, 1, y1 - y0 - 1, 'blue1')
    r(g, x0 - 3, y1 + 2, x1 - x0 + 6, 2, 'ivory'); r(g, x0 - 3, y1 + 4, x1 - x0 + 6, 1, 'plaster0')   # sill
    # door (two leaves, painted blue), frame and step
    x0, y0, x1, y1 = rc['door']
    r(g, x0 - 3, y0 - 3, x1 - x0 + 6, y1 - y0 + 3, 'ivory'); r(g, x0 - 3, y0 - 3, 1, y1 - y0 + 3, 'plaster3')
    if door == 'closed':
        r(g, x0, y0, x1 - x0, y1 - y0, 'blue1')
        for lx in (x0 + 2, (x0 + x1) // 2 + 2):
            r(g, lx, y0 + 3, (x1 - x0) // 2 - 4, 22, 'blue0'); r(g, lx, y0 + 3, (x1 - x0) // 2 - 4, 1, 'blue2')
            r(g, lx, y0 + 30, (x1 - x0) // 2 - 4, 26, 'blue0'); r(g, lx, y0 + 30, (x1 - x0) // 2 - 4, 1, 'blue2')
        r(g, (x0 + x1) // 2 - 1, y0, 2, y1 - y0, 'blue2')
        r(g, (x0 + x1) // 2 - 4, y0 + 34, 2, 3, 'gold'); r(g, (x0 + x1) // 2 + 2, y0 + 34, 2, 3, 'gold')
    else:
        _casa_open_interior(g, x0, y0, x1, y1, light)
        r(g, x0 - 1, y0, 3, y1 - y0, 'blue1'); r(g, x0, y0, 1, y1 - y0, 'blue2')            # the left leaf, swung inward, edge-on
        r(g, x1 - 1, y0, 2, y1 - y0, 'blue1')                                              # the right leaf, edge-on
    r(g, rc['step'][0], 118, rc['step'][2] - rc['step'][0], 3, 'plaster3'); r(g, rc['step'][0], 118, rc['step'][2] - rc['step'][0], 1, 'ivory')
    r(g, rc['step'][0] - 4, 121, rc['step'][2] - rc['step'][0] + 8, 3, 'plaster2')
    # number tile (no digits), plant pot, meter box
    r(g, fx + 108, 70, 8, 6, 'ivory'); r(g, fx + 109, 71, 6, 4, 'blue2')
    r(g, fx + 114, 108, 12, 10, 'clay'); r(g, fx + 113, 107, 14, 2, 'brick')
    ellipse(g, fx + 120, 103, 6, 6, 'green'); ellipse(g, fx + 118, 100, 3, 3, 'metal2')
    r(g, fx + 4, 52, 10, 8, 'steel1'); r(g, fx + 5, 53, 8, 6, 'steel3')
    if lamp_on:
        r(g, fx + 56, 50, 4, 4, 'gold')


def _casa_open_interior(g, x0, y0, x1, y1, light):
    """What the open doorway shows: the lit room with the recurring table at the back (the same table as the interior views)."""
    w = x1 - x0
    r(g, x0, y0, w, y1 - y0, 'ivory'); r(g, x0, y0, w, 14, 'cream')                               # warm back wall
    r(g, x0, 96, w, y1 - 96, 'brick'); r(g, x0, 96, w, 1, 'clay')                                  # floor
    r(g, x0 + 4, 76, 18, 14, 'wood0'); r(g, x0 + 5, 77, 16, 12, 'blue0')                           # TV on the shelf, glimpsed
    poly(g, [(x0 + 12, y0), (x0 + 22, y0), (x0 + 30, 96), (x0 + 6, 96)], 'ivory')
    r(g, x0 + 11, y0, 2, 5, 'wood1'); ellipse(g, x0 + 12, y0 + 6, 3, 2, 'gold')                    # hanging bulb
    r(g, x0 + 8, 92, 30, 3, 'wood2'); r(g, x0 + 8, 95, 30, 1, 'wood0')                            # table, far end
    for lx in (x0 + 9, x0 + 35):
        r(g, lx, 95, 2, 14, 'wood1')
    for px in (x0 + 12, x0 + 24):
        ellipse(g, px, 91, 4, 1, 'cream')
    r(g, x0 + 34, 80, 1, 18, 'wood1'); r(g, x0 + 40, 80, 1, 18, 'wood1'); r(g, x0 + 34, 80, 7, 1, 'wood0'); r(g, x0 + 34, 86, 7, 1, 'wood0')        # the old chair at the table's end: empty
    r(g, x0 + 33, 91, 9, 2, 'red1'); r(g, x0 + 36, 91, 3, 1, 'cream')


# ----------------------------------------------------------------------------------------------------- shop, school, works
def _oficina(g, x, w, rng, signs):
    r(g, x, 36, w, 82, 'brick'); r(g, x, 34, w, 4, 'wood0'); r(g, x, 34, w, 1, 'wood2')
    for yy in range(40, 116, 6):
        for xx in range(x + (yy // 6 % 2) * 5, x + w, 10):
            if rng.random() < .5:
                r(g, xx, yy, 8, 1, rng.choice(['clay', 'plaster0']))
    r(g, x + 2, 38, w - 4, 14, 'metal0'); r(g, x + 2, 38, w - 4, 1, 'metal2')
    if signs:
        _sign_text(g, OFICINA_SIGN[0], OFICINA_SIGN[1], 'cream')
    dx0, dy0, dx1, dy1 = BAIRRO_ANCHORS['oficina_door']
    r(g, dx0 - 2, dy0 - 2, dx1 - dx0 + 4, dy1 - dy0 + 2, 'steel0'); r(g, dx0, dy0, dx1 - dx0, dy1 - dy0, 'wood1')
    for zx in range(dx0 + 3, dx1 - 2, 5):
        r(g, zx, dy0 + 2, 1, dy1 - dy0 - 3, 'wood3')
    r(g, dx1 - 6, 90, 2, 3, 'gold')
    r(g, x + 52, 64, 44, 38, 'steel0'); r(g, x + 54, 66, 40, 34, 'glass0')                        # workshop window with a machine inside
    r(g, x + 58, 82, 18, 18, 'steel1'); r(g, x + 56, 80, 22, 3, 'steel2'); r(g, x + 80, 76, 10, 24, 'steel0')
    for bx in range(x + 54, x + 95, 7):
        r(g, bx, 66, 1, 34, 'steel2')
    r(g, x + 50, 102, 48, 3, 'steel1')
    g.paste(crate(19, 14), BAIRRO_ANCHORS['crate'][0], 104)                                       # the crate, behind the walkers


def _mercearia(g, x, w, rng, signs, year, empty=False):
    r(g, x, 36, w, 82, 'plaster3'); r(g, x, 34, w, 4, 'wood0'); r(g, x, 34, w, 1, 'wood2')
    r(g, x, 98, w, 20, 'plaster2')
    for _ in range(40):
        r(g, rng.randrange(x, x + w - 3), rng.randrange(52, 114), rng.randrange(1, 3), 1, 'plaster2')
    r(g, x + 2, 38, w - 4, 14, 'green'); r(g, x + 2, 38, w - 4, 1, 'metal2')
    if signs:
        _sign_text(g, MERCEARIA_SIGN[0], MERCEARIA_SIGN[1], 'ivory')
    for k in range(0, w - 4, 8):                                                                   # striped awning
        r(g, x + 2 + k, 54, 8, 7, 'ivory' if k % 16 else 'red1')
        r(g, x + 2 + k, 61, 8, 2, 'red0' if not k % 16 else 'plaster2')
    r(g, x + 2, 54, w - 4, 1, 'red0')
    sx0, sy0, sx1, sy1 = SHOP_SHUTTER_RECT                                                         # open doorway: dark shop inside
    r(g, sx0 - 2, sy0 - 1, sx1 - sx0 + 4, sy1 - sy0 + 1, 'wood0'); r(g, sx0, sy0, sx1 - sx0, sy1 - sy0, 'umber')
    r(g, sx0 + 2, 90, sx1 - sx0 - 4, 28, 'wood1'); r(g, sx0 + 4, 80, 8, 10, 'ochre')
    wx0, wy0, wx1, wy1 = BAIRRO_ANCHORS['shop_window']                                             # display window
    r(g, wx0 - 2, wy0 - 2, wx1 - wx0 + 4, wy1 - wy0 + 4, 'wood0'); r(g, wx0, wy0, wx1 - wx0, wy1 - wy0, 'glass0')
    r(g, wx0, wy0, wx1 - wx0, 7, 'glass1')
    r(g, wx0, wy0 + 20, wx1 - wx0, 2, 'wood2'); r(g, wx0 + (wx1 - wx0) // 2, wy0, 2, wy1 - wy0, 'wood2')
    for k, gx in enumerate(range(wx0 + 3, wx1 - 4, 6)):
        if empty:
            continue                                                                                # 12c: the shelves are bare
        ellipse(g, gx + 2, wy0 + 17, 2, 2, ['red1', 'gold', 'green', 'ochre'][k % 4])
        r(g, gx, wy0 + 28, 5, 6, ['cream', 'blue2', 'sand'][k % 3])
    r(g, wx0 - 4, wy1 + 1, wx1 - wx0 + 8, 3, 'cream')
    r(g, wx0 - 3, wy1 + 4, wx1 - wx0 + 6, 14, 'plaster1')
    if year >= 2025:
        r(g, wx1 - 12, wy0 + 5, 9, 6, 'ivory'); r(g, wx1 - 11, wy0 + 6, 7, 1, 'red1')          # a small printed offer card in the window
    r(g, x + 98, 100, 14, 18, 'wood1'); r(g, x + 99, 101, 12, 5, 'cream')                          # stacked crates by the wall


def _school(g, x, w, top, base, signs, sign_rect, rng, big=False):
    """The modest school: pale blue wall patched in two places, flat roof, double door, two windows. Used by the BAIRRO (small)
    and by `school_street` (the same drawing, taller)."""
    h = base - top
    r(g, x, top, w, h, 'blue3'); r(g, x, top, w, 3, 'steel1'); r(g, x - 2, top - 2, w + 4, 3, 'steel0')
    r(g, x, base - 14, w, 14, 'blue2'); r(g, x, base - 14, w, 1, 'ivory')
    _noise(g, rng, 40, x, top + 4, x + w - 3, base - 16, ['blue2', 'glass1'], 3)
    by0 = sign_rect[1] - 2
    r(g, x + 4, by0, w - 8, sign_rect[3] - sign_rect[1] + 4, 'blue0'); r(g, x + 4, by0, w - 8, 1, 'blue1')
    if signs:
        _sign_text(g, 'ESCOLA', sign_rect, 'ivory')
    cx = x + w // 2
    dh = 62                                                                                          # door 62 rows (1.27 x the adult), both drawings
    r(g, cx - 18, base - dh - 2, 36, dh + 2, 'steel0'); r(g, cx - 16, base - dh, 32, dh, 'wood1')
    r(g, cx - 1, base - dh, 2, dh, 'wood0')
    for zx in (cx - 14, cx + 3):
        r(g, zx, base - dh + 3, 11, 22, 'wood2'); r(g, zx, base - dh + 3, 11, 1, 'wood3')
    r(g, cx - 5, base - dh // 2 + 3, 2, 3, 'gold'); r(g, cx + 3, base - dh // 2 + 3, 2, 3, 'gold')
    for wx in (x + 8, x + w - 30):                                                                 # windows
        r(g, wx, base - 52, 22, 26, 'steel0'); r(g, wx + 2, base - 50, 18, 22, 'glass0'); r(g, wx + 2, base - 50, 18, 7, 'glass1')
        r(g, wx + 10, base - 50, 1, 22, 'steel0'); r(g, wx, base - 26, 22, 2, 'ivory')
    for (px, py, pw, ph, c) in ((x + 8, base - 82 if big else base - 70, 18, 11, 'plaster3'), (x + w - 34, base - 40 if big else base - 36, 15, 9, 'sand')):  # the two patches
        r(g, px, py, pw, ph, c); r(g, px, py, pw, 1, 'plaster2'); r(g, px, py + ph - 1, pw, 1, 'plaster1')
    r(g, cx - 22, base, 44, 3, 'plaster3'); r(g, cx - 26, base + 3, 52, 3, 'plaster2')            # steps


def _lamp(g, x, base=118):
    r(g, x, base - 52, 2, 52, 'steel0'); r(g, x - 4, base - 54, 10, 3, 'steel0'); r(g, x - 3, base - 51, 8, 2, 'steel2')


def _bus_shelter(g, x, base=118):
    r(g, x, base - 44, 66, 4, 'steel1'); r(g, x, base - 44, 66, 1, 'steel3')
    for px in (x + 2, x + 62):
        r(g, px, base - 44, 2, 44, 'steel0')
    r(g, x + 4, base - 40, 58, 28, 'glass0'); r(g, x + 4, base - 40, 58, 6, 'glass1')
    r(g, x + 8, base - 20, 50, 3, 'wood2'); r(g, x + 10, base - 17, 2, 17, 'wood1'); r(g, x + 52, base - 17, 2, 17, 'wood1')
    r(g, x + 70, base - 58, 2, 58, 'steel0'); r(g, x + 66, base - 62, 10, 8, 'blue1'); r(g, x + 67, base - 61, 8, 6, 'blue3')   # stop post, no text


def bairro(time='day', year=2003, signs=True, shutter='up', shop_empty=False):
    names = {'OFICINA', 'MERCEARIA', 'ESCOLA'} if signs is True else (set() if signs is False else set(signs))
    assert names <= {'OFICINA', 'MERCEARIA', 'ESCOLA'}
    """BAIRRO: the master street, 620 x 180 (wider than the frame; the shot pans it, `ctx.shot(..., pan=(x0, x1))` with negative x).
    OFICINA | MERCEARIA | gap (tree, lamp; bus shelter when year >= 2025) | ESCOLA | CASA.  Sidewalk y 118-146, kerb 146-149.
    time: 'day' | 'golden' (long shadows toward the left, 08g) ; year: 2003 | 2010 | 2025 ; signs: True (all three boards' text), False (32c), or a tuple of names to letter, e.g. ('OFICINA', 'MERCEARIA') for 08a (an undeclared sign never appears and
    never reads as a cropped false word next to another during the pan) ; shutter: 'up' (shop doorway open) | 'down' (roll-up shutter closed over the doorway) |
    'down_wide' (doorway and display window, 12c) ; shop_empty: bare shelves (12c, 2015)."""
    assert time in ('day', 'golden') and year in (2003, 2010, 2025) and shutter in ('up', 'down', 'down_wide')
    g = Geometry(); rng = random.Random(2003)
    w = BAIRRO_W
    sky_gradient(g, '#6f9ab4', '#c9dac6', 0, 40, 6)
    skycols = set(g.cells.values()) | {P['blue3']}
    r(g, 0, 40, w, 120, 'blue3')
    rr = random.Random(32)                                                                         # distant skyline
    for x in range(-10, w, 52):
        h = rr.randrange(22, 44)
        r(g, x, 62 - h, 44, h + 60, 'steel2'); r(g, x, 62 - h, 44, 2, 'steel3')
        for y in range(66 - h, 84, 9):
            for xx in range(x + 5, x + 40, 9):
                r(g, xx, y, 4, 4, 'glass1')
    _oficina(g, *BAIRRO_X['oficina'][:1], 103, random.Random(1), 'OFICINA' in names)
    _mercearia(g, BAIRRO_X['mercearia'][0], BAIRRO_X['mercearia'][1] - BAIRRO_X['mercearia'][0], random.Random(2), 'MERCEARIA' in names, year, shop_empty)
    # the gap between shop and school: tree, lamp, low wall; the bus shelter in 2025
    r(g, 227, 96, 109, 22, 'plaster2'); r(g, 227, 96, 109, 2, 'plaster3')
    tree(g, 298, 118, 54, 9)                                                                       # canopy x 268-330, clear of every sign board
    _lamp(g, 240)
    if year >= 2025:
        _bus_shelter(g, 232)
    else:
        r(g, 250, 104, 22, 14, 'wood1'); r(g, 250, 104, 22, 2, 'wood3')                              # a bench against the wall
    _school(g, BAIRRO_X['escola'][0], 100, 36, 118, 'ESCOLA' in names, ESCOLA_BAIRRO_SIGN[1], random.Random(3))
    _casa_facade(g, BAIRRO_X['casa'][0], light='day')
    tree(g, 606, 118, 60, 5)
    # ground: sidewalk with joints, kerb, road (below row 149 it is only the caption band's backdrop)
    r(g, 0, 118, w, 28, 'plaster2'); r(g, 0, 118, w, 1, 'plaster0')
    for xx in range(0, w, 14):
        r(g, xx, 119, 1, 27, 'plaster1')
    for yy in (126, 134, 142):
        r(g, 0, yy, w, 1, 'plaster1')
    _noise(g, rng, 120, 0, 120, w, 146, ['plaster3', 'plaster1'], 4)
    r(g, 0, 146, w, 3, 'plaster3'); r(g, 0, 146, w, 1, 'ivory'); r(g, 0, 149, w, 31, 'steel0')
    for xx in range(0, w, 38):
        r(g, xx, 163, 17, 2, 'plaster3')
    if shutter == 'down':
        sq, sx, sy = bairro_shutter(1.0)
        g.paste(sq, sx, sy)
    elif shutter == 'down_wide':
        sq, sx, sy = bairro_shutter(1.0, wide=True)
        g.paste(sq, sx, sy)
    if time == 'golden':
        skycells = [xy for xy, c in g.cells.items() if xy[1] < 40 and c in skycols]
        _grade(g, (1.08, .94, .78), (10, 0, -6))
        golden = Geometry(); sky_gradient(golden, '#5f87ad', '#f2b884', 0, 40, 6)
        for xy in skycells:
            g.cells[xy] = golden.cells.get(xy, g.cells[xy])
        for (x0, x1) in ((0, 103), (108, 227), (336, 436), (446, 576)):                            # long shadows on the sidewalk, toward the left
            poly(g, [(x0, 118), (x1, 118), (x1 - 52, 146), (x0 - 52, 146)], 'plaster1')
        poly(g, [(236, 118), (240, 118), (196, 146), (190, 146)], 'plaster1')
    return g


SHOP_SHUTTER_WIDE = (116, 64, 224, 118)   # doorway AND display window (12c: the whole shop front is shuttered)


def bairro_shutter(frac=1.0, wide=False):
    """Roll-up shutter over the shop doorway lowered to `frac` (0..1) of its height. Returns (Geometry, x, y) to paste/place over
    a `bairro(shutter='up')` background (the caller steps `frac` in time: it is the woman's hand that moves it)."""
    x0, y0, x1, y1 = SHOP_SHUTTER_WIDE if wide else SHOP_SHUTTER_RECT
    h = max(0, round((y1 - y0) * frac))
    g = Geometry()
    if h:
        r(g, 0, 0, x1 - x0, h, 'steel1')
        for yy in range(0, h, 3):
            r(g, 0, yy, x1 - x0, 1, 'steel2' if yy % 6 == 0 else 'steel0')
        r(g, 0, h - 2, x1 - x0, 2, 'steel0'); r(g, (x1 - x0) // 2 - 4, h - 4, 8, 2, 'steel3')
    return g, x0, y0


# --------------------------------------------------------------------------------------------- time-of-day helpers
SKIES = {'day': ('#6f9ab4', '#c9dac6'), 'morning': ('#7fa6c0', '#f0cfa0'), 'golden': ('#5f87ad', '#f2b884'),
         'dusk': ('#43577e', '#e69a6c'), 'night': ('#0b1428', '#28395c')}


def _sky(g, time, y1, bands=6):
    """Draw the sky gradient of `time` on rows 0..y1; returns the cells (x, y) that are sky, so grading can leave them alone."""
    top, bot = SKIES[time]
    q = Geometry(); sky_gradient(q, top, bot, 0, y1, bands)
    g.cells.update({xy: c for xy, c in q.cells.items()})
    return dict(q.cells)


def _grade_keep_sky(g, time, sky):
    """Grade everything except the cells in `sky` (which keep the sky gradient of the time of day)."""
    gr = GRADES.get(time)
    if gr:
        keep = {xy: g.cells[xy] for xy in sky if g.cells.get(xy) == sky[xy]}
        _grade(g, *gr)
        g.cells.update(keep)
    return g


def _stars(g, rng, n=26, y1=34):
    for _ in range(n):
        r(g, rng.randrange(0, 320), rng.randrange(1, y1), 1, 1, rng.choice(['ivory', 'steel3', 'cream']))


# ---------------------------------------------------------------------------------------------- recurring house, exterior
HOUSE_EXT_SHAFT_BOXES = [(CASA_X_EXT + 62, 119, CASA_X_EXT + 102, 128), (CASA_X_EXT + 56, 128, CASA_X_EXT + 108, 137), (CASA_X_EXT + 48, 137, CASA_X_EXT + 114, 146)]
HOUSE_STREET_LAMP_X = 38


def house_ext_shaft():
    """The warm light shaft that falls from the open door onto the step and the pavement (32m); draw with ctx.G(..., opacity=.3).
    Dust specks go only inside HOUSE_EXT_SHAFT_BOXES."""
    g = Geometry(); fx = CASA_X_EXT
    poly(g, [(fx + 62, 118), (fx + 102, 118), (fx + 118, 146), (fx + 44, 146)], 'v3_shaft')
    return g


def house_window_overlay(state):
    """Curtain of the house window as an overlay (25a: the woman draws it): state 'open' | 'half' | 'closed' | 'dim' (window light
    dimmed behind the closed curtain). Placed at (0, 0) over `house_exterior(...)` (same 320x180 canvas)."""
    g = Geometry(); x0, y0, x1, y1 = casa_rects(CASA_X_EXT)['window']
    if state == 'dim':
        r(g, x0, y0, x1 - x0, y1 - y0, 'blue1'); r(g, x0, y0, x1 - x0, 1, 'blue2')
        for k in range(x0 + 1, x1, 3):
            r(g, k, y0 + 1, 1, y1 - y0 - 1, 'blue0')
        r(g, x0, y1 - 1, x1 - x0, 1, 'ochre'); r(g, x0, y0, 1, y1 - y0, 'ochre'); r(g, x1 - 1, y0, 1, y1 - y0, 'ochre')   # warm light leaking round the edge
        return g
    q = Geometry(); _casa_facade(q, CASA_X_EXT, 'night', curtain=state, window_lit=True)
    for (x, y), c in q.cells.items():
        if x0 - 3 <= x < x1 + 3 and y0 - 3 <= y < y1 + 5:
            g.cells[x, y] = c
    return g


def house_exterior(time='day', door='closed', curtain='open', window_lit=None, street_lamp=None):
    """The recurring house seen from the street (the same facade as the BAIRRO's CASA), 320x180, facade at x 78-208, door x 138-182.
    time: 'morning' (09h) | 'day' (32l, 32m) | 'dusk' (30g2) | 'night' (25a) ; door: 'closed' | 'open' (warm lit room behind; family
    slots HOUSE_DOOR_SLOTS) ; curtain: 'open' | 'half' | 'closed' ; window_lit: default lit at dusk/night ;
    street_lamp: default on at night (lamp post at x 38, glow) . Soles of figures: step y 118-121, pavement down to 145."""
    assert time in ('morning', 'day', 'dusk', 'night') and door in ('closed', 'open') and curtain in ('open', 'half', 'closed')
    g = Geometry(); rng = random.Random(1946); fx = CASA_X_EXT
    lamp = (time == 'night') if street_lamp is None else street_lamp
    sky = _sky(g, time, 70)
    r(g, 0, 70, 320, 80, 'blue3')
    rr = random.Random(77)
    for x in range(-10, 320, 46):                                                                    # far blocks
        h = rr.randrange(14, 34)
        r(g, x, 76 - h, 40, h + 50, 'steel2'); r(g, x, 76 - h, 40, 2, 'steel3')
        for y in range(80 - h, 100, 9):
            for xx in range(x + 5, x + 36, 9):
                r(g, xx, y, 4, 4, 'glass1')
    # neighbours: left a plain house with a gate, right a house with a green door
    r(g, 0, 52, fx - 4, 66, 'plaster2'); r(g, 0, 48, fx - 2, 5, 'clay'); r(g, 0, 98, fx - 4, 20, 'plaster1')
    r(g, 8, 70, 26, 24, 'wood0'); r(g, 10, 72, 22, 20, 'glass0'); r(g, 20, 72, 1, 20, 'wood0')
    r(g, 44, 74, 22, 44, 'wood1'); r(g, 46, 76, 18, 40, 'wood0')
    x2 = fx + CASA_W + 4
    r(g, x2, 56, 320 - x2, 62, 'sand'); r(g, x2, 50, 320 - x2, 6, 'red0'); r(g, x2, 100, 320 - x2, 18, 'plaster3')
    r(g, x2 + 14, 72, 24, 46, 'metal1'); r(g, x2 + 16, 74, 20, 42, 'metal0'); r(g, x2 + 52, 70, 26, 22, 'wood0'); r(g, x2 + 54, 72, 22, 18, 'glass0')
    _casa_facade(g, fx, light=time, door=door, curtain=curtain, window_lit=window_lit, lamp_on=False)
    _lamp(g, HOUSE_STREET_LAMP_X)
    tree(g, 306, 118, 62, 7)
    r(g, 0, 118, 320, 28, 'plaster2'); r(g, 0, 118, 320, 1, 'plaster0')
    for xx in range(0, 320, 14):
        r(g, xx, 119, 1, 27, 'plaster1')
    for yy in (126, 134, 142):
        r(g, 0, yy, 320, 1, 'plaster1')
    _noise(g, rng, 60, 0, 120, 320, 146, ['plaster3', 'plaster1'], 4)
    r(g, 0, 146, 320, 3, 'plaster3'); r(g, 0, 146, 320, 1, 'ivory'); r(g, 0, 149, 320, 31, 'steel0')
    for xx in range(0, 320, 38):
        r(g, xx, 163, 17, 2, 'plaster3')
    _grade_keep_sky(g, time, sky)
    if time == 'night':
        _stars(g, random.Random(5))
    lit = (time in ('dusk', 'night')) if window_lit is None else window_lit
    rc = casa_rects(fx)
    if lit:                                                                                           # windows stay lit after the grade
        q = Geometry(); _casa_facade(q, fx, 'night', curtain=curtain, window_lit=True)
        x0, y0, x1, y1 = rc['window']
        for (x, y), c in q.cells.items():
            if x0 - 3 <= x < x1 + 3 and y0 - 3 <= y < y1 + 5:
                g.cells[x, y] = c
    if door == 'open':
        x0, y0, x1, y1 = rc['door']
        q = Geometry(); _casa_open_interior(q, x0, y0, x1, y1, time)
        g.cells.update(q.cells)
        r(g, x0 - 1, y0, 3, y1 - y0, 'blue1'); r(g, x1 - 1, y0, 2, y1 - y0, 'blue1')
    if lamp:
        ellipse(g, HOUSE_STREET_LAMP_X + 1, 63, 7, 5, 'cream'); r(g, HOUSE_STREET_LAMP_X - 2, 64, 6, 2, 'gold'); r(g, HOUSE_STREET_LAMP_X - 3, 62, 8, 2, 'ivory')
        for k in range(0, 14, 2):
            r(g, HOUSE_STREET_LAMP_X - 12 + k, 128 + (k % 4), 1, 1, 'plaster3')
        r(g, HOUSE_STREET_LAMP_X - 14, 124, 30, 1, 'floor3'); r(g, HOUSE_STREET_LAMP_X - 10, 130, 22, 1, 'floor3'); r(g, HOUSE_STREET_LAMP_X - 7, 137, 16, 1, 'floor3')
    return g


def _door_slots(fx=CASA_X_EXT):
    x0, y0, x1, y1 = casa_rects(fx)['door']
    return dict(threshold_standing=(x0 + 8, 119), table_seat_left=(x0 + 8, 92), table_seat_right=(x0 + 24, 92), inside_walk_y=100)


HOUSE_DOOR_SLOTS = _door_slots()        # where figures may stand (sprite origin x, sole/seat y) in the open doorway (sprites are ~19 px wide, 48 high)


# ------------------------------------------------------------------------------------------------------------ SCHOOL street
ESCOLA_STREET_SIGN = ('ESCOLA', (130, 24, 200, 34))
SCHOOL_DOOR = (147, 56, 183, 118)       # 10f / 11f1 wide view: door frame (x0, y0, x1, y1)


def school_street(angle='wide', time='day', signs=True, door='closed'):
    """SCHOOL-WALK (10f) and SCHOOL-WALK-2 (11f1): the street in front of the modest school (the BAIRRO's ESCOLA, same drawing).
    angle: 'wide' (10f: whole facade centred at x 165, sign ESCOLA at (130,24,200,34)) | 'door' (11f1, other angle: the door seen
    nearer and off-centre from the right, mid-shot, NO sign: pass signs=False) ; door: 'closed' | 'open' (dark classroom glimpsed);
    time: 'day' | 'morning'. Sidewalk y 118-146."""
    assert angle in ('wide', 'door') and time in ('day', 'morning') and door in ('closed', 'open')
    g = Geometry(); rng = random.Random(1010)
    sky = _sky(g, time, 60)
    r(g, 0, 60, 320, 90, 'blue3')
    rr = random.Random(61)
    for x in range(-10, 320, 46):
        h = rr.randrange(16, 34)
        r(g, x, 70 - h, 40, h + 50, 'steel2'); r(g, x, 70 - h, 40, 2, 'steel3')
        for y in range(74 - h, 100, 9):
            for xx in range(x + 5, x + 36, 9):
                r(g, xx, y, 4, 4, 'glass1')
    if angle == 'wide':
        _school(g, 90, 150, 20, 118, signs, ESCOLA_STREET_SIGN[1], random.Random(3), big=True)
        r(g, 0, 70, 90, 48, 'plaster2'); r(g, 0, 66, 90, 5, 'clay'); r(g, 240, 74, 80, 44, 'sand'); r(g, 240, 68, 80, 6, 'red0')
        r(g, 6, 82, 22, 22, 'wood0'); r(g, 8, 84, 18, 18, 'glass0'); r(g, 270, 82, 24, 22, 'wood0'); r(g, 272, 84, 20, 18, 'glass0')
        tree(g, 40, 118, 60, 3); _lamp(g, 266)
        dx0 = 165
    else:
        _school(g, 20, 230, 14, 118, False, ESCOLA_STREET_SIGN[1], random.Random(3), big=True)      # nearer: the same wall, door off-centre
        r(g, 250, 60, 70, 58, 'sand'); r(g, 250, 56, 70, 5, 'red0'); r(g, 262, 74, 24, 22, 'wood0'); r(g, 264, 76, 20, 18, 'glass0')
        r(g, 0, 56, 20, 62, 'plaster2'); _lamp(g, 12)
        dx0 = 135
    if door == 'open':
        q = Geometry(); r(q, dx0 - 14, 56, 29, 62, 'black')
        r(q, dx0 - 14, 62, 29, 56, 'wood0'); r(q, dx0 - 14, 100, 29, 18, 'floor0'); r(q, dx0 - 8, 72, 16, 18, 'blue0')   # the dim classroom, a board in it
        r(q, dx0 - 16, 56, 3, 62, 'wood1'); r(q, dx0 + 14, 56, 2, 62, 'wood1')                                              # the leaves, swung inward, edge-on
        g.paste(q, 0, 0)
    r(g, 0, 118, 320, 28, 'plaster2'); r(g, 0, 118, 320, 1, 'plaster0')
    for xx in range(0, 320, 14):
        r(g, xx, 119, 1, 27, 'plaster1')
    for yy in (126, 134, 142):
        r(g, 0, yy, 320, 1, 'plaster1')
    _noise(g, rng, 60, 0, 120, 320, 146, ['plaster3', 'plaster1'], 4)
    r(g, 0, 146, 320, 3, 'plaster3'); r(g, 0, 146, 320, 1, 'ivory'); r(g, 0, 149, 320, 31, 'steel0')
    for xx in range(0, 320, 38):
        r(g, xx, 163, 17, 2, 'plaster3')
    _grade_keep_sky(g, time, sky)
    return g


# ------------------------------------------------------------------------------------------------ TABLE and recurring house, interior
TABLE_POS = (117, 100)                                    # table top-left in the frontal framing of 02a / 10a / 32d2
TABLE_STEAM = (TABLE_POS[0] + 72, TABLE_POS[1] - 14)      # rim of the pot: ctx.steam(s, *TABLE_STEAM, a, b)
TABLE_SHAFT_BOXES = [(62, 60, 96, 76), (82, 76, 118, 92), (102, 92, 140, 108), (122, 108, 156, 124)]   # dust only inside these
TABLE_SEATS = [(118, 77), (134, 77), (190, 77)]           # sprite origin (x, y) of the seated figures (cropped torsos, crop=24, as 02a)
TABLE_STANDING = (152, 62)                                # the standing mother behind the table


def table_shaft():
    """The light shaft of the frontal table framing (window at the left), same polygon as 02a. Draw with opacity .22."""
    g = Geometry(); poly(g, [(58, 36), (62, 70), (150, 126), (172, 126)], 'v3_shaft')
    return g


def _wall_modest(g, light='day', top=0, rng=None):
    r(g, 0, top, 320, 180 - top, 'plaster3')
    r(g, 0, 0, 320, 6, 'plaster2'); r(g, 0, 6, 320, 1, 'plaster1')                                   # ceiling edge
    r(g, 0, 78, 320, 40, 'glass1'); r(g, 0, 78, 320, 2, 'ivory'); r(g, 0, 80, 320, 1, 'glass2')     # painted dado
    r(g, 0, 116, 320, 2, 'plaster0')                                                                 # skirting
    rng = rng or random.Random(14)
    for _ in range(50):
        r(g, rng.randrange(320), rng.randrange(8, 76), rng.randrange(1, 3), 1, 'plaster2')


def _floor_modest(g, y0=118):
    r(g, 0, y0, 320, 180 - y0, 'brick'); r(g, 0, y0, 320, 1, 'floor0')
    rng = random.Random(15)
    for yy in range(y0 + 8, 180, 9):
        r(g, 0, yy, 320, 1, 'clay' if (yy // 9) % 2 else 'floor0')
    for xx in range(0, 320, 24):
        for yy in range(y0, 180, 18):
            r(g, xx + (yy // 18 % 2) * 12, yy, 1, 9, 'floor0')
    _noise(g, rng, 60, 0, y0, 320, 180, ['clay', 'red0'], 4)


def _window_modest(g, x, y, light, w=38, h=44, curtain='open'):
    """The recurring house's window (frame blue, mullion, blue curtains). light: 'day' | 'morning' | 'dusk' | 'night'."""
    gl = {'day': ('glass1', 'glass2'), 'morning': ('cream', 'ivory'), 'dusk': ('red2', 'gold'), 'night': ('blue0', 'blue1')}[light]
    r(g, x, y, w, h, 'blue1'); r(g, x + 3, y + 3, w - 6, h - 6, gl[0]); r(g, x + 3, y + 3, w - 6, 12, gl[1])
    r(g, x + w // 2 - 1, y + 3, 2, h - 6, 'blue1'); r(g, x + 3, y + h // 2 + 3, w - 6, 2, 'blue1')
    cw = {'open': 5, 'half': 12, 'closed': (w - 6) // 2}[curtain]
    for cx in (x + 3, x + w - 3 - cw):
        r(g, cx, y + 3, cw, h - 6, 'blue2'); r(g, cx, y + 3, cw, 1, 'blue3')
        for k in range(cx + 1, cx + cw, 3):
            r(g, k, y + 4, 1, h - 7, 'blue1')
    r(g, x - 3, y + h, w + 6, 3, 'ivory'); r(g, x - 3, y + h + 3, w + 6, 1, 'plaster0')


def _tv(g, x, y, year, on=False):
    """The TV on its shelf; (x, y) is the shelf board's top-left (board 44 wide). 2010: small CRT with its aerial attached to the set;
    2022/2025: flat screen on the wall, no aerial. Returns the screen rectangle."""
    r(g, x, y, 44, 3, 'wood2'); r(g, x, y, 44, 1, 'wood3'); r(g, x + 2, y + 3, 3, 8, 'wood1'); r(g, x + 39, y + 3, 3, 8, 'wood1')
    if year <= 2010:
        r(g, x + 4, y - 19, 28, 19, 'wood0'); r(g, x + 6, y - 17, 18, 15, 'blue0' if not on else 'blue2'); r(g, x + 26, y - 14, 4, 8, 'steel1')
        r(g, x + 6, y - 17, 18, 1, 'steel1')
        line(g, (x + 16, y - 19), (x + 8, y - 31), .5, 'steel2'); line(g, (x + 16, y - 19), (x + 26, y - 30), .5, 'steel2')       # the aerial, on the set
        rect = (x + 6, y - 17, x + 24, y - 2)
    else:
        r(g, x + 2, y - 22, 40, 21, 'black'); r(g, x + 3, y - 21, 38, 19, 'blue0' if not on else 'blue2'); r(g, x + 3, y - 21, 38, 1, 'steel0')
        r(g, x + 18, y - 1, 8, 1, 'steel0')
        rect = (x + 3, y - 21, x + 41, y - 2)
    if year <= 2010:
        ellipse(g, x + 36, y - 3, 3, 3, 'clay')                                                       # a clay jar beside the set
    return rect


def _photos(g, year, positions):
    """Framed photographs on the wall; more of them each era (the family grows): 2010 -> 1, 2022 -> 2, 2025 -> 3."""
    n = {2010: 1, 2022: 2, 2025: 3}[year]
    for k, (x, y) in enumerate(positions[:n]):
        r(g, x, y, 14, 17, 'wood1'); r(g, x + 1, y + 1, 12, 15, 'ivory'); r(g, x + 2, y + 2, 10, 13, 'blue2' if k % 2 == 0 else 'sand')
        ellipse(g, x + 7, y + 7, 2, 3, 'skin1'); r(g, x + 4, y + 11, 6, 4, 'red1' if k % 2 else 'blue0')


def _counter(g, x, y, year, w=58):
    """Kitchen counter with a two-burner stove and a tiled splash (y is the counter top). 2022+: a fridge stands at its left."""
    r(g, x, y - 26, w, 20, 'blue2'); r(g, x, y - 26, w, 1, 'blue3')
    for xx in range(x, x + w, 6):
        r(g, xx, y - 26, 1, 20, 'blue3')
    for yy in range(y - 26, y - 6, 6):
        r(g, x, yy, w, 1, 'blue3')
    r(g, x - 1, y - 6, w + 2, 4, 'steel1'); r(g, x - 1, y - 6, w + 2, 1, 'steel3')
    r(g, x, y - 2, w, 38, 'wood1'); r(g, x, y - 2, w, 1, 'wood3')
    r(g, x + 2, y + 2, 24, 30, 'wood2'); r(g, x + 2, y + 2, 24, 1, 'wood3'); r(g, x + 22, y + 14, 2, 4, 'gold')
    r(g, x + 29, y + 2, 25, 30, 'steel2'); r(g, x + 31, y + 5, 21, 3, 'steel1'); r(g, x + 31, y + 10, 21, 20, 'black'); r(g, x + 33, y + 12, 17, 6, 'steel0')
    r(g, x + 32, y - 9, 22, 3, 'black'); ellipse(g, x + 37, y - 8, 4, 1, 'steel0'); ellipse(g, x + 48, y - 8, 4, 1, 'steel0')
    r(g, x + 5, y - 16, 12, 10, 'ivory'); r(g, x + 5, y - 16, 12, 2, 'cream'); r(g, x + 7, y - 20, 8, 4, 'ivory')         # a flour tin and a cloth
    if year >= 2022:
        r(g, x - 26, y - 44, 24, 78, 'ivory'); r(g, x - 26, y - 44, 24, 1, 'plaster3'); r(g, x - 26, y - 14, 24, 2, 'steel2')
        r(g, x - 6, y - 36, 2, 12, 'steel1'); r(g, x - 6, y - 8, 2, 12, 'steel1')


def _chair_front(g, x, y, old=False):
    """Chair seen from the front/back: backrest from y, seat 22 below, legs down to y+40. 18 wide. `old` = the old chair
    (cream patched cushion, one mended leg): it stays in the same place in every scene."""
    for px in (x, x + 16):
        r(g, px, y, 2, 40, 'wood1'); r(g, px, y, 1, 40, 'wood2')
    for k in (2, 9, 16):
        r(g, x, y + k, 18, 3, 'wood2'); r(g, x, y + k, 18, 1, 'wood3')
    r(g, x - 1, y + 22, 20, 4, 'wood0'); r(g, x - 1, y + 22, 20, 1, 'wood2')
    if old:
        r(g, x, y + 20, 18, 3, 'red1'); r(g, x + 3, y + 20, 5, 3, 'cream'); r(g, x + 13, y + 33, 4, 2, 'steel2')


def _chair_side(g, x, y, face=1, old=False):
    c = Geometry(); c.paste(chair(), 0, 0)
    if face < 0:
        c = flip(c, 20)
    if old:
        r(c, 3 if face > 0 else 0, 19, 17, 2, 'red1')
    g.paste(c, x, y)


def _table_top_front(g, x, y, cloth=False):
    """Broadside table (80 wide, top y .. y+7, legs to y+32), the 2.0.0 table drawing; with an optional cloth."""
    q = _table_old(); q.cells = {xy: c for xy, c in q.cells.items() if xy[1] < 25}               # top 7 rows + legs to 25: top 24 rows above its foot line
    g.paste(q, x, y)
    if cloth:
        r(g, x - 2, y + 1, 84, 6, 'plaster3'); r(g, x - 2, y + 1, 84, 1, 'ivory')
        for k in range(x - 2, x + 82, 6):
            r(g, k, y + 3, 3, 3, 'blue3')


from .ctx import table as _table_old                                                           # noqa: E402


def _shaft_geom(wx1, wy0, wy1, fx0, fx1, floor=126):
    """Light shaft falling from a window whose right edge is x=wx1 (rows wy0..wy1) to the floor between x=fx0 and fx1.
    Returns (Geometry polygon, boxes) where boxes tile the inside of the polygon (dust only goes there)."""
    top, bot = (wx1, wy0 + 6), (wx1, wy1 - 4)
    pts = [top, bot, (fx1, floor), (fx0, floor)]
    g = Geometry(); poly(g, pts, 'v3_shaft')
    def left(y):  return top[0] + (fx0 - top[0]) * (y - top[1]) / (floor - top[1])
    def right(y): return bot[0] + (fx1 - bot[0]) * (y - bot[1]) / (floor - bot[1]) if y >= bot[1] else bot[0]
    boxes = []
    ys = [wy0 + 10 + k * (floor - wy0 - 10) // 4 for k in range(5)]
    for ya, yb in zip(ys, ys[1:]):
        xl = int(max(left(ya), left(yb))) + 2; xr = int(min(right(ya), right(yb))) - 2
        if xr - xl >= 6:
            boxes.append((xl, ya, xr, yb))
    return g, boxes


HOUSE_VIEWS = ('front', 'k1', 'k2', 'k3', 'k4', 'k5', 'k6', 'k7', 'k8', 'k9', 'door', 'window')
HOUSE_YEARS = (2010, 2022, 2025)
_HOUSE_GRADE = {'day': None, 'morning': None, 'dusk': ((.96, .84, .76), (6, -2, 0)), 'night': ((.80, .74, .80), (4, 0, 8))}


def house_interior(view='front', light='day', year=2010, empty_chair=False, cloth=False):
    """The recurring house, interior, the background of one composition (the table and other foreground pieces are NOT in it:
    `house_interior_pieces` returns them so figures can sit behind). All views share: sage dado over cream wall, burnt-cement floor,
    the blue-curtained window, the kitchen counter with stove, the TV shelf with its aerial, the old chair (cream cushion).
    view: 'front' (10a, 32d2: frontal, the same camera as 02a) | 'k1' (09e) | 'k2' (09f) | 'k3' (09g top-down) | 'k4' (25d) |
    'k5' (30a) | 'k6' (30e) | 'k7' (10b) | 'k8' (10e) | 'k9' (30g3) | 'door' (25g) | 'window' (10h, seen from OUTSIDE).
    light: 'day' | 'morning' | 'dusk' | 'night' ; year: 2010 | 2022 | 2025 (TV, photographs, fridge) ;
    empty_chair: the old chair is drawn pushed in with the plate untouched (25d); cloth: table cloth (2022+)."""
    assert view in HOUSE_VIEWS and light in _HOUSE_GRADE and year in HOUSE_YEARS
    g = Geometry(); rng = random.Random(1947)
    fn = globals()['_view_' + view]
    fn(g, light, year, empty_chair, rng)
    gr = _HOUSE_GRADE[light]
    if gr and view != 'window':
        _grade(g, *gr)
    return g


def _wall_light(g, light, x, y, w=38, h=44, curtain='open'):
    _window_modest(g, x, y, light, w, h, curtain)


def _view_front(g, light, year, empty, rng):
    _wall_modest(g, light, rng=rng); _floor_modest(g)
    _wall_light(g, light, 22, 30)
    r(g, 18, 74, 46, 3, 'plaster0'); r(g, 18, 74, 46, 1, 'cream')
    _tv(g, 262, 74, year)
    ellipse(g, 276, 67, 4, 4, 'clay'); ellipse(g, 288, 68, 3, 4, 'ochre')
    _photos(g, year, [(206, 38), (226, 38), (246, 38)])
    # far-side chairs behind the seated figures (the figures hide most of them)
    for cx in (TABLE_SEATS[0][0] - 2, TABLE_SEATS[1][0] - 2, TABLE_SEATS[2][0] - 2):
        _chair_front(g, cx, 62, old=(cx == TABLE_SEATS[2][0] - 2))
    r(g, 120, 126, 80, 1, 'floor0')


def house_interior_pieces(view='front', year=2010, light='day', empty_chair=False, cloth=False):
    """Foreground pieces of a view as a list of (name, Geometry, x, y) in draw order (draw them after the figures), plus anchors
    in `HOUSE_ANCHORS[view]`. Shaft polygons come as ('shaft', Geometry, 0, 0): draw with opacity .22."""
    fn = globals()['_pieces_' + view]
    return fn(year, light, empty_chair, cloth)


HOUSE_ANCHORS = {}


def _bowl(full=False, empty=False):
    b = Geometry(); ellipse(b, 4, 2, 5, 2, 'cream'); r(b, 0, 2, 9, 2, 'ivory'); r(b, 0, 3, 9, 1, 'blue1')
    ellipse(b, 4, 1, 3, 1, 'wood0' if empty else ('cream' if full else 'ochre'))
    return b


def _pot_modest():
    p = Geometry(); r(p, 0, 3, 14, 9, 'ivory'); r(p, 0, 3, 14, 1, 'cream'); r(p, 0, 9, 14, 3, 'blue1'); r(p, -2, 5, 3, 2, 'steel1'); r(p, 13, 5, 3, 2, 'steel1')
    ellipse(p, 7, 3, 7, 1, 'steel0')
    return p


def _pieces_front(year, light, empty, cloth):
    tx, ty = TABLE_POS
    out = []
    sh = table_shaft() if light in ('day', 'morning', 'dusk') else None
    if sh:
        out.append(('shaft', sh, 0, 0))
    t = Geometry(); _table_top_front(t, 0, 0, cloth)
    out.append(('table', t, tx, ty))
    for i, bx in enumerate((tx + 6, tx + 24, tx + 44)):
        out.append((f'bowl{i}', _bowl(full=False), bx, ty - 3))
    out.append(('bowl_full', _bowl(full=True), tx + 24, ty - 3))
    out.append(('pot', _pot_modest(), tx + 66, ty - 12))
    jug = Geometry(); r(jug, 0, 2, 5, 8, 'glass2'); r(jug, 0, 2, 5, 1, 'ivory'); r(jug, 5, 4, 2, 3, 'glass1')
    out.append(('jug', jug, tx + 52, ty - 10))
    return out


HOUSE_ANCHORS['front'] = dict(seats=TABLE_SEATS, standing=TABLE_STANDING, steam=TABLE_STEAM, shaft_boxes=TABLE_SHAFT_BOXES, table=TABLE_POS)


def table_room(era='modest', light='day', year=2010):
    """TABLE: the frontal table room. era 'rancho' = the 02a room (mud brick, plank floor; identical to scene_02.rancho_bg) ;
    'modest' = the recurring house in its frontal framing (10a, 32d2): same table position, window, shaft and pot place."""
    assert era in ('rancho', 'modest')
    if era == 'modest':
        return house_interior('front', light=light, year=year)
    g = Geometry(); rng = random.Random(1952)
    r(g, 0, 0, 320, 180, 'plaster1'); r(g, 0, 0, 320, 18, 'umber')
    for yy in range(18, 118, 6):
        for xx in range(-8 + (yy // 6 % 2) * 9, 320, 18):
            r(g, xx, yy, 16, 5, rng.choice(['brick', 'brick', 'clay', 'brown']))
            if rng.random() < .4:
                r(g, xx + 1, yy, 14, 1, 'ochre')
    for x in (60, 250):
        r(g, x, 0, 4, 118, 'wood0'); r(g, x, 0, 1, 118, 'wood2')
    r(g, 0, 118, 320, 62, 'floor1'); r(g, 0, 118, 320, 1, 'floor0')
    for yy in (126, 138, 152, 168):
        r(g, 0, yy, 320, 1, 'floor0')
    for i in range(80):
        r(g, rng.randrange(320), rng.randrange(120, 178), rng.choice([2, 3, 4]), 1, rng.choice(['floor0', 'floor2']))
    r(g, 22, 30, 38, 44, 'wood0'); r(g, 25, 33, 32, 38, 'glass1'); r(g, 25, 33, 32, 12, 'glass2'); r(g, 40, 33, 2, 38, 'wood0'); r(g, 25, 50, 32, 2, 'wood0')
    r(g, 18, 74, 46, 3, 'plaster0'); r(g, 18, 74, 46, 1, 'cream')
    r(g, 262, 54, 44, 3, 'wood1'); ellipse(g, 272, 50, 4, 4, 'clay'); ellipse(g, 284, 50, 3, 4, 'ochre'); ellipse(g, 296, 51, 4, 3, 'metal2')
    return g


def table_pieces(era='modest', bowls=3, pot=True, bread=False, cloth=False):
    """Pieces of the frontal table as a list of (name, Geometry, x, y) in draw order, to be drawn after the seated figures:
    'table', 'bowl0..', 'pot' (+ 'cloth', 'bread_whole', 'bread0..3' for era 'rancho'). Same positions in both eras so 10a is
    the callback of 02a. Steam: ctx.steam(s, *TABLE_STEAM, a, b)."""
    tx, ty = TABLE_POS
    out = []
    t = Geometry(); _table_top_front(t, 0, 0, cloth and era == 'modest')
    out.append(('table', t, tx, ty))
    xs = (tx + 6, tx + 24, tx + 44, tx + 62)[:bowls]
    for i, bx in enumerate(xs):
        b = Geometry(); ellipse(b, 4, 2, 5, 2, 'clay'); r(b, 0, 2, 9, 2, 'brown'); ellipse(b, 4, 1, 3, 1, 'cream' if i < 3 else 'wood0')
        if era == 'modest':
            b = _bowl()
        out.append((f'bowl{i}', b, bx, ty - 3))
    if era == 'rancho' and bread:
        c = Geometry(); r(c, 0, 0, 26, 3, 'plaster3'); r(c, 0, 0, 26, 1, 'ivory'); out.append(('cloth', c, tx + 30, ty - 1))
        w = Geometry(); ellipse(w, 8, 1, 8, 2, 'ochre'); r(w, 2, 0, 12, 1, 'sand'); out.append(('bread_whole', w, tx + 34, ty - 4))
        for k in range(4):
            pc = Geometry(); ellipse(pc, 2, 1, 2, 1, 'ochre'); r(pc, 1, 0, 3, 1, 'sand'); out.append((f'bread{k}', pc, tx + 33 + k * 5, ty - 3))
    if pot:
        if era == 'rancho':
            p = Geometry(); r(p, 0, 3, 14, 9, 'steel0'); r(p, 0, 3, 14, 1, 'steel1'); r(p, -2, 5, 3, 2, 'black'); r(p, 13, 5, 3, 2, 'black'); ellipse(p, 7, 3, 7, 1, 'black')
        else:
            p = _pot_modest()
        out.append(('pot', p, tx + 66, ty - 12))
    return out


# ------------------------------------------------ remaining interior views and their pieces
def _setup(g, light, year, rng, window=(22, 30), curtain='open', tv=True, photos=None):
    _wall_modest(g, light, rng=rng); _floor_modest(g)
    if window:
        _wall_light(g, light, window[0], window[1], curtain=curtain)
    if photos:
        _photos(g, year, photos)


def _tbl_pieces(tx, ty, cloth=False):
    t = Geometry(); _table_top_front(t, 0, 0, cloth)
    return [('table', t, tx, ty)]


def _plate(rx=6, ry=2, food=True, untouched=False):
    p = Geometry(); ellipse(p, rx, ry + 1, rx, ry, 'steel2'); ellipse(p, rx, ry, rx, ry, 'ivory'); ellipse(p, rx, ry, rx - 2, max(1, ry - 1), 'cream')
    if food:
        ellipse(p, rx - 2, ry, max(1, rx // 3), max(1, ry - 1), 'ochre'); r(p, rx + 1, ry - 1, 3, 1, 'wood1')
    if untouched:
        r(p, -3, ry, 2, 1, 'steel2'); r(p, rx * 2 + 2, ry, 2, 1, 'steel2')                             # fork and knife at the plate
    return p


def _view_k1(g, light, year, empty, rng):
    _setup(g, light, year, rng, window=(196, 54), photos=[(130, 22), (150, 22), (170, 22)])
    _counter(g, 36, 98, year)
    r(g, 214, 98, 40, 22, 'wood1'); r(g, 214, 98, 40, 2, 'wood3'); r(g, 218, 104, 32, 10, 'wood2'); r(g, 231, 108, 6, 2, 'gold'); r(g, 214, 120, 3, 12, 'wood0'); r(g, 251, 120, 3, 12, 'wood0')
    _tv(g, 264, 82, year)
    _chair_side(g, 96, 96, 1); _chair_side(g, 186, 96, -1, old=True)


def _pieces_k1(year, light, empty, cloth):
    t = Geometry(); poly(t, [(0, 0), (44, 0), (48, 6), (-4, 6)], 'wood2'); r(t, -4, 6, 52, 3, 'wood0'); r(t, -4, 6, 52, 1, 'sand')
    r(t, 1, 9, 4, 24, 'wood1'); r(t, 39, 9, 4, 24, 'wood1'); r(t, 1, 9, 1, 24, 'wood3')
    bag = Geometry(); r(bag, 0, 4, 14, 14, 'sand'); r(bag, 0, 4, 14, 1, 'cream'); r(bag, 12, 4, 2, 14, 'ochre')
    ellipse(bag, 4, 3, 3, 2, 'ivory'); ellipse(bag, 9, 3, 3, 2, 'wood1'); r(bag, 6, 0, 2, 4, 'green')              # rice, beans, a herb
    slip = Geometry(); r(slip, 0, 0, 9, 6, 'ivory'); r(slip, 1, 1, 7, 1, 'steel1'); r(slip, 1, 3, 5, 1, 'steel1')
    drawer = Geometry(); r(drawer, 0, 0, 32, 8, 'wood2'); r(drawer, 0, 0, 32, 1, 'wood3'); r(drawer, 13, 2, 6, 2, 'gold'); r(drawer, 0, 8, 32, 3, 'wood0')
    return [('table', t, 128, 100), ('bag', bag, 140, 88), ('slip', slip, 218, 104), ('drawer_open', drawer, 218, 104 + 4)]


HOUSE_ANCHORS['k1'] = dict(table_end=(128, 100), bag=(140, 88), drawer=(218, 104), counter=(36, 98), tv=(264, 82), free_wall=(6, 6, 110, 40),
                           mother=(110, 74), father=(222, 76), girl=(100, 78))


def _view_k2(g, light, year, empty, rng):
    _setup(g, light, year, rng, window=(262, 54), photos=[(190, 24), (210, 24), (232, 24)])
    _counter(g, 36, 98, year)
    cb = (124, 38, 48, 36)                                                                                # corkboard
    r(g, cb[0] - 2, cb[1] - 2, cb[2] + 4, cb[3] + 4, 'wood1'); r(g, cb[0], cb[1], cb[2], cb[3], 'ochre')
    _noise(g, rng, 30, cb[0], cb[1], cb[0] + cb[2] - 2, cb[1] + cb[3], ['sand', 'clay'], 2)
    for px, py, pw, ph in ((cb[0] + 4, cb[1] + 5, 11, 8), (cb[0] + 30, cb[1] + 20, 12, 9)):               # old papers
        r(g, px, py, pw, ph, 'ivory'); r(g, px + 1, py + 1, pw - 2, 1, 'steel1'); r(g, px + 5, py - 1, 2, 2, 'red1')
    r(g, 0, 0, 11, 180, 'wood0'); r(g, 11, 0, 2, 180, 'wood1'); r(g, 0, 0, 1, 180, 'wood2')                 # the doorway's jamb, foreground left


def _pieces_k2(year, light, empty, cloth):
    out = _tbl_pieces(190, 104, cloth)
    slip = Geometry(); r(slip, 0, 0, 11, 8, 'ivory'); r(slip, 1, 1, 9, 1, 'steel1'); r(slip, 1, 3, 6, 1, 'steel1'); r(slip, 5, -1, 2, 2, 'red1')
    drawing = Geometry(); r(drawing, 0, 0, 13, 10, 'ivory'); r(drawing, 2, 5, 9, 4, 'green'); ellipse(drawing, 9, 3, 2, 2, 'gold'); r(drawing, 3, 2, 3, 3, 'red1')
    out += [('slip_pinned', slip, 128, 46), ('drawing', drawing, 224, 84)]
    return out


HOUSE_ANCHORS['k2'] = dict(corkboard=(124, 38, 172, 74), pin=(128, 46), counter=(36, 98), table=(190, 104), father=(140, 76), mother=(70, 74), girl=(240, 74), free_wall=(6, 6, 110, 40))


def _view_k3(g, light, year, empty, rng):
    _floor_modest(g, 0)
    r(g, 0, 0, 320, 6, 'plaster0')
    for (cx, cy, old) in ((102, 8, False), (190, 8, True), (102, 144, False), (190, 144, False)):             # chairs seen from above
        r(g, cx, cy, 24, 22, 'wood1'); r(g, cx, cy, 24, 22, 'wood1'); r(g, cx + 1, cy + 1, 22, 20, 'wood2')
        r(g, cx, cy + (0 if cy < 40 else 18), 24, 4, 'wood0')
        if old:
            r(g, cx + 3, cy + 5, 18, 11, 'red1'); r(g, cx + 7, cy + 8, 7, 4, 'cream')
    r(g, 66, 30, 188, 112, 'wood0'); r(g, 68, 32, 184, 108, 'wood2')                                       # the table top
    for yy in range(36, 140, 7):
        r(g, 68, yy, 184, 1, 'wood1')
        for k in range(rng.randrange(2, 4)):
            r(g, rng.randrange(70, 240), yy + 2, rng.randrange(6, 20), 1, 'wood3')
    r(g, 68, 32, 184, 1, 'wood3'); r(g, 68, 32, 1, 108, 'wood3')


def _pieces_k3(year, light, empty, cloth):
    slip = Geometry(); r(slip, 0, 0, 24, 15, 'ivory'); r(slip, 2, 3, 20, 1, 'steel1'); r(slip, 2, 6, 14, 1, 'steel1'); r(slip, 2, 9, 17, 1, 'steel1'); r(slip, 17, 11, 5, 2, 'red1')
    bill = Geometry(); r(bill, 0, 0, 18, 10, 'cream'); r(bill, 2, 2, 14, 1, 'steel1'); r(bill, 2, 5, 9, 1, 'steel1')
    bill2 = Geometry(); r(bill2, 0, 0, 17, 10, 'plaster3'); r(bill2, 2, 2, 13, 1, 'steel1'); r(bill2, 2, 6, 8, 1, 'steel1')
    loaf = Geometry(); ellipse(loaf, 13, 6, 13, 6, 'ochre'); ellipse(loaf, 13, 5, 11, 4, 'sand'); r(loaf, 6, 3, 2, 1, 'clay'); r(loaf, 13, 2, 2, 1, 'clay'); r(loaf, 18, 5, 2, 1, 'clay')
    beans = Geometry(); r(beans, 0, 0, 14, 20, 'sand'); r(beans, 0, 0, 14, 2, 'cream'); r(beans, 3, 6, 8, 8, 'wood1'); ellipse(beans, 7, 10, 3, 3, 'brick')
    jar = Geometry(); ellipse(jar, 8, 8, 8, 8, 'glass2'); ellipse(jar, 8, 8, 6, 6, 'glass1')
    for k in range(7):
        r(jar, 4 + (k * 5) % 9, 6 + (k * 3) % 7, 2, 2, 'gold')
    tin = Geometry(); ellipse(tin, 5, 5, 5, 5, 'steel2'); ellipse(tin, 5, 5, 3, 3, 'steel1'); r(tin, 4, 3, 2, 2, 'red1')
    return [('slip', slip, 92, 52), ('bill0', bill, 126, 50), ('bill1', bill2, 140, 60), ('loaf', loaf, 170, 80), ('beans', beans, 204, 74),
            ('tin', tin, 120, 100), ('jar', jar, 150, 108)]


HOUSE_ANCHORS['k3'] = dict(table=(66, 30, 254, 142), spots=dict(slip=(92, 52), bills=(126, 50), loaf=(170, 80), beans=(204, 74), tin=(120, 100), jar=(150, 108)))


def _view_k4(g, light, year, empty, rng):
    _setup(g, light, year, rng, window=(22, 54), photos=[(206, 36), (226, 36), (246, 36)])
    _tv(g, 262, 76, year)
    for cx in (96, 156):
        _chair_front(g, cx, 56)
    _chair_front(g, 232, 56, old=True)
    _chair_side(g, 30, 96, 1)


def _pieces_k4(year, light, empty, cloth):
    t = Geometry(); r(t, 0, 0, 200, 4, 'wood2'); r(t, 0, 0, 200, 1, 'wood3'); r(t, 0, 4, 200, 8, 'wood1'); r(t, 0, 11, 200, 1, 'wood0')
    r(t, 6, 12, 5, 34, 'wood1'); r(t, 6, 12, 1, 34, 'wood3'); r(t, 189, 12, 5, 34, 'wood1')
    if cloth or year >= 2022:
        r(t, -2, -1, 204, 3, 'plaster3'); r(t, -2, -1, 204, 1, 'ivory')
    out = [('table', t, 60, 88)]
    for i, px in enumerate((96, 150)):
        out.append((f'plate{i}', _plate(7, 2), px, 85))
    out.append(('plate_empty', _plate(7, 2, food=False, untouched=True), 232, 85))
    out.append(('plate_new', _plate(7, 2, food=False), 40, 85))
    return out


HOUSE_ANCHORS['k4'] = dict(table=(60, 88), seats=[(96, 56), (156, 56)], old_chair=(232, 56), end_chair=(30, 74), plate_empty=(232, 85), standing=(262, 70))


def _view_k5(g, light, year, empty, rng):
    _setup(g, light, year, rng, window=(236, 54), photos=[(150, 34), (172, 34), (194, 34)])
    _counter(g, 44, 98, year)
    _chair_front(g, 192, 62); _chair_front(g, 224, 62); _chair_front(g, 258, 62, old=True)


def _pieces_k5(year, light, empty, cloth):
    out = _tbl_pieces(176, 104, cloth)
    tx, ty = 176, 104
    for i, px in enumerate((tx + 8, tx + 30, tx + 52)):
        out.append((f'plate{i}', _plate(7, 2), px, ty - 3))
    pot = _pot_modest(); out.append(('pot_table', pot, tx + 60, ty - 12))
    stove_pot = Geometry(); r(stove_pot, 0, 0, 18, 11, 'steel1'); r(stove_pot, 0, 0, 18, 1, 'steel3'); r(stove_pot, -3, 3, 4, 2, 'black'); r(stove_pot, 17, 3, 4, 2, 'black'); ellipse(stove_pot, 9, 0, 9, 1, 'black')
    out.append(('stove_pot', stove_pot, 44 + 33, 98 - 20))
    return out


HOUSE_ANCHORS['k5'] = dict(counter=(44, 98), stove_pot=(77, 78), steam=(86, 76), table=(176, 104), old_chair=(258, 62), daughter=(100, 74), mother=(196, 60), father=(232, 60))


def _view_k6(g, light, year, empty, rng):
    r(g, 0, 0, 320, 180, 'plaster3'); r(g, 0, 40, 320, 6, 'glass1')
    r(g, 0, 46, 320, 134, 'wood2'); r(g, 0, 46, 320, 3, 'wood0'); r(g, 0, 49, 320, 1, 'wood3')
    for yy in range(56, 180, 9):
        r(g, 0, yy, 320, 1, 'wood1')
        for k in range(5):
            r(g, rng.randrange(320), yy + 3, rng.randrange(10, 40), 1, 'wood3')
    for (px, py) in ((42, 78), (146, 92), (250, 78)):                                                      # three full plates, big
        _big_plate(g, px, py)
    r(g, 100, 62, 26, 12, 'plaster3'); ellipse(g, 113, 66, 12, 5, 'ochre'); r(g, 104, 64, 12, 1, 'sand')    # bread in a cloth
    for gx in (20, 288):
        r(g, gx, 56, 8, 14, 'glass2'); r(g, gx, 56, 8, 2, 'ivory'); r(g, gx + 1, 62, 6, 8, 'glass1')
    if year >= 2022:                                                                                        # the old chair at the table's end, EMPTY: its cream cushion at the bottom right and an untouched plate
        ellipse(g, 316, 112, 24, 9, 'steel1'); ellipse(g, 316, 110, 24, 9, 'ivory'); ellipse(g, 316, 110, 19, 6, 'cream'); r(g, 290, 108, 3, 1, 'steel2'); r(g, 336, 108, 2, 1, 'steel2')
        r(g, 268, 150, 52, 5, 'wood0'); r(g, 268, 150, 52, 1, 'wood2'); r(g, 274, 158, 46, 18, 'red1'); r(g, 274, 158, 46, 2, 'red2'); r(g, 284, 164, 14, 7, 'cream')


def _big_plate(g, cx, cy):
    ellipse(g, cx, cy + 2, 30, 11, 'steel1'); ellipse(g, cx, cy, 30, 11, 'ivory'); ellipse(g, cx, cy, 25, 8, 'cream')
    ellipse(g, cx - 8, cy, 10, 5, 'ivory'); ellipse(g, cx + 7, cy - 1, 9, 5, 'wood1'); r(g, cx + 12, cy + 2, 8, 3, 'green')
    r(g, cx - 14, cy - 3, 3, 2, 'ivory'); r(g, cx + 2, cy + 3, 5, 1, 'brick')


def _pieces_k6(year, light, empty, cloth):
    p = Geometry(); ellipse(p, 30, 13, 30, 11, 'steel1'); ellipse(p, 30, 11, 30, 11, 'ivory'); ellipse(p, 30, 11, 25, 8, 'cream'); ellipse(p, 22, 11, 10, 5, 'ivory'); ellipse(p, 37, 10, 9, 5, 'wood1')
    return [('plate_passing', p, 200, 118)]


HOUSE_ANCHORS['k6'] = dict(plates=[(42, 78), (146, 92), (250, 78)], passing=(200, 118))


def _view_k7(g, light, year, empty, rng):
    _setup(g, light, year, rng, window=(22, 14), photos=[(206, 22), (226, 22), (246, 22)])
    for cx in (44, 270):
        _chair_front(g, cx, 52, old=(cx == 270))


def _pieces_k7(year, light, empty, cloth):
    t = Geometry(); r(t, 0, 0, 340, 6, 'wood2'); r(t, 0, 0, 340, 1, 'wood3'); r(t, 0, 6, 340, 12, 'wood1'); r(t, 0, 17, 340, 1, 'wood0')
    r(t, 20, 18, 7, 60, 'wood1'); r(t, 20, 18, 1, 60, 'wood3'); r(t, 303, 18, 7, 60, 'wood1')
    out = [('table', t, -10, 86)]
    shaft = None
    for i, bx in enumerate((120, 150, 176)):
        out.append((f'bowl{i}', _bowl(), bx, 81))
    out.append(('pot', _pot_modest(), 206, 74))
    ladle = Geometry(); line(ladle, (0, 8), (9, 0), .5, 'steel2'); ellipse(ladle, 0, 9, 2, 2, 'steel1')
    out.append(('ladle', ladle, 212, 66))
    out.append(('bowl_full', _bowl(full=True), 150, 81))
    return out


HOUSE_ANCHORS['k7'] = dict(table_top_y=86, steam=(213, 70), pot=(206, 74), bowls=[(120, 81), (150, 81), (176, 81)], mother=(226, 40), girl=(70, 38))


def _view_k8(g, light, year, empty, rng):
    r(g, 0, 0, 320, 180, 'plaster3'); r(g, 0, 26, 320, 6, 'glass1')
    r(g, 0, 32, 320, 148, 'wood2'); r(g, 0, 32, 320, 3, 'wood0'); r(g, 0, 35, 320, 1, 'wood3')
    for yy in range(44, 180, 11):
        r(g, 0, yy, 320, 1, 'wood1')
        for k in range(4):
            r(g, rng.randrange(320), yy + 4, rng.randrange(14, 50), 1, 'wood3')
    r(g, 244, 52, 22, 6, 'plaster3'); r(g, 244, 52, 22, 1, 'ivory')                                         # the cloth corner


def _pieces_k8(year, light, empty, cloth):
    def big_bowl(full):
        b = Geometry(); ellipse(b, 28, 20, 28, 12, 'blue1'); ellipse(b, 28, 18, 28, 12, 'ivory'); ellipse(b, 28, 19, 23, 9, 'wood0' if not full else 'cream')
        if full:
            for k in range(14):
                r(b, 12 + (k * 7) % 32, 14 + (k * 5) % 10, 3, 2, ['brick', 'wood1', 'ivory', 'ochre'][k % 4])
            ellipse(b, 20, 17, 6, 3, 'ivory')
        else:
            ellipse(b, 28, 20, 18, 6, 'brown')
        return b
    sp = Geometry(); line(sp, (0, 8), (16, 0), 1, 'steel2'); ellipse(sp, 0, 9, 4, 3, 'steel3')
    return [('bowl_empty', big_bowl(False), 108, 76), ('bowl_full', big_bowl(True), 108, 76), ('spoon', sp, 150, 62)]


HOUSE_ANCHORS['k8'] = dict(bowl=(108, 76, 164, 112))


def _view_k9(g, light, year, empty, rng):
    _setup(g, light, year, rng, window=None, photos=[(120, 36), (142, 36), (164, 36)])
    _counter(g, 254, 98, year)
    r(g, 0, 0, 22, 150, 'plaster2'); r(g, 22, 0, 2, 150, 'plaster0')                                       # the window wall, camera side
    _window_modest(g, -22, 36, light, 38, 44)
    for cx in (76, 118, 160, 204):                                                                           # three ordinary chairs for the three seated people, the OLD chair empty at the table's end
        _chair_front(g, cx, 66, old=(cx == 204))
    if light in ('dusk', 'night'):
        r(g, 140, 22, 2, 14, 'wood1'); ellipse(g, 141, 38, 4, 3, 'gold'); ellipse(g, 141, 38, 2, 1, 'ivory')


def _pieces_k9(year, light, empty, cloth):
    t = Geometry(); poly(t, [(30, 0), (150, 0), (166, 14), (14, 14)], 'wood2'); r(t, 14, 14, 152, 4, 'wood1'); r(t, 14, 14, 152, 1, 'wood3')
    r(t, 18, 18, 5, 26, 'wood1'); r(t, 157, 18, 5, 26, 'wood1')
    out = [('table', t, 60, 100)]
    for i, (px, py) in enumerate(((82, 100), (124, 100), (166, 100))):
        out.append((f'plate{i}', _plate(8, 3), px, py + 3))
    if light in ('day', 'morning', 'dusk'):
        g_, boxes = _shaft_geom(22, 36, 80, 40, 150, 140)
        out.insert(0, ('shaft', g_, 0, 0)); HOUSE_ANCHORS['k9']['shaft_boxes'] = boxes
    return out


HOUSE_ANCHORS['k9'] = dict(table=(60, 100), seats=[(76, 66), (118, 66), (160, 66)], old_chair=(204, 66), shaft_boxes=[])   # the old chair stays EMPTY (the pandemic loss, set up in 25d)


def _view_door(g, light, year, empty, rng):
    _setup(g, light, year, rng, window=(220, 34), photos=[(60, 26)])
    x0, y0, x1, y1 = 138, 54, 182, 118
    r(g, x0 - 4, y0 - 4, x1 - x0 + 8, y1 - y0 + 4, 'ivory'); r(g, x0 - 4, y0 - 4, 1, y1 - y0 + 4, 'plaster3')
    r(g, x0, y0, x1 - x0, y1 - y0, 'blue1')
    for lx in (x0 + 2, (x0 + x1) // 2 + 2):
        r(g, lx, y0 + 3, 18, 22, 'blue0'); r(g, lx, y0 + 3, 18, 1, 'blue2'); r(g, lx, y0 + 30, 18, 26, 'blue0'); r(g, lx, y0 + 30, 18, 1, 'blue2')
    r(g, (x0 + x1) // 2 - 1, y0, 2, y1 - y0, 'blue2')
    r(g, 150, y0 + 33, 14, 3, 'steel2'); r(g, 150, y0 + 33, 14, 1, 'steel3'); r(g, 172, y0 + 34, 2, 4, 'gold'); r(g, 168, y0 + 34, 2, 4, 'gold')
    r(g, 143, y0 + 8, 6, 2, 'steel1')                                                                         # the bolt
    r(g, x0 - 6, 118, x1 - x0 + 12, 4, 'plaster3'); r(g, x0 - 6, 118, x1 - x0 + 12, 1, 'ivory')           # sill / step
    r(g, 70, 60, 36, 4, 'wood1'); r(g, 72, 62, 3, 3, 'steel2'); r(g, 86, 62, 3, 3, 'steel2'); r(g, 100, 62, 3, 3, 'steel2')   # the hook board
    # coat on the hook, and shoes on the floor
    poly(g, [(84, 64), (100, 64), (103, 82), (104, 100), (82, 100), (82, 82)], 'trouser1'); r(g, 84, 64, 16, 2, 'trouser0'); r(g, 91, 66, 2, 34, 'trouser0'); r(g, 96, 80, 3, 2, 'steel2')
    for sx in (92, 106):
        r(g, sx, 128, 12, 5, 'wood0'); r(g, sx + 1, 125, 7, 4, 'wood0'); r(g, sx, 133, 12, 1, 'black')


def _pieces_door(year, light, empty, cloth):
    out = []
    if light in ('day', 'morning', 'dusk'):
        ga, boxes_a = _shaft_geom(258, 34, 78, 188, 250, 140)
        gb, boxes_b = _shaft_geom(258, 34, 78, 176, 236, 140)
        out += [('shaft_a', ga, 0, 0), ('shaft_b', gb, 0, 0)]
        HOUSE_ANCHORS['door']['shaft_boxes_a'] = boxes_a; HOUSE_ANCHORS['door']['shaft_boxes_b'] = boxes_b
    return out


HOUSE_ANCHORS['door'] = dict(door=(138, 54, 182, 118), step_y=118, mother=(150, 98), hook=(84, 64), shoes=(92, 125), shaft_boxes_a=[], shaft_boxes_b=[])


def _view_window(g, light, year, empty, rng):
    """The house seen from OUTSIDE, close on its window: the lit dining room framed by the blue window (10h)."""
    ext = Geometry()
    r(ext, 0, 0, 320, 180, 'glass2'); r(ext, 0, 112, 320, 70, 'glass1'); r(ext, 0, 111, 320, 1, 'ivory')
    for _ in range(80):
        r(ext, rng.randrange(320), rng.randrange(0, 180), rng.randrange(1, 4), 1, 'plaster3' if rng.random() < .6 else 'plaster2')
    r(ext, 0, 138, 320, 6, 'plaster0')
    r(ext, 276, 100, 20, 38, 'clay'); r(ext, 274, 98, 24, 4, 'brick'); ellipse(ext, 286, 90, 12, 11, 'green'); ellipse(ext, 282, 84, 6, 5, 'metal2')
    r(ext, 22, 20, 5, 118, 'steel1'); r(ext, 22, 20, 1, 118, 'steel2')                                      # a drain pipe
    gr = _HOUSE_GRADE[light]
    if gr:
        _grade(ext, *gr)
    g.paste(ext, 0, 0)
    wx, wy, ww, wh = 64, 18, 192, 94
    r(g, wx - 5, wy - 5, ww + 10, wh + 10, 'blue1'); r(g, wx - 5, wy - 5, ww + 10, 2, 'blue2'); r(g, wx - 5, wy - 5, 2, wh + 10, 'blue2')
    # the lit room behind
    r(g, wx, wy, ww, wh, 'ivory'); r(g, wx, wy, ww, 20, 'cream'); r(g, wx, wy + 52, ww, wh - 52, 'glass1'); r(g, wx, wy + 52, ww, 2, 'ivory')
    r(g, wx, wy + 74, ww, 20, 'brick')
    poly(g, [(wx + 86, wy), (wx + 106, wy), (wx + 140, wy + 74), (wx + 52, wy + 74)], 'ivory')                # lamp glow
    r(g, wx + 95, wy, 2, 12, 'wood1'); ellipse(g, wx + 96, wy + 14, 5, 3, 'gold'); ellipse(g, wx + 96, wy + 14, 3, 1, 'ivory')
    _tv(g, wx + 8, wy + 50, year)
    r(g, wx + 150, wy + 34, 36, 3, 'wood1'); ellipse(g, wx + 160, wy + 30, 4, 4, 'clay'); ellipse(g, wx + 172, wy + 31, 3, 4, 'ochre')
    _photos(g, year, [(wx + 56, wy + 22), (wx + 130, wy + 18), (wx + 80, wy + 22)])
    for cx in (wx + 62, wx + 94, wx + 126):
        _chair_front(g, cx, wy + 38, old=(cx == wx + 126))
    # curtains drawn aside, mullion, sill
    for cx in (wx, wx + ww - 16):
        r(g, cx, wy, 16, wh, 'blue2'); r(g, cx, wy, 16, 1, 'blue3')
        for k in range(cx + 2, cx + 16, 4):
            r(g, k, wy + 1, 1, wh - 1, 'blue1')
    r(g, wx - 8, wy + wh + 5, ww + 16, 4, 'ivory'); r(g, wx - 8, wy + wh + 9, ww + 16, 2, 'plaster0')


# 10h: the pot stands on the table's free right end, BEHIND no seat: the steam column (9 x 14 px, cells x -5..3, y -14..-1 from the anchor) must clear the
# head box (18 x 22 from each seat anchor) of father, mother and girl, and the lamp. The table is widened to hold pot and jug (it ends at x 224).
WINDOW_TABLE_W = 118
WINDOW_POT = (196, 76)                 # pot piece origin; rim row = y + 3; the pot is 14 wide (+ 2 px handles each side), centre x + 7
WINDOW_JUG = (214, 80)
WINDOW_STEAM = (WINDOW_POT[0] + 7, WINDOW_POT[1] + 3)      # ctx.steam(p, *WINDOW_STEAM, a, b) = (203, 79)
WINDOW_HEAD_BOX = (18, 22)             # (w, h) of the head box at a seat anchor: x sx..sx+18, y sy..sy+22


def _pieces_window(year, light, empty, cloth):
    W = WINDOW_TABLE_W
    t = Geometry(); r(t, 0, 0, W, 6, 'wood2'); r(t, 0, 0, W, 1, 'wood3'); r(t, 0, 6, W, 7, 'wood1'); r(t, 0, 12, W, 1, 'wood0')
    out = [('table', t, 106, 88)]
    for i, bx in enumerate((118, 140, 162)):
        out.append((f'bowl{i}', _bowl(), bx, 84))
    out.append(('pot', _pot_modest(), *WINDOW_POT))
    jug = Geometry(); r(jug, 0, 2, 5, 8, 'glass2'); r(jug, 0, 2, 5, 1, 'ivory'); r(jug, 5, 4, 2, 3, 'glass1'); out.append(('jug', jug, *WINDOW_JUG))
    return out


HOUSE_ANCHORS['window'] = dict(window=(64, 18, 256, 112), table=(106, 88), seats=[(114, 56), (146, 56), (178, 56)], steam=WINDOW_STEAM, pot=WINDOW_POT, jug=WINDOW_JUG, lamp=(160, 32))


# ============================================================================================ GABINETE-O1 (presidential office)
GABINETE_MAP_RECT = (252, 46, 300, 90)      # the wall map of Brazil (07e); in 14f it is gone and a faded patch remains
GABINETE_DOOR_RECT = (8, 58, 36, 118)       # the door the office is entered by (07e: Lula enters, the door closes at +4.6)
GABINETE_DESK = dict(top_y=98, x0=109, x1=221, seat=(166, 106), front_y=106)   # `seat` = hip point of the person in the chair


def gabinete_o1(map_on=True, door='closed', light='day'):
    """GABINETE-O1: the presidential office, 320x180. Desk top, high-back leather chair, flag at the left, window with the Brasilia
    skyline, wall map of Brazil at the right (`map_on=False` for 14f: the map is gone, a faded patch and a nail remain), door at the
    far left ('closed' | 'open': dark corridor; the closing leaf is `gabinete_o1_door_leaf`). The desk's FRONT panel is not in
    this background: draw `gabinete_o1_fg()` after the seated figure so legs are hidden (2.0.0 defect V-027).
    light: 'day' | 'night' (13i is another room: OFFICE-O2)."""
    assert door in ('closed', 'open') and light in ('day', 'night')
    g = Geometry(); rng = random.Random(1999)
    r(g, 0, 0, 320, 180, 'plaster2'); r(g, 0, 0, 320, 7, 'plaster1'); r(g, 0, 7, 320, 1, 'plaster3')
    r(g, 0, 90, 320, 28, 'wood1'); r(g, 0, 90, 320, 2, 'wood3')                                       # panelled dado (28 rows, a chair-rail height)
    for xx in range(6, 320, 26):
        r(g, xx, 95, 20, 18, 'wood2'); r(g, xx, 95, 20, 1, 'wood3'); r(g, xx, 112, 20, 1, 'wood0')
    r(g, 0, 116, 320, 64, 'floor1'); r(g, 0, 116, 320, 2, 'floor0')
    for yy in (124, 139, 157):
        r(g, 0, yy, 320, 1, 'floor0')
    r(g, 70, 114, 190, 34, 'red0'); r(g, 70, 114, 190, 1, 'red1'); r(g, 74, 118, 182, 26, 'brick')             # rug under the desk
    # window with the Brasilia skyline: sill 20 above the wall base (y 98), top 62 above (y 56), centred behind the chair
    r(g, 110, 56, 100, 42, 'wood0'); r(g, 113, 59, 94, 36, 'glass1')
    r(g, 114, 80, 92, 15, 'green'); r(g, 148, 68, 6, 22, 'plaster3'); r(g, 160, 68, 6, 22, 'plaster3'); r(g, 125, 84, 72, 3, 'ivory')
    ellipse(g, 134, 84, 9, 4, 'ivory'); ellipse(g, 188, 82, 9, 4, 'ivory'); r(g, 178, 77, 18, 4, 'glass1')
    r(g, 159, 58, 2, 38, 'wood1'); r(g, 109, 97, 102, 3, 'cream')
    # flag on a stand
    line(g, (56, 58), (56, 126), 1, 'wood2'); poly(g, [(57, 59), (87, 62), (85, 90), (57, 87)], 'green'); poly(g, [(60, 74), (70, 66), (80, 75), (70, 84)], 'gold'); ellipse(g, 70, 75, 4, 4, 'blue0')
    r(g, 51, 123, 12, 4, 'wood0')
    # door
    x0, y0, x1, y1 = GABINETE_DOOR_RECT
    r(g, x0 - 3, y0 - 3, x1 - x0 + 6, y1 - y0 + 3, 'wood0')
    if door == 'closed':
        r(g, x0, y0, x1 - x0, y1 - y0, 'wood1')
        for py, ph in ((y0 + 4, 22), (y0 + 31, 24)):
            r(g, x0 + 4, py, x1 - x0 - 8, ph, 'wood2'); r(g, x0 + 4, py, x1 - x0 - 8, 1, 'wood3')
        r(g, x1 - 7, y0 + 28, 3, 4, 'gold')
    else:
        r(g, x0, y0, x1 - x0, y1 - y0, 'umber'); r(g, x0 + 2, y0 + 24, x1 - x0 - 4, y1 - y0 - 24, 'floor0')            # dark corridor
        r(g, x0, y0, 3, y1 - y0, 'wood1')
    # map or its ghost
    mx0, my0, mx1, my1 = GABINETE_MAP_RECT
    if map_on:
        r(g, mx0, my0, mx1 - mx0, my1 - my0, 'wood1'); r(g, mx0 + 2, my0 + 2, mx1 - mx0 - 4, my1 - my0 - 4, 'blue2')
        poly(g, [(mx0 + 11, my0 + 7), (mx0 + 24, my0 + 4), (mx0 + 35, my0 + 8), (mx0 + 41, my0 + 16), (mx0 + 42, my0 + 24),
                 (mx0 + 36, my0 + 31), (mx0 + 30, my0 + 37), (mx0 + 22, my0 + 38), (mx0 + 16, my0 + 33), (mx0 + 9, my0 + 26), (mx0 + 6, my0 + 18), (mx0 + 6, my0 + 12)], 'green')
        for (a, b, c, d) in ((16, 13, 27, 15), (27, 15, 35, 23), (20, 23, 31, 27), (19, 30, 27, 33)):
            line(g, (mx0 + a, my0 + b), (mx0 + c, my0 + d), .4, 'metal2')
        ellipse(g, mx0 + 24, my0 + 20, 2, 2, 'gold')
    else:
        r(g, mx0, my0, mx1 - mx0, my1 - my0, 'plaster3'); r(g, mx0, my0, mx1 - mx0, 1, 'plaster2'); r(g, mx0, my1 - 1, mx1 - mx0, 1, 'plaster2')
        r(g, mx0, my0, 1, my1 - my0, 'plaster2'); r(g, mx1 - 1, my0, 1, my1 - my0, 'plaster2')
        r(g, (mx0 + mx1) // 2, my0 + 3, 2, 3, 'steel1')                                                  # the nail
    # desk top and what stands on it, then the chair behind
    d = GABINETE_DESK
    r(g, 150, 62, 32, 40, 'red0'); r(g, 150, 62, 32, 2, 'red1'); r(g, 148, 60, 36, 3, 'wood0'); r(g, 152, 64, 28, 2, 'brick')   # high chair back
    r(g, 154, 70, 24, 1, 'red1'); r(g, 154, 80, 24, 1, 'red1')
    poly(g, [(116, d['top_y']), (211, d['top_y']), (221, d['front_y']), (109, d['front_y'])], 'wood2'); r(g, 109, d['front_y'] - 1, 112, 1, 'sand')
    poly(g, [(140, 100), (160, 100), (163, 104), (143, 104)], 'ivory'); r(g, 145, 101, 14, 1, 'plaster1')                         # a blotter
    r(g, 190, 96, 11, 7, 'black'); r(g, 189, 95, 13, 3, 'steel0'); r(g, 116, 100, 7, 3, 'gold')                                     # phone, inkwell
    if light == 'night':
        _grade(g, (.5, .5, .72), (0, 4, 20))
    return g


def gabinete_o1_fg():
    """Desk front (the panel in front of the chair), 320x180 canvas: draw AFTER the seated figure."""
    g = Geometry(); d = GABINETE_DESK
    r(g, d['x0'] + 2, d['front_y'], d['x1'] - d['x0'] - 4, 22, 'wood1'); r(g, d['x0'] + 2, d['front_y'], d['x1'] - d['x0'] - 4, 1, 'wood3')
    for dx in (6, 40, 74):
        r(g, d['x0'] + dx, d['front_y'] + 3, 28, 15, 'wood2'); r(g, d['x0'] + dx, d['front_y'] + 3, 28, 1, 'wood3'); r(g, d['x0'] + dx + 11, d['front_y'] + 7, 6, 2, 'gold')
    r(g, d['x0'], d['front_y'] + 22, 112, 2, 'wood0')                                   # desk top 22 rows above its foot line (y 128)
    return g


def gabinete_o1_door_leaf(state):
    """The office door leaf over `gabinete_o1(door='open')`: state 0 open (nothing), 1 ajar, 2 nearly closed, 3 closed.
    Placed at (0, 0). The caller steps the states in time (the closing is one agent: the door)."""
    g = Geometry(); x0, y0, x1, y1 = GABINETE_DOOR_RECT
    if state == 0:
        return g
    w = {1: 12, 2: 24, 3: x1 - x0}[state]; s = {1: 8, 2: 3, 3: 0}[state]
    poly(g, [(x0, y0), (x0 + w, y0 + s), (x0 + w, y1 - s), (x0, y1)], 'wood1')
    if w > 14:
        r(g, x0 + 4, y0 + 4 + s, w - 8, 22, 'wood2'); r(g, x0 + 4, y0 + 31, w - 8, 24, 'wood2')
    if state == 3:
        r(g, x1 - 7, y0 + 28, 3, 4, 'gold')
    return g


# ============================================================================================ GABINETE-DOOR (corridor)
GABINETE_CORRIDOR_DOOR = (128, 58, 188, 118)     # double door, 60 x 60 rows (1.2 x the 49-row adult)


def gabinete_door(door='closed', light='day'):
    """GABINETE-DOOR (07f, 14g): the office door seen from the corridor, 320x180: a panelled double-height wooden door in the centre,
    wall sconces at both sides ('a lamp'), a red runner on the floor. door: 'closed' | 'open' (warm lit room behind, leaf swung
    in: `gabinete_door_leaf(frac)` closes it). light: 'day' | 'night' (sconces glow in both)."""
    assert door in ('closed', 'open') and light in ('day', 'night')
    g = Geometry(); rng = random.Random(7)
    r(g, 0, 0, 320, 180, 'plaster3'); r(g, 0, 0, 320, 10, 'plaster2'); r(g, 0, 10, 320, 2, 'plaster1')
    r(g, 0, 90, 320, 28, 'wood1'); r(g, 0, 90, 320, 2, 'wood3')
    for xx in range(10, 320, 30):
        r(g, xx, 95, 22, 18, 'wood2'); r(g, xx, 95, 22, 1, 'wood3')
    r(g, 0, 116, 320, 64, 'floor1'); r(g, 0, 116, 320, 2, 'floor0')
    for yy in (126, 140, 158):
        r(g, 0, yy, 320, 1, 'floor0')
    poly(g, [(130, 118), (190, 118), (236, 180), (84, 180)], 'red0'); poly(g, [(134, 118), (186, 118), (226, 180), (94, 180)], 'brick')
    x0, y0, x1, y1 = GABINETE_CORRIDOR_DOOR
    r(g, x0 - 6, y0 - 6, x1 - x0 + 12, y1 - y0 + 6, 'wood0'); r(g, x0 - 6, y0 - 6, x1 - x0 + 12, 1, 'wood2')
    if door == 'closed':
        r(g, x0, y0, x1 - x0, y1 - y0, 'wood1')
        for (px, py, pw, ph) in ((x0 + 5, y0 + 5, 22, 20), (x0 + 33, y0 + 5, 22, 20), (x0 + 5, y0 + 30, 22, 24), (x0 + 33, y0 + 30, 22, 24)):
            r(g, px, py, pw, ph, 'wood2'); r(g, px, py, pw, 1, 'wood3'); r(g, px, py + ph - 1, pw, 1, 'wood0')
        r(g, x0 + 26, y0 + 27, 2, 4, 'gold'); r(g, x0 + 32, y0 + 27, 2, 4, 'gold'); r(g, x0 + 20, y0 + 56, 20, 2, 'gold')                                                      # brass kick plate
    else:
        r(g, x0, y0, x1 - x0, y1 - y0, 'ivory'); r(g, x0, y0, x1 - x0, 12, 'cream'); r(g, x0, 102, x1 - x0, y1 - 102, 'brick')
        r(g, x0 + 14, 96, 30, 3, 'wood2'); r(g, x0 + 16, 99, 2, 12, 'wood1'); r(g, x0 + 40, 99, 2, 12, 'wood1')                # a desk edge inside
    r(g, x0 - 4, y1, x1 - x0 + 8, 3, 'plaster2')
    for sx in (74, 238):                                                                                   # the wall lamps (centre 50 rows above the floor)
        r(g, sx, 62, 8, 11, 'steel1'); r(g, sx + 1, 63, 6, 9, 'gold' if light == 'night' else 'cream'); r(g, sx - 1, 60, 10, 3, 'steel0'); r(g, sx - 1, 73, 10, 2, 'steel0')
        if light == 'night':
            poly(g, [(sx + 1, 75), (sx + 7, 75), (sx + 18, 104), (sx - 10, 104)], 'cream')
    if light == 'night':
        _grade(g, (.62, .6, .78), (0, 2, 12))
        for sx in (74, 238):
            r(g, sx, 62, 8, 11, 'steel1'); r(g, sx + 1, 63, 6, 9, 'gold'); r(g, sx - 1, 60, 10, 3, 'steel0')
    return g


def gabinete_door_leaf(frac):
    """The corridor door leaf as a perspective polygon, hinged at its left edge, over `gabinete_door(door='open')`.
    frac 0 = swung open (a thin slice at the hinge), 1 = closed (the leaf fills the doorway with its four panels). Steps of .25."""
    x0, y0, x1, y1 = GABINETE_CORRIDOR_DOOR
    g = Geometry(); w = max(2, round((x1 - x0) * frac)); s = round((1 - frac) * 9)
    poly(g, [(x0, y0), (x0 + w, y0 + s), (x0 + w, y1 - s), (x0, y1)], 'wood1')
    if w > 20:
        pw = (w - 12) // 2
        for k in range(2):
            px = x0 + 4 + k * (pw + 4)
            r(g, px, y0 + 6 + s, pw, 20, 'wood2'); r(g, px, y0 + 6 + s, pw, 1, 'wood3'); r(g, px, y0 + 31, pw, 24 - s, 'wood2')
    if frac >= 1:
        r(g, x0 + 26, y0 + 27, 2, 4, 'gold'); r(g, x0 + 32, y0 + 27, 2, 4, 'gold'); r(g, x0 + 20, y0 + 56, 20, 2, 'gold')
    return g


# ============================================================================================ TV-ROOM
TV_SCREEN_WIDE = (122, 64, 178, 88)       # screen glass, camera 'wide' (06a, 06f, 06h): captions 'DERROTA' x 125-175, y 80-88 fall inside
TV_SCREEN_FAR = (128, 62, 184, 86)         # camera 'far' (17g, 28a): captions '2018' x 130-160 / '2006' x 140-170, y 70-78 fall inside
TV_CLOSE_SCREEN = (36, 22, 284, 132)       # tv_close() (28b): caption '2022' x 130-160, y 40-48 falls inside
TV_CALENDAR_SIGN_RECT = (60, 40, 90, 60)   # the wall calendar's sign rectangle (06a 1989, 06f 1989, 06h 1998): the year is drawn in the page
TV_ROOM_YEARS = (1989, 1994, 1998, 2006, 2018)


def _tv_body(g, sx0, sy0, sx1, sy1):
    """CRT set around the screen rectangle (body = screen + 4 black + 1 wood each side, 34 rows tall for a 24-row screen): knobs, speaker grille, aerial attached to the set."""
    r(g, sx0 - 5, sy0 - 5, sx1 - sx0 + 10, sy1 - sy0 + 10, 'wood0'); r(g, sx0 - 5, sy0 - 5, sx1 - sx0 + 10, 1, 'wood2')
    r(g, sx0 - 4, sy0 - 4, sx1 - sx0 + 8, sy1 - sy0 + 8, 'black')
    r(g, sx0, sy0, sx1 - sx0, sy1 - sy0, 'blue0')
    r(g, sx1 + 6, sy0 + 1, 4, 10, 'steel0')
    for k in range(4):
        r(g, sx1 + 6, sy0 + 1 + k * 3, 4, 1, 'steel1')
    ellipse(g, sx1 + 8, sy1 - 7, 2, 2, 'steel2'); ellipse(g, sx1 + 8, sy1 - 2, 2, 2, 'steel2')
    mx = (sx0 + sx1) // 2
    line(g, (mx, sy0 - 5), (mx - 10, sy0 - 21), .5, 'steel2'); line(g, (mx, sy0 - 5), (mx + 12, sy0 - 20), .5, 'steel2')      # the aerial, attached to the set
    r(g, mx - 3, sy0 - 7, 6, 2, 'steel1')


def tv_room(year=1989, camera='wide', light='night', calendar=None):
    """TV-ROOM: the family living room, 320x180; the TV is at the centre with its aerial ATTACHED to the set. The TV picture is
    driven by the caller: draw the content inside `TV_SCREEN_WIDE` / `TV_SCREEN_FAR` and then `tv_room_fg(camera)` (bezel and
    glass glare) so nothing spills; a dark glass is drawn here (set off). Also `tv_glow(camera)` for the blue spill on the floor.
    year: 1989 (06a, 06f) | 1994 (06g: as 1989, one photograph, calendar '1994') | 1998 (06h: bigger plant, two photographs) | 2006 (28a) | 2018 (17g: same set, newer curtains) ;
    camera: 'wide' (06a/f/h: TV nearer, sofa back in the foreground via `tv_room_sofa()`) | 'far' (17g, 28a: TV smaller on the far wall) ;
    light: 'night' (default: window dark, lamp on) | 'day' ; calendar: draw the wall calendar page with the year (default True for
    1989, 1994 and 1998, the plan's signs, rect `TV_CALENDAR_SIGN_RECT`; False for 2006 and 2018)."""
    assert year in TV_ROOM_YEARS and camera in ('wide', 'far') and light in ('night', 'day')
    cal = (year in (1989, 1994, 1998)) if calendar is None else calendar
    g = Geometry(); rng = random.Random(1989)
    r(g, 0, 0, 320, 180, 'plaster2'); r(g, 0, 0, 320, 6, 'plaster1')
    r(g, 0, 90, 320, 28, 'wood1'); r(g, 0, 90, 320, 2, 'wood3')                                         # wood dado
    for xx in range(0, 320, 20):
        r(g, xx, 94, 1, 22, 'wood0')
    _noise(g, rng, 60, 0, 8, 320, 88, ['plaster3', 'plaster1'], 3)
    r(g, 0, 116, 320, 64, 'floor1'); r(g, 0, 116, 320, 2, 'floor0')
    for yy in (126, 140, 158):
        r(g, 0, yy, 320, 1, 'floor0')
    r(g, 40, 122, 240, 44, 'red0'); r(g, 44, 126, 232, 36, 'brick'); r(g, 40, 122, 240, 1, 'red1')    # rug
    # window (left) and plant
    gl = ('glass1', 'glass2') if light == 'day' else ('blue0', 'blue1')
    r(g, 14, 56, 38, 42, 'wood0'); r(g, 17, 59, 32, 36, gl[0]); r(g, 17, 59, 32, 10, gl[1]); r(g, 32, 59, 2, 36, 'wood0'); r(g, 17, 75, 32, 2, 'wood0')
    cur = 'blue2' if year != 2018 else 'red2'
    for cx in (17, 41):
        r(g, cx, 59, 8, 36, cur); r(g, cx, 59, 8, 1, 'ivory')
        for k in range(cx + 1, cx + 8, 3):
            r(g, k, 60, 1, 34, 'blue1' if year != 2018 else 'red1')
    r(g, 10, 98, 46, 3, 'wood2')                                                                         # sill: 20 rows above the wall base
    big = 1 if year == 1998 else 0
    px = 28
    r(g, px - 5, 106, 10, 12, 'clay'); r(g, px - 6, 105, 12, 3, 'brick')
    for (dx, dy, rr_) in ((0, -6, 6), (-5, -12 - 4 * big, 5), (5, -13 - 5 * big, 5), (0, -17 - 6 * big, 5)):
        ellipse(g, px + dx, 104 + dy, rr_, rr_ * .8, 'green'); ellipse(g, px + dx - 1, 103 + dy, rr_ - 2, (rr_ - 2) * .8, 'metal2')
    # bookshelf (right) with books, two photographs
    shelf(g, 236, 60, 70, 58)                                                                            # bookshelf, 58 rows
    r(g, 208, 62, 11, 13, 'wood1'); r(g, 209, 63, 9, 11, 'ivory'); r(g, 210, 64, 7, 9, 'sand'); ellipse(g, 213, 68, 2, 2, 'skin1')
    if year >= 1998:
        r(g, 192, 62, 11, 13, 'wood1'); r(g, 193, 63, 9, 11, 'ivory'); r(g, 194, 64, 7, 9, 'blue2'); ellipse(g, 197, 68, 2, 2, 'skin1')
    # wall calendar (the sign): the year printed on its page
    if cal:
        cx0, cy0, cx1, cy1 = TV_CALENDAR_SIGN_RECT
        r(g, cx0 - 1, cy0 - 1, cx1 - cx0 + 2, cy1 - cy0 + 2, 'wood0'); r(g, cx0, cy0, cx1 - cx0, cy1 - cy0, 'ivory'); r(g, cx0, cy0, cx1 - cx0, 6, 'red1')
        _sign_text(g, str(year), (cx0, cy0 + 8, cx1, cy0 + 17), 'steel0')
        for yy in (cy0 + 19, cy0 + 24, cy0 + 29, cy0 + 34):
            for xx in range(cx0 + 2, cx1 - 3, 4):
                r(g, xx, yy, 2, 1, 'steel1')
        r(g, (cx0 + cx1) // 2 - 1, cy0 - 3, 2, 3, 'steel1')
    # the TV on its cabinet
    sc = TV_SCREEN_WIDE if camera == 'wide' else TV_SCREEN_FAR
    ty = sc[3] + 6                                                                                       # cabinet top: 24 rows above the wall base (y 118)
    r(g, sc[0] - 14, ty, sc[2] - sc[0] + 28, 118 - ty + 10, 'wood2'); r(g, sc[0] - 14, ty, sc[2] - sc[0] + 28, 2, 'wood3')
    r(g, sc[0] - 14, 118 + 8, sc[2] - sc[0] + 28, 2, 'wood0')
    for dx in (sc[0] - 8, (sc[0] + sc[2]) // 2 + 2):
        r(g, dx, ty + 6, (sc[2] - sc[0]) // 2 - 4, 18, 'wood1'); r(g, dx, ty + 6, (sc[2] - sc[0]) // 2 - 4, 1, 'wood3'); r(g, dx + (sc[2] - sc[0]) // 4, ty + 14, 3, 2, 'gold')
    _tv_body(g, *sc)
    if light == 'night':
        _grade(g, (.78, .74, .86), (0, 2, 10))
    return g


def tv_room_sofa():
    """Sofa back seen from behind in the foreground (06a, 06f, 06h: the family sits from behind). 320x180 canvas; draw it AFTER the
    figures (their lower bodies disappear behind it). Figures (sprite origin y ~ 95: heads at y ~ 100-112) sit with the sofa top at y 124; sprite origin y 95 keeps the soles at row 143."""
    g = Geometry()
    r(g, 70, 124, 180, 24, 'red0'); r(g, 70, 124, 180, 2, 'red1'); r(g, 64, 128, 10, 20, 'brick'); r(g, 246, 128, 10, 20, 'brick')
    for x in (110, 160, 210):
        r(g, x, 128, 1, 18, 'brick')
    r(g, 64, 128, 10, 2, 'red1'); r(g, 246, 128, 10, 2, 'red1')
    return g


def tv_room_fg(camera='wide'):
    """Bezel and glass glare of the TV on top of the content the caller draws in the screen (320x180 canvas)."""
    sc = TV_SCREEN_WIDE if camera == 'wide' else TV_SCREEN_FAR
    g = Geometry(); x0, y0, x1, y1 = sc
    r(g, x0 - 4, y0 - 4, x1 - x0 + 8, 4, 'black'); r(g, x0 - 4, y1, x1 - x0 + 8, 4, 'black'); r(g, x0 - 4, y0, 4, y1 - y0, 'black'); r(g, x1, y0, 4, y1 - y0, 'black')
    poly(g, [(x0 + 2, y0 + 1), (x0 + 10, y0 + 1), (x0 + 2, y0 + 12)], 'steel1')
    return g


def tv_test_card(camera='wide'):
    """TV colour-bars test card (06g, the screen before the broadcast starts): a Geometry on the 320 x 180 canvas, in ABSOLUTE coordinates, covering exactly
    `TV_SCREEN_WIDE` (camera 'wide') or `TV_SCREEN_FAR` ('far'): seven bars (white, yellow, cyan, green, purple, red, blue; each (width // 7) px wide, the last takes the
    remainder) over the top 18 rows and a 6-row strip of blue / black / purple / black / cyan / black / white blocks under them. Draw it with `ctx.G(s, tv_test_card(), 0, 0)`
    after `tv_room`, before the content and `tv_room_fg(camera)` (the bezel covers nothing of it: it stays inside the glass)."""
    sc = TV_SCREEN_WIDE if camera == 'wide' else TV_SCREEN_FAR
    x0, y0, x1, y1 = sc; w, h = x1 - x0, y1 - y0; g = Geometry()
    bw = w // 7; cols = ('f2_white', 'gold', 'blue3', 'green', 'purple', 'red1', 'blue1')
    for k, c in enumerate(cols):
        xa = x0 + k * bw; xb = x1 if k == 6 else xa + bw
        r(g, xa, y0, xb - xa, h - 6, c)
    strip = ('blue1', 'black', 'purple', 'black', 'blue3', 'black', 'f2_white')
    for k, c in enumerate(strip):
        xa = x0 + k * bw; xb = x1 if k == 6 else xa + bw
        r(g, xa, y1 - 6, xb - xa, 6, c)
    return g


def tv_screen_off(camera='wide'):
    """The dark glass (what the TV shows when it is off), to redraw over content when the TV is switched off (06h +3.8 s)."""
    sc = TV_SCREEN_WIDE if camera == 'wide' else TV_SCREEN_FAR
    g = Geometry(); r(g, sc[0], sc[1], sc[2] - sc[0], sc[3] - sc[1], 'black'); poly(g, [(sc[0] + 2, sc[1] + 1), (sc[0] + 10, sc[1] + 1), (sc[0] + 2, sc[1] + 12)], 'metal0')
    return g


def tv_glow(camera='wide'):
    """Blue light spilling from the lit TV over the rug and wall: draw with opacity ~.15."""
    sc = TV_SCREEN_WIDE if camera == 'wide' else TV_SCREEN_FAR
    g = Geometry(); poly(g, [(sc[0], sc[3] + 6), (sc[2], sc[3] + 6), (sc[2] + 40, 150), (sc[0] - 40, 150)], 'blue3')
    return g


def tv_close(light='night'):
    """TV-CLOSE (28b): the set filling the frame; screen glass `TV_CLOSE_SCREEN` (caller draws the 'two lecterns' there and morphs them
    into the 2022 ticket), then `tv_close_fg()`. Dark glass here."""
    g = Geometry()
    r(g, 0, 0, 320, 180, 'plaster2'); r(g, 0, 150, 320, 30, 'wood1')
    x0, y0, x1, y1 = TV_CLOSE_SCREEN
    r(g, x0 - 22, y0 - 16, x1 - x0 + 44, y1 - y0 + 32, 'wood0'); r(g, x0 - 21, y0 - 15, x1 - x0 + 42, 1, 'wood2')
    r(g, x0 - 8, y0 - 8, x1 - x0 + 16, y1 - y0 + 16, 'black'); r(g, x0, y0, x1 - x0, y1 - y0, 'blue0')
    r(g, x1 + 10, y0 + 6, 18, 36, 'steel0')
    for k in range(9):
        r(g, x1 + 10, y0 + 6 + k * 4, 18, 1, 'steel1')
    ellipse(g, x1 + 19, y1 - 10, 5, 5, 'steel2'); ellipse(g, x1 + 19, y1 + 4, 5, 5, 'steel2')
    line(g, (160, y0 - 16), (110, 2), .8, 'steel2'); line(g, (160, y0 - 16), (210, 4), .8, 'steel2')
    return g


def tv_close_fg():
    g = Geometry(); x0, y0, x1, y1 = TV_CLOSE_SCREEN
    r(g, x0 - 8, y0 - 8, x1 - x0 + 16, 8, 'black'); r(g, x0 - 8, y1, x1 - x0 + 16, 8, 'black'); r(g, x0 - 8, y0, 8, y1 - y0, 'black'); r(g, x1, y0, 8, y1 - y0, 'black')
    poly(g, [(x0 + 3, y0 + 2), (x0 + 24, y0 + 2), (x0 + 3, y0 + 30)], 'steel1')
    return g


# ============================================================================================ SENATE-PLENARY (blue carpet)
SENADO_SIGN = ('SENADO FEDERAL', (124, 14, 224, 24))        # wall sign (14a); 2016, the Senate
SENADO_SCREEN = (230, 26, 300, 56)                           # side screen on the right wall: dark glass here, the scene builder fills it (61 x 20)
CPI_SIGN = ('CPI DA PANDEMIA', (100, 90, 220, 98))           # table sign (26e); 2021
SENATE_LECTERN_ANCHOR = (160, 118)                           # where the speaker stands (sprite soles) behind the lectern


def _blue_carpet(g, y0):
    r(g, 0, y0, 320, 180 - y0, 'blue1')
    for yy in range(y0, 180, 10):
        for xx in range(((yy - y0) // 10 % 2) * 12, 320, 24):
            poly(g, [(xx + 6, yy), (xx + 12, yy + 5), (xx + 6, yy + 10), (xx, yy + 5)], 'blue0')
    r(g, 0, y0, 320, 2, 'blue2')


def senate_plenary(view='floor', signs=True, screen=True):
    """SENATE-PLENARY, 320x180, BLUE carpet. view: 'floor' (14a: from the floor toward the lectern: SENADO FEDERAL wall sign at
    (124,14,224,24), presiding dais, lectern anchor, the side screen on the right wall at (230,26,300,56) is dark glass for the builder
    to fill) | 'tiers' (14c, the reverse: rows of blue seats rising behind the tribune, no sign) | 'cpi' (26e: committee room, long
    table with the placard CPI DA PANDEMIA at (100,90,220,98)). Foreground pieces: `senate_lectern()`, `senate_desks_fg()`."""
    assert view in ('floor', 'tiers', 'cpi')
    g = Geometry(); rng = random.Random(2016)
    if view == 'floor':
        r(g, 0, 0, 320, 120, 'plaster3'); r(g, 0, 0, 320, 8, 'plaster2')
        r(g, 100, 30, 126, 76, 'wood2')
        for xx in range(100, 226, 12):
            r(g, xx, 30, 1, 76, 'wood1')
        # left wall with two tall windows, right wall (slanted) with the screen
        r(g, 0, 0, 92, 118, 'plaster2'); poly(g, [(92, 0), (100, 0), (100, 108), (92, 118)], 'plaster1')
        for wx in (14, 52):                                                                          # sill 20 rows above the wall base (y 104), top 62 above
            r(g, wx, 42, 24, 42, 'wood0'); r(g, wx + 2, 44, 20, 38, 'glass1'); r(g, wx + 11, 44, 2, 38, 'wood0')
        poly(g, [(226, 0), (320, 0), (320, 120), (226, 106)], 'plaster2'); poly(g, [(226, 0), (229, 0), (229, 106), (226, 106)], 'plaster1')
        sx0, sy0, sx1, sy1 = SENADO_SCREEN
        r(g, sx0 - 3, sy0 - 3, sx1 - sx0 + 6, sy1 - sy0 + 6, 'steel0')
        r(g, sx0, sy0, sx1 - sx0, sy1 - sy0, 'blue0' if screen else 'steel0')
        r(g, 118, 12, 108, 14, 'wood0'); r(g, 119, 13, 106, 12, 'blue0'); r(g, 119, 13, 106, 1, 'blue1')                 # the wall sign's board, over both walls
        if signs:
            _sign_text(g, SENADO_SIGN[0], SENADO_SIGN[1], 'ivory')
        # presiding dais
        r(g, 106, 78, 108, 26, 'wood1'); r(g, 104, 76, 112, 3, 'wood3'); r(g, 106, 79, 108, 1, 'wood0')
        for xx in range(112, 210, 14):
            r(g, xx, 84, 10, 16, 'wood2'); r(g, xx, 84, 10, 1, 'wood3')
        r(g, 150, 56, 20, 22, 'red0'); r(g, 150, 56, 20, 2, 'red1')                                   # the presiding chair
        r(g, 142, 70, 4, 8, 'ivory'); r(g, 174, 70, 4, 8, 'ivory')
        _blue_carpet(g, 104)
        r(g, 0, 104, 320, 1, 'wood0')
        for (x0, w) in ((20, 66), (100, 66), (180, 66), (254, 60)):                                    # a far row of desks
            r(g, x0, 112, w, 7, 'wood2'); r(g, x0, 112, w, 1, 'wood3'); r(g, x0, 119, w, 3, 'wood0')
    elif view == 'tiers':
        r(g, 0, 0, 320, 180, 'plaster3'); r(g, 0, 0, 320, 8, 'plaster2')
        r(g, 0, 8, 320, 24, 'wood2')
        for xx in range(0, 320, 16):
            r(g, xx, 8, 1, 24, 'wood1')
        for k in range(3):                                                                              # three tiers of seats rising to the back
            y = 36 + k * 20
            r(g, 0, y, 320, 20, 'blue0'); r(g, 0, y, 320, 2, 'wood2')
            for xx in range(2 + (k % 2) * 8, 320, 16):
                r(g, xx, y + 4, 12, 9, 'blue1'); r(g, xx, y + 4, 12, 2, 'blue2'); r(g, xx, y + 14, 12, 3, 'wood0')
        _blue_carpet(g, 98)
        r(g, 0, 96, 320, 2, 'wood0')
    else:
        r(g, 0, 0, 320, 106, 'plaster3'); r(g, 0, 0, 320, 8, 'plaster2')
        r(g, 20, 24, 280, 80, 'wood2')
        for xx in range(20, 300, 14):
            r(g, xx, 24, 1, 80, 'wood1')
        ellipse(g, 160, 50, 18, 18, 'gold'); ellipse(g, 160, 50, 14, 14, 'blue0'); ellipse(g, 160, 50, 6, 6, 'gold')    # the seal
        for fx in (60, 260):
            line(g, (fx, 28), (fx, 104), 1, 'wood0'); poly(g, [(fx + 1, 30), (fx + 30, 34), (fx + 28, 60), (fx + 1, 56)], 'green')
        _blue_carpet(g, 106)
        # long committee table across the room, placard standing on it
        r(g, 30, 100, 260, 5, 'wood2'); r(g, 30, 100, 260, 1, 'wood3'); r(g, 30, 105, 260, 36, 'wood1'); r(g, 30, 105, 260, 1, 'wood0')
        for xx in range(34, 290, 28):
            r(g, xx, 110, 22, 26, 'wood2'); r(g, xx, 110, 22, 1, 'wood3')
        r(g, 96, 86, 128, 14, 'wood0'); r(g, 97, 87, 126, 12, 'blue0')
        if signs:
            _sign_text(g, CPI_SIGN[0], CPI_SIGN[1], 'ivory')
        for mx in (56, 78, 242, 264):
            r(g, mx, 94, 2, 6, 'steel1'); r(g, mx - 2, 92, 6, 2, 'steel0'); r(g, mx - 1, 91, 4, 1, 'steel2')          # microphones
        r(g, 40, 98, 4, 6, 'glass2'); r(g, 276, 98, 4, 6, 'glass2')
    return g


def senate_lectern():
    """The speaker's lectern (floor view) / tribune (tiers view) as a foreground piece on the 320x180 canvas; draw after the speaker."""
    g = Geometry()
    poly(g, [(144, 96), (176, 96), (174, 124), (146, 124)], 'wood1'); r(g, 144, 94, 32, 3, 'wood3'); r(g, 148, 100, 24, 20, 'wood2'); r(g, 148, 100, 24, 1, 'wood3')
    r(g, 159, 86, 2, 8, 'steel1'); r(g, 156, 84, 8, 2, 'steel0'); r(g, 158, 83, 4, 1, 'steel2')                  # microphone
    r(g, 154, 108, 12, 6, 'blue0'); r(g, 156, 110, 8, 2, 'gold')
    return g


def senate_desks_fg():
    """Front desks of the senators (floor view): draw after the seated 'back' figures; heads at y ~100-112, desks hide their lower bodies."""
    g = Geometry()
    for (x0, w) in ((10, 90), (116, 88), (222, 90)):
        r(g, x0, 126, w, 6, 'wood2'); r(g, x0, 126, w, 1, 'wood3'); r(g, x0, 132, w, 16, 'wood1'); r(g, x0, 132, w, 1, 'wood0')
        for xx in range(x0 + 6, x0 + w - 16, 26):
            r(g, xx, 136, 18, 9, 'wood2'); r(g, xx + 7, 139, 4, 1, 'gold')
    return g


# ============================================================================================ STF-PLENARY
STF_W = 340                                   # the background is 340 wide: 20 px of margin for the 10 px (20b) and 14 px (29d) pans
STF_PLAQUE = ('AP 2668', (130, 90, 200, 98))   # 29f only (state '2025')
STF_CENTRE = 170


def stf_plenary(state='plain'):
    """STF-PLENARY, 340x180 (pan with a negative x: 20b 0 -> -10, 29d 0 -> -14). Eleven high-back chairs behind a long bench, red
    drapes, tall windows, marble floor. state: 'plain' (20b, no sign) | 'damaged' (29d: four chairs overturned on the floor, one window
    pane broken with its shards, papers on the floor; no sign) | '2025' (29f: restored, plaque AP 2668 at (130,90,200,98) on the
    bench). Pieces: `stf_gavel()`, `stf_bench_fg()` (the bench front: draw after the seated justices)."""
    assert state in ('plain', 'damaged', '2025')
    g = Geometry(); rng = random.Random(2023)
    w = STF_W
    r(g, 0, 0, w, 180, 'plaster3'); r(g, 0, 0, w, 6, 'plaster2')
    for xx in range(6, w, 34):
        r(g, xx, 6, 8, 100, 'ivory'); r(g, xx, 6, 1, 100, 'plaster3'); r(g, xx + 7, 6, 1, 100, 'plaster1')      # pilasters
    r(g, 12, 52, w - 24, 52, 'red0')                                                                       # curtain behind the justices
    for xx in range(14, w - 12, 5):
        r(g, xx, 52, 2, 52, 'red1')
    r(g, 12, 50, w - 24, 3, 'gold')
    for (wx, broken) in ((30, False), (w - 66, state == 'damaged')):
        r(g, wx - 3, 8, 42, 42, 'wood0'); r(g, wx, 11, 36, 36, 'glass1'); r(g, wx, 11, 36, 10, 'glass2'); r(g, wx + 17, 11, 2, 36, 'wood0'); r(g, wx, 28, 36, 2, 'wood0')
        if broken:
            poly(g, [(wx + 20, 12), (wx + 36, 12), (wx + 36, 38), (wx + 28, 30), (wx + 24, 40), (wx + 18, 26)], 'black')          # the missing pane
            for (a, b, c, d) in ((wx + 18, 26, wx + 6, 14), (wx + 18, 26, wx + 8, 38), (wx + 24, 40, wx + 22, 47), (wx + 6, 14, wx + 2, 22)):
                line(g, (a, b), (c, d), .3, 'ivory')                                                      # cracks
    cx = STF_CENTRE
    over = {1, 3, 6, 8} if state == 'damaged' else set()
    for i in range(11):
        x = cx - 5 * 26 + i * 26 - 11
        tall = 6 if i == 5 else 0
        if i in over:
            continue
        r(g, x, 58 - tall, 22, 46 + tall, 'wood0'); r(g, x + 2, 60 - tall, 18, 38 + tall, 'red1'); r(g, x + 2, 60 - tall, 18, 2, 'red2')
        r(g, x + 9, 62 - tall, 4, 30 + tall, 'brick')
        if i == 5:
            r(g, x + 5, 54 - tall + 2, 12, 3, 'gold')
    r(g, 8, 100, w - 16, 5, 'wood2'); r(g, 8, 100, w - 16, 1, 'wood3'); r(g, 8, 105, w - 16, 20, 'wood1'); r(g, 8, 105, w - 16, 1, 'wood0')
    for xx in range(14, w - 20, 30):
        r(g, xx, 109, 24, 12, 'wood2'); r(g, xx, 109, 24, 1, 'wood3')
    for mx in range(cx - 130, cx + 131, 26):                                                               # microphones
        r(g, mx, 94, 2, 6, 'steel1'); r(g, mx - 2, 92, 6, 2, 'steel0')
    # marble floor
    r(g, 0, 125, w, 55, 'steel2'); r(g, 0, 125, w, 2, 'steel1')
    for yy in range(135, 180, 12):
        r(g, 0, yy, w, 1, 'steel1')
    for xx in range(0, w, 30):
        for yy in range(127, 180, 12):
            r(g, xx + ((yy // 12) % 2) * 15, yy, 1, 12, 'steel1')
    _noise(g, rng, 60, 0, 127, w, 178, ['steel3', 'steel1'], 4)
    if state == '2025':
        px0, py0, px1, py1 = STF_PLAQUE[1]
        r(g, px0 - 3, py0 - 3, px1 - px0 + 6, py1 - py0 + 8, 'gold'); r(g, px0 - 2, py0 - 2, px1 - px0 + 4, py1 - py0 + 6, 'blue0')
        _sign_text(g, STF_PLAQUE[0], STF_PLAQUE[1], 'ivory')
        r(g, px0 + 28, py1 + 3, 14, 2, 'wood0')
    if state == 'damaged':
        for k in over:                                                                                     # overturned chairs on the floor
            x = cx - 5 * 26 + k * 26 - 18 + (k % 3) * 6
            y = 140 + (k % 2) * 7
            poly(g, [(x, y), (x + 36, y - 3), (x + 38, y + 12), (x + 2, y + 15)], 'red1'); r(g, x, y, 36, 3, 'wood0'); r(g, x + 36, y - 3, 3, 15, 'wood0')
            r(g, x + 4, y + 11, 32, 4, 'wood0'); line(g, (x + 8, y + 14), (x + 2, y + 24), .6, 'wood1'); line(g, (x + 30, y + 14), (x + 38, y + 22), .6, 'wood1')
        for k in range(18):
            r(g, rng.randrange(40, w - 40), rng.randrange(132, 176), 3, 2, 'ivory')                         # papers and glass
        for k in range(12):
            poly(g, [(w - 52 + rng.randrange(-14, 14), 128 + rng.randrange(0, 40))] * 1 + [(w - 50, 130), (w - 47, 133)], 'glass2')
        r(g, 8, 100, 28, 5, 'wood0'); r(g, cx - 130 + 52, 92, 6, 8, 'steel0')
    return g


def stf_gavel():
    """Gavel and sound block (20b +0.5 lifts, +2.0 taps; 29f +3.4). Geometry origin = block's top-left; place on the bench at the
    president's right hand (x ~ STF_CENTRE + 34, y 96, clear of the plaque)."""
    g = Geometry(); r(g, 0, 4, 14, 3, 'wood0'); r(g, 0, 4, 14, 1, 'wood2')
    r(g, 20, 0, 10, 5, 'wood1')
    return g


def stf_bench_fg(state='plain'):
    """Front of the bench on top of the justices' legs (STF_W wide canvas): draw after the figures. In state '2025' the plaque
    AP 2668 is part of it, so the seated president never hides the sign."""
    g = Geometry(); w = STF_W
    r(g, 8, 100, w - 16, 5, 'wood2'); r(g, 8, 100, w - 16, 1, 'wood3'); r(g, 8, 105, w - 16, 20, 'wood1'); r(g, 8, 105, w - 16, 1, 'wood0')
    for xx in range(14, w - 20, 30):
        r(g, xx, 109, 24, 12, 'wood2'); r(g, xx, 109, 24, 1, 'wood3')
    if state == '2025':
        px0, py0, px1, py1 = STF_PLAQUE[1]
        r(g, px0 - 3, py0 - 3, px1 - px0 + 6, py1 - py0 + 8, 'gold'); r(g, px0 - 2, py0 - 2, px1 - px0 + 4, py1 - py0 + 6, 'blue0')
        _sign_text(g, STF_PLAQUE[0], STF_PLAQUE[1], 'ivory')
        r(g, px0 + 28, py1 + 3, 14, 2, 'wood0')
    return g


# ============================================================================================ MERCEARIA shop front (close)
MERCEARIA_FRONT_SIGN = ('MERCEARIA', (60, 30, 130, 40))            # 08b / 08c awning sign (same shop as the BAIRRO's MERCEARIA_SIGN)
MERCEARIA_WINDOW = (22, 64, 204, 112)
MERCEARIA_DOOR = (214, 62, 250, 118)


def mercearia_front(lamp=True, signs=True, empty=False):
    """The MERCEARIA window in close frontal view (08b lights on then off, 08c lights on, 3 customers enter), 320x180. Dark top strip for
    the plate (y < 27). The shopkeeper stands inside the window (draw him, then `mercearia_front_fg()` = glass glints over him).
    lamp: the pendant lamp is drawn lit (warm pool); the caller swaps to `mercearia_lamp(False)` and draws `mercearia_dark()` with
    opacity .6 when the lamp is switched off (08b +1.2, +2.2). empty: bare shelves."""
    g = Geometry(); rng = random.Random(2009)
    r(g, 0, 0, 320, 180, 'plaster3'); r(g, 0, 0, 320, 27, 'metal0'); r(g, 0, 27, 320, 1, 'metal1')
    r(g, 30, 28, 134, 14, 'green'); r(g, 30, 28, 134, 1, 'metal2'); r(g, 30, 41, 134, 1, 'metal0')
    if signs:
        _sign_text(g, MERCEARIA_FRONT_SIGN[0], MERCEARIA_FRONT_SIGN[1], 'ivory')
    for k in range(0, 134, 8):                                                                       # striped awning under the sign board
        r(g, 30 + k, 42, 8, 12, 'ivory' if k % 16 else 'red1'); r(g, 30 + k, 54, 8, 2, 'red0' if not k % 16 else 'plaster2')
    r(g, 30, 42, 134, 1, 'red0')
    _noise(g, rng, 60, 0, 58, 320, 116, ['plaster2', 'plaster3'], 3)
    r(g, 0, 98, 320, 20, 'plaster2')
    x0, y0, x1, y1 = MERCEARIA_WINDOW
    r(g, x0 - 3, y0 - 3, x1 - x0 + 6, y1 - y0 + 6, 'wood0'); r(g, x0, y0, x1 - x0, y1 - y0, 'plaster2')                    # frame, inner wall
    for sy in (y0 + 12, y0 + 24):                                                                       # shelves along the back wall
        r(g, x0, sy, x1 - x0, 2, 'wood1')
        if not empty:
            for k, gx in enumerate(range(x0 + 3, x1 - 6, 7)):
                col = ['red1', 'gold', 'green', 'ochre', 'cream', 'blue2'][(k + sy) % 6]
                r(g, gx, sy - 6, 5, 6, col); r(g, gx, sy - 6, 5, 1, 'ivory')
    r(g, x0, y1 - 12, x1 - x0, 12, 'wood1'); r(g, x0, y1 - 12, x1 - x0, 2, 'wood3')                                             # counter inside
    r(g, x0 + 150, y1 - 18, 20, 6, 'steel1'); r(g, x0 + 152, y1 - 17, 16, 2, 'ivory')                                           # the scale / till
    r(g, x1 - 24, y0 + 18, 12, 9, 'ivory'); r(g, x1 - 23, y0 + 20, 10, 1, 'steel1'); r(g, x1 - 23, y0 + 23, 7, 1, 'steel1')    # hand-written price card (no readable text)
    r(g, x0, y1, x1 - x0, 6, 'wood1')
    r(g, x1 + 4, y0, 6, y1 - y0, 'wood0')
    dx0, dy0, dx1, dy1 = MERCEARIA_DOOR
    r(g, dx0 - 3, dy0 - 3, dx1 - dx0 + 6, dy1 - dy0 + 3, 'wood0'); r(g, dx0, dy0, dx1 - dx0, dy1 - dy0, 'wood1'); r(g, dx0 + 3, dy0 + 3, dx1 - dx0 - 6, 24, 'glass0'); r(g, dx0 + 3, dy0 + 3, dx1 - dx0 - 6, 7, 'glass1')
    r(g, dx1 - 7, dy0 + 32, 2, 4, 'gold')
    r(g, 0, 118, 320, 28, 'plaster2'); r(g, 0, 118, 320, 1, 'plaster0')
    for xx in range(0, 320, 14):
        r(g, xx, 119, 1, 27, 'plaster1')
    for yy in (126, 134, 142):
        r(g, 0, yy, 320, 1, 'plaster1')
    r(g, 0, 146, 320, 34, 'steel0')
    if lamp:
        g.paste(mercearia_lamp(True), 112, 64)
    else:
        g.paste(mercearia_lamp(False), 112, 64)
    return g


def mercearia_lamp(on=True):
    """The pendant lamp inside the window (origin = its cord's top at the window's top edge, place at (112, 64))."""
    g = Geometry(); r(g, 12, 0, 1, 8, 'steel1')
    if on:
        poly(g, [(9, 10), (15, 10), (22, 30), (2, 30)], 'cream'); ellipse(g, 12, 10, 5, 3, 'gold'); ellipse(g, 12, 10, 3, 2, 'cream')
    else:
        ellipse(g, 12, 10, 5, 3, 'steel1'); ellipse(g, 12, 10, 3, 2, 'steel2')
    return g


def mercearia_dark():
    """A black rectangle over the window interior (draw with opacity ~.6 when the lamp is off). 320x180 canvas."""
    g = Geometry(); x0, y0, x1, y1 = MERCEARIA_WINDOW
    r(g, x0, y0, x1 - x0, y1 - y0, 'black')
    return g


def mercearia_front_fg():
    """Glass glints over the window (and so over the shopkeeper behind it): draw after the figures, 320x180 canvas."""
    g = Geometry(); x0, y0, x1, y1 = MERCEARIA_WINDOW
    for sx in (x0 + 14, x0 + 84, x0 + 130):
        poly(g, [(sx, y0), (sx + 8, y0), (sx - 6, y1), (sx - 14, y1)], 'ivory')
    return g


def mercearia_shutter(frac=1.0):
    """Roll-up shutter that lowers FROM THE TOP over the window and door of `mercearia_front` (frac 0..1; 1 = fully down).
    Returns (Geometry, x, y); driven by the shopkeeper's hand (the caller steps frac and keys the hand)."""
    x0, y0 = 20, 61
    x1, y1 = 254, 118
    h = max(0, round((y1 - y0) * frac)); g = Geometry()
    if h:
        r(g, 0, 0, x1 - x0, h, 'steel1')
        for yy in range(0, h, 3):
            r(g, 0, yy, x1 - x0, 1, 'steel2' if yy % 6 == 0 else 'steel0')
        r(g, 0, h - 2, x1 - x0, 2, 'steel0'); r(g, (x1 - x0) // 2 - 4, h - 4, 8, 2, 'steel3')
    return g, x0, y0


# ============================================================================================ TIMELINE-3
TIMELINE3_CARDS = [(22, 40, 98, 116), (122, 40, 198, 116), (222, 40, 298, 116)]     # 13h: framed icon cards (the icons are the builder's, inside inset 4)
TIMELINE3_ARROWS = [(100, 70, 120, 86), (200, 70, 220, 86)]
TIMELINE3_NUMERALS = {2017: (30, 60, 90, 84), 2018: (130, 60, 190, 84), 2019: (230, 60, 290, 84)}   # 18e sign rectangles
TIMELINE3_ICON_ZONE = (20, 96, 300, 144)


def timeline3_board(kind='cards'):
    """TIMELINE-3 board, 320x180. kind 'cards' (13h): empty dark board with a faint rail; the three card frames and two arrows come as
    pieces (`timeline3_card_frame`, `timeline3_arrow`) so they appear one by one. kind 'years' (18e): the strip behind the big numerals
    (`timeline3_numeral`)."""
    assert kind in ('cards', 'years')
    g = Geometry(); rng = random.Random(13)
    r(g, 0, 0, 320, 180, 'blue0'); _noise(g, rng, 80, 0, 0, 320, 180, ['blue1', 'deep'], 3)
    if kind == 'cards':
        r(g, 10, 124, 300, 2, 'blue1')
        for k, c in enumerate(TIMELINE3_CARDS):
            r(g, (c[0] + c[2]) // 2 - 1, 120, 2, 8, 'blue2')
    else:
        r(g, 12, 56, 296, 32, 'blue1'); r(g, 12, 56, 296, 1, 'blue2'); r(g, 12, 87, 296, 1, 'blue0')
        for xs in (110, 210):
            r(g, xs, 62, 1, 20, 'blue2')
        r(g, 12, 90, 296, 2, 'blue2')
    return g


def timeline3_card_frame(i):
    """Frame of card i (0..2): wood border and cream inner card; returns (Geometry, x, y). The icon is drawn by the caller inside
    (x+4, y+4, x+72, y+72)."""
    x0, y0, x1, y1 = TIMELINE3_CARDS[i]; w, h = x1 - x0, y1 - y0
    g = Geometry(); r(g, 0, 0, w, h, 'wood0'); r(g, 1, 1, w - 2, h - 2, 'wood2'); r(g, 3, 3, w - 6, h - 6, 'wood0'); r(g, 4, 4, w - 8, h - 8, 'ivory')
    r(g, 4, 4, w - 8, 1, 'cream'); r(g, 1, 1, w - 2, 1, 'wood3')
    return g, x0, y0


def timeline3_arrow(i):
    """Arrow i (0: card 1 -> 2, 1: card 2 -> 3): returns (Geometry, x, y)."""
    x0, y0, x1, y1 = TIMELINE3_ARROWS[i]; w, h = x1 - x0, y1 - y0
    g = Geometry(); r(g, 0, h // 2 - 2, w - 8, 4, 'gold'); poly(g, [(w - 9, 0), (w, h // 2), (w - 9, h)], 'gold'); r(g, 0, h // 2 - 2, w - 8, 1, 'cream')
    return g, x0, y0


def timeline3_numeral(year):
    """Big numeral of 18e (2017, 2018, 2019) drawn at 2x inside its sign rectangle `TIMELINE3_NUMERALS[year]`; returns
    (Geometry, x, y). The same rectangle is what `ctx.sign(str(year), rect)` declares."""
    x0, y0, x1, y1 = TIMELINE3_NUMERALS[year]
    q, w = lettering(str(year), 'ivory'); q = resize(q, 2)
    g = Geometry(); g.paste(q, 0, 0)
    return g, x0 + (x1 - x0 - 2 * w) // 2, y0 + (y1 - y0 - 14) // 2


# ============================================================================================ CÂMARA DOS DEPUTADOS (green carpet)
CAMARA_W = 340                                            # the picture is 340 wide: 20 px of margin for the 8 px drift of 29c and any pan
CAMARA_SIGN = ('CÂMARA DOS DEPUTADOS', (100, 14, 220, 24))   # wall sign of the 'dais' view (13b, 13f partly in frame; plan rectangle)
CAMARA_SEAT = (150, 54)                                   # sprite origin of the president, seated ('sit' pose, seat line y+34 = 88); the table front hides the legs
CAMARA_CLERK_SEAT = (204, 54)                             # a second seat at his right (13f: the clerk takes the paper)
CAMARA_LIGHTS = [(50, 3, 40, 6), (150, 3, 40, 6), (250, 3, 40, 6)]   # ceiling light panels of the 'plenary' view (x, y, w, h); 29c flickers the middle one
CAMARA_ROW_BASES = (110, 127, 144)                        # foot lines of the three seat rows of the 'plenary' view (figures walk between them: soles <= 145)
CAMARA_ROW_CHAIR = ((13, 18), (15, 21), (16, 24))         # chair (width, height) per row: the far rows are smaller, the near row is life size (24 rows = 0.85 m)
CAMARA_STATES = ('plain', 'damaged', 'bare')


def _camara_slots():
    out = []
    for i, b in enumerate(CAMARA_ROW_BASES):
        for k in range(12):
            step = (22, 24, 26)[i]
            x = 14 + step * k + (i % 2) * 6
            if abs(x + 8 - 170) < 16 or x > 306:
                continue                                   # the centre aisle
            out.append((x, b))
    return out


CAMARA_SLOTS = _camara_slots()                              # (x, foot) of every chair, upright chair = 16 wide, 24 tall above the foot
def _pick(row, idx):
    q = [s for s in CAMARA_SLOTS if s[1] == CAMARA_ROW_BASES[row]]
    return [q[k % len(q)] for k in idx]


CAMARA_EMPTY_SLOTS = sorted(set(_pick(2, (1, 3, 6, 8)) + _pick(1, (2, 5, 7)) + _pick(0, (3, 8))), key=lambda s: (s[1], s[0]))   # nine chairs thrown down (29c) / missing until the staff put them back (29h)
CAMARA_NEAR_EMPTY = [q for q in CAMARA_EMPTY_SLOTS if q[1] == CAMARA_ROW_BASES[2]]   # those on the near row: the chairs the staff carry (life size)
CAMARA_CHAIR_SIZE = (16, 24)                                # the near-row chair; `camara_chair(row=2)`


def _green_carpet(g, y0, w, dark=False, y1=180):
    base, dia, edge = ('metal1', 'metal0', 'metal2') if dark else ('v3_leaf', 'green', 'v3_leaf2')
    r(g, 0, y0, w, y1 - y0, base)
    for yy in range(y0, y1, 10):
        for xx in range(((yy - y0) // 10 % 2) * 12, w, 24):
            poly(g, [(xx + 6, yy), (xx + 12, yy + 5), (xx + 6, yy + 10), (xx, yy + 5)], dia)
    r(g, 0, y0, w, 2, edge)


def _brazil_flag(g, x, y, w=28, h=21):
    poly(g, [(x + 1, y), (x + w, y + 3), (x + w - 2, y + h), (x + 1, y + h - 3)], 'green')
    poly(g, [(x + 4, y + 10), (x + w // 2, y + 3), (x + w - 5, y + 11), (x + w // 2 - 1, y + h - 4)], 'gold')
    ellipse(g, x + w // 2, y + 10, 4, 4, 'blue0')


def _camara_chair(g, x, b, upright=True, variant=0, row=2):
    """Plenary chair seen from behind: width/height by row (`CAMARA_ROW_CHAIR`), foot line b. Overturned: legs up (variant 0) or on its side (variant 1)."""
    w, h = CAMARA_ROW_CHAIR[row]
    if upright:
        r(g, x, b - h, w, h - 7, 'steel1'); r(g, x + 1, b - h - 1, w - 2, 1, 'steel1'); r(g, x, b - h, w, 1, 'steel2')
        r(g, x, b - h, 1, h - 7, 'steel0'); r(g, x + w - 1, b - h, 1, h - 7, 'steel0'); r(g, x + w // 2 - 1, b - h + 2, 2, h - 11, 'steel0')
        r(g, x - 1, b - 7, w + 2, 4, 'wood0'); r(g, x - 1, b - 7, w + 2, 1, 'wood2'); r(g, x + 1, b - 3, 2, 3, 'wood0'); r(g, x + w - 3, b - 3, 2, 3, 'wood0')
    elif variant == 0:
        r(g, x, b - 4, w + 2, 6, 'steel1'); r(g, x, b - 4, w + 2, 1, 'steel2'); r(g, x - 1, b - 10, w + 4, 4, 'wood0')
        r(g, x + 2, b - 20, 2, 10, 'wood0'); r(g, x + w - 2, b - 20, 2, 10, 'wood0')
    else:
        r(g, x, b - 6, w + 8, 10, 'steel1'); r(g, x, b - 6, w + 8, 1, 'steel2'); r(g, x + w + 6, b - 14, 4, 18, 'wood0')
        r(g, x + 1, b - 14, 2, 8, 'wood0'); r(g, x + 12, b - 14, 2, 8, 'wood0')


def camara_chair(state='upright', variant=0):
    """One near-row plenary chair as a piece (origin top-left, 16 x 24 upright; overturned about 24 x 20) so the staff of 29h can carry it and set
    it down on a slot `(x, foot)` of `CAMARA_EMPTY_SLOTS` (place at (x, foot - 24) for a near-row slot; far rows are smaller, scale is the builder's
    to match by choosing slots of the near row for the carried pieces, `CAMARA_NEAR_EMPTY`)."""
    g = Geometry(); _camara_chair(g, 1 if state == 'upright' else 0, 24 if state == 'upright' else 20, state == 'upright', variant, 2)
    return g


def _camara_dais_back(g, w, signs):
    r(g, 0, 0, w, 180, 'plaster3')
    r(g, 0, 0, w, 10, 'wood1'); r(g, 0, 10, w, 2, 'wood0')
    for xx in range(0, w, 20):
        r(g, xx, 0, 1, 10, 'wood0')
    r(g, 60, 12, 200, 92, 'plaster2'); r(g, 60, 12, 200, 2, 'plaster1')
    for xx in range(60, 260, 20):
        r(g, xx, 14, 1, 90, 'plaster1')
    r(g, 96, 11, 128, 16, 'wood0'); r(g, 97, 12, 126, 14, 'blue0'); r(g, 97, 12, 126, 1, 'blue1')           # the wall sign's board
    if signs:
        _sign_text(g, CAMARA_SIGN[0], CAMARA_SIGN[1], 'ivory')
    ellipse(g, 160, 38, 9, 9, 'gold'); ellipse(g, 160, 38, 6, 6, 'blue0'); ellipse(g, 160, 38, 2, 2, 'gold')    # the national arms, behind the president's chair
    for fx in (34, 286):
        line(g, (fx, 56), (fx, 104), 1, 'wood0'); _brazil_flag(g, fx + 1, 57)
    for sx in (18, 322):
        r(g, sx, 42, 6, 12, 'steel1'); r(g, sx + 1, 43, 4, 9, 'cream'); r(g, sx - 1, 40, 8, 3, 'steel0')
    r(g, 0, 104, w, 8, 'wood2'); r(g, 0, 104, w, 1, 'wood3'); r(g, 0, 111, w, 1, 'wood0')                   # the dais platform, one step
    _green_carpet(g, 112, w)
    for cx, top in ((112, 56), (208, 56), (160, 44)):                                                       # the high chairs behind the table
        r(g, cx - 12, top, 24, 88 - top, 'metal1'); r(g, cx - 10, top + 2, 20, 88 - top - 2, 'metal2'); r(g, cx - 12, top, 24, 2, 'wood0')


def _camara_plenary(g, w, state):
    r(g, 0, 0, w, 180, 'plaster3')
    r(g, 0, 0, w, 16, 'wood1'); r(g, 0, 16, w, 2, 'wood0')
    for (lx, ly, lw, lh) in CAMARA_LIGHTS:
        r(g, lx - 1, ly - 1, lw + 2, lh + 2, 'wood0'); r(g, lx, ly, lw, lh, 'cream'); r(g, lx, ly, lw, 1, 'ivory')
        for xx in range(lx + 8, lx + lw, 8):
            r(g, xx, ly, 1, lh, 'wood2')
    for xx in range(0, w, 30):
        r(g, xx, 8, 1, 8, 'wood0')
    for side in (0, 1):                                                                                      # side galleries with a rail
        gx = 0 if side == 0 else w - 70
        r(g, gx, 24, 70, 36, 'wood0'); r(g, gx + 2, 26, 66, 22, 'plaster0')
        r(g, gx, 48, 70, 3, 'wood3'); r(g, gx, 51, 70, 1, 'wood0')
        for xx in range(gx + 3, gx + 68, 6):
            r(g, xx, 52, 2, 8, 'wood2')
    r(g, 100, 20, 140, 70, 'plaster2'); r(g, 100, 20, 140, 2, 'plaster1')
    for xx in range(100, 240, 20):
        r(g, xx, 22, 1, 68, 'plaster1')
    ellipse(g, 170, 36, 7, 7, 'gold'); ellipse(g, 170, 36, 5, 5, 'blue0'); ellipse(g, 170, 36, 2, 2, 'gold')
    for fx in (92, 248):
        line(g, (fx, 40), (fx, 92), 1, 'wood0'); _brazil_flag(g, fx + 1, 41, 22, 16)
    r(g, 0, 92, w, 4, 'wood2'); r(g, 0, 92, w, 1, 'wood3')                                                   # dais edge
    _green_carpet(g, 96, w)
    r(g, 120, 66, 100, 4, 'wood3'); r(g, 120, 70, 100, 17, 'wood1'); r(g, 122, 73, 96, 12, 'wood2'); r(g, 120, 87, 100, 5, 'wood0')   # presidency table, far
    for cx in (140, 170, 200):
        r(g, cx - 8, 48, 16, 18, 'metal1'); r(g, cx - 8, 48, 16, 2, 'wood0')
    # chair rows, far to near
    empty = set(CAMARA_EMPTY_SLOTS)
    rng = random.Random(29)
    for i, b in enumerate(CAMARA_ROW_BASES):
        for (x, bb) in [s for s in CAMARA_SLOTS if s[1] == b]:
            if (x, bb) in empty and state != 'plain':
                if state == 'damaged':
                    _camara_chair(g, x + rng.randrange(-3, 6), b + rng.randrange(-1, 3), upright=False, variant=rng.randrange(2), row=i)
                continue
            _camara_chair(g, x, b, row=i)
    if state == 'damaged':
        lx, ly, lw, lh = CAMARA_LIGHTS[1]                                                                     # a ceiling panel hangs by one corner, its wire cut
        r(g, lx - 1, ly - 1, lw + 2, lh + 2, 'wood1'); r(g, lx, ly, lw, lh, 'wood0')
        poly(g, [(lx, ly), (lx + lw, ly), (lx + lw - 6, ly + 20), (lx - 8, ly + 16)], 'wood0'); poly(g, [(lx + 2, ly + 1), (lx + lw - 2, ly + 1), (lx + lw - 7, ly + 17), (lx - 6, ly + 14)], 'cream')
        line(g, (lx + lw, ly + 6), (lx + lw - 4, ly + 20), .5, 'black')
        for _ in range(26):                                                                                  # papers and glass on the carpet
            r(g, rng.randrange(8, w - 40), rng.randrange(100, 150), rng.randrange(2, 5), 2, rng.choice(['ivory', 'ivory', 'cream', 'glass2']))
        for _ in range(8):
            r(g, rng.randrange(60, 280), rng.randrange(104, 148), 1, 1, 'glass2')
        poly(g, [(w - 70, 52), (w - 40, 52), (w - 34, 60), (w - 70, 60)], 'wood0')                            # the gallery rail broken: a gap
        r(g, w - 58, 51, 14, 9, 'wood0')
        r(g, 134, 69, 10, 8, 'black'); line(g, (140, 66), (150, 80), .6, 'steel0')                            # a microphone torn off the presidency table


def _camara_corridor(g, w):
    r(g, 0, 0, w, 180, 'plaster3'); r(g, 0, 0, w, 10, 'plaster2'); r(g, 0, 10, w, 2, 'plaster1')
    r(g, 0, 90, w, 28, 'wood1'); r(g, 0, 90, w, 2, 'wood3')
    for xx in range(10, w, 30):
        r(g, xx, 95, 22, 18, 'wood2'); r(g, xx, 95, 22, 1, 'wood3')
    for dx in (36, 156, 276):                                                                                # three doors, 28 x 60
        r(g, dx - 3, 55, 34, 63, 'wood0'); r(g, dx, 58, 28, 60, 'wood1'); r(g, dx + 3, 61, 22, 22, 'wood2'); r(g, dx + 3, 86, 22, 28, 'wood2'); r(g, dx + 22, 84, 3, 4, 'gold')
    for sx in (96, 216):
        r(g, sx, 62, 8, 11, 'steel1'); r(g, sx + 1, 63, 6, 9, 'cream'); r(g, sx - 1, 60, 10, 3, 'steel0')
    r(g, 0, 118, w, 62, 'steel2'); r(g, 0, 118, w, 2, 'steel1')
    for yy in range(130, 180, 12):
        r(g, 0, yy, w, 1, 'steel1')
    for xx in range(0, w, 30):
        for yy in range(120, 180, 12):
            r(g, xx + ((yy // 12) % 2) * 15, yy, 1, 12, 'steel1')
    _noise(g, random.Random(13), 50, 0, 120, w, 178, ['steel3', 'steel1'], 4)
    r(g, 70, 118, 200, 62, 'v3_leaf'); r(g, 70, 118, 200, 2, 'v3_leaf2'); r(g, 70, 118, 2, 62, 'green'); r(g, 268, 118, 2, 62, 'green')   # the green runner
    for px in (84, 140, 196, 252):                                                                           # stanchions and the press rope
        r(g, px, 96, 2, 36, 'gold'); ellipse(g, px + 1, 95, 2, 2, 'gold'); r(g, px - 3, 132, 8, 2, 'steel0')
    for (xa, xb) in ((86, 140), (142, 196), (198, 252)):
        line(g, (xa, 99), ((xa + xb) // 2, 106), .6, 'red1'); line(g, ((xa + xb) // 2, 106), (xb, 99), .6, 'red1')


def camara(view='dais', state='plain', signs=True):
    """CÂMARA DOS DEPUTADOS, 340 x 180 (pan with a negative x), GREEN carpet. A different room from the Senate: marble backdrop with the national
    arms, flags both sides, wood ceiling with light panels; the dais table is the foreground piece `camara_dais_fg()`.
    view: 'dais' (13b, 13f: frontal on the presidency table; sign `CAMARA_SIGN` (100,14,220,24); the president sits at `CAMARA_SEAT`, a clerk at
    `CAMARA_CLERK_SEAT`) | 'plenary' (29c, 29h: wide from the floor, three rows of chairs, ceiling light panels `CAMARA_LIGHTS`, no sign) |
    'corridor' (13g: press pen of the Câmara, stanchions and rope, no sign).
    state (plenary only): 'plain' (every chair in place) | 'damaged' (29c: nine chairs thrown down at `CAMARA_EMPTY_SLOTS`, a ceiling panel
    hanging, papers and glass, a torn microphone, broken gallery rail) | 'bare' (29h start: the nine slots EMPTY and clean; the staff carry
    `camara_chair()` to them). signs=False draws the board blank."""
    assert view in ('dais', 'plenary', 'corridor') and state in CAMARA_STATES
    g = Geometry(); w = CAMARA_W
    if view == 'dais':
        _camara_dais_back(g, w, signs)
    elif view == 'plenary':
        _camara_plenary(g, w, state)
    else:
        _camara_corridor(g, w)
    return g


def camara_dais_fg():
    """Presidency table of the 'dais' view (340 x 180 canvas): top at y 80, front down to the platform line y 104 (24 rows). Draw AFTER the seated
    figures. Carries the name plaque (blank brass) at (150,86) and two microphones."""
    g = Geometry()
    r(g, 66, 79, 188, 5, 'wood3'); r(g, 66, 79, 188, 1, 'ivory'); r(g, 66, 84, 188, 20, 'wood1'); r(g, 66, 84, 188, 1, 'wood0')
    for xx in range(72, 250, 30):
        r(g, xx, 88, 24, 12, 'wood2'); r(g, xx, 88, 24, 1, 'wood3')
    r(g, 150, 86, 20, 5, 'gold'); r(g, 150, 86, 20, 1, 'ivory')
    for mx in (128, 192):
        r(g, mx, 72, 2, 7, 'steel1'); r(g, mx - 2, 70, 6, 2, 'steel0'); r(g, mx - 1, 69, 4, 1, 'steel2')
    r(g, 66, 103, 188, 1, 'wood0')
    return g


def camara_dim():
    """Full-canvas black veil for the flicker of 29c (+0.5): draw over everything with opacity ~ .35 for 2-3 frames."""
    g = Geometry(); r(g, 0, 0, CAMARA_W, 180, 'black'); return g


CAMARA_PRESS_MIC = (232, 100)                                  # 13g: where the press microphone cluster stands (foot point); piece below, origin top-left


def camara_press_mics():
    """A stand with three press microphones (13g). Origin top-left, 14 x 22; place at (CAMARA_PRESS_MIC[0] - 7, CAMARA_PRESS_MIC[1] - 22 + 22)."""
    g = Geometry(); r(g, 6, 8, 2, 14, 'steel0'); r(g, 3, 20, 8, 2, 'steel0')
    for (mx, my) in ((0, 2), (5, 0), (10, 2)):
        r(g, mx, my, 3, 7, 'black'); r(g, mx, my, 3, 1, 'steel2')
    r(g, 2, 8, 10, 1, 'steel1')
    return g

# ------------------------------------------------------------------------------------- CONSELHO DE ÉTICA (small committee room)
CONSELHO_SIGN = ('CONSELHO DE ÉTICA', (105, 16, 215, 24))     # wall plaque of the 'room' view (13c; plan rectangle)
CONSELHO_PT_SIGN = ('PT', (150, 108, 170, 116))                # nameplate on the table of the 'reverse' view (13e; plan rectangle)
CONSELHO_SEATS = [(100, 84), (150, 84), (200, 84)]            # 'room' view: sprite origins (seat line y+34 = 118, chair foot 134) of the three members seen from behind
CONSELHO_REVERSE = dict(mic=(108, 70), seats=[(94, 68), (196, 68), (242, 68)])   # 'reverse' view: the speaker's origin at the microphone, three seated members (feet hidden by `conselho_table_fg('reverse')`)


def _conselho_chair_back(g, cx, top, bot):
    r(g, cx - 9, top, 18, bot - top, 'metal1'); r(g, cx - 8, top + 1, 16, bot - top - 1, 'metal2'); r(g, cx - 9, top, 18, 2, 'wood0')


def conselho_etica(view='room', signs=True):
    """CONSELHO DE ÉTICA, 320 x 180: a SMALL, DARK committee room (low wood ceiling, two pendant lamps, dark panelling, dark green carpet), nothing
    like the Câmara's marble dais. view: 'room' (13c: wall plaque `CONSELHO_SIGN` (105,16,215,24); a horseshoe table of nine chairs (three at the open
    end seen from behind, four at the bar, one at each arm); the three members of the plan sit at `CONSELHO_SEATS`; draw `conselho_table_fg('room')`
    after them) | 'reverse' (13e: the other side: a plain dark wall (x 6-110, y 6-66 left free for the TL plate), the table bar across the room
    with the nameplate PT at `CONSELHO_PT_SIGN` (150,108,170,116) and a microphone; `CONSELHO_REVERSE` anchors; draw `conselho_table_fg('reverse')`)."""
    assert view in ('room', 'reverse')
    g = Geometry(); rng = random.Random(2015)
    r(g, 0, 0, 320, 180, 'plaster0'); r(g, 0, 0, 320, 10, 'wood0'); r(g, 0, 10, 320, 2, 'wood1')
    for xx in range(0, 320, 16):
        r(g, xx, 0, 1, 10, 'umber')
    _noise(g, rng, 60, 0, 12, 320, 60, ['plaster1', 'wood1'], 3)
    r(g, 0, 78, 320, 40, 'wood1'); r(g, 0, 78, 320, 2, 'wood2'); r(g, 0, 116, 320, 2, 'wood0')                 # dark panelling
    for xx in range(4, 320, 24):
        r(g, xx, 84, 18, 28, 'wood0'); r(g, xx, 84, 18, 1, 'wood2')
    _green_carpet(g, 118, 320, dark=True)
    for sx in ((90, 230) if view == 'room' else (230,)):                                                    # pendant lamps (none in the TL plate zone of 13e)
        r(g, sx, 10, 1, 8, 'steel0'); poly(g, [(sx - 7, 24), (sx + 8, 24), (sx + 4, 17), (sx - 3, 17)], 'wood0'); r(g, sx - 6, 24, 13, 2, 'gold')
    if view == 'room':
        r(g, 101, 13, 118, 16, 'wood0'); r(g, 102, 14, 116, 14, 'blue0'); r(g, 102, 14, 116, 1, 'blue1')           # the plaque
        if signs:
            _sign_text(g, CONSELHO_SIGN[0], CONSELHO_SIGN[1], 'ivory')
        line(g, (46, 30), (46, 108), 1, 'wood0'); _brazil_flag(g, 47, 31, 26, 19)
        r(g, 262, 34, 28, 22, 'wood0'); r(g, 264, 36, 24, 18, 'plaster3'); ellipse(g, 276, 45, 5, 6, 'skin1')       # a framed portrait
        # horseshoe: bar at the far wall, arms toward the camera; the open end is where the three members sit
        for cx in (100, 140, 180, 220):
            _conselho_chair_back(g, cx, 40, 72)
        for cx in (50, 270):
            _conselho_chair_back(g, cx, 70, 100)
        r(g, 70, 70, 180, 5, 'wood3'); r(g, 70, 70, 180, 1, 'ivory'); r(g, 70, 75, 180, 17, 'wood2'); r(g, 70, 75, 180, 1, 'wood3'); r(g, 70, 91, 180, 1, 'wood0')   # the bar
        for ax in (58, 240):                                                                                   # the two arms come toward the camera
            r(g, ax, 74, 22, 34, 'wood3'); r(g, ax, 74, 22, 1, 'ivory'); r(g, ax, 108, 22, 5, 'wood2'); r(g, ax, 112, 22, 1, 'wood0')
        for xx in (96, 140, 180, 224):
            r(g, xx, 62, 2, 8, 'steel1'); r(g, xx - 2, 60, 6, 2, 'steel0')                                      # a microphone for every bar chair
        for xx in (100, 224):
            r(g, xx, 71, 14, 3, 'ivory')                                                                        # blank nameplates
        for cx in (110, 160, 210):                                                                            # the open end: the three near chairs, backs to the camera
            r(g, cx - 9, 100, 18, 28, 'metal1'); r(g, cx - 8, 101, 16, 26, 'metal2'); r(g, cx - 9, 100, 18, 2, 'wood0')
    else:
        r(g, 150, 30, 110, 40, 'wood0'); r(g, 152, 32, 106, 36, 'plaster1')                                   # a large framed map on the right half
        r(g, 160, 40, 46, 20, 'green'); r(g, 214, 38, 36, 26, 'blue2')
        line(g, (292, 28), (292, 112), 1, 'wood0'); _brazil_flag(g, 293, 29, 24, 18)
        for cx in (104, 150, 206, 252):
            _conselho_chair_back(g, cx, 64, 98)
    return g


def conselho_table_fg(view='room'):
    """The horseshoe table / bar as a foreground piece (320 x 180 canvas), 22 rows from top front edge to foot: draw AFTER the seated figures.
    'room': bar y 82-104 with two side arms; 'reverse': the bar across the room, top surface y 104-114, front y 114-136, nameplate PT (blank
    here: the caller draws `ctx.sign('PT', CONSELHO_PT_SIGN[1])`; the plate itself is drawn by the set at the rectangle) and a microphone."""
    assert view in ('room', 'reverse')
    g = Geometry()
    if view == 'room':
        return g                                                                                              # the whole horseshoe is in the background: the members sit in front of it
    else:
        r(g, 40, 104, 240, 10, 'wood3'); r(g, 40, 104, 240, 1, 'ivory'); r(g, 40, 114, 240, 22, 'wood2'); r(g, 40, 114, 240, 1, 'wood3'); r(g, 40, 135, 240, 1, 'wood0')
        for xx in range(48, 270, 32):
            r(g, xx, 118, 26, 14, 'wood1'); r(g, xx, 118, 26, 1, 'wood3')
        x0, y0, x1, y1 = CONSELHO_PT_SIGN[1]                                                                   # the tent nameplate
        r(g, x0 - 2, y0 - 1, x1 - x0 + 4, y1 - y0 + 2, 'wood0'); r(g, x0 - 1, y0, x1 - x0 + 2, y1 - y0, 'ivory'); _sign_text(g, CONSELHO_PT_SIGN[0], CONSELHO_PT_SIGN[1], 'black')
        mx = 118                                                                                                # the speaker's microphone
        r(g, mx, 90, 2, 14, 'steel1'); r(g, mx - 3, 88, 8, 2, 'steel0'); r(g, mx - 1, 86, 4, 2, 'steel2')
        r(g, 210, 100, 2, 4, 'steel1'); r(g, 208, 98, 6, 2, 'steel0'); r(g, 70, 100, 2, 4, 'steel1'); r(g, 68, 98, 6, 2, 'steel0')
    return g



# ============================================================================================ exterior helpers (Planalto, Congress, STF, esplanade)
def _lawn(g, w, y0, y1, seed=7):
    r(g, 0, y0, w, y1 - y0, 'v3_leaf'); r(g, 0, y0, w, 1, 'v3_leaf2')
    _noise(g, random.Random(seed), w // 6, 0, y0 + 1, w, y1, ['green', 'v3_leaf2'], 4)


def _plaza(g, w, y0, y1=146, seed=9):
    """Paved square: pale slabs with joints, a kerb and the road below."""
    r(g, 0, y0, w, y1 - y0, 'plaster3'); r(g, 0, y0, w, 1, 'ivory')
    for yy in range(y0 + 8, y1, 9):
        r(g, 0, yy, w, 1, 'plaster2')
    for xx in range(0, w, 16):
        for yy in range(y0, y1, 18):
            r(g, xx + (yy // 18 % 2) * 8, yy, 1, 9, 'plaster2')
    _noise(g, random.Random(seed), w // 5, 0, y0 + 1, w, y1, ['plaster2', 'plaster1'], 4)
    r(g, 0, y1, w, 3, 'plaster1'); r(g, 0, y1, w, 1, 'ivory'); r(g, 0, y1 + 3, w, 180 - y1 - 3, 'steel0')
    for xx in range(0, w, 38):
        r(g, xx, 163, 17, 2, 'plaster3')


def _col_poly(g, x, top, base, cw, c='ivory'):
    """One of the Planalto's curved columns (the Alvorada profile): wide head, narrow waist, flaring foot."""
    H = base - top
    pts = [(x, top), (x + cw, top), (x + cw * .55, top + H * .36), (x + cw * .45, top + H * .72), (x + cw * 1.5, base), (x + cw * .7, base), (x - cw * .1, top + H * .76), (x - cw * .1, top + H * .36)]
    poly(g, [(round(a), round(b)) for a, b in pts], c)
    line(g, (round(x + cw - 1), top + 1), (round(x + cw * .5), round(top + H * .36)), .5, 'plaster3')


def _planalto_building(g, x0, x1, top, base, cols, mull=9):
    """The palace's front: roof slab, glass band with mullions, curved columns at the x positions in `cols`. Returns the glass bays (x, y, w, h) for lit windows."""
    H = base - top
    r(g, x0, top, x1 - x0, max(5, H // 8), 'ivory'); r(g, x0, top + max(5, H // 8), x1 - x0, 2, 'plaster3')
    gy0, gy1 = top + max(5, H // 8) + 3, base - 4
    r(g, x0 + 3, gy0, x1 - x0 - 6, gy1 - gy0, 'glass0'); r(g, x0 + 3, gy0, x1 - x0 - 6, 2, 'glass2')
    bays = []
    for xx in range(x0 + 3, x1 - 3, mull):
        r(g, xx, gy0, 1, gy1 - gy0, 'steel1')
        bays.append((xx + 2, gy0 + 4, max(2, mull // 2), (gy1 - gy0) // 2))
    r(g, x0, base - 4, x1 - x0, 4, 'plaster3'); r(g, x0, base - 4, x1 - x0, 1, 'ivory')
    cw = max(5, round(11 * H / 61))
    for cx in cols:
        _col_poly(g, cx, top, base - 3, cw)
    return bays


def _lit(g, rects, col='gold', every=1):
    for k, (x, y, w, h) in enumerate(rects):
        if k % every == 0:
            r(g, x, y, w, h, col)


def _ext_finish(g, time, sky, lit=None):
    """Grade everything except the sky for dusk/night, then draw the lit windows (`lit`: list of rect lists) at full colour."""
    if time in ('dusk', 'night', 'golden'):
        _grade_keep_sky(g, time, sky)
    if time in ('dusk', 'night') and lit:
        for rects, col, every in lit:
            _lit(g, rects, col, every)
    return g


# --------------------------------------------------------------------------------------------- shared life pieces (flag, pigeon, guard)
def three_powers_flag(frame=0, w=24, h=16):
    """The national flag cloth waving, 4 frames (0-3), origin = top-left at the mast; the mast belongs to the set. Frame-cycle it at 6-8 fps.
    24 x 16 by default (use w=18, h=12 for the small flags of the row)."""
    import math
    g = Geometry(); ph = frame % 4 * math.pi / 2
    tops = []; bots = []
    for i in range(0, w + 1, max(2, w // 8)):
        o = round(1.6 * math.sin(i / 5.0 - ph) * i / w)
        tops.append((i, o)); bots.append((i, h + o))
    poly(g, [(a, b) for a, b in tops] + [(a, b) for a, b in reversed(bots)], 'green')
    mo = round(1.6 * math.sin(w / 2 / 5.0 - ph) * .5)
    cx, cy = w // 2, h // 2 + mo
    poly(g, [(cx - w // 2 + 3, cy), (cx, cy - h // 2 + 2), (cx + w // 2 - 3, cy), (cx, cy + h // 2 - 2)], 'gold')
    ellipse(g, cx, cy, max(2, h // 5), max(2, h // 5), 'blue0')
    return g


def three_powers_pigeon(frame=0):
    """A pigeon, 3 frames: 0 perched/walking, 1 wings up, 2 wings down; 7 x 6, origin top-left; face left. Cross the frame in frames 1-2 alternating (about 8 fps), land with frame 0."""
    g = Geometry()
    r(g, 1, 3, 5, 2, 'steel1'); r(g, 0, 2, 2, 2, 'steel0'); r(g, 5, 4, 2, 1, 'steel0'); r(g, 1, 3, 5, 1, 'steel2')
    if frame == 1:
        poly(g, [(3, 3), (5, 3), (6, 0), (2, 0)], 'steel2')
    elif frame == 2:
        poly(g, [(2, 4), (5, 4), (6, 6), (1, 6)], 'steel2')
    else:
        r(g, 2, 3, 3, 1, 'steel0'); r(g, 2, 5, 1, 1, 'clay'); r(g, 4, 5, 1, 1, 'clay')
    return g


def guard_silhouette(size='far', pose=0):
    """A guard in dark uniform and cap as a flat silhouette, origin = top-left, sole at the bottom row. size 'far' 5 x 14 (the row of the Three Powers,
    beside a door or on the ramp) | 'near' 9 x 26 (the Planalto ramp / doors of 28d, 29b). pose 0 standing, 1 one step (alternate for a slow patrol)."""
    g = Geometry()
    if size == 'far':
        r(g, 1, 0, 3, 1, 'black'); r(g, 1, 1, 3, 2, 'skin0'); r(g, 0, 3, 5, 6, 'f2_char1'); r(g, 1, 9, 1, 5 - pose, 'black'); r(g, 3, 9, 1, 5, 'black'); r(g, 2 + pose, 13, 2, 1, 'black')
    else:
        r(g, 2, 0, 5, 2, 'black'); r(g, 3, 2, 3, 4, 'skin0'); r(g, 1, 6, 7, 11, 'f2_char1'); r(g, 0, 7, 1, 8, 'f2_char1'); r(g, 8, 7, 1, 8, 'f2_char1'); r(g, 4, 6, 1, 6, 'gold')
        r(g, 2, 17, 2, 9 - pose, 'black'); r(g, 5, 17, 2, 9, 'black'); r(g, 1 + 2 * pose, 25, 3, 1, 'black')
    return g


# ============================================================================================ PLANALTO (ramp, doors, foot)
PLANALTO_W = 320
PLANALTO_RAMP_PATH = [(222, 144), (169, 108)]                # soles of someone climbing the ramp (07d, 28d): bottom -> top; slope 1.44 px right per row
PLANALTO_RAMP_TOP = (169, 108)
PLANALTO_FLAGS = [(121, 28), (216, 28)]                       # top-left of the flag cloth on each mast (`three_powers_flag(frame)` pieces; `flags=False` leaves bare masts)
PLANALTO_CROWD_BANDS = [dict(x0=2, x1=138, rows=(118, 140)), dict(x0=246, x1=318, rows=(118, 140))]   # where the crowd of 07d / 28d stands (both sides of the ramp, soles of the two rows)
PLANALTO_DOOR_FRAME = (96, 38, 224, 118)                      # the entrance of the 'doors' view
PLANALTO_DOOR_LEAVES = {'L': (128, 42, 160, 118), 'R': (160, 42, 192, 118)}   # each leaf 32 x 76
PLANALTO_PANE_RECT = (163, 46, 189, 112)                       # the right leaf's glass (29b broken, 29i the glaziers fit a new one)
PLANALTO_DOOR_STATES = ('closed', 'open', 'broken', 'empty_frame', 'restored')


def planalto_ramp(view='ramp', time='day', year=2003, flags=True, state='plain'):
    """PLANALTO, 320 x 180: the palace's glass front under a roof slab with its curved white columns, the ramp rising to the entrance, lawns, plaza.
    view: 'ramp' (07d 2003, 28d 2023: crowd on both sides, the climber follows `PLANALTO_RAMP_PATH`, crowd bands `PLANALTO_CROWD_BANDS`; one drawing, the
    year only changes the flags: 2003 two flags, 2023 two flags and the second row of poles) | 'foot' (12b: low view at the foot of the ramp, three curved columns close, the
    ramp rising to the right: the drawing of scene_12.planalto_foot, now shared; figures at the foot stand at y 118-145).
    time: 'day' | 'dusk' | 'night' (windows lit). flags: draw the flag cloth (False: bare masts, place `three_powers_flag(frame)` at `PLANALTO_FLAGS`).
    state: 'plain' | 'aftermath' (29b, ramp wide: a chair and papers on the ramp, the right glass door cracked)."""
    assert view in ('ramp', 'foot') and time in ('day', 'dusk', 'night') and state in ('plain', 'aftermath')
    g = Geometry(); rng = random.Random(1960 + year)
    if view == 'foot':
        sky = _sky(g, time if time != 'day' else 'day', 76)
        r(g, 0, 30, 320, 6, 'ivory'); r(g, 0, 36, 320, 2, 'plaster3')
        r(g, 0, 38, 320, 62, 'glass0')
        for x in range(4, 320, 14):
            r(g, x, 38, 1, 62, 'steel1')
        r(g, 0, 60, 320, 2, 'glass2')
        for x in (18, 196, 290):
            poly(g, [(x, 30), (x + 22, 30), (x + 12, 62), (x + 10, 86), (x + 32, 110), (x + 16, 110), (x - 2, 88), (x - 2, 62)], 'ivory')
            line(g, (x + 21, 31), (x + 11, 62), .5, 'plaster3')
        r(g, 0, 100, 320, 10, 'plaster3'); r(g, 0, 100, 320, 1, 'ivory')
        poly(g, [(170, 110), (320, 64), (320, 76), (196, 114)], 'plaster3'); line(g, (170, 110), (320, 64), .6, 'ivory')
        r(g, 0, 110, 320, 70, 'steel1'); r(g, 0, 110, 320, 1, 'steel2')
        lit = [([(x, 66, 3, 14) for x in range(8, 320, 28)], 'gold', 1)]
        return _ext_finish(g, time, sky, lit)
    sky = _sky(g, time, 64)
    for xx in range(-6, 320, 34):                                                               # far line of trees behind the palace
        ellipse(g, xx + 12, 66, 18, 7, 'v3_leaf'); ellipse(g, xx + 14, 64, 12, 5, 'v3_leaf2')
    r(g, 0, 64, 320, 54, 'plaster3')
    bays = _planalto_building(g, 22, 298, 40, 104, [40, 102, 214, 274])
    r(g, 150, 64, 40, 40, 'black'); r(g, 152, 66, 18, 38, 'glass2'); r(g, 172, 66, 16, 38, 'glass2'); r(g, 170, 66, 2, 38, 'steel0')           # entrance doors seen from afar
    r(g, 148, 60, 44, 4, 'ivory')
    _lawn(g, 320, 104, 118)
    r(g, 24, 104, 272, 6, 'plaster3'); r(g, 24, 104, 272, 1, 'ivory')                            # the porch
    _plaza(g, 320, 118)
    poly(g, [(148, 108), (190, 108), (252, 150), (208, 150)], 'plaster2'); poly(g, [(148, 108), (190, 108), (193, 110), (151, 110)], 'ivory')
    line(g, (148, 108), (208, 150), .8, 'ivory'); line(g, (190, 108), (252, 150), .8, 'ivory')
    line(g, (146, 98), (206, 140), .6, 'steel1'); line(g, (190, 98), (251, 140), .6, 'steel1')
    for t in (0, .2, .4, .6, .8, 1.0):
        lx = 146 + (206 - 146) * t; ly = 98 + 42 * t; rx = 190 + 61 * t
        r(g, round(lx), round(ly), 1, 10, 'steel0'); r(g, round(rx), round(ly), 1, 10, 'steel0')
    for (fx, fy) in PLANALTO_FLAGS:
        r(g, fx, fy, 1, 80, 'steel1'); r(g, fx - 1, fy - 2, 3, 2, 'gold')
        if flags:
            g.paste(three_powers_flag(0), fx + 1, fy)
    if year >= 2023:
        for fx in (96, 244):
            r(g, fx, 40, 1, 66, 'steel1')
            if flags:
                g.paste(three_powers_flag(2, 18, 12), fx + 1, 40)
    if state == 'aftermath':
        r(g, 232, 138, 8, 3, 'wood1'); r(g, 232, 130, 2, 8, 'wood1'); r(g, 238, 130, 2, 8, 'wood1'); r(g, 232, 130, 8, 2, 'wood2')                         # a chair on the ramp
        for _ in range(14):
            r(g, rng.randrange(170, 246), rng.randrange(112, 148), rng.randrange(2, 4), 1, 'ivory')
        line(g, (176, 70), (182, 90), .5, 'ivory'); line(g, (182, 90), (174, 102), .5, 'ivory'); line(g, (182, 90), (188, 98), .5, 'ivory')                 # cracks in a glass leaf
    lit = [(bays, 'gold', 2)]
    return _ext_finish(g, time, sky, lit)


def planalto_doors(state='closed', time='day'):
    """PLANALTO-DOOR, 320 x 180 (28e, 29b, 29i): the entrance at the top of the ramp seen close: roof slab, curved columns left and right, glass side lights and
    two leaves of 32 x 76 (`PLANALTO_DOOR_LEAVES`), porch floor y 118-145 for the guards, glaziers and intruders. state: 'closed' | 'open' (the leaves are
    OUT: a lit lobby; for 28e draw this and step `planalto_door_leaf(side, frac)` from 0 (closed) to 1 (open): the guards pull the doors) | 'broken' (29b: the right
    leaf's glass smashed, cracks, shards on the floor, a lit lobby through the hole) | 'empty_frame' (29i start: the right leaf's frame without glass; fit
    `planalto_pane()` at `PLANALTO_PANE_RECT`) | 'restored' (29i end: the new pane in place, the picture of 'closed')."""
    assert state in PLANALTO_DOOR_STATES and time in ('day', 'dusk', 'night')
    g = Geometry(); rng = random.Random(2023)
    sky = _sky(g, time, 40)
    r(g, 0, 40, 320, 106, 'plaster3')
    r(g, 70, 22, 180, 12, 'ivory'); r(g, 70, 34, 180, 2, 'plaster3')                             # roof slab over the entrance
    r(g, 0, 28, 70, 8, 'ivory'); r(g, 250, 28, 70, 8, 'ivory')
    for cx in (22, 54, 252, 284):
        _col_poly(g, cx, 36, 120, 10)
    fx0, fy0, fx1, fy1 = PLANALTO_DOOR_FRAME
    r(g, fx0, fy0, fx1 - fx0, fy1 - fy0, 'steel0')                                               # frame
    lobby = Geometry(); r(lobby, fx0, fy0, fx1 - fx0, fy1 - fy0, 'plaster2'); r(lobby, fx0, fy0, fx1 - fx0, 14, 'cream'); r(lobby, fx0, 100, fx1 - fx0, 18, 'floor3')
    for k in range(5):
        r(lobby, fx0 + 6 + k * 24, 54, 14, 46, 'blue0'); r(lobby, fx0 + 7 + k * 24, 55, 12, 44, 'blue1')                    # the corridor behind
    def leaf(rect, glass='glass1', pane=True, cracked=False):
        x0, y0, x1, y1 = rect
        r(g, x0, y0, x1 - x0, y1 - y0, 'steel1')
        if pane:
            r(g, x0 + 3, y0 + 4, x1 - x0 - 6, y1 - y0 - 8, glass); r(g, x0 + 3, y0 + 4, x1 - x0 - 6, 3, 'glass2')
        r(g, x0 + 2, y0 + 36, x1 - x0 - 4, 3, 'steel1'); r(g, x1 - 5 if x0 < 160 else x0 + 2, y0 + 34, 3, 12, 'steel3')
    g.paste(lobby, 0, 0)
    for rect in ((fx0 + 3, fy0 + 3, 128, fy1 - 2), (192, fy0 + 3, fx1 - 3, fy1 - 2)):                    # fixed side lights
        r(g, rect[0], rect[1] + 1, rect[2] - rect[0], rect[3] - rect[1] - 1, 'steel1'); r(g, rect[0] + 2, rect[1] + 4, rect[2] - rect[0] - 4, rect[3] - rect[1] - 8, 'glass1'); r(g, rect[0] + 2, rect[1] + 4, rect[2] - rect[0] - 4, 3, 'glass2')
    L, R = PLANALTO_DOOR_LEAVES['L'], PLANALTO_DOOR_LEAVES['R']
    if state in ('closed', 'restored', 'broken', 'empty_frame'):
        leaf(L)
        if state in ('closed', 'restored'):
            leaf(R)
        else:
            leaf(R, pane=False)
            px0, py0, px1, py1 = PLANALTO_PANE_RECT
            if state == 'broken':
                r(g, px0, py0, px1 - px0, py1 - py0, 'glass1'); r(g, px0, py0, px1 - px0, 3, 'glass2')
                poly(g, [(px0 + 6, py0 + 20), (px1 - 2, py0 + 10), (px1 - 2, py0 + 60), (px0 + 12, py0 + 54), (px0 + 4, py0 + 36)], 'plaster2')     # the hole: lobby wall
                r(g, px0 + 6, py0 + 36, px1 - px0 - 8, 20, 'cream')
                for (a, b, c, d) in ((px0 + 4, py0 + 36, px0 - 0, py0 + 8), (px0 + 8, py0 + 22, px0 + 22, py0 + 2), (px0 + 8, py0 + 54, px0 + 2, py0 + 62), (px0 + 20, py0 + 58, px0 + 24, py0 + 64), (px1 - 3, py0 + 12, px1 - 2, py0 + 4)):
                    line(g, (a, b), (c, d), .5, 'ivory')
                for _ in range(16):
                    r(g, rng.randrange(px0 - 6, px1 + 8), rng.randrange(112, 120), rng.randrange(1, 4), 1, 'glass2')
    r(g, 0, 118, 320, 28, 'plaster2'); r(g, 0, 118, 320, 2, 'ivory')
    for yy in (126, 134, 142):
        r(g, 0, yy, 320, 1, 'plaster1')
    for xx in range(0, 320, 22):
        r(g, xx, 119, 1, 27, 'plaster1')
    if state == 'broken':
        for _ in range(26):
            r(g, rng.randrange(120, 210), rng.randrange(120, 144), rng.randrange(1, 3), 1, 'glass2')
    r(g, 0, 146, 320, 3, 'plaster1'); r(g, 0, 149, 320, 31, 'steel0')
    lit = [([(fx0 + 8, 44, 4, 20), (fx1 - 12, 44, 4, 20)], 'gold', 1)]
    return _ext_finish(g, time, sky, lit)


def planalto_door_leaf(side='R', frac=0.0):
    """One door leaf as a piece on the 320 x 180 canvas, hinged at its OUTER edge (L: x 128, R: x 192), for the guards of 28e: frac 0 = closed (fills the leaf
    rectangle), 1 = swung wide open (a thin slice at the hinge); steps of .25. Use over `planalto_doors('open')`."""
    x0, y0, x1, y1 = PLANALTO_DOOR_LEAVES[side]
    g = Geometry(); w = max(2, round((x1 - x0) * (1 - frac))); s = round(frac * 8)
    if side == 'L':
        pts = [(x0, y0 + s * 0), (x0 + w, y0 + s), (x0 + w, y1 - s), (x0, y1)]
    else:
        pts = [(x1, y0), (x1 - w, y0 + s), (x1 - w, y1 - s), (x1, y1)]
    poly(g, pts, 'steel1')
    if w > 10:
        a, b = (x0 + 3, x0 + w - 3) if side == 'L' else (x1 - w + 3, x1 - 3)
        poly(g, [(a, y0 + 4 + s), (b, y0 + 4 + s * 2), (b, y1 - 4 - s * 2), (a, y1 - 4 - s)], 'glass1')
        r(g, min(a, b), y0 + 4 + s, abs(b - a), 2, 'glass2')
    return g


def planalto_pane():
    """The new glass pane the glaziers of 29i carry (origin top-left, 26 x 66 = `PLANALTO_PANE_RECT`): lift at +0.5, fit at +2.0."""
    x0, y0, x1, y1 = PLANALTO_PANE_RECT; w, h = x1 - x0, y1 - y0
    g = Geometry(); r(g, 0, 0, w, h, 'glass1'); r(g, 0, 0, w, 3, 'glass2'); r(g, 0, 0, w, 1, 'ivory'); r(g, 0, h - 1, w, 1, 'steel1')
    poly(g, [(3, 5), (10, 5), (3, 20)], 'glass2')
    return g

# ============================================================================================ CONGRESS (exterior, several angles)
CONGRESS_VIEWS = ('front', 'c2', 'c3', 'c4', 'door')
CONGRESS_H = {'front': 180, 'c2': 180, 'c3': 260, 'c4': 180, 'door': 180}
SENADO_PLAQUE = ('SENADO FEDERAL', (100, 60, 200, 70))        # 22k (view 'c4'): plaque at the entrance; a Senate sign belongs here and nowhere in 22b
CONGRESS_RAMP_PATH = [(24, 144), (112, 113)]                  # 05e ('front'): soles of the two men climbing the left ramp, bottom -> top (the doorman stands at CONGRESS_DOORMAN)
CONGRESS_DOORMAN = (96, 127)                                  # 05e: a doorman beside the ramp, soles
CONGRESS_DOORS = {'c2': (116, 98, 150, 114), 'c4': (130, 72, 190, 134), 'door': (128, 56, 192, 120)}   # the entrances (x0, y0, x1, y1): 11b +3.4 'doors open', 22k Moro enters, 27h guards
CONGRESS_ROAD_Y = 140                                         # 11b: the car arrives along the road (soles / wheel line)
CONGRESS_C3_WINDOWS = [(x, y, 8, 5) for y in range(30, 236, 12) for x in (112, 128, 144, 160, 190, 206, 222, 238)]   # 13j: every tower window, all dark in the background


def _dome(g, cx, base, rx, ry, c='ivory', sh='plaster3'):
    """Senate dome (convex), drawn above the slab line `base`."""
    ellipse(g, cx, base, rx, ry, c)
    ellipse(g, cx + rx // 4, base - 1, rx * 3 // 4, ry - 2, sh)
    ellipse(g, cx - rx // 5, base - 1, rx * 3 // 4, ry - 3, c)
    r(g, cx - rx - 1, base, 2 * rx + 3, 4, c)


def _cbowl(g, cx, base, rx, ry):
    """Chamber bowl (concave, opens upward): lower half of an ellipse with a visible rim and a dark inner side."""
    ellipse(g, cx, base - ry // 2, rx, ry, 'ivory')
    ellipse(g, cx, base - ry, rx - 1, max(2, ry // 3), 'plaster2')
    r(g, cx - rx, base - ry - 2, 2 * rx, 2, 'ivory')
    r(g, cx - rx - 1, base, 2 * rx + 3, 3, 'ivory')


def _tower(g, x, top, base, w, windows=True, lit=None):
    r(g, x, top, w, base - top, 'plaster3'); r(g, x, top, w, 2, 'ivory'); r(g, x + w - 3, top, 3, base - top, 'plaster2'); r(g, x, top, 1, base - top, 'ivory')
    rects = []
    for yy in range(top + 8, base - 6, 7):
        r(g, x + 2, yy, w - 4, 2, 'steel1')
        for xx in range(x + 3, x + w - 5, 6):
            rects.append((xx, yy + 2, 3, 3))
    return rects


def congress_exterior(view='front', time='day', lit=None):
    """CONGRESS exterior (one drawing across scenes 05, 11, 13, 22, 27, 28, 29). 320 x 180 except 'c3' (320 x 260).
    view: 'front' (05e, angle C1: low frontal view: two towers, slab, Senate dome at left and Chamber bowl at right, the left ramp rising to the roof: climbers follow
    `CONGRESS_RAMP_PATH`, a doorman at `CONGRESS_DOORMAN`) | 'c2' (11b: THREE-QUARTER from the front left, towers at the right, the Senate dome nearer, the road in
    front for the car at `CONGRESS_ROAD_Y`, lawn for the small crowd, entrance `CONGRESS_DOORS['c2']`; pan along the facade = x pan) | 'c3' (13j: the towers
    filling the picture, 260 rows high for the slow tilt up, all windows dark in the background and `CONGRESS_C3_WINDOWS`: light them with `congress_lit('c3', [i, ...])`) |
    'c4' (22k, angle C4: from the side, a tall tower at the left, the long low wing with the entrance `CONGRESS_DOORS['c4']` (62 rows high) and the plaque
    `SENADO_PLAQUE` at (100,60,200,70)) | 'door' (27h: the main doors `CONGRESS_DOORS['door']` seen frontally, plaza in front for the barrier and the car; no sign).
    time: 'day' | 'dusk' | 'night'. lit: None = default (day: none, dusk and night: the tower windows alternate lit) | 'all' | 'none' | n (every n-th window lit)."""
    assert view in CONGRESS_VIEWS and time in ('day', 'dusk', 'night')
    H = CONGRESS_H[view]; g = Geometry(); rng = random.Random(1960)
    sky = _sky(g, time, 100 if view != 'c3' else 150)
    if time == 'night':
        _stars(g, rng, 30, 60 if view != 'c3' else 140)
    windows = []
    if view == 'front':
        for xx in range(0, 320, 30):
            ellipse(g, xx + 10, 100, 18, 5, 'v3_leaf')
        r(g, 0, 100, 320, 20, 'plaster3')
        windows += _tower(g, 135, 6, 100, 28); windows += _tower(g, 171, 6, 100, 28)
        r(g, 134, 4, 66, 3, 'ivory')
        r(g, 20, 100, 280, 12, 'ivory'); r(g, 20, 112, 280, 5, 'plaster2'); r(g, 20, 100, 280, 1, 'cream')
        _dome(g, 78, 100, 40, 17); _cbowl(g, 248, 100, 40, 14)
        r(g, 24, 117, 272, 12, 'glass0'); r(g, 24, 117, 272, 1, 'glass2')
        for xx in range(30, 296, 12):
            r(g, xx, 117, 1, 12, 'steel1')
        r(g, 0, 112, 320, 17, 'plaster3')
        _lawn(g, 320, 129, 138)
        _plaza(g, 320, 138)
        poly(g, [(8, 146), (30, 146), (118, 112), (100, 112)], 'plaster2'); line(g, (8, 146), (100, 112), .8, 'ivory'); line(g, (30, 146), (118, 112), .8, 'ivory')         # left ramp
        poly(g, [(312, 146), (290, 146), (202, 112), (220, 112)], 'plaster2'); line(g, (312, 146), (220, 112), .8, 'ivory'); line(g, (290, 146), (202, 112), .8, 'ivory')
        for t in (0, .25, .5, .75, 1):
            lx = round(8 + 92 * t); ly = round(146 - 34 * t)
            r(g, lx, ly - 8, 1, 8, 'steel0'); r(g, 320 - lx - 1, ly - 8, 1, 8, 'steel0')
    elif view == 'c2':
        for xx in range(-4, 320, 26):
            ellipse(g, xx + 10, 98, 16, 6, 'v3_leaf'); ellipse(g, xx + 12, 96, 10, 4, 'v3_leaf2')
        r(g, 0, 98, 320, 22, 'plaster3')
        windows += _tower(g, 170, 10, 98, 30); r(g, 200, 10, 9, 88, 'plaster1'); r(g, 200, 10, 9, 2, 'plaster2')
        windows += _tower(g, 214, 14, 98, 30); r(g, 244, 14, 9, 84, 'plaster1'); r(g, 244, 14, 9, 2, 'plaster2')
        poly(g, [(20, 96), (252, 96), (264, 90), (60, 90)], 'plaster3'); r(g, 20, 96, 232, 18, 'ivory'); r(g, 252, 90, 12, 24, 'plaster2'); r(g, 20, 96, 232, 1, 'cream')
        _dome(g, 86, 90, 38, 17); _cbowl(g, 262, 92, 26, 11)
        x0, y0, x1, y1 = CONGRESS_DOORS['c2']
        r(g, 24, y0, 224, 16, 'glass0'); r(g, 24, y0, 224, 1, 'glass2')
        for xx in range(30, 248, 10):
            r(g, xx, y0, 1, 16, 'steel1')
        r(g, x0, y0, x1 - x0, y1 - y0, 'black'); r(g, x0 + 2, y0 + 2, 14, y1 - y0 - 2, 'glass2'); r(g, x0 + 18, y0 + 2, 14, y1 - y0 - 2, 'glass2')
        _lawn(g, 320, 114, 134, 3)
        r(g, 0, 134, 320, 16, 'plaster1'); r(g, 0, 134, 320, 1, 'plaster2'); r(g, 0, 150, 320, 30, 'steel0')                    # the road (wheel line y 140)
        for xx in range(0, 320, 40):
            r(g, xx, 142, 18, 1, 'plaster3')
        r(g, 24, 120, 100, 10, 'plaster3'); r(g, 24, 120, 100, 1, 'ivory')                                                      # a stone walk to the entrance
    elif view == 'c3':
        r(g, 0, 150, 320, 110, 'blue0')
        windows += _tower(g, 100, 8, 232, 70); windows += _tower(g, 186, 8, 232, 70)
        windows = list(CONGRESS_C3_WINDOWS)
        r(g, 96, 4, 164, 4, 'ivory')
        r(g, 0, 232, 320, 28, 'plaster3'); r(g, 0, 232, 320, 2, 'ivory')
        _dome(g, 40, 232, 38, 16); _cbowl(g, 282, 232, 36, 14)
        _lawn(g, 320, 246, 260)
    elif view == 'c4':
        for xx in range(0, 320, 30):
            ellipse(g, xx + 10, 76, 18, 6, 'v3_leaf')
        r(g, 0, 76, 320, 58, 'plaster3')
        windows += _tower(g, 6, 2, 134, 44)
        r(g, 50, 76, 270, 58, 'ivory'); r(g, 50, 76, 270, 3, 'cream'); r(g, 50, 128, 270, 6, 'plaster2')
        for xx in range(60, 320, 22):
            if not (126 < xx < 194):
                r(g, xx, 82, 12, 44, 'glass0'); r(g, xx, 82, 12, 3, 'glass2'); r(g, xx + 12, 82, 3, 44, 'plaster3')
        x0, y0, x1, y1 = CONGRESS_DOORS['c4']
        r(g, x0 - 4, y0 - 2, x1 - x0 + 8, y1 - y0 + 2, 'steel0'); r(g, x0, y0, x1 - x0, y1 - y0, 'black'); r(g, x0 + 2, y0 + 2, 28, y1 - y0 - 2, 'glass2'); r(g, x0 + 30, y0 + 2, 28, y1 - y0 - 2, 'glass2')
        px0, py0, px1, py1 = SENADO_PLAQUE[1]
        r(g, px0 - 4, py0 - 3, px1 - px0 + 8, py1 - py0 + 6, 'wood0'); r(g, px0 - 3, py0 - 2, px1 - px0 + 6, py1 - py0 + 4, 'blue0'); r(g, px0 - 3, py0 - 2, px1 - px0 + 6, 1, 'blue1')
        _sign_text(g, SENADO_PLAQUE[0], SENADO_PLAQUE[1], 'ivory')
        r(g, 0, 134, 320, 8, 'plaster3'); r(g, 0, 134, 320, 1, 'ivory')
        r(g, 100, 134, 120, 4, 'plaster3'); r(g, 96, 138, 128, 4, 'plaster2')                                               # steps
        r(g, 0, 142, 320, 4, 'plaster3'); r(g, 0, 146, 320, 3, 'plaster1'); r(g, 0, 149, 320, 31, 'steel0')
    else:
        r(g, 0, 40, 320, 106, 'plaster3')
        r(g, 70, 22, 180, 12, 'plaster2'); r(g, 70, 22, 180, 2, 'ivory')
        r(g, 74, 34, 172, 86, 'glass0')
        for x in range(78, 246, 14):
            r(g, x, 34, 4, 86, 'ivory')
        x0, y0, x1, y1 = CONGRESS_DOORS['door']
        r(g, x0 - 3, y0 - 3, x1 - x0 + 6, y1 - y0 + 3, 'steel0'); r(g, x0, y0, x1 - x0, y1 - y0, 'black'); r(g, x0 + 3, y0 + 3, 29, y1 - y0 - 3, 'glass2'); r(g, x0 + 33, y0 + 3, 29, y1 - y0 - 3, 'glass2'); r(g, x0 + 31, y0 + 3, 2, y1 - y0 - 3, 'steel0')
        r(g, 0, 118, 320, 28, 'floor3'); r(g, 110, 120, 100, 4, 'plaster1'); r(g, 104, 124, 112, 3, 'plaster1')
        r(g, 0, 146, 320, 3, 'plaster1'); r(g, 0, 149, 320, 31, 'steel0')
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < H}
    # lit windows
    mode = lit if lit is not None else ('none' if time == 'day' else 'default')
    rects = windows
    if mode == 'all':
        sel = rects
    elif mode == 'none':
        sel = []
    elif isinstance(mode, int):
        sel = rects[::mode]
    else:
        sel = [q for k, q in enumerate(rects) if (q[0] + q[1]) % 3 and time != 'day']
    if view == 'c3':
        for (x, y, w, h) in CONGRESS_C3_WINDOWS:
            r(g, x, y, w, h, 'blue0' if time != 'day' else 'glass1')
    _ext_finish(g, time, sky, [(sel, 'gold', 1)] if sel else None)
    return g


def congress_lit(view='c3', which=()):
    """Individual lit windows as a piece on the picture's canvas (for 13j: window 1 at +0.5, 2 at +1.7, 3 at +2.9): `which` are indices into `CONGRESS_C3_WINDOWS`."""
    assert view == 'c3'
    g = Geometry()
    for i in which:
        x, y, w, h = CONGRESS_C3_WINDOWS[i]; r(g, x, y, w, h, 'gold'); r(g, x, y, w, 1, 'ivory')
    return g


# ============================================================================================ STF (exterior)
STF_FACADE_SIGN = ('SUPREMO TRIBUNAL FEDERAL', (90, 40, 230, 48))   # 11d: plaque on the facade (plan rectangle)
STF_FACADE_WALK = (0, 138, 320, 146)                                 # 11d: the clerk walks along y 140-145 (soles), left to right at the pace of the cycle


def _stf_building(g, x0, x1, top, base, ncol, ped=True):
    """The STF front: pediment slab, straight columns (straightened, as 11d), dark glass between, steps. Returns the window bays."""
    W = x1 - x0; H = base - top
    r(g, x0, top, W, 6, 'ivory')
    if ped:
        poly(g, [(x0, top), ((x0 + x1) // 2, top - H // 4), (x1, top)], 'ivory'); poly(g, [(x0 + 12, top - 1), ((x0 + x1) // 2, top - H // 4 + 4), (x1 - 12, top - 1)], 'plaster3')
    r(g, x0, top + 6, W, max(6, H // 6), 'plaster3'); r(g, x0, top + 6, W, 1, 'ivory')
    gy0 = top + 6 + max(6, H // 6) + 2
    r(g, x0 + 4, gy0, W - 8, base - gy0 - 4, 'glass0'); r(g, x0 + 4, gy0, W - 8, 1, 'glass2')
    bays = []
    step = W / ncol
    for k in range(ncol):
        cx = round(x0 + 6 + k * (W - 22) / (ncol - 1)) if ncol > 1 else x0
        r(g, cx, gy0 - 2, 9, base - gy0, 'ivory'); r(g, cx, gy0 - 2, 2, base - gy0, 'plaster3'); r(g, cx + 7, gy0 - 2, 2, base - gy0, 'steel2'); r(g, cx - 2, gy0 - 4, 13, 3, 'ivory'); r(g, cx - 2, base - 5, 13, 3, 'ivory')
        if k < ncol - 1:
            bx = cx + 12; bw = max(4, int((W - 22) / (ncol - 1)) - 15)
            bays.append((bx, gy0 + 5, bw, (base - gy0) // 2))
    for k in range(3):
        r(g, x0 - 4 * k, base + k * 3 - 2, W + 8 * k, 3, 'plaster3' if k % 2 else 'ivory')
    return bays


def stf_facade(time='day'):
    """STF-EXT, 320 x 180 (11d, and any exterior of the Supreme Court): pediment, straight columns, steps and the plaque SUPREMO TRIBUNAL FEDERAL at
    `STF_FACADE_SIGN` (90,40,230,48). The plan's clerk walks along `STF_FACADE_WALK` (soles y 140-145). time: 'day' | 'dusk' | 'night' (windows lit at dusk and night)."""
    assert time in ('day', 'dusk', 'night')
    g = Geometry(); rng = random.Random(2012)
    sky = _sky(g, time, 70)
    r(g, 0, 70, 320, 70, 'plaster2')
    bays = _stf_building(g, 40, 280, 32, 118, 7)
    x0, y0, x1, y1 = STF_FACADE_SIGN[1]
    r(g, x0 - 4, y0 - 2, x1 - x0 + 8, y1 - y0 + 4, 'plaster1'); r(g, x0 - 3, y0 - 1, x1 - x0 + 6, y1 - y0 + 2, 'cream')
    _sign_text(g, STF_FACADE_SIGN[0], STF_FACADE_SIGN[1], 'black')
    r(g, 0, 138, 320, 42, 'steel1')
    for _ in range(60):
        r(g, rng.randrange(320), rng.randrange(142, 178), rng.randrange(1, 5), 1, rng.choice(['steel0', 'steel2']))
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < 180}
    return _ext_finish(g, time, sky, [(bays, 'gold', 1)])

# ============================================================================================ THREE-POWERS (Planalto | Congress | STF), ESPLANADE
THREE_W = {'row': 780, 'esplanade': 640, 'aerial': 320}
THREE_BASE = 112                                                   # the buildings' ground line in 'row' and 'esplanade'; the plaza is y 112-146 (walkers' soles 118-145)
THREE_X = dict(planalto=(20, 250), congress=(296, 500), stf=(545, 745))         # 'row': x extent of each building
THREE_PAN = dict(planalto=0, congress=-240, stf=-460)              # 'row': the pan x that centres each building (28f: 0 -> -460 over 4 s; 28g: back)
THREE_FLAGS = [(262, 36), (525, 44), (752, 40)]                    # 'row': top-left of the flag cloth on each mast (pieces `three_powers_flag(frame, 18, 12)`); masts are drawn in the background
THREE_PIGEON_SPOTS = [(60, 50), (120, 50), (330, 100), (470, 100), (580, 56), (680, 56), (180, 122), (440, 122)]   # 'row': where pigeons perch (x, y of the sprite's top-left): roofs and plaza
THREE_GUARD_SPOTS = dict(planalto_door=(158, 112), planalto_ramp=(150, 111), stf_steps=(642, 112), congress_door=(402, 112))   # 'row': sole point for `guard_silhouette('far')` (origin top-left = x-2, y-14)
ESPLANADE_LAMPS = [(250 + 70 * k, 118) for k in range(5)]         # 'esplanade': foot of each lamp post (27i +0.5: they turn on: `esplanade_lamps_on()`)
AERIAL_RAMP = (112, 78)                                           # 'aerial' (29a): the foot of the Planalto ramp, where the groups arrive (+1.4)
AERIAL_PATHS = [((150, 176), (112, 82)), ((172, 176), (130, 90)), ((190, 176), (230, 84))]   # start -> end of three streams of walkers along the esplanade
_ROW_CACHE = {}


def _ground_row(g, w, time):
    _lawn(g, w, 94, 112)
    r(g, 0, 112, w, 34, 'plaster3'); r(g, 0, 112, w, 1, 'ivory')
    for yy in (121, 130, 139):
        r(g, 0, yy, w, 1, 'plaster2')
    for xx in range(0, w, 20):
        for yy in range(112, 146, 18):
            r(g, xx + (yy // 18 % 2) * 10, yy, 1, 9, 'plaster2')
    _noise(g, random.Random(3), w // 4, 0, 113, w, 146, ['plaster2', 'plaster1'], 4)
    r(g, 0, 146, w, 3, 'plaster1'); r(g, 0, 146, w, 1, 'ivory'); r(g, 0, 149, w, 31, 'steel0')
    for xx in range(0, w, 38):
        r(g, xx, 163, 17, 2, 'plaster3')


def _three_buildings(g, pos):
    """Draw the three buildings at the x extents in `pos` (planalto, congress, stf); returns {name: [lit-window rects]}."""
    out = {}
    (pa, pb), (ca, cb), (sa, sb) = pos['planalto'], pos['congress'], pos['stf']
    pw = pb - pa
    cols = [pa + 14 + k * (pw - 40) // 4 for k in range(5)]
    out['planalto'] = _planalto_building(g, pa, pb, 52, THREE_BASE, cols, 10)
    mid = (pa + pb) // 2
    r(g, mid - 12, 74, 24, 34, 'black'); r(g, mid - 10, 76, 10, 32, 'glass2'); r(g, mid, 76, 10, 32, 'glass2')            # the entrance
    poly(g, [(mid - 14, 112), (mid + 14, 112), (mid + 40, 118), (mid - 4, 118)], 'plaster2')                                # the ramp's foot
    cw = cb - ca; cm = (ca + cb) // 2
    r(g, ca, 100, cw, 12, 'ivory'); r(g, ca, 100, cw, 1, 'cream'); r(g, ca, 108, cw, 4, 'plaster2')
    tw = _tower(g, cm - 25, 12, 104, 22) + _tower(g, cm + 3, 12, 104, 22)
    r(g, cm - 26, 10, 54, 3, 'ivory')
    _dome(g, ca + 38, 100, 36, 19); _cbowl(g, cb - 38, 100, 36, 15)
    r(g, ca + 4, 104, cw - 8, 6, 'glass0')
    out['congress'] = tw
    out['stf'] = _stf_building(g, sa, sb, 62, THREE_BASE, 6)
    return out


def _row_windows():
    if 'row' not in _ROW_CACHE:
        _ROW_CACHE['row'] = _three_buildings(Geometry(), THREE_X)
    return _ROW_CACHE['row']


def three_powers(view='row', time='day', lights=None, lamps=False):
    """THREE-POWERS and the ESPLANADE: Planalto, Congress and STF in one row, ground level. One drawing per building shared with `planalto_ramp`, `congress_exterior`,
    `stf_facade` (same columns, towers, domes, pediment).
    view: 'row' (28f, 28g, 32i: 780 x 180, Planalto x 20-250, Congress 296-500, STF 545-745; pan x with negative values: `THREE_PAN`; 28f 0 -> -460, 28g -460 -> 0) |
    'esplanade' (12h: Planalto at the left, the avenue with five lamps, Congress at the right, 640 x 180, pan 0 -> -320; 27i: the empty esplanade at dusk) |
    'aerial' (29a: 320 x 180 high angle on the plaza: Planalto left, STF right, the Congress far at the back, the esplanade avenue coming from the bottom; walkers' streams
    `AERIAL_PATHS`, the ramp's foot `AERIAL_RAMP`).
    time: 'day' | 'golden' | 'dusk' | 'night'. lights: None/'off' (all windows dark) | 'on' | a tuple of names ('planalto', 'congress', 'stf'): lit in the background. For the
    switch driven by the scene use `three_powers_lights(names)` pieces over a dark background (28g +0.5 'stf', +3.5 'congress'; 12h +2.0 'congress'). lamps: draw the esplanade
    lamps lit (False: dark; `esplanade_lamps_on()` piece). Flags on the masts: pieces `three_powers_flag(frame, 18, 12)` at `THREE_FLAGS` (the masts are in the set)."""
    assert view in THREE_W and time in ('day', 'golden', 'dusk', 'night')
    w = THREE_W[view]; g = Geometry(); rng = random.Random(1958)
    if view == 'aerial':
        return _three_aerial(time, lights)
    sky = _sky(g, time, 96)
    if time == 'night':
        _stars(g, rng, 60, 70)
    for xx in range(0, w, 70):                                                                                   # far trees, a low skyline
        ellipse(g, xx + 20, 98, 26, 7, 'v3_leaf'); ellipse(g, xx + 24, 96, 16, 5, 'v3_leaf2')
    _ground_row(g, w, time)
    if view == 'row':
        wins = _three_buildings(g, THREE_X)
        for xx in (270, 520):
            tree(g, xx, 118, 44, 7 + xx)
        for (fx, fy) in THREE_FLAGS:
            r(g, fx, fy, 1, 112 - fy, 'steel1'); r(g, fx - 1, fy - 2, 3, 2, 'gold')
    else:
        pos = dict(planalto=(10, 190), congress=(400, 620), stf=(-300, -200))
        wins = _three_buildings(g, {'planalto': pos['planalto'], 'congress': pos['congress'], 'stf': (900, 1000)})
        r(g, 0, 112, w, 34, 'plaster3')
        for (lx, ly) in ESPLANADE_LAMPS:
            r(g, lx, ly - 40, 2, 40, 'steel0'); r(g, lx - 4, ly - 42, 10, 3, 'steel0'); r(g, lx - 3, ly - 39, 8, 2, 'cream' if lamps else 'steel2')
        for (fx, fy) in ((200, 40),):
            r(g, fx, fy, 1, 112 - fy, 'steel1'); r(g, fx - 1, fy - 2, 3, 2, 'gold')
        wins = {'planalto': wins['planalto'], 'congress': wins['congress'], 'stf': []}
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < w and 0 <= xy[1] < 180}
    if lights == 'on':
        names = ('planalto', 'congress', 'stf')
    else:
        names = tuple(lights) if lights and lights != 'off' else ()
    lit = [([q for q in wins[n] if (q[0] + q[1]) % 3], 'gold', 1) for n in names]
    if lamps and view == 'esplanade':
        lit.append(([(lx - 3, ly - 39, 8, 2) for (lx, ly) in ESPLANADE_LAMPS], 'ivory', 1))
    return _ext_finish(g, time, sky, lit)


def three_powers_lights(names=('stf',), view='row'):
    """Lit windows of the named buildings as a piece on the background's canvas (780 x 180 for 'row', 640 for 'esplanade'); draw over a background made with `lights=None`.
    Switch the buildings on one after the other (28g: 'stf' at +0.5, 'congress' at +3.5)."""
    assert view in ('row', 'esplanade')
    g = Geometry()
    if view == 'row':
        wins = _row_windows()
    else:
        wins = _three_buildings(Geometry(), {'planalto': (10, 190), 'congress': (400, 620), 'stf': (900, 1000)})
    for n in names:
        _lit(g, [q for q in wins[n] if (q[0] + q[1]) % 3], 'gold')
    return g


def esplanade_lamps_on():
    """The five esplanade lamps lit (27i +0.5): warm heads and a soft cone on the paving, 640 x 180 canvas (draw cone with opacity ~ .25 if wanted: the cone is `esplanade_lamp_glow()`)."""
    g = Geometry()
    for (lx, ly) in ESPLANADE_LAMPS:
        r(g, lx - 3, ly - 39, 8, 2, 'ivory'); r(g, lx - 2, ly - 41, 6, 1, 'cream')
    return g


def esplanade_lamp_glow():
    g = Geometry()
    for (lx, ly) in ESPLANADE_LAMPS:
        poly(g, [(lx, ly - 38), (lx + 2, ly - 38), (lx + 20, ly + 20), (lx - 18, ly + 20)], 'cream')
    return g


def _three_aerial(time, lights):
    g = Geometry(); rng = random.Random(29)
    _lawn(g, 320, 0, 180, 5)
    poly(g, [(120, 40), (200, 40), (250, 180), (70, 180)], 'plaster3')                                          # the esplanade avenue, widening toward us
    poly(g, [(150, 40), (170, 40), (172, 180), (148, 180)], 'plaster2')
    r(g, 40, 56, 240, 74, 'plaster3'); r(g, 40, 56, 240, 1, 'ivory'); r(g, 40, 129, 240, 1, 'plaster2')           # the plaza
    for yy in range(62, 128, 11):
        r(g, 40, yy, 240, 1, 'plaster2')
    for xx in range(40, 280, 24):
        r(g, xx, 56, 1, 74, 'plaster2')
    # Congress, far at the back
    r(g, 100, 40, 120, 8, 'ivory'); r(g, 100, 47, 120, 2, 'plaster2')
    ellipse(g, 118, 40, 14, 6, 'ivory'); ellipse(g, 204, 39, 14, 6, 'ivory'); ellipse(g, 204, 36, 12, 3, 'plaster2')
    r(g, 154, 14, 5, 28, 'plaster3'); r(g, 161, 14, 5, 28, 'plaster3'); r(g, 154, 14, 12, 1, 'ivory')
    for yy in range(18, 40, 4):
        r(g, 155, yy, 3, 1, 'steel1'); r(g, 162, yy, 3, 1, 'steel1')
    # Planalto, left; STF, right: roofs seen from above, fronts toward the plaza
    for (x0, x1, flip) in ((6, 110, False), (210, 314, True)):
        r(g, x0, 66, x1 - x0, 12, 'ivory'); r(g, x0, 66, x1 - x0, 1, 'cream'); r(g, x0, 77, x1 - x0, 2, 'plaster2')
        r(g, x0 + 2, 79, x1 - x0 - 4, 26, 'glass0'); r(g, x0 + 2, 79, x1 - x0 - 4, 1, 'glass2')
        for xx in range(x0 + 6, x1 - 8, 12 if not flip else 11):
            if flip:
                r(g, xx, 79, 5, 26, 'ivory'); r(g, xx + 4, 79, 1, 26, 'plaster3')
            else:
                _col_poly(g, xx, 78, 106, 5)
        r(g, x0, 105, x1 - x0, 4, 'plaster3'); r(g, x0, 105, x1 - x0, 1, 'ivory')
    poly(g, [(104, 108), (124, 108), (136, 126), (116, 126)], 'plaster2'); line(g, (104, 108), (116, 126), .6, 'ivory'); line(g, (124, 108), (136, 126), .6, 'ivory')   # the ramp's foot
    for (fx, fy) in ((126, 100), (214, 96)):
        r(g, fx, fy, 1, 10, 'steel1')
    for xx in (30, 296):
        tree(g, xx, 150, 24, xx)
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < 180}
    return g



# ============================================================================================ SCHOOL FRONT (the voting school: 27g, 31a)
SCHOOL_BANNER = ('ELEIÇÕES 2026', (110, 14, 220, 24))            # 31a: the banner hung over the facade (plan rectangle, amended: x 110-220)
SCHOOL_FRONT_SIGN = ESCOLA_STREET_SIGN                           # 27g: the board over the door, the same drawing and the same rectangle as `school_street('wide')` and the BAIRRO's ESCOLA
SCHOOL_FRONT_DOOR = (147, 56, 183, 118)                          # the double door, 36 x 62 (view 'door' and 'voting': the same door as `school_street('wide')`)
SCHOOL_QUEUE = [(104, 134), (122, 138), (140, 142), (88, 130)]   # soles of the queue approaching the door from the left (the first one at the door); sprites ~19 px wide
SCHOOL_WAIT_SPOT = (236, 140)                                    # 27g +1.8: a woman waits here
SCHOOL_DOOR_SPOT = (165, 119)                                    # where a voter vanishes into the doorway (soles at the threshold, x = door centre)


def school_front(view='door', time='morning', signs=True):
    """The school of an election day, 320 x 180, the same building as `school_street('wide')` and the BAIRRO's ESCOLA (pale blue wall, two patches, double door,
    two windows), lit as a Sunday morning, with what a polling place has: a rope barrier along the queue, a flag at the door.
    view: 'door' (27g, SCHOOL-DOOR: voters entering, board ESCOLA at `SCHOOL_FRONT_SIGN` (130,24,200,34); `signs=False` blanks it) | 'voting' (31a, SCHOOL-FRONT:
    the facade a little lower, no ESCOLA board, the banner `SCHOOL_BANNER` 'ELEIÇÕES 2026' at (110,14,220,24) on two poles; queue along `SCHOOL_QUEUE`, a woman with a
    child and an elderly man join later). time: 'morning' (default) | 'day' | 'dusk'. Figures: soles y 118-145; the barrier posts are in the background, the rope is `school_front_fg()`."""
    assert view in ('door', 'voting') and time in ('morning', 'day', 'dusk')
    g = Geometry(); rng = random.Random(2026)
    sky = _sky(g, time, 60)
    r(g, 0, 60, 320, 90, 'blue3')
    rr = random.Random(61)
    for x in range(-10, 320, 46):
        h = rr.randrange(16, 34)
        r(g, x, 70 - h, 40, h + 50, 'steel2'); r(g, x, 70 - h, 40, 2, 'steel3')
        for y in range(74 - h, 100, 9):
            for xx in range(x + 5, x + 36, 9):
                r(g, xx, y, 4, 4, 'glass1')
    top = 20 if view == 'door' else 32
    rect = ESCOLA_STREET_SIGN[1] if view == 'door' else (130, 36, 200, 46)
    _school(g, 90, 150, top, 118, signs and view == 'door', rect, random.Random(3), big=True)
    r(g, 0, 70, 90, 48, 'plaster2'); r(g, 0, 66, 90, 5, 'clay'); r(g, 240, 74, 80, 44, 'sand'); r(g, 240, 68, 80, 6, 'red0')
    r(g, 6, 82, 22, 22, 'wood0'); r(g, 8, 84, 18, 18, 'glass0'); r(g, 270, 82, 24, 22, 'wood0'); r(g, 272, 84, 20, 18, 'glass0')
    tree(g, 40, 118, 60, 3); _lamp(g, 266)
    r(g, 0, 118, 320, 28, 'plaster2'); r(g, 0, 118, 320, 1, 'plaster0')
    for xx in range(0, 320, 14):
        r(g, xx, 119, 1, 27, 'plaster1')
    for yy in (126, 134, 142):
        r(g, 0, yy, 320, 1, 'plaster1')
    _noise(g, rng, 60, 0, 120, 320, 146, ['plaster3', 'plaster1'], 4)
    r(g, 0, 146, 320, 3, 'plaster3'); r(g, 0, 146, 320, 1, 'ivory'); r(g, 0, 149, 320, 31, 'steel0')
    for xx in range(0, 320, 38):
        r(g, xx, 163, 17, 2, 'plaster3')
    # the polling-place marks: a flag at the door, a blank notice board, barrier posts
    r(g, 190, 62, 1, 56, 'steel1'); g.paste(three_powers_flag(0, 16, 11), 191, 62)
    for (px, py) in ((84, 126), (108, 132), (132, 138), (156, 142)):
        r(g, px, py - 14, 2, 14, 'steel0'); r(g, px - 1, py - 15, 4, 2, 'gold'); r(g, px - 3, py, 8, 1, 'steel0')
    if view == 'voting':
        for px in (104, 226):
            r(g, px, 6, 2, 34, 'steel1')
        r(g, 104, 11, 124, 16, 'green'); r(g, 105, 12, 122, 14, 'ivory'); r(g, 105, 12, 122, 1, 'cream'); r(g, 105, 25, 122, 1, 'plaster2')
        _sign_text(g, SCHOOL_BANNER[0], SCHOOL_BANNER[1], 'blue0')
    if time == 'dusk':
        _grade_keep_sky(g, 'dusk', sky)
    elif time == 'morning':
        pass
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < 180}
    return g


def school_front_fg():
    """The rope between the barrier posts (red tape), drawn over the queue's legs: 320 x 180 canvas, draw after the figures."""
    g = Geometry()
    for (a, b) in (((84, 126), (108, 132)), ((108, 132), (132, 138)), ((132, 138), (156, 142))):
        line(g, (a[0] + 1, a[1] - 11), (b[0] + 1, b[1] - 11), .7, 'red1')
    return g



# ============================================================================================ MARKET-STALL (08f, 30f, 30g1)
MARKET_VENDOR = (150, 80)            # sprite origin of the keeper behind the counter (soles at row 128; the counter front hides the legs from row 113)
MARKET_CUSTOMERS = [(86, 96), (214, 96)]   # sprite origins of customers in front of the counter (soles at row 145)
MARKET_BAG_SPOT = (112, 100)         # 08f: top-left of `market_bag(fill)` on the counter (bags fill at +3.0)
MARKET_COUNTER = (72, 113, 248, 137)  # the counter (x0, top, x1, foot): top 24 rows above its foot line (y 137), the keeper's hips at y 104
MARKET_CRATE_SPOTS = [(34, 124), (34, 112), (34, 100), (262, 124), (262, 112)]   # 30g1: where `market_crate()` pieces stack (top-left); the first two of each side are drawn in the background unless crates is lower
MARKET_TARP_RECT = (48, 40, 272, 70)  # the tarp's extent (30g1: it is folded at +0.5 with `market_tarp(frac)`)


def _crate(g, x, y, w=22, h=12):
    r(g, x, y, w, h, 'wood2'); r(g, x, y, w, 1, 'wood3'); r(g, x, y + h - 1, w, 1, 'wood0')
    for yy in range(y + 3, y + h - 2, 4):
        r(g, x, yy, w, 1, 'wood1')
    r(g, x, y, 2, h, 'wood1'); r(g, x + w - 2, y, 2, h, 'wood1')


def _basket(g, x, y, kind, w=22):
    r(g, x, y + 4, w, 8, 'clay'); r(g, x, y + 4, w, 1, 'ochre')
    for xx in range(x + 1, x + w, 3):
        r(g, xx, y + 5, 1, 7, 'brick')
    col = {'orange': ('red2', 'gold'), 'banana': ('gold', 'sand'), 'tomato': ('red1', 'red2'), 'leaf': ('v3_leaf', 'v3_leaf2'), 'lemon': ('v3_leaf2', 'gold')}[kind]
    for k, xx in enumerate(range(x + 1, x + w - 3, 4)):
        ellipse(g, xx + 2, y + 3 - (k % 2), 2, 2, col[k % 2])
    r(g, x + 2, y + 2, w - 4, 2, col[0])


def market_stall(time='day', tarp=True, crates=3):
    """MARKET-STALL, 320 x 180: a street stall under a striped tarp in a street of the BAIRRO's kind (house fronts behind, paving, kerb), baskets of fruit and greens, hanging
    bananas and a price tag with scribbles only (no readable text: the plan has no signs). Foreground piece `market_counter_fg()` (counter, produce, balance scale): draw it AFTER the
    keeper, so the counter front covers his legs (2.0.0 defects 3b #2, 3e #6). Anchors: `MARKET_VENDOR`, `MARKET_CUSTOMERS`, `MARKET_BAG_SPOT`, `MARKET_COUNTER`.
    tarp: False draws the poles only (30g1: fold it with `market_tarp(frac)` pieces, frac 0 = fully drawn, 1 = folded to a roll on the left pole); crates: how many crates stand
    in the background (0-5, filling `MARKET_CRATE_SPOTS` in order; the rest are `market_crate()` pieces the vendor stacks). time: 'day' | 'dusk' (30g1)."""
    assert time in ('day', 'dusk') and 0 <= crates <= 5
    g = Geometry(); rng = random.Random(1930)
    sky = _sky(g, time, 30)
    r(g, 0, 28, 320, 90, 'plaster3')
    for (x0, x1, c, sc) in ((0, 98, 'clay', 'brick'), (98, 224, 'sand', 'ochre'), (224, 320, 'plaster2', 'plaster1')):                         # three house fronts behind
        r(g, x0, 26, x1 - x0, 92, c); r(g, x0, 26, x1 - x0, 4, sc)
    for (wx, wy) in ((12, 52), (76, 52), (232, 52), (292, 52)):
        r(g, wx, wy, 20, 24, 'wood0'); r(g, wx + 2, wy + 2, 16, 20, 'glass0'); r(g, wx + 2, wy + 2, 16, 6, 'glass1'); r(g, wx + 9, wy + 2, 2, 20, 'wood0')
    r(g, 140, 54, 40, 64, 'wood1'); r(g, 142, 56, 36, 62, 'wood0')                                           # a dark doorway behind the stall
    _plaza(g, 320, 118, 146, 5)
    for k in range(min(crates, 5)):
        _crate(g, *MARKET_CRATE_SPOTS[k])
    for px in (60, 260):                                                                                       # tarp poles
        r(g, px, 40, 3, 96, 'wood1'); r(g, px, 40, 1, 96, 'wood2')
    if tarp:
        _market_tarp(g, 0)
    r(g, 112, 70, 1, 12, 'steel1')
    for k in range(3):
        ellipse(g, 114 + k * 4, 84 + k * 2, 2, 5, 'gold')                                                     # hanging bananas
    r(g, 188, 72, 14, 10, 'cream'); r(g, 188, 72, 14, 1, 'ivory')
    for yy in (75, 78):
        r(g, 190, yy, 10, 1, 'steel1')                                                                         # the price tag: scribble lines, no letters
    if time == 'dusk':
        _grade_keep_sky(g, 'dusk', sky)
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < 180}
    return g


def _market_tarp(g, frac):
    """Tarp cloth: stripes red/ivory sagging between the poles; frac 0 full, up to 1 a roll on the left pole (steps of .25)."""
    x0, y0, x1, y1 = MARKET_TARP_RECT
    w = int((x1 - x0) * (1 - frac))
    if frac >= 1:
        r(g, x0 + 4, y0 + 2, 10, 8, 'red1'); r(g, x0 + 4, y0 + 2, 10, 1, 'ivory'); return
    xs = x0 + 12 if frac else x0
    if frac:
        r(g, x0, y0, max(w, 6), 4, 'wood0')
    sag = int(1 + 3 * (1 - frac))
    for xx in range(xs, xs + max(w, 4)):
        c = 'red1' if ((xx - x0) // 8) % 2 == 0 else 'ivory'
        r(g, xx, y0 + 2, 1, 22 - int(frac * 12), c)
        r(g, xx, y0 + 24 - int(frac * 12), 1, sag if (xx // 4) % 2 else 1, c)
    if frac:
        r(g, x0 + 4, y0 + 2, 10, 8, 'red1'); r(g, x0 + 4, y0 + 2, 10, 1, 'ivory')


def market_tarp(frac=0.0):
    """The tarp as a piece (320 x 180 canvas) for 30g1: draw over `market_stall(tarp=False)`; frac 0, .25, .5, .75, 1 (1 = the folded roll at the left pole)."""
    g = Geometry(); _market_tarp(g, frac); return g


def market_counter_fg(produce=True):
    """Counter with baskets and a balance scale on it, 320 x 180 canvas: draw AFTER the keeper and the customers' hands. The keeper's legs vanish behind the front panel."""
    g = Geometry(); x0, top, x1, foot = MARKET_COUNTER
    r(g, x0, top, x1 - x0, 4, 'wood3'); r(g, x0, top, x1 - x0, 1, 'ivory'); r(g, x0, top + 4, x1 - x0, foot - top - 4, 'wood1'); r(g, x0, top + 4, x1 - x0, 1, 'wood0')
    for xx in range(x0 + 6, x1 - 24, 34):
        r(g, xx, top + 8, 28, 12, 'wood2'); r(g, xx, top + 8, 28, 1, 'wood3')
    r(g, x0, foot - 1, x1 - x0, 1, 'wood0')
    if produce:
        for k, (bx, kind) in enumerate(((x0 + 6, 'orange'), (x0 + 30, 'banana'), (x0 + 118, 'tomato'), (x0 + 142, 'leaf'))):
            _basket(g, bx, top - 12, kind)
        r(g, x0 + 84, top - 18, 2, 18, 'steel1'); r(g, x0 + 76, top - 20, 18, 1, 'steel1')                    # a balance scale: post, beam, two pans
        r(g, x0 + 74, top - 12, 6, 1, 'steel2'); r(g, x0 + 90, top - 14, 6, 1, 'steel2'); line(g, (x0 + 76, top - 20), (x0 + 77, top - 12), .4, 'steel1'); line(g, (x0 + 93, top - 20), (x0 + 92, top - 14), .4, 'steel1')
    return g


def market_bag(fill=0):
    """A shopping bag on the counter, 4 fill levels (0 empty ... 3 full of produce, a lemon and a leaf out of the top); origin top-left, 16 x 18 (08f +3.0 'the bag fills')."""
    g = Geometry(); r(g, 1, 4, 14, 14, 'cream'); r(g, 1, 4, 14, 1, 'ivory'); r(g, 13, 4, 2, 14, 'sand'); r(g, 5, 0, 1, 5, 'sand'); r(g, 10, 0, 1, 5, 'sand'); r(g, 5, 0, 6, 1, 'sand')
    if fill >= 1:
        r(g, 3, 14, 10, 4, 'red1')
    if fill >= 2:
        r(g, 3, 10, 10, 4, 'gold'); ellipse(g, 6, 9, 2, 2, 'red2')
    if fill >= 3:
        r(g, 3, 6, 10, 4, 'v3_leaf'); ellipse(g, 9, 4, 2, 2, 'gold'); r(g, 7, 2, 3, 3, 'v3_leaf2')
    return g


def market_crate():
    """One crate (22 x 12) for the vendor to stack (30g1 +1.8) at `MARKET_CRATE_SPOTS`."""
    g = Geometry(); _crate(g, 0, 0); return g



# ============================================================================================ PROPS shared by several builders
# ---------------------------------------------------------------------------------------------- URNA-BOX (05c, 20e, 24a, 24f)
URNA_SIZE = (44, 36)
URNA_LABEL = ('URNA', (10, 22, 34, 30))      # label rectangle RELATIVE to the box origin (24 x 8; the text is 23 px wide)


def urna_box(label=True, light=0):
    """The ballot box as a piece (origin top-left, 44 x 36): grey body, slanted top with a small screen and a keypad, front plate for the label. Place it so that the
    centre of its label meets the centre of the plan's rectangle: origin = (cx - 22, y0 - 22), cx = (x0 + x1) // 2: 05c (372,100,396,108) -> origin (362, 78); 20e (252,92,280,100) -> (244, 70);
    24a/24f (148,100,172,108) -> (138, 78). The text lies inside every one of those rectangles. `label=False`: a plain plate. `light` 0..2: light on the screen (24f: the light narrows to the box)."""
    g = Geometry()
    r(g, 2, 14, 40, 22, 'steel2'); r(g, 2, 14, 40, 1, 'steel3'); r(g, 2, 35, 40, 1, 'steel1'); r(g, 2, 14, 1, 22, 'steel3'); r(g, 41, 14, 1, 22, 'steel0')
    poly(g, [(4, 14), (40, 14), (36, 6), (8, 6)], 'steel3'); r(g, 8, 6, 28, 1, 'ivory')
    r(g, 10, 8, 14, 5, 'black'); r(g, 11, 9, 12, 3, ['blue0', 'blue2', 'glass2'][max(0, min(2, light))])
    for k in range(3):
        for j in range(2):
            r(g, 27 + k * 3, 8 + j * 3, 2, 2, 'steel0')
    r(g, 8, 20, 28, 12, 'steel1'); r(g, 9, 21, 26, 10, 'cream')
    if label:
        _sign_text(g, URNA_LABEL[0], (10 + 0, 22, 34, 30), 'black')
    r(g, 0, 36, 44, 0, 'steel0')
    return g


# ---------------------------------------------------------------------------------------------- PODIUM / LECTERN (04c, 06b, 13a, 14c, 15a, 22b, 22e, 23a, 23b, 23g, 24b, 26b, 27b)
def podium_sign_rect(w=64):
    """Sign rectangle relative to the podium's origin: (8, 22, w - 8, 32) (10 rows high; 98 wide lettering needs w >= 114)."""
    return (8, 22, w - 8, 32)


def podium(w=64, sign=None, mics=2, flash=False):
    """A lectern as a piece: origin top-left; mic stands y 0-9, top slab y 10-13, front y 14-43, foot line y 44 (31 rows from foot to top: lectern height). `w` wide (>= 28).
    `sign`: text drawn on a board at `podium_sign_rect(w)` (the caller declares `ctx.sign(text, abs_rect)` with abs_rect = rect + origin; plan examples: 23a 'MINISTÉRIO PÚBLICO' (112,80,210,90) -> w 114,
    origin (104, 58); 23b 'CANDIDATO' (135,80,187,90) is the SAME lectern (w 114, origin (104, 58): the text is centred at 161 inside that rectangle); 23g: left (30,80,128,90) -> w 114 origin (22, 58), right 'CANDIDATO' (200,80,252,90) centre 226 -> w 114 origin (169, 58)). mics: 0-3 microphones (gooseneck). The speaker stands behind it with his
    legs hidden by the front: draw the podium AFTER the figure. Flags are `three_powers_flag(frame)` pieces beside it."""
    assert w >= 28
    g = Geometry()
    r(g, 0, 10, w, 4, 'wood3'); r(g, 0, 10, w, 1, 'ivory'); r(g, 1, 14, w - 2, 30, 'wood1'); r(g, 1, 14, w - 2, 1, 'wood0'); r(g, 1, 43, w - 2, 1, 'wood0')
    r(g, 3, 17, w - 6, 24, 'wood2'); r(g, 3, 17, w - 6, 1, 'wood3')
    xs = [w // 2] if mics == 1 else [w // 2 - 8, w // 2 + 8] if mics == 2 else [w // 2 - 12, w // 2, w // 2 + 12][:max(0, mics)]
    for mx in (xs if mics else []):
        r(g, mx, 3, 1, 7, 'steel1'); r(g, mx - 2, 1, 5, 2, 'steel0'); r(g, mx - 1, 0, 3, 1, 'steel2')
    if sign:
        x0, y0, x1, y1 = podium_sign_rect(w)
        r(g, x0 - 2, y0 - 2, x1 - x0 + 4, y1 - y0 + 4, 'wood0'); r(g, x0 - 1, y0 - 1, x1 - x0 + 2, y1 - y0 + 2, 'cream')
        _sign_text(g, sign, (x0, y0, x1, y1), 'black')
    return g


# ---------------------------------------------------------------------------------------------- STAGE (05f 1989, 07b 2002, 18a 2018, 28c 2022)
STAGE_SOLES = (106, 116)      # soles of the people on the platform (y): a 48-row figure's head top is then >= 58, below every banner text row (plan rects end at y 56); the crowd stands in front (soles 132-145); the truck bed is shallower: `STAGE_SOLES_TRUCK`
STAGE_SOLES_TRUCK = (106, 112)
STAGE_KINDS = ('truck', 'campaign', 'rally', 'victory')


def stage(kind='campaign', banner=None, time='day'):
    """Outdoor stage, 320 x 180; the platform surface is at y 90-118 (people stand with soles `STAGE_SOLES` 106-116, so their heads stay below the banner text, plan rects end at y 56), a mic bank at the front edge x 150-200.
    kind: 'truck' (05f: the platform is a truck bed, cab at the left, wheel arch) | 'campaign' (07b: wooden platform, two poles, room for allies) | 'rally' (18a: big stage with a
    BANK of microphones and flags, no banner) | 'victory' (28c: dark backdrop with gold trim, many flags). banner: list of (text, (x0, y0, x1, y1)) drawn on cloth between two
    poles; the cloth is made to cover every rectangle (+4 px): 05f [('LULA',(120,28,170,44)), ('1989',(128,46,182,56))]; 07b [('LULA',(120,28,170,38)), ('2002',(128,40,165,50))]. time: 'day' | 'dusk'."""
    assert kind in STAGE_KINDS and time in ('day', 'dusk')
    g = Geometry(); rng = random.Random(1989)
    sky = _sky(g, 'dusk' if (time == 'dusk' or kind == 'victory') else 'day', 70)
    for xx in range(-6, 320, 36):
        ellipse(g, xx + 14, 74, 22, 8, 'v3_leaf'); ellipse(g, xx + 16, 72, 14, 5, 'v3_leaf2')
    r(g, 0, 72, 320, 56, 'plaster3')
    if kind == 'victory':
        r(g, 24, 16, 272, 76, 'blue0'); r(g, 24, 16, 272, 2, 'gold'); r(g, 24, 90, 272, 2, 'gold')
        for k in range(9):
            r(g, 36 + k * 30, 20, 14, 68, 'blue1')
    elif kind == 'rally':
        r(g, 20, 24, 280, 68, 'steel0'); r(g, 20, 24, 280, 3, 'steel1')
        for k in range(8):
            r(g, 32 + k * 34, 30, 22, 58, 'steel1')
    for fx in ((60, 258) if kind in ('rally', 'victory') else (30, 290)):                                     # flags on poles
        r(g, fx, 20 if kind != 'campaign' else 40, 1, 72 if kind != 'campaign' else 52, 'steel1'); g.paste(three_powers_flag(0, 24, 16), fx + 1, 20 if kind != 'campaign' else 40)
    if kind == 'victory':
        for fx in (100, 220):
            r(g, fx, 26, 1, 66, 'steel1'); g.paste(three_powers_flag(2, 24, 16), fx + 1, 26)
    if banner:
        xs0 = min(b[1][0] for b in banner) - 6; xs1 = max(b[1][2] for b in banner) + 6
        ys0 = min(b[1][1] for b in banner) - 5; ys1 = max(b[1][3] for b in banner) + 5
        for px in (xs0 - 6, xs1 + 4):
            r(g, px, ys0 - 8, 2, 92 - ys0 + 8, 'wood1')
        r(g, xs0, ys0, xs1 - xs0, ys1 - ys0, 'red1'); r(g, xs0, ys0, xs1 - xs0, 1, 'red2'); r(g, xs0, ys1 - 1, xs1 - xs0, 1, 'red0')
        for text, rect in banner:
            _sign_text(g, text, rect, 'ivory')
    # the platform: a top surface to stand on (soles inside `STAGE_SOLES`), then its front face
    if kind == 'truck':
        r(g, 20, 100, 280, 14, 'wood2'); r(g, 20, 100, 280, 1, 'wood3'); r(g, 20, 114, 280, 14, 'wood1'); r(g, 20, 114, 280, 1, 'wood0')
        for xx in range(26, 296, 10):
            r(g, xx, 116, 1, 12, 'wood0')
        for yy in (106, 111):
            r(g, 20, yy, 280, 1, 'wood1')
        r(g, 0, 90, 22, 38, 'red0'); r(g, 0, 90, 22, 3, 'red1'); r(g, 3, 96, 14, 12, 'glass1')
    else:
        r(g, 14, 90, 292, 26, 'wood2'); r(g, 14, 90, 292, 1, 'wood3')
        for yy in range(96, 116, 6):
            r(g, 14, yy, 292, 1, 'wood1')
        r(g, 14, 116, 292, 12, 'wood0'); r(g, 14, 116, 292, 1, 'wood1')
        for xx in range(20, 300, 24):
            r(g, xx, 119, 14, 7, 'wood1')
    for mx in ((150, 162, 174, 186, 198) if kind == 'rally' else (170, 182) if kind != 'truck' else (176,)):  # the microphones
        md = 10 if kind == 'truck' else 0                                                                      # the truck platform is 10 rows lower
        r(g, mx, 78 + md, 1, 14 if md == 0 else 12, 'steel1'); r(g, mx - 2, 76 + md, 5, 2, 'steel0'); r(g, mx - 1, 75 + md, 3, 1, 'steel2')
    r(g, 0, 128, 320, 18, 'plaster3'); r(g, 0, 128, 320, 1, 'plaster2')
    r(g, 0, 146, 320, 3, 'plaster1'); r(g, 0, 149, 320, 31, 'steel0')
    for xx in range(0, 320, 38):
        r(g, xx, 163, 17, 2, 'plaster3')
    if kind == 'truck':
        for wx in (60, 240):
            ellipse(g, wx, 124, 12, 12, 'black'); ellipse(g, wx, 124, 5, 5, 'steel1')
    if time == 'dusk' or kind == 'victory':
        _grade_keep_sky(g, 'dusk', sky)
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < 180}
    return g


# ---------------------------------------------------------------------------------------------- TV-SET prop (05h, 07a, 11a, 15c, 26h) and WALL-CALENDAR, DOC-KIT
def tv_set_prop(x, y, w=56, h=34, aerial=True, bracket=False, on=False):
    """A TV set drawn at (x, y) = top-left of the CABINET/body on a 320 x 180 canvas, with ITS OWN AERIAL attached to the set (D4). Returns (Geometry, screen_rect (x0, y0, x1, y1)).
    The screen is `w - 12` x `h - 12` (so w 56, h 34 holds the 2002 caption x 140-170, y 52-60 if placed at x 128, y 44: screen (134,50,178,66)). bracket=True: a wall bracket under it
    (07a, 15c); False: no support (put it on a shelf or table of the scene). Pair with `tv_set_prop_fg(rect)` for the bezel over the content."""
    g = Geometry()
    r(g, x, y, w, h, 'wood0'); r(g, x + 1, y + 1, w - 2, 1, 'wood2'); r(g, x + 3, y + 3, w - 6, h - 6, 'black')
    sx0, sy0, sx1, sy1 = x + 6, y + 6, x + w - 6, y + h - 6
    r(g, sx0, sy0, sx1 - sx0, sy1 - sy0, 'blue2' if on else 'blue0')
    r(g, sx0, sy0, 1, sy1 - sy0, 'black')
    mx = x + w // 2
    if aerial:
        line(g, (mx, y), (mx - 9, y - 14), .5, 'steel2'); line(g, (mx, y), (mx + 10, y - 13), .5, 'steel2'); r(g, mx - 3, y - 2, 6, 2, 'steel1')
    if bracket:
        r(g, x + 6, y + h, 3, 6, 'steel1'); r(g, x + w - 9, y + h, 3, 6, 'steel1'); r(g, x + 2, y + h + 5, w - 4, 2, 'steel0')
    return g, (sx0, sy0, sx1, sy1)


def tv_set_prop_fg(rect):
    """Glass glare and bezel over the content of a `tv_set_prop` screen (canvas coordinates of the rect it returned)."""
    g = Geometry(); x0, y0, x1, y1 = rect
    r(g, x0 - 3, y0 - 3, x1 - x0 + 6, 3, 'black'); r(g, x0 - 3, y1, x1 - x0 + 6, 3, 'black'); r(g, x0 - 3, y0, 3, y1 - y0, 'black'); r(g, x1, y0, 3, y1 - y0, 'black')
    poly(g, [(x0 + 1, y0 + 1), (x0 + 7, y0 + 1), (x0 + 1, y0 + 7)], 'steel1')
    return g


def calendar_date_ring(rect, text):
    """Default ring of `wall_calendar`: (cx, cy, rx, ry) circling the FIRST glyph of `text` (the date numeral: '2' in '2 DE DEZEMBRO DE 2015'), never the word after it. The text is
    centred in `rect` exactly as `_sign_text` draws it; the glyph is 5 px wide x 7 rows, the next word starts 9 px after its origin, so rx 5 (ring x -3..+7) clears it."""
    x0, y0, x1, y1 = rect
    tx = x0 + (x1 - x0 - text_width(text)) // 2; ty = y0 + (y1 - y0 - 7) // 2
    return (tx + 2, ty + 3, 5, 6)


def wall_calendar(rect, text, circle=None, grid=True, header='red1'):
    """A wall calendar page on a 320 x 180 canvas around the sign rectangle `rect` = (x0, y0, x1, y1) of the plan: the paper covers the rectangle +4 px (+9 above for the binding), the
    text (any of 11g '2012' / '2011' / '2010' at (118,42,139,49), 13d '2 DE DEZEMBRO DE 2015' at (70,40,250,90), 17e '2018', 19a '2019', 22a 'ABRIL 2020', 22j 'OUTUBRO 2022', 26d 'OFERTAS',
    31f 'OUTUBRO 2026' at (123,18,192,25)) is drawn centred in it. Flip pages by drawing another call at the same rect (the pages flip in place). grid: the day grid in the free space above/below the
    text when the rectangle is at least 24 rows high. circle: (cx, cy, rx, ry) of a hand-drawn ring (13d: the day circled at +0.5; 22j: days 2 and 4; 31f: dashed), or 'date' = `calendar_date_ring(rect, text)`, the ring around the first
    glyph of the text (the date numeral, never the word after it); None draws no ring."""
    g = Geometry(); x0, y0, x1, y1 = rect
    r(g, x0 - 6, y0 - 12, x1 - x0 + 12, y1 - y0 + 18, 'wood0'); r(g, x0 - 5, y0 - 11, x1 - x0 + 10, y1 - y0 + 16, 'ivory')
    r(g, x0 - 5, y0 - 11, x1 - x0 + 10, 6, header); r(g, x0 - 5, y0 - 11, x1 - x0 + 10, 1, 'red2')
    r(g, (x0 + x1) // 2 - 1, y0 - 14, 2, 4, 'steel1')
    if grid and y1 - y0 >= 24:
        for yy in range(y1 - 14, y1 + 3, 4):
            for xx in range(x0 + 2, x1 - 3, 8):
                r(g, xx, yy, 4, 1, 'steel1')
    _sign_text(g, text, rect, 'black')
    if circle:
        cx, cy, rx, ry = calendar_date_ring(rect, text) if circle == 'date' else circle
        import math
        for k in range(48):
            t = k * math.tau / 48
            r(g, round(cx + rx * math.cos(t)), round(cy + ry * math.sin(t)), 1, 1, 'red1')                          # a hand-drawn ring: outline only, the day number stays readable
    return g


def doc_folder(text, rect, color='sand'):
    """A folder cover on a 320 x 180 canvas: card of the colour covering the rectangle +6 px, a tab, the title lettering in the rectangle (14b 'DECRETOS ORÇAMENTÁRIOS' (42,60,169,70) and
    'PEDALADAS FISCAIS' (171,60,266,70); 16c 'CONTRATOS · PETROBRAS' (112,80,229,90); 16f etc.). Draw them one after another."""
    g = Geometry(); x0, y0, x1, y1 = rect
    r(g, x0 - 6, y0 - 10, x1 - x0 + 12, y1 - y0 + 24, color); r(g, x0 - 6, y0 - 10, x1 - x0 + 12, 1, 'ivory'); r(g, x0 - 6, y1 + 13, x1 - x0 + 12, 1, 'wood1')
    r(g, x0 - 6, y0 - 14, 26, 4, color); r(g, x0 - 6, y0 - 14, 26, 1, 'ivory')
    r(g, x0 - 3, y0 - 2, x1 - x0 + 6, y1 - y0 + 4, 'ivory'); _sign_text(g, text, rect, 'black')
    return g


def doc_stamp(text, rect):
    """A rubber-stamp mark (20c 'ANULADA' (100,60,220,72)): red frame and lettering over the page, slightly faded; 320 x 180 canvas."""
    g = Geometry(); x0, y0, x1, y1 = rect
    for (a, b, c, d) in ((x0, y0, x1, y0 + 1), (x0, y1 - 1, x1, y1), (x0, y0, x0 + 1, y1), (x1 - 1, y0, x1, y1)):
        r(g, a, b, c - a, d - b, 'red1')
    _sign_text(g, text, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), 'red1')
    return g


def doc_page(lines=5, rect=(110, 40, 210, 110), highlight=None):
    """A document page of glyph bars (grey lines of text, no readable words) on a 320 x 180 canvas covering `rect`; `highlight`: row index drawn with a yellow bar (`highlight_bar`)."""
    g = Geometry(); x0, y0, x1, y1 = rect
    r(g, x0, y0, x1 - x0, y1 - y0, 'ivory'); r(g, x0, y0, x1 - x0, 1, 'cream'); r(g, x0, y1 - 1, x1 - x0, 1, 'plaster2')
    rng = random.Random(x0 * 7 + lines)
    step = max(4, (y1 - y0 - 12) // max(1, lines))
    for k in range(lines):
        yy = y0 + 6 + k * step
        if highlight == k:
            r(g, x0 + 4, yy - 1, x1 - x0 - 8, 4, 'gold')
        r(g, x0 + 5, yy, rng.randrange(max(8, (x1 - x0) // 2), x1 - x0 - 9), 2, 'steel1')
    return g



# ============================================================================================ TRUCK-BED (02c, callback 32a, 32b)
TRUCK_BED_FRAME = (80, 64, 240, 153)          # the region seen at the 2x framing (zoom centred on (150, 100)): everything the shot needs lies inside it
TRUCK_BED_ANCHORS = dict(mother=(128, 68), seat_boy=(160, 93), seat_boy_crop=17, siblings=[(148, 90), (176, 90), (198, 90)], bundle=(218, 100), pot=(222, 114), cloth=(160, 106),
                         sacks=[(170, 113, 10, 'sand'), (188, 114, 11, 'ochre'), (212, 113, 10, 'sand')])   # figures' sprite origins as 02c places them; the boy of 32a and Lula of 32b sit at `seat_boy`
TRUCK_BED_TIMES = ('dawn', 'sunrise', 'day')
_TB_SKIES = {'dawn': ('#4d6f94', '#f1b383'), 'sunrise': ('#46689a', '#ffc47a'), 'day': ('#6f9ab4', '#c9dac6')}


def truck_bed(time='dawn'):
    """TRUCK-BED, 320 x 180 (drawn for a 2x framing: region `TRUCK_BED_FRAME`): inside the bed at child height, the canvas tarp stretched over a bow with its hem, grommets and knotted ropes,
    the far side board, plank floor, tailgate post at the right; no road visible. time: 'dawn' (02c: IDENTICAL to scene_02.bed_bg(), a test compares them) | 'sunrise' (32a, 32b: a
    warmer sky and the sun's disc rising behind the far board at about x 196) | 'day'. The props (sacks, pot, cloth, bundle, cloud strip) are `truck_bed_props()` and
    `truck_bed_cloud(i)`; figures at `TRUCK_BED_ANCHORS`: mother (02c), the boy / Lula (32a, 32b) at `seat_boy` with crop 17 (the bed hides the legs)."""
    assert time in TRUCK_BED_TIMES
    g = Geometry(); rng = random.Random(7)
    sky_gradient(g, *_TB_SKIES[time], 0, 104, 8)
    if time == 'sunrise':
        ellipse(g, 196, 94, 16, 16, '#ffd9a0'); ellipse(g, 196, 94, 11, 11, '#fff0cc')
    edge = [(0, 100), (40, 92), (70, 88), (100, 78), (122, 68), (142, 58), (156, 52)]
    poly(g, [(0, 0), (160, 0)] + edge[::-1], 'plaster2')
    for (ax, ay), (bx, by_) in zip(edge, edge[1:]):
        line(g, (ax, ay), (bx, by_), 1.0, 'plaster0'); line(g, (ax, ay - 2), (bx, by_ - 2), .5, 'plaster3')
    for (ax, ay) in edge[1:-1]:
        r(g, ax - 1, ay + 2, 3, 3, 'steel2'); r(g, ax, ay + 3, 1, 1, 'steel0')
    for (ax, ay, n) in ((70, 88, 8), (122, 68, 10)):
        line(g, (ax, ay + 4), (ax - 1, ay + 4 + n), .5, 'wood2'); r(g, ax - 2, ay + 4 + n, 3, 2, 'wood3')
    r(g, 156, 0, 5, 56, 'wood1'); r(g, 156, 0, 1, 56, 'wood3'); r(g, 160, 0, 1, 56, 'wood0')
    r(g, 0, 94, 320, 10, 'wood0'); r(g, 0, 94, 320, 2, 'wood2')
    r(g, 0, 104, 320, 90, 'wood1')
    for yy in range(108, 190, 12):
        r(g, 0, yy, 320, 1, 'wood0'); r(g, 0, yy + 1, 320, 1, 'wood2')
    for xx in range(4, 320, 44):
        r(g, xx, 104, 1, 90, 'wood0')
    r(g, 232, 0, 90, 104, 'wood0'); r(g, 232, 0, 2, 104, 'wood2')
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < 180}
    return g


def truck_bed_props(pot=True, sacks=True, cloth=False, bundle=True):
    """The props of 02c as pieces `(name, Geometry, x, y)` in draw order (same drawings as scene_02): sacks in front of the seated children, the tin pot, the red cloth the
    mother spreads over the two smaller children (+1.5 s in 02c; for 32a/32b leave it out), the bundle on the boy's lap."""
    out = []
    if pot:
        p = Geometry(); r(p, 0, 0, 9, 6, 'steel0'); r(p, 0, 0, 9, 1, 'steel1'); out.append(('pot', p, *TRUCK_BED_ANCHORS['pot']))
    if sacks:
        for k, (x, y, w, c) in enumerate(TRUCK_BED_ANCHORS['sacks']):
            sk = Geometry(); ellipse(sk, 0, 0, w, 5, c); r(sk, -w // 2, -3, w, 1, 'cream'); out.append((f'sack{k}', sk, x, y))
    if cloth:
        cl = Geometry(); r(cl, 0, 0, 56, 9, 'red1'); r(cl, 0, 0, 56, 2, 'red2'); r(cl, 0, 7, 56, 2, 'red0')
        for xx in range(4, 54, 8):
            r(cl, xx, 3, 3, 3, 'plaster3')
        out.append(('cloth', cl, *TRUCK_BED_ANCHORS['cloth']))
    if bundle:
        b = Geometry(); ellipse(b, 4, 4, 5, 4, 'plaster3'); r(b, 0, 4, 9, 1, 'plaster1'); out.append(('bundle', b, *TRUCK_BED_ANCHORS['bundle']))
    return out


def truck_bed_cloud(i=0):
    """A cloud of the sliding sky strip (02c from +2.2 s the truck rolls: move it 8 px left over the rest of the shot): i 0 at (180,30), i 1 at (210,56); origin = ellipse centre."""
    w = (30, 22)[i % 2]
    c = Geometry(); ellipse(c, 0, 0, w, 4, '#f3cdb4'); ellipse(c, 6, -3, w * .4, 3, '#f8e0c8')
    return c, [(180, 30), (210, 56)][i % 2]



# ============================================================================================ CLASSROOM (10g, 32h), VACCINATION-ROOM (26g, 32h), COURT-FLOOR, CAR, URN-KEYPAD
CLASSROOM_DOOR = (40, 56, 76, 118)             # the door of 10g seen from inside: 36 x 62; the leaf swings INTO the room (`classroom_door_leaf(frac)`)
CLASSROOM_BOARD = (112, 34, 252, 84)           # the chalkboard (no chalk, no ledge object)
CLASSROOM_TEACHER = (128, 70)                  # sprite origin of the teacher (soles at 118)... draw her in front of the board
CLASSROOM_DESK_ROWS = (130, 146)               # foot lines of the two desk rows (x 110-300); the left aisle x 0-104 is free for the girl to walk in (soles 118-145)
CLASSROOM_WINDOW = (264, 56, 304, 98)          # window: sill 20 above the wall base, top 62 above


def _classroom(g, ox=0, door='closed'):
    r(g, ox, 0, 320, 180, 'blue3'); r(g, ox, 0, 320, 8, 'steel2'); r(g, ox, 8, 320, 1, 'steel1')
    r(g, ox, 90, 320, 28, 'blue2'); r(g, ox, 90, 320, 1, 'ivory')
    r(g, ox, 118, 320, 62, 'floor1'); r(g, ox, 118, 320, 2, 'floor0')
    for yy in (126, 140, 158):
        r(g, ox, yy, 320, 1, 'floor0')
    for xx in range(0, 320, 40):
        r(g, ox + xx, 119, 1, 61, 'floor0')
    x0, y0, x1, y1 = CLASSROOM_DOOR
    r(g, ox + x0 - 3, y0 - 3, x1 - x0 + 6, y1 - y0 + 3, 'wood0')
    if door == 'closed':
        r(g, ox + x0, y0, x1 - x0, y1 - y0, 'wood1'); r(g, ox + x0 + 4, y0 + 4, x1 - x0 - 8, 22, 'wood2'); r(g, ox + x0 + 4, y0 + 31, x1 - x0 - 8, 25, 'wood2'); r(g, ox + x1 - 8, y0 + 30, 3, 4, 'gold')
    else:
        r(g, ox + x0, y0, x1 - x0, y1 - y0, 'ivory'); r(g, ox + x0, y0, x1 - x0, 20, 'glass2'); r(g, ox + x0, 100, x1 - x0, 18, 'plaster3')       # the bright corridor outside
    bx0, by0, bx1, by1 = CLASSROOM_BOARD
    r(g, ox + bx0 - 3, by0 - 3, bx1 - bx0 + 6, by1 - by0 + 6, 'wood1'); r(g, ox + bx0, by0, bx1 - bx0, by1 - by0, 'metal1'); r(g, ox + bx0, by0, bx1 - bx0, 1, 'metal2')
    r(g, ox + bx0 - 3, by1 + 3, bx1 - bx0 + 6, 2, 'wood0')
    wx0, wy0, wx1, wy1 = CLASSROOM_WINDOW
    r(g, ox + wx0, wy0, wx1 - wx0, wy1 - wy0, 'wood0'); r(g, ox + wx0 + 2, wy0 + 2, wx1 - wx0 - 4, wy1 - wy0 - 4, 'glass1'); r(g, ox + wx0 + 2, wy0 + 2, wx1 - wx0 - 4, 8, 'glass2'); r(g, ox + (wx0 + wx1) // 2 - 1, wy0 + 2, 2, wy1 - wy0 - 4, 'wood0')
    r(g, ox + wx0 - 2, wy1, wx1 - wx0 + 4, 3, 'ivory')
    r(g, ox + 84, 54, 16, 22, 'ivory'); r(g, ox + 85, 55, 14, 20, 'sand'); r(g, ox + 88, 60, 8, 1, 'steel1'); r(g, ox + 88, 64, 8, 1, 'steel1')                  # a drawing on the wall
    for i, fb in enumerate(CLASSROOM_DESK_ROWS):
        for k in range(6 - i):
            x = ox + 114 + k * 31 + i * 8
            r(g, x, fb - 24, 24, 4, 'wood3'); r(g, x, fb - 24, 24, 1, 'ivory'); r(g, x, fb - 20, 24, 3, 'wood1')
            r(g, x + 1, fb - 17, 2, 17, 'wood0'); r(g, x + 21, fb - 17, 2, 17, 'wood0')
            r(g, x + 5, fb - 16, 14, 4, 'wood2')


def classroom(door='closed'):
    """CLASSROOM (10g SCHOOL-DOOR, interior view of the door opening onto a modest classroom): 320 x 180, blue wall with a dado, wood floor, the door at the left
    `CLASSROOM_DOOR` (36 x 62), a plain chalkboard `CLASSROOM_BOARD` with NO chalk object, a window `CLASSROOM_WINDOW`, two rows of desks (tops 24 rows above their foot lines
    `CLASSROOM_DESK_ROWS`) at the right; the aisle at the left is free. door: 'closed' | 'open' (the doorway shows the bright corridor; the leaf is `classroom_door_leaf(frac)`: 10g +0.0
    the door opens: draw `door='open'` with the leaf stepped from frac 0 (closed) to 1 (open); +1.0 the girl walks in from the doorway (soles 118 -> 130); +2.0 the teacher at
    `CLASSROOM_TEACHER` greets her). No signs."""
    assert door in ('closed', 'open')
    g = Geometry(); _classroom(g, 0, door)
    return g


def classroom_door_leaf(frac):
    """The classroom door leaf swinging into the room, hinged at its left edge: frac 0 closed (fills the door), 1 open (a thin slice); steps of .25. 320 x 180 canvas."""
    x0, y0, x1, y1 = CLASSROOM_DOOR
    g = Geometry(); w = max(3, round((x1 - x0) * (1 - frac))); s = round(frac * 9)
    poly(g, [(x0, y0), (x0 + w, y0 + s), (x0 + w, y1 - s), (x0, y1)], 'wood1')
    if w > 14:
        r(g, x0 + 3, y0 + 4 + s, w - 6, 20, 'wood2'); r(g, x0 + 3, y0 + 31, w - 6, 24 - s, 'wood2')
    if frac == 0:
        r(g, x1 - 8, y0 + 30, 3, 4, 'gold')
    return g


# ---------------------------------------------------------------------------------------------- VACCINATION-ROOM
VACC_SIGN = ('SALA DE VACINAÇÃO', (122, 20, 218, 28))       # 26g door sign (plan rectangle)
VACC_SUS = ('SUS', (220, 20, 250, 28))                       # 26g plaque
VACC_QUEUE = [(34, 142), (60, 142), (86, 142), (112, 142), (138, 142)]   # soles of the five people; they step forward by one place (+1.8) and the next sits (+3.2) at `VACC_CHAIR`
VACC_NURSE = (252, 70)                                       # sprite origin of the nurse behind the table (soles 118; the table front covers the legs)
VACC_CHAIR = (186, 76)                                       # where the person being vaccinated sits (sprite origin of the 'sit' pose; seat line y+34 = 110 = the seat of the chair drawn by the set, soles y+45 = 121 <= 145; the chair legs end at row 121)
VACC_CHAIR_SOLES = VACC_CHAIR[1] + 45                        # 121: the soles of a seated adult at VACC_CHAIR (the rule: <= 145)
VACC_TABLE = (214, 98, 292, 122)                              # table: top y 98 front to 122 (24 rows): vial, cotton on it (`vaccination_table_fg`)


def _vacc(g, ox=0, signs=True):
    r(g, ox, 0, 320, 180, 'glass2'); r(g, ox, 0, 320, 8, 'ivory'); r(g, ox, 8, 320, 1, 'glass1')
    r(g, ox, 90, 320, 28, 'ivory'); r(g, ox, 90, 320, 1, 'glass1')
    r(g, ox, 118, 320, 62, 'steel2'); r(g, ox, 118, 320, 2, 'steel1')
    for yy in range(130, 180, 12):
        r(g, ox, yy, 320, 1, 'steel1')
    for xx in range(0, 320, 24):
        for yy in range(120, 180, 12):
            r(g, ox + xx + ((yy // 12) % 2) * 12, yy, 1, 12, 'steel1')
    r(g, ox + 144, 56, 36, 62, 'wood0'); r(g, ox + 146, 58, 32, 60, 'ivory'); r(g, ox + 146, 58, 32, 6, 'cream')                                            # the door (closed, white)
    r(g, ox + 172, 88, 3, 4, 'gold')
    r(g, ox + 118, 15, 102, 16, 'wood0'); r(g, ox + 119, 16, 100, 14, 'green'); r(g, ox + 119, 16, 100, 1, 'v3_leaf2')
    if signs:
        _sign_text(g, VACC_SIGN[0], (ox + VACC_SIGN[1][0], 20, ox + VACC_SIGN[1][2], 28), 'ivory')
    r(g, ox + 222, 15, 28, 16, 'wood0'); r(g, ox + 223, 16, 26, 14, 'blue1'); r(g, ox + 223, 16, 26, 1, 'blue2')
    if signs:
        _sign_text(g, VACC_SUS[0], (ox + VACC_SUS[1][0], 20, ox + VACC_SUS[1][2], 28), 'ivory')
    r(g, ox + 20, 40, 60, 30, 'ivory'); r(g, ox + 20, 40, 60, 2, 'red1'); r(g, ox + 24, 48, 22, 1, 'steel1'); r(g, ox + 24, 53, 30, 1, 'steel1'); r(g, ox + 24, 58, 18, 1, 'steel1')   # a poster with glyph bars, no text
    for (qx, qy) in VACC_QUEUE:
        r(g, ox + qx - 8, qy + 4, 16, 1, 'steel1')                                                              # floor marks of the queue
    r(g, ox + 190, VACC_CHAIR[1] + 34, 14, 3, 'wood2'); r(g, ox + 192, VACC_CHAIR[1] + 37, 2, VACC_CHAIR_SOLES - VACC_CHAIR[1] - 37, 'wood1'); r(g, ox + 200, VACC_CHAIR[1] + 37, 2, VACC_CHAIR_SOLES - VACC_CHAIR[1] - 37, 'wood1'); r(g, ox + 196, 98, 3, 12, 'wood1')       # the patient's chair: seat at the seat line of VACC_CHAIR, legs end on the soles row


def vaccination_room(signs=True):
    """VACCINATION-ROOM (26g, and the right half of the track of 32h): 320 x 180, a clinic: white door under the sign board `VACC_SIGN = ('SALA DE VACINAÇÃO', (122,20,218,28))` and the
    plaque `VACC_SUS = ('SUS', (220,20,250,28))`, tiled floor with queue marks along `VACC_QUEUE` (five people 'back' kinds, +1.8 they step forward), the patient's chair `VACC_CHAIR = (186, 76)` (a seated adult 'sit' sprite placed there has its seat on the chair's seat and its soles at row 121, `VACC_CHAIR_SOLES`), a
    poster of glyph bars. The nurse stands at `VACC_NURSE` behind the table `VACC_TABLE`: draw `vaccination_table_fg()` AFTER her (the front covers her legs; vial and cotton on the
    top). TL plate zone (x 6-110, y 6-40) holds only the poster's edge. signs=False blanks both boards."""
    g = Geometry(); _vacc(g, 0, signs); return g


def vaccination_table_fg():
    g = Geometry(); x0, top, x1, foot = VACC_TABLE
    r(g, x0, top, x1 - x0, 4, 'steel3'); r(g, x0, top, x1 - x0, 1, 'f2_white'); r(g, x0, top + 4, x1 - x0, foot - top - 4, 'steel1'); r(g, x0, top + 4, x1 - x0, 1, 'steel2')
    r(g, x0 + 4, top + 8, 30, 12, 'steel2'); r(g, x0 + 4, top + 8, 30, 1, 'steel3'); r(g, x0 + 42, top + 8, 30, 12, 'steel2'); r(g, x0 + 42, top + 8, 30, 1, 'steel3')
    r(g, x0 + 10, top - 6, 3, 6, 'glass2'); r(g, x0 + 10, top - 7, 3, 1, 'red1'); r(g, x0 + 10, top - 4, 3, 2, 'blue2')                  # the vial
    r(g, x0 + 20, top - 3, 6, 3, 'ivory'); r(g, x0 + 21, top - 4, 4, 1, 'f2_white')                                                       # cotton
    return g


def school_clinic_track():
    """The lateral track of 32h: 640 x 180, the classroom (x 0-320, pupils' desks, the board) then the vaccination room (x 320-640, nurse, table); the join is a plain doorway at x 320.
    Pan by x only (no scale): +0.0 track starts at x 0, +0.8 the class passes, +1.4 the nurse (`VACC_NURSE` + 320) passes. No signs (`signs=False` for the clinic's boards)."""
    g = Geometry(); _classroom(g, 0, 'closed'); _vacc(g, 320, False)
    r(g, 316, 0, 8, 180, 'wood1'); r(g, 316, 0, 1, 180, 'wood3'); r(g, 323, 0, 1, 180, 'wood0')
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 640 and 0 <= xy[1] < 180}
    return g


# ---------------------------------------------------------------------------------------------- COURT-FLOOR (19e, 24c1-e, 24d)
COURT_DESK_POS = {'L': (24, 92), 'R': (212, 88)}             # top-left of `court_desk(side)`: the prosecutors' desk at the left, the judge's bench at the right
COURT_LINE_X = 160                                           # the painted floor line runs along x 160, y 120-176
COURT_STATES = ('whole', 'broken', 'none')


def court_floor(line='whole', desks=True):
    """COURT-FLOOR, 320 x 180: a hall with a wood floor, a panelled wall, two windows, a flag; a white line painted on the floor along x `COURT_LINE_X` between two tables. line: 'whole'
    (19e: Moro walks across it) | 'broken' (24c1, 24c2: the line has a gap in the middle y 138-152; the pieces separate at +1.3) | 'none'. desks: draw the two desks (24c1 draws them as
    pieces: `court_desk('L')` and `('R')` at `COURT_DESK_POS`, sliding in at +0.3). 24d: voters fill the centre; 24e: a bailiff lays `court_stanchion()` posts and `court_tape(x0, x1)` along the line.
    No signs."""
    assert line in COURT_STATES
    g = Geometry()
    r(g, 0, 0, 320, 180, 'plaster3'); r(g, 0, 0, 320, 8, 'plaster2'); r(g, 0, 8, 320, 1, 'plaster1')
    r(g, 0, 84, 320, 34, 'wood1'); r(g, 0, 84, 320, 2, 'wood3')
    for xx in range(6, 320, 26):
        r(g, xx, 90, 20, 22, 'wood2'); r(g, xx, 90, 20, 1, 'wood3')
    for wx in (40, 250):
        r(g, wx, 30, 30, 46, 'wood0'); r(g, wx + 2, 32, 26, 42, 'glass1'); r(g, wx + 2, 32, 26, 10, 'glass2'); r(g, wx + 14, 32, 2, 42, 'wood0')
    r(g, 150, 22, 20, 28, 'wood0'); r(g, 152, 24, 16, 24, 'blue0'); ellipse(g, 160, 36, 5, 5, 'gold')                                 # a seal
    r(g, 0, 118, 320, 62, 'floor1'); r(g, 0, 118, 320, 2, 'floor0')
    for yy in (126, 140, 158):
        r(g, 0, yy, 320, 1, 'floor0')
    for xx in range(0, 320, 40):
        for yy in range(120, 180, 20):
            r(g, xx + (yy // 20 % 2) * 20, yy, 1, 20, 'floor0')
    if line != 'none':
        for yy in range(120, 178):
            if line == 'broken' and 138 <= yy < 152:
                continue
            r(g, COURT_LINE_X - 1, yy, 3, 1, 'ivory')
    if desks:
        for side in ('L', 'R'):
            g.paste(court_desk(side), *COURT_DESK_POS[side])
    return g


def court_desk(side='L'):
    """A desk piece (origin top-left): 'L' the prosecutors' table (80 x 40 with papers), 'R' the judge's bench (raised, 96 x 46 with a gavel block). Table tops 24 rows above their feet."""
    g = Geometry()
    if side == 'L':
        r(g, 0, 0, 80, 4, 'wood3'); r(g, 0, 0, 80, 1, 'ivory'); r(g, 0, 4, 80, 20, 'wood1'); r(g, 0, 4, 80, 1, 'wood0'); r(g, 4, 8, 72, 12, 'wood2')
        r(g, 10, -3, 12, 3, 'ivory'); r(g, 30, -2, 10, 2, 'ivory'); r(g, 56, -4, 2, 4, 'steel1'); r(g, 55, -5, 4, 1, 'steel0')
        r(g, 0, 24, 80, 1, 'wood0')
    else:
        r(g, 0, 0, 96, 5, 'wood3'); r(g, 0, 0, 96, 1, 'ivory'); r(g, 0, 5, 96, 31, 'wood1'); r(g, 0, 5, 96, 1, 'wood0'); r(g, 6, 12, 84, 20, 'wood2')
        r(g, 40, -3, 8, 3, 'wood0'); r(g, 52, -1, 8, 1, 'wood2'); r(g, 0, 36, 96, 1, 'wood0')
    return g


def court_stanchion():
    """A stanchion post (origin top-left, 6 x 18) for the bailiff of 24e."""
    g = Geometry(); r(g, 2, 0, 2, 14, 'steel1'); r(g, 1, 0, 4, 2, 'gold'); r(g, 0, 14, 6, 2, 'steel0'); r(g, 1, 16, 4, 2, 'steel0')
    return g


def court_tape(x0, x1, y=150):
    """The tape between posts: a red line from x0 to x1 at height `y - 10` (320 x 180 canvas); grow x1 as the bailiff walks (24e +2.4)."""
    g = Geometry(); line(g, (x0, y - 10), (x1, y - 10), .8, 'red1'); return g


# ---------------------------------------------------------------------------------------------- CAR (11b, 17a, 25c, 27h)
CAR_KINDS = ('sedan', 'pf', 'ambulance')


def car(kind='sedan', size='mid', wheel=0):
    """A car in side view facing RIGHT (flip it with `common.flip` to face left), origin top-left, wheels included. kind: 'sedan' (11b arrives; 27h stops: dark) | 'pf' (17a: a Polícia
    Federal car, white with a dark blue stripe, no lettering) | 'ambulance' (25c: white box body, red stripe, a light bar OFF, no lettering). size: 'far' 48 x 20 (distance) | 'mid'
    96 x 40 | 'near' 144 x 60. wheel 0 or 1: the hubs' spokes turn between the two frames (alternate them while the car moves: 6-8 fps)."""
    assert kind in CAR_KINDS and size in ('far', 'mid', 'near')
    g = Geometry()
    if kind == 'ambulance':
        r(g, 0, 4, 48, 11, 'f2_white'); r(g, 0, 4, 48, 1, 'f2_whiteshade'); r(g, 30, 1, 14, 3, 'f2_white'); r(g, 4, 9, 40, 2, 'red1'); r(g, 36, 6, 7, 4, 'glass1'); r(g, 12, 0, 10, 2, 'steel1')
        r(g, 0, 14, 48, 1, 'steel0')
    elif kind == 'pf':
        r(g, 0, 8, 48, 7, 'f2_white'); r(g, 8, 3, 28, 6, 'f2_white'); r(g, 10, 4, 10, 4, 'glass1'); r(g, 21, 4, 12, 4, 'glass1'); r(g, 0, 11, 48, 2, 'blue0'); r(g, 0, 14, 48, 1, 'steel0')
    else:
        r(g, 0, 8, 48, 7, 'steel0'); r(g, 8, 3, 28, 6, 'steel1'); r(g, 10, 4, 10, 4, 'glass1'); r(g, 21, 4, 12, 4, 'glass1'); r(g, 0, 8, 48, 1, 'steel2'); r(g, 0, 14, 48, 1, 'black')
    r(g, 45, 10, 3, 2, 'gold'); r(g, 0, 10, 2, 2, 'red1')
    for wx in (9, 36):
        ellipse(g, wx + 2, 16, 4, 4, 'black'); ellipse(g, wx + 2, 16, 2, 2, 'steel1')
        if wheel:
            r(g, wx + 1, 14, 1, 4, 'steel2')
        else:
            r(g, wx - 0, 16, 4, 1, 'steel2')
    k = {'far': 1, 'mid': 2, 'near': 3}[size]
    return resize(g, k) if k > 1 else g


# ---------------------------------------------------------------------------------------------- URN-KEYPAD (31g, 32j)
URN_KEYS = {}
URN_CONFIRMA = (190, 124, 252, 144)           # the green CONFIRMA key (32j: the finger presses it at +0.5)


def urn_keypad(pressed=None, flash=False):
    """URN-KEYPAD, 320 x 180 close-up of the ballot box's keypad: the screen at the top (an empty dark glass, NO candidate number), a 3 x 4 key block with digits and the three colour keys BRANCO, CORRIGE
    and CONFIRMA (`URN_CONFIRMA` rect). pressed: a digit character or 'CONFIRMA' to draw that key sunk; flash: the screen lights (32j +1.4 'light flashes'). `URN_KEYS` maps each digit to its key rect."""
    g = Geometry()
    r(g, 0, 0, 320, 180, 'steel0'); r(g, 24, 8, 272, 164, 'steel2'); r(g, 24, 8, 272, 3, 'steel3'); r(g, 24, 169, 272, 3, 'steel1')
    r(g, 52, 18, 150, 46, 'black'); r(g, 56, 22, 142, 38, 'glass2' if flash else 'blue0'); r(g, 56, 22, 142, 2, 'blue1')
    r(g, 220, 22, 56, 34, 'steel1'); r(g, 224, 28, 48, 4, 'steel0'); r(g, 224, 38, 48, 4, 'steel0')
    for row in range(4):
        for col in range(3):
            d = (row * 3 + col + 1) if row < 3 else (0 if col == 1 else None)
            if d is None:
                continue
            x, y = 58 + col * 40, 72 + row * 24
            URN_KEYS[str(d)] = (x, y, x + 34, y + 20)
            sunk = pressed == str(d)
            r(g, x, y + (2 if sunk else 0), 34, 20 - (2 if sunk else 0), 'black'); r(g, x + 1, y + (3 if sunk else 1), 32, 17 - (2 if sunk else 0), 'steel1'); r(g, x + 1, y + (3 if sunk else 1), 32, 1, 'steel3')
            q, w = lettering(str(d), 'black'); g.paste(q, x + (34 - w) // 2, y + 6 + (2 if sunk else 0))
    for (label, rect, col) in (('BRANCO', (190, 72, 252, 92), 'f2_white'), ('CORRIGE', (190, 98, 252, 118), 'red2'), ('CONFIRMA', URN_CONFIRMA, 'v3_leaf2')):
        x0, y0, x1, y1 = rect
        sunk = pressed == label
        r(g, x0, y0 + (2 if sunk else 0), x1 - x0, y1 - y0 - (2 if sunk else 0), 'black'); r(g, x0 + 1, y0 + (3 if sunk else 1), x1 - x0 - 2, y1 - y0 - 3 - (2 if sunk else 0), col)
        q, w = lettering(label, 'black'); g.paste(q, x0 + (x1 - x0 - w) // 2, y0 + 7 + (2 if sunk else 0))
    return g


# ---------------------------------------------------------------------------------------------------------- FACTORY (scenes 03, 04, 05)
# FACTORY-GATE (03a walk view, 04b street view; 05a/05c) and FACTORY-FLOOR (03b side view, 04a aisle view). Public API at the end of the
# block: factory_gate(view), factory_floor(view), FACTORY_SIGN; pieces for the animated machines: flywheel, press_body, lathe_body, hood2,
# belt_ticks, aisle_machine_pos, AISLE_VP.
import math                                                                                        # noqa: E402
FACTORY_SIGN = ('FÁBRICA', (215, 30, 275, 38))      # plan rows 03a/04b (amended list: unchanged); text 39 px, drawn centred in the rect
FACTORY_WALK_W = 360                                # width of the 03a walk view (pan it 0 -> -25 and the sign lands on FACTORY_SIGN's rect)
AISLE_VP = (230, 92)
VP = AISLE_VP

def _fsky(g, top, bottom, y0, y1, w=320, bands=7):
    def rgb(h):
        h = P.get(h, h); return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    t, b = rgb(top), rgb(bottom)
    for i in range(bands):
        u = i / (bands - 1)
        c = '#%02x%02x%02x' % tuple(round(t[k] + (b[k] - t[k]) * u) for k in range(3))
        r(g, 0, y0 + (y1 - y0) * i // bands, w, (y1 - y0) * (i + 1) // bands - (y1 - y0) * i // bands, c)


def _sign_into(g, sign, ox, dy=1):
    from common import text_width
    from scene_art import lettering
    text, rect = sign
    q, w = lettering(text, 'ivory')
    g.paste(q, rect[0] + ox + (rect[2] - rect[0] - w) // 2, rect[1] + dy)


def _gate_arch(g, ox=0):
    """The gate with its arch board (sign FACTORY_SIGN at world x 240-300, y 30-38 + ox). Shared with 04b (GATE-EXT)."""
    X = lambda x: x + ox
    r(g, X(232), 27, 76, 14, 'wood0'); r(g, X(234), 29, 72, 10, 'blue0'); r(g, X(234), 29, 72, 1, 'blue1')
    for x in (232, 296):                                        # brick piers with caps
        r(g, X(x), 41, 14, 74, 'clay'); r(g, X(x), 41, 2, 74, 'sand'); r(g, X(x + 12), 41, 2, 74, 'brick')
        for yy in range(46, 114, 6):
            r(g, X(x), yy, 14, 1, 'brick')
        r(g, X(x - 2), 39, 18, 3, 'plaster3'); r(g, X(x - 2), 39, 18, 1, 'ivory')
    r(g, X(246), 41, 50, 21, 'clay')                             # lintel with arch
    for yy in range(44, 62, 5):
        r(g, X(246), yy, 50, 1, 'brick')
    poly(g, [(X(246), 62), (X(296), 62), (X(296), 66), (X(284), 58), (X(258), 58), (X(246), 66)], 'plaster1')
    r(g, X(246), 62, 50, 53, 'black')                            # dark passage into the works
    r(g, X(250), 64, 42, 46, 'metal0'); r(g, X(250), 64, 42, 1, 'metal1')
    r(g, X(250), 96, 42, 14, 'black')
    for x in range(X(247), X(256), 3):                           # folded gate leaves
        r(g, x, 62, 1, 52, 'steel1')
    for x in range(X(286), X(295), 3):
        r(g, x, 62, 1, 52, 'steel1')
    r(g, X(246), 62, 10, 1, 'steel2'); r(g, X(286), 62, 10, 1, 'steel2'); r(g, X(246), 108, 10, 1, 'steel2'); r(g, X(286), 108, 10, 1, 'steel2')
    return FACTORY_SIGN


def _street_walk(W_=360):
    g = Geometry(); rng = random.Random(1975)
    _fsky(g, '#8aa3b4', '#e3d3b0', 0, 74, W_)
    for x, y, w in [(20, 20, 40), (150, 12, 34), (310, 24, 36)]:
        ellipse(g, x, y, w, 3, '#c9d2d4'); ellipse(g, x + 8, y - 3, w * .45, 3, '#dfe5e2')
    for x, h, w in [(150, 38, 11), (190, 30, 10)]:               # two chimneys
        r(g, x, 6 + (38 - h) , w, h + 4, 'brick'); r(g, x, 6 + (38 - h), 2, h + 4, 'clay'); r(g, x + w - 2, 6 + (38 - h), 2, h + 4, 'red0')
        r(g, x - 1, 4 + (38 - h), w + 2, 3, 'wood0'); r(g, x, 14 + (38 - h), w, 1, 'plaster3'); r(g, x, 24 + (38 - h), w, 1, 'plaster3')
    r(g, 110, 40, 250, 32, 'plaster1'); r(g, 110, 40, 250, 2, 'plaster3')           # works behind the wall
    for x in range(116, 360, 26):
        r(g, x, 48, 14, 10, 'glass0'); r(g, x, 48, 14, 1, 'glass2'); r(g, x + 6, 48, 1, 10, 'metal0')
    for x in range(110, 360, 34):                                                     # saw-tooth roof
        poly(g, [(x, 40), (x + 14, 30), (x + 30, 40)], 'metal1'); poly(g, [(x + 14, 30), (x + 18, 30), (x + 22, 40), (x + 14, 40)], 'glass1')
    r(g, 0, 70, W_, 44, 'brick')                                                      # the long brick wall
    for yy in range(71, 112, 5):
        for xx in range(-9 + (yy // 5 % 2) * 8, W_, 17):
            r(g, xx, yy, 15, 1, 'clay' if rng.random() < .7 else 'wood1')
    for xx in range(14, W_, 54):
        r(g, xx, 66, 8, 48, 'brick'); r(g, xx, 66, 2, 48, 'clay'); r(g, xx - 1, 64, 10, 3, 'plaster3')
    r(g, 0, 66, W_, 4, 'plaster3'); r(g, 0, 66, W_, 1, 'ivory')
    _gate_arch(g, 0)
    _sign_into(g, FACTORY_SIGN, 25)
    # sidewalk, kerb, street
    r(g, 0, 114, W_, 24, 'steel1'); r(g, 0, 114, W_, 2, 'steel2')
    for xx in range(0, W_, 26):
        r(g, xx, 116, 1, 22, 'steel0')
    r(g, 0, 137, W_, 3, 'steel3'); r(g, 0, 140, W_, 2, 'steel0')
    r(g, 0, 142, W_, 40, 'trouser0')
    for i in range(70):
        r(g, rng.randrange(W_), rng.randrange(144, 178), rng.choice([1, 2, 3]), 1, rng.choice(['trouser1', 'black', 'steel0']))
    for xx in range(10, W_, 60):
        r(g, xx, 160, 24, 2, 'trouser2')
    for x in (34, 150):                                                               # lamp posts
        r(g, x, 70, 2, 56, 'wood0'); r(g, x - 4, 68, 10, 3, 'metal0'); ellipse(g, x + 1, 73, 3, 2, 'gold')
    r(g, 200, 120, 12, 14, 'wood1'); r(g, 200, 120, 12, 2, 'wood3'); r(g, 214, 124, 9, 10, 'wood1'); r(g, 214, 124, 9, 1, 'wood3')   # crates against the wall
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < W_}
    return g


def flywheel(phase, r_=9, spokes=3):
    g = Geometry(); c = r_ + 1
    ellipse(g, c, c, r_, r_, 'metal0'); ellipse(g, c, c, r_ - 1, r_ - 1, 'steel1'); ellipse(g, c, c, r_ - 3, r_ - 3, 'metal0')
    for i in range(spokes):
        a = phase + i * math.tau / spokes
        line(g, (c, c), (c + (r_ - 2) * math.cos(a), c + (r_ - 2) * math.sin(a)), 1.1, 'steel2')
    ellipse(g, c, c, 2, 2, 'steel3')
    return g


def press_body(k=1.0):
    """A punch press seen from the side without its flywheel (origin top-left, about 44 x 52 at k=1)."""
    g = Geometry()
    def R(x, y, w, h, c):
        r(g, round(x * k), round(y * k), max(1, round(w * k)), max(1, round(h * k)), c)
    R(2, 42, 40, 10, 'metal0'); R(2, 42, 40, 2, 'metal2')                       # base
    R(26, 8, 12, 36, 'metal1'); R(26, 8, 2, 36, 'metal3'); R(36, 8, 2, 36, 'metal0')   # column
    R(12, 6, 26, 12, 'steel0'); R(12, 6, 26, 2, 'steel2')                       # head
    R(16, 18, 6, 18, 'steel1'); R(16, 18, 1, 18, 'steel3')                      # ram
    R(8, 34, 22, 8, 'steel0'); R(8, 34, 22, 2, 'steel2')                        # bed
    R(36, 14, 8, 3, 'metal0')                                                   # belt pulley housing
    return g


def lathe_body(k=1.0):
    """A heavy lathe seen from the side (about 76 x 36)."""
    g = Geometry()
    def R(x, y, w, h, c):
        r(g, round(x * k), round(y * k), max(1, round(w * k)), max(1, round(h * k)), c)
    R(0, 12, 20, 22, 'metal1'); R(0, 12, 20, 2, 'metal3'); R(0, 12, 2, 22, 'metal2')        # headstock
    R(4, 18, 8, 8, 'steel1'); ellipse(g, 21 * k, 22 * k, 3 * k, 5 * k, 'steel2')            # chuck
    R(0, 28, 76, 6, 'steel0'); R(0, 28, 76, 1, 'steel2')                                    # bed
    R(2, 34, 6, 2, 'metal0'); R(66, 34, 6, 2, 'metal0')
    R(52, 14, 16, 14, 'metal1'); R(52, 14, 16, 2, 'metal3'); R(48, 20, 6, 3, 'steel2')      # tailstock
    R(30, 22, 12, 6, 'steel1'); R(30, 22, 12, 1, 'steel3')                                 # tool post
    R(6, 2, 8, 10, 'metal0')                                                                # pulley housing on top
    return g


def hood2(w=20, h=15):
    """Extraction hood: a cone that closes over the operator's head (face hidden), hung from a duct."""
    g = Geometry()
    poly(g, [(w // 2 - 4, 0), (w // 2 + 4, 0), (w, h), (0, h)], 'steel1')
    poly(g, [(w // 2 - 4, 0), (w // 2 - 1, 0), (3, h), (0, h)], 'steel2')
    r(g, 0, h - 3, w, 3, 'metal0'); r(g, 0, h - 3, w, 1, 'steel0'); r(g, w // 2 - 5, 0, 10, 2, 'steel0')
    for x in range(4, w - 3, 5):
        r(g, x, h - 7, 1, 1, 'steel3')
    return g


def belt_ticks(phase, n, length, x0=0, y0=0):
    """A vertical belt 3 px wide with lacing ticks that travel along it (n phases)."""
    g = Geometry()
    r(g, x0, y0, 3, length, 'black'); r(g, x0, y0, 1, length, 'metal0')
    for y in range(y0 + phase * (6 // n), y0 + length, 6):
        r(g, x0 + 1, y, 2, 1, 'steel1')
    return g


def factory_wall(g, w=320, with_windows=True):
    rng = random.Random(1978)
    r(g, 0, 0, w, 180, 'brick')
    for yy in range(46, 112, 5):
        for xx in range(-9 + (yy // 5 % 2) * 8, w, 17):
            r(g, xx, yy, 15, 1, rng.choice(['clay', 'clay', 'wood1']))
    r(g, 0, 0, w, 44, 'wood0')                                     # dark roof space (plates sit on it)
    for x in range(-10, w, 38):
        line(g, (x, 44), (x + 19, 6), .7, 'umber'); line(g, (x + 38, 44), (x + 19, 6), .7, 'umber')
    r(g, 0, 40, w, 4, 'umber'); r(g, 0, 43, w, 1, 'wood1')
    if with_windows:
        for x in (22, 78, 134, 190):
            r(g, x, 50, 38, 28, 'metal0'); r(g, x + 2, 52, 34, 24, 'glass1')
            r(g, x + 2, 52, 34, 8, 'glass2'); r(g, x + 18, 52, 2, 24, 'metal0'); r(g, x + 2, 64, 34, 1, 'metal0')
    r(g, 0, 108, w, 72, 'trouser0')                               # cold concrete floor
    r(g, 0, 108, w, 2, 'trouser1')
    for yy in (120, 134, 152, 172):
        r(g, 0, yy, w, 1, 'steel0')
    for i in range(110):
        r(g, rng.randrange(w), rng.randrange(112, 178), rng.choice([2, 3, 5]), 1, rng.choice(['steel0', 'trouser1', 'black']))
    r(g, 0, 110, w, 6, 'black')                                   # wall foot shadow


def line_shaft(g, w=320, y=45, xs=()):
    r(g, 0, y, w, 3, 'steel1'); r(g, 0, y, w, 1, 'steel3')
    for x in range(14, w, 52):
        r(g, x, 40, 2, y - 40, 'metal0')
    for x in xs:
        ellipse(g, x, y + 1, 5, 5, 'metal0'); ellipse(g, x, y + 1, 4, 4, 'steel1'); ellipse(g, x, y + 1, 1, 1, 'steel3')


def _floor_side():
    g = Geometry()
    factory_wall(g)
    line_shaft(g, 320, 45, xs=(130, 160, 212))
    # hanging lamps (the TR plate zone x 210-314, y 6-40 stays empty)
    for x in (52, 170):
        r(g, x, 44, 1, 8, 'wood0')
        poly(g, [(x - 7, 60), (x + 8, 60), (x + 3, 52), (x - 2, 52)], 'metal0'); r(g, x - 7, 60, 15, 1, 'ivory')
    return g


def aisle_pt(near, s):
    return (VP[0] + (near[0] - VP[0]) * s, VP[1] + (near[1] - VP[1]) * s)


def _floor_aisle():
    g = Geometry(); rng = random.Random(1978)
    r(g, 0, 0, 320, 180, 'wood0')
    # back wall with the big loading door at the end of the aisle
    r(g, 168, 40, 150, 62, 'brick')
    for yy in range(42, 100, 5):
        for xx in range(166 + (yy // 5 % 2) * 8, 318, 17):
            r(g, xx, yy, 15, 1, 'clay')
    r(g, 200, 54, 52, 48, 'metal0'); r(g, 203, 57, 46, 45, 'plaster3'); r(g, 203, 57, 46, 10, 'ivory')
    for x in range(212, 248, 12):
        r(g, x, 57, 1, 45, 'plaster1')
    # ceiling
    poly(g, [(0, 0), (320, 0), (320, 40), (168, 40), (0, -50 + 0)], 'wood0')
    for x in range(-40, 330, 36):
        line(g, aisle_pt((x, -20), 1.0), aisle_pt((x, -20), .3), .6, 'umber')
    r(g, 0, 0, 320, 14, 'umber')
    # left wall (brick) with high windows
    poly(g, [(0, 0), (170, 44), (170, 107), (0, 148)], 'brick')
    for yy in range(14, 148, 5):
        for xx in range(0 + (yy // 5 % 2) * 8, 170, 17):
            r(g, xx, yy, 15, 1, 'clay') if (yy < 8 + (xx / 170) * 40 + 0 or True) and 0 <= xx < 170 else None
    poly(g, [(0, 0), (170, 44), (170, 40), (0, -3)], 'umber')
    poly(g, [(0, 0), (170, 44), (170, 62), (0, 44)], 'wood0')                      # dark upper wall (plate sits here)
    for x0 in (120, 150):
        poly(g, [(x0, 62), (x0 + 14, 64), (x0 + 14, 76), (x0, 74)], 'glass1')
    # right wall strip
    poly(g, [(290, 40), (320, 20), (320, 150), (290, 104)], 'plaster1')
    r(g, 300, 60, 18, 40, 'metal0')
    # floor
    poly(g, [(0, 148), (170, 107), (318, 102), (320, 180), (0, 180)], 'trouser0')
    poly(g, [(170, 107), (318, 102), (320, 150), (230, 120)], 'trouser0')
    for xb in range(-120, 520, 70):
        line(g, VP, (xb, 180), .5, 'steel0')
    for k in range(1, 8):
        t = 1 - .52 ** k * 1.0
        yy = VP[1] + (180 - VP[1]) * .5 ** (k - 1) * .75
        r(g, 0, round(yy), 320, 1, 'steel0')
    for i in range(80):
        r(g, rng.randrange(320), rng.randrange(120, 178), rng.choice([1, 2, 3]), 1, rng.choice(['steel0', 'black', 'trouser1']))
    # line shaft running down the aisle
    line(g, (0, 52), aisle_pt((0, 52), .9), 1.2, 'steel1')
    return g


def aisle_machine_pos():
    out = []
    A = (10, 142)
    for s in (1.0, .8, .64, .51, .41):
        x, y = aisle_pt(A, s)
        out.append((round(x), round(y), s))
    return out


def _street_gate():
    g = Geometry(); rng = random.Random(1978)
    _fsky(g, '#8794a0', '#cdbfa2', 0, 70)
    for x, h, w in [(40, 34, 11), (86, 28, 10)]:
        r(g, x, 4 + 34 - h, w, h + 6, 'brick'); r(g, x, 4 + 34 - h, 2, h + 6, 'clay'); r(g, x - 1, 3 + 34 - h, w + 2, 3, 'wood0')
    r(g, 0, 38, 320, 34, 'plaster1'); r(g, 0, 38, 320, 2, 'plaster3')
    for x in range(6, 320, 26):
        r(g, x, 46, 14, 10, 'glass0'); r(g, x, 46, 14, 1, 'glass2'); r(g, x + 6, 46, 1, 10, 'metal0')
    r(g, 0, 70, 320, 44, 'brick')
    for yy in range(71, 112, 5):
        for xx in range(-9 + (yy // 5 % 2) * 8, 320, 17):
            r(g, xx, yy, 15, 1, 'clay' if rng.random() < .7 else 'wood1')
    for xx in range(10, 320, 54):
        r(g, xx, 66, 8, 48, 'brick'); r(g, xx, 66, 2, 48, 'clay'); r(g, xx - 1, 64, 10, 3, 'plaster3')
    r(g, 0, 66, 320, 4, 'plaster3'); r(g, 0, 66, 320, 1, 'ivory')
    _gate_arch(g, -25)
    _sign_into(g, FACTORY_SIGN, 0)
    r(g, 0, 114, 320, 26, 'steel1'); r(g, 0, 114, 320, 2, 'steel2')
    for xx in range(0, 320, 26):
        r(g, xx, 116, 1, 22, 'steel0')
    r(g, 0, 137, 320, 3, 'steel3'); r(g, 0, 140, 320, 2, 'steel0'); r(g, 0, 142, 320, 40, 'trouser0')
    for i in range(70):
        r(g, rng.randrange(320), rng.randrange(144, 178), rng.choice([1, 2, 3]), 1, rng.choice(['trouser1', 'black', 'steel0']))
    for xx in range(10, 320, 60):
        r(g, xx, 160, 24, 2, 'trouser2')
    r(g, 24, 70, 2, 54, 'wood0'); r(g, 20, 68, 10, 3, 'metal0'); ellipse(g, 25, 73, 3, 2, 'gold')
    return g

def factory_gate(view='walk'):
    """FACTORY-GATE. view 'walk' = 03a: long brick wall, sidewalk, two chimneys, 360 x 180; the sign is drawn 25 px right of
    FACTORY_SIGN's rect so a 0 -> -25 pan ends on it (05a/05c: pan the same way or use view 'street'). view 'street' = 04b: the same gate
    straight on from the street, 320 x 180, sign exactly in FACTORY_SIGN's rect. Declare the sign with ctx.sign(*FACTORY_SIGN)."""
    if view not in ('walk', 'street'):
        raise ValueError(view)
    g, w = (_street_walk(FACTORY_WALK_W), FACTORY_WALK_W) if view == 'walk' else (_street_gate(), 320)
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < w and 0 <= xy[1] < 180}
    return g


def factory_floor(view='side'):
    """FACTORY-FLOOR. view 'side' = 03b: brick wall, line shaft, windows, dark roof strip (TR/TL plate zone y 6-40 empty); 'aisle' = 04a:
    perspective down the aisle to the loading door (plate zone TL empty). Machines, operators and hoods are drawn by the scene
    (press_body, lathe_body, hood2, flywheel, belt_ticks, aisle_machine_pos)."""
    if view not in ('side', 'aisle'):
        raise ValueError(view)
    g = _floor_side() if view == 'side' else _floor_aisle()
    g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < 320 and 0 <= xy[1] < 180}
    return g


# ---------------------------------------------------------------------------------------------------------- canvas clipping
import functools                                                                                   # noqa: E402


def _clipped(fn, width):
    """Drop cells outside the canvas (the sky gradient helper paints 2000 columns): every 3.0.0 set is exactly width x 180."""
    @functools.wraps(fn)
    def inner(*a, **k):
        g = fn(*a, **k)
        g.cells = {xy: c for xy, c in g.cells.items() if 0 <= xy[0] < width and 0 <= xy[1] < 180}
        return g
    return inner


for _n, _w in (('bairro', BAIRRO_W), ('house_exterior', 320), ('school_street', 320), ('house_interior', 320), ('table_room', 320),
               ('gabinete_o1', 320), ('gabinete_door', 320), ('tv_room', 320), ('tv_close', 320), ('senate_plenary', 320),
               ('stf_plenary', STF_W), ('camara', CAMARA_W), ('conselho_etica', 320), ('planalto_ramp', 320), ('school_front', 320), ('market_stall', 320), ('truck_bed', 320), ('classroom', 320), ('vaccination_room', 320), ('school_clinic_track', 640), ('court_floor', 320), ('urn_keypad', 320), ('planalto_doors', 320), ('stf_facade', 320), ('mercearia_front', 320), ('timeline3_board', 320)):
    globals()[_n] = _clipped(globals()[_n], _w)
