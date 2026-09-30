# Changelog

All notable changes to pnkit. Versions follow semantic versioning: a patch release changes no output; a minor
release adds components or parameters and keeps every existing default's output byte-identical (the golden tests
prove it); a change to an existing default's output is a major release until 1.0, and a minor one is never allowed
to hide it. Each release names the golden projects it was checked against.

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
