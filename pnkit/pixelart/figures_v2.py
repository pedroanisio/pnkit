"""Figures v2 for the Lula film 3.0.0: own procedural pixel art, no image input.

Same grid, scale and API shape as chapter_art.actor / full_art.actor: figures are
about 20 x 51 logical px on the 320x180 grid (6x at 1920x1080), drawn facing right
and mirrored with `flip(g, 27)` for facing=True. Limbs follow the worker construction
(two-cycle foot contact on 'walk', bob on the body, segmented arms).

Recognition comes from silhouette cues only (hair line and colour, glasses, beard,
build, suit, tie, hat). Reference photos were used once, only to read these features
(see work/RIGHTS.md); nothing is traced, converted or embedded.

Height contract (scene 31): every kind has its highest pixel at y=1 (hair or hat crown)
and its soles at y=50 in idle, so all kinds share one head-to-foot extent.
"""
import math
from .geometry import Geometry
from .scene_art import P, r, poly, line, ellipse

# Own named colours (added to the shared palette dict P; names are prefixed f2_).
P.update({
 'f2_white':'#f2f0e6','f2_whiteshade':'#bcc0b6','f2_whitedeep':'#8f958d',
 'f2_straw':'#e3cf99','f2_strawshade':'#b79e68','f2_band':'#5a3b2a',
 'f2_char0':'#15181e','f2_char1':'#262a33','f2_char2':'#444a56',
 'f2_navy0':'#17263a','f2_navy1':'#243a56','f2_navy2':'#3f5c7c','f2_stripe':'#4b5f7a',
 'f2_ash0':'#5d6563','f2_ash1':'#8f9894','f2_ash2':'#bcc3bc',
 'f2_sky0':'#4f7f9f','f2_sky1':'#7fa9c4','f2_sky2':'#aecbd8',
 'f2_hmoro':'#16120f','f2_hdel':'#2a201c','f2_hjair':'#6a5d54','f2_hjair2':'#8a8078',
 'f2_hflav':'#3b2c25','f2_hcol':'#2c211c','f2_hgrey':'#a7aaa4',
 'f2_tiered':'#a3352f','f2_tiepink':'#c45a78','f2_tieblue':'#2f4f93','f2_tiedark':'#1c1f2a',
 'f2_tiestripe':'#3c4f7c','f2_tiewine':'#6a1f2c','f2_tiesky':'#7ea4d0',
 'f2_glass':'#5a5652','f2_glass2':'#9a948c',
 # 3.0.0 v3: warm-neutral salt-and-pepper (no blue, no teal) for Lula 'pres'
 'f2_sp0':'#575350','f2_sp1':'#8d8984','f2_sp2':'#c3bfb7','f2_sph':'#6a6661',
 # Flavio: charcoal-grey suit, silver tie
 'f2_gc0':'#23262c','f2_gc1':'#3b3f47','f2_gc2':'#585d68','f2_tiesilver':'#a2a7b0','f2_tieplum':'#6b3a4f',
 # prison / plain clothes: grey tracksuit, light tee
 'f2_tr0':'#5b5d60','f2_tr1':'#7c7e80','f2_tr2':'#a3a5a4','f2_tee':'#dcd9cf'})

from . import figures_v3_pose as _pose

def flip(q, width=27):
    g = Geometry(); g.cells = {(width - x, y): c for (x, y), c in q.cells.items()}; return g

def _k(x, k):  # horizontal build factor around the torso centre
    return 12.5 + (x - 12.5) * k

# ----------------------------------------------------------------- heads
def _head_base(g, pt, skin=('skin0', 'skin1', 'skin2')):
    r(g, 11, pt(0, 10)[1], 4, 5, skin[0])
    poly(g, [pt(10, 4), pt(13, 2), pt(17, 4), pt(17, 8), pt(19, 9), pt(17, 10), pt(16, 13), pt(12, 13), pt(10, 10)], skin[1])
    poly(g, [pt(14, 5), pt(17, 5), pt(17, 8), pt(18, 9), pt(16, 10), pt(16, 12), pt(14, 12), pt(13, 9)], skin[2])
    r(g, 16, pt(0, 7)[1], 1, 1, 'ink')

def _glasses(g, pt):
    # thin rectangular frame, as in the Dallagnol and Alckmin photos: a mid-grey top bar that
    # runs back to the ear, a lighter lower rim, the eye (ink) between them. No blue, no solid lens,
    # so the eye row never reads as a dark mask at 20 px.
    y = pt(0, 7)[1]
    r(g, 11, y - 1, 7, 1, 'f2_glass')                              # top bar + temple arm
    r(g, 14, y + 1, 4, 1, 'f2_glass2')                             # lower rim
    r(g, 14, y, 1, 1, 'f2_glass2'); r(g, 16, y, 1, 1, 'ink')       # nose-side rim, eye

# Beard / hair colours per Lula era: (hair, beard mass, beard shade, moustache edge/lower shade)
LULA_ERAS = {
 # owner 2026-10-06: black beard in the factory and union years (scenes 03-05, 1970s-80s)
 'black':    dict(hair='f2_bk1', beard='f2_bk0', shade='f2_bk2', edge='f2_bk3', hair2=None),
 # salt-and-pepper, warm neutral greys only: mass sp1, light flecks sp2, dark-grey shadow sp0
 'pres':     dict(hair='f2_sph', beard='f2_sp1', shade='f2_sp0', edge='f2_sp2', hair2='f2_sp2', fleck='f2_sp2'),
 'white':    dict(hair='f2_white', beard='f2_white', shade='f2_whiteshade', edge='f2_whitedeep', hair2=None),
 'whitehat': dict(hair='f2_white', beard='f2_white', shade='f2_whiteshade', edge='f2_whitedeep', hair2=None),
}
P.update({'f2_bk0':'#17120f','f2_bk1':'#241c18','f2_bk2':'#2f2520','f2_bk3':'#4a3a30'})

def head_lula(g, pt, era):
    e = LULA_ERAS[era]; hat = era == 'whitehat'
    _head_base(g, pt, ('skin0', 'skin1', 'skin2'))
    # hair: short, receding at the front (no hair mass above the brow line)
    poly(g, [pt(9, 5), pt(10, 2), pt(13, 1), pt(16, 2), pt(17, 4), pt(14, 4), pt(12, 5), pt(11, 7), pt(11, 10), pt(9, 9)], e['hair'])
    if e['hair2']: r(g, 10, pt(0, 5)[1], 2, 1, e['hair2']); r(g, 11, pt(0, 3)[1], 3, 1, e['hair2'])
    elif era == 'white': r(g, 9, pt(0, 7)[1], 2, 3, e['shade'])
    # BEARD: one large mass from the ear along the jaw to past the chin, plus moustache.
    poly(g, [pt(10, 8), pt(12, 9), pt(15, 10), pt(17, 10), pt(19, 10), pt(19, 12), pt(18, 15), pt(15, 16), pt(12, 15), pt(10, 12)], e['beard'])
    poly(g, [pt(11, 12), pt(14, 13), pt(17, 13), pt(17, 15), pt(14, 15.5), pt(11, 14)], e['shade'])
    r(g, 15, pt(0, 10)[1], 4, 1, e['edge'])                      # moustache edge
    r(g, 14, pt(0, 12)[1], 3, 1, 'skin0')                        # mouth shadow keeps the mass from reading as a bib
    if e.get('fleck'):                                           # salt-and-pepper: light flecks on the mass
        mass, fl = P[e['beard']], P[e['fleck']]
        for (x, y), c in list(g.cells.items()):
            if c == mass and (x + 2 * y) % 4 == 0: g.cells[x, y] = fl
    if hat:
        # PANAMA: straw crown with dark band, wide brim (1 px beyond the face in front, 2 px behind).
        poly(g, [pt(10, 4), pt(10, 2), pt(12, 1), pt(16, 1), pt(18, 2), pt(18, 4)], 'f2_straw')
        r(g, 10, pt(0, 3)[1], 9, 1, 'f2_band'); r(g, 15, pt(0, 1)[1], 3, 1, 'f2_strawshade')
        poly(g, [pt(7, 6), pt(8, 4), pt(12, 4), pt(18, 4), pt(22, 5), pt(22, 6), pt(16, 6)], 'f2_straw')
        r(g, 8, pt(0, 6)[1], 14, 1, 'f2_strawshade')

def head_moro(g, pt):
    _head_base(g, pt)
    # thick, dark, slightly wavy hair with a heavy fringe; clean-shaven strong jaw.
    poly(g, [pt(9, 6), pt(9, 3), pt(11, 1), pt(15, 1), pt(18, 3), pt(18, 5), pt(15, 4), pt(13, 5), pt(11, 7), pt(11, 10), pt(9, 9)], 'f2_hmoro')
    r(g, 14, pt(0, 3)[1], 3, 1, 'f2_hmoro'); r(g, 16, pt(0, 4)[1], 2, 1, 'f2_hmoro')
    r(g, 12, pt(0, 12)[1], 4, 1, 'skin0')                        # jaw shade

def head_dallagnol(g, pt):
    _head_base(g, pt)
    poly(g, [pt(9, 5), pt(10, 2), pt(13, 1), pt(17, 2), pt(18, 4), pt(14, 3), pt(12, 5), pt(11, 7), pt(11, 10), pt(9, 9)], 'f2_hdel')
    r(g, 15, pt(0, 4)[1], 3, 1, 'f2_hdel')
    _glasses(g, pt)

def head_bolsonaro(g, pt):
    _head_base(g, pt, ('skin0', 'skin1', 'skin2'))
    # greying brown hair combed to the side, receding at the temple, ear visible; clean-shaven.
    poly(g, [pt(9, 6), pt(9, 3), pt(12, 1), pt(16, 1), pt(18, 3), pt(17, 5), pt(14, 4), pt(12, 5), pt(11, 7), pt(11, 10), pt(9, 9)], 'f2_hjair')
    r(g, 12, pt(0, 2)[1], 4, 1, 'f2_hjair2'); r(g, 9, pt(0, 6)[1], 2, 2, 'f2_hjair2')
    r(g, 15, pt(0, 6)[1], 3, 1, 'f2_hjair')
    r(g, 14, pt(0, 12)[1], 3, 1, 'skin0')                        # set mouth, firm jaw

def head_flavio(g, pt):
    _head_base(g, pt, ('skin0', 'skin1', 'skin2'))
    # photo (Senado, 2025): short dark-brown hair, front lifted; full cheek and jaw. Clean-shaven, no glasses.
    poly(g, [pt(9, 6), pt(10, 2), pt(13, 1), pt(16, 1), pt(18, 3), pt(17, 4), pt(14, 3), pt(12, 5), pt(11, 7), pt(11, 10), pt(9, 9)], 'f2_hflav')
    r(g, 16, pt(0, 1)[1], 2, 1, 'f2_hflav'); r(g, 17, pt(0, 2)[1], 1, 1, 'f2_hflav')   # lifted front
    r(g, 17, pt(0, 10)[1], 1, 3, 'skin1'); r(g, 16, pt(0, 12)[1], 1, 1, 'skin1'); r(g, 12, pt(0, 12)[1], 4, 1, 'skin0')   # fuller cheek and jaw, 1 px forward

def head_alckmin(g, pt):
    _head_base(g, pt, ('skin0', 'skin1', 'skin2'))
    # bald crown (skin), grey hair only at the side and back, glasses, narrow face.
    r(g, 12, pt(0, 1)[1], 4, 1, 'skin2'); r(g, 11, pt(0, 2)[1], 6, 1, 'skin2'); r(g, 12, pt(0, 1)[1], 2, 1, 'skin3')  # bright bald crown
    poly(g, [pt(9, 8), pt(9, 5), pt(10, 4), pt(12, 5), pt(12, 8), pt(11, 10), pt(9, 10)], 'f2_hgrey')
    r(g, 9, pt(0, 4)[1], 1, 1, 'f2_hgrey')
    _glasses(g, pt)

def head_collor(g, pt):
    _head_base(g, pt)
    # 1989 look: full dark hair swept up and back with a high front volume (shape from the 2019 photo, colour from the 1990 photo); no grey; clean-shaven.
    poly(g, [pt(9, 7), pt(9, 3), pt(11, 1), pt(16, 1), pt(19, 3), pt(18, 5), pt(15, 4), pt(13, 5), pt(11, 7), pt(11, 10), pt(9, 10)], 'f2_hcol')
    r(g, 14, pt(0, 2)[1], 4, 1, 'f2_hcol'); r(g, 18, pt(0, 4)[1], 1, 1, 'f2_hcol')

# ----------------------------------------------------------------- kinds
# suit = (dark, mid, light), trousers, shirt, tie, k = build factor, head(g,pt)
KINDS = {
 'lula2023':    dict(suit=('f2_navy0', 'f2_navy1', 'f2_navy2'), shirt='ivory', tie='f2_tiepink', k=1.0, head=lambda g, pt: head_lula(g, pt, 'white')),
 'lula2023hat': dict(suit=('f2_navy0', 'f2_navy1', 'f2_navy2'), shirt='ivory', tie='f2_tiepink', k=1.0, head=lambda g, pt: head_lula(g, pt, 'whitehat')),
 # same body, face and proportions in every era; only beard/hair colour, hat and (by default) clothes change
 'lula_black':  dict(suit=('blue0', 'blue1', 'blue2'), shirt='blue2', tie=None, k=1.0, head=lambda g, pt: head_lula(g, pt, 'black')),
 'lula_pres':   dict(suit=('black', 'blue0', 'blue1'), shirt='ivory', tie='red0', k=1.0, head=lambda g, pt: head_lula(g, pt, 'pres')),
 'moro':        dict(suit=('f2_char0', 'f2_char1', 'f2_char2'), shirt='f2_sky2', tie='f2_tieblue', k=.96, head=head_moro),
 'dallagnol':   dict(suit=('steel0', 'steel1', 'steel2'), shirt='ivory', tie='f2_tiedark', k=.9, head=head_dallagnol),
 'bolsonaro':   dict(suit=('f2_navy0', 'f2_char1', 'f2_stripe'), shirt='ivory', tie='f2_tiestripe', k=1.1, head=head_bolsonaro, stripes=True),
 'flavio':      dict(suit=('f2_gc0', 'f2_gc1', 'f2_gc2'), shirt='ivory', tie='f2_tiesilver', k=1.0, head=head_flavio),
 'alckmin':     dict(suit=('f2_ash0', 'f2_ash1', 'f2_ash2'), shirt='ivory', tie='f2_tieplum', k=1.0, head=head_alckmin),
 'collor':      dict(suit=('f2_navy0', 'f2_navy1', 'f2_navy2'), shirt='ivory', tie='f2_tiewine', k=1.02, head=head_collor),
}

# Costume by scene, not by figure: `actor_v2(..., clothes=NAME)`. NAME is a key here, or (legacy) another kind's name.
CLOTHES = {
 'suit_navy':     dict(suit=('f2_navy0', 'f2_navy1', 'f2_navy2'), shirt='ivory', tie='f2_tiepink'),   # Lula 2017-: navy, ivory shirt, pink tie
 'suit_black':    dict(suit=('black', 'blue0', 'blue1'), shirt='ivory', tie='red0'),                  # presidency years
 'suit_charcoal': dict(suit=('f2_gc0', 'f2_gc1', 'f2_gc2'), shirt='ivory', tie='f2_tiesilver'),
 'work':          dict(suit=('blue0', 'blue1', 'blue2'), shirt='blue2', tie=None),                    # factory / union: blue work shirt
 'prison':        dict(suit=('f2_tr0', 'f2_tr1', 'f2_tr2'), shirt='f2_tee', tie=None),               # grey tracksuit, light tee, no tie
 'open_collar':   dict(suit=('steel0', 'steel1', 'steel2'), shirt='f2_sky2', tie=None),                # campaign look: jacket, light-blue open-collar shirt, no tie (23b Dallagnol)
}

ERA_KIND = {'black': 'lula_black', 'pres': 'lula_pres', 'white': 'lula2023', 'whitehat': 'lula2023hat'}

def actor_v2(kind, pose='idle', phase=0, facing=False, gesture=.5, era=None, clothes=None):
    """Same contract as `actor` (+ optional `era`): returns a Geometry (about 20 x 51 px, 28-px frame).

    kind 'lula' with era in black | pres | white | whitehat selects the Lula state
    (black beard 1970s-80s; 2.0.0 presidency grey 2003-2016; white beard 2017-2022; white beard + Panama hat 2023-).
    clothes=None keeps each era's default; pass a CLOTHES key ('suit_navy' | 'suit_black' | 'suit_charcoal' | 'work' | 'prison')
    or (legacy) another kind's name, e.g. clothes='lula2023', to wear its clothes.
    """
    if kind == 'lula':
        if era not in ERA_KIND: raise ValueError(f'lula needs era in {sorted(ERA_KIND)}')
        kind = ERA_KIND[era]
    if kind not in KINDS: raise ValueError(kind)
    c = dict(KINDS[kind])
    if clothes:
        src = CLOTHES[clothes] if clothes in CLOTHES else KINDS[clothes]
        c.update({k: src[k] for k in ('suit', 'shirt', 'tie')})
    dark, mid, light = c['suit']; k = c['k']
    if pose in _pose.BACK_POSES:                      # seen from behind (figures_v3_pose)
        return _pose.back_view(dict(suit=c['suit'], shirt=c['shirt'], k=k, belt='wood0'), _pose.BACK_HEAD[kind], pose, phase, facing,
                               gesture, head_fn=c['head'])
    sit = pose in _pose.SIT_POSES                      # seated (figures_v3_pose): no standing legs, lap hands
    walk = pose == 'walk'; s = math.sin(phase)
    bob = round(.6 * (1 - math.cos(phase * 2))) if walk else 0
    g = Geometry()
    def pt(x, y): return (x, y + bob)
    # legs: identical gait to worker (feet planted: no sliding)
    if sit: _pose.sit_legs(g, (dark, mid, light))
    for i in ([] if sit else [0, 1]):
        hip = (10 + i * 5, 30 + bob)
        if walk:
            u = (phase / (2 * math.pi) + i * .5) % 1
            if u < .5: dx = 15 * (.25 - u); lift = 0
            else:
                z = (u - .5) * 2; dx = 15 * (-.25 + .5 * z * z * (3 - 2 * z)); lift = 4 * math.sin(z * math.pi)
            f = (9 + i * 7 + dx, 49 - lift); knee = ((hip[0] + f[0]) * .5 + 2, 40 - lift * .5)
        else: f = (9 + i * 7, 49); knee = (10 + i * 6, 40)
        line(g, hip, knee, 2.2, mid); line(g, knee, (f[0], f[1] - 2), 1.7, mid)
        line(g, (hip[0] - 1, hip[1] + 2), (knee[0] - 1, knee[1]), .6, light if i else dark)
        line(g, (knee[0], knee[1] + 1), (f[0] - 1, f[1] - 2), .6, dark)
        poly(g, [(f[0] - 2, f[1] - 2), (f[0] + 2, f[1] - 2), (f[0] + 4, f[1]), (f[0] + 4, f[1] + 1), (f[0] - 2, f[1] + 1)], 'black')
        r(g, f[0] - 1, f[1] - 1, 3, 1, 'steel0')
    # far arm (behind torso)
    far = (6 - 3 * s, 33) if walk else (6, 33)
    if sit: far = (19, 31)
    sh = lambda x: _k(x, k)
    line(g, (sh(7), 17 + bob), (sh(5), 24 + bob), 2, dark); line(g, (sh(5), 24 + bob), (far[0], far[1] + bob), 1.2, 'skin0'); r(g, far[0] - 1, far[1] + bob, 2, 3, 'skin1')
    # torso: jacket
    T = lambda pts: [(sh(x), y + bob) for x, y in pts]
    poly(g, T([(8, 14), (14, 13), (18, 16), (19, 23), (17, 31), (8, 31), (6, 25), (6, 18)]), mid)
    poly(g, T([(8, 16), (10, 15), (10, 25), (12, 28), (9, 29), (7, 25)]), light)
    poly(g, T([(16, 16), (18, 18), (18, 26), (17, 30), (14, 29), (15, 25)]), dark)
    if c.get('stripes'):
        for x in range(8, 18, 2):
            for y in range(18, 30, 3): r(g, sh(x), y + bob + (x % 3 == 0), 1, 2, 'f2_stripe')
    r(g, sh(8), 30 + bob, 9, 1, 'wood0')
    # shirt V and tie
    poly(g, T([(10, 14), (14, 13), (17, 15), (13, 23)]), c['shirt'])
    poly(g, T([(10, 14), (12, 13), (13, 16), (12, 18)]), light); poly(g, T([(14, 13), (17, 15), (15, 18), (13, 16)]), light)
    if c['tie']:
        poly(g, T([(13, 16), (15, 16), (15, 22), (13, 25), (12, 21)]), c['tie'])
    # head
    c['head'](g, pt)
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

def bbox(g):
    xs = [x for x, _ in g.cells]; ys = [y for _, y in g.cells]
    return min(xs), min(ys), max(xs), max(ys)
