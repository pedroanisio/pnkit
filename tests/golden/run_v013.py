#!/usr/bin/env python3
"""run_v013.py — the golden test: v013's film.scene.xml, rebuilt with the vendored pnkit, is byte-identical.

    python3 tests/golden/run_v013.py [--project DIR] [--work DIR] [--patch FILE] [--validate] [--keep]

1. Copy the project to a work directory (out/ and qa/ left out; large read-only inputs linked, not copied).
2. Vendor this library into it (tools/sync.py). If the project does not use pnkit yet (no film/vendor/pnkit.lock),
   apply the project-side patch (default: v013-to-pnkit.diff next to this script).
3. Run `python3 film/build.py` in the copy and compare its film.scene.xml with the project's, byte for byte.
4. --validate: also run `scene-render validate` on the rebuilt scene (CPU only).
The project itself is only read. Exit status 0 when the files are identical (and valid, with --validate).
"""
import argparse, filecmp, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(os.path.dirname(HERE))
LINKED = ["assets", "fonts", "sfx", "film/tex", "film/physics.cache", "music/score.wav", "music/af", "vo/cache"]
SKIPPED = {"out", "qa", "__pycache__"}


def copy_project(src, dst):
    def ignore(d, names):
        rel = os.path.relpath(d, src)
        skip = {n for n in names if n in SKIPPED}
        skip |= {n for n in names if os.path.normpath(os.path.join(rel, n)) in LINKED}
        if rel == "vo":
            skip |= {n for n in names if n.endswith(".wav")}
        return skip
    shutil.copytree(src, dst, ignore=ignore, symlinks=True)
    for rel in LINKED:
        if os.path.exists(os.path.join(src, rel)):
            os.symlink(os.path.join(src, rel), os.path.join(dst, rel))
    vo = os.path.join(src, "vo")
    for n in sorted(os.listdir(vo)) if os.path.isdir(vo) else []:
        if n.endswith(".wav"):
            os.symlink(os.path.join(vo, n), os.path.join(dst, "vo", n))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--project", default=os.path.expanduser("~/videos/v013-jev-decisions"))
    ap.add_argument("--work", help="work directory (default: a new temporary one)")
    ap.add_argument("--patch", default=os.path.join(HERE, "v013-to-pnkit.diff"))
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--engine", default=os.environ.get("SCENE_RENDER") or os.path.expanduser("~/.local/share/scene-render/v013/engine/target/release/scene-render"))
    ap.add_argument("--keep", action="store_true", help="keep the work directory")
    args = ap.parse_args()
    project = os.path.abspath(args.project)
    work = os.path.abspath(args.work) if args.work else tempfile.mkdtemp(prefix="pnkit-golden-")
    dst = os.path.join(work, os.path.basename(project))
    if os.path.exists(dst):
        shutil.rmtree(dst)
    copy_project(project, dst)
    adopted = os.path.exists(os.path.join(project, "film", "vendor", "pnkit.lock"))
    run = lambda cmd, **k: subprocess.run(cmd, check=True, **k)
    run([sys.executable, os.path.join(LIB, "tools", "sync.py"), dst])
    if not adopted:
        run(["patch", "-p1", "--no-backup-if-mismatch", "-s", "-i", os.path.abspath(args.patch)], cwd=dst)
    os.remove(os.path.join(dst, "film.scene.xml"))
    run([sys.executable, "-B", "film/build.py"], cwd=dst)
    same = filecmp.cmp(os.path.join(dst, "film.scene.xml"), os.path.join(project, "film.scene.xml"), shallow=False)
    r = subprocess.run(["cmp", os.path.join(dst, "film.scene.xml"), os.path.join(project, "film.scene.xml")], capture_output=True, text=True)
    print(f"cmp: {'identical' if same else r.stdout.strip() or r.stderr.strip()}")
    ok = same
    if args.validate:
        v = subprocess.run([args.engine, "validate", "--color", "never", os.path.join(dst, "film.scene.xml")], capture_output=True, text=True)
        print("validate:", (v.stdout + v.stderr).strip().splitlines()[-1])
        ok = ok and v.returncode == 0
    if args.keep or args.work:
        print("work:", dst)
    else:
        shutil.rmtree(work)
    print("golden v013:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
