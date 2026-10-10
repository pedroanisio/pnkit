"""tools: sync + check_lock round trip, gate's parsers, kit.json against the package."""
import importlib.util, json, os, shutil, subprocess, sys, tempfile, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
import pnkit


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LIB, "tools", name + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


class Lock(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pnkit-")
        os.makedirs(os.path.join(self.tmp, "film"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_tool(self, name, *args):
        return subprocess.run([sys.executable, os.path.join(LIB, "tools", name), *args], capture_output=True, text=True)

    def test_sync_then_check(self):
        r = self.run_tool("sync.py", self.tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        lock = json.load(open(os.path.join(self.tmp, "film", "vendor", "pnkit.lock")))
        self.assertEqual(lock["version"], pnkit.__version__)
        self.assertIn("camera.py", lock["files"]); self.assertIn("kit.json", lock["files"]); self.assertIn("data/vo_lexicon.json", lock["files"])
        self.assertIn("pixelart/ctx.py", lock["files"]); self.assertIn("pixelart/__init__.py", lock["files"])
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "film", "vendor", "__init__.py")))
        self.assertEqual(self.run_tool("check_lock.py", self.tmp).returncode, 0)
        # the vendored copy imports as vendor.pnkit
        r = subprocess.run([sys.executable, "-c", "from vendor import pnkit; print(pnkit.__version__)"], cwd=os.path.join(self.tmp, "film"),
                           capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), pnkit.__version__, r.stderr)
        # the vendored vo reads its own copy of the dictionary
        r = subprocess.run([sys.executable, "-c", "from vendor.pnkit import vo; print(vo.speak('an A.I. model', 'en'), vo._DATA)"],
                           cwd=os.path.join(self.tmp, "film"), capture_output=True, text=True)
        self.assertTrue(r.stdout.startswith("an AI model " + os.path.join(self.tmp, "film")), r.stdout + r.stderr)

    def test_check_catches_edits_and_strays(self):
        self.run_tool("sync.py", self.tmp)
        dest = os.path.join(self.tmp, "film", "vendor", "pnkit")
        with open(os.path.join(dest, "text.py"), "a") as fh:
            fh.write("# local edit\n")
        open(os.path.join(dest, "extra.py"), "w").write("")
        open(os.path.join(dest, "data", "extra.json"), "w").write("{}")
        r = self.run_tool("check_lock.py", self.tmp)
        self.assertEqual(r.returncode, 1)
        self.assertIn("modified: text.py", r.stdout); self.assertIn("not in the lock: extra.py", r.stdout)
        self.assertIn("not in the lock: data/extra.json", r.stdout)

    def test_no_lock(self):
        self.assertEqual(self.run_tool("check_lock.py", self.tmp).returncode, 1)


class Gate(unittest.TestCase):
    def setUp(self):
        self.g = load("gate")

    def test_diagnostics(self):
        out = ('error[E05]: override in "i1": no element "nothere" inside it\n  --> a.scene.xml:11:7\n   |\n'
               'warning[W12]: something\n  --> a.scene.xml:3:1\n')
        d = self.g.diagnostics(out)
        self.assertEqual(d[0][:2], ("error", "E05")); self.assertEqual(d[0][3], "a.scene.xml:11:7")
        self.assertEqual(d[1][:2], ("warning", "W12"))

    def test_flash_state(self):
        self.assertFalse(self.g.flash_state(None)[0])
        self.assertTrue(self.g.flash_state({})[0])
        self.assertTrue(self.g.flash_state({"flashCheck": "error"})[0])
        self.assertFalse(self.g.flash_state({"flashCheck": "off"})[0])


class Catalog(unittest.TestCase):
    def test_kit_json(self):
        kit = json.load(open(os.path.join(LIB, "kit.json")))
        self.assertEqual(kit["id"], "pnkit"); self.assertEqual(kit["version"], pnkit.__version__)
        self.assertTrue(os.path.exists(os.path.join(LIB, kit["changelog"])))
        for c in kit["components"]:
            mod = importlib.import_module(c["module"])
            last = c["module"].split(".")[-1]
            for name in (n.strip() for n in c["name"].split(" / ")):
                obj = mod
                for part in name.split("."):
                    if part != last:
                        self.assertTrue(hasattr(obj, part), f"{c['module']}: {name}")
                        obj = getattr(obj, part)
            for k in ("summary", "params", "rules"):
                self.assertIn(k, c)


if __name__ == "__main__":
    unittest.main()
