#!/usr/bin/env python3
"""scopes_check.py — levels of rendered frames or an encoded film, gated on `scene-render scopes` (>= 0.6.0).

    python3 tools/scopes_check.py FILE ... [--step N] [--chroma-limit C] [--max-illegal F]
                                  [--max-out-of-gamut F] [--max-oversaturated F] [--max-clipped F]
                                  [--engine PATH] [--json]

`scene-render scopes` measures a still or a video (every --step-th frame): clipping at black and white, codes
outside the legal range, chroma above the limit and colours outside the gamut, as fractions of the samples.
This wrapper reads its scene-render-cli/1 JSON envelope and fails a file whose fraction exceeds a threshold:

- illegal, out-of-gamut and oversaturated fail above 0 by default (set --max-* to allow a fraction);
- illegal is measured only where the source has a legal range (limited-range Y'CbCr, float); on 8- and 16-bit
  RGB and full-range Y'CbCr there is nothing to measure and nothing is gated;
- clipping is reported but gated only when --max-clipped is given: clipped white can be a legitimate specular,
  so the project decides.

The thresholds are parameters, not a measured precision; as with flat_field.py, a pass is not proof. Exit 0
when every file passes, 1 on a finding, 2 when the engine cannot be run or has no scopes envelope (an engine
before 0.6.0). Run it where the frames are: the render host (pixelart films already run flat_field.py there).
"""
import argparse, json, os, subprocess, sys

DEFAULT_ENGINE = os.path.expanduser("~/.local/share/scene-render/v013/engine/target/release/scene-render")


def engine(path=None):
    import shutil
    for c in (path, os.environ.get("SCENE_RENDER"), shutil.which("scene-render"), DEFAULT_ENGINE):
        if c and os.path.exists(c):
            return c
    print("scopes_check: no scene-render engine (pass --engine or set SCENE_RENDER)", file=sys.stderr)
    sys.exit(2)


def measures(levels):
    """the gated fractions of a scopes result's levels: clipped is the largest black- or white-clipped
    fraction of any channel; illegal is None where the source has no legal range"""
    clip = levels.get("clipping") or {}
    sat = levels.get("saturation") or {}
    clipped = max((v for side in (clip.get("black"), clip.get("white")) if side for v in side.values()),
                  default=0.0)
    return {"clipped": clipped, "illegal": levels.get("illegal"),
            "out_of_gamut": sat.get("out_of_gamut", 0.0), "oversaturated": sat.get("above_limit", 0.0)}


def judge(levels, max_illegal=0.0, max_out_of_gamut=0.0, max_oversaturated=0.0, max_clipped=None):
    """(measures, findings): each finding is (measure, fraction, limit). A None fraction (illegal with no
    legal range) and a None limit (clipping by default) gate nothing."""
    m = measures(levels)
    limits = {"illegal": max_illegal, "out_of_gamut": max_out_of_gamut, "oversaturated": max_oversaturated,
              "clipped": max_clipped}
    findings = [(k, m[k], limits[k]) for k in ("illegal", "out_of_gamut", "oversaturated", "clipped")
                if m[k] is not None and limits[k] is not None and m[k] > limits[k]]
    return m, findings


def run_scopes(sr, path, step, chroma_limit):
    """the scopes result for one file, or an exit-2 message"""
    cmd = [sr, "scopes", "--format", "json", "--step", str(step)]
    if chroma_limit is not None:
        cmd += ["--chroma-limit", str(chroma_limit)]
    r = subprocess.run(cmd + [path], capture_output=True, text=True)
    try:
        env = json.loads(r.stdout)
    except ValueError:
        env = None
    if not (isinstance(env, dict) and env.get("format") == "scene-render-cli/1"):
        return None, f"no scene-render-cli/1 envelope from {sr} (scopes needs scene-render >= 0.6.0)"
    if env.get("exit_code") == 2 or not isinstance(env.get("result"), dict):
        err = env.get("error") or {}
        return None, err.get("message", f"scopes failed on {path}")
    return env["result"], None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("files", nargs="+", help="stills or videos (a video is measured every --step-th frame)")
    ap.add_argument("--step", type=int, default=1, help="measure every Nth frame of a video (default 1)")
    ap.add_argument("--chroma-limit", type=float, help="chroma above which a sample is oversaturated "
                    "(default: the engine's, the largest 75%% colour-bar chroma)")
    ap.add_argument("--max-illegal", type=float, default=0.0, help="largest illegal fraction (default 0)")
    ap.add_argument("--max-out-of-gamut", type=float, default=0.0, help="largest out-of-gamut fraction (default 0)")
    ap.add_argument("--max-oversaturated", type=float, default=0.0, help="largest oversaturated fraction (default 0)")
    ap.add_argument("--max-clipped", type=float, help="largest clipped fraction of any channel "
                    "(default: report only; clipped white can be a legitimate specular)")
    ap.add_argument("--engine", help="scene-render binary")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    args = ap.parse_args()
    sr = engine(args.engine)

    rows, ok = [], True
    for path in args.files:
        result, fault = run_scopes(sr, path, args.step, args.chroma_limit)
        if fault:
            print(f"scopes_check: {fault}", file=sys.stderr); sys.exit(2)
        m, findings = judge(result.get("levels") or {}, args.max_illegal, args.max_out_of_gamut,
                            args.max_oversaturated, args.max_clipped)
        ok = ok and not findings
        rows.append({"file": path, "ok": not findings, "measures": m,
                     "findings": [{"measure": k, "fraction": v, "limit": lim} for k, v, lim in findings],
                     "frames": (result.get("frames") or {}).get("analysed")})

    if args.json:
        print(json.dumps({"ok": ok, "engine": sr, "files": rows}, indent=1))
    else:
        for r in rows:
            m = r["measures"]
            ill = "n/a (no legal range)" if m["illegal"] is None else f"{m['illegal']:.6g}"
            print(f"{'PASS' if r['ok'] else 'FAIL'}  {r['file']}  frames={r['frames']}  clipped={m['clipped']:.6g}"
                  f"  illegal={ill}  out_of_gamut={m['out_of_gamut']:.6g}  oversaturated={m['oversaturated']:.6g}")
            for f in r["findings"]:
                print(f"      {f['measure']} {f['fraction']:.6g} > {f['limit']:.6g}")
        print(f"scopes_check: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
