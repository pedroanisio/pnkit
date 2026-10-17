#!/usr/bin/env python3
"""gate.py — the CPU checks a scene must pass before anything is rendered.

    python3 tools/gate.py SCENE [--probe T ...] [--markers] [--no-layouts] [--no-variants] [--no-assets] [--engine PATH] [--json]

1. `scene-render validate --deny-warnings`: structure, co-occurrence and reference rules, files and digests.
2. `scene-render eval` at probe times (default 0 s; --markers adds every <marker>), and once per declared
   <layout> and <variant> at the first probe. Validation does not apply overrides; evaluation does, and reports
   what it cannot apply: E05 (an override or bind targets an id that does not exist in its scope) and E06 (it
   sets an attribute the target does not declare, or a value its type rejects). A scene can validate clean and
   still fail here. Overrides are applied when the program is built, so one probe per layout and variant finds
   them; later probes find expression errors that only occur at those times, and they are slow when particle
   emitters use preroll (the simulation runs from 0: v013's eight marker probes take ~8 CPU-minutes).
3. Whether the document's photosensitivity check is on: the engine checks flashes at encode only when the
   scene's <metadata> holds an <accessibility> element whose flashCheck is not "off" (XSD default "warn").

A further check runs only to report a fault: an <instance> with no `start` whose symbol reads `time` in a `condition`
(tools/instance_clock.py), which shows an arbitrary first frame. Clean scenes print nothing for it.

The engine's output is read as the `scene-render-cli/1` JSON envelope (`--format json`, scene-render >= 0.6.0);
an engine that prints no envelope falls back to the human format, parsed as before. The gate's own report is the
same either way (`engine_format` in --json names which was read).

Exit status 0 when all three pass, 1 otherwise, 2 when the engine cannot be run. Nothing here uses the GPU.
Levels of the *rendered* frames (clipping, legal range, gamut) are the render host's check: tools/scopes_check.py.
"""
import argparse, json, os, re, shutil, subprocess, sys, xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

DEFAULT_ENGINE = os.path.expanduser("~/.local/share/scene-render/v013/engine/target/release/scene-render")
DIAG = re.compile(r"^(error|warning)\[(\w+)\]: (.*)$")
OVERRIDE_CODES = {"E05", "E06"}


def instance_clock_findings(scene):
    """tools/instance_clock.py's findings for the scene; [] when clean or when the XML cannot be parsed
    (validate reports that)"""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import instance_clock
    try:
        return instance_clock.lint(scene)
    except ET.ParseError:
        return []


def engine(path=None):
    for c in (path, os.environ.get("SCENE_RENDER"), shutil.which("scene-render"), DEFAULT_ENGINE):
        if c and os.path.exists(c):
            return c
    print("gate: no scene-render engine (pass --engine or set SCENE_RENDER)", file=sys.stderr)
    sys.exit(2)  # the docstring's contract: 2 when the engine cannot be run (sys.exit(str) would be 1)


def diagnostics(text):
    """[(severity, code, message, location)] from human-format output"""
    out, lines = [], text.splitlines()
    for i, line in enumerate(lines):
        m = DIAG.match(line.strip())
        if m:
            loc = next((l.strip()[4:] for l in lines[i + 1:i + 3] if l.strip().startswith("--> ")), "")
            out.append((m.group(1), m.group(2), m.group(3), loc))
    return out


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def envelope(stdout):
    """the scene-render-cli/1 envelope in stdout, or None (an engine before 0.6.0 prints none)"""
    try:
        env = json.loads(stdout)
    except ValueError:
        return None
    return env if isinstance(env, dict) and env.get("format") == "scene-render-cli/1" else None


def envelope_diagnostics(env, scene):
    """diagnostics() tuples from an envelope: validate keeps a file's findings in its result, eval's sit at the
    top; info findings are left out, as the text parser leaves them"""
    result = env.get("result")
    found = list(env.get("diagnostics") or [])
    for f in (result.get("files") or []) if isinstance(result, dict) else []:
        found += f.get("diagnostics") or []
    out = []
    for d in found:
        if d.get("severity") not in ("error", "warning"):
            continue
        loc = d.get("loc") or {}
        where = d.get("file", scene)
        if loc.get("line") is not None:
            where = f"{where}:{loc['line']}:{loc.get('column')}"
        out.append((d["severity"], d["code"], d.get("message", ""), where))
    return out


MODE = {"json": True}  # flipped off at the first run whose stdout holds no envelope; settled by validate,
                       # which runs before the eval pool starts


def engine_run(cmd, scene):
    """(exit, diagnostics, envelope-or-None, raw text) — the JSON envelope when the engine has it, else the
    human format"""
    if MODE["json"]:
        rc, out, err = run(cmd + ["--format", "json"])
        env = envelope(out)
        if env is not None:
            return rc, envelope_diagnostics(env, scene), env, out + err
        MODE["json"] = False
    rc, out, err = run(cmd)
    return rc, diagnostics(out + err), None, out + err


def scene_facts(path):
    """markers, layouts, variants and the accessibility element of a scene"""
    root = ET.parse(path).getroot()
    markers = sorted({float(m.get("time")) for m in root.iter("marker") if m.get("time") is not None})
    layouts = [l.get("id") for l in root.iter("layout") if l.get("id")]
    variants = [v.get("id") for v in root.iter("variant") if v.get("id")]
    meta = root.find("metadata")
    acc = meta.find("accessibility") if meta is not None else None
    return markers, layouts, variants, (dict(acc.attrib) if acc is not None else None)


def flash_state(acc):
    """(on, description) following the engine: no element -> nothing is checked"""
    if acc is None:
        return False, "off: no <accessibility> element in <metadata>, so the engine checks nothing"
    mode = acc.get("flashCheck")
    if mode is None:
        return True, "warn (the XSD default; <accessibility> is present without flashCheck)"
    return mode != "off", f"{mode} (explicit)" + ("" if mode != "off" else ": the check is disabled")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("scene")
    ap.add_argument("--probe", type=float, nargs="+", help="probe times, s (default: 0)")
    ap.add_argument("--markers", action="store_true", help="also probe at every <marker> time")
    ap.add_argument("--no-layouts", action="store_true", help="skip the per-layout evaluation")
    ap.add_argument("--no-variants", action="store_true", help="skip the per-variant evaluation")
    ap.add_argument("--no-assets", action="store_true", help="skip file and digest checks (validate and eval)")
    ap.add_argument("--engine", help="scene-render binary")
    ap.add_argument("--jobs", type=int, default=2, help="evaluations run at once (default 2)")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    args = ap.parse_args()
    sr = engine(args.engine)
    na = ["--no-assets"] if args.no_assets else []

    rc, v_diags, _, raw = engine_run([sr, "validate", "--deny-warnings", "--color", "never", *na, args.scene], args.scene)
    if rc == 2:
        print(raw); sys.exit(2)
    v_ok = rc == 0

    markers, layouts, variants, acc = scene_facts(args.scene)
    probes = sorted(set(args.probe or [0.0]) | (set(markers) if args.markers else set()))
    jobs = [("t", t, []) for t in probes]
    if not args.no_layouts:
        jobs += [("layout", l, ["--layout", l]) for l in layouts]
    if not args.no_variants:
        jobs += [("variant", v, ["--variant", v]) for v in variants]

    def ev(job):
        kind, what, extra = job
        t = what if kind == "t" else probes[0]
        rc_, diags_, env_, raw_ = engine_run([sr, "eval", args.scene, "--time", repr(t), "--color", "never", *na, *extra],
                                             args.scene)
        if env_ is not None and isinstance(env_.get("result"), dict):
            n = env_["result"].get("nodes")
            nodes = len(n) if isinstance(n, list) else None
        else:
            m = re.search(r"(\d+) nodes", raw_)
            nodes = int(m.group(1)) if m else None
        return {"kind": kind, "what": what, "time": t, "exit": rc_, "nodes": nodes, "diagnostics": diags_}

    with ThreadPoolExecutor(max(1, args.jobs)) as pool:
        evals = list(pool.map(ev, jobs))
    e_errors = [(e, d) for e in evals for d in e["diagnostics"] if d[0] == "error"]
    overrides = [(e, d) for e, d in e_errors if d[1] in OVERRIDE_CODES]
    e_ok = all(e["exit"] == 0 for e in evals) and not e_errors
    f_on, f_desc = flash_state(acc)
    clock = instance_clock_findings(args.scene)
    ok = v_ok and e_ok and f_on and not clock

    if args.json:
        print(json.dumps({"scene": args.scene, "ok": ok, "engine_format": "json" if MODE["json"] else "text",
                          "validate": {"ok": v_ok, "diagnostics": v_diags},
                          "eval": evals, "override_errors": len(overrides), "flashCheck": {"on": f_on, "state": f_desc,
                          "accessibility": acc}, **({"instance_clock": clock} if clock else {})}, indent=1))
    else:
        print(f"gate {args.scene}")
        print(f"  validate --deny-warnings: {'PASS' if v_ok else 'FAIL'}")
        for sev, code, msg, loc in v_diags:
            print(f"    {sev}[{code}] {msg}" + (f"  ({loc})" if loc else ""))
        print(f"  eval: {len(evals)} evaluation(s): {'PASS' if e_ok else 'FAIL'}"
              f" ({len(e_errors)} error(s), {len(overrides)} override/target error(s) E05/E06)")
        for e in evals:
            label = f"t={e['time']:g}" if e["kind"] == "t" else f"{e['kind']} {e['what']} at t={e['time']:g}"
            state = "ok" if e["exit"] == 0 else f"exit {e['exit']}"
            print(f"    {label}: {state}" + (f", {e['nodes']} nodes" if e["nodes"] is not None else ""))
            for sev, code, msg, loc in e["diagnostics"]:
                print(f"      {sev}[{code}] {msg}" + (f"  ({loc})" if loc else ""))
        print(f"  flash check: {'ON' if f_on else 'OFF'}: {f_desc}")
        if clock:
            print(f"  instance clock: FAIL ({len(clock)} instance(s) without start whose symbol reads time)")
            for line in clock:
                print(f"    {line}")
        print(f"gate: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
