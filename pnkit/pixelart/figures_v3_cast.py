"""Figures v3 cast for the Lula film 3.0.0: Dilma, Temer, Cunha, Alencar, Frei Chico.

Own procedural pixel art in the figures_v2 construction (same frame, limbs, poses and
mirroring as `actor_v2`); no image input. `figures_v2.py` is imported, not edited.

Frame contract (same as figures_v2): 28 px wide frame, drawn facing right and mirrored with
`flip(g, 27)` for facing=True; highest pixel y=1 (hair or bald crown), soles y=49 in idle.
The 3.0.0 plan (SHOTS-3.0.0.md, "Grid and zones") asks for one head-to-foot extent for every
figure and names no other height; so Dilma keeps it too (no shorter figure is asked for).

Recognition comes from cues read once in licensed reference photos (work/RIGHTS.md, section
"Cast v3"); nothing is traced, converted or embedded. Frei Chico has NO licensed photo found:
he is generic (see `head_chico`).

Kinds and eras (SHOTS-3.0.0.md scene -> kind):
  dilma     era '2010' (default; scenes 11h, 12a: 2010 campaign, chestnut hair, cream jacket),
            '2014' | '2016' (scenes 12b-12g, 13a, 13i, 14a: lighter golden-brown hair)
  temer     2016 (scene 14f); era ignored (None or '2016')
  cunha     2015 (scenes 13b, 13f, 13g); era ignored (None or '2015')
  alencar   2002-2003 (scene 07b); era None or '2002'
  freichico 1975 (scene 03b-03d); era None or '1975'
"""
import math
from . import figures_v3_pose as _pose
from .figures_v2 import (Geometry, P, r, poly, line, ellipse, flip, _k, _head_base, _glasses,
                        CLOTHES as CLOTHES_V2, KINDS as KINDS_V2, bbox)

# Own named colours (prefix f3_).
P.update({
 # Temer / Cunha / Alencar / Dilma hair and cues
 'f3_silver':'#c1c4c6','f3_silver2':'#e0e2e1','f3_silver0':'#8c9093',
 'f3_cgrey':'#8a8d90','f3_cgrey2':'#a9acae','f3_croot':'#4f5356','f3_stub':'#a08a7c',
 'f3_dh0':'#5a3b27','f3_dh1':'#7b5233',                       # Dilma 2010: chestnut, lighter top
 'f3_dh2':'#6e4a2a','f3_dh3':'#9a7142','f3_dhc':'#432a17','f3_dhc2':'#573820',                       # Dilma 2014-16: golden-brown
 'f3_lip':'#b23a3e','f3_lip2':'#d0605f','f3_pearl':'#fbf8ef','f3_brow':'#3a2619','f3_lash':'#2a1c14','f3_part':'#3d2a1c','f3_gold':'#d6a844','f3_lap':'#b9ad94','f3_btn':'#8a7d66',
 'f3_hch':'#2b211b','f3_hch2':'#43362d',                      # Frei Chico: generic dark-brown hair
 # clothes
 'f3_blk0':'#0d1016','f3_blk1':'#1a1f2b','f3_blk2':'#2c3342', # Temer: near-black suit
 'f3_tienavy':'#24385f','f3_tiestr':'#d6c56a',               # navy tie, thin yellow stripe
 'f3_cn0':'#1c2a44','f3_cn1':'#2a3d61','f3_cn2':'#415a82',   # Cunha: navy suit
 'f3_tieteal':'#2f9a8a',
 'f3_ab0':'#2a1d19','f3_ab1':'#43302a','f3_ab2':'#5f473c',   # Alencar: dark chocolate suit
 'f3_tiecopper':'#c0763a',
 'f3_cr0':'#a79b86','f3_cr1':'#d9cfba','f3_cr2':'#f1eadb',   # Dilma: cream jacket
 'f3_dn0':'#16203a','f3_dn1':'#26345a','f3_dn2':'#3c4d7a',   # Dilma 2015: dark navy patterned jacket
 'f3_blouse':'#6f7da0','f3_blousecr':'#e9dfcc',
 'f3_pant0':'#3a3f4c','f3_pant1':'#5f6577','f3_pant2':'#848a9c',   # Dilma trousers: mid charcoal-grey so jacket/trouser split is visible (drawing choice, see RIGHTS.md)
 'f3_pearld':'#8d939c',
 'f3_wk0':'#6a4a2b','f3_wk1':'#a77a45','f3_wk2':'#cfa576',    # Frei Chico: ochre work shirt
 'f3_wp0':'#2c3338','f3_wp1':'#46514f','f3_wp2':'#6c7568',    # work trousers
})

# ----------------------------------------------------------------- heads
def head_temer(g, pt):
    _head_base(g, pt)
    # photos (Beto Barata/PR 2017; Valter Campanato 2016): silver hair slicked straight back, high
    # forehead with the hairline receding at the temples, clean-shaven, long face, closed mouth.
    poly(g, [pt(9, 6), pt(9, 3), pt(11, 1), pt(16, 1), pt(18, 3), pt(17, 4), pt(14, 3), pt(12, 4), pt(11, 6), pt(11, 10), pt(9, 9)], 'f3_silver')
    r(g, 11, pt(0, 1)[1], 4, 1, 'f3_silver2'); r(g, 9, pt(0, 5)[1], 2, 2, 'f3_silver0')   # sheen, back shade
    r(g, 14, pt(0, 12)[1], 3, 1, 'skin0')                                                 # set mouth, long jaw

def head_cunha(g, pt):
    _head_base(g, pt)
    # photos (Jonas Pereira/Agencia Senado 2015; Marcelo Camargo/Agencia Brasil 2015): grey hair combed
    # back from a high forehead (darker grey at the temple), thin rectangular metal glasses, a faint
    # grey moustache shadow, full cheeks and jowl, heavy build.
    poly(g, [pt(9, 6), pt(9, 3), pt(11, 1), pt(16, 1), pt(18, 3), pt(17, 4), pt(14, 3), pt(12, 4), pt(11, 6), pt(11, 10), pt(9, 9)], 'f3_cgrey')
    r(g, 11, pt(0, 1)[1], 3, 1, 'f3_cgrey2'); r(g, 9, pt(0, 5)[1], 3, 2, 'f3_croot')
    r(g, 15, pt(0, 10)[1], 3, 1, 'f3_stub')                                               # faint moustache
    r(g, 17, pt(0, 10)[1], 1, 3, 'skin1'); r(g, 16, pt(0, 12)[1], 1, 1, 'skin1')          # full cheek and jowl
    r(g, 12, pt(0, 13)[1], 5, 1, 'skin0')                                                 # double-chin shade
    _glasses(g, pt)

def head_alencar(g, pt):
    _head_base(g, pt)
    # photos (Agencia Brasil 2005, 2004): large bald dome with white hair only as a rim behind the
    # ear and at the nape, heavy brows, big ear, a white moustache over the lip, no glasses, jowls.
    r(g, 12, pt(0, 1)[1], 4, 1, 'skin2'); r(g, 11, pt(0, 2)[1], 6, 1, 'skin2'); r(g, 12, pt(0, 1)[1], 2, 1, 'skin3')
    poly(g, [pt(10, 9), pt(10, 6), pt(11, 4), pt(12, 5), pt(12, 8), pt(11, 10)], 'f2_white')
    r(g, 15, pt(0, 10)[1], 4, 1, 'f2_white'); r(g, 16, pt(0, 11)[1], 2, 1, 'f2_whiteshade')   # moustache
    r(g, 17, pt(0, 12)[1], 1, 1, 'skin1'); r(g, 12, pt(0, 13)[1], 5, 1, 'skin0')               # jowl
    r(g, 12, pt(0, 9)[1], 1, 2, 'skin2')                                                        # large ear

def head_dilma(g, pt, era='2010'):
    _head_base(g, pt)
    base, hi = ('f3_dh0', 'f3_dh1') if era == '2010' else ('f3_dh2', 'f3_dh3')
    dk = 'f3_dhc' if era != '2010' else 'f3_dhc'
    Y = lambda y: pt(0, y)[1]
    # photos (Stuckert/PR 2011; Agencia Brasil 2014, 2015): a short, FULL, ROUNDED cut. High swept-up volume on
    # top, the hair standing out past the skull at the back and sides and curling under at the nape (a soft
    # rounded silhouette, not a flat crop), a side-swept fringe over the forehead, the ear showing in front of
    # the back mass with a pearl earring; dark arched brow, lashed eye, red lipstick; no glasses.
    rows = {1: (12, 17), 2: (10, 18), 3: (9, 19), 4: (8, 19), 5: (7, 14), 6: (7, 11), 7: (7, 10), 8: (7, 10), 9: (7, 10), 10: (8, 10), 11: (9, 10)}
    for y, (x0, x1) in rows.items(): r(g, x0, Y(y), x1 - x0 + 1, 1, base)
    r(g, 12, Y(1), 5, 1, hi); r(g, 10, Y(2), 3, 1, hi); r(g, 14, Y(2), 4, 1, hi)  # top volume catches the light
    r(g, 9, Y(3), 2, 1, hi); r(g, 13, Y(3), 3, 1, hi); r(g, 18, Y(3), 1, 1, hi); r(g, 8, Y(5), 1, 1, hi); r(g, 8, Y(8), 1, 1, hi)
    for x_, y_ in ((11, 2), (14, 1), (16, 3), (10, 4), (12, 5), (8, 6), (9, 8), (8, 10), (17, 2), (15, 4)): r(g, x_, Y(y_), 1, 1, dk)   # curl shadows
    r(g, 13, Y(4), 1, 1, 'f3_part'); r(g, 15, Y(4), 4, 1, base)                     # side part, fringe swept to the front
    r(g, 11, Y(9), 2, 2, 'skin2'); r(g, 11, Y(11), 2, 1, 'f3_pearl'); r(g, 11, Y(12), 1, 1, 'f3_pearld')               # ear and pearl earring (2 px at the lobe)
    r(g, 15, Y(5), 2, 1, 'f3_brow')                                                 # arched brow
    r(g, 17, Y(7), 1, 1, 'f3_lash')                                                 # lash line in front of the eye
    r(g, 15, Y(11), 2, 1, 'f3_lip')                                                 # lipstick

def _dilma_back_hair(g, era, dx=0, dy=0):
    """Hair volume seen from behind, drawn over `figures_v3_pose.draw_head_back` (which only has flat rows, 10 px wide):
    the same full rounded cut as `head_dilma` (wider than the skull, curling under at the nape, ear and 2 px pearl below it)."""
    base, hi = ('f3_dh0', 'f3_dh1') if era == '2010' else ('f3_dh2', 'f3_dh3')
    rows = {2: (10, 17), 3: (8, 19), 4: (7, 20), 5: (7, 20), 6: (7, 20), 7: (7, 20), 8: (8, 19), 9: (8, 19), 10: (9, 18), 11: (10, 17), 12: (11, 16)}
    for y, (x0, x1) in rows.items(): r(g, x0 + dx, y + dy, x1 - x0 + 1, 1, base)
    r(g, 11 + dx, 2 + dy, 6, 1, hi); r(g, 9 + dx, 3 + dy, 3, 1, hi); r(g, 16 + dx, 3 + dy, 3, 1, hi); r(g, 8 + dx, 5 + dy, 2, 1, hi); r(g, 18 + dx, 6 + dy, 2, 1, hi)
    r(g, 10 + dx, 9 + dy, 2, 1, hi); r(g, 16 + dx, 10 + dy, 2, 1, hi); r(g, 13 + dx, 11 + dy, 2, 1, hi)
    for x_, y_ in ((10, 4), (14, 3), (17, 4), (9, 7), (12, 6), (15, 7), (18, 8), (11, 10), (14, 9), (17, 11)): r(g, x_ + dx, y_ + dy, 1, 1, 'f3_dhc')   # curl shadows
    r(g, 8 + dx, 8 + dy, 1, 2, 'skin2'); r(g, 19 + dx, 8 + dy, 1, 2, 'skin2')                  # lobes
    r(g, 8 + dx, 10 + dy, 1, 2, 'f3_pearl'); r(g, 19 + dx, 10 + dy, 1, 2, 'f3_pearl'); r(g, 8 + dx, 12 + dy, 1, 1, 'f3_pearld'); r(g, 19 + dx, 12 + dy, 1, 1, 'f3_pearld')          # pearl earrings, 2 px

def head_chico(g, pt):
    _head_base(g, pt)
    # GENERIC. No licensed photo of Frei Chico was found (work/RIGHTS.md). Only what the script
    # and the plan say: an adult man of 1975, a factory-floor and union worker, brother of Lula.
    # Drawn: full short dark-brown hair that does not recede, clean-shaven, lean face. No beard.
    poly(g, [pt(9, 6), pt(9, 3), pt(11, 1), pt(16, 1), pt(18, 3), pt(18, 5), pt(15, 4), pt(13, 5), pt(11, 7), pt(11, 10), pt(9, 9)], 'f3_hch')
    r(g, 12, pt(0, 2)[1], 4, 1, 'f3_hch2')
    r(g, 14, pt(0, 12)[1], 3, 1, 'skin0')

# ----------------------------------------------------------------- kinds
# suit = (dark, mid, light), legs = (dark, mid, light), shirt, tie, k = build factor
KINDS = {
 'dilma':     dict(suit=('f3_cr0', 'f3_cr1', 'f3_cr2'), legs=('f3_pant0', 'f3_pant1', 'f3_pant2'), shirt='f3_blousecr', tie=None, k=.78, head='dilma', lapel=True),
 'temer':     dict(suit=('f3_blk0', 'f3_blk1', 'f3_blk2'), shirt='ivory', tie='f3_tienavy', k=.95, head='temer', tiestripe='f3_tiestr'),
 'cunha':     dict(suit=('f3_cn0', 'f3_cn1', 'f3_cn2'), shirt='ivory', tie='f3_tieteal', k=1.06, head='cunha'),
 'alencar':   dict(suit=('f3_ab0', 'f3_ab1', 'f3_ab2'), shirt='ivory', tie='f3_tiecopper', k=1.1, head='alencar'),
 'freichico': dict(suit=('f3_wk0', 'f3_wk1', 'f3_wk2'), legs=('f3_wp0', 'f3_wp1', 'f3_wp2'), shirt='f3_wk2', tie=None, k=.97, head='chico'),
}
ERAS = {'dilma': ('2010', '2014', '2016'), 'temer': ('2016',), 'cunha': ('2015',), 'alencar': ('2002',), 'freichico': ('1975',)}
DEFAULT_ERA = {'dilma': '2010', 'temer': '2016', 'cunha': '2015', 'alencar': '2002', 'freichico': '1975'}

# Costume by scene: `actor_v3(..., clothes=NAME)`. NAME is a key here, a figures_v2 CLOTHES key, or a figures_v2 kind name.
CLOTHES = {
 'jacket_cream': dict(suit=('f3_cr0', 'f3_cr1', 'f3_cr2'), shirt='f3_blousecr', tie=None),     # Dilma 2010-14 (2011 portrait, 2014 speech)
 'jacket_navy':  dict(suit=('f3_dn0', 'f3_dn1', 'f3_dn2'), shirt='f3_blousecr', tie=None),   # Dilma 2015 (patterned dark jacket, April 2015 photo)
 'jacket_red':   dict(suit=('red0', 'red1', 'red2'), shirt='f3_blousecr', tie=None),          # 2.0.0 look; NOT in any photo read here
 'work_ochre':   dict(suit=('f3_wk0', 'f3_wk1', 'f3_wk2'), shirt='f3_wk2', tie=None),
}

def _head_fn(c, era):
    h = c['head']
    return {'dilma': lambda g, pt: head_dilma(g, pt, era), 'temer': head_temer, 'cunha': head_cunha,
            'alencar': head_alencar, 'chico': head_chico}[h]

def actor_v3(kind, pose='idle', phase=0, facing=False, gesture=.5, era=None, clothes=None):
    """Same contract as `actor_v2` (+ `era`, `clothes`): a Geometry in the 28-px frame, about 20 x 49 px.

    kind in dilma | temer | cunha | alencar | freichico. era per kind: see the module docstring.
    clothes: key of CLOTHES here, of figures_v2.CLOTHES, or a figures_v2 kind name. Default per kind.
    """
    if kind not in KINDS: raise ValueError(f'{kind!r}: kinds are {sorted(KINDS)}')
    era = era or DEFAULT_ERA[kind]
    if era not in ERAS[kind]: raise ValueError(f'{kind} era must be one of {ERAS[kind]}')
    c = dict(KINDS[kind])
    if clothes:
        src = CLOTHES.get(clothes) or CLOTHES_V2.get(clothes) or KINDS_V2.get(clothes)
        if src is None: raise ValueError(f'unknown clothes {clothes!r}')
        c.update({k: src[k] for k in ('suit', 'shirt', 'tie')})
    dark, mid, light = c['suit']; ldark, lmid, llight = c.get('legs', c['suit']); k = c['k']
    if pose in _pose.BACK_POSES:                      # seen from behind (figures_v3_pose)
        hk = f'dilma:{era}' if kind == 'dilma' else kind
        spec = dict(suit=c['suit'], shirt=c['shirt'], k=k, belt='wood0', legs=c.get('legs'))
        if kind != 'dilma':
            return _pose.back_view(spec, _pose.BACK_HEAD[hk], pose, phase, facing, gesture, head_fn=_head_fn(c, era))
        spec['belt'] = None                                # tailored jacket: no belt line
        q = _pose.back_view(spec, _pose.BACK_HEAD[hk], pose, phase, False, gesture, head_fn=_head_fn(c, era))
        if pose != 'backturn':                             # backturn already draws head_dilma in profile
            walkb = pose == 'backwalk'
            _dilma_back_hair(q, era, round(.8 * math.sin(phase)) if walkb else 0,
                             round(.6 * (1 - math.cos(phase * 2))) if walkb else 0)
        return flip(q, 27) if facing else q
    sit = pose in _pose.SIT_POSES                      # seated (figures_v3_pose)
    walk = pose == 'walk'; s = math.sin(phase)
    bob = round(.6 * (1 - math.cos(phase * 2))) if walk else 0
    g = Geometry()
    def pt(x, y): return (x, y + bob)
    if sit: _pose.sit_legs(g, (ldark, lmid, llight))
    # legs: gait identical to figures_v2 (feet planted)
    for i in ([] if sit else [0, 1]):
        hip = (10 + i * 5, 30 + bob)
        if walk:
            u = (phase / (2 * math.pi) + i * .5) % 1
            if u < .5: dx = 15 * (.25 - u); lift = 0
            else:
                z = (u - .5) * 2; dx = 15 * (-.25 + .5 * z * z * (3 - 2 * z)); lift = 4 * math.sin(z * math.pi)
            f = (9 + i * 7 + dx, 49 - lift); knee = ((hip[0] + f[0]) * .5 + 2, 40 - lift * .5)
        else: f = (9 + i * 7, 49); knee = (10 + i * 6, 40)
        line(g, hip, knee, 2.2, lmid); line(g, knee, (f[0], f[1] - 2), 1.7, lmid)
        line(g, (hip[0] - 1, hip[1] + 2), (knee[0] - 1, knee[1]), .6, llight if i else ldark)
        line(g, (knee[0], knee[1] + 1), (f[0] - 1, f[1] - 2), .6, ldark)
        poly(g, [(f[0] - 2, f[1] - 2), (f[0] + 2, f[1] - 2), (f[0] + 4, f[1]), (f[0] + 4, f[1] + 1), (f[0] - 2, f[1] + 1)], 'black')
        r(g, f[0] - 1, f[1] - 1, 3, 1, 'steel0')
    # far arm
    far = (6 - 3 * s, 33) if walk else (6, 33)
    if sit: far = (19, 31)
    sh = lambda x: _k(x, k)
    line(g, (sh(7), 17 + bob), (sh(5), 24 + bob), 2, dark); line(g, (sh(5), 24 + bob), (far[0], far[1] + bob), 1.2, 'skin0'); r(g, far[0] - 1, far[1] + bob, 2, 3, 'skin1')
    # torso
    T = lambda pts: [(sh(x), y + bob) for x, y in pts]
    if kind == 'dilma':                               # jacket: narrow set shoulders with a small pad, straight body, flat hem (no waist drawn)
        poly(g, T([(8, 14), (14, 13), (18, 15), (19, 17), (19, 23), (18, 28), (17, 31), (9, 31), (7, 25), (6, 17)]), mid)
        poly(g, T([(8, 16), (10, 15), (10, 25), (11, 29), (8, 30), (7, 25)]), light)
        poly(g, T([(16, 17), (18, 18), (18, 26), (17, 30), (14, 29), (15, 25)]), dark)
        r(g, sh(8), 31 + bob, 10, 1, dark)            # hem shadow (no belt line)
        r(g, sh(7), 15 + bob, 2, 1, light); r(g, sh(18), 15 + bob, 2, 1, light)   # shoulder pad highlight
    else:
        poly(g, T([(8, 14), (14, 13), (18, 16), (19, 23), (17, 31), (8, 31), (6, 25), (6, 18)]), mid)
        poly(g, T([(8, 16), (10, 15), (10, 25), (12, 28), (9, 29), (7, 25)]), light)
        poly(g, T([(16, 16), (18, 18), (18, 26), (17, 30), (14, 29), (15, 25)]), dark)
        r(g, sh(8), 30 + bob, 9, 1, 'wood0')
    # shirt V and tie
    poly(g, T([(10, 14), (14, 13), (17, 15), (13, 23)]), c['shirt'])
    poly(g, T([(10, 14), (12, 13), (13, 16), (12, 18)]), light); poly(g, T([(14, 13), (17, 15), (15, 18), (13, 16)]), light)
    if c['tie']:
        poly(g, T([(13, 16), (15, 16), (15, 22), (13, 25), (12, 21)]), c['tie'])
        if c.get('tiestripe'):
            for yy in (18, 21): r(g, sh(13.5), yy + bob, 1, 1, c['tiestripe'])
    if kind == 'dilma':                                       # jacket edge closing below the neckline, button
        for x_, y_ in ((10, 14), (10, 15), (11, 16), (11, 17), (12, 18), (12, 19), (12, 20), (13, 21), (13, 22)): r(g, sh(x_), y_ + bob, 1, 1, 'f3_lap')   # near lapel edge (notch lapel, 2011 portrait)
        for x_, y_ in ((17, 15), (16, 16), (16, 17), (15, 18), (15, 19), (14, 20), (14, 21), (14, 22)): r(g, sh(x_), y_ + bob, 1, 1, 'f3_lap')           # far lapel edge
        r(g, sh(10), 13 + bob, 2, 1, 'f3_lap'); r(g, sh(15), 13 + bob, 3, 1, 'f3_lap')                                      # collar
        r(g, sh(13), 24 + bob, 1, 1, 'f3_btn')                                                                              # one button
        if era != '2010':                                     # thin gold chain on the blouse V (2014 and 2015 photos; none in the 2011 portrait)
            for x_, y_ in ((11, 15), (12, 16), (13, 17), (14, 17), (15, 16)): r(g, sh(x_), y_ + bob, 1, 1, 'f3_gold')
    _head_fn(c, era)(g, pt)
    # near arm
    shoulder = (sh(17), 17 + bob)
    if walk: elbow = (sh(18), 25 + bob); wrist = (sh(18) + 3 * s, 33 + bob)
    elif pose in ('talk', 'sittalk'): elbow = (sh(18), 26 + bob); wrist = (22 + 3 * gesture, 25 - 6 * gesture + bob)
    elif sit: elbow = (sh(18) + 1, 26 + bob); wrist = (sh(18) + 4, 30 + bob)
    else: elbow = (sh(18), 25 + bob); wrist = (sh(18), 33 + bob)
    line(g, shoulder, elbow, 2, mid); line(g, (sh(17), 18 + bob), (sh(17), 22 + bob), .7, light)
    line(g, elbow, wrist, 1.2, 'skin1'); line(g, (elbow[0] - 1, elbow[1]), (wrist[0] - 1, wrist[1]), .5, 'skin2')
    r(g, wrist[0] - 1, wrist[1], 3, 2, 'skin2')
    if pose in ('talk', 'sittalk'): r(g, wrist[0] + 1, wrist[1] - 1, 2, 1, 'skin1')
    return flip(g, 27) if facing else g
