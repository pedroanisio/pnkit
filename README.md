# pnkit — the PALS's Notes component kit

## Disclaimer

This work is subject to the methodological caveats and commitments described in [@DISCLAIMER.md](./DISCLAIMER.md).
> No statement or premise not backed by a real logical definition or verifiable reference should be taken for granted.

pnkit is the shared library for the Python generators that write PALS's Notes scenes (`film/build.py` →
`film.scene.xml`). It holds what every episode re-implemented: number formatting and ids, fades and keyframes,
text layers with the 36 px floor, self-drawing paths, pills, the 2D camera with its safe-rect clamp and check,
the brand kit's prologue and components, captions, the Shorts overlay and spans, the physics block, baked
tapered-tube meshes for 3D geometry no native primitive covers, and an articulated 3D figure built from them.

Since 1.0 pnkit builds its scenes with **`sr_core.scene`**, the Python scene SDK of sr-core (>= 1.8.0, installed from the
sr-core repository; `kit.json` records it under `requires.dependencies`). 1.8.0 is not tagged yet: until it is, a main
checkout with the two 1.8.0 SDK features pnkit needs works, because `pnkit.sdk` tests for the features, not the version
(the CHANGELOG's 1.0.0 entry names them). Nothing writes angle brackets by hand: a
component creates SDK elements, so an element in the wrong parent, an undeclared attribute, a bad enumeration value or a
colour that is not `#RRGGBB` raises when the element is made, not in a render.

- **What a component returns.** `pnkit.sdk.Xml`, a `str` holding the XML text that also keeps the SDK elements it was
  built from (`.element`, `.elements`, `.nodes`). Callers that used the 0.8 string (`str()`, `"\n".join`, f-strings, `in`,
  `ET.fromstring`) keep working without a change; callers that want the element read `.element`. This is the least
  disruptive design: no `*_xml` twin of each function, no changed signature. What a component *accepts* (`extra=`,
  `content=`, group items) may be an element, an `Xml` or a plain XML string; a string is parsed against its parent, so
  a foreign child raises there. `Cam.open()` + `Cam.CLOSE` still works (the legacy text pair); `Cam.group()` is the element form.
- **The document.** `Doc.build(project, composition, *parts)` returns an `sr_core.scene.Scene` made from the frame, the
  sections handed in (for example `Brand.prologue`'s) and the registries (`assets`, `paints`, `materials`, `physics`).
  `Doc.check()` returns `sr_core.scene.check(...)` findings; `build()` and `Doc.write()` raise `pnkit.sdk.BuildError` on
  a level-1 error, and `write()` writes nothing then. `pnkit.pixelart.ctx.Ctx` and `pnkit.filmbuild.assemble` build
  `Scene`s the same way (`Ctx.check_scene()`). `filmbuild`'s other modules, and `tools/gate.py`, `caption_gate.py`,
  `instance_clock.py`, only orchestrate or read documents, and are unchanged.
- **Numbers.** pnkit's 3-decimal form (`pnkit.xml.f`) is kept: the SDK is given that text, and sr-core 1.8.0 writes a valid
  lexical form of a number as given. Where 0.8 wrote another form (`time="855.0"`, `start="1.000"`, `gain="-13.0"`) the
  component formats the number as 0.8 did and hands the SDK that text (`sdk.set_exact`, the caption times), so the document
  carries the same digits.
- **Output equality.** `tests/golden/` compares C14N 2.0 with comments (`tests/c14n.py`), with no normalisation. The bytes
  differ from 0.8's only where the SDK serialises differently from ElementTree (see `tests/golden/README.md`).

It is a Python package. It writes inline XML (through the SDK). It does not use
`<include>` or symbol instances, because neither can carry per-use text: an included document resolves with its
own parameter defaults, and `encode` drops `<override>` on instances after the first frame (guide §6, Avoid 1).
The brand kit, `docs/palsnotes-brand.xml` in this repository (also reachable as `~/videos/docs/palsnotes-brand.xml` on the production machine, a symlink kept for older projects), stays the source of truth for tokens and styles. `docs/` also holds the thumbnail and cover guide (`thumbnail.md`) and the kit's fonts with their licence. pnkit reads
the copy each project pins, and `pnkit.palette.check()` compares pnkit's hex constants with the kit.

Version 0.1.0 was extracted from v013 "How Jev works" and rebuilt its `film.scene.xml` byte for byte; 1.0 is C14N-equal
to 0.8 on the component corpus and on all 32 Lula scenes (see `tests/golden/` and the CHANGELOG).

## Layout

```
pnkit/            the package; vendored into projects as film/vendor/pnkit/
  sdk.py          the one place pnkit meets sr_core.scene: Xml, new, adopt, put, add, BuildError (needs sr-core >= 1.8.0)
  _num.py         f (3-decimal numbers) and esc, shared by xml.py and sdk.py
  xml.py          f, esc, Ids, animate, opacity, keys, path_d, hash01, HASH_EXPR, fmt
  doc.py          Doc: frame, text-role styles, ids, registries (assets, paints, materials, fields, bodies); build, check, to_bytes, write
  palette.py      the kit's colours as hex; tokens(kit), check(kit)
  text.py         text_asset, label (>= 36 px)
  draw.py         draw, rect, disc, group, pill, arrow_d, round_rect_d
  camera.py       Cam: cues, safe rectangles, clamp, drift, verify()
  brand.py        prologue(kit, params), extend, Brand: title_card, chapter_card, lower_third, source_line,
                  end_card, notch, ink, emblem
  captions.py     split_cues, two_lines, timed, cue_xml, sidecar, short_cues, stats; no_break, line_break (no break
                  after a weak word, inside a number or a name), MIN_SHOW (no cue under 1 s)
                  written_words (the voice's spoken words -> caption words in the written form, "12,4%"; raises
                  CaptionAlignError naming the token), check_text (the caption text gate: cues vs the approved text)
  shorts.py       span_times, segments, overlay, output_xml, build
  physics.py      signature, block
  mesh.py         baked tapered-tube meshes (Mesh, tapered_tube, bake_bone) for geometry no primitive covers
  figure.py       an articulated 3D figure (stand/walk/run/crouch/kneel-fire/prone) built from mesh.py's bones
  vo.py           the narration dictionary: speak (numbers=True: pt-br digits as words), speak_map (written token ->
                  spoken words), pt_number, pt_cardinal, hazards, rules, entries, asr_aliases, asr_normalise
  data/vo_lexicon.json   its data by language (en, pt-br): respellings by engine (any, kokoro, chatterbox, piper,
                  elevenlabs), rules, Whisper aliases, each with a source
  pixel.py        build-time checks for integer-grid pixel-art films: view_outside (a zoom/pan view past the set),
                  figure_cut (a sprite cut through the torso), plate_line_breaks (a label parted from its value),
                  scale_off_grid (a scale that breaks the pixel grid)
  audio.py        a film's sound cues, held to the audio-design rule: Cues (sfx, ambience, check, assets, tracks,
                  bake_beds), retired, tail_ok, scene_cues, scene_tail_violations
  data/sfx_library.json  the channel's palette (AudioForge cues and tools/foley.py's files) and the retired cues
  files.py        approved files are write-once: write_once (raises WriteOnceError if the path exists), next_free
                  (excerpt.wav -> excerpt-v2.wav), write_next (write_once to the first free path)
pixelart/         the picture framework of an integer-grid pixel-art film (from Lula 3.0.0): geometry, art and figure
                  modules, ctx (Ctx: shots, zoom, plates, signs, actors, crowds), sets (shared sets), checks (CheckedCtx:
                  build-time picture checks, waivers), plan (the plan check), frames (flat field, plate visible), segment
                  (the per-segment render check, run on the render host)
filmbuild/        film_build: config (film.json), state (hash ledger), remote (runner), stages, assemble, gates, jobs (run on
                  the render host), voice (pronunciation list, timings from takes), pack (vpkg, verify, rebuild check)
timings.py        load and diff word-timings files
kit.json          the catalog: every component, its parameters and the guide rules it satisfies
tools/sync.py     vendor pnkit into a project and write its lock
tools/check_lock.py   verify a project's vendored copy against its lock
tools/gate.py     validate --deny-warnings, eval at probe times (E05/E06), flash-check state; reads the
                  scene-render-cli/1 JSON envelope (scene-render >= 0.6.0), falls back to the human format
tools/vo_probe.py how Kokoro reads a line, heard back by Whisper, with internal pauses (voice venv)
tools/foley.py    synthesise the palette's own sounds into sfx/custom (struck bodies, filtered noise; voice venv)
tools/tail_check.py   measure an encoded film's ending: cues, held pure tone, glide, decay (voice venv)
tools/flat_field.py   flat or empty picture on rendered frames of a pixel-art film (Pillow; thresholds judged by eye)
tools/scopes_check.py levels of rendered frames or an encoded film through `scene-render scopes` (>= 0.6.0): illegal
                  codes, out-of-gamut and oversaturated samples fail past a threshold (default 0); clipping is
                  reported, gated only with --max-clipped; run on the render host
tools/instance_clock.py   an <instance> with no `start` whose symbol reads `time` in a condition (also run by gate.py)
tools/cue_drift.py    word-tied score markers against the film's current word timings; exit 1 over --tol (0.10 s)
tools/vm_preflight.py  before a batch: reachability, free disk, who holds ~/heavy.lock, CPU model, cross-VM frame hashes
tools/caption_gate.py CUES --approved TEXT   the caption text gate: cues (.vtt, scene .xml or .json) must equal the approved
                  written text and, in pt-br, must not spell numbers out; exit 1 on findings
tools/timings_diff.py A.json B.json   sentences and words whose start or end moved by more than --threshold (0.15 s)
tools/film_build.py FILM.json [STAGE ...]   build a film in restartable, hash-recorded stages (docs/film-kit/README.md)
tools/pixelart/lula_alias.py   build Lula 3.0.0 scene modules against pnkit.pixelart and print their sha256
tests/            unit tests (python3 -m unittest discover -s tests) and the golden test (tests/golden/)
```

## Using it in a project

1. Vendor it: `python3 LIB/tools/sync.py PROJECT_DIR`, where `LIB` is this library's checkout (on the production
   machine, `~/videos/lib`, a symlink; the commands below write `LIB` the same way). This copies the package and `kit.json` to
   `PROJECT_DIR/film/vendor/pnkit/`, creates `film/vendor/__init__.py`, and writes `film/vendor/pnkit.lock`
   with the version, the library commit and the SHA-256 of each file. The copy travels with the project, so a
   `.vpkg.zip` builds on another machine. pnkit has no `~` or absolute paths, and it passes the vpkg
   portability lint.
2. Bind it once, in the project's `lib.py`. There is one `Doc` per scene document. The project names its text
   styles and aliases the registries it writes into sections:

   ```python
   from vendor import pnkit
   from vendor.pnkit import camera
   from vendor.pnkit.xml import f, esc, opacity, keys, path_d
   from vendor.pnkit.palette import CREAM, MUTED, ORANGE, INK

   DOC = pnkit.Doc(W, H, styles={"text": "j-text", "caps": "j-caps", "num": "j-num", "head": "j-head",
                                 "note": "j-note", "big": "j-big"})
   ASSETS, PAINTS = DOC.assets, DOC.paints
   K = pnkit.bind(DOC)
   uid, text_asset, label, draw, rect, disc, group, pill = (K.uid, K.text_asset, K.label, K.draw, K.rect,
                                                            K.disc, K.group, K.pill)

   class Cam(camera.Cam):                      # the act's window and beat ids come from the project's timeline
       def __init__(self, act, cues, safe=None, drift=0.022, start=None, end=None):
           super().__init__(DOC, act, cues, ACT[act]["start"] if start is None else start,
                            ACT[act]["end"] if end is None else end, safe=safe, drift=drift, resolve=tb)
   ```

   Brand: `BRAND = pnkit.brand.Brand(DOC)`, `KIT = pnkit.brand.prologue(kit_path, PARAMS)`. Write
   `BRAND.assets` with the assets and `BRAND.overlays` after the finish adjustment. Captions:
   `pnkit.captions.sidecar(words)`. Shorts: `pnkit.shorts.build(DOC, SHORTS, segs_of, cues_of, overlay_of, ...)`,
   where `overlay_of` calls `pnkit.shorts.overlay(..., subject=<the episode's drawing>, hook_title=...)`.
   `~/videos/done/v013-jev-decisions/film/` (the production machine's archive of finished projects) is the worked example once `tests/golden/v013-to-pnkit.diff` is applied.
   Narration: `from vendor.pnkit import vo`, then `say = vo.speak(text, "en")` (numbers in words by the project),
   `vo.hazards(say, "en")` before synthesis, and `vo.asr_normalise` on both sides of the Whisper check. Test a new term
   with `~/.venvs/voice/bin/python LIB/tools/vo_probe.py --lang en "bare." "respelled."` and add it to
   `pnkit/data/vo_lexicon.json` with its source (guide §12 step 3).
   Written-form captions (a film whose voice says "doze vírgula quatro por cento" and whose screen says "12,4%"): never
   rebuild captions from the spoken text. Keep the approved written text, synthesise from
   `vo.speak(text, "pt-br", "elevenlabs", numbers=True)` (the engine is the one the audio is made with), and time the
   written tokens with the TTS alignment: `words = captions.written_words(aligned_spoken_words, text, "pt-br",
   engine="elevenlabs")` gives `[(word, start, end)]` with "12,4%" carrying the start of "doze" and the end of "cento",
   ready for `captions.sidecar(words)`. The map comes from `vo.speak_map`, so a text that differs from what was spoken
   raises `captions.CaptionAlignError` naming the token, instead of a guess. Before delivery run the text gate on the
   finished cues, `python3 LIB/tools/caption_gate.py film.scene.xml --approved approved.txt --lang pt-br`
   (or `captions.check_text(cues, approved, "pt-br")`): it fails on a clause that was cut and is still shown, a stale
   copy of the text, and spelled-out "vírgula" / "por cento" / number words where the approved text has digits. When a
   narration is re-voiced, `python3 LIB/tools/timings_diff.py old.json new.json` lists what moved (the simple
   format is `[{"sentence": id, "text": ..., "words": [[word, start, end], ...]}]`; the Lula `timings-v2.json` shape is
   read as it is). Letter-name respellings (ABC -> "á bê cê") are approved by ear: Whisper cannot verify them.
   Sound: `from vendor.pnkit import audio`, then `CUES = audio.Cues()`, `CUES.sfx(t, "clunk", 0.26)` and
   `CUES.ambience("room", 0.1)` where the film places its sounds. A retired cue (a pitch sweep, a synthetic sting) or
   an unknown name raises `audio.AudioDesignError`. Before writing the document call `CUES.check(voice_end, duration)`:
   after the last word only soft struck foley may start. Write `CUES.assets(duration, tag, digest)` with the assets and
   `CUES.tracks(duration)` in the audio mix, and call `CUES.bake_beds(ROOT, duration, tag)` so each bed ends with the
   film. Make the palette's own files once per project with `~/.venvs/voice/bin/python LIB/tools/foley.py`
   (run in the project directory). After the encode, `tools/tail_check.py out/film.mp4 --voice-end T --scene
   film.scene.xml` measures the ending itself. `~/videos/done/v015-short-pack` (in that archive) is where the rule and the palette come from.
3. Keep episode code in the project: the timeline, acts, subjects and emblems, effects and sound. Pass them in
   where pnkit takes a callable or a parameter.
4. Before delivery, run `python3 LIB/tools/check_lock.py PROJECT_DIR`, which checks that the copy is
   untouched and pinned. Then run `python3 LIB/tools/gate.py PROJECT_DIR/film.scene.xml`, which runs
   validate with warnings as errors, then eval at 0 s (`--probe` and `--markers` add times) and once per layout
   and variant. It
   reports override and target errors (E05, E06), which validate does not see. It also reports whether the
   flash check is on. A scene can validate clean and still fail the gate. After the encode, on the render host,
   `python3 LIB/tools/scopes_check.py out/film.mp4 --step 24` fails the film on illegal codes, out-of-gamut or
   oversaturated samples (`scene-render scopes`, >= 0.6.0); clipping is reported, and gated only when the project
   sets `--max-clipped` (clipped white can be a legitimate specular).

### Pixel-art films

For films drawn on an integer grid (Lula 3.0.0: 320 x 180 cells, 6 x 6 pixels each) the picture can be wrong in ways
the validator, the gate and a human read of the build all miss. Lula's scene 11a showed 22 % of the frame as flat
background (`zoom(2, 276, 76)` on a 320-column set; `zoom(2, 240, 76)` is clean), and four reads did not see it. Run
the checks at two points:

- **At build time, before any render**, from the project's scene builder, on every shot and every plate:
  `pnkit.pixel.view_outside` (a zoom/pan view that leaves the set), `figure_cut` (a sprite cropped between 35 % and
  85 % of its height with nothing over the cut), `plate_line_breaks` (a line ending in ":" or an arrow, a value
  orphaned from its label) and `scale_off_grid` (a scale that is not a whole number). Fail the build on a finding, or
  waive it in the project with a reason. pnkit takes numbers, not the project's context, so the project calls these
  where it places a zoom, an actor or a plate.
- **On the first rendered frame of each shot** (a still is enough): `python3 LIB/tools/flat_field.py --bg
  '#rrggbb' frame.png ...` reports an empty background or a flat field with the frame path. Its thresholds were judged
  by eye on about 12 frames of one film; they are parameters, not a measured precision. A pass is not proof.

`tools/gate.py` also reports an `<instance>` with no `start` whose symbol reads `time` in a `condition` (its first
frame sits on the film's absolute clock, so a crowd pops at the cut); the line appears only when there is one.

## Before a render batch

Three habits from the Lula 3.0.0 film, each with a tool or helper here.

- **Is the score still on the words?** After any re-voice or retime, run `python3 tools/cue_drift.py --markers
  markers.json --timings words.json` (format in the tool's docstring; `--format lula` reads the Lula score's
  `make_score.py` against two timings files). It exits 1 when a marker sits more than 0.10 s from its words. Lula's score
  had 10 of 37 markers 0.1-0.49 s off after a re-voice and nothing said so.
- **Do the hosts render the same bytes?** Run `python3 tools/vm_preflight.py [HOSTS] --min-free-gb 20`, with `--scene`,
  `--times 1,5,9` and `--render-cmd 'TEMPLATE'` to render the same frames on every host and compare their sha256. It also
  reports free disk, who holds or waits on `~/heavy.lock`, and each host's CPU model, and warns when the models differ. The
  Lula package rebuild matched 26 of 32 segments; the 6 that differed were the ones rendered on style3, the only Intel
  CPU. Re-rendering on style3 reproduced the published bytes, so the engine is deterministic per host, not across CPU
  models: do not split a film that must rebuild byte for byte across them without this check. The tool goes through
  `tools/vm/vmrun.sh` by default (`--runner` or `PNKIT_VM_RUNNER` to change it) and its tests use a fake runner only.
- **Never overwrite an approved file.** A tool that writes a file the owner approved uses `pnkit.files.write_once`, or
  `write_next` to put the new version beside it with a `-v2` suffix. Lula's approved score excerpt was once replaced by a
  re-run.

## Library first: rule text for the production guide (draft)

> **Library first (Default).** Before writing a helper or a brand component in an episode's generators, look it
> up in the library's `kit.json` (`LIB/kit.json`). If pnkit has it, vendor pnkit (`tools/sync.py`) and use it. Do not copy its code
> into the project. Don't fork it there either.
>
> - **When pnkit needs to change.** If you need a parameter, a default or a component it lacks, change the
>   library, not the vendored copy:
>   - Add a unit test and a CHANGELOG entry.
>   - Bump the version.
>   - Rebuild the golden projects. They must stay C14N-equal (byte-identical where the SDK writes the same bytes).
>   - Sync.
>
>   A change to what an existing default writes is a breaking change and is released as one.
> - **Episode code.** Drawings, subjects, emblems, acts and the timeline stay in the project. pnkit takes them as
>   callables or parameters.
> - **Per-use text.** Never use `<include>` or `<instance>` with `<override>`. pnkit writes inline copies.
> - **Before delivery.** `tools/check_lock.py` must pass: the copy matches its lock and was synced from a
>   committed library. `tools/gate.py film.scene.xml` must pass:
>   - `validate --deny-warnings` is clean;
>   - `eval` reports no errors at the probes, including E05/E06 override and target errors;
>   - the flash check is on.

## Changing the library

1. Edit `pnkit/` and add or adjust tests: `python3 -m unittest discover -s tests`.
2. Run the golden tests: `python3 tests/golden/run_v013.py --ab --validate` and the same with `--draft`
   (see `tests/golden/README.md`).
3. Bump `__version__` in `pnkit/__init__.py` and `version` in `kit.json` together (`tests/test_tools.py`
   checks that they agree). Add a CHANGELOG entry. Commit.
4. Sync each project that should move to the new version, and rebuild it.

## Why not XML

The duplication across v900, v012 and v013 sat in the Python generators, not in the XML. There were three to
four drifting copies of `brand.py` and of the helpers. An XML library would need `<include>` to take per-use
parameters and text. Today it cannot: the engine templates an included document with its own defaults
(`sr-eval/src/program.rs`, `include()`). SREP draft:
`~/.local/share/scene-render/sr-core/srep-drafts/include-params.md` (a working draft on the production machine,
not yet in the sr-core repository's `srep/`). If that SREP is accepted, pnkit's brand
components could become includes of the kit's symbols, and pnkit would keep the rest.
