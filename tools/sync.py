#!/usr/bin/env python3
"""sync.py — vendor pnkit into a project and pin it.

    python3 tools/sync.py PROJECT_DIR [--dry-run]

Copies the package (pnkit/*.py) and the component catalog (kit.json) into PROJECT_DIR/film/vendor/pnkit/, replacing
what was there, makes sure PROJECT_DIR/film/vendor/__init__.py exists (so `from vendor import pnkit` finds this
copy first), and writes PROJECT_DIR/film/vendor/pnkit.lock: the version, the library commit it came from, and the
SHA-256 of every vendored file. tools/check_lock.py verifies a project against its lock.

The vendored copy is part of the project: edit the library, not the copy, and sync again.
"""
import argparse, hashlib, json, os, shutil, subprocess, sys

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(LIB, "pnkit")
VENDOR_INIT = '"""Vendored libraries, pinned by their lock files (pnkit.lock). Written by pnkit\'s tools/sync.py: edit the library, not the copies."""\n'


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def package_files():
    """[(relative path, source path)] of what is vendored, sorted"""
    out = [(n, os.path.join(PKG, n)) for n in sorted(os.listdir(PKG)) if n.endswith(".py")]
    out.append(("kit.json", os.path.join(LIB, "kit.json")))
    return out


def version():
    ns = {}
    for line in open(os.path.join(PKG, "__init__.py"), encoding="utf-8"):
        if line.startswith("__version__"):
            exec(line, ns)
    return ns["__version__"]


def commit():
    """(HEAD commit or None, whether the package or catalog differ from it)"""
    try:
        head = subprocess.run(["git", "-C", LIB, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", LIB, "status", "--porcelain", "--", "pnkit", "kit.json"], capture_output=True, text=True,
                               check=True).stdout.strip() != ""
        return head, dirty
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project", help="the project directory (contains film/)")
    ap.add_argument("--dry-run", action="store_true", help="print what would be written")
    args = ap.parse_args()
    film = os.path.join(os.path.abspath(args.project), "film")
    if not os.path.isdir(film):
        sys.exit(f"sync: {film} is not a directory (a project has its generators in film/)")
    kit = json.load(open(os.path.join(LIB, "kit.json"), encoding="utf-8"))
    ver = version()
    if kit.get("version") != ver:
        sys.exit(f"sync: kit.json says {kit.get('version')}, pnkit/__init__.py says {ver}")
    dest = os.path.join(film, "vendor", "pnkit")
    files = package_files()
    head, dirty = commit()
    lock = {"package": "pnkit", "version": ver, "source": LIB, "commit": head, "dirty": dirty,
            "files": {rel: sha256(src) for rel, src in files}}
    if args.dry_run:
        print(json.dumps(lock, indent=1)); return
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for rel, src in files:
        shutil.copyfile(src, os.path.join(dest, rel))
    init = os.path.join(film, "vendor", "__init__.py")
    if not os.path.exists(init):
        open(init, "w", encoding="utf-8").write(VENDOR_INIT)
    with open(os.path.join(film, "vendor", "pnkit.lock"), "w", encoding="utf-8") as fh:
        json.dump(lock, fh, indent=1, sort_keys=True); fh.write("\n")
    note = "" if head and not dirty else "  (library has uncommitted changes: commit it and sync again before delivery)"
    print(f"pnkit {ver} -> {dest}: {len(files)} files, commit {head[:12] if head else 'none'}{note}")


if __name__ == "__main__":
    main()
