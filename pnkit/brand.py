"""pnkit.brand — the PALS's Notes brand kit in an episode: its prologue, and its components as inline copies.

prologue(kit_path, params) returns the kit's prologue sections verbatim, with only the parameter defaults set for
the episode: style and token references resolve only inside the document that uses them, so every episode carries
them (guide §14, Brand).

Brand(doc) makes the kit's components (title card, chapter card, lower third, source line, end card, notch, ink)
as inline copies with the kit's styles, sizes, positions and motion, not as symbol instances: per-instance text
would need <override>, which the encoder drops after the first frame (guide §6, Avoid 1), and <include> cannot
carry per-use text (it resolves with the included document's own parameter defaults). Placed components go to
Brand.overlays, which the scene writes after its finish adjustment (halation, grain, vignette), so the brand
colours stay exact (guide §14). Their text assets go to Brand.assets; every text sets its colour explicitly (a
<text> that takes its colour from a textStyle renders white: guide §14, open engine bug).

The kit file is passed in by the project (a pinned copy, e.g. film/kit/palsnotes-brand.xml); pnkit reads no fixed
path.
"""
import hashlib

from . import sdk
from .sdk import S
from .xml import animate, f

__all__ = ["MOTION_IN", "MOTION_OUT", "NOTCH", "SIZES", "COLOURS", "prologue", "extend", "kit_sha256", "fade", "Brand"]

MOTION_IN, MOTION_OUT = 0.40, 0.30          # pn:motion-in cubic-out, pn:motion-out cubic-in
NOTCH = 64                                  # the brand mark, px at 1080p
SIZES = {"pn-label": 28, "pn-display": 120, "pn-number": 160, "pn-heading": 64, "pn-cite": 24}
COLOURS = {"pn-label": "var(--pn-cream-muted)", "pn-display": "var(--pn-cream)", "pn-number": "var(--pn-orange)",
           "pn-heading": "var(--pn-cream)", "pn-cite": "var(--pn-cream-muted)"}
NEXT = "NEXT ON PALS'S NOTES"               # the kit's pn-next default (English)


def _section(el):
    """a kit section as it stood in the file: indented two spaces, then the element"""
    return sdk.Xml.of(S.Text("  "), el.copy(), sep="")


def prologue(kit_path, params):
    """the kit's sections, read with the SDK and kept as they are (comments, white space, attribute text) except the
    parameter defaults in `params` ({param id: value}; each must exist exactly once, with a default).
    -> {parameters, styles, layouts, safeAreas, symbols: section `Xml`; font: the font asset; texts: [the kit's text
    assets]; accessibility: the kit's accessibility element}"""
    kit = S.read(kit_path)
    pars = kit.find("parameters")
    for pid, val in params.items():
        hits = [p for p in (pars.find_all("param") if pars is not None else []) if p.id == pid and "default" in p.attributes()]
        if len(hits) != 1:
            raise KeyError(f"kit parameter {pid!r} found {len(hits)} times in {kit_path}")
        hits[0].default = val
    assets = kit.find("assets")
    font = next(e for e in assets.find_all("font") if e.id == "pn-archivo")
    texts = [e for e in assets.find_all("text") if (e.id or "").startswith("pn-t-")]
    out = {k: (_section(kit.find(k)) if kit.find(k) is not None else sdk.Xml("")) for k in ("parameters", "styles", "layouts", "safeAreas", "symbols")}
    out.update(font=sdk.Xml.of(font.copy()), texts=[sdk.Xml.of(t.copy()) for t in texts], accessibility=sdk.Xml.of(kit.find("metadata").find("accessibility").copy()))
    return out


def extend(block, tag, xml):
    """a prologue section with `xml` added before its closing tag (e.g. the episode's own text styles); a new section,
    the one given is left as it was"""
    if isinstance(block, sdk.Xml) and block.elements:
        el = block.elements[0]
        pre = [S.Text(n.text) for n in block.nodes[:block.nodes.index(el)]]
        el = el.copy()
    else:
        text = str(block)
        pre = [S.Text(text[:len(text) - len(text.lstrip())])] if text[:1].isspace() else []
        el = sdk.parse_sections(text)[0]
    last = el.nodes[-1] if el.nodes and isinstance(el.nodes[-1], S.Text) else None
    indent = ""
    if last is not None:                                  # the closing tag's indentation stays last
        indent = last.text[len(last.text.rstrip(" ")):]
        last.text = last.text[:len(last.text) - len(indent)]
    sdk.adopt(el, xml)
    if indent:
        el.nodes.append(S.Text(indent))
    return sdk.Xml.of(*pre, el, sep="")


def kit_sha256(kit_path):
    """the kit file's SHA-256, to compare with the pin a project keeps next to its copy"""
    return hashlib.sha256(open(kit_path, "rb").read()).hexdigest()


def fade(a, b, fin=MOTION_IN, fout=MOTION_OUT):
    """the kit's opacity motion: in over fin (cubic-out), out over fout (cubic-in); b is pushed out so both fit"""
    b = max(b, a + fin + fout)
    return animate("opacity", [(a, "0", "cubic-out"), (a + fin, "1", None), (b - fout, "1", "cubic-in"), (b, "0", None)])


class Brand:
    """The kit's components for one document. doc: the pnkit Doc (ids, frame size)."""

    def __init__(self, doc):
        self.doc = doc
        self.assets = []       # brand text assets made for this document
        self.overlays = []     # placed components, to write above the finish

    # ---------------------------------------------------------------- pieces
    def text(self, txt, style, width, height, extra=""):
        """a brand text asset at the kit's size for `style`, coloured explicitly -> asset id. extra: more attributes,
        as text (` wrap="balance" maxLines="3"`)"""
        aid = self.doc.uid("bt")
        more = sdk.attrs_of(extra)
        if "color" not in more:
            more = {"color": COLOURS[style], **more}
        self.assets.append(sdk.Xml.of(sdk.new(S.Assets, "text", id=aid, text=txt, width=width, height=height, size=SIZES[style], style=style, **more)))
        return aid

    def notch(self, a, b, x=0, y=None):
        """the brand mark (orange right triangle), bottom-left by default"""
        y = self.doc.height - NOTCH if y is None else y
        sh = sdk.new(S.Composition, "shape", id=self.doc.uid("notch"), shape="path", x=x, y=y, width=NOTCH, height=NOTCH,
                     path=f"M0 0 L0 {NOTCH} L{NOTCH} {NOTCH} Z", fill="var(--pn-orange)", tags="logo")
        sdk.adopt(sh, fade(a, b))
        return sdk.Xml.of(sh)

    def ink(self, a, b, fin=0.5, fout=0.6):
        """a full-frame ink field"""
        sh = sdk.new(S.Composition, "shape", id=self.doc.uid("ink"), shape="rect", width=self.doc.width, height=self.doc.height, fill="var(--pn-ink)")
        sdk.adopt(sh, fade(a, b, fin, fout))
        return sdk.Xml.of(sh)

    def emblem(self, items, a, b, dur=1.6):
        """a line-drawn subject: items [(path d, colour, width[, fill])]; each stroke draws on in turn (trimEnd), then
        fades with the card; the whole emblem drifts left 12 px/s, so the card never holds a frozen frame"""
        W, H = self.doc.width, self.doc.height
        out, n = [], max(1, len(items))
        for i, it in enumerate(items):
            d, col, w = it[:3]; fill = it[3] if len(it) > 3 else "#00000000"
            t0 = a + 0.25 + (dur - 0.6) * i / n
            sh = sdk.new(S.Composition, "shape", id=self.doc.uid("em"), shape="path", width=W, height=H, path=d, fill=fill, stroke=col,
                         strokeWidth=w, strokeCap="round", strokeJoin="round", trimEnd=0)
            sdk.adopt(sh, animate("trimEnd", [(t0, "0", "cubic-out"), (t0 + 0.7, "1", None)]), fade(a, b, 0.2, MOTION_OUT))
            out.append(sdk.Xml.of(sh))
        drift = animate("x", [(a, "0", "linear"), (b, "-" + f(12 * (b - a)), None)])
        g = sdk.new(S.Composition, "group", drift, id=self.doc.uid("emg"))
        for i, sh in enumerate(out):
            if i:
                sdk.ws(g)
            sdk.adopt(g, sh)
        return sdk.Xml.of(g)

    # ---------------------------------------------------------------- components (XML)
    def title_card_xml(self, a, b, kicker, title, emblem=None):
        """the opening title over ink: kicker (pn-label) at 192,300, title (pn-display, balanced, <= 3 lines) rising
        into 192,360, an optional emblem (items for emblem()), the notch"""
        k = self.text(kicker, "pn-label", 1200, 48); t = self.text(title, "pn-display", 1400, 360, ' wrap="balance" maxLines="3"')
        uid = self.doc.uid
        out = [self.ink(a, b), sdk.Xml.of(sdk.new(S.Composition, "layer", fade(a, b), id=uid("tc-k"), asset=k, x=192, y=300)),
               sdk.Xml.of(sdk.new(S.Composition, "layer", fade(a + 0.1, b), animate("y", [(a + 0.1, "392", "cubic-out"), (a + 0.5, "360", None)]),
                                  id=uid("tc-t"), asset=t, x=192, y=360))]
        if emblem:
            out.append(self.emblem(emblem, a + 0.2, b, 2.0))
        out.append(self.notch(a, b))
        return sdk.Xml.of(*out)

    def chapter_card_xml(self, a, b, number, title, emblem=None):
        """a chapter divider over ink: the number (pn-number, orange) at 192,340, a rule at y 520, the title
        (pn-heading, <= 2 lines) at 192,540, an optional emblem"""
        n = self.text(number, "pn-number", 400, 180); t = self.text(title, "pn-heading", 1300, 160, ' wrap="balance" maxLines="2"')
        uid = self.doc.uid
        out = [self.ink(a, b, 0.35, 0.5), sdk.Xml.of(sdk.new(S.Composition, "layer", fade(a, b), id=uid("cc-n"), asset=n, x=192, y=340)),
               sdk.Xml.of(sdk.new(S.Composition, "shape", fade(a, b), id=uid("cc-r"), shape="rect", width=1536, height=2, x=192, y=520, fill="var(--pn-rule)")),
               sdk.Xml.of(sdk.new(S.Composition, "layer", fade(a + 0.15, b), id=uid("cc-t"), asset=t, x=192, y=540))]
        if emblem:
            out.append(self.emblem(emblem, a + 0.1, b, 1.8))
        return sdk.Xml.of(*out)

    def lower_third_xml(self, a, b, name, role):
        """the kit's lower third: raised panel with an orange bar at 192,680, 900 x 152 (orange is never type here)"""
        nm = self.text(name, "pn-heading", 820, 84, ' maxLines="1"'); rl = self.text(role, "pn-label", 820, 40, ' maxLines="1"')
        gid = self.doc.uid("lt")
        g = sdk.new(S.Composition, "group", fade(a, b), animate("x", [(a, "160", "cubic-out"), (a + 0.4, "192", None)]),
                    id=gid, x=192, y=680, width=900, height=152)
        sdk.adopt(g, sdk.new(g, "shape", id=f"{gid}-p", shape="rect", width=900, height=152, fill="var(--pn-ink-raised)"),
                  sdk.new(g, "shape", id=f"{gid}-b", shape="rect", width=8, height=152, fill="var(--pn-orange)"),
                  sdk.new(g, "layer", id=f"{gid}-n", asset=nm, x=40, y=22), sdk.new(g, "layer", id=f"{gid}-r", asset=rl, x=40, y=98))
        return sdk.Xml.of(g)

    def source_line_xml(self, a, b, text):
        """the citation line (pn-cite, <= 2 lines) at 192,108, top-left inside title safe"""
        s = self.text(text, "pn-cite", 1100, 64, ' maxLines="2"')
        return sdk.Xml.of(sdk.new(S.Composition, "layer", fade(a, b), id=self.doc.uid("sl"), asset=s, x=192, y=108))

    def end_card_xml(self, a, b, credits, next_label=NEXT):
        """the end card over ink: the next-video label at 192,480 and credit lines below it, drifting up slowly;
        the right two thirds stay free for the platform's end-screen elements"""
        uid = self.doc.uid
        nx = self.text(next_label, "pn-label", 1200, 48)
        txt = [sdk.Xml.of(sdk.new(S.Composition, "layer", fade(a + 0.2, b, 0.4, 1.2), id=uid("ec"), asset=nx, x=192, y=480))]
        for i, line in enumerate(credits):
            c = self.text(line, "pn-cite", 620, 36)
            txt.append(sdk.Xml.of(sdk.new(S.Composition, "layer", fade(a + 0.6 + 0.1 * i, b, 0.4, 1.2), id=uid("ec-c"), asset=c, x=192, y=560 + 34 * i)))
        drift = animate("y", [(a, "12", "linear"), (b, "-" + f(5 * (b - a)), None)])
        g = sdk.new(S.Composition, "group", drift, id=uid("ecg"))
        for i, t in enumerate(txt):
            if i:
                sdk.ws(g)
            sdk.adopt(g, t)
        return sdk.Xml.of(self.ink(a, b, 0.8, 1.2), sdk.Xml.of(g), self.notch(a, b))

    # ---------------------------------------------------------------- components (placed above the finish)
    def place(self, xml):
        self.overlays.append(xml); return ""

    def title_card(self, *a, **k):
        return self.place(self.title_card_xml(*a, **k))

    def chapter_card(self, *a, **k):
        return self.place(self.chapter_card_xml(*a, **k))

    def lower_third(self, *a, **k):
        return self.place(self.lower_third_xml(*a, **k))

    def source_line(self, *a, **k):
        return self.place(self.source_line_xml(*a, **k))

    def end_card(self, *a, **k):
        return self.place(self.end_card_xml(*a, **k))
