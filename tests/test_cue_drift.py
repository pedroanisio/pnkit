"""tools/cue_drift.py: word-tied score markers against the film's current word timings."""
import json, os, shutil, subprocess, sys, tempfile, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = os.path.join(LIB, "tools", "cue_drift.py")
sys.path.insert(0, os.path.join(LIB, "tools"))
import cue_drift as cd


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def words(scene, start, text, step=0.4, dur=0.3):
    return [{"scene": scene, "text": w, "start": round(start + i * step, 3), "end": round(start + i * step + dur, 3)}
            for i, w in enumerate(text.split())]


FILM = words("s01", 1.0, "São a mesma pessoa. Como uma vida chega") + words("s02", 12.0, "Foram treze dias num caminhão")


class Core(unittest.TestCase):
    def units(self, w=FILM):
        return cd.units_by_scene(w)

    def test_fold_drops_case_accents_and_punctuation(self):
        self.assertEqual(cd.fold("  São, A  MESMA pessoa! "), "sao a mesma pessoa")

    def test_find_phrase_start_and_end_edges(self):
        u = self.units()["s01"]
        self.assertEqual(cd.locate(u, "mesma pessoa", "start"), 1.0 + 2 * 0.4)
        self.assertEqual(cd.locate(u, "mesma pessoa", "end"), round(1.0 + 3 * 0.4 + 0.3, 3))

    def test_phrase_matches_whole_words_only(self):
        self.assertIsNone(cd.locate(self.units()["s01"], "mesm", "start"))

    def test_occurrence_selects_the_nth_match(self):
        u = cd.units_by_scene(words("a", 0, "um dois um dois um"))["a"]
        self.assertEqual(cd.locate(u, "um", "start", occurrence=1), 0.8)
        self.assertIsNone(cd.locate(u, "um", "start", occurrence=3))

    def test_no_drift_passes(self):
        m = [{"id": "a", "scene": "s02", "find": "treze dias", "edge": "start", "time": 12.4}]
        r = cd.compare(m, self.units(), 0.10)
        self.assertEqual((r["markers"], r["drifted"]), (1, []))

    def test_drift_over_tolerance_is_reported_with_delta(self):
        m = [{"id": "a", "scene": "s02", "find": "treze dias", "edge": "start", "time": 12.4 - 0.24}]
        r = cd.compare(m, self.units(), 0.10)
        self.assertEqual([(d["id"], d["delta_s"]) for d in r["drifted"]], [("a", 0.24)])

    def test_tolerance_is_inclusive_despite_float_noise(self):
        m = [{"id": "a", "scene": "s02", "find": "treze", "edge": "start", "time": 12.4 - 0.1}]
        self.assertEqual(cd.compare(m, self.units(), 0.10)["drifted"], [])

    def test_lost_phrase_counts_as_drift(self):
        m = [{"id": "a", "scene": "s02", "find": "quinze dias", "time": 12.8}]
        r = cd.compare(m, self.units(), 0.10)
        self.assertEqual(len(r["drifted"]), 1)
        self.assertFalse(r["drifted"][0]["found"])

    def test_unknown_scene_is_a_problem_not_a_crash(self):
        r = cd.compare([{"id": "a", "scene": "s99", "find": "x", "time": 1}], self.units(), 0.1)
        self.assertEqual(len(r["drifted"]), 1)
        self.assertIn("scene", r["drifted"][0]["problem"])

    def test_marker_without_scene_searches_the_whole_film(self):
        m = [{"id": "a", "find": "caminhão", "edge": "end", "time": 12.0 + 4 * 0.4 + 0.3}]
        self.assertEqual(cd.compare(m, self.units(), 0.1)["drifted"], [])

    def test_lula_proportion_ten_of_thirty_seven(self):
        # a re-voice moves the words after it: 10 of 37 markers drift 0.12-0.49 s, the rest are untouched
        shifts = [0.12, 0.15, 0.2, 0.25, 0.3, 0.33, 0.38, 0.42, 0.46, 0.49]
        film, marks = [], []
        for i in range(37):
            sc = f"s{i:02d}"
            w = words(sc, 10.0 * i, f"alfa{i} beta{i}")
            film += w
            marks.append({"id": sc, "scene": sc, "find": f"beta{i}", "time": w[1]["start"] - (shifts[i] if i < 10 else 0.0)})
        r = cd.compare(marks, cd.units_by_scene(film), 0.10)
        self.assertEqual((r["markers"], len(r["drifted"])), (37, 10))
        self.assertEqual(sorted(abs(d["delta_s"]) for d in r["drifted"]), sorted(shifts))


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pnkit-drift-")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def put(self, name, obj):
        p = os.path.join(self.tmp, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(obj if isinstance(obj, str) else json.dumps(obj))
        return p

    def run_tool(self, *a):
        return subprocess.run([sys.executable, TOOL, *a], capture_output=True, text=True)

    def test_words_format_exit_codes_and_report(self):
        t = self.put("t.json", {"words": FILM})
        ok = self.put("ok.json", {"markers": [{"id": "a", "scene": "s02", "find": "treze dias", "time": 12.4}]})
        bad = self.put("bad.json", {"markers": [{"id": "a", "scene": "s02", "find": "treze dias", "time": 12.2}]})
        self.assertEqual(self.run_tool("--markers", ok, "--timings", t).returncode, 0)
        out = os.path.join(self.tmp, "r.json")
        r = self.run_tool("--markers", bad, "--timings", t, "--out", out)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(load(out)["drifted"][0]["id"], "a")
        self.assertEqual(self.run_tool("--markers", bad, "--timings", t, "--tol", "0.7").returncode, 0)

    def test_default_threshold_is_a_tenth_of_a_second(self):
        self.assertEqual(cd.DEFAULT_TOL, 0.10)

    def test_missing_arguments_exit_2(self):
        self.assertEqual(self.run_tool("--markers", "x").returncode, 2)

    # --- the Lula score's format -------------------------------------------------------------------------------
    MS = ('def s01(c):\n    a = c.at("mesma pessoa", 0.55)\n    b = c.at("como uma vida", 0.78, "end")\n\n'
          'def s02(c):\n    t = c.at("treze dias", 0.4)\n')

    @staticmethod
    def old_t():
        return {"chapters": [{"id": "s01", "voice_start": 0.5, "voice_end": 10.0}, {"id": "s02", "voice_start": 12.0, "voice_end": 30.0}],
                "cues": [{"start": 6.6, "end": 8.1, "text": "São a mesma pessoa."},
                         {"start": 8.4, "end": 10.0, "text": "Como uma vida chega a esses extremos?"},
                         {"start": 14.0, "end": 16.0, "text": "São treze dias num caminhão."}]}

    @staticmethod
    def new_t(d1=0.0, d2=0.0, vs=0.5, drop=False):
        l = [{"caption": "São a mesma pessoa.", "start": 6.6 + d1, "end": 8.1},
             {"caption": "Como uma vida chega a esses extremos?", "start": 8.4, "end": 10.0 + d1}]
        return {"scenes": [{"id": "s01", "voice_start": vs, "voice_end": 10.0, "lines": l},
                           {"id": "s02", "voice_start": 12.0, "voice_end": 30.0,
                            "lines": [] if drop else [{"caption": "São treze dias num caminhão.", "start": 14.0 + d2, "end": 16.0}]}]}

    def lula(self, new, *extra):
        out = os.path.join(self.tmp, "r.json")
        r = self.run_tool("--format", "lula", "--score-timings", self.put("o.json", self.old_t()),
                          "--film-timings", self.put("n.json", new), "--make-score", self.put("ms.py", self.MS), "--out", out, *extra)
        return r.returncode, load(out)

    def test_lula_unchanged_passes(self):
        rc, r = self.lula(self.new_t())
        self.assertEqual((rc, r["markers"], r["drifted"]), (0, 3, []))

    def test_lula_moved_cue_fails_and_names_the_marker(self):
        rc, r = self.lula(self.new_t(d2=0.24))
        self.assertEqual((rc, [d["find"] for d in r["drifted"]], r["drifted"][0]["delta_s"]), (1, ["treze dias"], 0.24))

    def test_lula_small_move_within_tolerance(self):
        self.assertEqual(self.lula(self.new_t(d2=0.05))[0], 0)

    def test_lula_end_marker_uses_end_time(self):
        rc, r = self.lula(self.new_t(d1=0.3))
        self.assertEqual((rc, {d["find"] for d in r["drifted"]}), (1, {"mesma pessoa", "como uma vida"}))

    def test_lula_lost_sentence_and_voice_start_change(self):
        rc, r = self.lula(self.new_t(drop=True, vs=0.7))
        self.assertEqual(rc, 1)
        self.assertTrue(any(not d["found"] for d in r["drifted"]))
        self.assertEqual([tuple(v) for v in r["voice_start_changes"]], [("s01", 0.2)])


if __name__ == "__main__":
    unittest.main()
