#!/usr/bin/env python3
"""fake host python for the film_build tests: answers the measuring jobs film_build runs on a render host with canned,
clean results (the real measures need ffmpeg, which this machine must not run)."""
import json, os, sys

args = sys.argv[1:]
mod, rest = args[1], args[2:]
if mod == "pnkit.pixelart.segment":
    mp4, n, shots, out = rest[:4]
    os.makedirs(out, exist_ok=True)
    bad = os.environ.get("FAKE_SEGMENT_FLAG") == f"s{int(n):02d}"
    json.dump({"scene": int(n), "frames": 60, "findings": ["first-frame1"] if bad else []}, open(os.path.join(out, "check.json"), "w"))
    json.dump({"scene": int(n), "hashes": []}, open(os.path.join(out, "hashes.json"), "w"))
elif mod == "pnkit.filmbuild.jobs" and rest[0] == "film-gates":
    film, shots, segs, out = rest[1:5]
    exp = float(rest[rest.index("--expected") + 1])
    segs = json.load(open(segs))
    I = float(os.environ.get("FAKE_LUFS", "-14.0"))
    json.dump({"film": film, "duration": {"video": exp, "audio": exp, "frames": 120, "expected": exp, "fps": 24},
               "loudness": {"I": I, "LRA": 2.0, "true_peak": -1.6}, "black": [], "first_frames": [], "shots": len(json.load(open(shots))),
               "joins": [{"after_scene": s["scene"], "frame": 60, "psnr_db": float("inf")} for s in segs[:-1]]}, open(out, "w"))
elif mod == "pnkit.filmbuild.jobs" and rest[0] == "sheets":
    out = rest[2]
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "film-01.png"), "wb").write(b"\x89PNG fake")
elif mod == "pnkit.filmbuild.jobs" and rest[0] == "psnr":
    print("[]")
else:
    sys.exit(f"fake python: unexpected {args}")
