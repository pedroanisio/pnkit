# Changelog

All notable changes to pnkit. Versions follow semantic versioning: a patch release changes no output; a minor
release adds components or parameters and keeps every existing default's output byte-identical (the golden tests
prove it); a change to an existing default's output is a major release until 1.0, and a minor one is never allowed
to hide it. Each release names the golden projects it was checked against.

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
