"""pnkit.camera — a 2D camera group for one act, clamped to safe rectangles and verified (guide §14, Camera).

A Cam is a list of framing cues (when, cx, cy, zoom[, "hold"]) and safe rectangles (when, (x0, y0, x1, y1)): what
must stay in frame from that time on, in world coordinates. Every cue, and the drift after it, is clamped so the
safe rectangle in force sits inside the frame's usable area (MX, MY px from the edges). Moves are sine-in-out,
lead their cue by LEAD s (widening moves are quicker, narrowing moves wait until the old content has gone), and a
slow drift follows each cue so no shot holds still unless the cue says "hold".

`when` is a number (film seconds), a beat reference, or (beat reference, offset). References go through the
`resolve` callable the project passes (e.g. its timeline's beat-start function); pnkit knows nothing of timelines.

Content placed between cam.open() and Cam.CLOSE lives in world coordinates. verify() samples the camera and
returns every breach; a build should fail (or at least report) when it is not empty.
"""
import math
from . import sdk
from .sdk import S
from .xml import keys

__all__ = ["Cam"]


class Cam:
    MOVE = (1.8, 3.6)      # shortest and longest move between cues, s
    LEAD = 1.2             # a move starts this long before its cue
    MX, MY = 150, 84       # the safe rect is kept this far inside the frame (the kit's title-safe is 5 %: 96 x 54)
    INSET = 150            # the default safe rect: the frame inset by this much on every side
    CLOSE = "</group>"

    def __init__(self, doc, name, cues, start, end, safe=None, drift=0.022, resolve=None):
        """doc: the pnkit Doc (frame size, ids). name: used in the group id (cam2d-<name>) and in verify() reports.
        start, end: the act's window (numbers or references). safe: [(when, rect)], default the frame inset by
        INSET from start. drift: the zoom added by the drift after each cue."""
        self.doc, self.name, self.resolve = doc, name, resolve
        self.W, self.H = doc.width, doc.height
        self.CX, self.CY = self.W / 2, self.H / 2
        self.start = start if isinstance(start, (int, float)) else self._t(start)
        self.end = end if isinstance(end, (int, float)) else self._t(end)
        full = (self.INSET, self.INSET, self.W - self.INSET, self.H - self.INSET)
        self.holds = {round(self._t(c[0]), 3) for c in cues if len(c) > 4 and c[4] == "hold"}   # no drift after these cues
        self.cues = sorted(((self._t(c[0]), c[1], c[2], c[3]) for c in cues), key=lambda c: c[0])
        self.safe = sorted(((self._t(w), r) for w, r in (safe or [(self.start, full)])), key=lambda s: s[0])
        self.drift = drift
        self.keys = self._track()

    def _t(self, w):
        if isinstance(w, (int, float)):
            return float(w)
        if self.resolve is None:
            raise TypeError(f"Cam {self.name!r}: {w!r} is not a time and no resolve callable was given")
        return self.resolve(w[0]) + w[1] if isinstance(w, tuple) else self.resolve(w)

    def safe_at(self, t):
        """the safe rect in force at t"""
        rect_ = self.safe[0][1]
        for w, r in self.safe:
            if w <= t + 1e-6: rect_ = r
        return rect_

    def clamp(self, t, cx, cy, z):
        """(cx, cy, z) moved and zoomed out just enough that the safe rect in force at t, with the drift's slack,
        sits inside the usable view"""
        x0, y0, x1, y1 = self.safe_at(t)
        slack = 1 + self.drift
        z = min(z, (self.W - 2 * self.MX) / (x1 - x0) / slack, (self.H - 2 * self.MY) / (y1 - y0) / slack)
        hw, hh = (self.CX - self.MX) / (z * slack), (self.CY - self.MY) / (z * slack)   # half the usable view, in world units
        cx = min(max(cx, x1 - hw), x0 + hw)
        cy = min(max(cy, y1 - hh), y0 + hh)
        return cx, cy, z

    def _track(self):
        cues = [(t, *self.clamp(t, cx, cy, z)) for t, cx, cy, z in self.cues]
        a, b = self.start - 0.5, self.end + 0.5
        keys_ = [(a, *cues[0][1:])]
        for i, (t, cx, cy, z) in enumerate(cues):
            nxt = cues[i + 1][0] - self.LEAD if i + 1 < len(cues) else b
            prev = keys_[-1]
            r0, r1 = self.safe_at(t - 0.5), self.safe_at(t)
            area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
            widening, narrowing = area(r1) > area(r0) * 1.05, area(r1) < area(r0) * 0.95
            if i == 0:
                keys_.append((max(t, a + 0.1), cx, cy, z))
            else:
                start = max(prev[0] + 0.05, t + 1.2 if narrowing else t - self.LEAD)
                if start > prev[0] + 0.05:
                    keys_.append((start, *prev[1:]))
                dur = 1.4 if widening else 1.7 if narrowing else min(max((nxt - start) * 0.5, self.MOVE[0]), self.MOVE[1])
                tt = min(start + dur, max(start + 0.3, nxt - 0.05))
                keys_.append((tt, cx, cy, z))
            sgn = -1 if i % 2 else 1
            last = keys_[-1]
            if round(t, 3) in self.holds:
                keys_.append((max(last[0] + 0.1, nxt - 0.05), *last[1:]))
                continue
            dcx, dcy, dz = self.clamp(max(last[0] + 0.1, nxt - 0.05), cx + sgn * 12, cy - 7, z * (1 + self.drift))
            keys_.append((max(last[0] + 0.1, nxt - 0.05), dcx, dcy, dz))
        return keys_

    def at(self, t):
        """(cx, cy, z) at film time t (sine-in-out between keys)"""
        k = self.keys
        if t <= k[0][0]: return k[0][1:]
        for (t0, *p), (t1, *q) in zip(k, k[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / max(t1 - t0, 1e-6); e = 0.5 - 0.5 * math.cos(math.pi * u)
                return tuple(pp + (qq - pp) * e for pp, qq in zip(p, q))
        return k[-1][1:]

    def anim(self, factor=1.0):
        """the group's x, y, scaleX, scaleY keys; factor < 1 scales the move down (a parallax plane)"""
        CX, CY = self.CX, self.CY
        xs, ys, ss = [], [], []
        for t, cx, cy, z in self.keys:
            cx, cy, z = CX + (cx - CX) * factor, CY + (cy - CY) * factor, 1 + (z - 1) * factor
            xs.append((t, round(CX - (cx - CX) * z, 2))); ys.append((t, round(CY - (cy - CY) * z, 2))); ss.append((t, round(z, 4)))
        return sdk.Xml.of(keys("x", xs), keys("y", ys), keys("scaleX", ss), keys("scaleY", ss), sep="")

    def _group(self, gid):
        g = sdk.new(S.Composition, "group", id=self.doc.uid(gid or "cam2d-" + self.name), anchorX=self.CX, anchorY=self.CY, x=self.CX, y=self.CY)
        sdk.adopt(g, self.anim())
        return g

    def group(self, *content, gid=None):
        """the camera group as one element: its animation, then `content` (SDK elements, Xml or XML strings)"""
        g = self._group(gid)
        sdk.adopt(g, *content)
        return sdk.Xml.of(g)

    def open(self, gid=None):
        """the camera group's opening tag with its animation, as text (the streaming form: close it with Cam.CLOSE);
        group() is the same group as an element"""
        t = str(sdk.Xml.of(self._group(gid)))
        return t[:-len(self.CLOSE)]

    def verify(self, fade=1.2, step=0.25, lo=None, hi=None, tolerance=6):
        """every `step` s from lo (default start + 3.6) to hi (default end): the safe rect in force, and the one in
        force `fade` s earlier (its content may still be fading out), must sit inside the usable view.
        -> [(name, t, px over)] for every breach over `tolerance` px"""
        CX, CY = self.CX, self.CY
        bad = []
        t = self.start + 3.6 if lo is None else lo
        hi = self.end if hi is None else hi
        while t < hi:
            cx, cy, z = self.at(t)
            vx0, vx1, vy0, vy1 = cx - (CX - self.MX) / z, cx + (CX - self.MX) / z, cy - (CY - self.MY) / z, cy + (CY - self.MY) / z
            for x0, y0, x1, y1 in {self.safe_at(t), self.safe_at(t - fade)}:
                over = max(vx0 - x0, x1 - vx1, vy0 - y0, y1 - vy1) * z
                if over > tolerance: bad.append((self.name, round(t, 2), round(over)))
            t += step
        return bad
