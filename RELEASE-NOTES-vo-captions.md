---
disclaimer:
  notice: >-
    No information within this document should be taken for granted.
    Any statement or premise not backed by a real logical definition
    or verifiable reference may be invalid, erroneous, or a hallucination.
  generated_by: "Claude Sonnet 5.5 via Claude Code"
  date: "2026-10-07"
---

# Release notes: branch feat/vo-captions

Proposed text for the merge. This branch does not bump `__version__` and does not edit `CHANGELOG.md` or `kit.json`;
whoever merges chooses the version number (additive only, so a minor release by the rule in the CHANGELOG preamble)
and pastes the entries below.

## CHANGELOG entry (proposed)

```markdown
## 0.X.0 — 2026-10-07 — written-form captions, the caption text gate, the ElevenLabs pt-br lexicon

Additive: every existing default's output is unchanged (`speak()` without `numbers`, every `captions` function, the
engines other than `elevenlabs`). Prompted by the Lula 3.0.0 film, published with caption defects (lula-filme
p3/CHANGES.md; docs/reviews/2026-10-07/PIPELINE-REVIEW.md).

Found
- Captions were rebuilt from the SPOKEN text: six captions read "DOZE VÍRGULA QUATRO PARA SEIS VÍRGULA SETE POR CENTO"
  instead of "12,4% PARA 6,7%".
- One caption kept a clause the owner had cut: a stale copy of the text fed the assembler, and no gate compared the
  caption text with the approved text.
- ElevenLabs (Henrique, eleven_v4, pt-BR) read "ABC" in English.

Added
- `vo_lexicon.json`, pt-br, engine `elevenlabs`: ABC "á bê cê", PT "pê tê", FHC "éfe agá cê", IBGE "í bê gê é", STJ
  "ésse tê jota", PF "pê éfe", CPI "cê pê í", PIB "píbi", ONU "ônu", SUS "sus" (approved by the owner's ear,
  2026-10-07); OAS and TSE as tested-as-written entries (the respellings "ó á ésse" and "tê essi é" were tried and the
  owner preferred the original); a pt-br rule: Whisper cannot verify letter names. `elevenlabs` is a new allowed
  `engine` value; `speak()` already took any engine name.
- `vo.speak(text, lang, engine, numbers=False)`: `numbers=True` writes digits as words (pt-br only; `ValueError`
  otherwise): `12,4%` -> "doze vírgula quatro por cento", `2003` -> "dois mil e três", `5.772`, a leading-zero decimal
  digit by digit. Not part of a range, a version or a code (`2003-2010`, `1.4.0`, `A12` stay as written).
- `vo.speak_map(text, lang, engine, numbers)` -> `SpeakMap(written, spoken, tokens)`: the token-level written -> spoken
  map (`MapToken.written`, `.spoken`, `.words`, `.start`, `.end`). An entry that spans whitespace ("Dia D") is one
  token. `.spoken` equals `speak()` for every lexicon entry on every engine (tested). `vo.pt_number`, `vo.pt_cardinal`.
- `captions.written_words(spoken_words, written_text, lang, engine, numbers=None)`: caption words in the WRITTEN
  form, each with the start of its first spoken word and the end of its last, aligned with `vo.speak_map`; the result
  feeds `split_cues`/`sidecar`. `captions.CaptionAlignError(token, index, expected, got)` when they do not align.
- `captions.check_text(cues, approved_text, lang)` -> `[Finding(kind, cue, detail)]`: `text` (the cues differ from the
  approved text; only whitespace and line breaks are normalised; reported per difference), `spelled-out` (pt only:
  "vírgula" or "por cento" the approved text does not contain, or a number spelled out where the approved text has
  its digits). `captions.Finding`.
- `tools/caption_gate.py CUES --approved TEXT [--lang] [--json]`: the gate as a CLI over .vtt, scene .xml or .json
  cues; exit 1 on findings, 2 on unreadable input.
- `tools/timings_diff.py A B [--threshold 0.15] [--json]`: sentences and words whose start or end moved by more than
  the threshold, for the simple format `[{"sentence", "text", "words": [[word, start, end]]}]` and the Lula
  `timings-v2.json` shape; exit 1 when anything moved.

Checked against
- 124 -> 164 unit tests (40 new; 4 skipped as before), including all 32 narrations of the Lula film
  (`v2-fixed.json`) mapped and aligned, and `timings-v2.2.json` against `timings-v2.json` (scenes 16 and 23 do not move).
- The v013 golden test could not be run on the machine this was written on (`~/videos/done/v013-jev-decisions` is
  absent). Replaced by: 300 random word lists give byte-identical `sidecar()` and `short_cues()` output between the
  previous `captions.py` and this one. The golden test must be run by the merger.
```

## kit.json component entries (proposed)

Add to `components` (the existing `vo.speak / ...` entry may also list the new names in its title; the entries below
stand on their own). Add the two tools to `tools`.

```json
{
 "components": [
  {"name": "vo.speak (numbers=True) / vo.speak_map / vo.pt_number / vo.pt_cardinal", "module": "pnkit.vo",
   "summary": "Numbers and the token-level written -> spoken map. speak(..., numbers=True) writes digits as pt-BR words (12,4% -> doze vírgula quatro por cento; 2003 -> dois mil e três) and speak_map() returns SpeakMap(written, spoken, tokens): for each written token the spoken words it became (lexicon respellings and numbers), which written_words() uses to time captions. speak() without numbers is unchanged.",
   "params": ["speak(text, lang, engine='kokoro', numbers=False)", "speak_map(text, lang, engine='kokoro', numbers=False) -> SpeakMap(written, spoken, tokens[MapToken(written, spoken, start, end)])", "pt_number(token) -> words; pt_cardinal(n) -> words (n < 10**12)", "engine: any | kokoro | chatterbox | piper | elevenlabs (the lexicon's engine field); numbers=True is pt-br only"],
   "rules": ["captions show the written text and are timed by the spoken words; never rebuild captions from the spoken text (Lula 3.0.0: 'DOZE VÍRGULA QUATRO ...')", "ElevenLabs letter-name respellings (ABC -> á bê cê) are approved by ear: Whisper cannot verify letter names", "OAS and TSE are read correctly as written by ElevenLabs; leave them"]},
  {"name": "captions.written_words / captions.CaptionAlignError", "module": "pnkit.captions",
   "summary": "Caption words in the written form from the timed spoken words of a TTS alignment: '12,4%' carries the start of 'doze' and the end of 'cento'. Uses vo.speak_map, so the alignment follows a map, not a guess, and raises CaptionAlignError naming the written token when the spoken words do not match (a stale or edited text).",
   "params": ["written_words(spoken_words [(word, start, end)], written_text, lang, engine='kokoro', numbers=None) -> [(word, start, end)]", "CaptionAlignError(token, index, expected, got)", "pass the engine the audio was made with; numbers=None is on for pt, off otherwise"],
   "rules": ["compare by letters and digits only: case, accents kept, punctuation ignored", "a punctuation-only token is joined to the previous word", "no silent repair: a mismatch raises"]},
  {"name": "captions.check_text / captions.Finding", "module": "pnkit.captions",
   "summary": "The caption text gate: the cues' joined text must equal the approved written text (only whitespace and line breaks normalised), and for pt-br no cue may spell out 'vírgula', 'por cento' or a number the approved text writes in digits.",
   "params": ["check_text(cues, approved_text, lang) -> [Finding(kind 'text'|'spelled-out', cue, detail)]", "cues: strings, {'text': ...}, word lists, (word, start, end) lists or timed cues (words, start, end)"],
   "rules": ["run it on the finished cues before delivery, against the approved text, never against a text derived from the cues or from the spoken text"]}
 ],
 "tools": {
  "tools/caption_gate.py CUES --approved TEXT [--lang pt-br] [--json]": "the caption text gate as a CLI: CUES is .vtt, a scene .xml (every <cue text>) or .json; exit 1 on findings, 2 on unreadable input",
  "tools/timings_diff.py A.json B.json [--threshold 0.15] [--json]": "sentences and words whose start or end moved by more than the threshold; simple format [{sentence, text, words [[word, start, end]]}] or the Lula timings-v2.json shape; exit 1 when anything moved"
 }
}
```

## Notes for the merger

- `vo.hazards()` treats every spoken form in the lexicon as a known acronym regardless of engine, so with the
  tested-as-written entries OAS and TSE are no longer flagged as untested acronyms in pt-br (any engine). That is the
  existing semantics of "spoken == written means tested", now applied to two more terms.
- Run the v013 golden test (`python3 tests/golden/run_v013.py --ab --validate`, and with `--draft`) where the project
  exists; this branch only appends to `captions.py` and touches no function the golden build calls.
- Not done: the project's own assembler must call `written_words` and `check_text`; this branch is the library side.
