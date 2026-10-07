---
disclaimer:
  notice: >-
    No information within this document should be taken for granted.
    Any statement or premise not backed by a real logical definition
    or verifiable reference may be invalid, erroneous, or a hallucination.
  generated_by: "Claude Sonnet 5.5 via Claude Code"
  date: "2026-10-07"
---

# Release notes: feat/audio-ops (proposed for the next minor release)

Not applied: `__version__`, `kit.json` and `CHANGELOG.md` are untouched on this branch. The release owner bumps the
version (a minor release: everything is additive, no existing output changes; the golden test is byte-identical)
and pastes the entries below.

## CHANGELOG entry

```markdown
## 0.7.0 — YYYY-MM-DD — pre-batch checks from the Lula 3.0.0 film

Additive: no existing default's output changes (golden v013 byte-identical).

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
```

## Proposed kit.json entries

Add to `components` (after the `audio.*` entry):

```json
{"name": "files.write_once / files.next_free / files.write_next / files.WriteOnceError", "module": "pnkit.files",
 "summary": "Approved files are write-once: write_once creates a path atomically and raises WriteOnceError (a FileExistsError) if anything is there, even a dangling symlink; next_free returns the path itself when free, else the first of stem-v2.ext, stem-v3.ext, ...; write_next writes to the first free path and returns it.",
 "params": ["write_once(path, data, encoding='utf-8')", "next_free(path, suffix='-v')", "write_next(path, data, suffix='-v', encoding='utf-8')"],
 "rules": ["a file the owner approved is never overwritten by a re-run: write the new version beside it with a suffix"]}
```

Add to `tools`:

```json
"tools/cue_drift.py --markers M.json --timings T.json [--tol 0.10] [--out F]": "compare a score's word-tied cue markers with the film's current word timings (generic JSON format in the docstring); exit 1 when a marker is over --tol seconds off or lost; --format lula --score-timings OLD --film-timings NEW --make-score make_score.py reads the Lula score's c.at() markers",
"tools/vm_preflight.py [HOST ...] [--min-free-gb 20] [--scene S --times 1,5,9 --render-cmd TEMPLATE] [--runner TEMPLATE] [--out vm_preflight.json]": "before a render batch: reachability, free disk, who holds or waits on ~/heavy.lock, CPU model per host (warns when they differ) and a cross-VM frame sha256 probe; one table plus a JSON report; exit 1 on an unreachable host, low disk, a failed render or disagreeing hosts"
```

## What was and was not verified

- All new code is covered by unit tests with fake inputs: `tests/test_files.py`, `tests/test_cue_drift.py`,
  `tests/test_vm_preflight.py` (a fake runner; nothing contacted a VM, `vmrun.sh` and ssh were never run).
- The remote probe script was executed once on this machine with `bash -c` (read-only) to check its syntax and that
  `parse_probe` reads its output. Its behaviour on the VMs (`/proc/locks` format, `ps`, `stat`) is the standard Linux
  behaviour but was not run there.
- The default runner template is `tools/vm/vmrun.sh {host} run {cmd}`: `vmrun.sh` needs the `run` operation word, so
  the template differs from the brief's `{host} {cmd}`.
- The determinism probe's render command is the caller's template: the engine's command line was not read, so no
  engine invocation is shipped. The scene must already be on each host.
- The lock check matches `/proc/locks` entries by inode only (no device number), so an unrelated lock on another
  filesystem with the same inode number could be listed.
- Whether the 10 drifting Lula markers are audible was not tested (the sound review says nobody listened).
