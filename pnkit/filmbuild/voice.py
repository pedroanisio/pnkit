"""pnkit.filmbuild.voice — the voice stage's pure parts: the pronunciation list and the timings built from the takes.

  pronounce_terms(text, lang, extra)   acronyms, numerals, names (a capital not at a sentence start) and the extra terms
                                       film.json lists (foreign words), each once, with the spoken form pnkit.vo gives;
                                       plus pnkit.vo.hazards of the spoken text. One clip each is made before the full
                                       synthesis (Lula 3.0.0: 7,116 characters and four owner rounds were spent because
                                       this list did not exist).
  build_timings(scenes, takes, ...)    the film's one timings file from the narrative and each scene's take: slots tile
                                       the film, a line's words keep their WRITTEN form (captions.written_words) with
                                       the spoken words' times.
"""
import re

from .. import vo, captions

_ACR = re.compile(r"\b[A-ZÀ-Ý]{2,}[a-z]?\b")
_NUM = re.compile(r"\S*\d\S*")
_LINK = {"de", "da", "do", "das", "dos", "e", "of", "the"}


def pronounce_terms(text, lang, extra=(), engine="kokoro"):
    seen, out = set(), []

    def add(term, kind):
        t = term.strip(".,;:!?\"'()«»“”")
        if t and t not in seen:
            seen.add(t)
            out.append({"term": t, "kind": kind, "spoken": vo.speak(t, lang, engine, numbers=lang.lower().startswith("pt"))})
    for m in _ACR.findall(text):
        add(m, "acronym")
    for m in _NUM.findall(text):
        add(m, "numeral")
    for sent in re.split(r"(?<=[.?!])\s+", text):
        run = []
        for i, w in enumerate(sent.split()):
            core = w.strip(".,;:!?\"'()«»“”")
            cap = i > 0 and core[:1].isupper() and not _ACR.fullmatch(core) and not any(ch.isdigit() for ch in core)
            if cap or (run and core in _LINK):
                run.append(core)
            if (not cap and not (run and core in _LINK)) or w != core:          # a name ends at a lower-case word or a punctuation mark
                while run and run[-1] in _LINK:
                    run.pop()
                if run:
                    add(" ".join(run), "name")
                run = []
        if run:
            add(" ".join(r for r in run), "name")
    for t in extra:
        add(t, "term")
    hz = [str(h) for h in vo.hazards(vo.speak(text, lang, engine, numbers=lang.lower().startswith("pt")), lang)]
    return {"terms": out, "hazards": hz}


def build_timings(narrative, takes, lang, engine, lead=0.5, tail=0.8, min_s=None):
    """narrative: {"scenes": [{"n", "id", "lines": [{"line", "text"}], "min_s"}]}; takes: {n: (duration_s, spoken words
    [(word, start, end)] relative to the take)}. -> {"scenes": [{n, id, slot_start, slot_end, voice_start, voice_end,
    lines: [{line, caption, words [[w, start, end]], start, end}]}]}"""
    numbers = lang.lower().startswith("pt")
    t, out = 0.0, []
    for sc in narrative["scenes"]:
        dur, spoken = takes[sc["n"]]
        vs = round(t + lead, 3)
        lines, k = [], 0
        for ln in sc["lines"]:
            n_sp = len(vo.speak(ln["text"], lang, engine, numbers=numbers).split())
            part = [(w, a + vs, b + vs) for w, a, b in spoken[k:k + n_sp]]
            if len(part) != n_sp:
                raise ValueError(f"scene {sc['n']} line {ln['line']}: the take has {len(spoken) - k} words left, the line needs {n_sp}")
            k += n_sp
            ww = captions.written_words(part, ln["text"], lang, engine, numbers=numbers)
            lines.append({"line": ln["line"], "caption": ln["text"], "words": [[w, round(a, 3), round(b, 3)] for w, a, b in ww],
                          "start": round(ww[0][1], 3), "end": round(ww[-1][2], 3)})
        if k != len(spoken):
            raise ValueError(f"scene {sc['n']}: the take has {len(spoken) - k} words the narrative does not")
        end = max(vs + dur + tail, t + (sc.get("min_s") or min_s or 0))
        out.append({"n": sc["n"], "id": sc["id"], "slot_start": round(t, 3), "slot_end": round(end, 3),
                    "voice_start": vs, "voice_end": round(vs + dur, 3), "lines": lines})
        t = round(end, 3)
    return {"scenes": out}
