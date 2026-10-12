# Golden tests

A golden test rebuilds a delivered project with the vendored pnkit and compares the scene it writes with the
delivered one. From 1.0 the comparison is C14N 2.0 with comments (`tests/c14n.py`), strict, with no normalisation of numbers: the scene
SDK (sr-core >= 1.8.0) writes a number as the text it is given, and pnkit gives the text 0.8.0 wrote. The goldens frozen from
pnkit 0.8.0 (below) are the reference for 1.0. A release of
pnkit must pass every golden test listed here. If a change is meant to alter output, it must say so in the CHANGELOG
and bump the version as a breaking change.

## The 0.8.0 goldens that 1.0 is held to

- `components-0.8.0.json` + `components_corpus.py`: what 0.8.0 wrote for 78 fixed calls of every component that writes scene XML
  (xml, text, draw, camera, brand, captions, shorts, physics, figure, audio, filmbuild.assemble). Regenerate the reference
  from an old checkout with `python3 components_corpus.py KIT OLD_LIB > components-0.8.0.json`. Checked in
  `tests/test_sdk.py` (`Golden`): all 78 entries are strictly C14N-equal (or have equal id lists), 58 also byte-identical as strings.
- `pixelart/lula-3.0.0.json`: per scene `sha256` (0.8.0 bytes, record only) and `c14n_sha256`.
  1.0 matches `c14n_sha256` for all 32 scenes (`PNKIT_LULA_ALL=1`, about 45 s; 3 scenes by default) and its
  scenes are level-1 clean (`tools/pixelart/lula_alias.py --c14n`). The bytes differ from `sha256` in every scene, only by
  what the SDK serialises differently from ElementTree: `<?xml version="1.0" encoding="UTF-8"?>` (ET wrote single quotes
  and `utf-8`), `/>` (ET wrote ` />`), a literal `>` in an attribute value (ET wrote `&gt;`), and a final newline. With those
  four undone on the new bytes, all 32 hash to `sha256`.

## The v013 project goldens (byte for byte, 0.1.0 to 0.8.0)

## v013 "How Jev works" (`~/videos/done/v013-jev-decisions`)

```bash
python3 tests/golden/run_v013.py --ab --validate          # the strict A/B (use this)
python3 tests/golden/run_v013.py --ab --draft --validate  # the same for JEV_DRAFT=1 builds
python3 tests/golden/run_v013.py --expect PINNED.xml      # against a pinned delivered scene
```

Add `--work DIR --keep` to inspect the copies.

1. The project is copied to a work directory. `out/` and `qa/` are left out, and the large read-only inputs are
   symlinked: `vo/*.wav`, `vo/cache`, `sfx/`, `music/score.wav`, `music/af`, `assets/`, `fonts/`, `film/tex/`
   and `film/physics.cache`. The project itself is only read.
2. `tools/sync.py` vendors this library into the copy's `film/vendor/pnkit/` and writes `film/vendor/pnkit.lock`.
3. If the project does not use pnkit yet, `v013-to-pnkit.diff` is applied to the copy with `patch -p1`. The
   patch changes `film/lib.py`, `brand.py`, `captions.py`, `shorts.py`, `emblems.py`, `styles.py` and `build.py`
   so that everything extracted comes from `vendor.pnkit`:
   - `lib.py` binds the `Doc`, the palette, `Cam` and the physics block.
   - `brand.py` keeps only the episode's parameters and its title-card emblem.
   - `captions.py` keeps only its word list and the extra weak word "queue".
   - `shorts.py` keeps only the list of Shorts, the subject and the hook title.

   The rest stays in the project: `objects.py`, `timeline.py`, `backdrop.py`, `sfx.py`, `textures.py` and the
   acts. Once the patch is applied to the project itself, step 3 is skipped.
4. `python3 film/build.py` runs in the copy, with `JEV_DRAFT=1` when `--draft` is given. `cmp` compares its
   `film.scene.xml` with one of three references:
   - with `--ab`, a second copy of the project built by its own generators from the same inputs;
   - with `--expect`, the file given;
   - otherwise, the project's own `film.scene.xml`.

   `--validate` also runs `scene-render validate`, which is CPU-only.

`--ab` is the strict test. The project's own scene goes stale whenever its inputs change or it is rebuilt in
another mode. On 2026-09-30 both happened while this test was being written: the physics cache was regenerated,
which adds `cache=` to `<physics>`, and the scene was rebuilt as a draft.

Results at 0.1.0 (2026-09-30):

- Full build against the delivered `film.scene.xml` of 22:08 (sha256 `a628b2c2…`, before the physics cache was
  regenerated): identical.
- `--ab` full build and `--ab --draft`: identical.
- `--draft` against the project's scene as rebuilt at 22:40: identical.
- `scene-render validate --deny-warnings`: 0 errors, 0 warnings.
- `tools/gate.py`: PASS. The evaluations at 0 s, per layout and per variant report no E05/E06, and the flash check
  is on (`warn`). The eight marker probes also pass, but take about 8 CPU-minutes.

The v013 build also registers one 176 px cover-headline text per Short (`hl-s1` … `hl-s6`) that no layer places.
The project, not pnkit, keeps registering it so that the document stays identical.
