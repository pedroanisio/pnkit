"""Figures v3 extra for the Lula film 3.0.0: generic (non-real-person) figures the shot plan needs
beyond `actor_v2`, `actor_v3` and the kept 2.0.0 kinds.

Own procedural pixel art in the figures_v2 construction (same 28 px frame, limbs, poses, gait and
mirroring as `actor_v2`); no image input. `figures_v2.py` and `figures_v3_cast.py` are imported, not
edited. Colours added to the shared palette `P` carry the prefix `f4_`.

No real person is depicted: every kind below is a role (mother, girl, nurse, guard, judge...) drawn
only from what SHOTS-3.0.0.md says about it. Faces are plain; nothing is caricatured.

Frame contract (same as figures_v2 / figures_v3_cast): drawn facing right and mirrored for
facing=True. Highest pixel y=1 in idle for every kind (hair, cap or crown). Soles (largest y):
  adults (mother, woman, teacher, father, nurse, doctor, officer, guard, judge, citizen,
  girl era 'adult')                                                          49
  teen  (teen, girl era '15')                                                43
  child (girl era '7')                                                       31  (the kept 2.0.0 `child` height)
Children and teens are drawn at adult size and scaled down with an area-majority resample that
keeps the eye, ribbon, glasses and mask pixels; the walk stride is widened before scaling so that
one cycle still travels 15 px (the build's `walk_rate` assumes 15 px per cycle, so feet do not slide).
Walk adds up to 1 px of bob to the top row, as in `actor_v2`.

`actor_v3x(kind, pose='idle', phase=0, facing=False, gesture=.5, era=None, clothes=None)`

kind        era (first is default)                       clothes (first is default)
mother      adult | older                                apron | street          recurring-family mother, teal apron
girl        7 | 15 | adult                               plain | uniform         recurring girl, red hair ribbon in every age
teen        None                                         work | plain            teen worker, beardless (also the trainee)
father      adult | older                                shirt | work            recurring-family father
teacher     None                                         blouse                  teacher
woman       a | b | c                                    dress                   passer-by or customer, three looks
nurse       glasses | plain                              scrubs | scrubs_unmasked
doctor      None                                         scrubs | scrubs_unmasked  scrubs, open white coat
officer     None                                         uniform                 dark uniform, peaked cap (PF / 1980 officers)
guard       None                                         uniform                 lighter shirt, cap (door and barrier guards)
judge       a | b | c | d | e                            robe                    black robe, white collar band; five looks
citizen     None                                         casual | casual_masked  generic man; masked for the 2020 passer-by
fhc         1998 | 1994 (same figure)                    suit                    Fernando Henrique Cardoso (real person: cues in work/RIGHTS.md)
"""
import math
from . import figures_v3_pose as _pose
from .figures_v2 import Geometry, P, r, poly, line, ellipse, flip, _k, _head_base, _glasses, bbox

# Own named colours (prefix f4_).
P.update({
 # teal apron
 'f4_tl0':'#1d5f5c', 'f4_tl1':'#2f8f87', 'f4_tl2':'#70c4b6',
 # mother blouse / skirt (rust), girl and woman clothes
 'f4_rs0':'#6e3426', 'f4_rs1':'#9d5238', 'f4_rs2':'#c47e58',
 'f4_sk0':'#3a2c33', 'f4_sk1':'#55434c', 'f4_sk2':'#75616a',          # plum-grey skirt
 'f4_yl0':'#b27a22', 'f4_yl1':'#dca43c', 'f4_yl2':'#f2cf72',          # girl 7: mustard dress
 'f4_lb0':'#4a6f98', 'f4_lb1':'#7599c0', 'f4_lb2':'#a6c3de',          # girl 15: light-blue blouse
 'f4_ub0':'#27395a', 'f4_ub1':'#3a5282', 'f4_ub2':'#5873a3',          # uniform navy
 'f4_ubl0':'#aab9c4', 'f4_ubl1':'#cfdae0', 'f4_ubl2':'#eef2f1',       # uniform shirt, pale
 'f4_rib0':'#a81d22', 'f4_rib1':'#d22f2e', 'f4_rib2':'#f06a56',       # red hair ribbon
 # hair
 'f4_hb0':'#2a1c16', 'f4_hb1':'#4a3125', 'f4_hb2':'#6a4a36',          # dark brown
 'f4_hg0':'#8e908e', 'f4_hg1':'#b4b5b1', 'f4_hg2':'#d6d6d0',          # grey
 'f4_hk':'#17120f',
 # father, teacher, passers-by
 'f4_fs0':'#5b6a5c', 'f4_fs1':'#869683', 'f4_fs2':'#b1c0ad',          # father: sage shirt
 'f4_ft0':'#3a3f46', 'f4_ft1':'#555b64', 'f4_ft2':'#747b85',          # trousers
 'f4_mu0':'#8c6a1c', 'f4_mu1':'#c0963a', 'f4_mu2':'#e1c06a',          # teacher: mustard-olive blouse
 'f4_mv0':'#5c4a68', 'f4_mv1':'#80698f', 'f4_mv2':'#a692b2',          # woman a: mauve
 'f4_gb0':'#46606e', 'f4_gb1':'#6c8896', 'f4_gb2':'#97b0bc',          # woman b: grey-blue
 'f4_oc0':'#8a4e24', 'f4_oc1':'#bd7a3f', 'f4_oc2':'#dba76c',          # woman c: ochre
 'f4_cs0':'#6b5a4a', 'f4_cs1':'#9a8670', 'f4_cs2':'#c4b49c',          # citizen: sand shirt
 # health
 'f4_sc0':'#2f6f8f', 'f4_sc1':'#4f95b4', 'f4_sc2':'#8cc2d6',          # nurse scrubs (blue)
 'f4_dc0':'#1f4a5c', 'f4_dc1':'#2f6578', 'f4_dc2':'#4f879b',          # doctor scrubs (deep teal-blue)
 'f4_coat0':'#aeb6b4', 'f4_coat1':'#dde2df', 'f4_coat2':'#f4f6f2',   # white coat
 'f4_mask0':'#aab9bf', 'f4_mask1':'#d6e0e3', 'f4_mask2':'#f1f5f5',   # surgical mask
 # uniforms
 'f4_of0':'#161c28', 'f4_of1':'#232d42', 'f4_of2':'#3a4864',          # officer: dark navy
 'f4_ofc':'#0f1420', 'f4_ofv':'#07090f',                              # cap crown, visor
 'f4_gd0':'#4b5649', 'f4_gd1':'#6e7b6a', 'f4_gd2':'#93a08c',          # guard: green-grey shirt
 'f4_gt0':'#222831', 'f4_gt1':'#363e4b', 'f4_gt2':'#505968',          # guard trousers
 'f4_gcap':'#2c342b',
 'f4_belt':'#15171b',
 # judges
 'f4_rb0':'#101217', 'f4_rb1':'#1d2028', 'f4_rb2':'#343843',
 'f4_jw':'#f0eee6',
 # fhc (1994, 1998): dark navy suit, copper tie (cues: work/RIGHTS.md, section FHC)
 'f4_fn0':'#12192b', 'f4_fn1':'#1f2b47', 'f4_fn2':'#34456c',
 'f4_fc0':'#6a3516', 'f4_fc1':'#94501f', 'f4_fc2':'#b97a3c',
 'f4_fh0':'#5d6063', 'f4_fh1':'#8e908e',            # fhc hair: steel grey, lighter strands
})

# ----------------------------------------------------------------- frame helpers
def _scale(g, s, keep=(), width=27):
    """Area-majority downscale with the top row (y=1) and x origin fixed; `keep` colours get triple weight."""
    if not g.cells: return Geometry()
    inv = 1.0 / s; out = Geometry()
    xs = [x for x, _ in g.cells]; ys = [y for _, y in g.cells]
    keepc = {P[k] for k in keep}
    tx1 = int(max(xs) * s) + 1; ty1 = int((max(ys) - 1) * s) + 2
    for ty in range(0, ty1 + 1):
        y0 = 1 + (ty - 1) * inv; y1 = y0 + inv
        for tx in range(0, tx1 + 1):
            x0 = tx * inv; x1 = x0 + inv
            acc = {}; tot = 0.0
            for yy in range(int(math.floor(y0)), int(math.ceil(y1))):
                hy = min(y1, yy + 1) - max(y0, yy)
                if hy <= 0: continue
                for xx in range(int(math.floor(x0)), int(math.ceil(x1))):
                    wx = min(x1, xx + 1) - max(x0, xx)
                    if wx <= 0: continue
                    a = hy * wx; tot += a
                    c = g.cells.get((xx, yy))
                    if c is not None: acc[c] = acc.get(c, 0.0) + a * (3 if c in keepc else 1)
            if not acc: continue
            c, w = max(sorted(acc.items()), key=lambda kv: kv[1])
            cover = sum(a / (3 if k in keepc else 1) for k, a in acc.items())
            if cover >= .45 * tot or c in keepc: out.cells[tx, ty] = c
    return out

# ----------------------------------------------------------------- heads
def _hair_short(g, pt, hair, hi, grey=None):
    poly(g, [pt(9, 6), pt(9, 3), pt(11, 1), pt(16, 1), pt(18, 3), pt(18, 5), pt(15, 4), pt(13, 5), pt(11, 7), pt(11, 10), pt(9, 9)], hair)
    r(g, 12, pt(0, 2)[1], 4, 1, hi)
    if grey: r(g, 9, pt(0, 5)[1], 3, 4, grey); r(g, 11, pt(0, 4)[1], 2, 1, grey)

def head_man(g, pt, hair='f4_hb0', hi='f4_hb1', grey=None, mask=False, glasses=False, bald=False, fringe=None):
    _head_base(g, pt)
    if bald:
        r(g, 12, pt(0, 1)[1], 4, 1, 'skin2'); r(g, 11, pt(0, 2)[1], 6, 1, 'skin2'); r(g, 12, pt(0, 1)[1], 2, 1, 'skin3')
        poly(g, [pt(9, 9), pt(9, 5), pt(10, 4), pt(12, 5), pt(12, 8), pt(11, 10)], fringe or 'f4_hg2')
    else:
        _hair_short(g, pt, hair, hi, grey)
    r(g, 14, pt(0, 12)[1], 3, 1, 'skin0')
    if glasses: _glasses(g, pt)
    if mask: _mask(g, pt)

def _mask(g, pt):
    # surgical mask: covers nose-to-chin on the visible half of the face, with an ear loop.
    y = pt(0, 8)[1]
    poly(g, [pt(13, 8), pt(19, 8), pt(19, 11), pt(18, 14), pt(14, 14), pt(13, 12)], 'f4_mask1')
    r(g, 14, y, 5, 1, 'f4_mask2'); r(g, 14, pt(0, 12)[1], 4, 1, 'f4_mask0'); r(g, 13, pt(0, 10)[1], 1, 1, 'f4_mask0')
    r(g, 11, pt(0, 9)[1], 2, 1, 'f4_mask0')                                    # ear loop

def head_woman(g, pt, hair='f4_hb0', hi='f4_hb1', grey=None, bun=True, ribbon=False, tail=False, mask=False, glasses=False, cap=None):
    _head_base(g, pt)
    # hair pulled back from the forehead; seen from the side: cap of hair, ear showing, low bun or tail behind.
    poly(g, [pt(9, 9), pt(9, 4), pt(11, 1), pt(16, 1), pt(18, 3), pt(18, 5), pt(15, 4), pt(13, 5), pt(12, 7), pt(11, 8), pt(10, 9)], hair)
    r(g, 12, pt(0, 1)[1], 5, 1, hi); r(g, 14, pt(0, 3)[1], 3, 1, hi)
    if grey:
        r(g, 10, pt(0, 5)[1], 2, 2, grey); r(g, 16, pt(0, 2)[1], 2, 1, grey); r(g, 13, pt(0, 1)[1], 2, 1, grey)
    r(g, 11, pt(0, 9)[1], 1, 2, 'skin2')                                       # ear
    if bun:
        ellipse(g, 8, pt(0, 9)[1], 2.6, 2.6, hair); r(g, 7, pt(0, 8)[1], 2, 1, grey or hi)
    if tail:                                                                   # ponytail hanging behind the neck
        r(g, 8, pt(0, 5)[1], 2, 6, hair); r(g, 7, pt(0, 10)[1], 2, 5, hair); r(g, 7, pt(0, 12)[1], 1, 2, hi)
    if ribbon:                                                                 # red bow at the tie, with two short tails
        r(g, 7, pt(0, 4)[1], 4, 3, 'f4_rib1'); r(g, 7, pt(0, 4)[1], 4, 1, 'f4_rib2'); r(g, 8, pt(0, 5)[1], 2, 1, 'f4_rib0')
        r(g, 6, pt(0, 7)[1], 2, 1, 'f4_rib0'); r(g, 9, pt(0, 7)[1], 1, 1, 'f4_rib0')
    r(g, 15, pt(0, 11)[1], 2, 1, 'skin0')                                      # closed mouth
    if glasses: _glasses(g, pt)
    if cap: poly(g, [pt(9, 6), pt(10, 2), pt(12, 1), pt(16, 1), pt(18, 3), pt(18, 5), pt(12, 5)], cap)
    if mask: _mask(g, pt)

def _cap(g, pt, crown, visor, band=None, hair='f4_hk'):
    r(g, 8, pt(0, 6)[1], 2, 4, hair)                                           # hair at the nape
    poly(g, [pt(9, 5), pt(9, 3), pt(11, 1), pt(17, 1), pt(19, 3), pt(19, 5)], crown)
    r(g, 9, pt(0, 4)[1], 11, 1, band or visor)
    poly(g, [pt(17, 5), pt(22, 5), pt(22, 6), pt(17, 6)], visor)

def head_judge(g, pt, look):
    _head_base(g, pt)
    if look == 'a':   head_man(g, pt, 'f4_hg1', 'f4_hg2', grey='f4_hg0')                         # grey hair
    elif look == 'b': head_man(g, pt, bald=True, fringe='f4_hg2')                                # bald, white fringe
    elif look == 'c': head_man(g, pt, 'f4_hb0', 'f4_hb1', glasses=True)                          # dark hair, glasses
    elif look == 'd': head_man(g, pt, 'f4_hg2', 'f4_jw', grey='f4_hg1', glasses=True)               # white hair, glasses
    elif look == 'e': head_woman(g, pt, 'f4_hb0', 'f4_hb1', grey='f4_hg0', bun=True)             # grey-streaked, bun
    else: raise ValueError(look)

# ----------------------------------------------------------------- body core
# spec: suit (dark, mid, light), legs (dark, mid, light) | None (skin legs), skirt (hem, (dark, mid, light)) | None,
#       shirt, tie, k, head(g, pt), torso_fx(g, T, sh, bob, s), legs_fx(g, bob, s), hand ('skin' ...), keep colours
def _core(spec, pose, phase, gesture, stride):
    sit = pose in _pose.SIT_POSES
    walk = pose == 'walk'; s = math.sin(phase)
    bob = round(.6 * (1 - math.cos(phase * 2))) if walk else 0
    dark, mid, light = spec['suit']; k = spec['k']
    skirt = spec.get('skirt')
    ldark, lmid, llight = spec.get('legs') or ('skin0', 'skin1', 'skin2')
    g = Geometry()
    def pt(x, y): return (x, y + bob)
    sh = lambda x: _k(x, k)
    T = lambda pts: [(sh(x), y + bob) for x, y in pts]
    if sit:                                                                    # seated: thighs forward, skirts and robes hang from the knee
        _pose.sit_legs(g, (ldark, lmid, llight), shoe=spec.get('shoe', 'black'), shoetop=spec.get('shoetop', 'steel0'), x0=round(sh(6.5)),
                       skirt=spec['skirt'][1] if skirt else None, shin=('skin0', 'skin1', 'skin2') if skirt else None,
                       robe=('f4_rb0', 'f4_rb1', 'f4_rb2') if spec.get('legs_fx') is _robe_legs else None)
    for i in ([] if sit else [0, 1]):
        hip = (10 + i * 5, 30 + bob)
        if walk:
            u = (phase / (2 * math.pi) + i * .5) % 1
            if u < .5: dx = 15 * stride * (.25 - u); lift = 0
            else:
                z = (u - .5) * 2; dx = 15 * stride * (-.25 + .5 * z * z * (3 - 2 * z)); lift = 4 * stride * math.sin(z * math.pi)
            f = (9 + i * 7 + dx, 49 - lift); knee = ((hip[0] + f[0]) * .5 + 2, 40 - lift * .5)
        else: f = (9 + i * 7, 49); knee = (10 + i * 6, 40)
        w1, w2 = (2.2, 1.7) if not skirt else (1.9, 1.5)
        line(g, hip, knee, w1, lmid); line(g, knee, (f[0], f[1] - 2), w2, lmid)
        line(g, (hip[0] - 1, hip[1] + 2), (knee[0] - 1, knee[1]), .6, llight if i else ldark)
        line(g, (knee[0], knee[1] + 1), (f[0] - 1, f[1] - 2), .6, ldark)
        poly(g, [(f[0] - 2, f[1] - 2), (f[0] + 2, f[1] - 2), (f[0] + 4, f[1]), (f[0] + 4, f[1] + 1), (f[0] - 2, f[1] + 1)], spec.get('shoe', 'black'))
        r(g, f[0] - 1, f[1] - 1, 3, 1, spec.get('shoetop', 'steel0'))
    far = (6 - 3 * s, 33) if walk else (6, 33)
    if sit: far = (19, 31)
    line(g, (sh(7), 17 + bob), (sh(5), 24 + bob), 2, dark); line(g, (sh(5), 24 + bob), (far[0], far[1] + bob), 1.2, 'skin0'); r(g, far[0] - 1, far[1] + bob, 2, 3, 'skin1')
    if spec.get('legs_fx') and not sit: spec['legs_fx'](g, bob, s, sh)
    if skirt and not sit:
        hem, (sd, sm, sl) = skirt; sw = 1.5 * s if walk else 0
        poly(g, T([(8, 29), (17, 29), (19, hem - 2), (19 + sw / 2, hem), (6 + sw, hem), (6.5, hem - 2)]), sm)
        poly(g, T([(8, 29), (10, 29), (9, hem - 1), (6 + sw, hem), (6.5, hem - 2)]), sl)
        poly(g, T([(15, 29), (17, 29), (19, hem - 2), (19 + sw / 2, hem), (15, hem)]), sd)
    poly(g, T([(8, 14), (14, 13), (18, 16), (19, 23), (17, 31), (8, 31), (6, 25), (6, 18)]), mid)
    poly(g, T([(8, 16), (10, 15), (10, 25), (12, 28), (9, 29), (7, 25)]), light)
    poly(g, T([(16, 16), (18, 18), (18, 26), (17, 30), (14, 29), (15, 25)]), dark)
    if spec.get('belt'): r(g, sh(8), 30 + bob, 9, 1, spec['belt'])
    poly(g, T([(10, 14), (14, 13), (17, 15), (13, 23)]), spec['shirt'])
    poly(g, T([(10, 14), (12, 13), (13, 16), (12, 18)]), light); poly(g, T([(14, 13), (17, 15), (15, 18), (13, 16)]), light)
    if spec.get('tie'): poly(g, T([(13, 16), (15, 16), (15, 22), (13, 25), (12, 21)]), spec['tie'])
    if spec.get('torso_fx'): spec['torso_fx'](g, T, sh, bob, s, **({'sit': True} if sit and spec['torso_fx'] in (_apron, _coat) else {}))
    spec['head'](g, pt)
    shoulder = (sh(17), 17 + bob)
    if walk: elbow = (sh(18), 25 + bob); wrist = (sh(18) + 3 * s * stride, 33 + bob)
    elif pose in ('talk', 'sittalk'): elbow = (sh(18), 26 + bob); wrist = (22 + 3 * gesture, 25 - 6 * gesture + bob)
    elif sit: elbow = (sh(18) + 1, 26 + bob); wrist = (sh(18) + 4, 30 + bob)
    else: elbow = (sh(18), 25 + bob); wrist = (sh(18), 33 + bob)
    line(g, shoulder, elbow, 2, mid); line(g, (sh(17), 18 + bob), (sh(17), 22 + bob), .7, light)
    sleeve = spec.get('sleeve')                                                  # long sleeve: cover the forearm
    if sleeve:
        line(g, elbow, ((elbow[0] * .3 + wrist[0] * .7), (elbow[1] * .3 + wrist[1] * .7)), 1.9, sleeve)
        line(g, (elbow[0] - 1, elbow[1]), (elbow[0] * .3 + wrist[0] * .7 - 1, elbow[1] * .3 + wrist[1] * .7), .5, light)
        t = (elbow[0] * .3 + wrist[0] * .7, elbow[1] * .3 + wrist[1] * .7)
        line(g, t, wrist, 1.2, 'skin1')
    else:
        line(g, elbow, wrist, 1.2, 'skin1'); line(g, (elbow[0] - 1, elbow[1]), (wrist[0] - 1, wrist[1]), .5, 'skin2')
    r(g, wrist[0] - 1, wrist[1], 3, 2, 'skin2')
    if pose in ('talk', 'sittalk'): r(g, wrist[0] + 1, wrist[1] - 1, 2, 1, 'skin1')
    return g

# ----------------------------------------------------------------- spec fx
def _apron(g, T, sh, bob, s, sit=False):
    # teal apron: bib with neck straps, waist tie, front panel over the skirt, pocket.
    poly(g, T([(11, 15), (15, 15), (16, 22), (16, 30), (11, 30)]), 'f4_tl1')
    r(g, sh(11), 15 + bob, 1, 14, 'f4_tl2'); r(g, sh(16), 18 + bob, 1, 12, 'f4_tl0')
    r(g, sh(11), 14 + bob, 1, 2, 'f4_tl0'); r(g, sh(15), 14 + bob, 1, 2, 'f4_tl0')   # straps
    r(g, sh(8), 30 + bob, 10, 1, 'f4_tl0')                                           # waist tie
    if sit: return                                                                  # seated: the lap panel is the skirt
    sw = round(1.2 * s) if s else 0
    poly(g, T([(9, 31), (17, 31), (18, 41), (8 + sw, 41)]), 'f4_tl1')
    r(g, sh(9), 31 + bob, 1, 10, 'f4_tl2'); r(g, sh(17), 33 + bob, 1, 8, 'f4_tl0')
    r(g, sh(11), 35 + bob, 4, 3, 'f4_tl0'); r(g, sh(12), 36 + bob, 2, 1, 'f4_tl1')   # pocket

def _robe(g, T, sh, bob, s):
    # judge's robe: yoke and chest over the torso, white collar tabs.
    poly(g, T([(10, 14), (14, 13), (17, 15), (16, 22), (13, 20)]), 'f4_rb1')
    r(g, sh(12), 15 + bob, 2, 3, 'f4_jw'); r(g, sh(14), 16 + bob, 1, 3, 'f4_jw')

def _robe_legs(g, bob, s, sh):
    sw = round(1.3 * s)
    T = lambda pts: [(sh(x), y + bob) for x, y in pts]
    poly(g, T([(7, 28), (18, 28), (21, 44), (4 + sw, 44)]), 'f4_rb1')
    poly(g, T([(7, 28), (10, 28), (8, 43), (4 + sw, 44)]), 'f4_rb2')
    poly(g, T([(15, 28), (18, 28), (21, 44), (16, 44)]), 'f4_rb0')
    r(g, sh(4 + sw), 44 + bob, 17, 1, 'f4_rb0')

def _coat_legs(g, bob, s, sh):
    pass

def _coat(g, T, sh, bob, s, sit=False):
    # doctor's open white coat over the scrub top: lapels and long hem on the near side.
    e = 30 if sit else 40                                                           # seated: the coat stops at the hips
    poly(g, T([(8, 14), (11, 14), (11, 26), (11, e), (7, e), (6, 25), (6, 18)]), 'f4_coat1')
    poly(g, T([(15, 16), (18, 16), (19, 23), (18, e), (14, e), (15, 28)]), 'f4_coat1')
    r(g, sh(15), 20 + bob, 1, e - 20, 'f4_coat0'); r(g, sh(11), 16 + bob, 1, e - 16, 'f4_coat0')
    r(g, sh(7), 18 + bob, 1, e - 18, 'f4_coat2')

def _scrub_trim(g, T, sh, bob, s):
    pass

def _shirt_pocket_guard(g, T, sh, bob, s):
    r(g, sh(15), 20 + bob, 2, 2, 'f4_gd0'); r(g, sh(15), 20 + bob, 2, 1, 'f4_gd1')

# ----------------------------------------------------------------- kinds
def _mk(spec, **ov): d = dict(spec); d.update(ov); return d

def _spec(kind, era, clothes):
    """Return (spec, scale_sole_y or None, keep colours). Raises ValueError for unknown kind/era/clothes."""
    def pick(options, value, name):
        value = value or next(iter(options))
        if value not in options: raise ValueError(f'{kind}: {name} must be one of {sorted(options)}, got {value!r}')
        return value, options[value]
    KEEP = ('ink', 'f4_rib1', 'f4_rib2', 'f4_rib0', 'f2_glass', 'f2_glass2')
    if kind == 'mother':
        era, _ = pick({'adult': 0, 'older': 1}, era, 'era'); old = era == 'older'
        cl, _ = pick({'apron': 0, 'street': 1}, clothes, 'clothes')
        head = lambda g, pt: head_woman(g, pt, 'f4_hb0', 'f4_hb1', grey='f4_hg0' if old else None, bun=True)
        base = dict(suit=('f4_rs0', 'f4_rs1', 'f4_rs2'), shirt='f4_rs2', tie=None, k=.88, head=head,
                    skirt=(41, ('f4_sk0', 'f4_sk1', 'f4_sk2')), sleeve=None)
        if cl == 'apron': base.update(torso_fx=_apron, skirt=(41, ('f4_rs0', 'f4_rs1', 'f4_rs2')))
        else: base.update(suit=('f4_ub0', 'f4_ub1', 'f4_ub2'), shirt='f4_ub2', skirt=(41, ('f4_sk0', 'f4_sk1', 'f4_sk2')))
        if old: base['k'] = .9
        return base, None, KEEP
    if kind == 'teacher':
        pick({'blouse': 0}, clothes, 'clothes'); pick({None: 0}, era, 'era') if era else None
        head = lambda g, pt: head_woman(g, pt, 'f4_hb0', 'f4_hb1', bun=True, glasses=False)
        return dict(suit=('f4_mu0', 'f4_mu1', 'f4_mu2'), shirt='f4_mu2', tie=None, k=.88, head=head,
                    skirt=(43, ('f4_sk0', 'f4_sk1', 'f4_sk2')), sleeve=None), None, KEEP
    if kind == 'woman':
        era, _ = pick({'a': 0, 'b': 1, 'c': 2}, era, 'era'); pick({'dress': 0}, clothes, 'clothes')
        cols = {'a': ('f4_mv0', 'f4_mv1', 'f4_mv2'), 'b': ('f4_gb0', 'f4_gb1', 'f4_gb2'), 'c': ('f4_oc0', 'f4_oc1', 'f4_oc2')}[era]
        hair = {'a': ('f4_hb1', 'f4_hb2', None), 'b': ('f4_hk', 'f4_hb0', None), 'c': ('f4_hb0', 'f4_hb1', 'f4_hg0')}[era]
        head = lambda g, pt: head_woman(g, pt, hair[0], hair[1], grey=hair[2], bun=era != 'b', tail=era == 'b')
        return dict(suit=cols, shirt=cols[2], tie=None, k=.88, head=head, skirt=(40 + (era == 'c') * 3, cols)), None, KEEP
    if kind == 'girl':
        era, _ = pick({'7': 0, '15': 1, 'adult': 2}, era, 'era')
        cl, _ = pick({'plain': 0, 'uniform': 1}, clothes, 'clothes')
        if cl == 'uniform' and era != 'adult': raise ValueError("girl: clothes 'uniform' exists for era 'adult' only (shot 30b)")
        head = lambda g, pt: head_woman(g, pt, 'f4_hb0', 'f4_hb1', bun=False, tail=True, ribbon=True)
        if era == '7':
            sp = dict(suit=('f4_yl0', 'f4_yl1', 'f4_yl2'), shirt='f4_yl2', tie=None, k=.9, head=head, skirt=(42, ('f4_yl0', 'f4_yl1', 'f4_yl2')))
            return sp, 31, KEEP
        if cl == 'uniform':
            sp = dict(suit=('f4_ubl0', 'f4_ubl1', 'f4_ubl2'), shirt='f4_ubl2', tie=None, k=.88, head=head,
                      skirt=(42, ('f4_ub0', 'f4_ub1', 'f4_ub2')), belt='f4_ub0')
            return sp, None, KEEP
        sp = dict(suit=('f4_lb0', 'f4_lb1', 'f4_lb2'), shirt='f4_lb2', tie=None, k=.88, head=head, skirt=(42, ('f4_sk0', 'f4_sk1', 'f4_sk2')))
        return sp, (43 if era == '15' else None), KEEP
    if kind == 'teen':
        pick({None: 0}, era, 'era') if era else None
        cl, _ = pick({'work': 0, 'plain': 1}, clothes, 'clothes')
        head = lambda g, pt: head_man(g, pt, 'f4_hb0', 'f4_hb1')
        if cl == 'work':   # same blue work colours as Lula 'work' clothes, so the 03a growth swap reads as one person
            return dict(suit=('blue0', 'blue1', 'blue2'), shirt='blue2', tie=None, k=.95, head=head, legs=('f4_ft0', 'f4_ft1', 'f4_ft2'), belt='wood0'), 43, KEEP
        return dict(suit=('f4_cs0', 'f4_cs1', 'f4_cs2'), shirt='f4_cs2', tie=None, k=.95, head=head, legs=('f4_ft0', 'f4_ft1', 'f4_ft2'), belt='wood0'), 43, KEEP
    if kind == 'father':
        era, _ = pick({'adult': 0, 'older': 1}, era, 'era'); old = era == 'older'
        cl, _ = pick({'shirt': 0, 'work': 1}, clothes, 'clothes')
        head = lambda g, pt: head_man(g, pt, 'f4_hb0' if not old else 'f4_hg0', 'f4_hb1' if not old else 'f4_hg1', grey=None if not old else 'f4_hg1')
        suit = ('f4_fs0', 'f4_fs1', 'f4_fs2') if cl == 'shirt' else ('blue0', 'blue1', 'blue2')
        return dict(suit=suit, shirt=suit[2], tie=None, k=1.0, head=head, legs=('f4_ft0', 'f4_ft1', 'f4_ft2'), belt='wood0'), None, KEEP
    if kind == 'citizen':
        pick({None: 0}, era, 'era') if era else None
        cl, _ = pick({'casual': 0, 'casual_masked': 1}, clothes, 'clothes')
        head = lambda g, pt: head_man(g, pt, 'f4_hb1', 'f4_hb2', mask=cl == 'casual_masked')
        return dict(suit=('f4_cs0', 'f4_cs1', 'f4_cs2'), shirt='f4_cs2', tie=None, k=1.0, head=head, legs=('f4_ft0', 'f4_ft1', 'f4_ft2'), belt='wood0'), None, KEEP
    if kind == 'nurse':
        era, _ = pick({'glasses': 0, 'plain': 1}, era, 'era'); cl, _ = pick({'scrubs': 0, 'scrubs_unmasked': 1}, clothes, 'clothes')
        head = lambda g, pt: head_woman(g, pt, 'f4_hb1', 'f4_hb2', bun=True, glasses=era == 'glasses', mask=cl == 'scrubs')
        return dict(suit=('f4_sc0', 'f4_sc1', 'f4_sc2'), shirt='f4_sc2', tie=None, k=.9, head=head, legs=('f4_sc0', 'f4_sc1', 'f4_sc2'),
                    shoe='f4_coat2', shoetop='f4_coat0'), None, KEEP + ('f4_mask0', 'f4_mask1', 'f4_mask2')
    if kind == 'doctor':
        pick({None: 0}, era, 'era') if era else None
        cl, _ = pick({'scrubs': 0, 'scrubs_unmasked': 1}, clothes, 'clothes')
        head = lambda g, pt: head_man(g, pt, 'f4_hg0', 'f4_hg1', grey='f4_hg1', mask=cl == 'scrubs')
        return dict(suit=('f4_dc0', 'f4_dc1', 'f4_dc2'), shirt='f4_dc2', tie=None, k=1.0, head=head, legs=('f4_dc0', 'f4_dc1', 'f4_dc2'),
                    torso_fx=_coat, shoe='f4_coat0', shoetop='f4_coat1'), None, KEEP + ('f4_mask0', 'f4_mask1', 'f4_mask2')
    if kind == 'officer':
        pick({None: 0}, era, 'era') if era else None; pick({'uniform': 0}, clothes, 'clothes')
        head = lambda g, pt: (head_man(g, pt, 'f4_hk', 'f4_hk'), _cap(g, pt, 'f4_ofc', 'f4_ofv', 'f4_of2'))
        return dict(suit=('f4_of0', 'f4_of1', 'f4_of2'), shirt='f4_of2', tie='f4_ofc', k=1.02, head=head, legs=('f4_of0', 'f4_of0', 'f4_of1'),
                    belt='f4_belt', sleeve='f4_of1'), None, KEEP
    if kind == 'guard':
        pick({None: 0}, era, 'era') if era else None; pick({'uniform': 0}, clothes, 'clothes')
        head = lambda g, pt: (head_man(g, pt, 'f4_hb0', 'f4_hb1'), _cap(g, pt, 'f4_gcap', 'f4_belt', 'f4_gd0', hair='f4_hb0'))
        return dict(suit=('f4_gd0', 'f4_gd1', 'f4_gd2'), shirt='f4_gd2', tie=None, k=1.02, head=head, legs=('f4_gt0', 'f4_gt1', 'f4_gt2'),
                    belt='f4_belt', torso_fx=_shirt_pocket_guard), None, KEEP
    if kind == 'judge':
        era, _ = pick({c: 0 for c in 'abcde'}, era, 'era'); pick({'robe': 0}, clothes, 'clothes')
        head = lambda g, pt: head_judge(g, pt, era)
        return dict(suit=('f4_rb0', 'f4_rb1', 'f4_rb2'), shirt='f4_jw', tie=None, k={'a': 1.0, 'b': 1.12, 'c': .96, 'd': 1.04, 'e': .9}[era], head=head, torso_fx=_robe, legs_fx=_robe_legs,
                    legs=('f4_rb0', 'f4_rb0', 'f4_rb1'), sleeve='f4_rb1'), None, KEEP
    if kind == 'fhc':   # a real person (Fernando Henrique Cardoso, TV figure of 06g / 06h): cues from licensed photos only, see work/RIGHTS.md
        pick({'1998': 0, '1994': 1}, era, 'era'); pick({'suit': 0}, clothes, 'clothes')
        head = lambda g, pt: head_man(g, pt, 'f4_fh0', 'f4_fh1', grey='f4_hg0', glasses=True)      # full grey hair brushed back, thin wire glasses, clean-shaven
        return dict(suit=('f4_fn0', 'f4_fn1', 'f4_fn2'), shirt='f4_jw', tie='f4_fc1', k=1.0, head=head,
                    legs=('f4_fn0', 'f4_fn0', 'f4_fn1')), None, KEEP
    raise ValueError(f'{kind!r}: kinds are {sorted(KINDS)}')

KINDS = ('mother', 'girl', 'teen', 'father', 'teacher', 'woman', 'nurse', 'doctor', 'officer', 'guard', 'judge', 'citizen', 'fhc')

def actor_v3x(kind, pose='idle', phase=0, facing=False, gesture=.5, era=None, clothes=None):
    """Same contract as `actor_v3` (+ `era`, `clothes`): a Geometry in the 28-px frame.

    Soles (max y) at idle: 49 for adult kinds, 43 for teen kinds, 31 for girl era '7'; highest pixel y=1.
    See the module docstring for the kinds and their era / clothes options.
    """
    if kind not in KINDS: raise ValueError(f'{kind!r}: kinds are {sorted(KINDS)}')
    if pose not in ('idle', 'walk', 'talk') + _pose.NEW_POSES:
        raise ValueError(f'pose must be idle | walk | talk | sit | sittalk | back | backwalk | backhands | backturn | backsit, got {pose!r}')
    spec, sole, keep = _spec(kind, era, clothes)
    if pose in _pose.BACK_POSES:                                              # seen from behind, built at adult size, then scaled like the rest
        bspec, bhead = _pose.extra_back(kind, era, clothes, spec)
        g = _pose.back_view(bspec, bhead, pose, phase, False, gesture, head_fn=lambda u, pt: spec['head'](u, pt))
        if sole is not None:
            s = sole / 49.0; g = _scale(g, s, keep)
        else:
            s = 1.0
        return flip(g, round(27 * s)) if facing else g
    if sole is None:
        g = _core(spec, pose, phase, gesture, 1.0)
        return flip(g, 27) if facing else g
    s = sole / 49.0
    g = _scale(_core(spec, pose, phase, gesture, 1.0 / s), s, keep)
    return flip(g, round(27 * s)) if facing else g
