"""vo — the narration dictionary: how written text becomes the text a TTS engine is given, by language.

The data lives in pnkit/data/vo_lexicon.json (so it can grow without code changes):
    {"<lang>": {"entries":     [{"written", "spoken", "engine", "why", "source"}],   written -> spoken respellings
                                                                                     (engine: any | kokoro | chatterbox | piper | elevenlabs)
                "rules":       [{"rule", "example", "why", "source"}],              conventions (numbers, pauses, ...)
                "asr_aliases": [{"heard", "means", "source"}]}}                     Whisper normalisation for QA only
Languages are BCP 47 tags as the projects use them ("en", "pt-br").

    from vendor.pnkit import vo
    say = vo.speak("released an AI model", "en")       # applies the entries (whole words, case-sensitive)
    for h in vo.hazards(say, "en"): print(h)            # before synthesis: what the engine is likely to misread
    vo.rules("en")                                      # the conventions, for the script writer
    vo.asr_normalise(hyp, "en")                         # the Whisper check: known mis-hearings compare equal
    vo.asr_currency(hyp)                                # "$450 billion" -> "450 billion dollars", before spelling numbers
    vo.speak("cai de 12,4%", "pt-br", "elevenlabs", numbers=True)   # pt-br: "cai de doze vírgula quatro por cento"
    m = vo.speak_map(text, "pt-br", "elevenlabs", numbers=True)     # the same, plus m.tokens: written token -> spoken
    captions.written_words(timed_spoken_words, text, "pt-br")       # captions in the written form, timed by the voice

`hazards` is the check that would have caught v013's "A.I.": Kokoro pauses at the periods of a dotted abbreviation, and
a one-sentence-per-call synthesiser also splits there, so the listener hears a pause inside the word. An entry whose
`spoken` equals its `written` records a term tested as read correctly as written (hazards then does not flag it).
New terms are tested with tools/vo_probe.py.
"""
import json, os, re
from dataclasses import dataclass

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vo_lexicon.json")
_LEX = None


def lexicon():
    """the whole dictionary, loaded once"""
    global _LEX
    if _LEX is None:
        with open(_DATA, encoding="utf-8") as f:
            _LEX = json.load(f)
    return _LEX


def _lang(lang):
    lex = lexicon()
    key = lang.lower()
    if key in lex:
        return lex[key]
    base = key.split("-")[0]
    for k in lex:
        if k.split("-")[0] == base:
            return lex[k]
    raise KeyError(f"no VO dictionary for {lang!r} (have: {', '.join(k for k in lex if not k.startswith('_'))})")


def entries(lang):
    return list(_lang(lang).get("entries", []))


def rules(lang):
    return list(_lang(lang).get("rules", []))


def asr_aliases(lang):
    """{heard: means} for Whisper QA normalisation (never used to write spoken text)"""
    return {a["heard"]: a["means"] for a in _lang(lang).get("asr_aliases", [])}


def asr_normalise(text, lang):
    """lower-cased text with each alias replaced as a whole token, for both the reference and the transcript of a
    word-error check (so a known mis-hearing and its meaning compare equal)"""
    t = " ".join(text.lower().split())
    for heard, means in sorted(asr_aliases(lang).items(), key=lambda kv: -len(kv[0])):
        t = re.sub(rf"(?<![\w.]){re.escape(heard.lower())}(?![\w])", means.lower(), t)
    return t


_CURRENCY = re.compile(r"\$\s*(\d[\d,]*(?:\.\d+)?)(\s*(?:thousand|million|billion|trillion))?", re.I)


def asr_currency(text):
    """'$450 billion' -> '450 billion dollars', '$5' -> '5 dollars': a transcript writes the symbol first, the narration
    says the unit last. For both sides of a word-error check, before the project's number speller (asr_normalise does
    not call it: it only applies the aliases)."""
    return _CURRENCY.sub(lambda m: f"{m.group(1)}{m.group(2) or ''} dollars", text)


_UN = ("zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete "
       "dezoito dezenove").split()
_TENS = "_ _ vinte trinta quarenta cinquenta sessenta setenta oitenta noventa".split()
_HUN = "_ cento duzentos trezentos quatrocentos quinhentos seiscentos setecentos oitocentos novecentos".split()
_SCALES = ((10 ** 9, "bilhão", "bilhões"), (10 ** 6, "milhão", "milhões"), (1000, "mil", "mil"))


def pt_cardinal(n):
    """a non-negative integer below 10**12 as pt-BR cardinal words (masculine): 2010 -> 'dois mil e dez', 1933 -> 'mil
    novecentos e trinta e três', 103000000 -> 'cento e três milhões'. A remainder under 100, or a whole hundred, is
    joined with 'e'; any other remainder with a space."""
    if not 0 <= n < 10 ** 12:
        raise ValueError(f"number out of range for pt_cardinal: {n}")
    if n < 20:
        return _UN[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " e " + _UN[n % 10])
    if n == 100:
        return "cem"
    if n < 1000:
        return _HUN[n // 100] + ("" if n % 100 == 0 else " e " + pt_cardinal(n % 100))
    for size, one, many in _SCALES:
        if n >= size:
            q, r = divmod(n, size)
            head = "mil" if (size == 1000 and q == 1) else f"{pt_cardinal(q)} {one if q == 1 else many}"
            return head + ("" if r == 0 else (" e " if r < 100 or r % 100 == 0 else " ") + pt_cardinal(r))


# a plain number: digits with optional '.' thousands groups, optional ',' decimals, optional '%'. Not part of a longer
# token (a range 2003-2010, a version 1.4.0, a code A12) and not followed by a digit group it cannot read.
_PT_NUMBER = re.compile(r"(?<![\w,.\-–—])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(%)?(?![\w\-–—]|[.,]\d)")


def _pt_number_match(m):
    whole, frac, pct = m.group(1), m.group(2), m.group(3)
    out = pt_cardinal(int(whole.replace(".", "")))
    if frac is not None:
        out += " vírgula " + (" ".join(_UN[int(c)] for c in frac) if frac.startswith("0") else pt_cardinal(int(frac)))
    return out + (" por cento" if pct else "")


def pt_number(token):
    """one written number as pt-BR words: '12,4%' -> 'doze vírgula quatro por cento', '5.772' -> 'cinco mil setecentos e
    setenta e dois', '2003' -> 'dois mil e três'. A decimal part with a leading zero is read digit by digit ('5,06' ->
    'cinco vírgula zero seis'). Raises ValueError when the token is not a plain number."""
    m = _PT_NUMBER.fullmatch(token)
    if not m:
        raise ValueError(f"not a plain number: {token!r}")
    return _pt_number_match(m)


def _engine_entries(lang, engine):
    return [e for e in entries(lang) if e.get("engine", "any") in ("any", engine) and e.get("written")
            and e.get("spoken") not in (None, e["written"])]


def speak(text, lang, engine="kokoro", numbers=False):
    """the spoken form: each entry's `written` replaced by its `spoken` as a whole token (longest first), for entries
    whose engine is `any` or the given engine (kokoro, chatterbox, piper, elevenlabs). With numbers=False (the default)
    numbers are not converted (use the project's number speller). numbers=True also writes digits as words, pt-br only
    (see pt_number). To know which written token became which spoken words, call speak_map."""
    if numbers:
        return speak_map(text, lang, engine, numbers=True).spoken
    for e in sorted(_engine_entries(lang, engine), key=lambda e: -len(e["written"])):
        w = re.escape(e["written"])
        text = re.sub(rf"(?<![\w.-]){w}(?![\w-])", e["spoken"], text)
    return text


@dataclass(frozen=True)
class MapToken:
    """one written token (whitespace-separated, punctuation attached; an entry that spans whitespace, such as 'Dia D',
    is one token) and the spoken text it became, with the same attached punctuation"""
    written: str
    spoken: str
    start: int            # character range of `written` in the written text
    end: int

    @property
    def words(self):
        return self.spoken.split()


@dataclass(frozen=True)
class SpeakMap:
    written: str
    spoken: str
    tokens: tuple


def speak_map(text, lang, engine="kokoro", numbers=False):
    """speak() that also reports, token by token, what each written token became: the map a caption needs to put the
    written form ("12,4%") on the spoken words ("doze vírgula quatro por cento"). -> SpeakMap(written, spoken, tokens).
    `.spoken` equals speak(text, lang, engine, numbers) except where speak() would apply one respelling to the output
    of another (not done here). numbers=True needs a number speller (pt-br); other languages raise ValueError."""
    if numbers and lang.lower().split("-")[0] != "pt":
        raise ValueError(f"no number speller for {lang!r} (pt-br only)")
    units = []                                               # (start, end, spoken), non-overlapping

    def free(a, b):
        return all(b <= u[0] or a >= u[1] for u in units)

    for e in sorted(_engine_entries(lang, engine), key=lambda e: -len(e["written"])):
        for m in re.finditer(rf"(?<![\w.-]){re.escape(e['written'])}(?![\w-])", text):
            if free(m.start(), m.end()):
                units.append((m.start(), m.end(), e["spoken"]))
    if numbers:
        for m in _PT_NUMBER.finditer(text):
            if free(m.start(), m.end()):
                units.append((m.start(), m.end(), _pt_number_match(m)))
    units.sort()

    def render(a, b):                                        # the spoken text of text[a:b]; units lie wholly inside
        out, i = [], a
        for u0, u1, sp in units:
            if u1 > a and u0 < b:
                out += [text[i:u0], sp]; i = u1
        out.append(text[i:b])
        return "".join(out)

    spans = []
    for m in re.finditer(r"\S+", text):
        a, b = m.start(), m.end()
        if spans and a < spans[-1][1]:                       # inside a unit that began in an earlier token
            continue
        grown = True
        while grown:                                         # a unit that spans whitespace joins its tokens
            grown = False
            for u0, u1, _ in units:
                if u0 < b < u1:
                    b, grown = u1, True
        spans.append((a, b))
    return SpeakMap(text, render(0, len(text)), tuple(MapToken(text[a:b], render(a, b), a, b) for a, b in spans))


@dataclass
class Hazard:
    kind: str
    match: str
    advice: str

    def __str__(self):
        return f"{self.kind}: {self.match!r} — {self.advice}"


_DOTTED = re.compile(r"\b(?:[A-Za-z]\.){2,}")                     # A.I.  U.S.  e.g.
_INITIAL = re.compile(r"(?<![\w.])[A-Z]\.(?=\s)")                 # George W. Bush (not "on X. Then")
_ABBREV = {"en": ("Dr.", "Mr.", "Mrs.", "Ms.", "St.", "vs.", "etc.", "No.", "approx.", "Inc.", "Ltd.", "Jr.", "Sr."),
           "pt": ("Sr.", "Sra.", "Dr.", "Dra.", "etc.", "nº.", "aprox.", "Ltda.", "p.ex.")}
_DIGITS = re.compile(r"\d")
_SYMBOLS = re.compile(r"[%×$€£&+=/#@~^<>|\\]")
_CAPS = re.compile(r"\b[A-Z]{2,}[a-z]?\b")                        # LLM, RLHF, LLMs
_DASH = re.compile(r"[–—]")                                       # en and em dash
_ELLIPSIS = re.compile(r"(\.\.\.|…)\s+\S")                          # an ellipsis with more text after it


def hazards(spoken, lang, known_acronyms=()):
    """problems in a spoken text before it goes to the synthesiser: sentence splits inside a word, digits and symbols
    the engine may read oddly, dashes and ellipses, single capital letters, acronyms not tested, over-long sentences.
    -> [Hazard] (kinds: split, digits, symbol, dash, ellipsis, letter, acronym, long)"""
    out, base = [], lang.lower().split("-")[0]
    for m in _DOTTED.finditer(spoken):
        out.append(Hazard("split", m.group(0), f"a dotted abbreviation cuts the sentence here; write {m.group(0).replace('.', '')}"))
    for m in _INITIAL.finditer(spoken):
        before = spoken[:m.start()].split()
        if not before or (before[-1][:1].isupper() and not re.fullmatch(r"[A-Z]", before[-1])):   # after a name ("George W. Bush"), not "on X." or "G R P O."
            out.append(Hazard("split", m.group(0), "an initial followed by a space ends the sentence here; drop the period or spell the name"))
    for a in _ABBREV.get(base, ()):
        if re.search(rf"(?<![\w.]){re.escape(a)}\s", spoken):
            out.append(Hazard("split", a, "an abbreviation with a period ends the sentence here; write it out"))
    if _DIGITS.search(spoken):
        out.append(Hazard("digits", ", ".join(sorted(set(re.findall(r"[\d][\d.,:]*", spoken))))[:80],
                          "write numbers as words in the spoken text (years, decimals, versions have their own conventions)"))
    for m in set(_SYMBOLS.findall(spoken)):
        out.append(Hazard("symbol", m, "write the symbol as words (percent, times, dollars, and, plus, slash)"))
    for m in sorted(set(_DASH.findall(spoken))):
        out.append(Hazard("dash", m, "say what the dash means: 'to' between numbers, a hyphen inside a name (Harvard-Smithsonian), "
                                     "a comma for a pause; a blanket dash -> 'to' shipped 'Harvard to Smithsonian' in beta-pic"))
    if _ELLIPSIS.search(spoken.rstrip().rstrip(".…").rstrip() + " "):
        out.append(Hazard("ellipsis", "...", "an ellipsis inside a line: use a full stop for a real pause, or a comma"))
    words = spoken.split()
    cores = [w.strip(",;:!?.\"'()") for w in words]
    spelled = lambda j: 0 <= j < len(cores) and (re.fullmatch(r"[A-Z]s?", cores[j]) is not None)     # part of R L H F, L L Ms
    for i, w in enumerate(words):
        core = cores[i]
        if len(core) == 1 and core.isupper() and core != "I" and i > 0 and not words[i - 1].endswith((".", "?", "!")) \
                and not (spelled(i - 1) or spelled(i + 1)):
            out.append(Hazard("letter", " ".join(words[max(0, i - 1):i + 1]), "a single capital letter may be misread (pt-BR 'Dia D' was read 'dia W'; "
                                                                           "'queue A' is heard 'QO'): give it a noun, or write its name (Dia Dê)"))
    said = {e["written"]: e["spoken"] for e in entries(lang)}
    known = set(known_acronyms) | set(said.values())
    for m in sorted(set(_CAPS.findall(spoken))):
        if m in known:
            continue
        if m in said:
            out.append(Hazard("acronym", m, f"the dictionary says {said[m]!r}; it was left as written (joined to a hyphen or a digit?)"))
        else:
            out.append(Hazard("acronym", m, "check how the engine reads it: spell it as letters with spaces (L L M), or pass it in known_acronyms if it is read as a word"))
    for s in re.split(r"(?<=[.?!])\s+", spoken):
        n = len(s.split())
        if n > 40:
            out.append(Hazard("long", s[:60] + "…", f"{n} words in one sentence; split it or add commas for breath"))
    return out
