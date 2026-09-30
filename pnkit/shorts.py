"""pnkit.shorts — vertical Shorts cut from the film's own document by output segments (SREP 13).

A Short is a list of film spans played at speed 1 through a 1080 x 1920 `fit` layout, consecutive spans joined by
a 0.3 s crossfade, and a last HOOK-second segment (the film's musical close) under the hook card. Its overlay
symbol, in output time, draws:
  - the cover card for the first 0.8 s, so the first frame is the cover (thumbnail.md): ink, the subject in the
    subject band, the notch; the headline sits over it and then rises into the top band;
  - while the picture runs: ink bands above and below the fitted 16:9 picture (y PIC_Y0..PIC_Y1), a 22 px feather
    where the film's vignetted edge meets them, the headline (before / ACCENT / after) and a small notch;
  - the hook for the last HOOK s: a pointer to the long video over ink, with the subject again.
Each Short burns its own caption track in output time (pnkit.captions.short_cues).

The subject drawing is injected: subject(x, y, s, gid) -> XML, placed at cover_at and hook_at (x, y, scale); the
defaults suit a 640 x 400 subject. Timelines are the project's: span_times() takes [(beat key, start, end)].
"""
from .xml import f, esc, keys
from .palette import INK

__all__ = ["OW", "OH", "PIC_Y0", "PIC_Y1", "HOOK", "LAYOUT_ID", "LAYOUT_XML", "span_times", "segments", "feather_paints",
           "overlay", "output_xml", "build"]

OW, OH = 1080, 1920
PIC_Y0, PIC_Y1 = 656, 1264          # where the fitted 16:9 picture lands
HOOK = 2.6                          # the hook segment, s
CROSSFADE = 0.3                     # between consecutive spans, s
LAYOUT_ID = "short-9x16"
LAYOUT_XML = f'    <layout id="{LAYOUT_ID}" width="{OW}" height="{OH}" aspect="9:16" reframe="fit"/>\n'
HOOK_KICKER = "THE FULL VIDEO"
HOOK_CTA = "ON PALS'S NOTES · LINKED BELOW"


def span_times(beats, b0, b1, pre=0.72, post=0.45):
    """the film span for beats b0..b1 of beats [(key, start, end)] (film order): from `pre` s before the first word
    (inside the pause before it) to `post` s after the last word, both checked against the neighbouring beats"""
    keys_ = [b[0] for b in beats]
    i0, i1 = keys_.index(b0), keys_.index(b1)
    start, end = beats[i0][1] - pre, beats[i1][2] + post
    if i0 > 0:
        assert start > beats[i0 - 1][2] + 0.05, (b0, "starts inside the previous line")
    if i1 + 1 < len(beats):
        assert end < beats[i1 + 1][1] - 0.1, (b1, "ends inside the next line")
    return round(start, 3), round(end, 3)


def segments(segs, crossfade=CROSSFADE):
    """segs [(from, to)] -> ([<segment> lines], maps [(from, to, output start)], total duration)"""
    o, maps, lines = 0.0, [], []
    for i, (a, b) in enumerate(segs):
        maps.append((a, b, o))
        tr = f'<transition type="crossfade" duration="{f(crossfade)}"/>' if i + 1 < len(segs) else ""
        lines.append(f'    <segment from="{f(a)}" to="{f(b)}">{tr}</segment>')
        o += b - a
    return lines, maps, o


def feather_paints(ink=INK):
    """the two gradients the overlay's feathers use (pt-feather-down, pt-feather-up)"""
    return [f'<linearGradient id="pt-feather-down" x1="0" y1="0" x2="0" y2="1"><stop offset="0" color="{ink}FF"/><stop offset="1" color="{ink}00"/></linearGradient>',
            f'<linearGradient id="pt-feather-up" x1="0" y1="0" x2="0" y2="1"><stop offset="0" color="{ink}00"/><stop offset="1" color="{ink}FF"/></linearGradient>']


def _headline(aid, height, size, lines, before, accent, after):
    return (f'<text id="{aid}" width="920" height="{height}" size="{size}" style="pn-cover-headline" verticalAlign="bottom" wrap="balance" maxLines="{lines}">'
            f'<span style="pn-cover-headline" color="var(--pn-cream)">{esc(before)}</span><span style="pn-cover-accent" color="var(--pn-orange)">{esc(accent)}</span>'
            f'<span style="pn-cover-headline" color="var(--pn-cream)">{esc(after)}</span></text>')


def overlay(doc, sid, T, head, subject, hook_title, hook_kicker=HOOK_KICKER, hook_cta=HOOK_CTA, cover_at=(100, 760, 1.3),
            hook_at=(210, 1000, 1.0), hook=HOOK):
    """the overlay <symbol id="ov-<sid>"> of a Short T s long. head: (before, accent, after) headline words;
    hook_title: (words, accent) of the long video's title. Registers its text assets in doc.assets."""
    before, accent, after = head
    out = []
    # the cover card, first 0.8 s: ink, the subject band (the subject), the notch
    cover = [f'<shape id="{sid}-cv-bg" shape="rect" width="{OW}" height="{OH}" fill="var(--pn-ink)"/>',
             subject(cover_at[0], cover_at[1], cover_at[2], f"{sid}-cv-card"),
             f'<shape id="{sid}-cv-n" shape="path" x="80" y="1336" width="64" height="64" path="M0 0 L0 64 L64 64 Z" fill="var(--pn-orange)"/>']
    # running: ink above and below the picture, the headline in the top band
    aid2 = doc.uid(f"hs-{sid}")
    doc.assets.append(_headline(aid2, 300, 118, 2, before, accent, after))
    out.append(f'<shape id="{sid}-top" shape="rect" width="{OW}" height="{PIC_Y0}" fill="var(--pn-ink)"/>')
    out.append(f'<shape id="{sid}-bot" shape="rect" y="{PIC_Y1}" width="{OW}" height="{OH - PIC_Y1}" fill="var(--pn-ink)"/>')
    # the film's vignetted edge meets the bands' ink: a short feather hides the seam
    out.append(f'<shape id="{sid}-ft" shape="rect" y="{PIC_Y0}" width="{OW}" height="22" fill="url(#pt-feather-down)"/>')
    out.append(f'<shape id="{sid}-fb" shape="rect" y="{PIC_Y1 - 22}" width="{OW}" height="22" fill="url(#pt-feather-up)"/>')
    out.append(f'<shape id="{sid}-n" shape="path" x="80" y="600" width="40" height="40" path="M0 0 L0 40 L40 40 Z" fill="var(--pn-orange)"/>')
    out.append(f'<group id="{sid}-cover">' + keys("opacity", [(0, 1, "hold"), (0.8, 1, "cubic-in"), (1.05, 0)]) + cover[0]
               + f'<group id="{sid}-cv-fg">' + keys("opacity", [(0, 1, "hold"), (0.5, 1, "cubic-in"), (0.78, 0)]) + "".join(cover[1:]) + "</group></group>")
    # the same headline over the cover and above the picture: it rises from the cover's headline band into the top band
    out.append(f'<layer id="{sid}-head" asset="{aid2}" x="80" y="390">' + keys("y", [(0, 390, "hold"), (0.8, 390, "cubic-in-out"), (1.15, 290)])
               + keys("opacity", [(0, 1, "hold"), (T - hook - 0.1, 1, "cubic-in"), (T - hook + 0.2, 0)]) + "</layer>")
    # the hook, last `hook` s: a pointer to the long video
    k1, k2, k3 = doc.uid(f"hk1-{sid}"), doc.uid(f"hk2-{sid}"), doc.uid(f"hk3-{sid}")
    doc.assets.append(f'<text id="{k1}" text="{esc(hook_kicker)}" width="920" height="60" size="44" style="pn-label" color="var(--pn-cream-muted)" tracking="120"/>')
    doc.assets.append(f'<text id="{k2}" width="920" height="380" size="150" style="pn-display" wrap="balance" maxLines="2">'
                      f'<span color="var(--pn-cream)">{esc(hook_title[0])}</span><span color="var(--pn-orange)">{esc(hook_title[1])}</span></text>')
    doc.assets.append(f'<text id="{k3}" text="{esc(hook_cta)}" width="920" height="60" size="40" style="pn-label" color="var(--pn-cream-muted)" tracking="80"/>')
    ta = T - hook
    hk = [f'<shape id="{sid}-hk-bg" shape="rect" width="{OW}" height="{OH}" fill="var(--pn-ink)"/>',
          f'<layer id="{sid}-hk1" asset="{k1}" x="80" y="430"/>',
          f'<layer id="{sid}-hk2" asset="{k2}" x="80" y="500">' + keys("y", [(ta, 540, "cubic-out"), (ta + 0.5, 500)]) + "</layer>",
          f'<layer id="{sid}-hk3" asset="{k3}" x="80" y="880"/>',
          subject(hook_at[0], hook_at[1], hook_at[2], f"{sid}-hk-card"),
          f'<shape id="{sid}-hk-n" shape="path" x="80" y="1336" width="64" height="64" path="M0 0 L0 64 L64 64 Z" fill="var(--pn-orange)"/>']
    out.append(f'<group id="{sid}-hook" opacity="0">' + keys("opacity", [(ta, 0, "cubic-out"), (ta + 0.35, 1)]) + "".join(hk) + "</group>")
    return f'    <symbol id="ov-{sid}" width="{OW}" height="{OH}" duration="{f(round(T, 3))}">\n' + "\n".join(out) + "\n    </symbol>\n"


def output_xml(sid, slug, segment_lines, cues, caption_style, active_style, out_dir="out/shorts", language="en", label="English",
               codec='codec="h264" crf="18" preset="slow"'):
    """the Short's <output>: its segments, its cover thumbnail (t 0.2 s) and its burned active-word caption track
    (2 x 26 characters, centred at 67.4 % of the height)"""
    return (f'  <output id="{sid}" path="{out_dir}/{sid}-{slug}.mp4" {codec} layout="{LAYOUT_ID}" '
            f'overlay="ov-{sid}" burnCaptions="cap-{sid}" captions="cap-{sid}" joinFade="0.05">\n'
            f'    <thumbnail path="{out_dir}/{sid}-{slug}-cover.png" format="png" time="0.2" width="1080"/>\n'
            + "\n".join(segment_lines) + "\n"
            f'    <captionTrack id="cap-{sid}" language="{language}" kind="captions" label="{label}" mode="burn" preset="highlight" style="{caption_style}" '
            f'activeStyle="{active_style}" maxCharsPerLine="26" maxLines="2" x="50%" y="67.4%" width="90%">\n{cues}\n    </captionTrack>\n'
            f'  </output>')


def build(doc, shorts, segs_of, cues_of, overlay_of, caption_style, active_style):
    """all Shorts of a document. shorts: [(id, slug, spans, head)]; segs_of(spans) -> [(from, to)] with the hook
    segment last; cues_of(maps) -> cue XML for the spoken segments' maps [(from, to, output start)] (the hook
    carries no captions); overlay_of(id, T, head) -> the overlay symbol (usually a partial of overlay()).
    Adds the feather paints to doc.paints. -> (outputs XML, symbols XML, layouts XML)"""
    doc.paints.extend(feather_paints())
    outputs, symbols = [], []
    for sid, slug, spans, head in shorts:
        lines, maps, T = segments(segs_of(spans))
        outputs.append(output_xml(sid, slug, lines, cues_of(maps[:-1]), caption_style, active_style))
        symbols.append(overlay_of(sid, T, head))
    return "\n".join(outputs), "".join(symbols), LAYOUT_XML
