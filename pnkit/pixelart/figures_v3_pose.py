"""Poses 'sit' and 'back' for the Lula film 3.0.0 figures (shared by figures_v2, figures_v3_cast, figures_v3_extra and the
kept 2.0.0 sprites). Own procedural pixel art, no image input. Routed through `common.Ctx.sprite_frame`, so
`ctx.actor(p, kind, 'sit', ...)` works for every kind that draws, and `ctx.sit_talk` / `ctx.walk_back` exist as helpers.

SEATED (profile, facing right, same 28-px frame as the standing figures)
  poses   'sit'      hands on the lap (idle; the idle breathing rule of common.py applies)
          'sittalk'  the same body, the near arm gestures like 'talk' (gesture 0..1)
  Highest pixel y=1 (same head, torso and arms as standing). The hips are on the seat, thighs forward, torso upright.
  SEAT_ROW  = 34   the first row BELOW the thighs: put the TOP SURFACE of the chair/stool/bunk at y_figure + 34.
  SIT_HEIGHT = 33  distance from the head top (row 1) to the seat line (row 34).
  SOLE_ROW  = 45   the lowest shoe pixel; the floor is at y_figure + 46 (11 rows below the seat line).
  Frame x range: about 3..29 (knees and toes reach x 28-29), flip(g, 27) mirrors it for facing=True.
  A desk top at the lap: its top surface is usually at y_figure + 29..31 (the hands rest at row 30-31).
  Scaled kinds (girl 7, girl 15, teen, child, sister) are seated at adult size and scaled by the same factor as standing.

FROM BEHIND (frame centre x = 13.5 so flip(g, 27) mirrors about the body axis)
  poses   'back'       standing, seen from behind, arms at the sides (idle, breathing applies)
          'backwalk'   walking away (cycle as the standing walk: 15 px per cycle; use ctx.walk_back for the rate)
          'backhands'  standing, hands clasped behind the back (Lula on the terrace, 11e)
          'backturn'   standing from behind with the head turned to the right in profile (the kind's own head)
          'backsit'    seated, seen from behind: back, shoulders and head down to the seat (row 34) and the lower legs and
                       shoes below it (rows 35-45); a chair back or desk drawn by the scene hides the rest.
  Highest pixel y=1, soles y=49 (backsit: y=45). Hair, hat, bun, ribbon or cap seen from behind, ears, jacket back with
  centre seam and vent, belt, two legs.
"""
import math
from .geometry import Geometry
from .scene_art import P, r, poly, line, ellipse


def flip(q, width=27):
    g = Geometry(); g.cells = {(width - x, y): c for (x, y), c in q.cells.items()}; return g

SEAT_ROW = 34
SOLE_ROW = 45
SIT_HEIGHT = SEAT_ROW - 1
SIT_POSES = ('sit', 'sittalk')
BACK_POSES = ('back', 'backwalk', 'backhands', 'backturn', 'backsit')
NEW_POSES = SIT_POSES + BACK_POSES
CX = 13.5


def _k(x, k, cx=12.5):
    return cx + (x - cx) * k


# ===================================================================================================== seated lower body
def sit_legs(g, tones, shoe='black', shoetop='steel0', x0=7, skirt=None, robe=None, shin=None):
    """Draw the seated lower body into g (call it first: torso and arms are drawn over it).
    tones = (dark, mid, light) of the thigh; skirt=(dark, mid, light) hangs 3 rows from the knee over bare `shin` tones;
    robe=(dark, mid, light) hangs from the knee to the floor; shin = (dark, mid, light) of the lower leg (default: tones)."""
    d, m, l = tones
    sd, sm, sl = shin or tones
    for i in (0, 1):
        kx = 21 if i == 0 else 24                                   # far leg 3 px behind the near one
        c, hl, sc = (d, m, sd) if i == 0 else (m, l, sm)
        xa = x0 if i == 0 else x0 + 1
        r(g, xa, 31, kx - xa + 3, 3, c)                             # thigh rows 31-33, knee cap one past kx+1
        r(g, xa, 31, kx - xa + 2, 1, hl)                            # top edge catches the light
        r(g, xa, 33, kx - xa + 3, 1, d if i else d)                 # underside
        g.cells.pop((kx + 2, 31), None)                             # round the knee
        # lower leg rows 34-42, shoe rows 43-45
        if robe:
            rd, rm, rl = robe
            r(g, kx - 1, 34, 6, 11, rm); r(g, kx - 1, 34, 1, 11, rl); r(g, kx + 4, 35, 1, 10, rd); r(g, kx - 1, 44, 6, 1, rd)
            r(g, kx + 2, 45, 4, 1, shoe)
            continue
        r(g, kx, 34, 2, 9, sc); r(g, kx, 34, 1, 9, sl if i else sm)
        if skirt:
            kd, km, kl = skirt
            r(g, kx - 1, 34, 4, 3, km); r(g, kx - 1, 34, 1, 3, kl); r(g, kx + 2, 35, 1, 2, kd); r(g, kx - 1, 36, 4, 1, kd)
        r(g, kx - 1, 43, 3, 1, shoe)                                # heel / ankle
        r(g, kx - 1, 44, 6, 1, shoe); r(g, kx, 44, 3, 1, shoetop)   # instep
        r(g, kx - 1, 45, 7, 1, shoe)                                # sole, toe to kx+5
    return g


def sit_arms(k_sh, sit_hand=True):
    """(far hand centre, near elbow, near wrist) for the seated idle pose, in the builders' coordinates."""
    return (19, 31), (k_sh(18) + 1, 26), (k_sh(18) + 4, 30)


# ===================================================================================================== from behind
HR = {1: (11, 16), 2: (10, 17), 3: (9, 18), 4: (9, 18), 5: (9, 18), 6: (9, 18), 7: (9, 18), 8: (9, 18), 9: (9, 18),
      10: (10, 17), 11: (11, 16)}


def _rows(u, a, b, colour, rows=HR):
    for y in range(a, b + 1):
        x0, x1 = rows[y]
        r(u, x0, y, x1 - x0 + 1, 1, colour)


def _bow(u, y, c0, c1, c2):
    r(u, 10, y, 3, 3, c1); r(u, 15, y, 3, 3, c1); r(u, 10, y, 3, 1, c2); r(u, 15, y, 3, 1, c2)
    r(u, 13, y + 1, 2, 1, c0); r(u, 12, y + 3, 1, 2, c0); r(u, 15, y + 3, 1, 1, c0)


def draw_head_back(u, h):
    """Head and neck seen from behind in the upper-body layer u. h: style short|bald|bun|tail|cap|hat plus colours."""
    st = h.get('style', 'short'); hair = h.get('hair', h.get('fringe')); hi = h.get('hi', hair); sh = h.get('shade', hair)
    skin1, skin0 = 'skin1', 'skin0'
    r(u, 11, 12, 6 - 0, 3, skin1); r(u, 11, 12, 6, 1, skin0)         # neck rows 12-14, shadow under the skull
    if h.get('ears', True) and st not in ('hat',):
        r(u, 8, 7, 1, 3, 'skin1'); r(u, 19, 7, 1, 3, 'skin1'); r(u, 8, 8, 1, 1, 'skin2'); r(u, 19, 8, 1, 1, 'skin2')
    if st in ('short', 'bun', 'tail'):
        _rows(u, 1, 10, hair)
        r(u, 11, 11, 6, 1, sh)                                         # hairline at the nape
        r(u, 11, 2, 4, 1, hi); r(u, 10, 3, 2, 1, hi); r(u, 16, 3, 2, 1, hi)
        r(u, 9, 9, 1, 2, sh); r(u, 18, 9, 1, 2, sh); r(u, 12, 10, 4, 1, sh)
        if h.get('grey'):
            for x in (10, 12, 15, 17):
                r(u, x, 3 + x % 2 * 2, 1, 1, h['grey'])
    elif st == 'bald':
        _rows(u, 1, 7, 'skin2'); r(u, 12, 1, 3, 2, 'skin3')
        _rows(u, 8, 10, h['fringe']); r(u, 12, 8, 4, 3, 'skin1'); r(u, 12, 11, 4, 1, h['fringe'])
        r(u, 11, 11, 1, 1, h['fringe']); r(u, 16, 11, 1, 1, h['fringe'])
        r(u, 9, 7, 2, 1, h['fringe']); r(u, 17, 7, 2, 1, h['fringe'])
    elif st == 'cap':
        crown, cdark, band, chi = h['cap']
        _rows(u, 1, 5, crown); r(u, 13, 1, 2, 5, cdark); r(u, 13, 1, 2, 1, chi)
        r(u, 9, 6, 10, 1, band)
        _rows(u, 7, 10, hair); r(u, 11, 11, 6, 1, hair); r(u, 12, 7, 4, 1, band)
    elif st == 'hat':
        r(u, 11, 1, 6, 1, 'f2_straw'); r(u, 10, 2, 8, 3, 'f2_straw'); r(u, 10, 5, 8, 1, 'f2_band')
        r(u, 15, 1, 2, 1, 'f2_strawshade'); r(u, 17, 2, 1, 3, 'f2_strawshade')
        r(u, 6, 6, 16, 1, 'f2_straw'); r(u, 5, 7, 18, 1, 'f2_straw'); r(u, 5, 7, 18, 1, 'f2_straw')
        r(u, 7, 8, 14, 1, 'f2_strawshade'); r(u, 5, 7, 2, 1, 'f2_strawshade'); r(u, 21, 7, 2, 1, 'f2_strawshade')
        r(u, 10, 9, 8, 2, hair); r(u, 11, 11, 6, 1, h.get('shade', hair))
    if st == 'bun':
        for y, (a, b) in {7: (12, 15), 8: (11, 16), 9: (11, 16), 10: (11, 16), 11: (12, 15)}.items():
            r(u, a, y, b - a + 1, 1, hair)
        r(u, 12, 8, 2, 1, hi); r(u, 11, 10, 6, 1, sh); r(u, 12, 11, 4, 1, sh)
    if st == 'tail':
        r(u, 12, 11, 4, 5, hair); r(u, 13, 16, 2, 4, hair); r(u, 12, 11, 1, 6, hi); r(u, 14, 17, 1, 3, sh)
        if h.get('ribbon'):
            _bow(u, 8, 'f4_rib0', 'f4_rib1', 'f4_rib2')
    if h.get('beard'):
        bc, bs = h['beard']
        r(u, 8, 10, 1, 3, bc); r(u, 19, 10, 1, 3, bc); r(u, 9, 12, 2, 1, bs); r(u, 17, 12, 2, 1, bs); r(u, 9, 11, 1, 1, bc); r(u, 18, 11, 1, 1, bc)
    if h.get('glass'):
        r(u, 8, 6, 1, 1, 'f2_glass'); r(u, 19, 6, 1, 1, 'f2_glass')
    if h.get('pearl'):
        r(u, 8, 10, 1, 1, 'f3_pearl'); r(u, 19, 10, 1, 1, 'f3_pearl')
    if h.get('mask'):
        r(u, 8, 8, 1, 2, 'f4_mask0'); r(u, 19, 8, 1, 2, 'f4_mask0')


def back_view(spec, head, pose='back', phase=0.0, facing=False, gesture=.5, head_fn=None):
    """Seen from behind. spec: suit (dark, mid, light), legs (default suit), shirt, k, belt, shoe, shoetop, sleeve,
    skirt=(hem_row, tones), apron=(dark, mid, light) or None. head: dict for draw_head_back. head_fn(u, pt): own profile
    head for pose 'backturn'. Returns a Geometry in the 28-px frame (centre x 13.5)."""
    walk = pose == 'backwalk'; sit = pose == 'backsit'
    s = math.sin(phase)
    bob = round(.6 * (1 - math.cos(phase * 2))) if walk else 0
    sway = round(.8 * s) if walk else 0
    dark, mid, light = spec['suit']; ld, lm, ll = spec.get('legs') or spec['suit']
    k = spec.get('k', 1.0)
    X = lambda x: CX + (x - CX) * k
    shoe = spec.get('shoe', 'black'); shoetop = spec.get('shoetop', 'steel0')
    g = Geometry()
    # ---- legs
    skirt = spec.get('skirt')
    if sit:
        r(g, 7, 31, 14, 3, lm); r(g, 7, 31, 14, 1, ll); r(g, 7, 33, 14, 1, ld)
        for x0 in (9, 15):
            r(g, x0, 35, 4, 8, lm); r(g, x0, 35, 1, 8, ll if x0 == 9 else lm); r(g, x0 + 3, 36, 1, 7, ld)
            r(g, x0 - 1, 43, 6, 3, shoe); r(g, x0, 43, 4, 1, shoetop)
    else:
        r(g, 8, 31, 12, 5, lm); r(g, 8, 31, 1, 5, ll); r(g, 19, 31, 1, 5, ld); r(g, 13, 33, 2, 3, ld)
        for i in (0, 1):
            u_ = (phase / (2 * math.pi) + i * .5) % 1 if walk else 0
            lift = 0
            if walk and u_ >= .5:
                z = (u_ - .5) * 2; lift = round(4 * math.sin(z * math.pi))
            x0 = 8 if i == 0 else 15
            foot = 47 - lift
            r(g, x0, 36, 5, 6, lm); r(g, x0 + (1 if i == 0 else 0), 42, 4, foot - 42, lm)
            r(g, x0, 36, 1, 6, ll if i == 0 else lm); r(g, x0 + 4, 36, 1, 6, ld if i else lm)
            sx = x0 - (0 if i == 1 else 0)
            r(g, sx, foot, 5, 3, shoe); r(g, sx + 1, foot, 3, 1, shoetop)
            if lift >= 2: r(g, sx, foot + 2, 5, 1, 'steel0')            # sole of the raised foot
    if skirt:
        hem, (kd, km, kl) = skirt
        fl = round(1.2 * s) if walk else 0
        poly(g, [(7, 29), (20, 29), (22, hem - 2), (22 + fl, hem), (5 + fl, hem), (5, hem - 2)], km)
        r(g, 6, 30, 2, hem - 31, kl); r(g, 19, 31, 2, hem - 32, kd); r(g, 13, 32, 2, hem - 33, kd)
        r(g, 5 + fl, hem, 18, 1, kd)
    # ---- upper body, drawn in its own layer so bob and sway move it together
    u = Geometry()
    T = lambda pts: [(X(x), y) for x, y in pts]
    sleeve = spec.get('sleeve')
    la, ra = round(X(7)) - 2, 27 - (round(X(7)) - 2) - 1                # arm columns (2 wide), mirrored about 13.5
    hands = pose == 'backhands'
    swing = round(1.6 * s) if walk else 0
    for side, xa, off in ((0, la, swing), (1, ra, -swing)):
        ac = dark if side == 0 else mid
        if hands:
            continue
        end = 25 + off
        r(u, xa, 16, 2, max(2, end - 16), ac)
        if sleeve: r(u, xa, end, 2, 5, sleeve); end += 5
        r(u, xa, end, 2, 33 - end, 'skin1')
        r(u, xa, 33 + off if not sleeve else 33 + off, 2, 3, 'skin2')
    poly(u, T([(6.5, 17), (8, 14), (11, 13), (16, 13), (19, 14), (20.5, 17), (20, 25), (19.5, 31), (7.5, 31), (7, 25)]), mid)
    r(u, round(X(8)), 17, 2, 11, light)                                  # lit left shoulder blade
    r(u, round(X(18)), 17, 2, 12, dark)                                  # shaded right side
    r(u, 13, 16, 1, 15, dark)                                            # centre seam
    r(u, 13, 27, 2, 4, dark)                                             # vent
    r(u, round(X(9)), 15, 9, 1, light)                                   # yoke
    r(u, 11, 13, 6, 1, spec['shirt']); r(u, 12, 14, 4, 1, spec['shirt'])  # collar from behind
    if spec.get('belt'): r(u, round(X(8)), 30, 12, 1, spec['belt'])
    if spec.get('apron'):
        ad, am, al = spec['apron']
        r(u, 10, 14, 8, 1, ad); r(u, 8, 29, 12, 2, ad); r(u, 11, 31, 3, 1, am); r(u, 10, 31, 1, 6, am); r(u, 15, 31, 1, 4, am)
        r(u, 12, 30, 4, 2, al)
    if hands:
        for xa, ac in ((la, dark), (ra, mid)):
            r(u, xa, 16, 2, 9, ac)
        line(u, (la + 1, 24), (12, 29.5), 1.4, sleeve or 'skin1'); line(u, (ra, 24), (15, 29.5), 1.4, sleeve or 'skin1')
        r(u, 12, 29, 4, 3, 'skin2'); r(u, 12, 29, 4, 1, 'skin1')
    if pose == 'backturn' and head_fn is not None:
        head_fn(u, lambda x, y: (x, y))
    else:
        draw_head_back(u, head)
    g.paste(u, sway, bob) if (sway or bob) else g.cells.update(u.cells)
    if facing:
        return flip(g, 27)
    return g


# ===================================================================================================== head tables (from behind)
# keys: figures_v2 kind names (after the Lula era mapping), figures_v3_cast 'kind' or 'dilma:<era>'
BACK_HEAD = {
    'lula_black': dict(style='short', hair='f2_bk1', hi='f2_bk3', shade='f2_bk0', beard=('f2_bk0', 'f2_bk2')),
    'lula_pres': dict(style='short', hair='f2_sph', hi='f2_sp2', shade='f2_sp0', beard=('f2_sp1', 'f2_sp0')),
    'lula2023': dict(style='short', hair='f2_white', hi='ivory', shade='f2_whiteshade', beard=('f2_white', 'f2_whiteshade')),
    'lula2023hat': dict(style='hat', hair='f2_white', shade='f2_whiteshade', beard=('f2_white', 'f2_whiteshade')),
    'moro': dict(style='short', hair='f2_hmoro', hi='f2_hdel', shade='black'),
    'dallagnol': dict(style='short', hair='f2_hdel', hi='f2_hflav', shade='f2_hmoro', glass=True),
    'bolsonaro': dict(style='short', hair='f2_hjair', hi='f2_hjair2', shade='f2_hdel'),
    'flavio': dict(style='short', hair='f2_hflav', hi='brown', shade='f2_hdel'),
    'alckmin': dict(style='bald', fringe='f2_hgrey', glass=True),
    'collor': dict(style='short', hair='f2_hcol', hi='f2_hdel', shade='f2_hmoro'),
    'dilma:2010': dict(style='short', hair='f3_dh0', hi='f3_dh1', shade='f3_dh0', pearl=True),
    'dilma:2014': dict(style='short', hair='f3_dh2', hi='f3_dh3', shade='f3_dh2', pearl=True),
    'dilma:2016': dict(style='short', hair='f3_dh2', hi='f3_dh3', shade='f3_dh2', pearl=True),
    'temer': dict(style='short', hair='f3_silver', hi='f3_silver2', shade='f3_silver0'),
    'cunha': dict(style='short', hair='f3_cgrey', hi='f3_cgrey2', shade='f3_croot', glass=True),
    'alencar': dict(style='bald', fringe='f2_white'),
    'freichico': dict(style='short', hair='f3_hch', hi='f3_hch2', shade='f3_hch'),
}


def extra_back(kind, era, clothes, spec):
    """(back spec, head dict) for a figures_v3_extra kind from its `_spec` dict (suit, legs, k, skirt, torso_fx, ...)."""
    sp = dict(suit=spec['suit'], shirt=spec['shirt'], k=spec.get('k', 1.0), belt=spec.get('belt'), sleeve=spec.get('sleeve'),
              legs=spec.get('legs'), shoe=spec.get('shoe', 'black'), shoetop=spec.get('shoetop', 'steel0'))
    if spec.get('skirt'): sp['skirt'] = (spec['skirt'][0], spec['skirt'][1])
    fx = getattr(spec.get('torso_fx'), '__name__', '')
    if fx == '_apron': sp['apron'] = ('f4_tl0', 'f4_tl1', 'f4_tl2')
    if spec.get('legs_fx') is not None and kind == 'judge':                   # robe to the hem, bare dark legs below
        sp['skirt'] = (44, ('f4_rb0', 'f4_rb1', 'f4_rb2')); sp['legs'] = ('f4_rb0', 'f4_rb0', 'f4_rb1')
    if fx == '_coat':                                                         # open white coat over scrubs: hem at row 40
        sp['skirt'] = (40, ('f4_coat0', 'f4_coat1', 'f4_coat2'))
    hair_old = dict(style='bun', hair='f4_hb0', hi='f4_hb1')
    if kind == 'mother':
        h = dict(hair_old, grey='f4_hg0') if era == 'older' else dict(hair_old)
    elif kind == 'teacher':
        h = dict(hair_old)
    elif kind == 'woman':
        h = {'a': dict(style='bun', hair='f4_hb1', hi='f4_hb2'), 'b': dict(style='tail', hair='f4_hk', hi='f4_hb0'),
             'c': dict(style='bun', hair='f4_hb0', hi='f4_hb1', grey='f4_hg0')}[era or 'a']
    elif kind == 'girl':
        h = dict(style='tail', hair='f4_hb0', hi='f4_hb1', ribbon=True)
    elif kind == 'nurse':
        h = dict(style='bun', hair='f4_hb1', hi='f4_hb2', glass=era in (None, 'glasses'), mask=clothes in (None, 'scrubs'))
    elif kind in ('teen', 'citizen'):
        h = dict(style='short', hair='f4_hb0' if kind == 'teen' else 'f4_hb1', hi='f4_hb1' if kind == 'teen' else 'f4_hb2')
        if clothes == 'casual_masked': h['mask'] = True
    elif kind == 'father':
        h = dict(style='short', hair='f4_hg0', hi='f4_hg1') if era == 'older' else dict(style='short', hair='f4_hb0', hi='f4_hb1')
    elif kind == 'doctor':
        h = dict(style='short', hair='f4_hg0', hi='f4_hg1', mask=clothes in (None, 'scrubs'))
    elif kind == 'officer':
        h = dict(style='cap', hair='f4_hk', cap=('f4_ofc', 'f4_ofv', 'f4_of2', 'f4_of1'))
    elif kind == 'guard':
        h = dict(style='cap', hair='f4_hb0', cap=('f4_gcap', 'f4_belt', 'f4_gd0', 'f4_gd1'))
    elif kind == 'fhc':
        h = dict(style='short', hair='f4_hg0', hi='f4_hg1', grey='f4_hg2')
    elif kind == 'judge':
        h = {'a': dict(style='short', hair='f4_hg1', hi='f4_hg2', shade='f4_hg0'),
             'b': dict(style='bald', fringe='f4_hg2'),
             'c': dict(style='short', hair='f4_hb0', hi='f4_hb1', glass=True),
             'd': dict(style='short', hair='f4_hg2', hi='f4_jw', shade='f4_hg1', glass=True),
             'e': dict(style='bun', hair='f4_hb0', hi='f4_hb1', grey='f4_hg0')}[era or 'a']
    else:
        h = dict(style='short', hair='f4_hb0', hi='f4_hb1')
    return sp, h


# ===================================================================================================== kept 2.0.0 sprites
_TR = ('trouser1', 'trouser0', 'trouser2')
_SKIN = ('skin0', 'skin1', 'skin2')
OLD_KINDS = {
    #            suit (dark, mid, light)                 legs        extra spec                         head
    'back':      (('metal0', 'metal1', 'metal2'), _TR, {}, dict(style='short', hair='hair', hi='brown')),
    'chico':     (('wood1', 'ochre', 'sand'), _TR, {}, dict(style='short', hair='hair', hi='brown')),
    'leader':    (('plaster1', 'plaster3', 'ivory'), _TR, {}, dict(style='short', hair='hair', hi='brown')),
    'clerk':     (('wood0', 'brown', 'clay'), _TR, {}, dict(style='short', hair='hair', hi='brown')),
    'old':       (('blue0', 'blue1', 'blue2'), _TR, {}, dict(style='short', hair='steel2', hi='steel3')),
    'lula':      (('blue0', 'blue1', 'blue2'), _TR, {}, dict(style='short', hair='hair', hi='brown')),
    'donalindu': (('metal0', 'metal1', 'metal2'), ('metal0', 'metal1', 'metal2'), dict(skirt=(44, ('metal0', 'metal1', 'metal2'))),
                  dict(style='bun', hair='hair', hi='brown')),
    'child':     (('wood1', 'ochre', 'sand'), _SKIN, {}, dict(style='short', hair='hair', hi='brown')),
    'sister':    (('wood1', 'ochre', 'sand'), _SKIN, dict(skirt=(38, ('red0', 'red1', 'red2'))), dict(style='tail', hair='hair', hi='brown')),
}
OLD_SCALE = {'child': .65, 'sister': .65}


def old_pose(kind, pose, phase, facing, gesture, old_actor, resize):
    """'sit' / 'sittalk' / 'back*' for the kept 2.0.0 kinds (back, chico, leader, clerk, old, donalindu, child, sister, lula-old)."""
    suit, legs, extra, head = OLD_KINDS[kind]
    g = None
    if pose in BACK_POSES:
        spec = dict(suit=suit, shirt=suit[2], k=1.0, belt='wood0', legs=legs, **extra)
        g = back_view(spec, head, pose, phase, False, gesture, head_fn=None)
    else:                                                                  # seated: cut the standing sprite at the hips, add lap and legs
        base = old_actor({'donalindu': 'mother'}.get(kind, kind) if kind not in OLD_SCALE else 'lula', 'talk' if pose == 'sittalk' else 'idle', phase, False, gesture)
        if kind in OLD_SCALE:                                              # rebuild the adult-size sprite the same way the kept code does
            remap = {P['blue0']: P['wood1'], P['blue1']: P['ochre'], P['blue2']: P['sand']}
            base.cells = {xy: remap.get(c, c) for xy, c in base.cells.items()}
        g = Geometry()
        skirt = extra.get('skirt')
        sit_legs(g, legs if kind not in ('donalindu',) else suit, skirt=skirt[1] if skirt else None,
                 shin=_SKIN if (skirt or kind in OLD_SCALE) else None, robe=None)
        far = (19, 31)
        r(g, 18, 31, 2, 3, 'skin1')
        up = {xy: c for xy, c in base.cells.items() if xy[1] <= 30}
        g.cells.update(up)
        if pose == 'sit': r(g, 20, 30, 3, 2, 'skin2')
    if kind in OLD_SCALE:
        g = resize(g, OLD_SCALE[kind])
    return flip(g, 18 if kind in OLD_SCALE else 27) if facing else g
