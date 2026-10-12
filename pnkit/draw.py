"""pnkit.draw — shapes that fade in and out on the film's clock: self-drawing paths, rects, discs, groups, pills.

Every element gets a unique id from the Doc (sid/gid/pid is the id's base). a, b are film times: the element is
visible [a, b] with the given fades (b None where allowed: no opacity animation). `extra` is XML appended inside
the element (more <animate>s), `attrs` is appended to its tag.
"""
import math
from . import sdk
from .sdk import S
from .xml import f, opacity, animate
from .text import text_asset
from .palette import CREAM, ORANGE, INK

__all__ = ["draw", "rect", "disc", "arrow_d", "round_rect_d", "group", "pill"]


def draw(doc, d, a, b, stroke=CREAM, width=3.0, dur=1.0, dash=None, fill="#00000000", effects=None, peak=1.0, fin=0.15, fout=0.5,
         sid=None, extra="", cap="round", ease="cubic-in-out", attrs=""):
    """a frame-sized path that draws itself (trimEnd 0 -> 1) from a over dur, then stays until b (dur 0: drawn at once)"""
    sh = sdk.new(S.Composition, "shape", id=doc.uid(sid or "p"), shape="path", width=doc.width, height=doc.height, path=d, fill=fill,
                 stroke=stroke, strokeWidth=width, strokeCap=cap, strokeJoin="round", trimEnd=0 if dur > 0 else 1,
                 dash=dash or None, effects=effects or None, **sdk.attrs_of(attrs))
    trim = animate("trimEnd", [(a, "0", ease), (a + dur, "1", None)]) if dur > 0 else None
    sdk.adopt(sh, trim, opacity(a, b, fin, fout, peak), extra)
    return sdk.Xml.of(sh)


def rect(doc, x, y, w, h, fill, a, b, radius=0, stroke=None, sw=2, peak=1.0, fin=0.4, fout=0.4, extra="", sid=None, attrs="", anchor="center"):
    """a rect at (x, y), anchored at its centre (anchor="center") or its top-left corner (anything else)"""
    ax, ay = (w / 2, h / 2) if anchor == "center" else (0, 0)
    sh = sdk.new(S.Composition, "shape", id=doc.uid(sid or "r"), shape="rect", x=x, y=y, anchorX=ax, anchorY=ay, width=w, height=h,
                 radius=radius, fill=fill, stroke=stroke or None, strokeWidth=sw if stroke else None, **sdk.attrs_of(attrs))
    sdk.adopt(sh, opacity(a, b, fin, fout, peak) if b is not None else None, extra)
    return sdk.Xml.of(sh)


def disc(doc, x, y, r, fill, a, b, stroke=None, sw=2, peak=1.0, fin=0.3, fout=0.4, extra="", sid=None, attrs=""):
    """a circle of radius r centred on (x, y)"""
    sh = sdk.new(S.Composition, "shape", id=doc.uid(sid or "d"), shape="ellipse", x=x, y=y, anchorX=r, anchorY=r, width=2 * r, height=2 * r,
                 fill=fill, stroke=stroke or None, strokeWidth=sw if stroke else None, **sdk.attrs_of(attrs))
    sdk.adopt(sh, opacity(a, b, fin, fout, peak) if b is not None else None, extra)
    return sdk.Xml.of(sh)


def arrow_d(x1, y1, x2, y2, head=16):
    """path data for an arrow from (x1, y1) to (x2, y2) with an open head of `head` px"""
    ang = math.atan2(y2 - y1, x2 - x1)
    h1 = (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45)); h2 = (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))
    return f"M{f(x1)} {f(y1)} L{f(x2)} {f(y2)} M{f(h1[0])} {f(h1[1])} L{f(x2)} {f(y2)} L{f(h2[0])} {f(h2[1])}"


def round_rect_d(x, y, w, h, r):
    """path data for a rounded rectangle with its top-left corner at (x, y), drawn clockwise from the top edge"""
    return (f"M{f(x + r)} {f(y)} L{f(x + w - r)} {f(y)} A{f(r)} {f(r)} 0 0 1 {f(x + w)} {f(y + r)} L{f(x + w)} {f(y + h - r)} "
            f"A{f(r)} {f(r)} 0 0 1 {f(x + w - r)} {f(y + h)} L{f(x + r)} {f(y + h)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(y + h - r)} "
            f"L{f(x)} {f(y + r)} A{f(r)} {f(r)} 0 0 1 {f(x + r)} {f(y)} Z")


def group(doc, content, gid=None, a=None, b=None, fin=0.5, fout=0.5, attrs="", extra=""):
    """a group of the non-empty items of `content`, one per line; with a, b it fades as a whole. Items are SDK elements,
    `Xml` or XML strings; the group takes only what the schema allows in a <group>."""
    g = sdk.new(S.Composition, "group", id=doc.uid(gid or "g"), **sdk.attrs_of(attrs))
    sdk.adopt(g, opacity(a, b, fin, fout) if a is not None else None, extra)
    sdk.ws(g)
    for i, c in enumerate([c for c in content if c]):
        if i:
            sdk.ws(g)
        sdk.adopt(g, c)
    sdk.ws(g)
    return sdk.Xml.of(g)


def pill(doc, x, y, text, a, b, w=None, h=64, fill=ORANGE, color=INK, size=38, pid=None, extra="", fin=0.3, fout=0.4, stroke=None, attrs=""):
    """a pill centred on (x, y): a fully rounded rect and a centred caps label, as one group anchored at its centre.
    Ids: <pid>, <pid>-b (the body), <pid>-t (the label)."""
    w = w or int(len(text) * size * 0.62 + 56)
    pid = doc.uid(pid or "pill")
    aid, tw_, th = text_asset(doc, text, size, color, "caps", width=w, align="center", tracking=20)
    g = sdk.new(S.Composition, "group", id=pid, x=x, y=y, anchorX=w / 2, anchorY=h / 2, width=w, height=h, **sdk.attrs_of(attrs))
    sdk.adopt(g, opacity(a, b, fin, fout), extra)
    sdk.adopt(g, sdk.new(g, "shape", id=f"{pid}-b", shape="rect", width=w, height=h, radius=h / 2, fill=fill,
                         stroke=stroke or None, strokeWidth=3 if stroke else None))
    sdk.adopt(g, sdk.new(g, "layer", id=f"{pid}-t", asset=aid, x=0, y=(h - th) / 2 + 1))
    return sdk.Xml.of(g)
