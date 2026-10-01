"""foley.py — the channel's own sound effects, synthesised (numpy, scipy, soundfile), 48 kHz stereo.

They are the `kind: file` cues of pnkit/data/sfx_library.json (pnkit.audio): tap, tok, thud, tink, clunk, chime, step,
swish, settle, rumble, cascade, and the beds under, hum and roomlarge.

Design rule (user, 2026-10-01): no laser-like sound. Every sound here is either filtered noise or a struck body with
FIXED modal frequencies; nothing glides in pitch, nothing sustains a pure high tone. They replace AudioForge's
synthetic sweeps and chirps (downlifter, riser, success sting, notification, ui/pop), which pnkit.audio refuses.

    ~/.venvs/voice/bin/python tools/foley.py [OUT_DIR]        (default: sfx/custom under the current directory)

Deterministic (seed 2026): the same files every time. Ends with a spectral self-check and fails if any sound has a
gliding tonal partial. Extracted from v015-short-pack/tools/foley.py; its output there is byte-identical.
"""
import os, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, sosfilt

OUT = os.path.join(os.getcwd(), "sfx", "custom")
SR = 48000


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def band(x, lo=None, hi=None, order=2):
    if lo and hi:
        sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    elif lo:
        sos = butter(order, lo, btype="high", fs=SR, output="sos")
    else:
        sos = butter(order, hi, btype="low", fs=SR, output="sos")
    return sosfiltfilt(sos, x)


def modal(freqs, taus, amps, dur, rng, click=0.0, click_band=(1500, 6000)):
    """a struck body: decaying partials at fixed frequencies and a short noise transient"""
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for f0, tau, a in zip(freqs, taus, amps):
        x += a * np.sin(2 * np.pi * f0 * t + rng.random() * 6.28) * np.exp(-t / tau)
    if click:
        m = int(0.012 * SR)
        c = band(rng.standard_normal(n), *click_band) * 0
        c[:m] = band(rng.standard_normal(m + 2000), *click_band)[1000:1000 + m] * np.hanning(2 * m)[m:]
        x += click * c
    a = int(0.0015 * SR); x[:a] *= np.linspace(0, 1, a)
    return x


def stereo(x, rng, width=0.15):
    """a little decorrelated width: the right channel is the left plus a quiet all-pass-ish copy"""
    d = int(0.0006 * SR)
    r = np.concatenate([np.zeros(d), x[:-d]]) if d else x
    return np.stack([x * (1 - width) + r * width, r * (1 - width) + x * width], -1)


def norm(x, peak_db=-6.0):
    return x / (np.abs(x).max() + 1e-12) * 10 ** (peak_db / 20)


def fade(x, fin=0.002, fout=0.02):
    a, b = int(fin * SR), int(fout * SR)
    x = x.copy(); x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim > 1 else np.linspace(0, 1, a)
    x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim > 1 else np.linspace(1, 0, b)
    return x


def save(name, x, rng=None, peak=-6.0):
    os.makedirs(OUT, exist_ok=True)
    if x.ndim == 1:
        x = stereo(x, rng or np.random.default_rng(1))
    x = fade(norm(x, peak))
    sf.write(os.path.join(OUT, f"{name}.wav"), x.astype(np.float32), SR, subtype="PCM_24")
    return x


def noise_shape(dur, rng, lo, hi, attack, release, colour=0.0):
    """band-limited noise with a smooth rise and fall; colour > 0 tilts it darker"""
    n = int(dur * SR)
    x = rng.standard_normal(n)
    if colour:
        x = np.cumsum(x); x -= np.linspace(x[0], x[-1], n); x = band(x, lo=30)
    x = band(x, lo, hi)
    t = np.arange(n) / SR
    e = np.clip(t / attack, 0, 1) ** 1.5 * np.clip((dur - t) / release, 0, 1) ** 1.5
    return x * e


def build():
    rng = np.random.default_rng(2026)
    made = {}
    # --- struck bodies (fixed modes) -------------------------------------------------------------------------------
    made["tap"] = save("tap", modal([410, 930, 1480], [0.030, 0.018, 0.010], [1.0, 0.45, 0.2], 0.16, rng, click=0.5), rng)             # a muted tap: something appears
    made["tok"] = save("tok", modal([215, 470, 760], [0.060, 0.035, 0.020], [1.0, 0.5, 0.25], 0.26, rng, click=0.35, click_band=(800, 3000)), rng)   # a wooden knock
    made["thud"] = save("thud", modal([62, 95, 140], [0.110, 0.070, 0.040], [1.0, 0.5, 0.25], 0.5, rng, click=0.25, click_band=(200, 900)), rng)     # a soft low thump
    made["tink"] = save("tink", modal([2150, 3480, 5320], [0.050, 0.035, 0.020], [1.0, 0.5, 0.3], 0.22, rng, click=0.3, click_band=(3000, 9000)), rng, peak=-12)  # glass: a filament, a slide
    made["clunk"] = save("clunk", modal([180, 395, 705, 1160, 1890], [0.080, 0.060, 0.045, 0.030, 0.020], [1.0, 0.7, 0.5, 0.3, 0.2], 0.45, rng, click=0.5,
                                        click_band=(600, 4000)), rng)                                                                       # a mechanism stopping
    # a warm two-note wooden confirmation (fixed pitches G4, C5; bar-like partials), for "correct" moments mid-film
    def bar(f0, dur=0.55):
        return modal([f0, f0 * 3.93, f0 * 9.2], [0.16, 0.05, 0.02], [1.0, 0.22, 0.06], dur, rng, click=0.12, click_band=(1500, 5000))
    c = np.zeros(int(0.9 * SR)); a = bar(392.0); b = bar(523.25)
    c[:len(a)] += a; o = int(0.14 * SR); c[o:o + len(b)] += b * 0.9
    made["chime"] = save("chime", c, rng, peak=-9)
    # a footstep on concrete: a thump, a scuff
    st = modal([70, 118], [0.060, 0.035], [1.0, 0.5], 0.3, rng, click=0.0)
    sc = noise_shape(0.09, rng, 1800, 5200, 0.004, 0.08)
    st[:len(sc)] += 0.35 * sc
    made["step"] = save("step", st, rng)
    # --- noise gestures --------------------------------------------------------------------------------------------
    made["swish"] = save("swish", band(noise_shape(0.42, rng, 280, 1500, 0.10, 0.30, colour=1.0), hi=1800), rng, peak=-8)                  # a stroke through water
    made["settle"] = save("settle", noise_shape(1.3, rng, 120, 900, 0.03, 1.25, colour=1.0), rng, peak=-9)                                  # a release: energy letting go
    r = noise_shape(2.0, rng, 35, 160, 1.9, 0.08, colour=1.0)                                                                                 # a low rumble that builds and stops
    made["rumble"] = save("rumble", r, rng, peak=-6)
    n = int(0.7 * SR); cs = np.zeros(n)                                                                                                       # many small things landing in a ripple
    for k in range(14):
        f0 = 380 + 60 * rng.integers(0, 9)
        g = modal([f0, f0 * 2.3], [0.022, 0.012], [1.0, 0.3], 0.1, rng, click=0.4)
        o = int((0.02 + 0.6 * (k / 14) ** 1.3 + 0.01 * rng.random()) * SR)
        cs[o:o + len(g)] += g[:n - o] * (0.5 + 0.5 * rng.random())
    made["cascade"] = save("cascade", cs, rng, peak=-8)
    # --- beds (40 s; the engine cuts them at the film's end) ------------------------------------------------------
    D = 40.0; n = int(D * SR); t = np.arange(n) / SR
    def brown():
        x = np.cumsum(rng.standard_normal(n)); x -= np.linspace(x[0], x[-1], n)
        return band(x, lo=25)
    lfo = 0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t + 1.0) * np.sin(2 * np.pi * 0.031 * t)
    uw = np.stack([band(brown(), 40, 320) * lfo, band(brown(), 40, 320) * np.roll(lfo, SR)], -1)                                             # under water: a low, slow, enclosed wash
    made["under"] = save("under", uw, peak=-14)
    hum = sum(a * np.sin(2 * np.pi * f0 * t + ph) for f0, a, ph in ((100, 1.0, 0.0), (200, 0.35, 1.1), (300, 0.12, 2.0), (50, 0.5, 0.4)))
    hum = hum * (0.9 + 0.1 * np.sin(2 * np.pi * 0.11 * t)) + 0.15 * band(rng.standard_normal(n), 300, 2500) * 0.2
    made["hum"] = save("hum", hum, rng, peak=-16)                                                                                             # mains hum: a live circuit, magnets
    room = np.stack([band(brown(), 60, 1400), band(brown(), 60, 1400)], -1) + 0.25 * np.stack([band(rng.standard_normal(n), 400, 3000)] * 2, -1) * 0.2
    made["roomlarge"] = save("roomlarge", room, peak=-16)                                                                                     # a large hard room: a warehouse, a hall
    return made


def check(made):
    """self-check: no sound may contain a gliding dominant partial (the laser signature)"""
    from scipy.signal import stft
    bad = []
    for name, x in made.items():
        m = x.mean(axis=1)
        f, t, Z = stft(m, SR, nperseg=2048, noverlap=1536)
        P = np.abs(Z) ** 2; tot = P.sum(axis=0); act = tot > tot.max() * 0.05
        ton = float(np.median((np.sort(P, axis=0)[-3:].sum(axis=0) / (tot + 1e-12))[act]))
        dom = f[np.argmax(P, axis=0)][act]
        glide = dom.max() / max(20.0, dom.min()) if len(dom) else 1.0
        cent = float((f[:, None] * P).sum() / P.sum())
        # the laser signature is a tonal partial that moves steadily one way: rank correlation of pitch against time
        if len(dom) > 6:
            rk = lambda v: np.argsort(np.argsort(v)).astype(float)
            trend = float(np.corrcoef(rk(dom), np.arange(len(dom)))[0, 1]) if dom.std() > 0 else 0.0
        else:
            trend = 0.0
        tonal_glide = ton > 0.5 and glide > 1.6 and abs(trend) > 0.8
        print(f"{name:10s} {len(m) / SR:5.2f}s centroid {cent:6.0f} Hz tonality {ton:.2f} dominant {dom.min():5.0f}-{dom.max():5.0f} Hz trend {trend:+.2f} {'GLIDE' if tonal_glide else 'ok'}")
        if tonal_glide:
            bad.append(name)
    return bad


if __name__ == "__main__":
    if len(sys.argv) > 1:
        OUT = os.path.abspath(sys.argv[1])
    bad = check(build())
    print(f"wrote {OUT}")
    raise SystemExit(f"gliding tonal sounds: {bad}" if bad else 0)
