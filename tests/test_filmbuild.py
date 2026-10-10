"""pnkit.filmbuild (film_build): config, state, the local stages on a two-scene fixture film (tests/fixtures/filmbuild/mini),
and the remote stages end to end against a fake runner (fake_vmrun.py: hosts are folders, the engine, python and ffmpeg are
stand-ins that write small deterministic files; nothing is rendered or encoded on this machine)."""
import io, json, os, shutil, sys, tempfile, unittest, wave, zipfile
from contextlib import redirect_stdout
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from pnkit.filmbuild import config, state, stages, gates, assemble, voice, cli
from pnkit.filmbuild.config import Film, FilmError

FIX = os.path.join(LIB, "tests", "fixtures", "filmbuild")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="filmbuild-")
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.dir = os.path.join(self.tmp, "mini")
        shutil.copytree(os.path.join(FIX, "mini"), self.dir)
        self.env = {"PNKIT_VM_RUNNER": os.path.join(FIX, "bin", "fake_vmrun.py"), "FAKE_VM_ROOT": os.path.join(self.tmp, "vms")}
        os.makedirs(self.env["FAKE_VM_ROOT"])
        self._old = {k: os.environ.get(k) for k in list(self.env) + ["MINI_ZOOM_X", "FAKE_SEGMENT_FLAG", "FAKE_LUFS", "FAKE_ENGINE_FAIL"]}
        os.environ.update(self.env)
        for k in ("MINI_ZOOM_X", "FAKE_SEGMENT_FLAG", "FAKE_LUFS", "FAKE_ENGINE_FAIL"):
            os.environ.pop(k, None)
        self.addCleanup(self._restore)

    def _restore(self):
        for k, v in self._old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def film_json(self, **patch):
        p = os.path.join(self.dir, "film.json")
        d = json.load(open(p))
        for k, v in patch.items():
            d[k] = dict(d.get(k, {}), **v) if isinstance(v, dict) else v
        json.dump(d, open(p, "w"), indent=1)
        return p

    def build(self, *names, force=False):
        b = stages.Build(Film(os.path.join(self.dir, "film.json")), force=force)
        return {r[0]: r for r in stages.run(b, list(names))}, b


class Config(Base):
    def test_loads_with_defaults(self):
        f = Film(os.path.join(self.dir, "film.json"))
        self.assertEqual(f["render"]["hub"], "h1"); self.assertEqual(f["gates"]["true_peak_max_dbtp"], -1.0)
        self.assertEqual(f.out, os.path.join(self.dir, "out"))

    def test_remote_path_with_tilde_is_refused(self):
        self.film_json(render={"remote_dir": "~/film-build/mini"})
        with self.assertRaises(FilmError):
            Film(os.path.join(self.dir, "film.json"))

    def test_captions_without_voice_are_refused(self):
        self.film_json(captions={"enabled": True})
        with self.assertRaisesRegex(FilmError, "captions need word times"):
            Film(os.path.join(self.dir, "film.json"))

    def test_scenes_must_be_numbered_in_order(self):
        self.film_json(scenes=[{"n": 2, "id": "s02", "module": "scene_02"}])
        with self.assertRaises(FilmError):
            Film(os.path.join(self.dir, "film.json"))

    def test_timings_must_tile_the_film(self):
        with self.assertRaisesRegex(FilmError, "starts at"):
            config.check_timings({"scenes": [{"n": 1, "slot_start": 0, "slot_end": 2}, {"n": 2, "slot_start": 2.5, "slot_end": 5}]},
                                 [{"n": 1}, {"n": 2}])


class Ledger(Base):
    def test_fresh_until_an_input_or_output_changes(self):
        L = state.Ledger(self.dir, os.path.join(self.dir, "out"))
        a = os.path.join(self.dir, "timings.json"); o = os.path.join(self.dir, "o.txt"); open(o, "w").write("x")
        L.save("s", {"status": "ok", "inputs": L.hashes([a]), "config": state.sha256_json({"k": 1}), "outputs": L.hashes([o])})
        self.assertTrue(L.fresh("s", L.hashes([a]), {"k": 1}))
        self.assertFalse(L.fresh("s", L.hashes([a]), {"k": 2}))
        open(o, "w").write("y")
        self.assertFalse(L.fresh("s", L.hashes([a]), {"k": 1}))


class LocalStages(Base):
    def test_snapshot_plan_generate_assemble(self):
        rows, b = self.build("snapshot", "voice", "plan", "generate", "assemble")
        self.assertEqual([r[1] for r in rows.values()], ["ran", "skipped", "ran", "ran", "ran"], rows)
        self.assertIn("identical over seeds [0, 1]", rows["generate"][3])
        self.assertIn("score regenerated bit-identical", rows["assemble"][3])
        self.assertIn("music layer: music", rows["assemble"][3])
        x = open(b.p("xml", "s02.scene.xml")).read()
        self.assertIn('start="2.5"', x); self.assertIn('end="5.0"', x); self.assertIn('audio="false"', x)
        a = open(b.p("xml", "full-audio.scene.xml")).read()
        self.assertIn('role="music"', a); self.assertIn('loudness="-14.0"', a)
        self.assertIn('normalize="none"', open(b.p("xml", "stem-music.scene.xml")).read())
        self.assertEqual(json.load(open(b.p("xml", "stems.json"))), ["full", "music"])          # no voice, no sfx: no empty stems
        self.assertFalse(os.path.exists(b.p("xml", "stem-voice.scene.xml")))
        rows2, _ = self.build("snapshot", "voice", "plan", "generate", "assemble")
        self.assertEqual([r[1] for r in rows2.values()], ["cached", "skipped", "cached", "cached", "cached"])

    def test_second_timings_file_is_refused(self):
        open(os.path.join(self.dir, "timings-old.json"), "w").write("{}")
        rows, _ = self.build("snapshot")
        self.assertEqual(rows["snapshot"][1], "FAIL"); self.assertIn("one timings file", rows["snapshot"][3])

    def test_zoom_past_the_set_fails_generate_until_waived(self):
        os.environ["MINI_ZOOM_X"] = "276"
        rows, _ = self.build("snapshot", "plan", "generate")
        self.assertEqual(rows["generate"][1], "FAIL"); self.assertIn("zoom-window-outside-set s02a_rua", rows["generate"][3])
        json.dump([{"check": "zoom-window-outside-set", "shot": "s02a_rua", "reason": "test: intended"}], open(os.path.join(self.dir, "waivers.json"), "w"))
        rows, _ = self.build("snapshot", "plan", "generate")
        self.assertEqual(rows["generate"][1], "ran", rows); self.assertIn("1 waived", rows["generate"][3])

    def test_plan_errors_stop_the_build(self):
        p = os.path.join(self.dir, "SHOTS.md")
        t = open(p).read(); open(p, "w").write(t.replace("0.00-2.50 s", "0.00-2.00 s"))
        rows, _ = self.build("snapshot", "plan")
        self.assertEqual(rows["plan"][1], "FAIL"); self.assertIn("plan spans", rows["plan"][3])

    def test_a_changed_score_without_its_script_fails(self):
        with wave.open(os.path.join(self.dir, "sound", "score.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(b"\0\0" * 800)
        rows, _ = self.build("snapshot", "plan", "generate", "assemble")
        self.assertEqual(rows["assemble"][1], "FAIL"); self.assertIn("not what its script makes", rows["assemble"][3])


class Remote(Base):
    ALL = stages.ORDER

    def test_end_to_end_then_cached_then_one_scene_changed(self):
        rows, b = self.build(*self.ALL)
        self.assertTrue(all(r[1] in ("ran", "skipped") for r in rows.values()), rows)
        self.assertIn("2 of 2 segments rendered", rows["render"][3])
        self.assertTrue(os.path.exists(os.path.join(self.dir, "out", "mini-v1.mp4")))
        self.assertIn("all gates pass", open(os.path.join(self.dir, "out", "GATES.md")).read())
        self.assertIn("generated_by", open(os.path.join(self.dir, "out", "GATES.md")).read())
        rec = json.load(open(b.p("render.json")))
        self.assertEqual({rec["1"]["host"], rec["2"]["host"]}, {"h1", "h2"})
        self.assertTrue(rec["1"]["cpu"] and rec["1"]["cores"] and len(rec["1"]["sha256"]) == 64)
        z = os.path.join(self.dir, "out", "mini-0.1.0.vpkg.zip")
        self.assertIn("byte-identical", rows["pack"][3])
        with zipfile.ZipFile(z) as zz:
            names = zz.namelist()
            self.assertIn("vpkg.json", names); self.assertIn("project/SHA256SUMS", names); self.assertIn("project/REBUILD.md", names)
            self.assertFalse(any(n.endswith(".mp4") for n in names))
            man = json.loads(zz.read("vpkg.json"))
            self.assertEqual(man["package"]["id"], "mini"); self.assertEqual(len(man["pipeline"]["steps"]), 4)
        rows2, _ = self.build(*self.ALL)
        self.assertTrue(all(r[1] in ("cached", "skipped") for r in rows2.values()), rows2)
        p = os.path.join(self.dir, "scenes", "scene_01.py")
        t = open(p).read(); open(p, "w").write(t.replace("ctx.plate(", "ctx.tint(ctx.cur['group'], 'black', 0.1); ctx.plate("))
        rows3, _ = self.build(*self.ALL[:-1])
        self.assertIn("1 of 2 segments rendered", rows3["render"][3], rows3)
        self.assertTrue(os.path.exists(os.path.join(self.dir, "out", "mini-v2.mp4")))
        self.assertTrue(os.path.exists(os.path.join(self.dir, "out", "mini-v1.mp4")), "a full render is never replaced")

    def test_a_flagged_segment_stops_the_render_stage(self):
        os.environ["FAKE_SEGMENT_FLAG"] = "s02"
        rows, _ = self.build(*self.ALL)
        self.assertEqual(rows["render"][1], "FAIL"); self.assertIn("s02", rows["render"][3])
        self.assertNotIn("audio", rows)

    def test_engine_failure_is_reported(self):
        os.environ["FAKE_ENGINE_FAIL"] = "s01"
        rows, _ = self.build(*self.ALL)
        self.assertEqual(rows["render"][1], "FAIL"); self.assertIn("render s01", rows["render"][3])

    def test_loudness_outside_the_range_fails_the_gates(self):
        os.environ["FAKE_LUFS"] = "-10.0"
        rows, _ = self.build(*self.ALL)
        self.assertEqual(rows["gates"][1], "FAIL"); self.assertIn("integrated loudness", rows["gates"][3])
        self.assertIn("**FAIL**", open(os.path.join(self.dir, "out", "GATES.md")).read())

    def test_engine_hash_mismatch_is_refused(self):
        self.film_json(render={"engine_sha256": "0" * 64})
        rows, _ = self.build(*self.ALL)
        self.assertEqual(rows["render"][1], "FAIL"); self.assertIn("engine on", rows["render"][3])

    def test_an_interrupted_render_attaches_to_the_live_worker(self):
        rows, b = self.build("snapshot", "plan", "generate", "assemble")
        h = os.path.join(self.env["FAKE_VM_ROOT"], "h1", "film-build", "mini")
        self.assertFalse(b._attach("h1", [1]))                                # nothing launched yet
        for d in ("xml", "shots", "logs"):
            os.makedirs(os.path.join(h, d), exist_ok=True)
        shutil.copyfile(b.p("xml", "s01.scene.xml"), os.path.join(h, "xml", "s01.scene.xml"))
        shutil.copyfile(b.p("picture", "shots-01.json"), os.path.join(h, "shots", "s01.json"))
        open(os.path.join(h, "logs", "worker.pid"), "w").write(str(os.getpid()))      # a live process
        self.assertTrue(b._attach("h1", [1]))
        open(os.path.join(h, "xml", "s01.scene.xml"), "a").write("<!-- other -->")
        with self.assertRaisesRegex(stages.StageFailed, "other documents"):
            b._attach("h1", [1])

    def test_cli_prints_one_table(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli.main([os.path.join(self.dir, "film.json"), "--to", "generate"])
        self.assertEqual(rc, 0, buf.getvalue())
        out = buf.getvalue().splitlines()
        self.assertTrue(out[1].startswith("stage")); self.assertEqual(len(out), 1 + 2 + 4)


class Voice(Base):
    def test_command_mode_with_a_recorded_take(self):
        nar = {"lang": "pt-br", "scenes": [{"n": 1, "id": "s01", "lines": [{"line": 1, "text": "Em 2003, o PT venceu."}]},
                                          {"n": 2, "id": "s02", "lines": [{"line": 1, "text": "Depois veio a crise."}]}]}
        json.dump(nar, open(os.path.join(self.dir, "narrative.json"), "w"), ensure_ascii=False)
        tts = os.path.join(FIX, "bin", "fixture_tts.py")
        self.film_json(voice={"mode": "command", "script": "narrative.json", "engine": "elevenlabs",
                              "tts": ["{python}", tts, "{scene}", "{text}", "{wav}", "{words}"], "lead": 0.5, "tail": 0.5})
        os.remove(os.path.join(self.dir, "timings.json"))
        rows, b = self.build("snapshot", "voice")
        self.assertEqual(rows["voice"][1], "ran", rows)
        T = json.load(open(os.path.join(self.dir, "timings.json")))
        ln = T["scenes"][0]["lines"][0]
        self.assertEqual([w[0] for w in ln["words"]], ["Em", "2003,", "o", "PT", "venceu."])          # written form, spoken times
        self.assertEqual(T["scenes"][1]["slot_start"], T["scenes"][0]["slot_end"])
        pr = json.load(open(b.p("voice", "pronounce.json")))
        self.assertEqual([t["term"] for t in pr["terms"]][:2], ["PT", "2003"])

    def test_pronounce_groups_names(self):
        t = voice.pronounce_terms("O ABC viu Lula em São Bernardo do Campo.", "pt-br", engine="elevenlabs")
        self.assertIn("São Bernardo do Campo", [x["term"] for x in t["terms"]])


class Gates(unittest.TestCase):
    EBUR = """[Parsed_ebur128_0 @ 0x1] Summary:

  Integrated loudness:
    I:         -14.1 LUFS
    Threshold: -24.3 LUFS

  Loudness range:
    LRA:         3.2 LU

  True peak:
    Peak:       -1.6 dBFS
"""

    def test_parsers(self):
        self.assertEqual(gates.parse_ebur128(self.EBUR), {"I": -14.1, "LRA": 3.2, "true_peak": -1.6})
        self.assertEqual(len(gates.parse_blackdetect("black_start:0 black_end:0.5 black_duration:0.5\nx")), 1)

    def test_psnr_and_margins(self):
        import numpy as np
        a = np.zeros((4, 4, 3), np.uint8); b = a.copy(); b[0, 0, 0] = 10
        self.assertEqual(gates.psnr(a, a), float("inf")); self.assertLess(gates.psnr(a, b), 60)
        t = np.linspace(0, 1, 48000)
        voice_ = np.stack([np.sin(2 * np.pi * 200 * t)] * 2, 1); bed = 0.1 * voice_
        m = gates.voice_margins(voice_ + bed, voice_, [{"id": "1.1", "start": 0.1, "end": 0.9}])
        self.assertAlmostEqual(m[0][4], 20.0, delta=0.2)

    def test_judge_and_md(self):
        m = {"loudness": {"I": -14.0, "true_peak": -1.2}, "black": [], "duration": {"video": 10.0, "audio": 10.0, "expected": 10.0, "fps": 24},
             "first_frames": [], "shots": 3, "joins": [{"psnr_db": float("inf")}]}
        g = config.DEFAULTS["gates"]
        rows = gates.judge(m, g, segments={"s01": []}, picture=[], music=["music"], voice=False)
        self.assertTrue(all(r["ok"] for r in rows), rows)
        rows = gates.judge(m, g, music=[], voice=False)
        self.assertFalse([r for r in rows if r["gate"].startswith("music")][0]["ok"])
        md = gates.gates_md({"title": "T", "version": "1"}, rows, "out/x.mp4", "ab" * 32, [("a", "b")], "2026-10-10")
        self.assertTrue(md.startswith("---\ndisclaimer:")); self.assertIn("FAIL: music layer", md)


class Assemble(unittest.TestCase):
    def test_caption_line_too_wide_raises(self):
        words = [("PALAVRAMUITOLONGASEMESPACOQUENAOCABE" * 2, 0.0, 1.0)]
        with self.assertRaises(ValueError):
            assemble.caption_pages([(words, 0.0, 1.0)], 200)

    def test_music_layer_reads_the_role(self):
        x = assemble.audio_xml({"width": 1920, "height": 1080, "fps": 24}, 5.0, {"score": ("audio/score.wav", "0" * 64)}, [], "score", None,
                               config.DEFAULTS["audio"])
        self.assertEqual(assemble.music_layer(x), ["music"])
        self.assertEqual(assemble.music_layer(assemble.audio_xml({"width": 1, "height": 1, "fps": 24}, 5.0, {}, [], None, None, config.DEFAULTS["audio"])), [])


if __name__ == "__main__":
    unittest.main()
