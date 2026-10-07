"""pnkit.captions — caption cues from narration words, as pure functions over [(word, start, end)].

Rules (guide §5 Typography, §13, §14 QA gates):
  - a cue is at most two lines of LINE (42) characters for the long film, SHORT_LINE (26) for a Short's burned track;
  - cues split at sentence ends and at pauses over PAUSE s, then into the fewest two-line cues that fit, preferring
    an even reading rate and breaks after punctuation;
  - no break, between cues or between lines, after a weak word (an article, preposition, auxiliary, possessive...),
    inside a number ("one in ten", "twenty thousand", "three times in ten", "75 per cent") or inside a name
    ("Apollo 12", "New Horizons"): no_break() lists those places, and they are used only when no other break fits;
  - one function, line_break(), decides whether a cue fits two lines and where its line breaks, so a cue is shown
    with the break it was accepted with;
  - each cue is shown for at least len(text) / CPS s (16.5 characters/s, inside the guide's 17) and never under
    MIN_SHOW s. The extra time comes from the cue's own tail first (it is held after its last word, up to HOLD s
    and never into the next cue), then from a lead before its first word, never more than LEAD s (FIRST_LEAD s for
    the first cue of the film): a caption does not run ahead of the voice. A cue that still cannot be shown long
    enough ("No." before the next sentence, a long cue said fast) joins a neighbour.

Captions show the WRITTEN text ("12,4%"), the voice says the SPOKEN one ("doze vírgula quatro por cento"):
written_words() puts the written tokens on the spoken words' times through vo.speak_map (and raises
CaptionAlignError when they do not align), and check_text() holds the finished cues to the approved written text.

Words carry their written punctuation ("decisions," "odds."); times are seconds on whatever clock the caller uses
(film time for a sidecar, output time for a Short). Nothing here reads files or timelines.
"""
import difflib, html, itertools, math, re, unicodedata
from dataclasses import dataclass

__all__ = ["LINE", "SHORT_LINE", "CPS", "MAX_CPS", "MIN_SHOW", "LEAD", "FIRST_LEAD", "HOLD", "PAUSE", "WEAK", "NUMBERS", "NUM_TAIL", "is_number",
           "no_break", "line_break", "split_units", "split_cues", "two_lines", "timed", "cue_xml", "sidecar",
           "short_cues", "stats", "CaptionAlignError", "written_words", "Finding", "check_text"]

LINE, SHORT_LINE = 42, 26         # characters per line: long film, Short
CPS = 16.5                        # display-time rate the timing aims for, characters/s
MAX_CPS = 17                      # the guide's readability limit, characters/s
RATE_SOFT = 16.8                  # cue splitting penalises a part read faster than this
MIN_SHOW = 1.0                    # no cue is shown for less than this, s
LEAD = 0.30                       # no cue starts more than this before its first word, s
FIRST_LEAD = 0.35                 # the same for the first cue of the film, s
HOLD = 1.0                        # a cue is held at most this long after its last word, s
PAUSE = 0.45                      # a pause longer than this ends a unit, like a sentence end
FAULT = 50.0                      # cue splitting: the cost of one break where none may fall, of one cue too short or too fast
WEAK = frozenset({"the", "a", "an", "of", "that", "are", "is", "to", "for", "and", "or", "if", "in", "with", "its", "it", "on",
                  "as", "at", "by", "from", "this", "these", "was", "were", "be", "been", "has", "have", "no", "not", "so", "than",
                  "when", "which", "does", "do", "can", "will", "would", "should", "into", "about", "more", "own",
                  "what", "how", "where", "who", "while", "because", "there", "here", "per", "our", "your", "their", "his", "her",
                  "my", "you", "we", "they", "but", "then", "after", "before"})
NUMBERS = frozenset("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
                    "seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand "
                    "million billion trillion half".split())
NUM_TAIL = frozenset({"in", "out", "of", "per", "cent", "percent", "%", "times"})   # what ties a number to the next one
_END = (".", "?", "!")            # a sentence ends
_STOP = _END + (";", ":")         # after these a break is always allowed
_PUNCT = ".,;:?!\"'"


def is_number(token):
    """a number as it is written: digits (1982, 3.8, 95%, 12-km), number words (twenty, ninety-five, half), and the
    per / cent / percent that belong to one"""
    t = token.lower().strip(_PUNCT + "()%").replace("\u2013", "-")
    if re.fullmatch(r"\d[\d,.\-]*[%a-z]*", t):
        return True
    parts = t.split("-")
    return any(p in NUMBERS for p in parts) and all(p in NUMBERS or p == "" for p in parts) or t in ("per", "cent", "percent")


def no_break(tokens, weak=WEAK, start=True):
    """{i}: the places where no break may fall between tokens[i - 1] and tokens[i], for cues and for lines alike:
      - after a weak word;
      - inside a number: between a number and the number, or the in / out / of / per / cent / percent / times,
        that follows it ("twenty thousand", "75 per cent"), and anywhere between two numbers joined by those words
        ("one in ten", "three times in ten");
      - inside a name: a capitalised word and the capitalised word or the digit that follows it. A word that only
        opens a sentence is no name ("Then Newton"), unless a digit follows ("Apollo 12").
    A token that ends in . ? ! ; : frees the break after it. start: tokens[0] opens a sentence."""
    out, n = set(), len(tokens)
    bare = [t.lower().strip(_PUNCT) for t in tokens]
    num = [is_number(t) for t in tokens]
    free = [t.endswith(_STOP) for t in tokens]
    for i in range(1, n):
        a, b = tokens[i - 1], tokens[i]
        if free[i - 1]:
            continue
        if bare[i - 1] in weak or num[i - 1] and (num[i] or bare[i] in NUM_TAIL):
            out.add(i)
        opens = start if i == 1 else tokens[i - 2].endswith(_END)
        if a[:1].isupper() and a != "I" and not a.endswith(",") and (b[:1].isdigit() or b[:1].isupper() and not opens):
            out.add(i)
    for j in range(n):                                      # a number, its joining words, the next number: one run
        if not num[j]:
            continue
        k = j + 1
        while k < n and bare[k] in NUM_TAIL and not free[k - 1]:
            k += 1
        if j + 1 < k < n and num[k] and not free[k - 1]:
            out.update(range(j + 1, k + 1))
    return out


def line_break(tokens, width, weak=WEAK, start=True):
    """(lines, legal) for a cue's words, or None when they do not fit two lines of `width`. The break is the most
    balanced one that no_break() allows, nearer punctuation when that is close; legal is False when every break
    that fits is one no_break() forbids, and the most balanced of those is used. Both split_cues (does this cue
    fit, is its break a good one) and two_lines (what is shown) come here."""
    text = " ".join(tokens)
    if len(text) <= width:
        return [text], True
    if len(text) > 2 * width + 1:
        return None
    stuck, best = no_break(tokens, weak, start), None
    for i in range(1, len(tokens)):
        a, b = " ".join(tokens[:i]), " ".join(tokens[i:])
        if len(a) > width or len(b) > width:
            continue
        score = (1000 if i in stuck else 0) + abs(len(a) - len(b)) - (8 if a.endswith((",",) + _STOP) else 0)
        if best is None or score < best[0]:
            best = (score, [a, b], i not in stuck)
    return best and (best[1], best[2])


def _opens(cues, k):
    """does cue k open a sentence"""
    return k == 0 or cues[k - 1][-1][0].endswith(_END)


def split_units(words):
    """sentences, and clauses that end at a pause over PAUSE s"""
    units, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        gap = words[i + 1][1] - w[2] if i + 1 < len(words) else 9
        if w[0].endswith(_END) or gap > PAUSE:
            units.append(cur); cur = []
    if cur:
        units.append(cur)
    return units


def split_cues(words, width=LINE, first_end=None, weak=WEAK, min_show=MIN_SHOW):
    """[[word, ...] per cue]: each unit split into the fewest two-line cues that fit with every break (between cues
    and between lines) where no_break() allows one and every cue on screen for min_show s, balanced by reading
    rate; then a cue the pauses cannot hold for min_show s joins a neighbour (_mend), so a cue may span a sentence
    end.
    first_end: the first cue should not end before this time (a Short's cover), a soft rule."""
    units = split_units(words)
    out = []
    for ui, u in enumerate(units):
        toks = [w[0] for w in u]
        opens = ui == 0 or units[ui - 1][-1][0].endswith(_END)
        stuck = no_break(toks, weak, opens)
        after = units[ui + 1][0][1] if ui + 1 < len(units) else u[-1][2] + 3.0
        if ui == 0:                                         # the lead timed() can give the unit's first cue
            early = min(FIRST_LEAD, u[0][1])
        else:                                               # the pause before it, less what the cue before needs of it
            q = out[-1]; said = q[-1][2] - q[0][1]
            early = min(LEAD, max(0.0, u[0][1] - q[-1][2] - 0.04 - max(0.15, len(" ".join(w[0] for w in q)) / CPS - said, min_show - said)))
        memo = {}

        def part(a, b):
            """u[a:b] as one cue: None when it does not fit, else (rate, faults, soft faults). Its faults: a line
            break where none may fall, under min_show s on screen, and (the limit, so it counts three times) over
            MAX_CPS however long it is shown"""
            if (a, b) not in memo:
                p, L = u[a:b], line_break(toks[a:b], width, weak, opens and a == 0)
                if L is None:
                    memo[a, b] = None
                else:
                    chars = len(" ".join(toks[a:b]))
                    room = min((u[b][1] if b < len(u) else after) - 0.04, p[-1][2] + HOLD) - p[0][1]   # the longest it can be shown
                    lead = early if a == 0 else 0.0
                    fast = chars / max(0.1, room + lead) > MAX_CPS
                    memo[a, b] = (chars / max(0.3, p[-1][2] - p[0][1] + 0.5), (not L[1]) + (room + min(lead, 0.15) < min_show) + 3 * fast,
                                  (b - a < 3) + (p[-1][2] - p[0][1] < 1.3))
            return memo[a, b]

        def search(places, n):
            """the best split into n cues cut at `places`: (score, faults, parts), or None when none fits"""
            best = None
            for cuts in itertools.combinations(places, n - 1):
                edges = (0,) + cuts + (len(u),)
                ps = [part(a, b) for a, b in zip(edges, edges[1:])]
                if None in ps:
                    continue
                # prefer even reading speed and breaks after punctuation; never a break after a weak word, inside a
                # number or a name, a cue under min_show s, or (softer) a stub
                top = max(p[0] for p in ps)
                faults = sum(p[1] for p in ps) + sum(c in stuck for c in cuts)
                score = (top + FAULT * faults + (2.0 * sum(p[2] for p in ps) if n > 1 else 0.0) + 8.0 * max(0.0, top - RATE_SOFT)
                         - 0.8 * sum(toks[c - 1].endswith((",", ";", ":")) for c in cuts)
                         + (10.0 if first_end is not None and ui == 0 and u[edges[1] - 1][2] < first_end else 0.0))
                if best is None or score < best[0]:
                    best = (score, faults, [u[a:b] for a, b in zip(edges, edges[1:])])
            return best

        legal, every = [i for i in range(1, len(u)) if i not in stuck], range(1, len(u))
        best = least = None                                 # least: the fewest cues that fit at all
        for n in range(1, min(len(u), 12) + 1):
            if math.comb(len(legal), n - 1) > 400000 or least is not None and n > least + 2:
                break
            got = search(legal, n)                          # first with legal cuts only, a cue more if that is the price
            if least is None and (got or (math.comb(len(u) - 1, n - 1) <= 400000 and search(every, n))):
                least = n
            if got and (best is None or got[0] < best[0]):
                best = got
            if got and not got[1]:
                break
        if (best is None or best[1]) and least is not None:   # no faultless split: the least bad of any cuts
            got = search(every, least)
            if got and (best is None or got[0] < best[0]):
                best = got
        if best is None:                                    # too many to try: balanced by length, as few parts as fit
            n = 2
            while True:
                total = sum(len(w[0]) + 1 for w in u)
                parts, cur, acc = [], [], 0
                for w in u:
                    if cur and acc + len(w[0]) / 2 > total * (len(parts) + 1) / n and len(parts) < n - 1:
                        parts.append(cur); cur = []
                    cur.append(w); acc += len(w[0]) + 1
                parts.append(cur)
                if all(line_break([w[0] for w in p], width, weak) for p in parts):
                    break
                n += 1
            best = (0, 0, parts)
        out += best[2]
    return _mend(out, width, weak, min_show)


def _mend(cues, width, weak, min_show):
    """a cue that timed() cannot show for min_show s, or under MAX_CPS, is cut again together with its two
    neighbours, into as many cues or fewer: it joins the one it belongs with (the smallest pause first) or the cuts
    move, whichever leaves the fewest faults; a cue may then span a sentence end ("No. Before the test, ...")"""
    def text(c):
        return " ".join(w[0] for w in c)

    def faults(trial, lo, n, stuck=(), cuts=()):
        tl, bad = timed(trial, min_show=min_show), sum(c in stuck for c in cuts)
        for k in range(lo, lo + n):
            c, a, b = tl[k]
            L = line_break([w[0] for w in c], width, weak, _opens(trial, k))
            if L is None:
                return None
            bad += (not L[1]) + (b - a < min_show - 1e-6) + 3 * (len(text(c)) / max(0.1, b - a) > MAX_CPS)
        return bad

    left = set()                                            # cues nothing can be done for
    for _ in range(4 * len(cues)):
        tl = timed(cues, min_show=min_show)
        k = next((k for k, (c, a, b) in enumerate(tl) if c[0] not in left
                  and (b - a < min_show - 1e-6 or len(text(c)) / max(0.1, b - a) > MAX_CPS)), None)
        if k is None:
            break
        lo, hi = max(0, k - 1), min(len(cues), k + 2)
        W = [w for c in cues[lo:hi] for w in c]
        toks = [w[0] for w in W]
        stuck = no_break(toks, weak, _opens(cues, lo))
        now = [len(c) for c in cues[lo:hi]]
        was, best = faults(cues, lo, hi - lo, stuck, list(itertools.accumulate(now))[:-1]), None
        for n in range(1, hi - lo + 1):
            for cuts in itertools.combinations(range(1, len(W)), n - 1):
                edges = (0,) + cuts + (len(W),)
                if any(len(" ".join(toks[a:b])) > 2 * width + 1 for a, b in zip(edges, edges[1:])):
                    continue
                trial = cues[:lo] + [W[a:b] for a, b in zip(edges, edges[1:])] + cues[hi:]
                bad = faults(trial, lo, n, stuck, cuts)
                if bad is None:
                    continue
                inside = [i for i in range(1, len(W)) if toks[i - 1].endswith(_END) and i not in cuts]
                rank = (bad, len(inside), sum(not toks[c - 1].endswith((",",) + _STOP) for c in cuts),
                        sum(W[i][1] - W[i - 1][2] for i in inside), n,
                        max(len(" ".join(toks[a:b])) for a, b in zip(edges, edges[1:])))
                if bad < was and (best is None or rank < best[0]):
                    best = (rank, trial)
        if best is None:
            left.add(cues[k][0])
        else:
            cues = best[1]
    return cues


def two_lines(text, width, weak=WEAK, start=True):
    """the cue's text as at most two lines of `width`: line_break()'s break (balanced, after punctuation when that is
    close, never after a weak word or inside a number or a name while another break fits). start: the text opens a
    sentence, so its first word's capital is no name."""
    L = line_break(text.split(" "), width, weak, start)
    return L[0] if L else [text]


def timed(cues, cps=CPS, min_show=MIN_SHOW):
    """[(cue, start, end)]: display windows. Each cue needs len(text)/cps s and at least min_show s; beyond its own
    speech it takes that time from its tail first (held after its last word, up to HOLD s and never into the next
    cue), and only what the tail cannot give from a lead before its first word. No cue starts more than LEAD s
    before its first word (FIRST_LEAD s for the first cue), whatever it needs: when lead and tail together are not
    enough split_cues joins it to a neighbour. A cue lingers up to HOLD s when a pause allows."""
    n = len(cues)
    span = [(c[0][1], c[-1][2]) for c in cues]
    need = [max(0.15, len(" ".join(w[0] for w in c)) / cps - (b - a), min_show - (b - a)) for c, (a, b) in zip(cues, span)]
    gap = [max(0.0, span[k + 1][0] - span[k][1] - 0.04) if k + 1 < n else 3.0 for k in range(n)]
    short = [max(0.0, nd - min(g, HOLD)) for nd, g in zip(need, gap)]         # what a cue's own tail cannot give it
    lead, tail = [0.0] * n, [0.0] * n
    lead[0] = min(max(0.25, min(short[0], FIRST_LEAD)), span[0][0])
    for k in range(n):
        g = gap[k]
        t = min(max(0.0, need[k] - lead[k]), g, HOLD)
        if k + 1 < n:
            l_ = min(short[k + 1], g - t, LEAD)
            r = g - t - l_
            t += min(r, max(0.0, HOLD - t)) * (0.7 if l_ < 0.25 else 1.0)
            lead[k + 1] = min(g - t, max(l_, min(0.25, g - t)))
        else:
            t = max(t, min(g, HOLD))
        tail[k] = t
    show = [(max(0.0, a - lead[k]), b + tail[k]) for k, (a, b) in enumerate(span)]
    return [(c, a, min(b, show[k + 1][0]) if k + 1 < n else b)       # word times that overlap never make cues overlap
            for k, (c, (a, b)) in enumerate(zip(cues, show))]


def cue_xml(cues, indent="      ", width=None, weak=WEAK, cps=CPS):
    """<cue> elements with their <word>s; width: break each cue's text into two lines (sidecar), None: one line
    (a burned track lays out its own lines)"""
    xml = []
    for k, (c, start, end) in enumerate(timed(cues, cps)):
        text = " ".join(w[0] for w in c)
        body = "\n".join(two_lines(text, width, weak, _opens(cues, k))) if width else text
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
    for k, (c, a, b) in enumerate(timed(cues, cps)):
        text = " ".join(w[0] for w in c)
        rates.append(len(text) / (b - a))
        longest = max(longest, max(len(x) for x in two_lines(text, width, weak, _opens(cues, k))))
    return len(cues), sum(r > max_cps for r in rates), round(max(rates), 1), longest


# ---- written-form captions and the caption text gate -------------------------------------------------------------

class CaptionAlignError(ValueError):
    """the spoken words do not line up with the written text's token-level spoken map. `token` is the written token
    where they diverge (the last one for spoken words left over), `expected` what its spoken form should be, `got` the
    spoken words found there."""

    def __init__(self, token, index, expected, got, detail=""):
        self.token, self.index, self.expected, self.got = token, index, expected, got
        super().__init__(f"written token {token!r} (#{index}) does not align: expected spoken {expected!r}, got {got!r}"
                         + (f" ({detail})" if detail else ""))


def _norm(word):
    return re.sub(r"[\W_]+", "", unicodedata.normalize("NFC", word).casefold())


def written_words(spoken_words, written_text, lang, engine="kokoro", numbers=None):
    """[(word, start, end)] in the WRITTEN form, from the timed SPOKEN words of the TTS alignment.

    `written_text` is what the cues must show ("12,4%"), `spoken_words` [(word, start, end)] what the engine said and
    the alignment timed ("doze vírgula quatro por cento"). vo.speak_map(written_text, lang, engine, numbers) says which
    spoken words each written token became (lexicon respellings, and in pt-br digits and percent: numbers=None means
    on for pt, off otherwise), and each caption word takes the start of its first spoken word and the end of its
    last. Spoken words are compared by letters and digits only (case, accents kept; punctuation ignored). A token of
    punctuation alone ("—") is joined to the previous word. Pass the same `engine` the audio was made with.
    Raises CaptionAlignError, naming the token, when the two do not align: no silent guess. The result feeds
    split_cues()/sidecar() as it is."""
    from . import vo
    if numbers is None:
        numbers = lang.lower().split("-")[0] == "pt"
    m = vo.speak_map(written_text, lang, engine, numbers=numbers)
    heard = [(w, s, e) for w, s, e in spoken_words if _norm(w)]
    out, pos, pending = [], 0, ""
    for i, tok in enumerate(m.tokens):
        words = [w for w in tok.words if _norm(w)]
        if not words:                                          # punctuation only: shown with its neighbour
            if out:
                out[-1] = (out[-1][0] + " " + tok.written, out[-1][1], out[-1][2])
            else:
                pending = (pending + " " + tok.written).strip()
            continue
        got = heard[pos:pos + len(words)]
        if len(got) < len(words) or any(_norm(a) != _norm(b[0]) for a, b in zip(words, got)):
            raise CaptionAlignError(tok.written, i, " ".join(words), " ".join(g[0] for g in got) or "<end of the spoken words>")
        out.append(((pending + " " if pending else "") + tok.written, got[0][1], got[-1][2]))
        pending, pos = "", pos + len(words)
    if pos < len(heard):
        last = m.tokens[-1].written if m.tokens else ""
        raise CaptionAlignError(last, len(m.tokens) - 1, "<end of the written text>", " ".join(h[0] for h in heard[pos:]),
                                "extra spoken words after the last written token")
    return out


@dataclass(frozen=True)
class Finding:
    """one problem the caption text gate found: kind 'text' (the cues differ from the approved text) or 'spelled-out'
    (a pt-br cue spells a number out); `cue` is the 0-based cue index where it can be placed"""
    kind: str
    cue: object
    detail: str

    def __str__(self):
        return f"{self.kind}" + (f" (cue {self.cue})" if self.cue is not None else "") + f": {self.detail}"


def _cue_text(cue):
    if isinstance(cue, str):
        t = cue
    elif isinstance(cue, dict):
        t = cue["text"]
    elif isinstance(cue, (list, tuple)):
        if len(cue) == 3 and isinstance(cue[0], (list, tuple)) and isinstance(cue[1], (int, float)):
            cue = cue[0]                                          # a timed cue: (words, start, end)
        t = " ".join(w if isinstance(w, str) else w[0] for w in cue)
    else:
        raise TypeError(f"cannot read a cue from {type(cue).__name__}")
    return " ".join(t.split())


def _plain(text):
    """for the spelled-out search: lower case, no accents, single spaces, no punctuation"""
    t = unicodedata.normalize("NFD", text.casefold())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " " + " ".join(re.sub(r"[^\w\s]", " ", t).split()) + " "


def check_text(cues, approved_text, lang):
    """the caption text gate: [Finding], empty when the cues are right.

    - 'text': the cues' joined text differs from `approved_text`. Only whitespace and line breaks are normalised, so a
      clause the owner cut, a stale copy of the text or a respelled word is a finding (each difference is reported on
      the word level: what the cues have extra, what they miss).
    - 'spelled-out' (pt only): a cue says "vírgula" or "por cento" that the approved text does not, or spells out a
      number the approved text writes in digits ("dois mil e três" where it has "2003").
    `cues`: strings, {"text": ...}, lists of words or of (word, start, end), or timed cues (words, start, end)."""
    texts = [_cue_text(c) for c in cues]
    approved = " ".join(approved_text.split())
    out = []
    cw, aw, owner = [], approved.split(), []
    for k, t in enumerate(texts):
        for w in t.split():
            cw.append(w); owner.append(k)
    if cw != aw:
        sm = difflib.SequenceMatcher(None, aw, cw, autojunk=False)
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op == "equal":
                continue
            cue = owner[min(b1, len(owner) - 1)] if owner else None
            want, have = " ".join(aw[a1:a2]), " ".join(cw[b1:b2])
            detail = {"delete": f"the cues miss {want!r}", "insert": f"the cues have extra {have!r}",
                      "replace": f"the approved text has {want!r} where the cues have {have!r}"}[op]
            out.append(Finding("text", cue, detail + f" (after {' '.join(aw[max(0, a1 - 3):a1])!r})"))
    if lang.lower().split("-")[0] == "pt":
        from . import vo
        ap = _plain(approved)
        for k, t in enumerate(texts):
            cp = _plain(t)
            for phrase, shown in (("virgula", "vírgula"), ("por cento", "por cento")):
                if f" {phrase} " in cp and f" {phrase} " not in ap:
                    out.append(Finding("spelled-out", k, f"{shown!r} is spelled out; the approved text writes digits and symbols"))
            for m in vo._PT_NUMBER.finditer(approved):
                spoken = _plain(vo._pt_number_match(m))
                if len(spoken.split()) > 1 and spoken in cp and spoken not in ap and m.group(0) not in t:
                    out.append(Finding("spelled-out", k, f"{spoken.strip()!r} is spelled out; the approved text has {m.group(0)!r}"))
    return out
