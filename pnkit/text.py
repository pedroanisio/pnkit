"""pnkit.text — text assets and text layers.

text_asset() registers a <text> asset in doc.assets (once per distinct text and look) and returns its id and box.
label() places one as a layer that fades in and out, and enforces the information size floor: a label that carries
information is at least 36 px at 1080p (guide §5, Typography). Brand components (pn-label 28 px, pn-cite 24 px)
are not labels in this sense and are made by pnkit.brand at the kit's sizes.
"""
from . import sdk
from .sdk import S
from .xml import f, opacity, keys
from .palette import CREAM

__all__ = ["MIN_INFO_PX", "WIDTH_PER_EM", "text_asset", "label", "text_box"]

MIN_INFO_PX = 36                       # guide §5: information >= 36 px at 1080p
WIDTH_PER_EM = {"caps": 0.78, "num": 0.62, "big": 0.56, "head": 0.62}      # estimated advance per character, in em
WIDTH_PER_EM_DEFAULT = 0.58


def text_box(text, size, style="text", tracking=None):
    """the default (width, height) of a one-line text box: an estimate from the role's advance per character,
    the tracking (1/1000 em) and 30 px of slack; height 1.4 x size"""
    per = WIDTH_PER_EM.get(style, WIDTH_PER_EM_DEFAULT)
    return (int(max(60, len(text) * size * per + (len(text) * (tracking or 0) * size / 1000) + 30)), int(size * 1.4))


def text_asset(doc, text, size=40, color=CREAM, style="text", width=None, height=None, align="start", tracking=None,
               wrap=None, spans=None):
    """-> (asset id, width, height). style is a role in doc.styles (text, caps, num, head, note, big).
    spans: [(text, role or None, colour or None)] for mixed runs; `text` then only keys the cache and sizes the box."""
    key = (text, size, color, style, width, height, align, tracking, wrap, str(spans))
    if key in doc.texts:
        return doc.texts[key]
    aid = doc.uid("t")
    bw, bh = text_box(text, size, style, tracking)
    width = width or bw
    height = height or bh
    st = doc.styles[style]
    if spans:
        asset = sdk.new(S.Assets, "text", id=aid, style=st, size=size, width=width, height=height, align=align, color=color,
                        tracking=tracking or None, wrap=wrap or None)
        for t, r, c in spans:
            asset.add(sdk.new(asset, "span", role=r or None, color=c or None)).content = t
    else:
        asset = sdk.new(S.Assets, "text", id=aid, text=text, style=st, size=size, width=width, height=height, align=align,
                        color=color, tracking=tracking or None, wrap=wrap or None)
    doc.assets.append(sdk.Xml.of(asset))
    doc.texts[key] = (aid, width, height)
    return aid, width, height


def label(doc, text, x, y, a, b, size=40, color=CREAM, style="text", anchor="center", fin=0.4, fout=0.4, extra="", width=None,
          tracking=None, peak=1.0, preset=None, pdur=0.8, wrap=None, height=None, spans=None, lid=None, attrs=""):
    """a text layer anchored center|left|right at (x, y), vertically centred, visible [a, b].
    With b None it fades in at a over fin and holds peak indefinitely, with no fade-out.
    size is raised to MIN_INFO_PX. preset: a textAnimator preset starting at a for pdur s. extra: XML appended inside
    the layer (more animation); attrs: attributes appended to the layer tag."""
    size = max(size, MIN_INFO_PX)
    aid, w, h = text_asset(doc, text, size, color, style, width=width, align={"center": "center", "left": "start", "right": "end"}[anchor],
                           tracking=tracking, wrap=wrap, height=height, spans=spans)
    ax = {"center": w / 2, "left": 0, "right": w}[anchor]
    anim = sdk.new(S.Layer, "textAnimator", preset=preset, presetStart=a, presetDuration=pdur) if preset else None
    if b is not None:
        op = opacity(a, b, fin, fout, peak)
    elif fin > 0:
        op = keys('opacity', [(a, 0, 'cubic-out'), (a + fin, peak)])
    elif a > 0:
        op = keys('opacity', [(0, 0, 'hold'), (a, peak, 'hold')])
    else:
        op = keys('opacity', [(a, peak, 'hold')])
    layer = sdk.new(S.Composition, "layer", id=lid or doc.uid("l-" + aid), asset=aid, x=x, y=y, anchorX=float(ax), anchorY=h / 2,
                    **sdk.attrs_of(attrs))
    sdk.adopt(layer, anim, op, extra)
    return sdk.Xml.of(layer)
