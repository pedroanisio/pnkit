"""pnkit.filmbuild.gates — the film gates as data: parse what the measuring tools print, judge it against film.json's
thresholds, and write GATES.md from the JSON (never by hand, so the known defects cannot drift from the measured ones).

Measures (taken on the delivered file by jobs.py on the render host): integrated loudness and true peak (ffmpeg
ebur128, peak=true), black frames (blackdetect), duration of picture and sound, first frame against second of every
shot, PSNR at every join (the joined film against the segment files), the voice margin per sentence (voice stem over
the bed, when there is a voice), the music layer (S2 §2.1: a role=music track exists), and the per-segment checks and
build-time picture findings the earlier stages recorded.
"""
import math, re

from .. import __version__ as PNKIT_VERSION


def parse_ebur128(text):
    """{I, LRA, true_peak} from ffmpeg's ebur128=peak=true summary (None for a value it does not print)"""
    i = text.rfind("Summary:")
    s = text[i:] if i >= 0 else text

    def num(pat):
        m = re.search(pat, s)
        return float(m.group(1)) if m else None
    tp = None
    m = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", s)
    if m:
        tp = -math.inf if m.group(1) == "-inf" else float(m.group(1))
    return {"I": num(r"I:\s+(-?[\d.]+) LUFS"), "LRA": num(r"LRA:\s+(-?[\d.]+) LU"), "true_peak": tp}


def parse_blackdetect(text):
    return [{"start": float(a), "end": float(b), "duration": float(c)}
            for a, b, c in re.findall(r"black_start:(-?[\d.]+) black_end:(-?[\d.]+) black_duration:(-?[\d.]+)", text)]


def psnr(a, b):
    """PSNR in dB of two uint8 arrays of one shape (inf when identical)"""
    import numpy as np
    d = (a.astype(np.float64) - b.astype(np.float64)) ** 2
    mse = float(d.mean())
    return math.inf if mse == 0 else 10 * math.log10(255.0 ** 2 / mse)


def voice_margins(full, voice, lines, sr=48000):
    """[(line id, text, start, end, margin dB)]: voice power over bed power (full minus voice) in each sentence's span"""
    import numpy as np
    n = min(len(full), len(voice))
    F, V = full[:n], voice[:n]
    bed = F - V
    out = []
    for ln in lines:
        s0, s1 = int(ln["start"] * sr), int(ln["end"] * sr)
        if s1 > n or s1 <= s0:
            continue
        pv, pb = float(np.mean(V[s0:s1] ** 2)), float(np.mean(bed[s0:s1] ** 2))
        out.append((ln.get("id"), ln.get("text", "")[:60], ln["start"], ln["end"], round(10 * math.log10(max(pv, 1e-20) / max(pb, 1e-20)), 1)))
    return out


def _row(gate, value, rule, ok, note=""):
    return {"gate": gate, "value": value, "rule": rule, "ok": bool(ok), "note": note}


def judge(m, g, segments=None, picture=None, music=None, captions=None, voice=True):
    """rows [{gate, value, rule, ok, note}] from the film measures m (jobs.film_gates JSON), the thresholds g
    (film.json gates), the per-segment findings {scene: [labels]}, the picture findings [{check, shot, waived}], the
    music track ids and the caption gate findings (None: no captions)"""
    rows = []
    lo, hi = g["loudness_lufs"]
    I = m["loudness"]["I"]
    rows.append(_row("integrated loudness", f"{I} LUFS", f"{lo} .. {hi} LUFS", I is not None and lo <= I <= hi))
    tp = m["loudness"]["true_peak"]
    rows.append(_row("true peak (decoded AAC)", f"{tp} dBTP", f"<= {g['true_peak_max_dbtp']} dBTP", tp is not None and tp <= g["true_peak_max_dbtp"]))
    nb = len(m["black"])
    rows.append(_row("black spans (>= 0.2 s)", nb, f"<= {g['black_frames_max']}", nb <= g["black_frames_max"]))
    dv, da = m["duration"]["video"], m["duration"]["audio"]
    want = m["duration"]["expected"]
    ok = dv is not None and da is not None and abs(dv - want) <= 1.0 / m["duration"]["fps"] + 1e-6 and abs(da - want) <= 0.05
    rows.append(_row("duration picture / sound", f"{dv} / {da} s", f"{want} s (1 frame / 50 ms)", ok))
    ff = m["first_frames"]
    rows.append(_row("first frame of each shot", f"{len(ff)} defects of {m['shots']} shots", f"<= {g['first_frame_defects_max']}",
                     len(ff) <= g["first_frame_defects_max"], ", ".join(d["shot"] for d in ff)))
    if m["joins"]:
        worst = min(j["psnr_db"] for j in m["joins"])
        rows.append(_row("PSNR at joins", "inf (identical)" if worst == math.inf else f"min {worst:.1f} dB over {len(m['joins'])} joins",
                         f">= {g['psnr_join_min_db']} dB", worst >= g["psnr_join_min_db"]))
    else:
        rows.append(_row("PSNR at joins", "no joins (one segment)", f">= {g['psnr_join_min_db']} dB", True))
    if music is not None:
        rows.append(_row("music layer (role=music)", ", ".join(music) or "none", "one wordless score track", len(music) >= 1))
    if voice:
        mg = m.get("voice_margin") or []
        low = min((r_[4] for r_ in mg), default=None)
        rows.append(_row("voice margin, lowest sentence", f"{low} dB" if low is not None else "not measured",
                         f">= {g['voice_margin_min_db']} dB", low is not None and low >= g["voice_margin_min_db"]))
    else:
        rows.append(_row("voice margin", "no narration", "n/a", True, "film has no voice"))
    if captions is not None:
        rows.append(_row("caption text = approved text", f"{len(captions)} findings", "0", not captions, "; ".join(map(str, captions[:3]))))
    if segments is not None:
        bad = {k: v for k, v in segments.items() if v}
        rows.append(_row("segment checks (still, black, geometry, first frame, flat field, plates)", f"{len(bad)} of {len(segments)} segments flagged",
                         "0", not bad, "; ".join(f"{k}: {','.join(v)}" for k, v in sorted(bad.items()))))
    if picture is not None:
        open_ = [f for f in picture if not f.get("waived")]
        rows.append(_row("build-time picture checks", f"{len(open_)} open, {len(picture) - len(open_)} waived", "0 open", not open_,
                         "; ".join(f"{f['check']} {f['shot']}" for f in open_[:5])))
    return rows


def gates_md(film, rows, film_file, film_sha, details, generated_date):
    """GATES.md text from the judged rows: the table, then each measure's detail as JSON references"""
    ok = all(r["ok"] for r in rows)
    lines = ["---", "disclaimer:", "  notice: >-", "    No information within this document should be taken for granted.",
             "    Any statement or premise not backed by a real logical definition", "    or verifiable reference may be invalid, erroneous, or a hallucination.",
             f'  generated_by: "pnkit {PNKIT_VERSION} film_build (gates stage), from the gate JSON"', f'  date: "{generated_date}"', "---", "",
             f"# Gates: {film['title']} {film['version']}", "",
             f"Generated from `gates/*.json` by `film_build gates`; do not edit by hand. Film file: `{film_file}`, sha256 `{film_sha}`.", "",
             f"**Result: {'all gates pass' if ok else 'FAIL: ' + ', '.join(r['gate'] for r in rows if not r['ok'])}.** "
             "A pass is a measurement, not a judgement of the picture or the sound: the 1 s sheets and a listen are still read by a person.", "",
             "| Gate | Measured | Rule | Result | Note |", "|---|---|---|---|---|"]
    for r in rows:
        note = str(r["note"]).replace("|", "\\|")
        lines.append(f"| {r['gate']} | {r['value']} | {r['rule']} | {'pass' if r['ok'] else '**FAIL**'} | {note} |")
    lines += ["", "## Where the numbers are", ""]
    for k, v in details:
        lines.append(f"- {k}: `{v}`")
    return "\n".join(lines) + "\n"
