"""pnkit.audio — a film's sound cues, held to the channel's audio-design rule.

The rule (user, 2026-10-01, after hearing v015's endings as laser beams): every film gets its own sound design, and no
sound may be laser-like: no pitch sweep, no synthetic sting, no sustained pure high tone. After the last word only
soft struck foley may start; then the music resolves.

A Cues object collects a film's effects and beds and refuses what the rule forbids, at build time:

    cues = audio.Cues()
    cues.ambience("room", 0.1)                      # a bed under the whole film
    cues.sfx(t_hit, "clunk", 0.26)                  # a cue from the palette (data/sfx_library.json)
    cues.sfx(t, "riser")                            # AudioDesignError: retired, use rumble or swell
    cues.check(voice_end, duration)                 # AudioDesignError if anything but soft struck foley starts in the ending
    assets, tracks = cues.assets(duration, tag="s07", digest=audio.resolve_digest(ROOT)), cues.tracks(duration)
    cues.bake_beds(ROOT, duration, tag="s07")       # ffmpeg: each bed cut to the film, its fades baked in

The palette is the channel's: AudioForge cues (generated at resolve) and the files tools/foley.py synthesises (struck
bodies with fixed modes and filtered noise; nothing glides). A project adds its own cues with Cues(extra={...}); it
cannot bring a retired name back.

The rule's other half, the ending as it sounds in the encoded file (a held pure tone, a glide, a decay), is measured
by tools/tail_check.py. scene_cues() and scene_tail_violations() read the cues back from a scene document for it.

Standard library only; bake_beds() runs ffmpeg.
"""
import json, os, re, subprocess

from . import sdk
from .sdk import S
from .xml import f

__all__ = ["AudioDesignError", "Cues", "library", "cue", "retired", "tail_ok", "resolve_digest", "scene_cues", "scene_tail_violations"]

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sfx_library.json")
_LIB = None
TAIL_LEAD = 0.5       # the ending starts this long before the last word ends
END_GUARD = 1.0       # a cue that would start in the film's last second is dropped: it could not be heard out
BED_OUT = (2.6, 2.4)  # a bed's fade-out starts this long before the end and lasts this long


class AudioDesignError(ValueError):
    """a cue the audio-design rule does not allow"""


def library():
    """the whole palette, loaded once"""
    global _LIB
    if _LIB is None:
        with open(_DATA, encoding="utf-8") as fh:
            _LIB = json.load(fh)
    return _LIB


def cue(name):
    """one palette entry by name (KeyError if there is none)"""
    for c in library()["cues"]:
        if c["name"] == name:
            return dict(c)
    raise KeyError(name)


def retired():
    """{name: what to use instead} for the cues a film may not name"""
    return {r["name"]: r["use"] for r in library()["retired"]}


def tail_ok():
    """the names allowed to start after the last word: soft struck foley"""
    return {c["name"] for c in library()["cues"] if c.get("tail_ok")}


def resolve_digest(root, cache_dir="sfx"):
    """name -> the SHA-256 that `scene-render resolve` recorded for a generated cue's cache (zeros before the first resolve)"""
    def digest(name):
        p = os.path.join(root, cache_dir, f"{name}.wav.resolve.json")
        if os.path.exists(p):
            with open(p) as fh:
                return json.load(fh).get("sha256") or "0" * 64
        return "0" * 64
    return digest


class Cues:
    """one film's effects and beds"""

    def __init__(self, extra=None, tail_lead=TAIL_LEAD, end_guard=END_GUARD):
        self.lib = {c["name"]: c for c in library()["cues"]}
        gone = retired()
        for name, entry in (extra or {}).items():
            if name in gone:
                raise AudioDesignError(f"audio design: '{name}' is retired (laser-like); use {gone[name]}")
            if entry.get("kind") not in ("audioforge", "file"):
                raise AudioDesignError(f"audio design: '{name}' needs kind audioforge (model, prompt) or file (path)")
            self.lib[name] = dict(entry, name=name)
        self.tail_lead, self.end_guard = tail_lead, end_guard
        self.sfx_events, self.beds = [], []

    def sfx(self, t, name, gain=None):
        """an effect starting at t (film seconds); gain None takes the palette's"""
        gone = retired()
        if name in gone:
            raise AudioDesignError(f"audio design: '{name}' is retired (laser-like); use {gone[name]}")
        if name not in self.lib:
            raise AudioDesignError(f"audio design: unknown effect '{name}'")
        self.sfx_events.append((round(t, 3), name, gain))

    def ambience(self, name, gain=None, fade_in=1.2):
        """a bed under the whole film (room tone, water, hum): the film's world, barely heard"""
        if name not in self.lib:
            raise AudioDesignError(f"audio design: unknown bed '{name}'")
        self.beds.append((name, gain if gain is not None else self.lib[name]["gain"], fade_in))

    def events(self, duration):
        """the effects that play, in time order: those that start before the film's last second"""
        return sorted(e for e in self.sfx_events if e[0] < duration - self.end_guard)

    def tail_violations(self, voice_end, duration):
        """[(t, name)] of the effects that start in the ending and are not soft struck foley"""
        ok = {n for n, c in self.lib.items() if c.get("tail_ok")}
        return [(t, n) for t, n, _ in self.events(duration) if t > voice_end - self.tail_lead and n not in ok]

    def check(self, voice_end, duration):
        """raise AudioDesignError if the ending holds anything but soft struck foley"""
        bad = self.tail_violations(voice_end, duration)
        if bad:
            raise AudioDesignError("audio design: not allowed in the ending: " + ", ".join(f"{n}@{t:.1f}" for t, n in bad))

    def bed_path(self, name, tag):
        return f"sfx/custom/bed-{tag}-{name}.wav"

    def source_path(self, name, cache_dir="sfx"):
        """where a cue's audio is, relative to the project: its file, or the cache resolve writes"""
        c = self.lib[name]
        return c["path"] if c["kind"] == "file" else f"{cache_dir}/{name}.wav"

    def assets(self, duration, tag="film", digest=None, cache_dir="sfx"):
        """the <audio> and <generated> assets: one per effect used (by name), then one per bed"""
        digest = digest or (lambda name: "0" * 64)
        out = []
        for n in sorted({n for _, n, _ in self.events(duration)}):
            c = self.lib[n]
            out.append(sdk.Xml.of(sdk.new(S.Assets, "audio", id=f"sfx-{n}", src=c["path"]) if c["kind"] == "file" else
                                  sdk.new(S.Assets, "generated", id=f"sfx-{n}", kind="sound-effect", provider="audioforge", model=c["model"],
                                          prompt=c["prompt"], cache=f"{cache_dir}/{n}.wav", cacheSha256=digest(n))))
        out += [sdk.Xml.of(sdk.new(S.Assets, "audio", id=f"amb-{n}", src=self.bed_path(n, tag))) for n, _, _ in self.beds]
        return out

    def tracks(self, duration, bus="fx-bus", duck="vo-bus"):
        """the <audioTrack>s: effects duck 8 dB under the voice, beds 5 dB"""
        track = lambda tid, asset, start, vol, amount, attack, release: sdk.Xml.of(sdk.new(
            S.AudioMix, "audioTrack", id=tid, asset=asset, role="effects", start=start, volume=f(vol), bus=bus, duckUnder=duck,
            duckAmount=amount, duckAttack=attack, duckRelease=release))
        out = [track(f"sfx-{i:03d}", f"sfx-{n}", f(max(0.0, t)), g if g is not None else self.lib[n]["gain"], "-8", "0.05", "0.4")
               for i, (t, n, g) in enumerate(self.events(duration))]
        out += [track(f"amb-{i}", f"amb-{n}", "0", g, "-5", "0.2", "0.8") for i, (n, g, _) in enumerate(self.beds)]
        return out

    def bed_jobs(self, duration, tag="film", cache_dir="sfx"):
        """[(destination, ffmpeg argv)]: each bed cut to the film's length with its fades baked in. A track's fadeOut acts
        at the end of its asset, not of the document, so a 40 s bed under a 30 s film would otherwise sound to the last frame."""
        jobs = []
        for n, _, fade_in in self.beds:
            dst = self.bed_path(n, tag)
            jobs.append((dst, ["ffmpeg", "-v", "error", "-y", "-i", self.source_path(n, cache_dir), "-t", f"{duration:.3f}", "-af",
                               f"afade=t=in:st=0:d={fade_in},afade=t=out:st={duration - BED_OUT[0]:.3f}:d={BED_OUT[1]}", "-c:a", "pcm_s24le", dst]))
        return jobs

    def bake_beds(self, root, duration, tag="film", cache_dir="sfx"):
        """run bed_jobs() in the project directory; returns the files written"""
        done = []
        for dst, argv in self.bed_jobs(duration, tag, cache_dir):
            os.makedirs(os.path.join(root, os.path.dirname(dst)), exist_ok=True)
            subprocess.run(argv, cwd=root, check=True)
            done.append(dst)
        return done


_TRACK = re.compile(r'<audioTrack id="sfx-\d+" asset="sfx-([A-Za-z0-9_-]+)" role="effects" start="([\d.]+)"')
_BED = re.compile(r'<audioTrack id="amb-\d+" asset="amb-([A-Za-z0-9_-]+)"')


def scene_cues(xml):
    """([(start, name)] in document order, [bed names]) read back from a scene document written with Cues.tracks()"""
    return [(float(t), n) for n, t in _TRACK.findall(xml)], _BED.findall(xml)


def scene_tail_violations(xml, voice_end, tail_lead=TAIL_LEAD, allowed=None):
    """(late, bad): the effects that start in the ending, and those among them that are not soft struck foley"""
    ok = tail_ok() if allowed is None else set(allowed)
    late = [(t, n) for t, n in scene_cues(xml)[0] if t > voice_end - tail_lead]
    return late, [(t, n) for t, n in late if n not in ok]
