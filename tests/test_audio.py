"""audio: the palette is well formed, Cues refuses what the audio-design rule forbids (retired cues, anything but soft
struck foley in the ending), its XML is what v015's twenty Shorts were encoded with, and tools/tail_check.py passes a
warm decaying ending and fails a held high tone and a sweep (the laser signatures)."""
import importlib.util, os, sys, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from pnkit import audio


class Data(unittest.TestCase):
    def test_cues_are_well_formed(self):
        names = [c["name"] for c in audio.library()["cues"]]
        self.assertEqual(len(names), len(set(names)))
        for c in audio.library()["cues"]:
            self.assertTrue({"name", "kind", "gain", "class", "tail_ok", "use", "source"} <= set(c), c)
            self.assertIn(c["kind"], ("audioforge", "file"), c)
            self.assertIn(c["class"], ("struck", "noise", "impact", "bed", "sting"), c)
            self.assertTrue({"model", "prompt"} <= set(c) if c["kind"] == "audioforge" else "path" in c, c)
            self.assertTrue(0 < c["gain"] <= 1, c)

    def test_retired_cues_are_gone(self):
        gone = audio.retired()
        self.assertEqual(set(gone), {"down", "riser", "pop", "success", "tone"})
        names = {c["name"] for c in audio.library()["cues"]}
        models = {c.get("model") for c in audio.library()["cues"]}
        for r in audio.library()["retired"]:
            self.assertTrue({"name", "model", "use", "why", "source"} <= set(r), r)
            self.assertNotIn(r["name"], names)
            self.assertNotIn(r["model"], models, "a retired AudioForge cue must not come back under another name")

    def test_the_ending_takes_soft_struck_foley_only(self):
        ok = audio.tail_ok()
        self.assertEqual(ok, {"tick", "click", "stamp", "paper", "pin", "shutter", "tap", "tok", "thud", "step", "clunk", "slide", "scratch"})
        for name in ok:
            self.assertNotIn(audio.cue(name)["class"], ("bed", "sting", "impact"), name)
        self.assertFalse(audio.cue("chime")["tail_ok"])          # warm, but tonal: never after the last word
        with self.assertRaises(KeyError):
            audio.cue("laser")


class Guard(unittest.TestCase):
    def test_retired_and_unknown_names_fail(self):
        c = audio.Cues()
        for name in ("riser", "down", "pop", "success", "tone"):
            with self.assertRaises(audio.AudioDesignError) as e:
                c.sfx(1.0, name)
            self.assertIn("retired", str(e.exception)); self.assertIn("use ", str(e.exception))
        with self.assertRaises(audio.AudioDesignError):
            c.sfx(1.0, "zap")
        with self.assertRaises(audio.AudioDesignError):
            c.ambience("nowhere")
        self.assertEqual(c.sfx_events, [])

    def test_a_project_cannot_bring_a_retired_cue_back(self):
        with self.assertRaises(audio.AudioDesignError):
            audio.Cues(extra={"riser": {"kind": "audioforge", "model": "transition/riser", "prompt": "", "gain": 0.3}})
        with self.assertRaises(audio.AudioDesignError):
            audio.Cues(extra={"door": {"gain": 0.3}})
        c = audio.Cues(extra={"door": {"kind": "file", "path": "sfx/custom/door.wav", "gain": 0.3, "tail_ok": True}})
        c.sfx(29.0, "door")
        self.assertEqual(c.tail_violations(28.5, 32.0), [])

    def test_the_ending(self):
        c = audio.Cues()
        c.sfx(27.9, "whoosh"); c.sfx(28.2, "chime"); c.sfx(28.4, "tick"); c.sfx(29.0, "thud"); c.sfx(31.5, "boom")
        # voice ends at 28.5, the film at 32: the ending starts at 28.0; a cue in the last second is dropped, not judged
        self.assertEqual([n for _, n, _ in c.events(32.0)], ["whoosh", "chime", "tick", "thud"])
        self.assertEqual(c.tail_violations(28.5, 32.0), [(28.2, "chime")])
        with self.assertRaises(audio.AudioDesignError) as e:
            c.check(28.5, 32.0)
        self.assertIn("chime@28.2", str(e.exception))
        ok = audio.Cues(); ok.sfx(28.4, "tick"); ok.sfx(29.0, "thud")
        ok.check(28.5, 32.0)


class Xml(unittest.TestCase):
    def setUp(self):
        self.c = audio.Cues()
        self.c.ambience("room", 0.1)
        self.c.sfx(12.5, "clunk", 0.26); self.c.sfx(0.65, "paper"); self.c.sfx(3.0, "clunk")

    def test_assets(self):
        self.assertEqual(self.c.assets(30.0, tag="s06", digest=lambda n: "ab" * 32), [
            '<audio id="sfx-clunk" src="sfx/custom/clunk.wav"/>',
            '<generated id="sfx-paper" kind="sound-effect" provider="audioforge" model="foley/paper-tap" prompt="duration=0.25 seed=1" '
            f'cache="sfx/paper.wav" cacheSha256="{"ab" * 32}"/>',
            '<audio id="amb-room" src="sfx/custom/bed-s06-room.wav"/>'])
        self.assertIn('cacheSha256="' + "0" * 64, self.c.assets(30.0)[1])       # before the first resolve

    def test_tracks(self):
        self.assertEqual(self.c.tracks(30.0), [
            '<audioTrack id="sfx-000" asset="sfx-paper" role="effects" start="0.65" volume="0.3" bus="fx-bus" duckUnder="vo-bus" duckAmount="-8" duckAttack="0.05" duckRelease="0.4"/>',
            '<audioTrack id="sfx-001" asset="sfx-clunk" role="effects" start="3" volume="0.24" bus="fx-bus" duckUnder="vo-bus" duckAmount="-8" duckAttack="0.05" duckRelease="0.4"/>',
            '<audioTrack id="sfx-002" asset="sfx-clunk" role="effects" start="12.5" volume="0.26" bus="fx-bus" duckUnder="vo-bus" duckAmount="-8" duckAttack="0.05" duckRelease="0.4"/>',
            '<audioTrack id="amb-0" asset="amb-room" role="effects" start="0" volume="0.1" bus="fx-bus" duckUnder="vo-bus" duckAmount="-5" duckAttack="0.2" duckRelease="0.8"/>'])

    def test_a_bed_is_cut_to_the_film(self):
        (dst, argv), = self.c.bed_jobs(30.0, tag="s06")
        self.assertEqual(dst, "sfx/custom/bed-s06-room.wav")
        self.assertEqual(argv, ["ffmpeg", "-v", "error", "-y", "-i", "sfx/room.wav", "-t", "30.000", "-af",
                                "afade=t=in:st=0:d=1.2,afade=t=out:st=27.400:d=2.4", "-c:a", "pcm_s24le", "sfx/custom/bed-s06-room.wav"])
        u = audio.Cues(); u.ambience("under")
        self.assertEqual(u.bed_jobs(20.0)[0][1][5], "sfx/custom/under.wav")       # a foley bed is read from its own file

    def test_read_back_from_a_scene(self):
        xml = "\n".join(self.c.assets(30.0) + self.c.tracks(30.0))
        cues, beds = audio.scene_cues(xml)
        self.assertEqual(cues, [(0.65, "paper"), (3.0, "clunk"), (12.5, "clunk")]); self.assertEqual(beds, ["room"])
        late, bad = audio.scene_tail_violations(xml, 12.8)
        self.assertEqual((late, bad), ([(12.5, "clunk")], []))
        bad_xml = xml + '\n<audioTrack id="sfx-003" asset="sfx-swell" role="effects" start="13" volume="0.2"/>'
        self.assertEqual(audio.scene_tail_violations(bad_xml, 12.8)[1], [(13.0, "swell")])

    def test_resolve_digest(self):
        self.assertEqual(audio.resolve_digest("/nonexistent")("paper"), "0" * 64)


try:
    import numpy as np, scipy  # noqa: F401
    HAVE_DSP = True
except ImportError:
    HAVE_DSP = False


@unittest.skipUnless(HAVE_DSP, "tools/tail_check.py needs numpy and scipy (run the tests in the voice venv to include it)")
class TailCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("tail_check", os.path.join(LIB, "tools", "tail_check.py"))
        cls.m = importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.m)
        cls.rng = np.random.default_rng(1)
        cls.t = np.arange(int(3.4 * cls.m.SR)) / cls.m.SR

    def film(self, tail):
        """3 s of noise for the narration, then the ending under test; the last word ends at 3.0 s"""
        return np.concatenate([0.1 * self.rng.standard_normal(3 * self.m.SR), tail]).astype(np.float32)

    def verdict(self, tail):
        r = self.m.measure(self.film(tail), 3.0)
        return r, self.m.report(r, None, [], "test")[0]

    def test_a_low_chord_dying_away_passes(self):
        t = self.t
        warm = 0.3 * (np.sin(2 * np.pi * 196 * t) + 0.5 * np.sin(2 * np.pi * 294 * t) + 0.3 * np.sin(2 * np.pi * 392 * t)) * np.exp(-t / 0.7)
        r, ok = self.verdict(warm)
        self.assertTrue(ok, r); self.assertLessEqual(r["held"], 0.4); self.assertFalse(r["glide"])

    def test_a_held_high_tone_fails(self):
        t = self.t
        flute = 0.3 * np.sin(2 * np.pi * 1175 * t) * np.clip(1 - t / 3.4, 0, 1) ** 0.3 + 0.01 * self.rng.standard_normal(len(t))
        r, ok = self.verdict(flute)
        self.assertFalse(ok); self.assertGreater(r["held"], 1.0); self.assertGreater(r["share"], 0.4)

    def test_a_sweep_fails(self):
        t = self.t
        freq = 600 * (2400 / 600) ** (t / 3.4)
        sweep = 0.3 * np.sin(2 * np.pi * np.cumsum(freq) / self.m.SR) * np.exp(-t / 2.0)
        r, ok = self.verdict(sweep)
        self.assertFalse(ok); self.assertTrue(r["glide"])

    def test_a_cue_from_the_scene_fails_the_line(self):
        t = self.t
        warm = 0.3 * np.sin(2 * np.pi * 196 * t) * np.exp(-t / 0.7)
        r = self.m.measure(self.film(warm), 3.0)
        ok, line = self.m.report(r, [(3.2, "swell")], [(3.2, "swell")], "test")
        self.assertFalse(ok); self.assertIn("NOT ALLOWED", line)


if __name__ == "__main__":
    unittest.main()
