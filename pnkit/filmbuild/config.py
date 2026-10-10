"""pnkit.filmbuild.config — film.json: one file that drives a film's build. Paths are relative to the file's folder;
remote paths are relative to the render host's $HOME (never `~`, never absolute: a `~` inside a quoted remote path once
expanded on the wrong side and wiped a home folder). No host, path or engine is built into the tool.

    {"film":    {"id", "version", "title", "lang", "description"},
     "timings": "timings.json",                      the one timings file (scenes: n, id, slot_start, slot_end[, lines])
     "scenes":  [{"n": 1, "id": "s01", "module": "scene_01"}, ...],
     "picture": {"framework": "pnkit.pixelart", "scenes_dir", "plan", "waivers", "fps": 24, "unit": 6,
                 "background": "#rrggbb" (default: the palette's black), "determinism_seeds": [0, 1]},
     "voice":   {"mode": "none"} | {"mode": "command", "script": "narrative.json", "tts": [argv with {scene} {text}
                 {wav} {words}], "pronounce": [argv with {term} {wav}] (optional), "lead": 0.5, "tail": 0.8},
     "captions": {"enabled": false} | {"enabled": true, "width": 42, "lang": "pt-br"},
     "audio":   {"score": "sound/score.wav", "score_script": [argv with {out}], "sfx": null, "music_gain": -13,
                 "music_duck": -8, "sfx_gain": -9, "duck_attack": 0.08, "duck_release": 1.0, "normalize": -14,
                 "true_peak": -1.5},
     "render":  {"hosts": ["prod"], "hub": "prod", "runner": "tools/vm/vmrun.sh", "remote_dir": "film-build/<id>",
                 "lock": "heavy.lock", "engine": "engine/<release>/scene-render", "engine_sha256": "...",
                 "python": "venv/bin/python", "env": {"SR_GPU_BACKEND": "vulkan"}, "encode_args": [...],
                 "poll_s": 15, "timeout_s": 7200},
     "gates":   {"loudness_lufs": [-15, -13], "true_peak_max_dbtp": -1.0, "black_frames_max": 0,
                 "voice_margin_min_db": 11, "psnr_join_min_db": 40, "first_frame_defects_max": 0},
     "out":     {"dir": "out", "name": "<id>"},
     "pack":    {"rebuild_segments": 1, "file_to": null}}
"""
import copy, json, os

from .state import read_json

DEFAULTS = {
    "picture": {"framework": "pnkit.pixelart", "scenes_dir": "scenes", "plan": None, "waivers": None, "fps": 24, "unit": 6,
                "background": None, "determinism_seeds": [0, 1]},
    "voice": {"mode": "none", "lead": 0.5, "tail": 0.8},
    "captions": {"enabled": False, "width": 42, "lang": "pt-br"},
    "audio": {"score": None, "score_script": None, "sfx": None, "music_gain": -13.0, "music_duck": -8.0, "sfx_gain": -9.0,
              "duck_attack": 0.08, "duck_release": 1.0, "normalize": -14.0, "true_peak": -1.5},
    "render": {"hub": None, "runner": "tools/vm/vmrun.sh", "lock": "heavy.lock", "python": "venv/bin/python", "env": {},
               "encode_args": ["--strict", "--no-upload", "--quality", "final", "--parallel", "2", "--hw", "software"],
               "poll_s": 15, "timeout_s": 7200, "engine_sha256": None, "engine_version": None},
    "gates": {"loudness_lufs": [-15.0, -13.0], "true_peak_max_dbtp": -1.0, "black_frames_max": 0, "voice_margin_min_db": 11.0,
              "psnr_join_min_db": 40.0, "first_frame_defects_max": 0},
    "out": {"dir": "out", "name": None},
    "pack": {"rebuild_segments": 1, "file_to": None},
}


class FilmError(ValueError):
    """film.json is missing something or contradicts itself"""


def _merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def _remote_ok(p, what):
    if not isinstance(p, str) or not p or p.startswith("/") or "~" in p or ".." in p.split("/"):
        raise FilmError(f"{what} {p!r}: a remote path is relative to the host's $HOME, without '~', '/' at the start or '..'")


class Film:
    def __init__(self, path):
        self.file = os.path.abspath(path)
        self.root = os.path.dirname(self.file)
        try:
            raw = read_json(self.file)
        except (OSError, ValueError) as e:
            raise FilmError(f"cannot read {path}: {e}")
        self.raw = raw
        for k in ("film", "timings", "scenes", "render"):
            if k not in raw:
                raise FilmError(f"film.json: '{k}' is required")
        d = {k: raw[k] for k in raw}
        for k, v in DEFAULTS.items():
            d[k] = _merge(v, raw.get(k))
        self.d = d
        f = d["film"]
        for k in ("id", "version", "title"):
            if not f.get(k):
                raise FilmError(f"film.json: film.{k} is required")
        if d["out"]["name"] is None:
            d["out"]["name"] = f["id"]
        ns = [s["n"] for s in d["scenes"]]
        if ns != list(range(1, len(ns) + 1)):
            raise FilmError(f"film.json: scenes must be numbered 1..N in order, got {ns}")
        for s in d["scenes"]:
            for k in ("id", "module"):
                if not s.get(k):
                    raise FilmError(f"film.json: scene {s['n']} needs '{k}'")
        r = d["render"]
        if not r.get("hosts"):
            raise FilmError("film.json: render.hosts is required (the render hosts, by the runner's names)")
        r["hub"] = r["hub"] or r["hosts"][0]
        for k in ("remote_dir", "engine"):
            if k not in r:
                raise FilmError(f"film.json: render.{k} is required")
        for k in ("remote_dir", "engine", "lock", "python"):
            _remote_ok(r[k], f"render.{k}")
        v = d["voice"]
        if v["mode"] not in ("none", "command"):
            raise FilmError(f"film.json: voice.mode {v['mode']!r} is not 'none' or 'command'")
        if v["mode"] == "command" and not (v.get("tts") and v.get("script")):
            raise FilmError("film.json: voice mode 'command' needs voice.script and voice.tts")
        if d["captions"]["enabled"] and v["mode"] == "none":
            raise FilmError("film.json: captions need word times, so a narration (voice.mode 'command')")
        if d["picture"]["framework"] != "pnkit.pixelart":
            raise FilmError(f"film.json: picture.framework {d['picture']['framework']!r}: only 'pnkit.pixelart' is built in")

    def __getitem__(self, k):
        return self.d[k]

    @property
    def id(self):
        return self.d["film"]["id"]

    @property
    def version(self):
        return self.d["film"]["version"]

    def path(self, rel):
        """a film-relative path made absolute (None stays None)"""
        if rel is None:
            return None
        return rel if os.path.isabs(rel) else os.path.normpath(os.path.join(self.root, rel))

    @property
    def out(self):
        return self.path(self.d["out"]["dir"])

    @property
    def build(self):
        return os.path.join(self.out, "build")

    def timings(self):
        t = read_json(self.path(self.d["timings"]))
        check_timings(t, self.d["scenes"])
        return t


def check_timings(t, scenes):
    """the timings cover the film's scenes, in order, with slots that tile the film"""
    if not isinstance(t, dict) or not isinstance(t.get("scenes"), list):
        raise FilmError('timings: expected {"scenes": [...]}')
    got = [s.get("n") for s in t["scenes"]]
    want = [s["n"] for s in scenes]
    if got != want:
        raise FilmError(f"timings: scenes {got}, film.json has {want}")
    prev = 0.0
    for s in t["scenes"]:
        a, b = s.get("slot_start"), s.get("slot_end")
        if a is None or b is None or b <= a:
            raise FilmError(f"timings: scene {s['n']} needs slot_start < slot_end")
        if abs(a - prev) > 1e-6:
            raise FilmError(f"timings: scene {s['n']} starts at {a}, the one before ends at {prev}")
        prev = b
    return t
