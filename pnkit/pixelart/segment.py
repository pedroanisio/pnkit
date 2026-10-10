"""pnkit.pixelart.segment — the per-segment render check of a pixel-art film (from Lula p3/check_scene_v3.py, the
"§1b" machine check). It runs on the render VM against the scene's video-only segment, right after the encode.

    python3 -m pnkit.pixelart.segment SEGMENT.mp4 N SHOTS.json OUTDIR [--fps 24] [--bg '#rrggbb'] [--sheet]

Measured on the render (numpy and ffmpeg; Pillow for the plate and flat-field reads):
  near-static spans   mean frame difference < 0.05 grey levels at 480x270; spans of 4 s or more listed, 8 s or more fail
  black or flat       frames with mean luma < 4 or standard deviation < 1
  jumps               frame differences over 8 levels more than 2 frames from a shot start
  first frame         a shot's first frame against its second (picture rows only): a figure or prop missing for a frame
  flat field          the first frame of each shot on the logical grid (frames.flat_field), with the project background
  plates visible      each plate's card at the middle of its window (the end for a growing plate), frames.plate_visible
  hashes              one 64-bit difference hash per second, for the cross-scene repeat check
Measured on the plan file (the shots of a Ctx build): plates and signs at rows <= 146, soles <= 145, no plate over a
sign or a figure active at the same time.
What it cannot judge, and a reader does: signs against the place and date, a figure's state against its era, whether a
prop moves without an agent. Writes OUTDIR/check.json and OUTDIR/hashes.json; --sheet adds 1 s tile sheets.
"""
import argparse, json, os, subprocess, sys

FPS = 24
GW, GH = 480, 270
PICTURE_ROWS = 146 / 180                # the caption band (rows 147-179) changes at sentence starts
STATIC = 0.05


def frame_diffs(x):
    """mean absolute difference of each frame against the previous one (0 for the first)"""
    import numpy as np
    return np.concatenate([[0.0], np.abs(np.diff(x, axis=0)).mean(axis=(1, 2))]) if len(x) else np.zeros(0)


def near_static_spans(d, fps=FPS, t0=0.0, min_s=4.0, thr=STATIC):
    spans, i, n = [], 0, len(d)
    while i < n:
        if d[i] < thr:
            j = i
            while j < n and d[j] < thr:
                j += 1
            if j - i >= min_s * fps:
                spans.append({"from_s": round(t0 + i / fps, 2), "to_s": round(t0 + j / fps, 2), "seconds": round((j - i) / fps, 1)})
            i = j
        else:
            i += 1
    return spans


def black_or_flat(x):
    return int(((x.mean(axis=(1, 2)) < 4) | (x.std(axis=(1, 2)) < 1.0)).sum())


def _blockmax(a, b, rows):
    dd = abs(a - b).astype(float)[:rows]
    h, w = dd.shape; bh, bw = max(1, h // 8), max(1, w // 8)
    return float(max(dd[i * bh:(i + 1) * bh, j * bw:(j + 1) * bw].mean() for i in range(h // bh) for j in range(w // bw)))


def first_frame_defects(x, starts, names, t0=0.0, fps=FPS, picture_rows=None):
    """shots whose first frame differs from the second by a localized block over 10 levels and 3x the next frames' change"""
    rows = picture_rows if picture_rows is not None else int(PICTURE_ROWS * x.shape[1])
    nf, out = len(x), []
    for name, k in zip(names, starts):
        if k + 1 >= nf:
            continue
        b0 = _blockmax(x[k], x[k + 1], rows)
        ref = [_blockmax(x[k + q], x[k + q + 1], rows) for q in range(1, 6) if k + q + 1 < nf]
        top = max(ref) if ref else 0.0
        if b0 > 10 and b0 > 3 * top:
            out.append({"shot": name, "frame": k, "t": round(t0 + k / fps, 3), "block_diff": round(b0, 1), "typical_next_frames": round(top, 1)})
    return out


def jumps(d, starts, t0=0.0, fps=FPS, level=8):
    return [(round(t0 + k / fps, 2), round(float(d[k]), 1)) for k in range(1, len(d))
            if d[k] > level and min(abs(k - s) for s in starts) > 2]


def dhash(tile):
    """16 hex digits: the sign of horizontal differences of a 9 x 8 grey tile"""
    bits = "".join("1" if v else "0" for v in (tile[:, 1:] > tile[:, :-1]).flatten())
    return f"{int(bits, 2):016x}"


def geometry_problems(shots, row_limit=146, sole_limit=145):
    def overlap(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
    def span(a, b, c, e): return a < e and c < b
    bad = []
    for s in shots:
        for p in s["plates"]:
            if p["rect"][3] - 1 > row_limit:
                bad.append(("plate below row 146", s["name"], p["text"]))
            for g in s["signs"]:
                if overlap(p["rect"], g["rect"]):
                    bad.append(("plate over sign", s["name"], p["text"], g["text"]))
            for f in s["figures"]:
                if span(p["start"], p["end"], f["start"], f["end"]) and overlap(p["rect"], f["rect"]):
                    bad.append(("plate over figure", s["name"], p["text"], f["kind"]))
        for f in s["figures"]:
            if f["rect"][3] - 1 > sole_limit:
                bad.append(("figure sole below row 145", s["name"], f["kind"], f["rect"]))
    return bad


# ------------------------------------------------------------------------------------------------ on the render host
def _decode_grey(mp4, vf, w, h):
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8)
    n = len(a) // (w * h)
    return a[: n * w * h].reshape(n, h, w).astype(np.int16)


def _frame_rgb(mp4, t):
    from PIL import Image
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(t, 0):.3f}", "-i", mp4, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    w, h = 1920, 1080
    if len(raw) != w * h * 3:
        raise ValueError(f"frame at {t:.3f}: expected a 1920x1080 frame, got {len(raw)} bytes")
    return Image.frombytes("RGB", (w, h), raw)


def check(mp4, n, shots, out, fps=FPS, bg=None, sheet=False):
    from . import frames
    from .scene_art import P
    os.makedirs(out, exist_ok=True)
    shots = [s for s in shots if s["scene"] == n]
    t0 = shots[0]["start"]
    starts = [int(round((s["start"] - t0) * fps)) for s in shots]
    x = _decode_grey(mp4, f"scale={GW}:{GH}:flags=area", GW, GH)
    d = frame_diffs(x)
    R = {"scene": n, "frames": len(x), "seconds": round(len(x) / fps, 2)}
    spans = near_static_spans(d, fps, t0)
    R["near_static_spans_4s_or_more"] = spans
    R["near_static_8s_or_more"] = [s for s in spans if s["seconds"] >= 8]
    R["black_or_flat_frames"] = black_or_flat(x)
    js = jumps(d, starts, t0, fps)
    R["jumps_over_8_levels_outside_shot_starts"] = js[:10]; R["n_jumps"] = len(js)
    R["first_vs_second_frame_defects"] = first_frame_defects(x, starts, [s["name"] for s in shots], t0, fps)
    R["geometry_problems"] = geometry_problems(shots)
    flat, missing = [], []
    bgc = bg or P["black"]
    for s, k in zip(shots, starts):
        r_ = frames.flat_field(_frame_rgb(mp4, k / fps + 0.5 / fps), frames.parse_rgb(bgc), rows=146)
        if r_["flags"]:
            flat.append({"shot": s["name"], "flags": r_["flags"], "empty_frac": round(r_["empty_frac"], 3),
                         "dominant_frac": round(r_["dominant_frac"], 3)})
        for p in s["plates"]:
            ts = [p["end"] - 1.0 / fps] if p.get("grows") else [p["start"] + (p["end"] - p["start"]) * q for q in (0.25, 0.5, 0.75)]
            res = [frames.plate_visible(_frame_rgb(mp4, t - t0), p["rect"], 6, P["blue0"], P["wood0"]) for t in ts]
            if not any(v["visible"] for v in res):
                missing.append({"shot": s["name"], "plate": p["text"], "reads": res})
    R["flat_field_first_frames"] = flat
    R["plates_missing"] = missing
    R["shots"] = [(s["name"], s["start"], s["end"]) for s in shots]
    tiles = _decode_grey(mp4, "fps=1,scale=9:8:flags=area", 9, 8)
    json.dump({"scene": n, "t0": t0, "hashes": [dhash(t) for t in tiles]}, open(os.path.join(out, "hashes.json"), "w"))
    if sheet:
        _sheet(mp4, n, t0, out)
    R["findings"] = summary(R)
    json.dump(R, open(os.path.join(out, "check.json"), "w"), indent=1, ensure_ascii=False)
    return R


def summary(R):
    """short finding labels of a check.json (empty: clean)"""
    out = []
    if R.get("near_static_8s_or_more"): out.append("still>=8s")
    if R.get("black_or_flat_frames"): out.append(f"black{R['black_or_flat_frames']}")
    if R.get("geometry_problems"): out.append(f"geometry{len(R['geometry_problems'])}")
    if R.get("first_vs_second_frame_defects"): out.append(f"first-frame{len(R['first_vs_second_frame_defects'])}")
    if R.get("flat_field_first_frames"): out.append(f"flat-field{len(R['flat_field_first_frames'])}")
    if R.get("plates_missing"): out.append(f"plate-missing{len(R['plates_missing'])}")
    return out


def _sheet(mp4, n, t0, out, cols=5, per=20):
    import glob
    from PIL import Image, ImageDraw
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf", "fps=1,scale=384:216", os.path.join(out, "t%04d.png")], check=True)
    fr = sorted(glob.glob(os.path.join(out, "t[0-9]*.png")))
    for k in range(0, len(fr), per):
        part = fr[k:k + per]; rows = (len(part) + cols - 1) // cols
        im = Image.new("RGB", (cols * 384, rows * 230), (30, 30, 30)); dr = ImageDraw.Draw(im)
        for q, f in enumerate(part):
            xx, yy = (q % cols) * 384, (q // cols) * 230
            im.paste(Image.open(f), (xx, yy + 14)); dr.text((xx + 2, yy + 1), f"{t0 + k + q:.0f}s", fill=(255, 255, 0))
        im.save(os.path.join(out, f"sheet-{n:02d}-{k // per + 1}.png"))
    for f in fr:
        os.remove(f)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mp4"); ap.add_argument("n", type=int); ap.add_argument("shots"); ap.add_argument("out")
    ap.add_argument("--fps", type=int, default=FPS); ap.add_argument("--bg"); ap.add_argument("--sheet", action="store_true")
    a = ap.parse_args(argv)
    R = check(a.mp4, a.n, json.load(open(a.shots, encoding="utf-8")), a.out, a.fps, a.bg, a.sheet)
    print(json.dumps({"scene": a.n, "findings": R["findings"]}))
    return 1 if R["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
