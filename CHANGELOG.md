# Changelog

All notable changes to pnkit. Versions follow semantic versioning: a patch release changes no output; a minor
release adds components or parameters and keeps every existing default's output byte-identical (the golden tests
prove it); a change to an existing default's output is a major release until 1.0, and a minor one is never allowed
to hide it. Each release names the golden projects it was checked against.

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
