"""pnkit.xml — number formatting, ids and animation keys for the scene SDK.

`f` and `esc` are pnkit's number and text forms (pnkit._num); `Ids` is the one registry a document needs to keep its ids
unique; `opacity` and `keys` build <animate> elements through `sr_core.scene` (pnkit.sdk) and return them as `Xml`,
a `str` that is their XML text. The rest is pure.
"""
import math

from ._num import f, esc
from . import sdk
from .sdk import S

__all__ = ["f", "esc", "Ids", "opacity", "keys", "animate", "path_d", "hash01", "HASH_EXPR", "fmt"]


class Ids:
    """The ids used in one document. uid(base) returns base, or base-2, base-3 ... when it is taken."""

    def __init__(self):
        self.used = set()

    def uid(self, base):
        i, k = base, 1
        while i in self.used:
            k += 1; i = f"{base}-{k}"
        self.used.add(i); return i

    def __contains__(self, i):
        return i in self.used

    def __len__(self):
        return len(self.used)


def animate(prop, rows):
    """an <animate property=prop> of <key>s from (time, value, interpolation or None) rows, as `Xml`"""
    an = sdk.new(S.Layer, "animate", property=prop)
    for t, v, e in rows:
        sdk.add(an, sdk.new(an, "key", time=t, value=v, interpolation=e))
    return sdk.Xml.of(an)


def opacity(a, b, fin=0.5, fout=0.5, peak=1.0, ease_in="cubic-out", ease_out="cubic-in"):
    """an opacity <animate>: visible from a (fading in over fin) to b (fading out over fout). A window shorter than
    0.1 s is widened to 0.1 s; fades that do not fit share the window equally."""
    a, b = float(a), float(b)
    if b < a + 0.1: b = a + 0.1
    if fin + fout > b - a: fin = fout = (b - a) / 2
    pk = f(float(peak))
    return animate("opacity", [(a, "0", ease_in), (a + fin, pk, None), (max(a + fin, b - fout), pk, ease_out), (b, "0", None)])


def keys(prop, pairs, ease="sine-in-out"):
    """<animate> from (time, value[, ease]) tuples; the ease of a key shapes the move that starts there. Times are
    rounded to the millisecond; numeric values go through f(), others are written as given."""
    rows = []
    for p in pairs:
        t, v = p[0], p[1]; e = p[2] if len(p) > 2 else ease
        rows.append((round(float(t), 3), f(v) if isinstance(v, (int, float)) else v, e))
    return animate(prop, rows)


def path_d(pts, closed=False):
    """a polyline as path data, coordinates rounded to 0.1 px"""
    d = "M" + " L".join(f"{f(round(float(x), 1))} {f(round(float(y), 1))}" for x, y in pts)
    return d + (" Z" if closed else "")


def hash01(i, salt=0):
    """a stable pseudo-random value in [0, 1) for an integer (the same formula is HASH_EXPR, for expressions)"""
    q = math.sin((i + salt * 97.13) * 12.9898) * 43758.5453
    return q - math.floor(q)


HASH_EXPR = "var q = Math.sin((index + {salt} * 97.13) * 12.9898) * 43758.5453; q = q - Math.floor(q);"


def fmt(n):
    """an integer with thousands separators (English)"""
    return f"{n:,}"
