#!/usr/bin/env python3
"""cue_drift.py — is a score still in step with the words the film now says?

A score is built against one set of word times. When the film's timings change afterwards (a re-voiced line, a new
retime) the score keeps the old cue times and no tool says so. Lula 3.0.0: after a re-voice, 10 of the score's 37
word-tied markers sat 0.1-0.49 s from their words. This tool compares each marker with the film's CURRENT timings.
It reads no audio and takes a moment.

    python3 tools/cue_drift.py --markers score-markers.json --timings film-words.json [--tol 0.10] [--out drift.json]
    python3 tools/cue_drift.py --format lula --score-timings OLD.json --film-timings NEW.json --make-score make_score.py

Exit status: 0 when every marker is within --tol seconds of its words; 1 when any marker moved by more than --tol
(default 0.10 s), its phrase no longer exists, or its scene is gone; 2 on a usage error.

Generic format (--format words, the default). Both files are JSON.

  markers file    {"markers": [{"id": "hit-1", "find": "treze dias", "edge": "start", "time": 14.8,
                                "scene": "s02", "occurrence": 0}, ...]}
      find        the words the cue is tied to (case, accents and punctuation do not matter; whole words)
      edge        "start" (the first word's start; default) or "end" (the last word's end)
      time        the time, in seconds, the score uses for this cue
      scene       optional: search only this scene's words (default: the whole film, in file order)
      occurrence  optional, default 0: which match of `find` when it occurs more than once
      id          optional label for the report

  timings file    {"words": [{"text": "treze", "start": 14.8, "end": 15.1, "scene": "s02"}, ...]}
                  ("word" is accepted for "text"; "scene" is optional; times are in the film's own timeline)

Lula format (--format lula): the Lula score's markers are `c.at("sentence text", frac[, "start"|"end"])` calls inside
`def sNN(c):` functions of make_score.py, tied to the caption cues of the timings file the score was built from.
--score-timings is that file ({"chapters": [...], "cues": [...]}) and --film-timings the film's current one
({"scenes": [{"id", "voice_start", "voice_end", "lines": [{"caption", "start", "end"}]}]}; the score's layout is
accepted there too). Each marker's score time is taken from the old file, then compared with the same sentence in the
new one; a scene whose voice start moved is reported as well and also fails the run.

The report (--out JSON) lists every marker: score_s, film_s, delta_s (film minus score), found; "drifted" holds the
ones over the threshold.
"""
import argparse, bisect, json, re, sys, unicodedata

DEFAULT_TOL = 0.10
_EPS = 1e-9   # a delta of exactly the tolerance passes, whatever the float noise


def _json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def fold(s):
    """lower case, no accents, punctuation as a single space"""
    s = "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def units_by_scene(words):
    """[{"text", "start", "end", "scene"?}] -> {scene: [unit, ...]} in file order; scene "" when absent"""
    out = {}
    for w in words:
        text = w.get("text", w.get("word", ""))
        out.setdefault(w.get("scene") or "", []).append({"text": text, "start": float(w["start"]), "end": float(w["end"])})
    return out


def locate(units, find, edge="start", occurrence=0):
    """the time of `find` among units (words, or whole captions), or None. A phrase may span consecutive units."""
    target = fold(find)
    if not target:
        return None
    texts, starts, pos = [], [], 0
    for u in units:
        t = fold(u["text"])
        if not t:
            continue
        texts.append((t, u)); starts.append(pos); pos += len(t) + 1
    joined = " " + " ".join(t for t, _ in texts) + " "     # shifted by one: whole-word search on " target "
    needle, at, n = " " + target + " ", -1, -1
    while n < occurrence:
        at = joined.find(needle, at + 1)         # overlapping matches count
        if at < 0:
            return None
        n += 1
    first, last = at, at + len(target) - 1       # offsets into the unpadded string
    i, j = bisect.bisect_right(starts, first) - 1, bisect.bisect_right(starts, last) - 1
    return texts[j][1]["end"] if edge == "end" else texts[i][1]["start"]


def compare(markers, by_scene, tol=DEFAULT_TOL):
    """-> {"markers": n, "tol_s": tol, "rows": [...], "drifted": [...]}"""
    everything = [u for us in by_scene.values() for u in us]
    rows = []
    for k, m in enumerate(markers):
        base = {"id": m.get("id", f"m{k + 1}"), "scene": m.get("scene") or "", "find": m["find"], "edge": m.get("edge", "start"),
                "score_s": round(float(m["time"]), 3)}
        scene = m.get("scene")
        if scene and scene not in by_scene:
            rows.append(dict(base, found=False, problem=f"scene {scene!r} not in the film's timings"))
            continue
        t = locate(by_scene[scene] if scene else everything, m["find"], base["edge"], int(m.get("occurrence", 0)))
        if t is None:
            rows.append(dict(base, found=False, problem="phrase not found in the film's timings"))
        else:
            rows.append(dict(base, film_s=round(t, 3), delta_s=round(t - float(m["time"]), 3), found=True))
    bad = [r for r in rows if not r["found"] or abs(r["delta_s"]) > tol + _EPS]
    return {"markers": len(rows), "tol_s": tol, "rows": rows, "drifted": bad}


# --- the Lula score's format ------------------------------------------------------------------------------------

def lula_load(path):
    """a timings file in either layout -> {scene: {"S", "V", "units": [{"text","start","end"}]}}"""
    J = _json(path)
    out = {}
    if "scenes" in J:
        for sc in J["scenes"]:
            out[sc["id"]] = {"S": sc["voice_start"], "V": sc["voice_end"],
                             "units": [{"text": l["caption"], "start": l["start"], "end": l["end"]} for l in sc.get("lines", [])]}
    else:
        for ch in J["chapters"]:
            out[ch["id"]] = {"S": ch["voice_start"], "V": ch["voice_end"],
                             "units": [{"text": c["text"], "start": c["start"], "end": c["end"]} for c in J["cues"]
                                       if ch["voice_start"] - 0.05 <= c["start"] <= ch["voice_end"] + 0.05]}
    return out


def lula_markers(path):
    """make_score.py -> [(scene, find, frac, edge)] from its c.at("text", frac[, "start"|"end"]) calls"""
    with open(path, encoding="utf-8") as fh:
        s = fh.read()
    parts = re.split(r"^def (s\d\d)\(c\):", s, flags=re.M)
    res = []
    for i in range(1, len(parts), 2):
        for m in re.finditer(r"c\.at\(\s*\"([^\"]+)\"\s*,\s*([0-9.]+)\s*(?:,\s*\"(start|end)\")?\s*\)", parts[i + 1].split("\ndef ")[0]):
            res.append((parts[i], m.group(1), float(m.group(2)), m.group(3) or "start"))
    return res


def lula_compare(score_timings, film_timings, make_score, tol=DEFAULT_TOL):
    old, new = lula_load(score_timings), lula_load(film_timings)
    markers, missing = [], []
    for k, (sid, find, frac, edge) in enumerate(lula_markers(make_score)):
        mid = f"{sid}:{find}"
        if sid not in old or sid not in new:
            missing.append({"id": mid, "scene": sid, "find": find, "edge": edge, "found": False,
                            "problem": "scene missing in one timings file"})
            continue
        t0 = locate(old[sid]["units"], find, edge)
        if t0 is None:                           # the score's own fallback: a fraction of the scene's voice span
            t0 = old[sid]["S"] + frac * (old[sid]["V"] - old[sid]["S"])
        markers.append({"id": mid, "scene": sid, "find": find, "edge": edge, "time": t0})
    res = compare(markers, {sid: sc["units"] for sid, sc in new.items()}, tol)
    res["rows"] += missing
    res["drifted"] += missing
    res["markers"] += len(missing)
    res["voice_start_changes"] = [(sid, round(new[sid]["S"] - old[sid]["S"], 3)) for sid in old
                                  if sid in new and abs(new[sid]["S"] - old[sid]["S"]) > 1e-3]
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Are a score's word-tied cue markers still on their words?")
    ap.add_argument("--format", choices=["words", "lula"], default="words")
    ap.add_argument("--markers"), ap.add_argument("--timings")
    ap.add_argument("--score-timings"), ap.add_argument("--film-timings"), ap.add_argument("--make-score")
    ap.add_argument("--tol", type=float, default=DEFAULT_TOL, help="seconds (default 0.10)")
    ap.add_argument("--out", help="write the JSON report here")
    a = ap.parse_args(argv)
    need = ("markers", "timings") if a.format == "words" else ("score_timings", "film_timings", "make_score")
    absent = [n for n in need if not getattr(a, n)]
    if absent:
        ap.error("--format %s needs %s" % (a.format, ", ".join("--" + n.replace("_", "-") for n in absent)))
    if a.format == "words":
        res = compare(_json(a.markers)["markers"],
                      units_by_scene(_json(a.timings)["words"]), a.tol)
    else:
        res = lula_compare(a.score_timings, a.film_timings, a.make_score, a.tol)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
    vs = res.get("voice_start_changes", [])
    print(f"{res['markers']} markers; {len(res['drifted'])} drifted over {a.tol} s or lost"
          + (f"; {len(vs)} scenes with a changed voice start" if "voice_start_changes" in res else ""))
    for r in res["drifted"]:
        print("  %-18s %-24s score %s -> film %s (%s)" % (r["id"], r["find"][:24], r["score_s"] if "score_s" in r else "-",
                                                         r.get("film_s", "-"), r.get("problem") or "%+.3f s" % r["delta_s"]))
    for sid, d in vs:
        print(f"  voice start of {sid} moved {d:+.3f} s")
    return 1 if res["drifted"] or vs else 0


if __name__ == "__main__":
    sys.exit(main())
