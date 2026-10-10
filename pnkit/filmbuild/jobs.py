"""pnkit.filmbuild.jobs — the measuring jobs film_build runs ON THE RENDER HOST (ffmpeg, numpy, Pillow), never locally.

    python3 -m pnkit.filmbuild.jobs film-gates FILM.mp4 SHOTS.json SEGMENTS.json OUT.json --expected S --fps 24
            [--full full.wav --voice voice.wav --timings timings.json]
    python3 -m pnkit.filmbuild.jobs sheets FILM.mp4 OUTDIR
    python3 -m pnkit.filmbuild.jobs psnr A.mp4 B.mp4 FRAMES        (frame indices, comma-separated)

SEGMENTS.json: [{"scene": n, "path": "seg/s01.mp4", "frames": k}] in film order; joins are the frame indices where one
segment ends and the next begins, compared as the last and first frames of the two segment files against the film.
"""
import argparse, json, math, os, subprocess, sys

from . import gates
from ..pixelart import segment


def _run(argv):
    return subprocess.run(argv, capture_output=True, text=True)


def probe(path):
    out = _run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration,nb_frames", "-of", "json", path]).stdout
    v = a = None
    nb = None
    for s in json.loads(out or "{}").get("streams", []):
        if s.get("codec_type") == "video":
            v = float(s["duration"]) if s.get("duration") else None
            nb = int(s["nb_frames"]) if s.get("nb_frames", "").isdigit() else None
        elif s.get("codec_type") == "audio":
            a = float(s["duration"]) if s.get("duration") else None
    return v, a, nb


def frame_rgb(path, index, w=1920, h=1080):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"select=eq(n\\,{index})", "-fps_mode", "passthrough", "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    if len(raw) != w * h * 3:
        raise ValueError(f"{path} frame {index}: no frame decoded")
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)


def first_frames(path, shots, fps, w=480, h=270):
    """segment.first_frame_defects over the whole film, streaming: only the frames after each shot start are kept"""
    import numpy as np
    starts = sorted({int(round(s["start"] * fps)) for s in shots})
    names = {int(round(s["start"] * fps)): s["name"] for s in shots}
    need = {k + q for k in starts for q in range(7)}
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h}:flags=area", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         stdout=subprocess.PIPE)
    fr, n = {}, 0
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h:
            break
        if n in need:
            fr[n] = np.frombuffer(b, np.uint8).reshape(h, w).astype(np.int16)
        n += 1
    p.wait()
    bad = []
    for k in starts:
        idx = [k + q for q in range(7) if k + q in fr]
        if len(idx) < 2 or idx[1] != k + 1 or idx[0] != k:
            continue
        x = np.stack([fr[i] for i in idx])
        bad += segment.first_frame_defects(x, [0], [names[k]], t0=k / fps, fps=fps)
    return bad, n


def film_gates(a):
    shots = json.load(open(a.shots, encoding="utf-8"))
    segs = json.load(open(a.segments, encoding="utf-8"))
    R = {"film": a.film}
    v, au, nb = probe(a.film)
    R["duration"] = {"video": v, "audio": au, "frames": nb, "expected": a.expected, "fps": a.fps}
    e = _run(["ffmpeg", "-nostats", "-i", a.film, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    R["loudness"] = gates.parse_ebur128(e)
    b = _run(["ffmpeg", "-nostats", "-i", a.film, "-vf", "blackdetect=d=0.2:pix_th=0.05", "-an", "-f", "null", "-"]).stderr
    R["black"] = gates.parse_blackdetect(b)
    R["first_frames"], _ = first_frames(a.film, shots, a.fps)
    R["shots"] = len(shots)
    joins, at = [], 0
    for s, t in zip(segs, segs[1:]):
        at += s["frames"]
        pa = gates.psnr(frame_rgb(a.film, at - 1), frame_rgb(s["path"], s["frames"] - 1))
        pb = gates.psnr(frame_rgb(a.film, at), frame_rgb(t["path"], 0))
        joins.append({"after_scene": s["scene"], "frame": at, "psnr_db": min(pa, pb)})
    R["joins"] = joins
    if a.full and a.voice and a.timings:
        import numpy as np
        def dec(p):
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "2", "-ar", "48000", "-"], capture_output=True, check=True).stdout
            return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
        T = json.load(open(a.timings, encoding="utf-8"))
        lines = [dict(id=f"{sc['n']}.{ln['line']}", text=ln.get("caption", ""), start=ln["start"], end=ln["end"]) for sc in T["scenes"] for ln in sc.get("lines", [])]
        R["voice_margin"] = gates.voice_margins(dec(a.full), dec(a.voice), lines)
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: None)
    print(json.dumps({"I": R["loudness"]["I"], "tp": R["loudness"]["true_peak"], "black": len(R["black"]), "first_frames": len(R["first_frames"]),
                      "joins": [j["psnr_db"] if j["psnr_db"] != math.inf else "inf" for j in joins]}))


def sheets(a):
    import glob
    from PIL import Image, ImageDraw
    os.makedirs(os.path.join(a.out, "t"), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.film, "-vf", "fps=1,scale=384:216", os.path.join(a.out, "t", "t%04d.png")], check=True)
    fr = sorted(glob.glob(os.path.join(a.out, "t", "t*.png")))
    cols, per = 5, 20
    for k in range(0, len(fr), per):
        part = fr[k:k + per]; rows = (len(part) + cols - 1) // cols
        im = Image.new("RGB", (cols * 384, rows * 230), (30, 30, 30)); d = ImageDraw.Draw(im)
        for i, f in enumerate(part):
            x, y = (i % cols) * 384, (i // cols) * 230
            im.paste(Image.open(f), (x, y + 14)); d.text((x + 2, y + 1), f"{k + i}s ({(k + i) // 60}:{(k + i) % 60:02d})", fill=(255, 255, 0))
        im.save(os.path.join(a.out, f"film-{k // per + 1:02d}.png"))
    for f in fr:
        os.remove(f)
    os.rmdir(os.path.join(a.out, "t"))
    print(json.dumps({"tiles": len(fr), "sheets": (len(fr) + per - 1) // per}))


def psnr_cmd(a):
    out = []
    for i in (int(x) for x in a.frames.split(",")):
        out.append({"frame": i, "psnr_db": gates.psnr(frame_rgb(a.a, i), frame_rgb(a.b, i))})
    print(json.dumps([dict(o, psnr_db="inf" if o["psnr_db"] == math.inf else round(o["psnr_db"], 2)) for o in out]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("film-gates")
    for k in ("film", "shots", "segments", "out"):
        g.add_argument(k)
    g.add_argument("--expected", type=float, required=True); g.add_argument("--fps", type=int, default=24)
    g.add_argument("--full"); g.add_argument("--voice"); g.add_argument("--timings")
    s = sub.add_parser("sheets"); s.add_argument("film"); s.add_argument("out")
    p = sub.add_parser("psnr"); p.add_argument("a"); p.add_argument("b"); p.add_argument("frames")
    a = ap.parse_args(argv)
    {"film-gates": film_gates, "sheets": sheets, "psnr": psnr_cmd}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
