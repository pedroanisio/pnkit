"""pnkit.pixelart.ctx — the build context of an integer-grid pixel-art film (scene-render 1.1 XML, 1920x1080, 6x the
320x180 grid). Extracted from the Lula 3.0.0 film (work/art3/v3/common.py, 2026-10-07); only the imports and the
timings source changed, so the same scene modules build the same bytes (pnkit tests, test_pixelart_lula.py).

Rules this module enforces (Lula SHOTS-3.0.0.md, section 2):
  * picture content lives above logical row 146 (rows 147-179 are the caption band, the assembler's);
  * plates are reserved rectangles in slot TL (x 6-110) or TR (x 210-314), checked against signs and figures;
  * ids carry a per-scene prefix (s01_g1, s01_p2, ...) so scene modules never collide;
  * only integer-pixel motion: x/y pans stepped on the logical grid; no scale animation (coordinator ruling);
  * the same input produces the same bytes (no clocks, no random without a seed, ids by counter).
Art primitives: scene_art, story_art, chapter_art, full_art (Lula 2.0.0) and the figure modules figures_v2,
figures_v3_pose, figures_v3_cast, figures_v3_extra.

The film's timings are not read from a fixed path: call set_timings(dict or path) once (film_build's generate stage
does), then timings() and slot(nn) answer from it.
"""
import math, json, re
from pathlib import Path
from .. import sdk
from ..sdk import S

from .geometry import Geometry
from .scene_art import P, FONT, r, poly, line, ellipse, lettering, plank, crate, barrel, worker, cog
from .story_art import resize, flip, tree, cactus, chair, table, village, truck, wheel, road_sky, ridges, roadside, city, house
from .full_art import actor as old_actor            # also installs extra font glyphs ($ % + / ( ) > º —)
from .figures_v2 import actor_v2, KINDS as V2_KINDS, CLOTHES, bbox
from . import figures_v3_cast as _cast             # redrawn cast (Dilma, Temer, Cunha, Alencar, Frei Chico)
CAST_KINDS = set(_cast.KINDS)

UNIT = 6
W, H = 320, 180
ROW_LIMIT = 146            # last logical row a picture element may occupy
SOLE_LIMIT = 145           # figures' soles
FPS = 24
SLOTS = {'TL': (6, 110), 'TR': (210, 314)}
SHOT_EPS = 1e-4            # a shot group starts 0.1 ms before its first frame time, so float rounding never drops that frame

# glyphs the 3.0.0 plates need and the 2.0.0 font lacks (additions only; FONT is a shared dict)
FONT.setdefault('·', ['0', '0', '0', '1', '0', '0', '0'])
FONT.setdefault('→', ['000000', '001000', '000100', '111110', '000100', '001000', '000000'])
FONT.setdefault('≠', ['00001', '11111', '00100', '11111', '01000', '00000', '00000'])
FONT.setdefault('"', ['101', '101', '000', '000', '000', '000', '000'])
FONT.setdefault('é', FONT['E'])

# own colours (names prefixed v3_)
P.update({'v3_dawn': '#e9a470', 'v3_dusk': '#c8704a', 'v3_night': '#0f1b33', 'v3_shaft': '#f1dca0',
          'v3_sea': '#5d8ea0', 'v3_sea2': '#86b2bc', 'v3_leaf': '#3f6b45', 'v3_leaf2': '#5a8a55'})

_TIMINGS = {'data': None}


def set_timings(data):
    """The film's timings: a dict ({"scenes": [{"n", "slot_start", "slot_end", ...}]}) or a path to its JSON file."""
    if not isinstance(data, dict):
        data = json.loads(Path(data).read_text(encoding='utf-8'))
    if not isinstance(data.get('scenes'), list):
        raise ValueError('timings: expected {"scenes": [...]}')
    _TIMINGS['data'] = data
    return data


def timings():
    if _TIMINGS['data'] is None:
        raise RuntimeError('pnkit.pixelart.ctx: no timings set; call set_timings(dict or path) first')
    return _TIMINGS['data']


def slot(nn):
    for s in timings()['scenes']:
        if s['n'] == int(nn):
            return s['slot_start'], s['slot_end']
    raise KeyError(nn)


def text_width(txt):
    return lettering(txt)[1]


def rects_overlap(a, b):
    """Rectangles (x0, y0, x1, y1) with exclusive x1/y1."""
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


class PlanError(AssertionError):
    pass


def fmt(v):
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, float):
        return str(round(v, 6))
    return str(v)


def _set(el, name, v):
    """one attribute: the value as the SDK's type takes it (a number as a number, else its `fmt` text)"""
    sdk.set_exact(el, name, v, fmt)


def E(p, tag, **attrs):
    if attrs.get('start') is not None and attrs['start'] > 0:      # every window opens SHOT_EPS early: fmt() rounds to 6 decimals, which can land a start after its own frame time
        attrs['start'] = attrs['start'] - SHOT_EPS
    el = sdk.new(p, tag)
    for k, v in attrs.items():
        if v is not None:
            _set(el, k, v)
    p.add(el)
    return el


def frame_condition(i, n, rate, a=None, b=None, loop=True):
    """The `condition` string that shows frame i of an n-frame cycle (None when n == 1): the ONE place every frame-cycled group takes its condition from.
    loop: frame floor((time - a) * rate) % n; once (loop=False): min(n - 1, floor((time - a) * n / (b - a))). `a` None: the clock is the plain `time`
    of a symbol (crowd instances). A group opens SHOT_EPS before its first frame, so `time - a` can be a hair below 0 and floor() gives -1, a value that
    matches no frame (and -1 % n stays -1 in JS): the phase is clamped with Math.max(0, ...) so exactly one frame matches at any time >= a - SHOT_EPS."""
    if n <= 1:
        return None
    t = 'time' if a is None else f'(time-{a})'
    if loop:
        return f'Math.max(0,Math.floor({t}*{rate}))%{n}=={i}'
    return f'Math.max(0,Math.min({n - 1},Math.floor({t}*{n / (b - a)})))=={i}'


def check_plate_rect(rect, signs=(), label=''):
    """Pure check used by Ctx and by the tests: plate ends at row <= 146 and avoids every sign."""
    x0, y0, x1, y1 = rect
    if y1 - 1 > ROW_LIMIT:
        raise PlanError(f'plate {label} {rect} ends at row {y1 - 1} > {ROW_LIMIT}')
    for s in signs:
        if rects_overlap(rect, s['rect']):
            raise PlanError(f'plate {label} {rect} overlaps sign {s["text"]!r} {s["rect"]}')
    return True


def check_row(y_last, what=''):
    if y_last > ROW_LIMIT:
        raise PlanError(f'{what} reaches row {y_last} > {ROW_LIMIT}')


class Ctx:
    """One build. `begin_scene(nn)` sets the id prefix; shots are opened with `shot()`."""

    def __init__(self, unit=UNIT, seed=1945):
        self.unit = unit
        self.root = S.Scene(version='1.1')
        self.proj = E(self.root, 'project', width=W * unit, height=H * unit, fps=FPS, duration=1, seed=seed,
                      background=P['black'], quality='final')
        self.comp = E(self.root, 'composition')
        self.shots = []
        self.scene = None
        self._count = {}
        self._began = set()
        self.zinfo = None
        self.z = 1; self.ox = 0; self.oy = 0       # zoom factor (integer) and output offset for a closer framing
        self.cur = None
        self.scene_ends = {}
        self._plate_groups = []                # (parent, group): plates are raised to the top of their parent at finish()

    # ----------------------------------------------------------------- ids and geometry of the output
    def begin_scene(self, nn):
        nn = int(nn)
        if nn in self._began:
            raise PlanError(f'scene {nn} begun twice')
        self._began.add(nn); self.scene = nn; self._count[nn] = 0
        return nn

    def ID(self, kind='n'):
        self._count[self.scene] += 1
        return f's{self.scene:02d}_{kind}{self._count[self.scene]}'

    @property
    def ue(self):
        return self.unit * self.z

    def X(self, x):
        return round(x) * self.ue + self.ox

    def Y(self, y):
        return round(y) * self.ue + self.oy

    def group(self, p, **attrs):
        return E(p, 'group', id=self.ID('g'), **attrs)

    def G(self, p, q, x=0, y=0, **attrs):
        g = self.group(p, x=self.X(x), y=self.Y(y), **attrs)
        for c, path in q.paths(self.ue).items():
            E(g, 'shape', id=self.ID('p'), shape='path', width=W * self.ue, height=H * self.ue, fill=c, path=path)
        return g

    class _Zoom:
        def __init__(s, ctx, z, cx, cy, parent, **attrs): s.c, s.z, s.cx, s.cy, s.p, s.attrs = ctx, z, cx, cy, parent, attrs
        def __enter__(s):
            c = s.c; s.old = (c.z, c.ox, c.oy, c.zinfo); c.z = s.z; c.zinfo = (s.z, s.cx, s.cy)
            gx = 160 * c.unit - s.cx * c.ue; gy = 73 * c.unit - s.cy * c.ue
            g = c.group(s.p, x=gx, y=gy, **s.attrs)
            c.ox = c.oy = 0
            return g
        def __exit__(s, *a):
            s.c.z, s.c.ox, s.c.oy, s.c.zinfo = s.old

    def zoom(self, z, cx, cy, parent, **attrs):
        """Closer framing at an INTEGER scale: a group, placed so that logical point (cx, cy) lands at the picture centre,
        whose children are drawn at z times the grid. Replaces a push-in (coordinator ruling: no scale animation).
        Use as `with ctx.zoom(2, 160, 90, parent=shot, start=a, end=b) as zg:` and draw into zg."""
        assert z == int(z) and z >= 1
        return Ctx._Zoom(self, int(z), cx, cy, parent, **attrs)

    # ----------------------------------------------------------------- text
    def text(self, p, txt, x, y, c='ivory', **kw):
        q, w = lettering(txt, c)
        return self.G(p, q, x, y, **kw)

    def center(self, p, txt, y, c='ivory', cx=160, **kw):
        q, w = lettering(txt, c)
        assert w <= 310, (txt, w)
        return self.G(p, q, round(cx - w / 2), y, **kw)

    def title(self, p, txt, c='cream', **kw):
        """Optional on-picture title in the upper-left; no outline (the assembly adds it)."""
        assert text_width(txt) <= 306, txt
        return self.text(p, txt, 8, 7, c, **kw)

    # ----------------------------------------------------------------- animation
    def keys(self, g, prop, values):
        a = E(g, 'animate', property=prop, defaultInterpolation='hold')
        for t, v in values:
            E(a, 'key', time=t, value=v)

    def move(self, g, prop, a, b, va, vb, hz=12):
        """Stepped integer-pixel move of x or y (logical px) from time a to b."""
        n = max(1, round((b - a) * hz))
        conv = self.X if prop == 'x' else self.Y
        self.keys(g, prop, [(a + (b - a) * i / n, conv(va + (vb - va) * i / n)) for i in range(n + 1)])

    def track(self, g, prop, points, hz=12):
        """Stepped integer-pixel path through (time, logical value) points: linear between points, rounded to the logical grid."""
        conv = self.X if prop == 'x' else self.Y
        out = []
        for (t0, v0), (t1, v1) in zip(points, points[1:]):
            n = max(1, round((t1 - t0) * hz))
            for i in range(n):
                out.append((t0 + (t1 - t0) * i / n, conv(v0 + (v1 - v0) * i / n)))
        out.append((points[-1][0], conv(points[-1][1])))
        self.keys(g, prop, out)

    # ----------------------------------------------------------------- shots
    def shot(self, name, a, b, bg=None, pan=None, hz=6, py=None):
        """Open a shot group [a, b) in the composition. Returns the group. `bg` is a Geometry (may be wider than 320
        when `pan=(x0, x1)` pans it with stepped x moves)."""
        assert re.fullmatch(rf's{self.scene:02d}[a-z]\d?_[a-z0-9_]+', name), f'shot name {name!r} does not fit scene {self.scene}'
        s = self.group(self.comp, start=a, end=b - SHOT_EPS, name=name)   # frame n belongs to the shot that starts at n
        rec = dict(name=name, scene=self.scene, start=a, end=b, signs=[], plates=[], occupy=[], notes=[])
        self.shots.append(rec); self.cur = rec; rec['group'] = s
        if bg is not None:
            g = self.G(s, bg)
            if pan:
                self.move(g, 'x', a, b, pan[0], pan[1], hz)
        return s

    # ----------------------------------------------------------------- signs and plates
    def sign(self, text, rect, p=None, c='ivory', at=None):
        """Declare a sign (a text that exists in the picture). rect = (x0, y0, x1, y1) with exclusive x1, y1.
        The text must fit inside the rectangle; it is NOT drawn here when `at` is None (the set draws it);
        with at=(x, y) the text is drawn on p."""
        w = text_width(text)
        x0, y0, x1, y1 = rect
        if w > x1 - x0:
            raise PlanError(f'sign {text!r} is {w}px wide, rect {rect} holds {x1 - x0}')
        check_row(y1 - 1, f'sign {text!r}')
        for pl in self.cur['plates']:
            if rects_overlap(rect, pl['rect']):
                raise PlanError(f'sign {text!r} {rect} overlaps plate {pl["text"]!r} {pl["rect"]}')
        self.cur['signs'].append(dict(text=text, rect=list(rect)))
        if at is not None:
            self.text(p, text, at[0], at[1], c)
        return rect

    def _wrap(self, text, maxw):
        out = []
        for seg in text.split(' / '):
            cur = ''
            for wd in seg.split():
                t = (cur + ' ' + wd).strip()
                if text_width(t) <= maxw or not cur:
                    cur = t
                else:
                    out.append(cur); cur = wd
            out.append(cur)
        return out

    def _plate_layer_check(self, p, label):
        """A plate (or box label) lives on the frame-level layer: a direct child of the shot group, never inside a zoom or any other
        group (a zoom would scale and clip it, a pan would move it). finish() raises it above everything else in the shot."""
        if self.z != 1 or p is not self.cur['group']:
            raise PlanError(f'plate {label!r} in {self.cur["name"]} must be a direct child of the shot group, not inside a zoom/pan group: '
                            'call ctx.plate(...) outside the `with ctx.zoom` block and without a parent argument')

    def plate(self, text, slot_, a, b, p=None, fill='blue0', color='cream', lines=None, grows=False):
        """A "Na tela" card in slot TL or TR from the top (y=6). Window [a, b) is absolute film time; it is clipped to
        the open shot, and a plate that carries over a cut is re-issued in the next shot with the same arguments.
        Height = 8 + 13 per line. grows=True: the card's lines are revealed one by one (25e), so it is full only at the end of its
        window; recorded as "grows": true in shots.json and checked at the end of the window by check_render_plates.py. Returns the group."""
        sh = self.cur; p = p if p is not None else sh['group']
        self._plate_layer_check(p, text)
        sx0, sx1 = SLOTS[slot_]
        maxw = sx1 - sx0 - 8
        ls = self._wrap(text, maxw)
        while lines is not None and len(ls) > lines and maxw < 170:   # widen the card (noted in shots.json) to hold the plan's line count
            maxw += 2; ls = self._wrap(text, maxw)
        if lines is not None and len(ls) != lines:
            raise PlanError(f'plate {text!r} wraps to {len(ls)} lines, plan says {lines}')
        w = max(text_width(t) for t in ls) + 8
        w = max(w, sx1 - sx0)                           # the slot width, wider only if a line needs it
        h = 8 + 13 * len(ls)
        x0 = sx0 if slot_ == 'TL' else sx1 - w
        rect = (x0, 6, x0 + w, 6 + h)
        check_plate_rect(rect, sh['signs'], text)
        ca, cb = max(a, sh['start']), min(b, sh['end'])
        if cb <= ca:
            raise PlanError(f'plate {text!r} window {a}-{b} outside shot {sh["name"]}')
        q = Geometry(); r(q, 0, 0, w, h, 'wood0'); r(q, 1, 1, w - 2, h - 2, fill); r(q, 1, 1, w - 2, 1, 'wood1')
        g = self.G(p, q, x0, 6, start=ca, end=cb)
        self._plate_groups.append((p, g))
        for i, t in enumerate(ls):
            tw = text_width(t)
            self.text(g, t, (w - tw) // 2, 5 + i * 13, color)
        sh['plates'].append(dict(text=text, slot=slot_, rect=list(rect), start=ca, end=cb, full=[a, b], lines=len(ls), **({'grows': True} if grows else {})))
        return g

    def box(self, p, reserved, a=None, b=None, fill='blue0', lines=(), color='cream', grows=False):
        """Generic plate in a RESERVED rectangle (x0, y0, x1, y1): asserts it ends at row <= 146 and does not overlap a
        declared sign rectangle. Lines are centred; the rectangle is the plate."""
        x0, y0, x1, y1 = reserved
        self._plate_layer_check(p, str(lines))
        check_plate_rect(reserved, self.cur['signs'], str(lines))
        w, h = x1 - x0, y1 - y0
        assert h >= 8 + 13 * len(lines) - 1, (reserved, lines)
        q = Geometry(); r(q, 0, 0, w, h, 'wood0'); r(q, 1, 1, w - 2, h - 2, fill)
        g = self.G(p, q, x0, y0, start=a, end=b)
        self._plate_groups.append((p, g))
        for i, t in enumerate(lines):
            tw = text_width(t); assert tw <= w - 6, (t, tw, w)
            self.text(g, t, (w - tw) // 2, 5 + i * 13, color)
        self.cur['plates'].append(dict(text=' / '.join(lines), slot='box', rect=list(reserved),
                                       start=a if a is not None else self.cur['start'], end=b if b is not None else self.cur['end'],
                                       **({'grows': True} if grows else {})))
        return g

    # ----------------------------------------------------------------- figures
    def sprite_frame(self, kind, pose, phase, flip_, gesture, era=None, clothes=None):
        if kind == 'donalindu':   # the kept 2.0.0 mother sprite (green dress, tan apron): Dona Lindu, scenes 01-02 and every Dona Lindu shot
            return old_actor('mother', pose, phase, flip_, gesture)
        if kind == 'lula' or kind in V2_KINDS:
            return actor_v2(kind, pose, phase, flip_, gesture, era=era, clothes=clothes)
        if kind in CAST_KINDS:
            return _cast.actor_v3(kind, pose, phase, flip_, gesture, era=era, clothes=clothes)
        return old_actor(kind, pose, phase, flip_, gesture)

    def actor(self, p, kind, pose, x, y, a, b, flip=False, n=8, rate=8, loop=True, gesture=lambda u: .5, endx=None,
              endy=None, scale=1, crop=None, era=None, clothes=None, beardless=False, hz=12, solid=True, remap=None):
        """A figure as n frames selected by time. New figures (figures_v2 kinds, 'lula' with era=) and the redrawn cast use
        their own builders; the 2.0.0 sprites remain for kept kinds (mother, child, back, clerk, chico...).
        Soles must be at row <= 145; for walks the cycle rate should match the travel (see walk_rate)."""
        g = self.group(p, x=self.X(x), y=self.Y(y), start=a, end=b)
        bottoms, boxes = [], []
        for i in range(n):
            u = i / (n - 1) if n > 1 else 0
            q = self.sprite_frame(kind, pose, math.tau * i / n, flip, gesture(u), era, clothes)
            if beardless:
                q = beardless_(q)
            if remap:
                q.cells = {xy: remap.get(c, c) for xy, c in q.cells.items()}
            if scale != 1:
                q = resize(q, scale)
            if crop is not None:
                q.cells = {xy: c for xy, c in q.cells.items() if xy[1] < crop}
            xs = [c[0] for c in q.cells]; ys = [c[1] for c in q.cells]
            bottoms.append(max(ys)); boxes.append((min(xs), min(ys), max(xs) + 1, max(ys) + 1))
            cond = frame_condition(i, n, rate, a, b, loop)
            self.G(g, q, condition=cond)
        if endx is not None:
            self.move(g, 'x', a, b, x, endx, hz)
        if endy is not None:
            self.move(g, 'y', a, b, y, endy, hz)
        bot = max(bottoms)
        for yy in (y, endy if endy is not None else y):
            if self.z == 1 and yy + bot > SOLE_LIMIT:
                raise PlanError(f'{kind} soles at row {yy + bot} > {SOLE_LIMIT} in {self.cur["name"]}')
        if solid:
            x0 = min(x, endx if endx is not None else x) + min(b_[0] for b_ in boxes)
            x1 = max(x, endx if endx is not None else x) + max(b_[2] for b_ in boxes)
            y0, y1 = y + min(b_[1] for b_ in boxes), y + bot + 1
            if self.zinfo:                                     # figures in a zoomed framing: register where they land in the frame
                z, cx, cy = self.zinfo
                x0, x1 = 160 + (x0 - cx) * z, 160 + (x1 - cx) * z; y0, y1 = 73 + (y0 - cy) * z, 73 + (y1 - cy) * z
            self.cur['occupy'].append(dict(kind=kind, rect=[x0, y0, x1, y1], start=a, end=b))
        return g

    def walk(self, p, kind, x, y, a, b, endx, flip=None, n=8, **kw):
        """Walking figure whose cycle rate matches the ground speed (one cycle moves a figure 15 logical px)."""
        v = abs(endx - x) / (b - a)
        rate = v * n / 15.0
        assert 1.0 <= rate <= 20, f'walk rate {rate:.1f} fps out of range for {kind} ({v:.1f} px/s)'
        return self.actor(p, kind, 'walk', x, y, a, b, flip=(endx < x) if flip is None else flip, n=n, rate=round(rate, 3), endx=endx, **kw)

    def talk(self, p, kind, x, y, a, b, flip=False, **kw):
        return self.actor(p, kind, 'talk', x, y, a, b, flip=flip, n=16, loop=False,
                          gesture=lambda u: .25 + .55 * math.sin(math.pi * u), **kw)

    # ----------------------------------------------------------------- effects with rules
    STEAM_FRAMES = 4                 # frames per cycle; the column of puffs moves up 1 px per frame, a cycle moves it one puff spacing (4 px)
    STEAM_SPACING = 4                # px between stacked puffs
    STEAM_DRIFT = (0, 0, 1, 1, 1, 0, 0, -1, -1, 0, 1, 1)    # x drift (px) by height above the rim: a slow S-curve that the puffs climb along
    STEAM_SIZE = ((3, 2), (4, 2), (5, 3), (5, 3), (6, 3), (6, 4), (7, 4), (7, 4), (8, 4), (8, 4), (7, 3), (6, 3))   # (w, h) of a puff by height: it swells as it rises

    @staticmethod
    def steam_frame(k):
        """Frame k (0..3) of the steam column as a Geometry in rim-relative coordinates (x 0 = pot centre, y 0 = rim, up is negative). Three soft puffs sit
        at heights H = 4 L + k (L = 0, 1, 2; H = 0..11 px above the rim), so the column climbs 1 px per frame and a full cycle (4 frames) lands on the same
        picture 4 px higher, with the next puff born at the rim. A puff is drawn by its height (`STEAM_SIZE`, `STEAM_DRIFT`): a rounded blob of the palette
        grey `steel2` with a lighter core `f2_white`, swelling as it rises and thinning to a faint dithered wisp (grey only) from H = 10. The column spans
        10-14 px above the rim. Integer pixels only."""
        q = Geometry()
        for L in range(3):
            H = 4 * L + k
            w, h = Ctx.STEAM_SIZE[H]; x = -(w // 2) + Ctx.STEAM_DRIFT[H]; y = -H - h
            if H >= 10:
                for yy in range(h):
                    for xx in range(w):
                        if (xx + yy) % 2 == 0 and not (yy in (0, h - 1) and xx in (0, w - 1)):
                            r(q, x + xx, y + yy, 1, 1, 'steel2')
                continue
            r(q, x + 1, y, w - 2, 1, 'steel2'); r(q, x, y + 1, w, h - 2, 'steel2'); r(q, x + 1, y + h - 1, w - 2, 1, 'steel2')
            if w >= 5 and h >= 3:
                r(q, x + 2, y + 1, w - 4, h - 2, 'f2_white')                                            # the lighter core
            else:
                r(q, x + 1, y, w - 2, 1, 'f2_white')
        return q

    def steam(self, p, x, y, a, b, life=1.4, every=.5):
        """Steam rising from a pot rim at (x, y): a column of 3 soft puffs, frame-cycled (`STEAM_FRAMES` = 4 frames of `every / 4` s each, so one cycle is `every`
        seconds and a puff climbs 8 px/s at the default), 10-14 px high, drifting 1 px either side, in palette greys with a lighter core (see `steam_frame`). Every
        frame is a short-lived group at (x, y). `life` is kept for old callers and unused. Visible from a to b."""
        fd = max(1 / 24.0, every / Ctx.STEAM_FRAMES); t = a; k = 0
        frames = [Ctx.steam_frame(i) for i in range(Ctx.STEAM_FRAMES)]
        while t < b - 1e-6:
            e = min(t + fd, b)
            self.G(p, frames[k % Ctx.STEAM_FRAMES], x, y, start=t, end=e)
            t += fd; k += 1

    def dust(self, p, shaft, a, b, seed=1, count=6):
        """Dust specks only inside `shaft`, a list of (x0, y0, x1, y1) boxes that tile the light shaft."""
        import random
        rng = random.Random(seed)
        for k in range(count):
            bx = rng.choice(shaft)
            x0 = rng.randrange(bx[0] + 1, bx[2] - 2); y0 = rng.randrange(bx[1] + 1, bx[3] - 4)
            dx, dy = rng.choice([-1, 1]), 2
            x1, y1 = x0 + dx, y0 + dy
            for (px, py_) in ((x0, y0), (x1, y1)):
                if not any(s[0] <= px < s[2] and s[1] <= py_ < s[3] for s in shaft):
                    x1, y1 = x0, y0
            q = Geometry(); r(q, 0, 0, 1, 1, 'v3_shaft')
            per = 2.0; t = a + rng.random() * per
            ts = a
            while ts < b:
                te = min(ts + per, b)
                g = self.G(p, q, x0, y0, start=ts, end=te)
                self.move(g, 'y', ts, te, y0, y1, 2); self.move(g, 'x', ts, te, x0, x1, 2)
                ts = te

    def tint(self, p, color, opacity, a=None, b=None, rect=(0, 0, W, H)):
        q = Geometry(); r(q, rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1], color)
        return self.G(p, q, 0, 0, start=a, end=b, opacity=opacity)

    # ----------------------------------------------------------------- finishing and checks
    def finish(self):
        end = max(s['end'] for s in self.shots)
        _set(self.proj, 'duration', end)
        for par, g in self._plate_groups:       # z-order: a plate is always drawn last in its shot (a set or zoom group added later must not cover it)
            par.remove(g); par.add(g)
        self.check()
        return self

    def check(self):
        """Plate windows against signs and figures; a plate whose window runs past its shot must be re-issued in the next one."""
        for sh in self.shots:
            for pl in sh['plates']:
                a, b = pl.get('full', [pl['start'], pl['end']])
                for o in self.shots:
                    if o['scene'] == sh['scene'] and o['start'] < b and a < o['end']:
                        for sg in o['signs']:
                            if rects_overlap(pl['rect'], sg['rect']):
                                raise PlanError(f'plate {pl["text"]!r} ({sh["name"]}) overlaps sign {sg["text"]!r} ({o["name"]})')
                        if o is not sh and o['start'] >= sh['end'] - 1e-9 and not any(q['text'] == pl['text'] for q in o['plates']):
                            raise PlanError(f'plate {pl["text"]!r} runs to {b} but is not re-issued in {o["name"]}')
                for oc in sh['occupy']:
                    if oc['start'] < pl['end'] and pl['start'] < oc['end'] and rects_overlap(pl['rect'], oc['rect']):
                        raise PlanError(f'plate {pl["text"]!r} overlaps a {oc["kind"]} figure in {sh["name"]}')

    def check_scene(self, **kw):
        """`sr_core.scene.check` findings of the built document (level 1; schema=True adds level 2)"""
        return S.check(self.root, **kw)

    def tostring(self):
        sdk.indent(self.root, ' ')
        return S.to_bytes(self.root)

    def shots_json(self):
        out = []
        for s in self.shots:
            out.append(dict(name=s['name'], scene=s['scene'], start=s['start'], end=s['end'],
                            signs=s['signs'], plates=[{k: v for k, v in pl.items()} for pl in s['plates']],
                            figures=s['occupy'], notes=s['notes']))
        return out


def beardless_(q):
    """Remove the 2.0.0 sprite's moustache/beard marks (brown pixels on the mouth rows) for beardless youths."""
    for (x, y), c in list(q.cells.items()):
        if c in (P['brown'], P['hair']) and 9 <= y <= 14 and 14 <= x <= 19:
            q.cells[x, y] = P['skin1']
    return q


def sky_gradient(g, top, bottom, y0, y1, bands=6):
    """Flat horizontal bands (no dithering) from colour `top` to `bottom` between rows y0 and y1."""
    def rgb(h): h = P.get(h, h); return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    t, b = rgb(top), rgb(bottom)
    for i in range(bands):
        u = i / (bands - 1)
        c = '#%02x%02x%02x' % tuple(round(t[k] + (b[k] - t[k]) * u) for k in range(3))
        r(g, 0, y0 + (y1 - y0) * i // bands, 2000, (y1 - y0) * (i + 1) // bands - (y1 - y0) * i // bands, c)


# =====================================================================================================================
# CROWDS (appended, additive: nothing above this line was changed). ctx.crowd(...) places ONE sprite geometry (or a few
# variants) many times through scene-render <symbol>/<instance> (reuse supported by schema 1.1, see README "Crowds").
# =====================================================================================================================
def crowd_offsets(rect, count, seed=1, min_gap=0):
    """Deterministic jittered-grid points inside rect=(x0, y0, x1, y1) (x1/y1 inclusive upper bound of the sampling box).
    One point per grid cell, cells chosen by Random(seed), ints; sorted back to front (y, then x). min_gap drops the
    cell jitter margin so neighbours keep at least that many px apart horizontally inside a row where possible."""
    import random
    x0, y0, x1, y1 = rect
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    rows = max(1, round(math.sqrt(count * h / w)))
    cols = -(-count // rows)
    while rows * cols < count:
        cols += 1
    rng = random.Random(seed)
    cells = [(i, j) for j in range(rows) for i in range(cols)]
    rng.shuffle(cells)
    cw, ch = w / cols, h / rows
    pts = []
    for (i, j) in cells[:count]:
        jx = rng.uniform(-.5, .5) * max(0.0, cw - min_gap); jy = rng.uniform(-.5, .5) * ch * .8
        pts.append((round(x0 + (i + .5) * cw + jx), round(y0 + (j + .5) * ch + jy)))
    return sorted(pts, key=lambda t: (t[1], t[0]))


def _crowd_variant(spec, d):
    out = dict(d)
    if isinstance(spec, str):
        out['kind'] = spec
    else:
        out.update(spec)
    return out


def _crowd_flag_cells(q, frame, color, pole_x, base_y, top_y):
    """Pole (wood) with a 7x4 cloth whose trailing edge shifts by frame: three flag frames."""
    for yy in range(top_y, base_y):
        q.cells[pole_x, yy] = P['wood1']
    c = P.get(color, color)
    for k in range(7):
        sag = (0, 1, 1, 0)[(k + frame) % 4] if k > 1 else 0
        for yy in range(4):
            q.cells[pole_x + 1 + k, top_y + yy + sag] = c
    return q


def _crowd_sprite(self, v, i, n, drift_dir):
    """One frame i of n for variant dict v (kind, pose, flip, remap, clothes, era, scale, prop, color)."""
    prop = v.get('prop')
    pose = v.get('pose', 'idle')
    gest = .5
    if prop == 'wave':
        pose = 'talk'; gest = (.95, .35)[i % 2]
    elif prop == 'clap':
        pose = 'talk'; gest = (.05, .30)[i % 2]
    q = self.sprite_frame(v['kind'], pose, math.tau * i / n, v.get('flip', False), gest, v.get('era'), v.get('clothes'))
    if v.get('remap'):
        rm = dict(v['remap']); q.cells = {xy: rm.get(c, c) for xy, c in q.cells.items()}
    if v.get('scale', 1) != 1:
        q = resize(q, v['scale'])
    if prop == 'flag':
        xs = [c[0] for c in q.cells]; ys = [c[1] for c in q.cells]
        fx = (min(xs) + 1) if v.get('flip', False) else (max(xs) - 1)
        _crowd_flag_cells(q, i, v.get('color', 'red1'), fx, max(ys) - 22, min(ys) - 12)
    if pose == 'idle' and v.get('bob', True) and (i % n) >= n // 2 and n > 1:         # breathing hop: whole body one row up
        q.cells = {(x, y - 1): c for (x, y), c in q.cells.items()}
    return q


def _crowd_symbol(self, v, n, rate):
    """Build (or fetch) the <symbol> for variant v. Returns dict(id, ox, oy, w, h, bottom). Cached per scene and unit."""
    key = (self.scene, self.ue, n, rate, tuple(sorted((k, str(val)) for k, val in v.items())))
    cache = self.__dict__.setdefault('_crowd_syms', {})
    if key in cache:
        return cache[key]
    frames = [_crowd_sprite(self, v, i, n, 0) for i in range(n)]
    xs = [c[0] for q in frames for c in q.cells]; ys = [c[1] for q in frames for c in q.cells]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs) + 1, max(ys) + 1
    bw, bh = x1 - x0, y1 - y0
    syms = self.__dict__.get('_crowd_symbols_el')
    if syms is None or syms.owner is not self.root:
        syms = sdk.new(S.Scene, 'symbols'); self.root.add(syms)               # the content model puts it before <composition>
        self._crowd_symbols_el = syms
    sid = self.ID('c')
    sym = E(syms, 'symbol', id=sid, width=bw * self.ue, height=bh * self.ue)
    ue = self.ue
    for i, q in enumerate(frames):
        q.cells = {(x - x0, y - y0): c for (x, y), c in q.cells.items()}
        cond = frame_condition(i, n, rate)
        g = E(sym, 'group', id=self.ID('g'), x=0, y=0, condition=cond)
        for c, path in q.paths(ue).items():
            E(g, 'shape', id=self.ID('p'), shape='path', width=bw * ue, height=bh * ue, fill=c, path=path)
    info = dict(id=sid, ox=x0, oy=y0, w=bw, h=bh, bottom=y1 - 1, n=n, rate=rate)
    cache[key] = info
    return info


def _crowd(self, p, kinds, offsets=None, a=None, b=None, *, rect=None, count=None, seed=1, pose='idle', flip=False,
           n=4, rate=3, phase='spread', props=(), drift=None, pan=None, hz=6, behind_plate=False, key=(),
           anchor='feet', dots=None, size=(2, 3), speeds=(1,), remap=None, tints=None, era=None, clothes=None, scale=1,
           min_gap=0):
    """ONE sprite geometry (or a few variants cycled by index) placed N times as <instance> of a <symbol>; every symbol is a
    frame-cycled actor (n frames, `rate` fps). Parent `p` is a shot group; a and b are absolute film seconds.

    kinds      'back' | {'kind': 'back', 'pose': 'idle', 'remap': {...}, 'flip': True, ...} | list of those (cycled by index)
    offsets    list of (x, y) points, OR None with rect=(x0, y0, x1, y1), count=N, seed=S (crowd_offsets, deterministic)
    anchor     'feet' (default): (x, y) is the figure's feet centre (x) and sole row (y); 'origin': actor-style sprite origin
    flip       False | True | 'alt' (alternate by index) | 'rng' (by seed)
    phase      'spread' (per-figure frame offset by seed, so they do not bob in sync) | 'sync' | list of frame offsets (cycled)
    props      plain data, first matching entry wins: [{'prop': 'flag'|'wave'|'clap', 'every': 4, 'offset': 1, 'color': 'red1'}]
    tints      list of {hex: hex} remaps cycled by index (shirt colours)
    drift      None | (dx, dy) | list per index | callable(i, (x, y)) -> (dx, dy): stepped move from a to b (walkers: 'walk' pose
               with a cycle rate matched to the speed, quantised to 0.5 fps, so there is a handful of symbols)
    pan        (x0, x1): the whole crowd moves with the shot's pan (stepped, hz)
    dots       list of colours: 'dots' mode, no sprites: marks of `size` (default 2x3 px); marks with the same drift share one
               group (`speeds` = multipliers picked by seed give a few speeds)
    behind_plate  True: the crowd is background, a plate may cover it. Figures whose index is in `key` stay registered.
    Returns the crowd group. Statistics of every call are in ctx.crowds."""
    import random
    rng = random.Random(seed)
    if a is None or b is None:
        raise PlanError('crowd needs a and b')
    if offsets is None:
        if rect is None or count is None:
            raise PlanError('crowd needs offsets or rect+count')
        offsets = crowd_offsets(rect, count, seed, min_gap)
    offsets = [tuple(o) for o in offsets]
    N = len(offsets)
    for col_ in (dots or ()):                                                   # an unknown colour name would emit an invalid fill
        if col_ not in P and not (isinstance(col_, str) and col_.startswith('#')):
            raise PlanError(f'crowd dots colour {col_!r} is not a palette name or #hex')
    if scale != 1 and (not isinstance(scale, int) or scale < 1):
        raise PlanError(f'crowd scale={scale!r}: geometry is resized onto the cell grid, only integer scale >= 1 keeps whole pixels')
    grp = self.group(p, x=self.X(0) if pan is None else self.X(pan[0]), y=self.Y(0), start=a, end=b)
    if pan is not None:
        self.move(grp, 'x', a, b, pan[0], pan[1], hz)
    px0, px1 = (0, 0) if pan is None else (min(pan), max(pan))

    def drift_of(i, o):
        if drift is None:
            return (0, 0)
        d = drift(i, o) if callable(drift) else (drift[i] if isinstance(drift[0], (tuple, list)) else drift)
        return (d[0], d[1])

    log = dict(scene=self.scene, shot=self.cur['name'], mode='dots' if dots else 'figures', count=N, symbols=0, instances=0)
    sym_before = len(self.__dict__.get('_crowd_syms', {}))

    def register(rect_, kind, i):
        if self.z != 1 and self.zinfo:
            z, cx, cy = self.zinfo
            rect_ = [160 + (rect_[0] - cx) * z, 73 + (rect_[1] - cy) * z, 160 + (rect_[2] - cx) * z, 73 + (rect_[3] - cy) * z]
        if behind_plate and i not in key:
            return
        self.cur['occupy'].append(dict(kind=kind, rect=list(rect_), start=a, end=b))

    if dots:                                                                    # ---------------- far crowd: marks
        w_, h_ = size
        buckets = {}
        for i, (fx, fy) in enumerate(offsets):
            dx, dy = drift_of(i, (fx, fy))
            s = speeds[rng.randrange(len(speeds))] if len(speeds) > 1 else speeds[0]
            dx, dy = round(dx * s), round(dy * s)
            col = dots[rng.randrange(len(dots))]
            ox, oy = (fx - w_ // 2, fy - h_ + 1) if anchor == 'feet' else (fx, fy)
            for yy in (oy, oy + dy):
                if self.z == 1 and yy + h_ - 1 > SOLE_LIMIT:
                    raise PlanError(f'crowd dot at row {yy + h_ - 1} > {SOLE_LIMIT} in {self.cur["name"]}')
            buckets.setdefault((dx, dy), []).append((ox, oy, col))
            register([min(ox, ox + dx) + px0, min(oy, oy + dy), max(ox, ox + dx) + w_ + px1, max(oy, oy + dy) + h_], 'dot', i)
        for (dx, dy), items in sorted(buckets.items()):
            q = Geometry()
            for ox, oy, col in items:
                r(q, ox, oy, w_, h_, col)
            g = self.G(grp, q, 0, 0)
            if dx:
                self.move(g, 'x', a, b, 0, dx, hz)
            if dy:
                self.move(g, 'y', a, b, 0, dy, hz)
            log['instances'] += len(items)
    else:                                                                       # ---------------- figures
        variants = kinds if isinstance(kinds, (list, tuple)) else [kinds]
        base = dict(pose=pose, flip=flip, era=era, clothes=clothes, scale=scale, remap=remap)
        order = []
        for i, o in enumerate(offsets):
            v = _crowd_variant(variants[i % len(variants)], base)
            fl = v.get('flip', False)
            d = drift_of(i, o)
            if fl == 'alt':
                fl = bool(i % 2)
            elif fl == 'rng':
                fl = bool(rng.randrange(2))
            if d[0] and v.get('pose') == 'walk' and 'flip_fixed' not in v:
                fl = d[0] < 0
            v['flip'] = bool(fl)
            if tints and not v.get('remap'):
                v['remap'] = tints[i % len(tints)]
            for pr in props:
                ev = pr.get('every', 1)
                if i % ev == pr.get('offset', 0) % ev:
                    v['prop'] = pr['prop']
                    if 'color' in pr:
                        v['color'] = pr['color']
                    break
            nn, rt = n, rate
            if d[0] or d[1]:
                if v.get('pose') == 'walk':
                    sp = math.hypot(*d) / (b - a)
                    nn = 8; rt = max(1.0, round(sp * nn / 15.0 * 2) / 2)
            if v.get('pose') == 'walk' and not (d[0] or d[1]):
                v['pose'] = 'idle'
            sym = _crowd_symbol(self, v, nn, rt)
            if phase == 'sync':
                k = 0
            elif phase == 'spread':
                k = rng.randrange(nn)
            else:
                k = phase[i % len(phase)] % nn
            if anchor == 'feet':
                ox, oy = o[0] - (sym['ox'] + sym['w'] // 2), o[1] - sym['bottom']
            else:
                ox, oy = o[0], o[1]
            order.append((oy + sym['bottom'], i, ox, oy, sym, k, d, rt, v))
        order.sort(key=lambda t: (t[0], t[1]))                                  # back to front: lower soles drawn later
        for (sole, i, ox, oy, sym, k, d, rt, v) in order:
            for yy in (oy, oy + d[1]):
                if self.z == 1 and yy + sym['bottom'] > SOLE_LIMIT:
                    raise PlanError(f'crowd figure {v["kind"]} soles at row {yy + sym["bottom"]} > {SOLE_LIMIT} in {self.cur["name"]}')
            # The symbol clock is (t - start) + clipIn, and a plain `time` in the symbol's frame conditions is that clock. An instance without its own `start`
            # has start 0, i.e. an ABSOLUTE clock: the frame shown at the shot's first frame was floor(a * rate + k) % n (a pop whenever a * rate is
            # not an integer, and k / rate rounded to 6 decimals could land just under the frame boundary). Starting the instance at the shot start
            # (E() opens it SHOT_EPS early: a margin of SHOT_EPS * rate of a frame, never a frame early) makes the first frame show exactly frame k of the cycle.
            # At a == 0 E() adds no offset, so the same margin goes into clipIn.
            ins = E(grp, 'instance', id=self.ID('i'), symbol=sym['id'], x=self.X(ox + sym['ox']), y=self.Y(oy + sym['oy']),
                    start=a, clipIn=(round(k / rt + (SHOT_EPS if a <= 0 else 0), 6) if k else None))
            if d[0]:
                self.move(ins, 'x', a, b, ox + sym['ox'], ox + sym['ox'] + d[0], hz)
            if d[1]:
                self.move(ins, 'y', a, b, oy + sym['oy'], oy + sym['oy'] + d[1], hz)
            register([min(ox, ox + d[0]) + sym['ox'] + px0, oy + sym['oy'] + min(0, d[1]),
                      max(ox, ox + d[0]) + sym['ox'] + sym['w'] + px1, oy + sym['bottom'] + 1 + max(0, d[1])], v['kind'], i)
            log['instances'] += 1
    log['symbols'] = len(self.__dict__.get('_crowd_syms', {})) - sym_before
    self.__dict__.setdefault('crowds', []).append(log)
    return grp


Ctx.crowd = _crowd


# the multiplication sign for data plates ("61 × 20"); the accents (acute, tilde, circumflex, grave, cedilla) already come from
# lettering()'s NFD handling, so É Á Í Ó Ú Ê Ã Õ Ô À Ç Â need no glyph of their own
FONT.setdefault('×', ['00000', '10001', '01010', '00100', '01010', '10001', '00000'])


# ---------------------------------------------------------------------------------------------------------------------
# Extra cast (figures_v3_extra.py, actor_v3x): routed ahead of the older builders for every kind the module declares in
# its KINDS (judge a-e, guard, officer, father, mother, citizen, woman, ...). Imported lazily (it adds colours to P when it
# loads); kinds it does not declare keep their old builders. In the Lula tree a broken module fell back silently; in the
# library it is shipped with the package, so an import error is raised.
# ---------------------------------------------------------------------------------------------------------------------
_V3X = {'mod': None, 'kinds': frozenset(), 'tried': False}


def _v3x_load():
    if _V3X['mod'] is None and not _V3X['tried']:
        _V3X['tried'] = True
        import importlib
        m = importlib.import_module('.figures_v3_extra', __package__)
        ks = getattr(m, 'KINDS', None)
        _V3X['kinds'] = frozenset(ks) if ks is not None else frozenset()
        _V3X['mod'] = m if callable(getattr(m, 'actor_v3x', None)) else None
    return _V3X['mod'], _V3X['kinds']


_sprite_frame_before_v3x = Ctx.sprite_frame


def _sprite_frame_v3x(self, kind, pose, phase, flip_, gesture, era=None, clothes=None):
    m, kinds = _v3x_load()
    if m is not None and kind in kinds:
        return m.actor_v3x(kind, pose, phase, flip_, gesture, era=era, clothes=clothes)
    return _sprite_frame_before_v3x(self, kind, pose, phase, flip_, gesture, era=era, clothes=clothes)


Ctx.sprite_frame = _sprite_frame_v3x


# ---------------------------------------------------------------------------------------------------------------------
# Idle breathing (coordinator 2026-10-06): every idle sprite gets a real second frame. When cos(phase) < -0.5 the cells above
# the hip line move up 1 px (the row just above the hip is kept as well, so torso and legs stay joined: the upper body is 1 px
# taller). Legs, feet and soles do not move; phase 0 is exactly the unmodified sprite. `hip` is row 30 for adults and scales
# with the sole row for the scaled kinds (child, teen, girl). Poses 'sit' and 'back' (see figures_v3_pose) use the same rule.
# ---------------------------------------------------------------------------------------------------------------------
BREATH_POSES = ('idle', 'sit', 'back', 'backsit', 'backhands')


def breathe(q, hip):
    """Return q with the cells at rows < hip raised by 1 px (row hip-1 kept too). New Geometry; q is not modified."""
    out = Geometry()
    for (x, y), c in q.cells.items():
        if y >= hip:
            out.cells[x, y] = c
        else:
            out.cells[x, y - 1] = c
            if y == hip - 1:
                out.cells[x, y] = c
    return out


_sprite_frame_before_breath = Ctx.sprite_frame


def _sprite_frame_breath(self, kind, pose, phase, flip_, gesture, era=None, clothes=None):
    q = _sprite_frame_before_breath(self, kind, pose, phase, flip_, gesture, era=era, clothes=clothes)
    if pose in BREATH_POSES and math.cos(phase) < -0.5 and q.cells:
        top = max(y for _, y in q.cells)
        hip = 30 if pose != 'idle' else max(1, round(30 * top / 49))
        q = breathe(q, hip)
    return q


Ctx.sprite_frame = _sprite_frame_breath


# ---------------------------------------------------------------------------------------------------------------------
# Named characters are never resampled below 1 (coordinator 2026-10-06): a cell-grid resample drops cells, so the same person would
# look different from shot to shot. Generic figures (mother, father, girl, teen, citizen, woman, judge, guard, officer, nurse,
# doctor, back, child, clerk, chico, ...) may be resampled; the builder checks the frame.
# ---------------------------------------------------------------------------------------------------------------------
NAMED_KINDS = frozenset({'lula'}) | frozenset(V2_KINDS) | frozenset(CAST_KINDS)
_actor_before_named = Ctx.actor


def _actor_named_guard(self, p, kind, pose, x, y, a, b, *args, **kw):
    sc = kw.get('scale', 1)
    if kind in NAMED_KINDS and sc < 1:
        raise PlanError(f'{kind} is a named character: scale {sc} < 1 resamples the cell grid and changes the face; '
                        f'use placement, overlap or a native child/teen kind')
    return _actor_before_named(self, p, kind, pose, x, y, a, b, *args, **kw)


Ctx.actor = _actor_named_guard


# ---------------------------------------------------------------------------------------------------------------------
# Poses 'sit', 'sittalk', 'back', 'backwalk', 'backhands', 'backturn', 'backsit' (figures_v3_pose.py): the named builders (figures_v2,
# figures_v3_cast, figures_v3_extra) draw them themselves; the kept 2.0.0 sprites are handled by figures_v3_pose.old_pose.
# `ctx.sit_talk`, `ctx.walk_back` are the helpers. Appended so every earlier routing stays as it was.
# ---------------------------------------------------------------------------------------------------------------------
from . import figures_v3_pose as _pose
_sprite_frame_before_pose = Ctx.sprite_frame


def _sprite_frame_pose(self, kind, pose, phase, flip_, gesture, era=None, clothes=None):
    if pose in _pose.NEW_POSES:
        m, kinds = _v3x_load()
        named = kind == 'lula' or kind in V2_KINDS or kind in CAST_KINDS or (m is not None and kind in kinds)
        if not named:
            if kind not in _pose.OLD_KINDS:
                raise ValueError(f'pose {pose!r} is not drawn for kind {kind!r}')
            return _pose.old_pose(kind, pose, phase, flip_, gesture, old_actor, resize)
    return _sprite_frame_before_pose(self, kind, pose, phase, flip_, gesture, era=era, clothes=clothes)


Ctx.sprite_frame = _sprite_frame_pose


def _sit_talk(self, p, kind, x, y, a, b, flip=False, **kw):
    """Seated figure that speaks: pose 'sittalk' (same gesture contract as ctx.talk). The seat line is at y + 34."""
    return self.actor(p, kind, 'sittalk', x, y, a, b, flip=flip, n=16, loop=False, gesture=lambda u: .25 + .55 * math.sin(math.pi * u), **kw)


def _walk_back(self, p, kind, x, y, a, b, endx, endy=None, flip=None, n=8, **kw):
    """Figure walking away (pose 'backwalk'); one cycle covers 15 px of ground travel, like ctx.walk. endy is optional depth travel."""
    dx = endx - x; dy = 0 if endy is None else endy - y
    v = math.hypot(dx, dy) / (b - a)
    rate = max(1.0, v * n / 15.0)
    assert rate <= 20, f'walk rate {rate:.1f} fps out of range for {kind}'
    return self.actor(p, kind, 'backwalk', x, y, a, b, flip=(endx < x) if flip is None else flip, n=n, rate=round(rate, 3), endx=endx, endy=endy, **kw)


Ctx.sit_talk = _sit_talk
Ctx.walk_back = _walk_back


# ---------------------------------------------------------------------------------------------------------------------
# Glyphs added 2026-10-06 (match the 7-row, 1-px-stroke style of FONT): en dash, semicolon, and the not-equal sign.
# lettering() decomposes every character with NFD and draws the base character, so U+2260 became '=' plus an ignored combining
# slash (an '=' that said the opposite). The wrapper below maps U+2260 to a private-use code point that has its own glyph; it is
# bound in this module and in scene_art, so ctx.plate / ctx.text / ctx.sign texts and `from common import lettering` all get it.
# ---------------------------------------------------------------------------------------------------------------------
from . import scene_art as _scene_art
FONT.setdefault('–', ['0000', '0000', '0000', '1111', '0000', '0000', '0000'])             # en dash: 4 wide (hyphen 3, em dash 5)
FONT.setdefault(';', ['00', '01', '01', '00', '01', '01', '10'])                           # dots of ':' plus the tail of ','
FONT[''] = ['00001', '00010', '11111', '00100', '11111', '01000', '10000']          # not equal: two bars, one slash
_lettering_orig = _scene_art.lettering


def lettering(text, color='ivory'):
    return _lettering_orig(text.replace('≠', ''), color)


_scene_art.lettering = lettering
