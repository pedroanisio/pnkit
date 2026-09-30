# Golden tests

A golden test rebuilds a delivered project with the vendored pnkit and compares the scene it writes with the
delivered one, byte for byte. A release of pnkit must pass every golden test listed here. If a change is meant
to alter output, it must say so in the CHANGELOG and bump the version as a breaking change.

## v013 "How Jev works" (`~/videos/v013-jev-decisions`)

```bash
python3 tests/golden/run_v013.py --validate          # add --work DIR --keep to inspect the rebuilt copy
```

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
4. `python3 film/build.py` runs in the copy. Its `film.scene.xml` must be identical to the project's, as `cmp`
   checks it (sha256 `a628b2c2…` at 0.1.0). `--validate` also runs `scene-render validate`, which is CPU-only.

Result at 0.1.0 (2026-09-30): `cmp` identical. `scene-render validate --deny-warnings`: 0 errors, 0 warnings.
`tools/gate.py`: PASS. The evaluations at 0 s, per layout and per variant report no E05/E06, and the flash check
is on (`warn`). The eight marker probes also pass but take about 8 CPU-minutes.

The v013 build also registers one 176 px cover-headline text per Short (`hl-s1` … `hl-s6`) that no layer places.
The project, not pnkit, keeps registering it so that the document stays identical.
