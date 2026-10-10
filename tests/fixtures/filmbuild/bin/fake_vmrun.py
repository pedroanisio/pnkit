#!/usr/bin/env python3
"""A stand-in for vmrun.sh in the film_build tests: every host is a folder under $FAKE_VM_ROOT used as $HOME, commands
run in a local bash there, put and get copy like scp -r. The host's engine, python and ffmpeg are the fakes in this
folder: they write small deterministic files, so no render or encode runs (this machine must not do heavy jobs)."""
import os, shutil, stat, subprocess, sys

BIN = os.path.dirname(os.path.abspath(__file__))


def home(host):
    root = os.environ["FAKE_VM_ROOT"]
    h = os.path.join(root, host)
    for rel, src in (("engine/fake/scene-render", "fake_engine.py"), ("venv/bin/python", "fake_python.py")):
        p = os.path.join(h, rel)
        if not os.path.exists(p):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            shutil.copyfile(os.path.join(BIN, src), p)
            os.chmod(p, os.stat(p).st_mode | stat.S_IEXEC)
    return h


def copy(src, dst):
    if os.path.isdir(src):
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src.rstrip("/")))
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        if dst.endswith("/") or os.path.isdir(dst):
            os.makedirs(dst, exist_ok=True)
            dst = os.path.join(dst, os.path.basename(src))
        shutil.copyfile(src, dst)


def main():
    host, op, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    if host in os.environ.get("FAKE_VM_DOWN", "").split(","):
        print("ssh: connect to host timed out", file=sys.stderr); return 255
    h = home(host)
    with open(os.path.join(os.environ["FAKE_VM_ROOT"], "calls.log"), "a") as fh:
        fh.write(f"{host} {op} {' '.join(args)[:200]}\n")
    if op == "run":
        env = dict(os.environ, HOME=h, PATH=os.path.join(BIN, "path") + os.pathsep + os.environ["PATH"])
        p = subprocess.run(["bash", "-c", " ".join(args)], cwd=h, env=env)
        return p.returncode
    if op == "put":
        *srcs, dst = args
        for s in srcs:
            copy(s, os.path.join(h, dst))
        return 0
    if op == "get":
        src, dst = args
        copy(os.path.join(h, src), dst)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
