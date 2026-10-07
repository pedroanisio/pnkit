"""tools/vm_preflight.py with a fake runner only: nothing here contacts a VM or runs ssh."""
import importlib.util, json, os, re, shutil, sys, tempfile, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("vm_preflight", os.path.join(LIB, "tools", "vm_preflight.py"))
vp = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(vp)

RYZEN, INTEL = "AMD Ryzen 7 5700G", "Intel(R) Core(TM) i7-12700"
SHA_A, SHA_B = "a" * 64, "b" * 64


def probe_out(free_kb=200 * 1048576, cpu=RYZEN, lock=()):
    """what the probe prints; lock = [(pid, waiting, user, etime, cmd)]"""
    s = f"PNKIT_OK\nFREE_KB={free_kb}\nCPU={cpu}\nLOCKFILE={'4242' if lock else 'none'}\n"
    for pid, waiting, user, et, cmd in lock:
        s += f"LOCK 1: {'-> ' if waiting else ''}FLOCK  ADVISORY  WRITE {pid} 08:01:4242 0 EOF\n"
        s += f"PS {pid:>6} {user} {et} {cmd}\n"
    return s


class Fake:
    """a runner: per host a probe output (or None = unreachable) and a frame hash (a str, or {t: str}, or an Exception text)"""
    def __init__(self, probes, frames=None):
        self.probes, self.frames, self.calls = probes, frames or {}, []

    def __call__(self, host, cmd):
        self.calls.append((host, cmd))
        if cmd == vp.PROBE:
            out = self.probes[host]
            return (255, "", "ssh: connect to host timed out") if out is None else (0, out, "")
        fr = self.frames[host]
        m = re.search(r"-t (\S+)", cmd)
        h = fr[m.group(1)] if isinstance(fr, dict) else fr
        if h.startswith("ERR"):
            return 1, "", h
        return 0, "noise from the renderer\n" + h + "\n", ""


class Parse(unittest.TestCase):
    def test_probe_parse(self):
        i = vp.parse_probe(probe_out(free_kb=50 * 1048576, cpu=INTEL))
        self.assertEqual((i["reachable"], i["free_gb"], i["cpu"], i["lock"]["present"]), (True, 50.0, INTEL, False))

    def test_not_ok_output_is_unreachable(self):
        self.assertEqual(vp.parse_probe("Permission denied"), {"reachable": False})

    def test_lock_holder_and_waiters(self):
        i = vp.parse_probe(probe_out(lock=[(901, False, "dev", "01:02:03", "flock /home/dev/heavy.lock python3 build.py"),
                                           (977, True, "dev", "00:10", "flock /home/dev/heavy.lock encode.sh")]))
        lk = i["lock"]
        self.assertEqual([h["pid"] for h in lk["holders"]], ["901"])
        self.assertEqual(lk["holders"][0]["user"], "dev")
        self.assertEqual(lk["holders"][0]["elapsed"], "01:02:03")
        self.assertIn("build.py", lk["holders"][0]["cmd"])
        self.assertEqual([w["pid"] for w in lk["waiters"]], ["977"])


class Hosts(unittest.TestCase):
    def test_all_good(self):
        r = Fake({"prod": probe_out(), "fix": probe_out()})
        rep = vp.preflight(r, ["prod", "fix"])
        self.assertTrue(rep["ok"])
        self.assertEqual((rep["failures"], rep["warnings"]), ([], []))
        self.assertEqual(rep["cpu_models"], {RYZEN: ["fix", "prod"]})

    def test_unreachable_host_fails(self):
        rep = vp.preflight(Fake({"prod": probe_out(), "lab": None}), ["prod", "lab"])
        self.assertFalse(rep["ok"])
        self.assertIn("lab: unreachable", rep["failures"][0])
        self.assertIn("timed out", rep["failures"][0])

    def test_low_disk_fails_and_threshold_is_configurable(self):
        probes = {"prod": probe_out(free_kb=5 * 1048576)}
        self.assertFalse(vp.preflight(Fake(probes), ["prod"], min_free_gb=20)["ok"])
        self.assertTrue(vp.preflight(Fake(probes), ["prod"], min_free_gb=4)["ok"])

    def test_held_lock_is_a_warning_not_a_failure(self):
        rep = vp.preflight(Fake({"fix": probe_out(lock=[(5, False, "dev", "10:00", "flock heavy.lock x")])}), ["fix"])
        self.assertTrue(rep["ok"])
        self.assertIn("heavy.lock held by 1", rep["warnings"][0])

    def test_differing_cpu_models_warn_and_are_recorded(self):
        rep = vp.preflight(Fake({"fix": probe_out(), "style3": probe_out(cpu=INTEL)}), ["fix", "style3"])
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["cpu_models"][INTEL], ["style3"])
        self.assertTrue(any("CPU models differ" in w and "style3" in w for w in rep["warnings"]))
        self.assertEqual({h["host"]: h["cpu"] for h in rep["hosts"]}, {"fix": RYZEN, "style3": INTEL})

    def test_probe_is_one_read_only_command_per_host(self):
        r = Fake({"prod": probe_out()})
        vp.preflight(r, ["prod"])
        self.assertEqual(r.calls, [("prod", vp.PROBE)])
        for bad in ("rm ", "kill", "> ", "mv ", "tee"):
            self.assertNotIn(bad, vp.PROBE)


class Determinism(unittest.TestCase):
    HOSTS = ["prod", "fix", "lab", "style1", "style2", "style3"]
    ARGS = dict(scene="/home/dev/s/film.scene.xml", times=["1", "5.5"], render_tmpl="render {scene} -t {t} -o {out}")

    def fleet(self, odd_cpu="style3", odd_frames=("1", "5.5")):
        probes = {h: probe_out(cpu=INTEL if h == odd_cpu else RYZEN) for h in self.HOSTS}
        frames = {h: {"1": SHA_A, "5.5": SHA_A} for h in self.HOSTS}
        for t in odd_frames:
            frames[odd_cpu][t] = SHA_B
        return Fake(probes, frames)

    def test_lula_case_one_intel_host_disagrees(self):
        rep = vp.preflight(self.fleet(), self.HOSTS, **self.ARGS)
        d = rep["determinism"]
        self.assertFalse(rep["ok"])
        self.assertEqual((d["agree"], d["disagreeing"], d["ambiguous"]), (False, ["style3"], False))
        self.assertEqual(d["frames_differing"], ["1", "5.5"])
        self.assertTrue(any("CPU model that the majority does not" in w for w in rep["warnings"]))
        self.assertTrue(any("CPU models differ" in w for w in rep["warnings"]))

    def test_only_one_frame_differs(self):
        rep = vp.preflight(self.fleet(odd_frames=("5.5",)), self.HOSTS, **self.ARGS)
        self.assertEqual(rep["determinism"]["frames_differing"], ["5.5"])

    def test_all_agree(self):
        r = self.fleet(odd_frames=())
        rep = vp.preflight(r, self.HOSTS, **self.ARGS)
        self.assertTrue(rep["ok"] and rep["determinism"]["agree"])
        self.assertEqual(rep["determinism"]["hashes"]["prod"], {"1": SHA_A, "5.5": SHA_A})

    def test_tie_has_no_majority(self):
        probes = {"a": probe_out(), "b": probe_out()}
        rep = vp.preflight(Fake(probes, {"a": SHA_A, "b": SHA_B}), ["a", "b"], **self.ARGS)
        d = rep["determinism"]
        self.assertEqual((d["ambiguous"], d["disagreeing"]), (True, ["a", "b"]))
        self.assertIn("no majority", rep["failures"][0])

    def test_render_failure_fails_that_host_only(self):
        r = self.fleet(odd_frames=())
        r.frames["lab"] = "ERR gpu device lost"
        rep = vp.preflight(r, self.HOSTS, **self.ARGS)
        self.assertFalse(rep["ok"])
        self.assertIn("lab", rep["determinism"]["errors"])
        self.assertEqual(rep["determinism"]["disagreeing"], [])

    def test_unreachable_host_is_skipped_by_the_probe(self):
        r = self.fleet(odd_frames=())
        r.probes["fix"] = None
        rep = vp.preflight(r, self.HOSTS, **self.ARGS)
        self.assertNotIn("fix", rep["determinism"]["hashes"])
        self.assertFalse(any(c[0] == "fix" and c[1] != vp.PROBE for c in r.calls))

    def test_command_is_the_callers_template_under_the_lock(self):
        r = self.fleet(odd_frames=())
        vp.preflight(r, ["prod", "fix"], **self.ARGS)
        cmd = [c for h, c in r.calls if h == "prod" and c != vp.PROBE][0]
        self.assertTrue(cmd.startswith('flock -w 900 "$HOME/heavy.lock" sh -c '))
        self.assertIn("render /home/dev/s/film.scene.xml -t 1 -o /tmp/pnkit-det-", cmd)
        self.assertIn("sha256sum", cmd)

    def test_no_lock_leaves_the_command_bare(self):
        r = self.fleet(odd_frames=())
        vp.preflight(r, ["prod"], lock_wait=None, **self.ARGS)
        self.assertFalse(any(c.startswith("flock") for h, c in r.calls))

    def test_scene_path_is_shell_quoted(self):
        c = vp.frame_command("r {scene} {t} {out}", "/a b/x;rm -rf y.xml", "1", "/tmp/o.png")
        self.assertIn("'/a b/x;rm -rf y.xml'", c)

    def test_table_names_the_odd_host(self):
        t = vp.table(vp.preflight(self.fleet(), self.HOSTS, **self.ARGS))
        row = [l for l in t.splitlines() if l.startswith("style3")][0]
        self.assertIn("DIFFERS", row)
        self.assertIn(INTEL, row)
        self.assertTrue(t.rstrip().endswith("PREFLIGHT FAILED"))


class Runner(unittest.TestCase):
    def test_template_fills_tokens_without_a_shell(self):
        seen = {}
        orig = vp.subprocess.run
        class P: returncode, stdout, stderr = 0, "x", ""
        vp.subprocess.run = lambda argv, **kw: (seen.update(argv=argv, kw=kw), P())[1]
        try:
            rc, out, _ = vp.make_runner("/bin/echo --on {host} run {cmd}")("prod", "echo 'a b'; ls")
        finally:
            vp.subprocess.run = orig
        self.assertEqual(seen["argv"], ["/bin/echo", "--on", "prod", "run", "echo 'a b'; ls"])
        self.assertNotIn("shell", seen["kw"])
        self.assertEqual((rc, out), (0, "x"))

    def test_missing_runner_is_a_127_not_a_crash(self):
        rc, _, err = vp.make_runner("/nonexistent/vmrun {host} {cmd}")("prod", "true")
        self.assertEqual(rc, 127)

    def test_default_template_matches_vmrun_usage(self):
        self.assertEqual(vp.DEFAULT_RUNNER, "tools/vm/vmrun.sh {host} run {cmd}")


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pnkit-pf-")
        self.out = os.path.join(self.tmp, "r.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_table_json_and_exit_code(self):
        rc = vp.main(["prod", "lab", "--out", self.out], run=Fake({"prod": probe_out(), "lab": None}))
        self.assertEqual(rc, 1)
        with open(self.out, encoding="utf-8") as fh:
            rep = json.load(fh)
        self.assertEqual([h["host"] for h in rep["hosts"]], ["prod", "lab"])
        self.assertFalse(rep["ok"])

    def test_exit_0_when_clean(self):
        self.assertEqual(vp.main(["prod", "--out", self.out], run=Fake({"prod": probe_out()})), 0)

    def test_partial_probe_arguments_are_a_usage_error(self):
        with self.assertRaises(SystemExit) as c:
            vp.main(["prod", "--scene", "/x.xml", "--out", self.out], run=Fake({}))
        self.assertEqual(c.exception.code, 2)

    def test_stray_braces_in_render_cmd_are_a_usage_error(self):
        with self.assertRaises(SystemExit) as c:
            vp.main(["prod", "--scene", "/x", "--times", "1", "--render-cmd", "r {nope}", "--out", self.out], run=Fake({}))
        self.assertEqual(c.exception.code, 2)

    def test_default_hosts_are_the_six(self):
        self.assertEqual(vp.DEFAULT_HOSTS, ["prod", "fix", "lab", "style1", "style2", "style3"])


if __name__ == "__main__":
    unittest.main()
