#!/usr/bin/env python3
"""vm_preflight.py — check the render VMs before a batch, not after it.

    python3 tools/vm_preflight.py [HOST ...] [--min-free-gb 20] [--out vm_preflight.json]
        [--scene SCENE --times 1,5,9 --render-cmd 'TEMPLATE'] [--runner 'TEMPLATE']

Per host (default: prod fix lab style1 style2 style3) it checks, in one read-only remote probe:
  1. reachability;
  2. free disk under $HOME against --min-free-gb;
  3. who holds or waits on ~/heavy.lock (from /proc/locks: holders and waiters, with pid, user, elapsed time and
     command where ps shows them; best effort, the lock file's inode is matched without its device number);
  4. the CPU model (the first `model name` of /proc/cpuinfo), and a warning when the hosts differ.
With --scene, --times and --render-cmd it also runs the cross-VM determinism probe: the same frames rendered on
every reachable host, each frame's sha256 collected, and the hosts that disagree reported.

Why 4: the Lula package rebuild matched 26 of 32 segments; the 6 that differed were exactly those rendered on style3,
the only Intel CPU (the others are Ryzen, same Mesa, same engine). Re-rendering on style3 reproduced the published
bytes, so the engine is deterministic per host, not across CPU models. A film split across hosts of different CPU
models can therefore differ from a rebuild on another host. Run this before a batch and after any VM, driver or
engine change.

The runner. Every command goes through a template, default
    tools/vm/vmrun.sh {host} run {cmd}          (env PNKIT_VM_RUNNER overrides; --runner overrides both)
{host} and {cmd} are replaced token by token and the command is run without a shell, so {cmd} stays one argument
(vmrun.sh joins its arguments and hands them to ssh). A relative script path is looked up from the working
directory and its parents. The tool never contacts a VM by any other route and prints no secrets; only the first
200 characters of a failing command's stderr are shown.

The determinism probe. --render-cmd is a template the caller supplies, run on each host through the runner:
    {scene}   the scene path ON THE HOST (already there: copy it first, e.g. with `vmrun.sh HOST put`), shell-quoted
    {t}       one of --times
    {out}     the frame file to write (a temp path on the host; removed afterwards)
Other braces must be doubled. The tool appends the sha256 of {out} and a clean-up. The command is wrapped in
`flock -w SECONDS ~/heavy.lock` (--lock-wait, default 900; --no-lock to skip) because rendering is a heavy job.
This tool does not know the engine's command line: the template is the caller's, and an engine option that
changes between versions is the caller's to keep in it.

Output: one table on stdout and a JSON report (--out, default vm_preflight.json, overwritten on each run: it is a
measurement, not an approved file). Exit status: 0 when every host passes; 1 when a host is unreachable, short of
disk, failed its renders, or the hosts disagree; 2 on a usage error. A held lock and differing CPU models are
warnings, not failures.
"""
import argparse, collections, concurrent.futures, datetime, json, os, re, shlex, subprocess, sys, uuid

DEFAULT_HOSTS = ["prod", "fix", "lab", "style1", "style2", "style3"]
DEFAULT_RUNNER = "tools/vm/vmrun.sh {host} run {cmd}"
LOCK = "$HOME/heavy.lock"

# read-only; prints PNKIT_OK, FREE_KB=, CPU=, LOCKFILE=, and LOCK / PS lines
PROBE = (
    'echo PNKIT_OK; '
    'echo FREE_KB=$(df -Pk "$HOME" | awk \'NR==2{print $4}\'); '
    'echo CPU=$(grep -m1 "model name" /proc/cpuinfo | sed "s/^[^:]*: *//"); '
    'ino=$(stat -c %i "$HOME/heavy.lock" 2>/dev/null); echo LOCKFILE=${ino:-none}; '
    'if [ -n "$ino" ]; then grep -E ":$ino " /proc/locks | sed "s/^/LOCK /"; '
    'for p in $(grep -E ":$ino " /proc/locks | awk \'{for(i=1;i<=NF;i++) if($i=="READ"||$i=="WRITE") print $(i+1)}\' | sort -u); '
    'do ps -o pid=,user=,etime=,args= -p $p | sed "s/^/PS /"; done; fi'
)


def _resolve_exe(token):
    """a relative script path with a slash is looked up from the working directory and its parents"""
    if os.path.isabs(token) or "/" not in token or os.path.exists(token):
        return token
    d = os.getcwd()
    while True:
        cand = os.path.join(d, token)
        if os.path.exists(cand):
            return cand
        up = os.path.dirname(d)
        if up == d:
            return token
        d = up


def make_runner(template, timeout=1200):
    """-> run(host, cmd) -> (rc, stdout, stderr); the template's tokens are filled one by one, no shell"""
    toks = shlex.split(template)
    if not toks:
        raise ValueError("empty runner template")
    toks[0] = _resolve_exe(toks[0])

    def run(host, cmd):
        argv = [t.replace("{host}", host).replace("{cmd}", cmd) for t in toks]
        try:
            p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return 124, "", f"timed out after {timeout} s"
        except OSError as e:
            return 127, "", str(e)
        return p.returncode, p.stdout, p.stderr
    return run


def _short(s, n=200):
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[:n] + "..."


def parse_probe(out):
    """the probe's stdout -> {"reachable", "free_gb", "cpu", "lock": {"present", "holders", "waiters"}}"""
    if "PNKIT_OK" not in out:
        return {"reachable": False}
    free = cpu = None
    present, locks, ps = False, [], {}
    for line in out.splitlines():
        if line.startswith("FREE_KB="):
            v = line[8:].strip()
            free = round(int(v) / 1048576, 2) if v.isdigit() else None
        elif line.startswith("CPU="):
            cpu = line[4:].strip() or "unknown"
        elif line.startswith("LOCKFILE="):
            present = line[9:].strip() not in ("", "none")
        elif line.startswith("LOCK "):
            t = line[5:].split()
            for i, w in enumerate(t):
                if w in ("READ", "WRITE") and i + 1 < len(t):
                    locks.append({"pid": t[i + 1], "waiting": "->" in t})
                    break
        elif line.startswith("PS "):
            t = line[3:].split(None, 3)
            if len(t) >= 3:
                ps[t[0]] = {"user": t[1], "elapsed": t[2], "cmd": _short(t[3] if len(t) > 3 else "", 120)}
    for l in locks:
        l.update(ps.get(l["pid"], {}))
    return {"reachable": True, "free_gb": free, "cpu": cpu or "unknown",
            "lock": {"present": present, "holders": [l for l in locks if not l["waiting"]],
                     "waiters": [l for l in locks if l["waiting"]]}}


def check_host(run, host, min_free_gb):
    rc, out, err = run(host, PROBE)
    info = parse_probe(out) if rc == 0 else {"reachable": False}
    info["host"] = host
    if not info["reachable"]:
        info["error"] = _short(err) or f"exit {rc}"
        info["disk_ok"] = None
        return info
    info["disk_ok"] = info["free_gb"] is not None and info["free_gb"] >= min_free_gb
    return info


def frame_command(render_tmpl, scene, t, out_path):
    render = render_tmpl.format(scene=shlex.quote(scene), t=t, out=out_path)
    return f"{render} && sha256sum {out_path} | cut -d' ' -f1; rc=$?; rm -f {out_path}; exit $rc"


def probe_frames(run, host, scene, times, render_tmpl, lock_wait=900):
    """-> {"hashes": {t: sha256}, "error": str|None} for one host"""
    hashes = {}
    for t in times:
        out_path = f"/tmp/pnkit-det-{uuid.uuid4().hex[:12]}.png"
        cmd = frame_command(render_tmpl, scene, t, out_path)
        if lock_wait is not None:
            cmd = f'flock -w {int(lock_wait)} "{LOCK}" sh -c {shlex.quote(cmd)}'
        rc, out, err = run(host, cmd)
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        if rc != 0 or not lines or not re.fullmatch(r"[0-9a-f]{64}", lines[-1]):
            return {"hashes": hashes, "error": f"t={t}: " + (_short(err) or f"exit {rc}, no sha256 in the output")}
        hashes[t] = lines[-1]
    return {"hashes": hashes, "error": None}


def compare_hashes(per_host):
    """{host: {t: sha}} (hosts with every frame) -> {"agree", "groups", "disagreeing", "ambiguous", "frames_differing"}"""
    groups = collections.defaultdict(list)
    for h, hs in per_host.items():
        groups[tuple(sorted(hs.items()))].append(h)
    gl = sorted((sorted(v) for v in groups.values()), key=lambda g: (-len(g), g))
    out = {"groups": gl, "agree": len(gl) <= 1, "disagreeing": [], "ambiguous": False, "frames_differing": []}
    if len(gl) > 1:
        out["ambiguous"] = len(gl[0]) == len(gl[1])
        out["disagreeing"] = sorted(h for g in (gl if out["ambiguous"] else gl[1:]) for h in g)
        times = {t for hs in per_host.values() for t in hs}
        out["frames_differing"] = sorted((t for t in times if len({hs.get(t) for hs in per_host.values()}) > 1), key=float)
    return out


def preflight(run, hosts, min_free_gb=20.0, scene=None, times=None, render_tmpl=None, lock_wait=900):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(hosts))) as ex:
        infos = list(ex.map(lambda h: check_host(run, h, min_free_gb), hosts))
    rep = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "min_free_gb": min_free_gb, "hosts": infos, "warnings": [], "failures": [], "determinism": None}
    for i in infos:
        if not i["reachable"]:
            rep["failures"].append(f"{i['host']}: unreachable ({i['error']})")
        elif not i["disk_ok"]:
            rep["failures"].append(f"{i['host']}: free disk {i['free_gb']} GB is under {min_free_gb} GB")
        elif i["lock"]["holders"] or i["lock"]["waiters"]:
            rep["warnings"].append(f"{i['host']}: heavy.lock held by {len(i['lock']['holders'])}, {len(i['lock']['waiters'])} waiting")
    cpus = collections.defaultdict(list)
    for i in infos:
        if i["reachable"]:
            cpus[i["cpu"]].append(i["host"])
    rep["cpu_models"] = {c: sorted(h) for c, h in cpus.items()}
    if len(cpus) > 1:
        rep["warnings"].append("CPU models differ: " + "; ".join(f"{c} ({', '.join(sorted(h))})" for c, h in sorted(cpus.items()))
                               + ". Renders may differ byte for byte across them (Lula: 6 of 32 segments, all on the one Intel host).")
    if scene:
        live = [i["host"] for i in infos if i["reachable"]]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(live))) as ex:
            res = dict(zip(live, ex.map(lambda h: probe_frames(run, h, scene, times, render_tmpl, lock_wait), live)))
        good = {h: r["hashes"] for h, r in res.items() if not r["error"]}
        det = {"scene": scene, "times": list(times), "hashes": {h: r["hashes"] for h, r in res.items()},
               "errors": {h: r["error"] for h, r in res.items() if r["error"]}}
        det.update(compare_hashes(good) if good else {"agree": False, "groups": [], "disagreeing": [], "ambiguous": False, "frames_differing": []})
        rep["determinism"] = det
        for h, e in det["errors"].items():
            rep["failures"].append(f"{h}: frame render failed ({e})")
        if len(good) < 2:
            rep["warnings"].append("determinism probe: fewer than two hosts produced frames, nothing to compare")
        if det["disagreeing"]:
            odd = ", ".join(det["disagreeing"])
            rep["failures"].append(f"hosts disagree on frames {det['frames_differing']}: {odd}" + (" (no majority)" if det["ambiguous"] else ""))
            cm = {h: i["cpu"] for i in infos for h in [i["host"]] if i["reachable"]}
            if len({cm[h] for h in det["disagreeing"] if h in cm} - {cm[h] for g in det["groups"][:1] for h in g if h in cm}) > 0 and not det["ambiguous"]:
                rep["warnings"].append("the disagreeing hosts have a CPU model that the majority does not (correlation, not proof of cause)")
    rep["ok"] = not rep["failures"]
    return rep


def table(rep):
    det = rep["determinism"]
    rows = [("host", "reach", "free GB", "disk", "heavy.lock", "CPU model", "frames")]
    for i in rep["hosts"]:
        if not i["reachable"]:
            rows.append((i["host"], "NO", "-", "-", "-", "-", "-"))
            continue
        lk = i["lock"]
        lock = "free" if not (lk["holders"] or lk["waiters"]) else "held %d, wait %d" % (len(lk["holders"]), len(lk["waiters"]))
        if lk["holders"] and lk["holders"][0].get("user"):
            lock += " (%s %s)" % (lk["holders"][0]["user"], lk["holders"][0].get("elapsed", ""))
        if det is None:
            fr = "n/a"
        elif i["host"] in det["errors"]:
            fr = "ERROR"
        elif i["host"] in det["disagreeing"]:
            fr = "DIFFERS"
        else:
            fr = "agree" if det["agree"] else "majority"
        rows.append((i["host"], "yes", "%s" % i["free_gb"], "ok" if i["disk_ok"] else "LOW", lock, i["cpu"], fr))
    w = [max(len(r[c]) for r in rows) for c in range(len(rows[0]))]
    lines = ["  ".join(r[c].ljust(w[c]) for c in range(len(r))).rstrip() for r in rows]
    lines.insert(1, "  ".join("-" * x for x in w))
    for x in rep["warnings"]:
        lines.append("WARNING: " + x)
    for x in rep["failures"]:
        lines.append("FAIL: " + x)
    lines.append("PREFLIGHT " + ("OK" if rep["ok"] else "FAILED"))
    return "\n".join(lines)


def main(argv=None, run=None):
    ap = argparse.ArgumentParser(description="Check the render VMs before a batch.")
    ap.add_argument("hosts", nargs="*", help="default: " + " ".join(DEFAULT_HOSTS))
    ap.add_argument("--runner", default=os.environ.get("PNKIT_VM_RUNNER", DEFAULT_RUNNER), help="template with {host} and {cmd}")
    ap.add_argument("--min-free-gb", type=float, default=20.0)
    ap.add_argument("--scene", help="scene path on the hosts, for the determinism probe")
    ap.add_argument("--times", help="comma-separated frame times for the probe, e.g. 1,5,9")
    ap.add_argument("--render-cmd", help="template with {scene} {t} {out}: renders one frame to {out}")
    ap.add_argument("--lock-wait", type=int, default=900, help="seconds the probe waits for ~/heavy.lock")
    ap.add_argument("--no-lock", action="store_true", help="run the probe without flock")
    ap.add_argument("--out", default="vm_preflight.json")
    a = ap.parse_args(argv)
    probe_args = [a.scene, a.times, a.render_cmd]
    if any(probe_args) and not all(probe_args):
        ap.error("the determinism probe needs --scene, --times and --render-cmd together")
    times = [t.strip() for t in (a.times or "").split(",") if t.strip()]
    if a.times and (not times or any(not re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) for t in times)):
        ap.error("--times must be comma-separated numbers")
    if a.render_cmd:
        try:
            a.render_cmd.format(scene="", t="", out="")
        except (KeyError, IndexError, ValueError) as e:
            ap.error(f"--render-cmd may use only {{scene}}, {{t}}, {{out}} (double other braces): {e}")
    hosts = a.hosts or DEFAULT_HOSTS
    if run is None:
        try:
            run = make_runner(a.runner)
        except ValueError as e:
            ap.error(str(e))
    rep = preflight(run, hosts, a.min_free_gb, a.scene, times, a.render_cmd, None if a.no_lock else a.lock_wait)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    print(table(rep))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
