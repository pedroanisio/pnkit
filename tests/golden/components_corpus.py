"""The component corpus: one fixed call of every function that writes scene XML, with the XML each returns.

`corpus(kit_path)` returns {name: XML text} for pnkit as it is imported. components-0.8.0.json holds what pnkit 0.8.0
(strings) wrote for the same calls; tests/test_golden_components.py checks that this version writes C14N-equal
documents. Every entry is a fragment: the checker wraps it in one root element, so a call that returns several
sibling elements is one entry. Pure, light, deterministic; the figure's OBJ meshes go to a temporary folder."""
import os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(os.path.dirname(HERE))


def corpus(kit_path, lib=LIB):
    if lib not in sys.path:
        sys.path.insert(0, lib)
    import pnkit
    from pnkit import xml, text, draw, camera, brand, captions, shorts, physics, figure, audio
    out = {}
    S = {"text": "s-text", "caps": "s-caps", "num": "s-num", "head": "s-head", "note": "s-note", "big": "s-big"}

    def put(name, value):
        out[name] = "\n".join(str(v) for v in value) if isinstance(value, (list, tuple)) else str(value)

    # ---- xml
    put("xml.opacity", xml.opacity(1, 4))
    put("xml.opacity.short-window", xml.opacity(2, 2.02))
    put("xml.opacity.peak", xml.opacity(1, 5, 0.5, 0.5, peak=0.6, ease_in="linear", ease_out="linear"))
    put("xml.keys", xml.keys("x", [(0.12345, 1.5), (1, "a,b", "linear"), (2, -3)]))

    # ---- text, draw
    doc = pnkit.Doc(styles=S)
    r1 = text.text_asset(doc, "Plain", 40)
    r2 = text.text_asset(doc, "CAPS", 40, style="caps", tracking=20, wrap="balance", width=500, height=80)
    r3 = text.text_asset(doc, "A & B", 44, style="num", align="center", color="#E8581C")
    r4 = text.text_asset(doc, "A B", 40, spans=[("A ", None, None), ("B < c", "accent", "#E8581C")])
    put("text.assets", doc.assets)
    out["text.assets.ids"] = repr([r1, r2, r3, r4])
    doc = pnkit.Doc(styles=S)
    put("text.label", text.label(doc, "Label one", 960, 300, 1, 4))
    put("text.label.left", text.label(doc, "LEFT & more", 200, 400, 1, 4, anchor="left", size=20, style="caps", tracking=40))
    put("text.label.right", text.label(doc, "Right", 1700, 400, 1, 4, anchor="right", preset="fade-up", pdur=0.5))
    put("text.label.open", text.label(doc, "Open", 200, 300, 2, None, fin=0.4, peak=0.6))
    put("text.label.step", text.label(doc, "Step", 200, 300, 2, None, fin=0))
    put("text.label.now", text.label(doc, "Now", 200, 300, 0, None, fin=0, peak=0.7))
    put("text.label.extra", text.label(doc, "Extra", 300, 300, 0, 3, extra=keys_y(xml), attrs=' tags="hud"', lid="my-label"))
    put("text.label.spans", text.label(doc, "S", 300, 500, 0, 3, spans=[("S ", None, None), ("p", "accent", "#E8581C")], wrap="balance"))
    put("text.label.assets", doc.assets)
    doc = pnkit.Doc(1080, 1920, styles=S)
    put("draw.draw", draw.draw(doc, "M0 0 L10 10", 1, 3))
    put("draw.draw.opts", draw.draw(doc, "M0 0 L10 10 Z", 1, 3, dash="8 6", effects="glow", fill="#112233", dur=0, sid="line", extra=xml.keys("x", [(0, 1)]), attrs=' tags="g"'))
    put("draw.rect", draw.rect(doc, 100, 200, 100, 40, "#112233", 0, 1))
    put("draw.rect.tl", draw.rect(doc, 0, 0, 100, 40, "#112233", 0, None, anchor="top-left", radius=8, stroke="#FFFFFF", sw=3))
    put("draw.disc", draw.disc(doc, 5, 5.5, 10, "#FFFFFF", 0, 1, stroke="#000000"))
    put("draw.group", draw.group(doc, [draw.rect(doc, 1, 2, 3, 4, "#112233", 0, 1), "", None, draw.disc(doc, 1, 2, 3, "#FFFFFF", 0, 1)], a=0, b=2))
    put("draw.group.plain", draw.group(doc, [draw.disc(doc, 1, 2, 3, "#FFFFFF", 0, 1)], gid="plain", attrs=' x="5"'))
    put("draw.pill", draw.pill(doc, 500, 400, "QUEUE C", 1, 4))
    put("draw.pill.opts", draw.pill(doc, 500.5, 400, "Q", 1, 4, w=300, h=70, stroke="#FFFFFF", pid="pp"))
    put("draw.assets", doc.assets)

    # ---- camera
    doc = pnkit.Doc(1920, 1080)
    cam = camera.Cam(doc, "act1", [(1.0, 960, 540, 1.0), (5.0, 700, 400, 1.4), (9.0, 960, 540, 1.0, "hold")], 0, 12)
    put("camera.anim", cam.anim())
    put("camera.anim.half", cam.anim(0.5))
    put("camera.group", cam.open() + draw.disc(doc, 5, 5, 10, "#FFFFFF", 0, 1) + camera.Cam.CLOSE)

    # ---- brand
    pro = brand.prologue(kit_path, {"pn-title": "A & B", "pn-kicker": "SCIENCE"})
    for k in ("parameters", "styles", "layouts", "safeAreas", "symbols", "font", "accessibility"):
        put("brand.prologue." + k, pro[k])
    put("brand.prologue.texts", pro["texts"])
    put("brand.extend", brand.extend(pro["styles"], "styles", '    <textStyle id="x-extra" basedOn="pn-base"/>\n'))
    put("brand.fade", brand.fade(1.0, 1.2))
    doc = pnkit.Doc()
    b = brand.Brand(doc)
    put("brand.title_card", b.title_card_xml(1, 5, "KICKER", "Title & more", emblem=[("M0 0 L10 10", "#F2EBDD", 5), ("M5 5 L9 9", "#E8581C", 4, "#112233")]))
    put("brand.chapter_card", b.chapter_card_xml(10, 13, "01", "A chapter", emblem=[("M0 0 L10 10", "#F2EBDD", 5)]))
    put("brand.lower_third", b.lower_third_xml(20, 25, "Name", "Role"))
    put("brand.source_line", b.source_line_xml(20, 25, "Source: x"))
    put("brand.end_card", b.end_card_xml(30, 40, ["Credits", "More credits"]))
    put("brand.notch", b.notch(0, 5, x=10, y=20))
    put("brand.ink", b.ink(0, 5))
    put("brand.assets", b.assets)

    # ---- captions
    words = [("Hello", 1.0, 1.3), ("there", 1.35, 1.7), ("my", 1.8, 1.9), ("dear", 1.95, 2.3), ("friend", 2.35, 2.9),
             ("and", 3.5, 3.7), ("goodbye", 3.75, 4.4), ("for", 4.45, 4.6), ("now", 4.65, 5.0), ("5", 5.1, 5.3), ("things", 5.35, 5.8)]
    put("captions.cue_xml", captions.cue_xml(captions.split_cues(words)))
    put("captions.cue_xml.width", captions.cue_xml(captions.split_cues(words), width=20))
    put("captions.sidecar", captions.sidecar(words))
    put("captions.sidecar.opts", captions.sidecar(words, track_id="subs-pt", language="pt-br", label="Português"))
    put("captions.short_cues", captions.short_cues(words, [(0.9, 3.0, 0.0), (3.4, 5.9, 2.2)], not_before=1.2))

    # ---- shorts
    put("shorts.layout", shorts.LAYOUT_XML)
    lines, maps, T = shorts.segments([(10.0, 20.0), (30.0, 35.0), (50.0, 52.6)])
    put("shorts.segments", lines)
    put("shorts.feather_paints", shorts.feather_paints())
    doc = pnkit.Doc()
    subj = lambda x, y, s, gid: f'<group id="{doc.uid(gid)}" x="{x}" y="{y}"><shape id="{gid}-s" shape="rect" width="{int(100 * s)}" height="40" fill="#112233"/></group>'
    put("shorts.overlay", shorts.overlay(doc, "s1", 7.27, ("A ", "B", " C"), subj, ("THE ", "TITLE & CO")))
    put("shorts.overlay.assets", doc.assets)
    put("shorts.output", shorts.output_xml("s1", "slug", lines, '      <cue start="0.900" end="2.000" text="x"/>', "cap", "cap-on"))
    doc = pnkit.Doc()
    subj2 = lambda x, y, s, gid: f'<group id="{doc.uid(gid)}"/>'
    o2, sy2, la2 = shorts.build(doc, [("s1", "slug", [("a", "a")], ("A ", "B", "")), ("s2", "two", [("b", "b")], ("C ", "D", "!"))],
                                lambda spans: [(4.78, 9.45), (20.0, 22.6)], lambda maps: '      <cue start="0.900" end="2.000" text="x"/>',
                                lambda sid, T, head: shorts.overlay(doc, sid, T, head, subj2, ("THE ", "TITLE")), "cap", "cap-on")
    put("shorts.build.outputs", o2); put("shorts.build.symbols", sy2); put("shorts.build.layouts", la2)
    put("shorts.build.registries", doc.paints + doc.assets)

    # ---- physics
    put("physics.block", physics.block(["a"], ['<forceField id="ff" type="gravity"/>']) or "")
    put("physics.block.empty", physics.block([], []) or "<none/>")

    # ---- figure
    with tempfile.TemporaryDirectory() as d:
        ids, assets = figure.bone_meshes(d)
        put("figure.bone_meshes", assets)
    mats, mxml = figure.default_materials()
    put("figure.materials", mxml)
    put("figure", figure.figure("f1", [(0, 2, "walk", [(0, 0), (100, 50)]), (2, 3, "stand", None)], 0, 0, ids, mats))
    put("figure.accessory", figure.figure("f2", [(0, 1, "stand", None)], 10, 5, ids, mats, head_accessory='<object3D id="f2-hat" primitive="box" parent="f2-spine"/>'))

    # ---- audio
    c = audio.Cues()
    c.ambience("room", 0.1)
    c.sfx(12.5, "clunk", 0.26); c.sfx(0.65, "paper"); c.sfx(3.0, "clunk")
    put("audio.assets", c.assets(30.0, tag="s06", digest=lambda n: "ab" * 32))
    put("audio.tracks", c.tracks(30.0))
    return out


def keys_y(xml):
    return xml.keys("y", [(0, 1, "hold")])


if __name__ == "__main__":
    import json
    json.dump(corpus(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else LIB), sys.stdout, indent=1, ensure_ascii=False)
