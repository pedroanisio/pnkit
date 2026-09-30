# pnkit — the PALS's Notes component kit

pnkit is the shared library for the Python generators that write PALS's Notes scenes (`film/build.py` →
`film.scene.xml`). It holds what every episode re-implemented: number formatting and ids, fades and keyframes,
text layers with the 36 px floor, self-drawing paths, pills, the 2D camera with its safe-rect clamp and check,
the brand kit's prologue and components, captions, the Shorts overlay and spans, and the physics block.

It is a Python package with no dependencies outside the standard library. It writes inline XML. It does not use
`<include>` or symbol instances, because neither can carry per-use text: an included document resolves with its
own parameter defaults, and `encode` drops `<override>` on instances after the first frame (guide §6, Avoid 1).
The brand kit, `docs/palsnotes-brand.xml` in this repository (also reachable as `~/videos/docs/palsnotes-brand.xml`, a symlink kept for older projects), stays the source of truth for tokens and styles. `docs/` also holds the thumbnail and cover guide (`thumbnail.md`) and the kit's fonts with their licence. pnkit reads
the copy each project pins, and `pnkit.palette.check()` compares pnkit's hex constants with the kit.

Version 0.1.0 was extracted from v013 "How Jev works". Rebuilding v013 with it gives a byte-identical
`film.scene.xml` (see `tests/golden/`).

## Layout

```
pnkit/            the package; vendored into projects as film/vendor/pnkit/
  xml.py          f, esc, Ids, opacity, keys, path_d, hash01, HASH_EXPR, fmt
  doc.py          Doc: frame, text-role styles, ids, registries (assets, paints, materials, fields, bodies)
  palette.py      the kit's colours as hex; tokens(kit), check(kit)
  text.py         text_asset, label (>= 36 px)
  draw.py         draw, rect, disc, group, pill, arrow_d, round_rect_d
  camera.py       Cam: cues, safe rectangles, clamp, drift, verify()
  brand.py        prologue(kit, params), extend, Brand: title_card, chapter_card, lower_third, source_line,
                  end_card, notch, ink, emblem
  captions.py     split_cues, two_lines, timed, cue_xml, sidecar, short_cues, stats
  shorts.py       span_times, segments, overlay, output_xml, build
  physics.py      signature, block
kit.json          the catalog: every component, its parameters and the guide rules it satisfies
tools/sync.py     vendor pnkit into a project and write its lock
tools/check_lock.py   verify a project's vendored copy against its lock
tools/gate.py     validate --deny-warnings, eval at probe times (E05/E06), flash-check state
tests/            unit tests (python3 -m unittest discover -s tests) and the golden test (tests/golden/)
```

## Using it in a project

1. Vendor it: `python3 ~/videos/lib/tools/sync.py PROJECT_DIR`. This copies the package and `kit.json` to
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
   `~/videos/v013-jev-decisions/film/` is the worked example once `tests/golden/v013-to-pnkit.diff` is applied.
3. Keep episode code in the project: the timeline, acts, subjects and emblems, effects and sound. Pass them in
   where pnkit takes a callable or a parameter.
4. Before delivery, run `python3 ~/videos/lib/tools/check_lock.py PROJECT_DIR`, which checks that the copy is
   untouched and pinned. Then run `python3 ~/videos/lib/tools/gate.py PROJECT_DIR/film.scene.xml`, which runs
   validate with warnings as errors, then eval at 0 s (`--probe` and `--markers` add times) and once per layout
   and variant. It
   reports override and target errors (E05, E06), which validate does not see. It also reports whether the
   flash check is on. A scene can validate clean and still fail the gate.

## Library first: rule text for the production guide (draft)

> **Library first (Default).** Before writing a helper or a brand component in an episode's generators, look it
> up in `~/videos/lib/kit.json`. If pnkit has it, vendor pnkit (`tools/sync.py`) and use it. Do not copy its code
> into the project. Don't fork it there either.
>
> - **When pnkit needs to change.** If you need a parameter, a default or a component it lacks, change the
>   library, not the vendored copy:
>   - Add a unit test and a CHANGELOG entry.
>   - Bump the version.
>   - Rebuild the golden projects. They must stay byte-identical.
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
`~/.local/share/scene-render/sr-core/srep-drafts/include-params.md`. If that SREP is accepted, pnkit's brand
components could become includes of the kit's symbols, and pnkit would keep the rest.
