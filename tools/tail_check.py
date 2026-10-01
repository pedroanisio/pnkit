#!/usr/bin/env python3
"""tail_check.py — a film's ending, as it sounds in the encoded file, against the audio-design rule (no laser-like
endings; user, 2026-10-01). pnkit.audio refuses the wrong cues at build time; this measures what was rendered.

    ~/.venvs/voice/bin/python tools/tail_check.py MEDIA --voice-end 28.53 [--scene SCENE.xml] [--out FILE] [--label NAME]
    ~/.venvs/voice/bin/python tools/tail_check.py MEDIA --timings vo/film.timings.json [--lead 0.6] ...

From the last word (--voice-end, film seconds; or --lead plus the "duration" in a timings JSON) to the last frame:
  1. cues (with --scene): every effect that starts after the last word minus 0.5 s must be soft struck foley
     (pnkit.audio.tail_ok());
  2. held tone: no single partial above 380 Hz may hold more than 35 % of the energy for longer than 0.4 s, and the mean
     share of the strongest such partial must stay at or under 30 %;
  3. glide: no tonal partial above 500 Hz may move steadily in one direction (rank correlation of pitch against time
     above 0.8 over a ratio of 1.5 or more, in small steps, while tonal): the sweep / zap signature;
  4. decay: the last 0.1 s is at least 15 dB under the level 2 s earlier.
Prints one line, writes it to --out if given, exits 0 on PASS and 1 on CHECK.

Calibration (v015, 2026-10-01): the endings the user heard as laser beams (a phrase doubled by a high sustained flute)
held one partial for 1.0-1.2 s at a 41-63 % mean share; the redesigned endings measure at most 0.21 s and 7-18 %.

Needs numpy, scipy and ffmpeg (the voice venv has the first two). Extracted from v015-short-pack/qa/tail.py; on that
pack's twenty files it gives the same figures.
"""
import argparse, json, os, subprocess, sys

import numpy as np
from scipy.signal import stft

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from pnkit import audio

SR = 24000
HELD_MAX, SHARE_MAX, DECAY_DB = 0.4, 0.3, 15.0


def load(path):
    """the file's audio, mono, at SR"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def measure(x, voice_end):
    """the ending's figures: tail seconds, longest held pure partial (s), its mean share, energy above 1.5 kHz, glide, levels"""
    seg = x[int(voice_end * SR):]
    f, t, Z = stft(seg, SR, nperseg=4096, noverlap=3072)
    P = np.abs(Z) ** 2
    tot = P.sum(axis=0); act = tot > tot.max() * 0.01
    hi_ = f > 380; fr, pu, lv = [], [], []
    for k in range(P.shape[1]):
        col = P[:, k]; tot_ = col[f > 120].sum() + 1e-12; i = int(np.argmax(col * hi_))
        fr.append(f[i]); pu.append(col[max(0, i - 2):i + 3].sum() / tot_); lv.append(10 * np.log10(tot_))
    fr, pu, lv = np.array(fr), np.array(pu), np.array(lv)
    loud = lv > lv.max() - 20
    best = run = 0; f0 = None
    for a_, p_, l_ in zip(fr, pu, loud):
        if l_ and p_ > 0.35 and (f0 is None or abs(a_ - f0) < 0.03 * f0):
            run += 1; f0 = a_ if f0 is None else f0
        else:
            run, f0 = (1, a_) if (l_ and p_ > 0.35) else (0, None)
        best = max(best, run)
    held, share = best * 1024 / SR, float(np.mean(pu[loud]))
    band = f > 500
    dom = f[band][np.argmax(P[band], axis=0)][act]
    ton = (np.sort(P[band], axis=0)[-3:].sum(axis=0) / (P[band].sum(axis=0) + 1e-12))[act]
    glide = False
    if len(dom) > 12:                                                # any 1.5 s stretch with a steady tonal slide
        w = int(1.5 * SR / 1024)
        rk = lambda v: np.argsort(np.argsort(v)).astype(float)
        for i in range(0, len(dom) - w, max(1, w // 3)):
            d = dom[i:i + w]
            if d.std() > 0 and np.median(ton[i:i + w]) > 0.5 and d.max() / max(50.0, d.min()) >= 1.5:
                steps = np.diff(d)
                smooth = np.mean(np.abs(steps) < 0.12 * d[:-1])        # a glide moves in small steps; a melody jumps and holds
                if abs(np.corrcoef(rk(d), np.arange(len(d)))[0, 1]) > 0.8 and smooth > 0.9 and np.mean(steps != 0) > 0.5:
                    glide = True
    rms = lambda a: 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-9)
    return dict(tail=len(seg) / SR, held=held, share=share, high=float(P[f > 1500].sum() / max(1e-12, P.sum())), glide=glide,
                last=rms(x[-int(0.1 * SR):]), before=rms(x[-int(2.1 * SR):-int(1.9 * SR)]))


def report(m, late, bad, label):
    ok = not bad and m["held"] <= HELD_MAX and m["share"] <= SHARE_MAX and not m["glide"] and m["last"] < m["before"] - DECAY_DB
    cues = "not checked (no --scene)" if late is None else ([f"{n}@{t:.1f}" for t, n in late] or "none")
    line = (f"{label} tail {m['tail']:.1f} s: cues after the last word {cues}"
            f"{' NOT ALLOWED ' + str([f'{n}@{t:.1f}' for t, n in bad]) if bad else ''}; longest held pure partial {m['held']:.2f} s, "
            f"mean share {m['share'] * 100:.0f} %; energy above 1.5 kHz {m['high'] * 100:.1f} %; glide {'YES' if m['glide'] else 'no'}; "
            f"last 0.1 s {m['last']:.0f} dBFS vs {m['before']:.0f} -> {'PASS' if ok else 'CHECK'}")
    return ok, line


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("media", help="the encoded film (anything ffmpeg reads)")
    ap.add_argument("--voice-end", type=float, help="when the last word ends, film seconds")
    ap.add_argument("--timings", help="a narration timings JSON with a 'duration'; the last word ends at --lead plus it")
    ap.add_argument("--lead", type=float, default=0.6, help="where the narration starts in the film (with --timings; default 0.6)")
    ap.add_argument("--scene", help="the scene document, to check the cues that start in the ending")
    ap.add_argument("--out", help="write the line here too")
    ap.add_argument("--label", help="what to call the film in the line (default: the media file's name)")
    args = ap.parse_args()
    if args.voice_end is None and not args.timings:
        ap.error("give --voice-end or --timings")
    ve = args.voice_end if args.voice_end is not None else args.lead + json.load(open(args.timings))["duration"]
    late = bad = None
    if args.scene:
        late, bad = audio.scene_tail_violations(open(args.scene, encoding="utf-8").read(), ve)
    ok, line = report(measure(load(args.media), ve), late, bad or [], args.label or os.path.basename(args.media))
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        open(args.out, "w").write(line + "\n")
    print(line)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
