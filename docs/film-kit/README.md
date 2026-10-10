---
disclaimer:
  notice: >-
    No information within this document should be taken for granted.
    Any statement or premise not backed by a real logical definition
    or verifiable reference may be invalid, erroneous, or a hallucination.
  generated_by: "Claude Opus 5.5 via Claude Code"
  date: "2026-10-10"
---

# The film kit: pixel-art picture framework and film_build

## Disclaimer

This work is subject to the methodological caveats and commitments described in [@DISCLAIMER.md](../../../../../pals-notes-channel/DISCLAIMER.md).
> No statement or premise not backed by a real logical definition or verifiable reference should be taken for granted.

Written for: whoever builds the next pixel-art film. Back to the library: [pnkit README](../../README.md).

The kit is two parts of pnkit 0.8.0. `pnkit.pixelart` is the Lula 3.0.0 picture framework as a library. `pnkit.filmbuild` is a build that one `film.json` drives, in stages that can be restarted. It was proven on a 10 s, two-scene golden film (`PALS-Notes/projects/golden-pixel/`).

## Start a film

1. Copy `PALS-Notes/projects/golden-pixel/` to `PALS-Notes/projects/<slug>/` and edit `film.json`: the film's id, version and title, the scenes, the render hosts, the engine path and its sha256.
2. Write one module per scene in `scenes/`, each with a `build(ctx)` that draws with `pnkit.pixelart.ctx` and `pnkit.pixelart.sets`. A Lula scene module ports by changing its imports only.
3. Write the plan, `SHOTS-<version>.md`, one row per shot (Lula's format; see the golden film). Without narration, write `timings.json` by hand. With narration, the voice stage writes it.
4. Run `python3 PALS-Notes/videos/lib/tools/film_build.py PALS-Notes/projects/<slug>/film.json`. It prints one table. Fix whatever failed and run it again: stages whose inputs did not change are skipped.

## The stages

| Stage | What it does | Where it runs |
|---|---|---|
| snapshot | freezes the inputs into `out/build/src`; refuses a second `timings*.json` | here |
| voice | the pronunciation list first, then one take per scene through the film's TTS command, then the timings (written words with the spoken times) | here (the TTS is the film's command) |
| plan | the plan alone (stacked plates, slots against the timings); the timings diff since the last build | here |
| generate | builds every scene on `CheckedCtx` with two hash seeds (they must agree); runs the picture checks and the waivers, then checks the built shots against the plan | here |
| assemble | one video-only document per scene, plus the audio document and four stems. The score must regenerate bit-identical from its script. With captions, the caption text gate runs here | here |
| render | segments over the hosts, under `flock ~/heavy.lock`; after each encode, the segment check on the host; records sha256, CPU and core count per segment; renders again only the segments that changed | render hosts |
| audio | the audio document and the stems | hub |
| join | lossless join and mux; `out/<name>-vN.mp4`, never overwritten | hub |
| gates | loudness, true peak, black, duration, first frames, PSNR at joins, music layer, voice margin; `out/GATES.md` written from the JSON | hub |
| sheets | 1 s sheets in `out/sheets/<name>-vN/`, for a person to read | hub |
| pack | `out/<id>-<version>.vpkg.zip`, verified; a rebuild check of N segments and the audio from the package itself | hub |

## The picture checks, and the defect each one would have caught

| Check | Lula defect | Function |
|---|---|---|
| zoom view outside the set | 11a: `zoom(2, 276, 76)` showed 36 columns of background | `pnkit.pixel.view_outside`, run by `CheckedCtx.zoom` |
| figure cut at the waist | 11a: crop at row 30 of a 51-row figure | `pnkit.pixel.figure_cut`, run by `CheckedCtx.finish` |
| plate line breaks | 09: "2003: 12,4% → 2010:" / "6,7%" | `pnkit.pixel.plate_line_breaks`, run by `CheckedCtx.plate` and `.box` |
| flat dark field | 11a's first frame, 22 % background | `pnkit.pixelart.frames.flat_field`, on each shot's first rendered frame (segment check) |

A finding is waived in `waivers.json` (`check`, `shot`, `reason`), and a waiver without a reason is refused.

## What it does not do, and what is unverified

- **The crop check only sees cover drawn later in the same group.** A figure placed behind furniture drawn into the set is reported (a false positive): waive it with the reason. Lula's own runner never ran this check (it did not call `finish()`). Through the library it reports crop findings in 18 Lula shots, not all of them defects.
- **The flat-field thresholds** were judged by eye on about 12 frames. They are not the result of a precision study.
- **Captions** are drawn as pixel lettering in the band, and the caption text gate checks them. The golden film has no narration, so this path is covered by unit tests only, not by a rendered film.
- **The voice stage** is tested with a recorded fixture take, not with ElevenLabs.
- **Score cues tied to words** (`tools/cue_drift.py`) and Whisper are not stages yet. Run them by hand when a film has narration.
