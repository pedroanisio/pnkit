#!/usr/bin/env python3
"""Build Lula 3.0.0 scene modules against pnkit.pixelart instead of the film's own framework and print each scene's
sha256 (the proof that the extraction changed no output).

    python3 tools/pixelart/lula_alias.py V3_DIR TIMINGS.json SCENES        (SCENES: 01,02 or all)
    python3 tools/pixelart/lula_alias.py --original V3_DIR TIMINGS.json SCENES   the film's own framework, same output
    python3 tools/pixelart/lula_alias.py --c14n V3_DIR TIMINGS.json SCENES       the hash of the C14N 2.0 form (with comments)
    python3 tools/pixelart/lula_alias.py --numeric V3_DIR TIMINGS.json SCENES    the same after plain decimals are written shortest

pnkit 1.0 builds the scene with sr_core.scene, which writes an xs:double in its shortest form ("855", never "855.0"),
so its bytes differ from 0.8.0 in every scene while its C14N form is equal once those decimals are compared shortest:
the golden of 1.0 is `c14n_numeric_sha256`. Every scene is also checked: a level-1 finding aborts the run.

The Lula modules import `common`, `sets`, `scene_art`, `figures_v2`, ...; with the alias they resolve to the pnkit
modules of the same content. Prints one JSON object {scene file: sha256}."""
import hashlib, importlib, json, os, sys

LIB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALIASES = {"common": "ctx", "sets": "sets", "pixel": "geometry", "scene_art": "scene_art", "story_art": "story_art",
           "chapter_art": "chapter_art", "full_art": "full_art", "figures_v2": "figures_v2",
           "figures_v3_pose": "figures_v3_pose", "figures_v3_cast": "figures_v3_cast", "figures_v3_extra": "figures_v3_extra"}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    original = "--original" in argv
    if original:
        argv.remove("--original")
    mode = "bytes"
    for flag, m in (("--c14n", "c14n"), ("--numeric", "numeric")):
        if flag in argv:
            argv.remove(flag); mode = m
    v3, timings, scenes = argv
    v3 = os.path.abspath(v3)
    if original:
        sys.path.insert(0, v3)
        common = importlib.import_module("common")
    else:
        sys.path.insert(0, LIB)
        for old, new in ALIASES.items():
            sys.modules[old] = importlib.import_module(f"pnkit.pixelart.{new}")
        common = sys.modules["common"]
        common.set_timings(timings)
        sys.path.append(v3)                          # scene_NN modules only; the aliases win over the film's files
    if scenes == "all":
        nums = sorted(int(n[6:8]) for n in os.listdir(v3) if n.startswith("scene_") and n.endswith(".py") and n[6:8].isdigit())
    else:
        nums = [int(x) for x in scenes.split(",")]
    out = {}
    for n in nums:
        ctx = common.Ctx(unit=6)
        importlib.import_module(f"scene_{n:02d}").build(ctx)
        ctx.finish()
        data = ctx.tostring()
        if mode != "bytes":
            sys.path.insert(0, os.path.join(LIB, "tests"))
            from c14n import c14n, c14n_numeric
            data = (c14n if mode == "c14n" else c14n_numeric)(data.decode("utf-8")).encode("utf-8")
        if not original:
            bad = [x for x in ctx.check_scene() if x.severity == "error"]
            if bad:
                raise SystemExit(f"scene_{n:02d}: {len(bad)} level-1 error(s): {bad[0].path}: {bad[0].message}")
        out[f"scene_{n:02d}.xml"] = hashlib.sha256(data).hexdigest()
    print(json.dumps(out))


if __name__ == "__main__":
    main()
