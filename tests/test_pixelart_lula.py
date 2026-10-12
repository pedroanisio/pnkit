"""pnkit.pixelart was extracted from the Lula 3.0.0 picture framework: the film's scene modules, built against it, give
the same scene as with the film's own common.py. Since 1.0 the scene is built with sr_core.scene, which writes an
number as the text it is given, so the C14N 2.0 form (with comments) is equal to 0.8.0's with no normalisation: the
golden is `c14n_sha256` in tests/golden/pixelart/lula-3.0.0.json (`sha256` is 0.8.0's bytes, kept as the record; the
bytes differ only in the XML declaration, " />", ">" in attributes and the final newline). Each scene is also
checked (level 1: no error). Skipped where the Lula project is not on disk; PNKIT_LULA_ALL=1 checks all 32 scenes."""
import json, os, subprocess, sys, unittest

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILM = os.environ.get("PNKIT_LULA_FILM", os.path.join(os.path.dirname(os.path.dirname(LIB)), "projects", "lula-filme"))
V3 = os.path.join(FILM, "work", "art3", "v3")
TIMINGS = os.path.join(FILM, "p3", "audio", "timings-v2.json")
GOLDEN = json.load(open(os.path.join(LIB, "tests", "golden", "pixelart", "lula-3.0.0.json")))["c14n_sha256"]


@unittest.skipUnless(os.path.isdir(V3) and os.path.exists(TIMINGS), "Lula 3.0.0 project not on this host")
class LulaScenes(unittest.TestCase):
    def build(self, scenes):
        r = subprocess.run([sys.executable, os.path.join(LIB, "tools", "pixelart", "lula_alias.py"), "--c14n", V3, TIMINGS, scenes],
                           capture_output=True, text=True, env=dict(os.environ, PYTHONHASHSEED="0"), timeout=1200)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        return json.loads(r.stdout)

    def test_sample_scenes_are_strictly_c14n_equal(self):
        # 01 (opening, sets), 11 (zoom 11a fixed), 25 (graded set, the old determinism defect)
        got = self.build("01,11,25")
        for k, v in got.items():
            self.assertEqual(v, GOLDEN[k], k)

    @unittest.skipUnless(os.environ.get("PNKIT_LULA_ALL"), "set PNKIT_LULA_ALL=1 for all 32 scenes (about a minute)")
    def test_all_scenes_are_strictly_c14n_equal(self):
        self.assertEqual(self.build("all"), GOLDEN)
