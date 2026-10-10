"""pnkit.filmbuild.generate — build every scene of a snapshot on CheckedCtx, one scene per Ctx (the per-scene document
the segment renders), in a fresh process so PYTHONHASHSEED is the caller's.

    python3 -m pnkit.filmbuild.generate SRC_DIR OUT_DIR

SRC_DIR is the snapshot (film.json, the timings, scenes/). Writes OUT_DIR/scene_NN.xml, shots-NN.json and
findings.json (the build-time picture findings); prints {"scene_NN.xml": sha256, ...}. A scene module defines
build(ctx) and imports the framework as `from pnkit.pixelart.ctx import ...`.
"""
import hashlib, importlib, json, os, sys

from .state import read_json, write_json, write_bytes


def main(argv=None):
    src, out = (sys.argv[1:] if argv is None else argv)[:2]
    film = read_json(os.path.join(src, "film.json"))
    pic = film.get("picture", {})
    sys.path.insert(0, os.path.join(src, pic.get("scenes_dir", "scenes")))
    from ..pixelart import ctx as C
    from ..pixelart.checks import CheckedCtx
    C.set_timings(os.path.join(src, os.path.basename(film["timings"])))
    os.makedirs(out, exist_ok=True)
    hashes, findings = {}, []
    for sc in film["scenes"]:
        n = sc["n"]
        c = CheckedCtx(unit=pic.get("unit", 6))
        importlib.import_module(sc["module"]).build(c)
        c.finish()
        x = c.tostring()
        write_bytes(os.path.join(out, f"scene_{n:02d}.xml"), x)
        write_json(os.path.join(out, f"shots-{n:02d}.json"), c.shots_json(), indent=1, ensure_ascii=False)
        hashes[f"scene_{n:02d}.xml"] = hashlib.sha256(x).hexdigest()
        findings += c.findings
    write_json(os.path.join(out, "findings.json"), findings, indent=1, ensure_ascii=False)
    print(json.dumps(hashes))


if __name__ == "__main__":
    main()
