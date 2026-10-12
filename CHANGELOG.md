# Changelog

All notable changes to pnkit. Versions follow semantic versioning: a patch release changes no output; a minor
release adds components or parameters and keeps every existing default's output unchanged (byte-identical to 0.8.0,
C14N-equal from 1.0; the golden tests prove it); a change to an existing default's output is a major release until 1.0, and a minor one is never allowed
to hide it. Each release names the golden projects it was checked against.

## 1.0.0 — 2026-10-12 — rebuilt on `sr_core.scene` (major)

Major: pnkit no longer writes XML text. Every component builds `sr_core.scene` elements (sr-core >= 1.8.0, installed from the
sr-core repository; `kit.json` `requires.dependencies`), part 3 of sr-core SREP 0000 (D10, open issue 6.3). The public
functions and their signatures are unchanged; what they return is now `pnkit.sdk.Xml`, a `str` of the same XML that also holds
the SDK elements, so existing callers work unchanged (the least disruptive design: no `*_xml` twins).

Why a major: output is no longer byte-identical to 0.8 (the SDK serialises the XML declaration, empty elements, `>` in an
attribute and the final newline differently from ElementTree), and it requires the SDK. Every golden below is compared as
C14N 2.0 with comments (`tests/c14n.py`), strictly: no number is normalised. sr-core 1.8.0 writes a valid lexical form of a
number as given, so a component that 0.8 wrote with `1.000`, `5.0` or `-13.0` hands the SDK that text. Goldens checked
against the 0.8.0 reference (ac380b2):
- component corpus, 78 entries (`tests/golden/components-0.8.0.json`): 78 strictly C14N-equal (or equal id lists); 58 are
  also byte-identical as strings.
- all 32 Lula 3.0.0 scenes (`tests/golden/pixelart/lula-3.0.0.json`): 32 strictly C14N-equal and level-1 clean
  (`PNKIT_LULA_ALL=1`). None is byte-identical: after the four serialisation differences above are undone on the SDK's
  bytes, all 32 match 0.8.0's `sha256`, so nothing else differs.
- the v013 project goldens of 0.1.0 to 0.8.0 were byte-for-byte, not C14N, and are not re-run by this suite (they need that
  project on disk); they are superseded by the corpus above for the components they exercise.

Added
- `pnkit.sdk`: `Xml`, `new`, `adopt`, `put`, `add`, `indent`, `set_exact`, `parse_fragment`, `BuildError`.
- `Doc.build`, `Doc.check` (the `sr_core.scene.check` findings), `Doc.to_bytes`, `Doc.write`; `build()` and `write()` raise
  `BuildError` on level-1 errors. `Ctx.check_scene()`. `xml.animate()`. `Cam.group()` (the element form of `open()` + `CLOSE`).
- `tools/pixelart/lula_alias.py --c14n`, and a level-1 check of each scene.

Changed
- Ported: xml, text, draw, camera, brand, captions, shorts, physics, figure, audio, pixelart.ctx, filmbuild.assemble.
  Unchanged (orchestrate or read only): the other filmbuild modules, mesh, vo, files, timings, pixel, palette, tools/.
- `Brand.prologue` reads the kit with `sr_core.scene.read` (a parameter default must exist exactly once, else `KeyError`).
- A number is written as the text pnkit gives the SDK (sr-core 1.8.0 keeps a valid lexical form as given): the digits of 0.8.
- `text`, `draw` and `Brand` arguments `extra=`/`content=`/group items accept an element, an `Xml` or an XML string; a string is
  parsed against its parent.

Found by the SDK (each was a latent invalid output or input in 0.8; none changed a golden)
- `Cues.assets()` wrote a prompt containing `"` into an attribute unescaped, so the audio document was not well-formed XML
  (`test_a_quote_in_a_prompt_is_escaped`). Now escaped by the writer.
- `text.label(..., preset="fade-up")` (the corpus call) is not a `textAnimator` preset; the corpus now uses `slide-up`.
- `physics.block` with `<forceField type="gravity"/>` (the corpus call): `gravity` is not a force-field type; the corpus uses `drag`.
- `tests/test_core.py` drew with `#fff` / `#000` (3-digit colours are not `#RRGGBB`) and grouped `<a/>` / `<b/>` (not scene
  elements); now `#FFFFFF`, `#000000` and `<group/>`. The 0.8 code wrote these without complaint.
- Two limits of the SDK 1.7.0, both lifted in sr-core 1.8.0 (which pnkit therefore requires): an `xs:double` could not be
  written as `2.0` (`g.start = "2.0"` was refused, although `read` kept `2.0`), and `Still(...)` was always written
  `<poster>`, never `<thumbnail>` (pnkit set the private name slot). Now a valid lexical `str` is kept as given and
  `Still(xml_name="thumbnail")` is public (`sdk.new` and the string parser use it). `sdk.py` tests for both features
  instead of reading the version, so a checkout of sr-core that has them works before 1.8.0 is tagged.

Tests: 310 passed / 6 skipped before; 339 passed / 5 skipped after (default run, by file, `PNKIT_KIT` set; the 4 skips need numpy and scipy), 340 passed with `PNKIT_LULA_ALL=1`.

## 0.8.0 — 2026-10-10 — the film kit: the pixel-art picture framework and film_build

Additive: every existing default's output is unchanged (no existing function's code path changed; tools/flat_field.py and
tools/timings_diff.py now import their unchanged cores from the library). Owner's go of 2026-10-09 on the reviews in
`PALS-Notes/docs/reviews/2026-10-07/` (PICTURE-REVIEW section 4, PIPELINE-REVIEW sections 3 and 4).

Added
- `pnkit.pixelart`: the Lula 3.0.0 picture framework as a library (geometry, art and figure modules, `ctx.Ctx`, the shared
  `sets`), imports made package-relative and the timings set by the caller (`ctx.set_timings`) instead of a fixed path.
  **Golden:** all 32 Lula scene modules build byte-identical against it (`tests/golden/pixelart/lula-3.0.0.json`,
  `tools/pixelart/lula_alias.py`; 3 scenes in the default suite, all 32 with `PNKIT_LULA_ALL=1`).
- `pnkit.pixelart.checks.CheckedCtx`: the build-time picture checks (view outside the set, figure cut mid-body, plate line
  breaks, judged by `pnkit.pixel`) and `apply_waivers` (a waiver needs a reason; unused waivers are reported).
  **Found while porting:** Lula's `checks_picture.run()` never called `finish()`, so its mid-body-crop check never ran on the
  film; the review's "0 crop findings" was not a measurement. Run through the library on the 32 Lula scenes the check reports
  crop findings in 18 shots; at least some are the "figure behind furniture drawn in the set" pattern the check cannot see
  (its known limit: only later draws in the same parent count as cover), so the count is an upper bound, not 18 defects.
- `pnkit.pixelart.plan`: the plan check as functions (parse_plan, check_plan_only, check_plan_slots, check_built); same 53
  errors and 63 warnings as Lula's check_plan.py on the same built shots.
- `pnkit.pixelart.frames` (flat or empty field, plate visible in a frame) and `pnkit.pixelart.segment` (the per-segment render
  check of Lula check_scene_v3.py, plus flat field on each shot's first frame and plate visibility).
- `pnkit.timings`: load and diff word-timings files (the core of tools/timings_diff.py).
- `pnkit.filmbuild` and `tools/film_build.py`: one film.json, stages snapshot, voice (pronunciation list first, TTS command,
  timings), plan, generate (two hash seeds must agree), assemble (segment, audio and stem documents; the score must regenerate
  bit-identical from its script; caption text gate when the film has captions), render (segments over film.json's hosts
  under the lock; per-segment sha256, host CPU and core count; only changed segments re-render), audio, join (write-once
  `name-vN.mp4`), gates (GATES.md generated from the gate JSON), sheets, pack (vpkg, verify, rebuild check of N segments and
  the audio). No host, path or engine is built in; remote paths are relative to the host's $HOME and may not contain `~`.
  Each stage records its inputs' hashes and is skipped when nothing changed. One summary table on stdout.
- `tools/sync.py` vendors subpackages (`pixelart/`, `filmbuild/`).

- `sets.ESCOLA_STREET_BOARD`: the school board's whole rectangle (no output change).

Fixed while proving it on the golden film (each with a test): the render worker exports the engine path for the
flock'd job; an interrupted render stage attaches to the worker still running on the host instead of launching a
second one; only stems that have tracks are rendered (an empty audioMix is engine error C35); a stage record made by
other pnkit code is stale; an unexpected error is a FAIL row, not a traceback.

Tests: 255 -> 316 (5 skipped), including an end-to-end run of every film_build stage against a fake runner (hosts are
folders; the engine, host python and ffmpeg are stand-ins), so no render runs on the development machine.
Golden film: `PALS-Notes/projects/golden-pixel/` (10 s, two scenes), built end to end on the prod VM by film_build with
engine v0.1.4 (v0.3.1 is not installed on lab or prod). 1.0.1: `out/golden-pixel-v2.mp4`, sha256 6b32e89c...1ed62c16,
10/10 gates, package rebuild byte-identical (1 segment and the audio). 1.0.0 passed every gate with a plate over the
ESCOLA board's end, which only the 1 s sheet showed; the sign is now declared as the whole board.

## 0.7.0 — 2026-10-07 — lessons of the Lula 3.0.0 film: written-form captions, picture checks, pre-batch checks

Additive: every existing default's output is unchanged. Three branches, merged by the coordinator: captions and the
narration dictionary, picture checks for pixel-art films, and pre-batch checks. Prompted by the reviews in
`PALS-Notes/docs/reviews/2026-10-07/`. 124 -> 254 unit tests, all passing (4 skipped as before).

**Golden test not run.** The v013 project (`~/videos/done/v013-jev-decisions`) is not on the host where this release
was made, and its filed package (`channel-wauwmhejrzu-1.0.0.vpkg.zip`) carries the scene and media but not the
generator sources, so `tests/golden/run_v013.py` cannot run anywhere we know of. In its place: no existing function's
code path was changed except `pnkit/__init__.py` (one added import) and appended code in `captions.py` and `vo.py`;
300 random word lists give byte-identical `sidecar()` and `short_cues()` output between 0.6.0 and 0.7.0. A new golden
project is needed.

Known limitation: `vo.hazards()` treats every spoken form in the lexicon as a known acronym whatever the engine, so
OAS and TSE (tested as written on ElevenLabs) are no longer flagged in pt-br on any engine.

### Captions and the narration dictionary
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

### Picture checks for integer-grid pixel-art films

Adds checks that need no render, from the Lula 3.0.0 reviews (a framing defect in scene 11a survived four human reads).
Additive: no existing default's output changes; the golden tests are unaffected.

Added
- `pnkit.pixel` (standard library only): `view_outside(set_w, set_h, grid_w, grid_h, zoom, cx, cy, anchor=None)` returns
  the region a zoom/pan view shows and how much of it lies outside the set (Lula 11a: `zoom(2, 276, 76)` on a 320-column
  set, 22.5 % outside; `zoom(2, 240, 76)` clean); `figure_cut(sprite_h, crop_row, occluded=False)` finds a crop between
  35 % and 85 % of the sprite height with nothing over the cut; `plate_line_breaks(lines)` finds a line ending in ":" or
  an arrow and a value orphaned from its label ("2003: 12,4% → 2010:" / "6,7%"); `scale_off_grid(scale)` finds a scale
  that is not a positive whole number.
- `tools/flat_field.py`: empty-background and flat-field findings on rendered frames, with the frame paths. Thresholds
  (`--empty-frac`, `--strip-cols`, `--flat-frac`) are parameters whose defaults were judged by eye on about 12 frames of
  one film; this is not a precision study. Needs Pillow, imported at run time with a clear message when missing.
- `tools/instance_clock.py`: flags an `<instance>` with no `start` whose symbol reads `time` in a `condition` (its first
  frame is on the absolute clock). `tools/gate.py` runs it and fails on a finding; a scene without the problem gets the
  same output as before.
- Tests: `tests/test_pixel.py`, `tests/test_picture_tools.py`, with the Lula 11a cases and the fixture
  `tests/fixtures/lula_11a_instance_clock.scene.xml`.

### Before a render batch

Added
- `pnkit.files`: approved files are write-once. `write_once(path, data)` raises `WriteOnceError` (a
  `FileExistsError`) when the path exists, dangling symlinks included, and creates it atomically otherwise;
  `next_free(path, suffix="-v")` gives the path itself when free, else `-v2`, `-v3`, ...; `write_next` writes to the
  first free path. Found when a re-run overwrote Lula's owner-approved score excerpt.
- `tools/cue_drift.py`: compares a score's word-tied cue markers (`find`, `edge`, `time`) with the film's current word
  timings and exits 1 when any marker is more than `--tol` (default 0.10 s) off, its phrase is gone or its scene is
  gone. `--format lula` reads the Lula score's `c.at("text", frac)` markers in `make_score.py` against the score's and
  the film's timings files and also fails on a changed scene voice start. Found when 10 of Lula's 37 markers sat
  0.1-0.49 s from their words after a re-voice.
- `tools/vm_preflight.py`: a pre-batch check of the render VMs through `tools/vm/vmrun.sh` (or `--runner`): reachability,
  free disk, who holds or waits on `~/heavy.lock`, each host's CPU model (warns when they differ) and, with
  `--scene --times --render-cmd`, a cross-VM determinism probe that renders the same frames on every host and reports the
  hosts whose sha256 disagree. One table plus a JSON report; exit 1 on an unreachable host, low disk, a failed render or
  a disagreement. Found when the Lula package rebuild matched 26 of 32 segments and the 6 that differed were exactly the
  ones rendered on style3, the only Intel CPU.
- README: layout and a "Before a render batch" section.

## 0.6.0 — 2026-10-02 — captions: no cue ahead of the voice

Changes what `pnkit.captions` writes (cue start and end times, and where a few cues are cut), so by the rule above
it is a breaking release (0.6.0). A project moves to it by syncing and rebuilding; its
sidecar changes.

Found by the sound specialist and an independent reviewer on v019 and v024: captions appeared before the voice. In
0.5.0 a cue led its first word by `max(what its reading time needs, 0.25 s)`, so 0.25 s was a floor and a long cue
after a pause was shown up to the whole pause early (v019: median 0.31 s, 90th percentile 0.66 s, at most 1.01 s,
37 of 62 cues over 0.25 s).

Changed
- `LEAD` (0.30 s), `FIRST_LEAD` (0.35 s) and `HOLD` (1.0 s) are new constants. `timed` starts no cue more than
  `LEAD` s before its first word (`FIRST_LEAD` s for the first cue of the film; it was 0.5 s), whatever the cue
  needs.
- `timed` takes a cue's extra reading time (17 characters/s, `min_show`) from its tail first: the cue is held after
  its last word, up to `HOLD` s and never past the next cue's start. Only what the tail cannot give comes from the
  lead, up to the cap. In 0.5.0 the lead was served first and the tail had no limit when the time was needed; a cue
  that needs nothing still leads by up to 0.25 s and lingers up to 1 s when the pauses allow, as before.
- A cue that lead and tail together cannot hold under 17 characters/s or for `min_show` s is no longer shown early:
  `split_cues` counts it as a fault (its estimate of a cue's room now has the same caps) and `_mend` cuts it again
  with its neighbours, as it already did for a cue under `min_show` s. So some cues are cut elsewhere than in 0.5.0,
  and a short sentence said straight after a long one may join it ("... ahead of the ground. Every day.").
- Unchanged: breaks (numbers, names, weak words), two lines of 42, 17 characters/s, 1 s minimum, no overlaps, every
  word once and in order.

Checked against (sidecars regenerated in a scratch folder from each film's word times; nothing written to a project)

| film | cues | lead before the first word: median / 90th percentile / max, 0.5.0 | same, now | `qa/caption_check.py` |
|---|---|---|---|---|
| v019 | 62 -> 62 | 0.31 / 0.66 / 1.01 s | 0.19 / 0.25 / 0.29 s | pass |
| v024 | 57 -> 56 | 0.25 / 0.54 / 0.92 s | 0.25 / 0.25 / 0.34 s (the first cue; 0.28 s after it) | pass |
| v028 | 65 -> 65 | 0.25 / 0.52 / 0.72 s | 0.25 / 0.25 / 0.30 s | pass |

- v019 and v028 keep every cue's text and line break; only times change. v024 has 8 cues recut into 7: its word
  times leave no pause after "ground." and "error.", so "Every day." and "Per day." join the sentence before them,
  and two sentences that open fast are cut one word group later.
- Known limit, at the Short width (26) on a whole film's words, which no product uses: one v024 cue ("Every
  satellite since has been built", said at 21 characters/s with no pause after it) stays at 17.8 characters/s; 0.5.0
  showed it 0.46 s early instead. No legal recut within its neighbours fits two lines of 26. One v028 cue was already
  at 17.8 in 0.5.0 and is unchanged.
- Tests: `tests/test_captions.py` gains `LeadCap` (7): a long cue after a short pause, the first cue, a cue that
  extends into its tail, the tail before the lead, a cue that must merge, both widths.

## 0.5.0 — 2026-10-01 — captions: breaks and minimum display time

Changes what `pnkit.captions` writes, so by the rule above it is a breaking release (0.5.0),
and the v013 golden test no longer passes byte for byte until its reference is regenerated. v013 rebuilt differs from its own build in 31 `<cue>` lines
and nowhere else, and validates clean. A project moves to it by syncing and rebuilding; its sidecar changes.

Found by the sound specialist's `qa/caption_check.py` on six films (v016, v018, v019, v020, v024, v028).

Changed
- `WEAK` gains what, how, where, who, while, because, there, here, per, our, your, their, his, her, my, you, we,
  they, but, then, after, before (the checker's list). A weak word followed by a comma is still weak; only
  `. ? ! ; :` free the break after it.
- `no_break(tokens, weak, start)` (new) lists the places where no break may fall, between cues or between lines:
  after a weak word; inside a number ("one in ten", "twenty thousand", "three times in ten", "75 per cent",
  `is_number`, `NUMBERS`, `NUM_TAIL`); inside a name (a run of capitalised words that is not just a sentence's
  first word, or a capitalised word and the digit after it: "Apollo 12").
- `line_break(tokens, width, weak, start)` (new) is the one function that says whether a cue fits two lines and where
  its line breaks. `split_cues` used a greedy wrap to accept a cue and `two_lines` a balanced break to show it;
  both now come here, as do `cue_xml` and `stats`. `two_lines` takes `start` (the text opens a sentence).
- `split_cues` cuts a unit only where `no_break` allows, taking a cue more when that is the price (up to two more
  than the fewest that fit), and counts as faults a cue whose only line break is a forbidden one, a cue the pauses
  cannot show for `min_show` s and a cue over 17 characters/s however long it is shown. Forbidden places are used
  only when no split is free of faults. Then a cue still under `min_show` s or over 17 characters/s is cut again
  with its two neighbours (`_mend`): "No." said 0.04 s before the next sentence becomes "No. Before the test, /
  your chance was one in a hundred.", so a cue may now span a sentence end.
- `timed` takes `min_show` (default `MIN_SHOW`, 1 s): a short cue is held from its own tail pause, never by showing
  it earlier. The first cue may lead by up to 0.5 s (it was 0.25 s) when its reading time needs it. A cue's end is
  clamped to the next cue's start, so word times that overlap in the source cannot make cues overlap.

## 0.4.0 — 2026-10-01

Adds the audio-design rule as code, generalized from v015-short-pack, and a few narration entries from the same
pack. No existing output changes: the golden test (v013 rebuilt with the vendored package, strict A/B, final and
draft) is byte-identical as before. v015 itself is unchanged and keeps its own film/core.py.

The rule (user, 2026-10-01, after hearing v015's endings as laser beams): every film gets its own sound design, and
nothing may sound laser-like: no pitch sweep, no synthetic sting, no sustained pure high tone. After the last word
only soft struck foley may start; then the music resolves.

Added
- `pnkit.audio`:
  - `Cues`: a film's effects and beds. `sfx(t, name, gain)` and `ambience(name, gain, fade_in)` take names from the
    palette; a retired cue (`down`, `riser`, `pop`, `success`, `tone`) or an unknown name raises
    `AudioDesignError` with what to use instead. `check(voice_end, duration)` raises if anything but soft struck
    foley starts in the ending (from 0.5 s before the last word ends). `assets()` and `tracks()` write the
    `<audio>`/`<generated>` assets and the `<audioTrack>`s (effects duck 8 dB under the voice, beds 5 dB);
    `bake_beds()` cuts each bed to the film with its fades baked in, because a track's `fadeOut` acts at the end
    of its asset, not of the document. `Cues(extra={...})` adds a project's own cues and cannot bring a retired
    name back.
  - `library()`, `cue(name)`, `retired()`, `tail_ok()`, `resolve_digest(root)`.
  - `scene_cues(xml)` and `scene_tail_violations(xml, voice_end)` read the cues back from a scene document.
- `pnkit/data/sfx_library.json`: the palette. 19 AudioForge cues and 14 files made by `tools/foley.py`, each with its
  default gain, its class (struck, noise, impact, bed, sting), whether it may start after the last word, what it is
  for and where it comes from; and the five retired cues with their AudioForge model, their replacement and why.
- `tools/foley.py [OUT_DIR]`: synthesises the palette's own sounds (struck bodies with fixed modes, filtered noise,
  three beds). Deterministic; ends with a self-check that fails on a gliding tonal partial. Voice venv.
- `tools/tail_check.py MEDIA --voice-end T | --timings JSON [--scene SCENE]`: measures an encoded film's ending. It
  reports the cues that start in it, the longest held pure partial above 380 Hz (limit 0.4 s), that partial's mean
  share (limit 30 %), glides, and the decay (the last 0.1 s at least 15 dB under the level 2 s earlier). Voice venv.
- `pnkit.vo.asr_currency(text)`: `$450 billion` becomes `450 billion dollars`, for both sides of a word-error check
  before the project's number speller. Whisper writes the symbol first; a normaliser that only drops it scores a
  false error on every figure. `asr_normalise` is unchanged and does not call it.
- `pnkit/data/vo_lexicon.json` (en): five Whisper aliases from v015 (`complimentary` for "complementary", and the
  names AlphaGenome, LiveAvatar, HardFlow and MIT as Whisper writes them) and the rule for money.
- Tests: `tests/test_audio.py` (15) and two in `tests/test_vo.py`. The four that exercise `tools/tail_check.py` need
  numpy and scipy and are skipped without them; run the suite with `~/.venvs/voice/bin/python` to include them.

Checked against
- v013 (golden): `run_v013.py --ab --validate` and `--ab --draft --validate`, identical.
- v015 (not a golden project; it does not vendor this version):
  - `Cues.assets()` and `Cues.tracks()` reproduce the audio assets and tracks of all twenty scene documents byte for
    byte, and `tail_violations()` finds none in them.
  - `tools/foley.py` writes the same fourteen files (SHA-256).
  - `tools/tail_check.py` prints the same line as the pack's `qa/sNN/tail.txt` for all twenty encoded files.
  - Controls: a low chord dying away passes; a 1175 Hz tone held for 3.4 s fails (held 3.46 s); a 600 to 2400 Hz sweep
    fails (glide).

Not in this release
- v015's 2D `stage()` camera: `pnkit.camera.Cam` already does it, with the safe-rectangle clamp and `verify()`.
- A self-contained Short builder and 3D camera helpers (projection, self-aimed keys, tags tracked to 3D points):
  candidates for a later release; `pnkit.shorts` still builds Shorts by cutting the long film.

## 0.3.0 — 2026-10-01

Adds baked tapered-tube meshes and an articulated 3D figure built from them, generalized from
v014-bayonet-charge-2011's film/trees.py and film/figures.py (a desert-camo rifle soldier). Both are new
modules with no existing consumer, so there is no golden project to keep byte-identical; v014 itself is
unchanged and keeps its own figures.py.

Added
- `pnkit.mesh`: `Mesh` (a triangle soup built from tapered tubes; `tube()`, `write()` as OBJ), `rot_towards`,
  `tapered_tube(length, r0, r1, ..., up=False)`, `bake_bone(out_dir, name, ..., up=False)` (cached per
  (out_dir, name)). For geometry a native primitive can't do — the engine's `capsule` is one uniform radius,
  and a limb drawn from one reads as a mannequin's rod up close. Pure standard library: no numpy, since
  baking is a one-off offline step, not a per-frame one. `up` is the direction a tube grows relative to its
  own origin (away from the root, or toward it) — see the module's docstring; this was the subtlest bug in
  porting v014's rig, caught only by rendering a figure and looking at it, not by reading the code.
- `pnkit.figure`: `figure(fid, segments, x0, z0, mesh_ids, materials, ...)`, `bone_meshes(assets_dir, dims)`,
  `default_materials()`, `POSES`, `DIMS`. An articulated figure (stand, walk, run, crouch, kneel-fire,
  prone) following a ground path at a cadence set by the pose, its limbs and torso built from
  `pnkit.mesh`'s tapered bones. v014's joint-angle *signs* are kept exactly (empirically tuned per joint,
  not a clean rule — see the module's docstring, lesson 1); its pose *magnitudes* are not — v014's figure
  carries a rifle across its chest even at "stand", which read as an invisible rifle on an unarmed figure
  with this module's defaults, so the default poses here are this module's own, sized for empty hands.

## 0.2.0 — 2026-09-30

Adds the narration dictionary. No existing output changes: the golden test (v013 rebuilt with the vendored
package) is byte-identical as before.

Added
- `pnkit.vo`:
  - `speak(text, lang, engine="kokoro")` applies the dictionary's respellings as whole tokens.
  - `hazards(spoken, lang, known_acronyms=())` is the pre-synthesis check. It flags:
    - a period that splits a word or phrase ("A.I.", "Dr.", "George W. Bush");
    - digits and symbols;
    - dashes, the en dash that shipped "Harvard to Smithsonian" in beta-pic;
    - a mid-line ellipsis;
    - a lone capital letter ("Dia D", "queue A");
    - acronyms not in the dictionary;
    - sentences over 40 words.
    Over the 497 spoken lines in the surveyed projects it flags 15, all worth a look. v013's final lines are clean.
  - `rules`, `entries`, `asr_aliases` and `lexicon` read the dictionary.
  - `asr_normalise(text, lang)` applies the aliases to both sides of a word-error check.
- `pnkit/data/vo_lexicon.json`, the data for `en` and `pt-br`:
  - English: 55 entries, 40 rules and 22 aliases.
  - Brazilian Portuguese: 16 entries, 22 rules and 7 aliases.
  - Every item names its source: a project file and line, the guide, or the 2026-09-30 probe.
  - The data merges v013's fixes, a survey of 13 projects and a Kokoro `af_heart` probe. The probe showed that Kokoro reads RLHF, LLMs, GPT, JSON, HTTP, FAQ, CUDA and NVIDIA correctly unaided. It also showed that "A.I." pauses about 0.3 s even in a single call and that digit decimals and versions are misread.
- `tools/vo_probe.py` (voice venv): Kokoro reads each line, Whisper large-v3 hears it back, and pauses over 0.25 s inside a line are listed. Use it to test a term before it goes into the dictionary.

Changed
- `tools/sync.py` also vendors the package's data files (`pnkit/data/*.json` becomes `film/vendor/pnkit/data/`).
- `tools/check_lock.py` walks subdirectories when it looks for files that are not in the lock. A project's `vpkg.json` needs `/film/vendor/pnkit/data/*` in its include list once it syncs 0.2.0.

## 0.1.0 — 2026-09-30

First release, extracted from v013 "How Jev works" (`~/videos/v013-jev-decisions/film/`). Golden (`tests/golden/`):
v013's `film.scene.xml` rebuilt with the vendored package is byte-identical to the delivered one, and to the
project's own generators on the same inputs, both as a full build and as a draft (`JEV_DRAFT=1`).

Added
- `pnkit.xml`: `f`, `esc`, `Ids`, `opacity`, `keys`, `path_d`, `hash01`, `HASH_EXPR`, `fmt` (v013 `lib.py`).
- `pnkit.doc`: `Doc`, the explicit registry for a document (ids, assets, paints, materials, fields, bodies, text
  cache, text-role styles), replacing v013's module-level lists and id set.
- `pnkit.text`: `text_asset`, `label` with the 36 px information floor (guide §5).
- `pnkit.draw`: `draw`, `rect`, `disc`, `group`, `pill`, `arrow_d`, and `round_rect_d` (v013 `emblems.rr`).
- `pnkit.camera`: `Cam` with the safe-rect clamp and `verify()` (guide §14). Decoupled from the timeline: the act
  window is passed in and beat references go through an injected `resolve` callable.
- `pnkit.brand`: `prologue(kit_path, params)`, `extend`, `kit_sha256`, `fade`, and `Brand` with `title_card`,
  `chapter_card`, `lower_third`, `source_line`, `end_card`, `notch`, `ink`, `emblem`. The kit path and the
  episode's parameters are passed in; the title card's emblem is a parameter (v013 drew its decision card there).
- `pnkit.palette`: the kit's colour tokens as hex, `tokens(kit)` and `check(kit)`.
- `pnkit.captions`: `split_units`, `split_cues`, `two_lines`, `timed`, `cue_xml`, `sidecar`, `short_cues`, `stats`,
  pure functions over `[(word, start, end)]`. The weak-word set is a parameter; v013's episode word "queue" is not
  in the default set (v013 adds it back).
- `pnkit.shorts`: `span_times`, `segments`, `feather_paints`, `overlay`, `output_xml`, `build`, with the subject
  drawing injected and the hook title a parameter.
- `pnkit.physics`: `signature`, `block`.
- `pnkit.bind(doc)`: the helpers with the Doc filled in.
- Tools: `sync.py`, `check_lock.py`, `gate.py`. Catalog: `kit.json`.

Defaults are v013's where the projects disagreed (v012's `f` rounds to 2 decimals and its fades are 0.6 s; pnkit
keeps 3 decimals and v013's fades).

Left in v013 (episode-specific): the timeline, acts, `objects.card` and the other recurring objects, emblems,
effects, sound, and one 176 px cover-headline text asset per Short that no layer places (`hl-s1` … `hl-s6`); the
project registers it itself so its document stays byte-identical.
