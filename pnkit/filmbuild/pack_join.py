#!/usr/bin/env python3
"""join.py (written into a film package by pnkit film_build): join the rendered segments without recoding, mux the
audio, and compare every file with SHA256SUMS.

    python3 join.py            run from the package's project/ folder after the render steps (ffmpeg on PATH)

Exit 0 when the film is byte-identical to the one that was built; 1 when a segment, the audio or the film differs (the
package then rebuilds 'within' the PSNR the rebuild check recorded, not byte for byte; see REBUILD.md); 2 when a file
is missing."""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    sums = {ln.split()[1]: ln.split()[0] for ln in open(os.path.join(HERE, "SHA256SUMS")) if ln.strip()}
    meta = json.load(open(os.path.join(HERE, "film-meta.json")))
    diff = []
    for rel in meta["segments"] + [meta["audio"]]:
        p = os.path.join(HERE, rel)
        if not os.path.exists(p):
            print("missing:", rel); return 2
        if sha(p) != sums.get(rel):
            diff.append(rel)
    os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
    lst = os.path.join(HERE, "output", "concat.txt")
    open(lst, "w").write("".join(f"file '{os.path.join(HERE, s)}'\n" for s in meta["segments"]))
    out = os.path.join(HERE, "output", meta["film_name"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", os.path.join(HERE, meta["audio"]),
                    "-c", "copy", "-map", "0:v", "-map", "1:a", "-movflags", "+faststart", out], check=True)
    if sha(out) != meta["film_sha256"]:
        diff.append("film")
    print("identical to the built film" if not diff else f"differs: {', '.join(diff)}")
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main())
