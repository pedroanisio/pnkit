"""tools: sync + check_lock round trip, gate's parsers (both engine output formats), scopes_check's judge,
kit.json against the package."""
import importlib.util, json, os, shutil, stat, subprocess, sys, tempfile, textwrap, unittest
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


def fake_engine(tmp, name, body):
    """an executable python script standing in for scene-render (as filmbuild's tests use fake_vmrun.py)"""
    path = os.path.join(tmp, name)
    with open(path, "w") as fh:
        fh.write("#!/usr/bin/env python3\nimport json, sys\n" + textwrap.dedent(body))
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


VALIDATE_ENV = {"format": "scene-render-cli/1", "schema_version": "1.1.0", "command": "validate", "ok": False,
                "exit_code": 1, "diagnostics": [], "error": {"kind": "invalid", "message": "1 of 1 file(s) invalid",
                "codes": ["E05"]}, "result": {"files": [{"diagnostics": [
                    {"severity": "error", "code": "E05", "message": "override in \"i1\": no element \"nothere\"",
                     "path": "i1", "loc": {"line": 11, "column": 7, "offset": 100}},
                    {"severity": "info", "code": "INERT-I13", "message": "accepted but not read",
                     "path": "fx", "loc": {"line": 3, "column": 1, "offset": 10}}]}]}}

EVAL_ENV = {"format": "scene-render-cli/1", "schema_version": "1.1.0", "command": "eval", "ok": True,
            "exit_code": 0, "error": None, "result": {"nodes": [{"id": "a"}, {"id": "b"}, {"id": "c"}]},
            "diagnostics": [{"severity": "warning", "code": "W12", "message": "something",
                             "path": "/scene", "file": "b.scene.xml",
                             "loc": {"line": 3, "column": 1, "offset": 10}}]}


class GateEnvelope(unittest.TestCase):
    """gate reads the scene-render-cli/1 envelope (>= 0.6.0) and falls back to the human format."""

    def setUp(self):
        self.g = load("gate")
        self.g.MODE["json"] = True
        self.tmp = tempfile.mkdtemp(prefix="pnkit-gate-")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_envelope(self):
        self.assertIsNone(self.g.envelope("error[E05]: not json"))
        self.assertIsNone(self.g.envelope(json.dumps({"format": "other/1"})))
        self.assertEqual(self.g.envelope(json.dumps(VALIDATE_ENV))["command"], "validate")

    def test_envelope_diagnostics(self):
        d = self.g.envelope_diagnostics(VALIDATE_ENV, "a.scene.xml")
        self.assertEqual(d, [("error", "E05", 'override in "i1": no element "nothere"', "a.scene.xml:11:7")])
        d = self.g.envelope_diagnostics(EVAL_ENV, "a.scene.xml")  # eval: top level, with its own file
        self.assertEqual(d, [("warning", "W12", "something", "b.scene.xml:3:1")])

    def test_engine_run_json(self):
        sr = fake_engine(self.tmp, "sr-json", f"""\
            assert "--format" in sys.argv and "json" in sys.argv
            print(json.dumps({VALIDATE_ENV!r}))
            sys.exit(1)
            """)
        rc, diags, env, _ = self.g.engine_run([sr, "validate", "a.scene.xml"], "a.scene.xml")
        self.assertEqual((rc, env["command"]), (1, "validate"))
        self.assertEqual(diags[0][:2], ("error", "E05"))
        self.assertTrue(self.g.MODE["json"])

    def test_engine_run_falls_back_before_0_6_0(self):
        sr = fake_engine(self.tmp, "sr-old", """\
            if "--format" in sys.argv:
                sys.stderr.write("error: unexpected argument '--format'\\n"); sys.exit(2)
            print('error[E05]: override in "i1": no element "nothere" inside it')
            print("  --> a.scene.xml:11:7")
            sys.exit(1)
            """)
        rc, diags, env, _ = self.g.engine_run([sr, "validate", "a.scene.xml"], "a.scene.xml")
        self.assertEqual((rc, env), (1, None))
        self.assertEqual(diags[0][:2], ("error", "E05")); self.assertEqual(diags[0][3], "a.scene.xml:11:7")
        self.assertFalse(self.g.MODE["json"])


SCOPES_LEVELS = {"samples": 64,
                 "clipping": {"black": {"r": 0.0, "g": 0.0, "b": 0.0, "y": 0.0},
                              "white": {"r": 0.015625, "g": 0.015625, "b": 0.015625, "y": 0.015625}},
                 "float_range": None, "legal": None, "illegal": None,
                 "saturation": {"above_limit": 0.0, "out_of_gamut": 0.0, "chroma_limit": 0.447, "max_chroma": 0.0}}


class ScopesCheck(unittest.TestCase):
    def setUp(self):
        self.s = load("scopes_check")
        self.tmp = tempfile.mkdtemp(prefix="pnkit-scopes-")
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def test_judge_clean(self):
        m, findings = self.s.judge(SCOPES_LEVELS)
        self.assertEqual(findings, [])  # illegal is None (no legal range) and clipping is not gated by default
        self.assertEqual(m["clipped"], 0.015625); self.assertIsNone(m["illegal"])

    def test_judge_findings(self):
        levels = dict(SCOPES_LEVELS, illegal=0.002,
                      saturation={"above_limit": 0.01, "out_of_gamut": 0.0005, "chroma_limit": 0.447, "max_chroma": 1.0})
        m, findings = self.s.judge(levels, max_oversaturated=0.02)  # an allowed fraction passes
        self.assertEqual([f[0] for f in findings], ["illegal", "out_of_gamut"])
        m, findings = self.s.judge(levels, max_illegal=0.01, max_out_of_gamut=0.001, max_oversaturated=0.02,
                                   max_clipped=0.001)
        self.assertEqual([f[0] for f in findings], ["clipped"])
        self.assertEqual(findings[0][1:], (0.015625, 0.001))

    def scopes_engine(self, levels):
        env = {"format": "scene-render-cli/1", "schema_version": "1.1.0", "command": "scopes", "ok": True,
               "exit_code": 0, "error": None, "diagnostics": [],
               "result": {"file": "f.png", "frames": {"analysed": 1, "step": 1}, "levels": levels}}
        return fake_engine(self.tmp, "sr-scopes", f"print(json.dumps({env!r}))\n")

    def test_tool_pass_and_fail(self):
        tool = os.path.join(LIB, "tools", "scopes_check.py")
        sr = self.scopes_engine(SCOPES_LEVELS)
        r = subprocess.run([sys.executable, tool, "f.png", "--engine", sr, "--json"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(json.loads(r.stdout)["ok"])
        sr = self.scopes_engine(dict(SCOPES_LEVELS, illegal=0.5))
        r = subprocess.run([sys.executable, tool, "f.png", "--engine", sr], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("illegal 0.5 > 0", r.stdout)

    def test_tool_refuses_an_engine_without_the_envelope(self):
        sr = fake_engine(self.tmp, "sr-old", "sys.stderr.write('unknown subcommand scopes\\n'); sys.exit(2)\n")
        tool = os.path.join(LIB, "tools", "scopes_check.py")
        r = subprocess.run([sys.executable, tool, "f.png", "--engine", sr], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("0.6.0", r.stderr)


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
