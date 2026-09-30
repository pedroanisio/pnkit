"""pnkit.captions — caption cues from narration words, as pure functions over [(word, start, end)].

Rules (guide §5 Typography, §13, §14 QA gates):
  - a cue is at most two lines of LINE (42) characters for the long film, SHORT_LINE (26) for a Short's burned track;
  - cues split at sentence ends and at pauses over PAUSE s, then into the fewest two-line cues that fit, preferring
    an even reading rate, breaks after punctuation, and never a break (between cues or lines) after a weak word
    (an article, preposition, auxiliary...) or a stub of one or two words;
  - each cue is shown for at least len(text) / CPS s (16.5 characters/s, inside the guide's 17), taking the extra
    time from the pauses either side, and lingers up to 1 s when a pause allows.

Words carry their written punctuation ("decisions," "odds."); times are seconds on whatever clock the caller uses
(film time for a sidecar, output time for a Short). Nothing here reads files or timelines.
"""
import html, itertools, math, re

__all__ = ["LINE", "SHORT_LINE", "CPS", "MAX_CPS", "PAUSE", "WEAK", "split_units", "split_cues", "two_lines", "timed",
           "cue_xml", "sidecar", "short_cues", "stats"]

LINE, SHORT_LINE = 42, 26         # characters per line: long film, Short
CPS = 16.5                        # display-time rate the timing aims for, characters/s
MAX_CPS = 17                      # the guide's readability limit, characters/s
RATE_SOFT = 16.8                  # cue splitting penalises a part read faster than this
PAUSE = 0.45                      # a pause longer than this ends a unit, like a sentence end
WEAK = frozenset({"the", "a", "an", "of", "that", "are", "is", "to", "for", "and", "or", "if", "in", "with", "its", "it", "on",
                  "as", "at", "by", "from", "this", "these", "was", "were", "be", "been", "has", "have", "no", "not", "so", "than",
                  "when", "which", "does", "do", "can", "will", "would", "should", "into", "about", "more", "own"})


def split_units(words):
    """sentences, and clauses that end at a pause over PAUSE s"""
    units, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        gap = words[i + 1][1] - w[2] if i + 1 < len(words) else 9
        if w[0].endswith((".", "?", "!")) or gap > PAUSE:
            units.append(cur); cur = []
    if cur:
        units.append(cur)
    return units


def split_cues(words, width=LINE, first_end=None, weak=WEAK):
    """[[word, ...] per cue]: each unit split into the fewest two-line cues that fit, balanced by reading rate.
    first_end: the first cue should not end before this time (a Short's cover), a soft rule."""
    units = split_units(words)

    def fits(ws):
        n, ln = 1, 0
        for w in ws:
            add = len(w[0]) + (1 if ln else 0)
            if ln + add > width:
                n, ln = n + 1, len(w[0])
            else:
                ln += add
        return n <= 2

    def rate(ws):
        return len(" ".join(w[0] for w in ws)) / max(0.3, ws[-1][2] - ws[0][1] + 0.5)

    def weak_lines(ws):
        t = " ".join(w[0] for w in ws)
        L = two_lines(t, width, weak)
        return len(L) > 1 and L[0].split()[-1].lower() in weak

    out = []
    for ui, u in enumerate(units):
        if fits(u) and not (weak_lines(u) and len(u) > 5):
            out.append(u); continue
        best = None
        for n in range(2, 9):
            if math.comb(len(u) - 1, n - 1) > 400000:       # too many to try: the greedy balanced split below
                break
            for cuts in itertools.combinations(range(1, len(u)), n - 1):
                parts = [u[a:b] for a, b in zip((0,) + cuts, cuts + (len(u),))]
                if not all(fits(p) for p in parts):
                    continue
                # prefer even reading speed, breaks after punctuation, and never after a function word or a stub
                bad = (sum(p[-1][0].lower().strip(",.") in weak for p in parts[:-1]) + sum(len(p) < 3 for p in parts)
                       + sum(weak_lines(p) for p in parts) + sum((p[-1][2] - p[0][1]) < 1.3 for p in parts))
                score = (max(rate(p) for p in parts) + 2.0 * bad + 8.0 * max(0.0, max(rate(p) for p in parts) - RATE_SOFT)
                         - 0.8 * sum(p[-1][0].endswith((",", ";", ":")) for p in parts[:-1])
                         + (10.0 if first_end is not None and ui == 0 and parts[0][-1][2] < first_end else 0.0))
                if best is None or score < best[0]:
                    best = (score, parts)
            if best:
                break
        if best is None:                                    # balanced by length, as few parts as fit
            n = 2
            while True:
                total = sum(len(w[0]) + 1 for w in u)
                parts, cur, acc = [], [], 0
                for w in u:
                    if cur and acc + len(w[0]) / 2 > total * (len(parts) + 1) / n and len(parts) < n - 1:
                        parts.append(cur); cur = []
                    cur.append(w); acc += len(w[0]) + 1
                parts.append(cur)
                if all(fits(p) for p in parts):
                    break
                n += 1
            best = (0, parts)
        out += best[1]
    return out


def two_lines(text, width, weak=WEAK):
    """the cue's text as at most two lines of `width`, balanced, broken after punctuation when that is close and
    not after a weak word"""
    if len(text) <= width:
        return [text]
    words = text.split(" ")
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) > width or len(b) > width:
            continue
        score = abs(len(a) - len(b)) - (8 if a.endswith((",", ";", ":", ".")) else 0) + (25 if words[i - 1].lower() in weak else 0)
        if best is None or score < best[0]:
            best = (score, [a, b])
    return best[1] if best else [text]


def timed(cues, cps=CPS):
    """[(cue, start, end)]: display windows. Each cue needs len(text)/cps s; beyond its own speech it takes that
    time from the pauses either side (its tail first, then the next cue's lead), and lingers up to 1 s when a pause
    allows."""
    n = len(cues)
    span = [(c[0][1], c[-1][2]) for c in cues]
    need = [max(0.15, len(" ".join(w[0] for w in c)) / cps - (b - a)) for c, (a, b) in zip(cues, span)]
    lead, tail = [0.0] * n, [0.0] * n
    lead[0] = min(0.25, span[0][0])
    for k in range(n):
        g = (span[k + 1][0] - span[k][1] - 0.04) if k + 1 < n else 3.0
        g = max(0.0, g)
        t = min(max(0.0, need[k] - lead[k]), g)
        if k + 1 < n:
            l_ = min(need[k + 1], g - t)
            r = g - t - l_
            t += min(r, max(0.0, 1.0 - t)) * (0.7 if l_ < 0.25 else 1.0)
            lead[k + 1] = min(g - t, max(l_, min(0.25, g - t)))
        else:
            t = max(t, min(g, 1.0))
        tail[k] = t
    return [(c, max(0.0, a - lead[k]), b + tail[k]) for k, (c, (a, b)) in enumerate(zip(cues, span))]


def cue_xml(cues, indent="      ", width=None, weak=WEAK, cps=CPS):
    """<cue> elements with their <word>s; width: break each cue's text into two lines (sidecar), None: one line
    (a burned track lays out its own lines)"""
    xml = []
    for c, start, end in timed(cues, cps):
        text = " ".join(w[0] for w in c)
        body = "\n".join(two_lines(text, width, weak)) if width else text
        ws = "".join(f'<word start="{w[1]:.3f}" end="{w[2]:.3f}" text="{html.escape(w[0], quote=True)}"/>' for w in c)
        xml.append(f'{indent}<cue start="{start:.3f}" end="{end:.3f}" text="{html.escape(body, quote=True).replace(chr(10), "&#10;")}">{ws}</cue>')
    return "\n".join(xml)


def sidecar(words, width=LINE, track_id="subs-en", language="en", label="English", weak=WEAK):
    """the <captions> section with one sidecar track (WebVTT next to the video)"""
    cues = split_cues(words, width, weak=weak)
    return (f'  <captions>\n    <captionTrack id="{track_id}" language="{language}" kind="subtitles" label="{label}" mode="sidecar">\n'
            + cue_xml(cues, width=width, weak=weak) + "\n    </captionTrack>\n  </captions>")


def short_cues(words, spans, not_before=0.0, width=SHORT_LINE, weak=WEAK):
    """the cues of a Short cut from `words`: spans [(from, to, output start)] map the words wholly inside each span to
    output time. No cue shows before `not_before` (the cover card); a first cue that would only flash before the
    cover lifts joins the next one when both fit. -> cue XML in output time"""
    ws = []
    for a, b, o in spans:
        for w, s, e in words:
            if s >= a and e <= b:
                ws.append((w, round(o + s - a, 3), round(o + e - a, 3)))
    cues = split_cues(ws, width, first_end=not_before + 0.8, weak=weak)
    if len(cues) > 1 and cues[0][-1][2] - not_before < 0.7 and len(" ".join(w[0] for w in cues[0] + cues[1])) <= 2 * width:
        cues = [cues[0] + cues[1]] + cues[2:]
    xml = cue_xml(cues, indent="      ", weak=weak)
    first = re.search(r'<cue start="([\d.]+)"', xml)
    if first and float(first.group(1)) < not_before:
        xml = xml.replace(first.group(0), f'<cue start="{not_before:.3f}"', 1)
    return xml


def stats(words, width=LINE, weak=WEAK, cps=CPS, max_cps=MAX_CPS):
    """(cues, cues over max_cps, worst characters/s, longest line) for a sidecar made from `words`"""
    cues = split_cues(words, width, weak=weak)
    rates, longest = [], 0
    for c, a, b in timed(cues, cps):
        text = " ".join(w[0] for w in c)
        rates.append(len(text) / (b - a))
        longest = max(longest, max(len(x) for x in two_lines(text, width, weak)))
    return len(cues), sum(r > max_cps for r in rates), round(max(rates), 1), longest
