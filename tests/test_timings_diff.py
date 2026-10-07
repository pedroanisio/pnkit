"""tools/timings_diff.py: sentences and words whose start or end moved by more than a threshold."""
import importlib.util, json, os, subprocess, sys, tempfile, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
spec = importlib.util.spec_from_file_location("timings_diff", os.path.join(LIB, "tools", "timings_diff.py"))
td = importlib.util.module_from_spec(spec); spec.loader.exec_module(td)

LULA = "/home/admin/src/render-frontend-js/PALS-Notes/projects/lula-filme/p3/audio"


def simple(shift=0.0, drop=False):
    words = [["o", 1.0, 1.1], ["desemprego", 1.2, 1.8], ["cai", 1.9 + shift, 2.2 + shift]]
    if drop:
        words = words[:2]
    return [{"sentence": "a", "text": "o desemprego cai", "words": words},
            {"sentence": "b", "text": "fim", "words": [["fim", 5.0, 5.4]]}]


class Diff(unittest.TestCase):
    def test_identical(self):
        r = td.diff(simple(), simple())
        self.assertEqual(r["sentences"], []); self.assertEqual(r["words"], []); self.assertFalse(r["moved"])

    def test_threshold(self):
        r = td.diff(simple(), simple(0.10))
        self.assertFalse(r["moved"])
        r = td.diff(simple(), simple(0.20))
        self.assertTrue(r["moved"])
        self.assertEqual([s["sentence"] for s in r["sentences"]], ["a"])
        s = r["sentences"][0]
        self.assertAlmostEqual(s["end_delta"], 0.20, 3); self.assertAlmostEqual(s["start_delta"], 0.0, 3)
        self.assertEqual([(w["word"], w["index"]) for w in r["words"]], [("cai", 2)])
        r = td.diff(simple(), simple(0.20), threshold=0.25)
        self.assertFalse(r["moved"])

    def test_structure_changes(self):
        r = td.diff(simple(), simple(drop=True))
        self.assertTrue(r["moved"])
        self.assertEqual(r["sentences"][0]["words_changed"], "3 -> 2 words")
        r = td.diff(simple(), simple()[:1])
        self.assertEqual(r["only_a"], ["b"])

    def test_lula_adapter(self):
        d = {"scenes": [{"id": "s16", "n": 16, "lines": [{"line": 2, "caption": "Um dois três.", "words": [["Um", 10.0], ["dois", 10.5], ["três.", 11.0]], "start": 10.0, "end": 11.6}]}]}
        out = td.load_sentences(d)
        self.assertEqual(out[0]["sentence"], "16.2")
        self.assertEqual(out[0]["text"], "Um dois três.")
        self.assertEqual(out[0]["words"], [["Um", 10.0, 10.5], ["dois", 10.5, 11.0], ["três.", 11.0, 11.6]])
        self.assertEqual(td.load_sentences(simple()), simple())

    def test_bad_format(self):
        with self.assertRaises(ValueError):
            td.load_sentences({"nothing": 1})
        with self.assertRaises(ValueError):
            td.load_sentences([{"sentence": "a"}])

    @unittest.skipUnless(os.path.exists(LULA + "/timings-v2.json") and os.path.exists(LULA + "/timings-v2.2.json"), "Lula timings not on this machine")
    def test_lula_real(self):
        a = td.load_sentences(json.load(open(LULA + "/timings-v2.2.json")))
        b = td.load_sentences(json.load(open(LULA + "/timings-v2.json")))
        self.assertEqual(len(a), 129)
        r = td.diff(a, b)
        moved = {s["sentence"] for s in r["sentences"]}
        # v2.5 takes scenes 16 and 23 from v2.2 (CHANGES.md): nothing moves there
        self.assertFalse([m for m in moved if m.split(".")[0] in ("16", "23")], moved)
        self.assertTrue(moved)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            pa, pb = os.path.join(d, "a.json"), os.path.join(d, "b.json")
            json.dump(simple(), open(pa, "w")); json.dump(simple(0.3), open(pb, "w"))
            tool = os.path.join(LIB, "tools", "timings_diff.py")
            r = subprocess.run([sys.executable, tool, pa, pb], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1); self.assertIn("cai", r.stdout)
            r = subprocess.run([sys.executable, tool, pa, pb, "--threshold", "0.5"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0)
            r = subprocess.run([sys.executable, tool, pa, pb, "--json"], capture_output=True, text=True)
            self.assertTrue(json.loads(r.stdout)["moved"])


if __name__ == "__main__":
    unittest.main()
