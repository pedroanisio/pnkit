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
import hashlib, re
from .xml import f, esc

__all__ = ["MOTION_IN", "MOTION_OUT", "NOTCH", "SIZES", "COLOURS", "prologue", "extend", "kit_sha256", "fade", "Brand"]

MOTION_IN, MOTION_OUT = 0.40, 0.30          # pn:motion-in cubic-out, pn:motion-out cubic-in
NOTCH = 64                                  # the brand mark, px at 1080p
SIZES = {"pn-label": 28, "pn-display": 120, "pn-number": 160, "pn-heading": 64, "pn-cite": 24}
COLOURS = {"pn-label": "var(--pn-cream-muted)", "pn-display": "var(--pn-cream)", "pn-number": "var(--pn-orange)",
           "pn-heading": "var(--pn-cream)", "pn-cite": "var(--pn-cream-muted)"}
NEXT = "NEXT ON PALS'S NOTES"               # the kit's pn-next default (English)


def _block(src, tag):
    m = re.search(rf"\n  <{tag}[ >].*?\n  </{tag}>", src, re.S)
    return m.group(0).strip("\n") if m else ""


def prologue(kit_path, params):
    """the kit's sections, verbatim except the parameter defaults in `params` ({param id: value}; each must exist
    exactly once). -> {parameters, styles, layouts, safeAreas, symbols: section XML; font: the font asset;
    texts: [the kit's text assets]; accessibility: the kit's accessibility element}"""
    src = open(kit_path, encoding="utf-8").read()
    pars = _block(src, "parameters")
    for pid, val in params.items():
        pars, n = re.subn(rf'(<param id="{pid}"[^>]*?default=")[^"]*(")', lambda m: m.group(1) + esc(val) + m.group(2), pars)
        if n != 1:
            raise KeyError(f"kit parameter {pid!r} found {n} times in {kit_path}")
    assets = _block(src, "assets")
    font = re.search(r'<font id="pn-archivo".*?/>', assets, re.S).group(0)
    texts = re.findall(r'<text id="pn-t-[^"]+".*?(?:/>|</text>)', assets, re.S)
    access = re.search(r"<accessibility [^>]*/>", src).group(0)
    return {"parameters": pars, "styles": _block(src, "styles"), "layouts": _block(src, "layouts"),
            "safeAreas": _block(src, "safeAreas"), "symbols": _block(src, "symbols"), "font": font, "texts": texts,
            "accessibility": access}


def extend(block, tag, xml):
    """a prologue section with `xml` added before its closing tag (e.g. the episode's own text styles)"""
    return block.replace(f"  </{tag}>", xml + f"  </{tag}>")


def kit_sha256(kit_path):
    """the kit file's SHA-256, to compare with the pin a project keeps next to its copy"""
    return hashlib.sha256(open(kit_path, "rb").read()).hexdigest()


def fade(a, b, fin=MOTION_IN, fout=MOTION_OUT):
    """the kit's opacity motion: in over fin (cubic-out), out over fout (cubic-in); b is pushed out so both fit"""
    b = max(b, a + fin + fout)
    return (f'<animate property="opacity"><key time="{f(a)}" value="0" interpolation="cubic-out"/><key time="{f(a + fin)}" value="1"/>'
            f'<key time="{f(b - fout)}" value="1" interpolation="cubic-in"/><key time="{f(b)}" value="0"/></animate>')


class Brand:
    """The kit's components for one document. doc: the pnkit Doc (ids, frame size)."""

    def __init__(self, doc):
        self.doc = doc
        self.assets = []       # brand text assets made for this document
        self.overlays = []     # placed components, to write above the finish

    # ---------------------------------------------------------------- pieces
    def text(self, txt, style, width, height, extra=""):
        """a brand text asset at the kit's size for `style`, coloured explicitly -> asset id"""
        aid = self.doc.uid("bt")
        if "color=" not in extra:
            extra = f' color="{COLOURS[style]}"' + extra
        self.assets.append(f'<text id="{aid}" text="{esc(txt)}" width="{width}" height="{height}" size="{SIZES[style]}" style="{style}"{extra}/>')
        return aid

    def notch(self, a, b, x=0, y=None):
        """the brand mark (orange right triangle), bottom-left by default"""
        y = self.doc.height - NOTCH if y is None else y
        return (f'<shape id="{self.doc.uid("notch")}" shape="path" x="{x}" y="{y}" width="{NOTCH}" height="{NOTCH}" path="M0 0 L0 {NOTCH} L{NOTCH} {NOTCH} Z" '
                f'fill="var(--pn-orange)" tags="logo">{fade(a, b)}</shape>')

    def ink(self, a, b, fin=0.5, fout=0.6):
        """a full-frame ink field"""
        return f'<shape id="{self.doc.uid("ink")}" shape="rect" width="{self.doc.width}" height="{self.doc.height}" fill="var(--pn-ink)">{fade(a, b, fin, fout)}</shape>'

    def emblem(self, items, a, b, dur=1.6):
        """a line-drawn subject: items [(path d, colour, width[, fill])]; each stroke draws on in turn (trimEnd), then
        fades with the card; the whole emblem drifts left 12 px/s, so the card never holds a frozen frame"""
        W, H = self.doc.width, self.doc.height
        out, n = [], max(1, len(items))
        for i, it in enumerate(items):
            d, col, w = it[:3]; fill = it[3] if len(it) > 3 else "#00000000"
            t0 = a + 0.25 + (dur - 0.6) * i / n
            out.append(f'<shape id="{self.doc.uid("em")}" shape="path" width="{W}" height="{H}" path="{d}" fill="{fill}" stroke="{col}" strokeWidth="{w}" '
                       f'strokeCap="round" strokeJoin="round" trimEnd="0"><animate property="trimEnd"><key time="{f(t0)}" value="0" interpolation="cubic-out"/>'
                       f'<key time="{f(t0 + 0.7)}" value="1"/></animate>{fade(a, b, 0.2, MOTION_OUT)}</shape>')
        drift = (f'<animate property="x"><key time="{f(a)}" value="0" interpolation="linear"/><key time="{f(b)}" value="-{f(12 * (b - a))}"/></animate>')
        return f'<group id="{self.doc.uid("emg")}">{drift}' + "\n".join(out) + "</group>"

    # ---------------------------------------------------------------- components (XML)
    def title_card_xml(self, a, b, kicker, title, emblem=None):
        """the opening title over ink: kicker (pn-label) at 192,300, title (pn-display, balanced, <= 3 lines) rising
        into 192,360, an optional emblem (items for emblem()), the notch"""
        k = self.text(kicker, "pn-label", 1200, 48); t = self.text(title, "pn-display", 1400, 360, ' wrap="balance" maxLines="3"')
        uid = self.doc.uid
        out = [self.ink(a, b), f'<layer id="{uid("tc-k")}" asset="{k}" x="192" y="300">{fade(a, b)}</layer>',
               f'<layer id="{uid("tc-t")}" asset="{t}" x="192" y="360">{fade(a + 0.1, b)}'
               f'<animate property="y"><key time="{f(a + 0.1)}" value="392" interpolation="cubic-out"/><key time="{f(a + 0.5)}" value="360"/></animate></layer>']
        if emblem:
            out.append(self.emblem(emblem, a + 0.2, b, 2.0))
        out.append(self.notch(a, b))
        return "\n".join(out)

    def chapter_card_xml(self, a, b, number, title, emblem=None):
        """a chapter divider over ink: the number (pn-number, orange) at 192,340, a rule at y 520, the title
        (pn-heading, <= 2 lines) at 192,540, an optional emblem"""
        n = self.text(number, "pn-number", 400, 180); t = self.text(title, "pn-heading", 1300, 160, ' wrap="balance" maxLines="2"')
        uid = self.doc.uid
        out = [self.ink(a, b, 0.35, 0.5), f'<layer id="{uid("cc-n")}" asset="{n}" x="192" y="340">{fade(a, b)}</layer>',
               f'<shape id="{uid("cc-r")}" shape="rect" width="1536" height="2" x="192" y="520" fill="var(--pn-rule)">{fade(a, b)}</shape>',
               f'<layer id="{uid("cc-t")}" asset="{t}" x="192" y="540">{fade(a + 0.15, b)}</layer>']
        if emblem:
            out.append(self.emblem(emblem, a + 0.1, b, 1.8))
        return "\n".join(out)

    def lower_third_xml(self, a, b, name, role):
        """the kit's lower third: raised panel with an orange bar at 192,680, 900 x 152 (orange is never type here)"""
        nm = self.text(name, "pn-heading", 820, 84, ' maxLines="1"'); rl = self.text(role, "pn-label", 820, 40, ' maxLines="1"')
        gid = self.doc.uid("lt")
        return (f'<group id="{gid}" x="192" y="680" width="900" height="152">{fade(a, b)}'
                f'<animate property="x"><key time="{f(a)}" value="160" interpolation="cubic-out"/><key time="{f(a + 0.4)}" value="192"/></animate>'
                f'<shape id="{gid}-p" shape="rect" width="900" height="152" fill="var(--pn-ink-raised)"/>'
                f'<shape id="{gid}-b" shape="rect" width="8" height="152" fill="var(--pn-orange)"/>'
                f'<layer id="{gid}-n" asset="{nm}" x="40" y="22"/><layer id="{gid}-r" asset="{rl}" x="40" y="98"/></group>')

    def source_line_xml(self, a, b, text):
        """the citation line (pn-cite, <= 2 lines) at 192,108, top-left inside title safe"""
        s = self.text(text, "pn-cite", 1100, 64, ' maxLines="2"')
        return f'<layer id="{self.doc.uid("sl")}" asset="{s}" x="192" y="108">{fade(a, b)}</layer>'

    def end_card_xml(self, a, b, credits, next_label=NEXT):
        """the end card over ink: the next-video label at 192,480 and credit lines below it, drifting up slowly;
        the right two thirds stay free for the platform's end-screen elements"""
        uid = self.doc.uid
        nx = self.text(next_label, "pn-label", 1200, 48)
        txt = [f'<layer id="{uid("ec")}" asset="{nx}" x="192" y="480">{fade(a + 0.2, b, 0.4, 1.2)}</layer>']
        for i, line in enumerate(credits):
            c = self.text(line, "pn-cite", 620, 36)
            txt.append(f'<layer id="{uid("ec-c")}" asset="{c}" x="192" y="{560 + 34 * i}">{fade(a + 0.6 + 0.1 * i, b, 0.4, 1.2)}</layer>')
        drift = f'<animate property="y"><key time="{f(a)}" value="12" interpolation="linear"/><key time="{f(b)}" value="-{f(5 * (b - a))}"/></animate>'
        return "\n".join([self.ink(a, b, 0.8, 1.2), f'<group id="{uid("ecg")}">{drift}' + "\n".join(txt) + "</group>", self.notch(a, b)])

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
