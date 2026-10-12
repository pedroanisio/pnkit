"""pnkit — the shared component library for PALS's Notes videos.

A Python package that builds scenes with `sr_core.scene` (the Python scene SDK, sr-core >= 1.7.0): the SDK checks
every element and attribute when it is made. Components return `Xml`, a `str` of the XML that also holds the SDK
elements (see `sdk`). It writes inline scene XML: formatting and ids (xml), the document's
registries (doc), text (text), shapes (draw), the 2D camera with its safe-rect clamp and check (camera), the brand
kit's prologue and components (brand), captions (captions), Shorts overlays and spans (shorts), the physics
block (physics), baked tapered-tube meshes for geometry no native primitive covers (mesh), an articulated 3D
figure built from them (figure), the narration dictionary (vo: written -> spoken text by language, and a
pre-synthesis check) and a film's sound cues held to the audio-design rule (audio: the palette, the retired sweeps and
stings, soft struck foley only after the last word). Projects vendor it into film/vendor/pnkit with tools/sync.py and pin it with a lock file.

    from vendor import pnkit
    DOC = pnkit.Doc(1920, 1080, styles={...})
    K = pnkit.bind(DOC)                 # the helpers with the Doc filled in: K.label(...), K.draw(...), K.Cam(...)
"""
import functools, types

from .doc import Doc
from . import sdk, xml, palette, text, draw, camera, brand, captions, shorts, physics, mesh, figure, vo, audio, files, timings

__version__ = "1.0.0"
__all__ = ["Doc", "bind", "__version__", "sdk", "xml", "palette", "text", "draw", "camera", "brand", "captions", "shorts",
           "physics", "mesh", "figure", "vo", "audio"]


def bind(doc):
    """a namespace of the helpers that register into `doc`, with doc already passed:
    uid, text_asset, label, draw, rect, disc, group, pill, Cam, Brand; and the pure ones as they are:
    f, esc, opacity, keys, path_d, arrow_d, round_rect_d, hash01, fmt"""
    p = functools.partial
    return types.SimpleNamespace(
        doc=doc, uid=doc.uid,
        text_asset=p(text.text_asset, doc), label=p(text.label, doc),
        draw=p(draw.draw, doc), rect=p(draw.rect, doc), disc=p(draw.disc, doc), group=p(draw.group, doc), pill=p(draw.pill, doc),
        Cam=p(camera.Cam, doc), Brand=p(brand.Brand, doc),
        f=xml.f, esc=xml.esc, opacity=xml.opacity, keys=xml.keys, path_d=xml.path_d, arrow_d=draw.arrow_d,
        round_rect_d=draw.round_rect_d, hash01=xml.hash01, fmt=xml.fmt)
