"""tools/flat_field.py, tools/instance_clock.py and gate.py's call to it (ported from the Lula 3.0.0 checks, 2026-10-07).
The 11a cases: a view running 36 columns past a 320-column set, and the crowd instances without `start`."""
import importlib.util, os, subprocess, sys, tempfile, textwrap, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(LIB, "tests", "fixtures")
sys.path.insert(0, LIB)

try:
    from PIL import Image, ImageDraw
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LIB, "tools", name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def tool(name, *args):
    return subprocess.run([sys.executable, os.path.join(LIB, "tools", name), *args], capture_output=True, text=True)


SCENE = textwrap.dedent('''\
    <scene>
     <metadata><accessibility flashCheck="warn"/></metadata>
     <symbols>
      <symbol id="walker"><group id="f0" condition="Math.floor(time*4.0)%2==0"/></symbol>
     </symbols>
     <group id="shot" start="773.25"><instance id="i1" symbol="walker" @ATTR@/></group>
    </scene>''')


class InstanceClock(unittest.TestCase):
    def setUp(self):
        self.m = load("instance_clock")
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)

    def write(self, attr):
        p = os.path.join(self.tmp.name, "s.scene.xml")
        open(p, "w").write(SCENE.replace("@ATTR@", attr)); return p

    @staticmethod
    def sub(p, a, b):
        text = open(p).read(); open(p, "w").write(text.replace(a, b))

    def test_lula_fixture_flags_only_the_instance_without_start(self):
        f = self.m.lint(os.path.join(FIX, "lula_11a_instance_clock.scene.xml"))
        self.assertEqual(len(f), 1); self.assertIn("crowd1", f[0]); self.assertIn("absolute clock", f[0])

    def test_start_makes_it_clean(self):
        self.assertEqual(self.m.lint(self.write('start="773.258233"')), [])

    def test_symbol_without_time_condition_is_clean(self):
        p = self.write("")
        self.sub(p, "Math.floor(time*4.0)", "Math.floor(timer*4.0)")   # `timer` is not `time`
        self.assertEqual(self.m.lint(p), [])

    def test_namespaced_scene(self):
        p = self.write("")
        self.sub(p, "<scene>", '<scene xmlns="urn:x">')
        self.assertEqual(len(self.m.lint(p)), 1)

    def test_command_line_exit_status(self):
        bad = tool("instance_clock.py", os.path.join(FIX, "lula_11a_instance_clock.scene.xml"))
        self.assertEqual(bad.returncode, 1); self.assertIn("crowd1", bad.stdout)
        ok = tool("instance_clock.py", self.write('start="1"'))
        self.assertEqual((ok.returncode, ok.stdout.strip()), (0, "clean"))


class GateCallsIt(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.engine = os.path.join(self.tmp.name, "fake-engine")
        open(self.engine, "w").write("#!/bin/sh\necho '12 nodes'\nexit 0\n"); os.chmod(self.engine, 0o755)

    def gate(self, attr, *extra):
        p = os.path.join(self.tmp.name, "s.scene.xml")
        open(p, "w").write(SCENE.replace("@ATTR@", attr))
        return tool("gate.py", p, "--engine", self.engine, *extra)

    def test_clean_scene_output_has_no_clock_line(self):
        r = self.gate('start="773.25"')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("instance clock", r.stdout); self.assertNotIn("instance_clock", self.gate('start="1"', "--json").stdout)
        self.assertTrue(r.stdout.rstrip().endswith("gate: PASS"))

    def test_scene_with_the_problem_fails_and_names_the_instance(self):
        r = self.gate("")
        self.assertEqual(r.returncode, 1)
        self.assertIn("instance clock: FAIL", r.stdout); self.assertIn("instance i1", r.stdout)
        self.assertTrue(r.stdout.rstrip().endswith("gate: FAIL"))
        j = self.gate("", "--json").stdout
        self.assertIn('"instance_clock"', j)


@unittest.skipUnless(HAVE_PIL, "Pillow is needed for the flat-field tool")
class FlatField(unittest.TestCase):
    BG = (11, 16, 32)

    def setUp(self):
        self.m = load("flat_field")

    def frame(self, rects, base=(60, 40, 30), size=(1920, 1080)):
        im = Image.new("RGB", size, base); d = ImageDraw.Draw(im)
        for x0, y0, x1, y1, col in rects:
            d.rectangle([x0 * 6, y0 * 6, x1 * 6 - 1, y1 * 6 - 1], fill=col)
        return im

    def varied(self):
        return [(i * 20, 10, i * 20 + 18, 140, (30 + i * 9, 80, 200 - i * 8)) for i in range(16)]

    def test_a_full_picture_passes(self):
        self.assertEqual(self.m.analyse(self.frame(self.varied()), self.BG)["flags"], [])

    def test_lula_11a_36_empty_columns_are_found(self):
        r = self.m.analyse(self.frame(self.varied()[:12] + [(284, 0, 320, 180, self.BG)]), self.BG)
        self.assertIn("empty-background", r["flags"]); self.assertGreaterEqual(r["empty_strip_cols"], 36)
        self.assertAlmostEqual(r["empty_frac"], 36 / 320, places=2)

    def test_an_icon_on_one_flat_colour_is_a_flat_field(self):
        r = self.m.analyse(self.frame([(130, 50, 190, 100, (200, 190, 120))], base=(30, 50, 80)), self.BG)
        self.assertEqual(r["flags"], ["flat-field"]); self.assertGreater(r["dominant_frac"], 0.75)

    def test_thresholds_are_parameters(self):
        im = self.frame([(0, 0, 320, 70, (200, 190, 120))], base=(30, 50, 80))     # 39 % / 61 % split
        self.assertEqual(self.m.analyse(im, self.BG)["flags"], [])
        self.assertEqual(self.m.analyse(im, self.BG, flat_frac=0.5)["flags"], ["flat-field"])

    def test_rows_limit_leaves_the_plate_band_out(self):
        im = self.frame(self.varied() + [(0, 146, 320, 180, self.BG)])
        self.assertIn("empty-background", self.m.analyse(im, self.BG, flat_frac=2, empty_frac=0.1)["flags"])
        self.assertEqual(self.m.analyse(im, self.BG, rows=146)["flags"], [])

    def test_other_grids_and_bad_sizes(self):
        im = self.frame([(0, 0, 40, 45, self.BG)], size=(640, 360))   # a 160x90 grid at 4 px per cell
        self.assertEqual(self.m.to_grid(im, (160, 90))[0][0], tuple(im.getpixel((2, 2))))
        with self.assertRaises(ValueError): self.m.to_grid(Image.new("RGB", (1000, 563)), (320, 180))

    def test_command_line_prints_paths_and_sets_the_exit_status(self):
        d = tempfile.mkdtemp(); self.addCleanup(__import__("shutil").rmtree, d)
        good, bad = os.path.join(d, "good.png"), os.path.join(d, "bad.png")
        self.frame(self.varied()).save(good)
        self.frame(self.varied()[:12] + [(284, 0, 320, 180, self.BG)]).save(bad)
        r = tool("flat_field.py", "--bg", "#0b1020", good, bad)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("empty-background", r.stdout); self.assertIn(bad, r.stdout); self.assertIn("2 frame(s), 1 flagged", r.stdout)
        self.assertEqual(tool("flat_field.py", "--bg", "11,16,32", good).returncode, 0)
        self.assertIn('"empty-background"', tool("flat_field.py", "--bg", "#0b1020", "--json", bad).stdout)

    def test_parse_rgb(self):
        self.assertEqual(self.m.parse_rgb("#0b1020"), (11, 16, 32)); self.assertEqual(self.m.parse_rgb("1, 2,3"), (1, 2, 3))
        with self.assertRaises(ValueError): self.m.parse_rgb("1,2")


if __name__ == "__main__":
    unittest.main()
