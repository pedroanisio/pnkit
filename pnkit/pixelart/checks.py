"""pnkit.pixelart.checks — build-time picture checks that need no render (from Lula work/art3/v3/checks_picture.py).

`CheckedCtx(Ctx)` observes the unchanged scene modules while they build and records findings (it never changes the
output: a scene built on CheckedCtx gives the same XML as on Ctx). The judgements are pnkit.pixel's:

  zoom-window-outside-set   ctx.zoom(z, cx, cy) shows set x cx-160/z .. cx+160/z, y cy-73/z .. cy+107/z (the zoom group puts
                            (cx, cy) at picture point (160, 73)). Past the set the picture is the project's flat
                            background (Lula 11a: zoom(2, 276, 76), x 196..356 on a 320-column set). pnkit.pixel.view_outside.
  figure-cut-mid-body       ctx.actor(..., crop=N) cut between 35 % and 85 % of the sprite height and nothing drawn later in
                            the same parent covers the cut rows over 60 % of the figure's width (a table, a counter).
                            pnkit.pixel.figure_cut. Limit: a cover drawn in another group is not seen (false positive).
  plate-line-break          a plate's wrapped lines end in ':' or an arrow, or leave a lone value on a line.
                            pnkit.pixel.plate_line_breaks.

Findings are dicts {check, shot, scene, detail}. Waivers are [{check, shot, reason}], reason required:
apply_waivers marks findings `waived`.
"""
from .. import pixel
from .ctx import Ctx, W, H

ANCHOR = (160, 73)          # the zoom group's picture point (ctx.Ctx._Zoom)
COVER = 0.6                 # a later draw covers a cut when it spans this share of the figure's width on the cut rows


class CheckedCtx(Ctx):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.findings = []
        self._wraps = {}
        self._seq = 0

    def _add(self, check, detail):
        self.findings.append(dict(check=check, shot=self.cur['name'] if self.cur else None, scene=self.scene, detail=detail))

    def shot(self, name, a, b, bg=None, pan=None, hz=6, py=None):
        s = super().shot(name, a, b, bg=bg, pan=pan, hz=hz, py=py)
        cells = bg.cells if bg is not None and bg.cells else {(0, 0): None}
        self.cur['set_w'] = max(W, max(x for x, _ in cells) + 1)
        self.cur['set_h'] = max(H, max(y for _, y in cells) + 1)
        return s

    def zoom(self, z, cx, cy, parent, **attrs):
        v = pixel.view_outside(self.cur['set_w'], self.cur['set_h'], W, H, int(z), cx, cy, anchor=ANCHOR)
        if v.outside:
            self._add('zoom-window-outside-set', f'zoom x{int(z)} at ({cx}, {cy}): {v.describe()}; set is {self.cur["set_w"]}x{self.cur["set_h"]}')
        return super().zoom(z, cx, cy, parent, **attrs)

    def G(self, p, q, x=0, y=0, **attrs):
        g = super().G(p, q, x, y, **attrs)
        if self.cur is not None and q.cells:
            rows = {}
            for (cx, cy) in q.cells:
                r_ = rows.get(cy)
                if r_ is None:
                    rows[cy] = [cx, cx]
                else:
                    r_[0] = min(r_[0], cx); r_[1] = max(r_[1], cx)
            self._seq += 1
            self.cur.setdefault('draws', []).append((self._seq, id(p), x, y, rows))
        return g

    def actor(self, p, kind, pose, x, y, a, b, **kw):
        crop = kw.get('crop')
        if crop is not None:
            q = self.sprite_frame(kind, pose, 0.0, kw.get('flip', False), .5, kw.get('era'), kw.get('clothes'))
            if q.cells:
                ys = [yy for _, yy in q.cells]; xs = [xx for xx, _ in q.cells]
                sc = kw.get('scale', 1)
                h = (max(ys) - min(ys) + 1) * sc
                if pixel.figure_cut(h, crop) is not None:
                    self.cur.setdefault('crops', []).append(dict(seq=self._seq + 1, parent=id(p), kind=kind, pose=pose, x=x, y=y, crop=crop,
                                                                 h=h, x0=x + min(xs) * sc, x1=x + (max(xs) + 1) * sc))
        return super().actor(p, kind, pose, x, y, a, b, **kw)

    @staticmethod
    def _occluded(c, draws):
        cut = c['y'] + c['crop']
        span = max(1, c['x1'] - c['x0'])
        for seq, par, gx, gy, rows in draws:
            if seq <= c['seq'] or par != c['parent']:
                continue
            for ry in (cut - 1, cut):
                rr = rows.get(ry - gy)
                if rr and min(c['x1'], gx + rr[1] + 1) - max(c['x0'], gx + rr[0]) >= COVER * span:
                    return True
        return False

    def finish(self):
        for rec in self.shots:
            for c in rec.get('crops', []):
                why = pixel.figure_cut(c['h'], c['crop'], occluded=self._occluded(c, rec.get('draws', [])))
                if why:
                    self.findings.append(dict(check='figure-cut-mid-body', shot=rec['name'], scene=rec['scene'],
                                              detail=f'{c["kind"]!r} {c["pose"]}: {why}'))
        return super().finish()

    def _wrap(self, text, maxw):
        out = super()._wrap(text, maxw)
        self._wraps[text] = out
        return out

    def plate(self, text, slot_, a, b, **kw):
        g = super().plate(text, slot_, a, b, **kw)
        why = pixel.plate_line_breaks(self._wraps.get(text, [text]))
        if why:
            self._add('plate-line-break', f'plate {text!r}: {"; ".join(why)}')
        return g

    def box(self, p, reserved, a=None, b=None, fill='blue0', lines=(), color='cream', grows=False):
        g = super().box(p, reserved, a=a, b=b, fill=fill, lines=lines, color=color, grows=grows)
        why = pixel.plate_line_breaks(list(lines))
        if why:
            self._add('plate-line-break', f'box {list(lines)!r}: {"; ".join(why)}')
        return g


def apply_waivers(findings, waivers, report_unused=False):
    """findings with `waived` set from waivers [{check, shot, reason}] (a waiver without a reason raises ValueError);
    with report_unused, also the waivers that matched nothing (stale exceptions)"""
    keys = {}
    for w in waivers:
        if not str(w.get('reason', '')).strip():
            raise ValueError(f'waiver {w!r} has no reason')
        keys[(w['check'], w['shot'])] = w
    used = set()
    out = []
    for f in findings:
        k = (f['check'], f['shot'])
        out.append(dict(f, waived=k in keys))
        if k in keys:
            used.add(k)
    if report_unused:
        return out, [w for k, w in keys.items() if k not in used]
    return out
