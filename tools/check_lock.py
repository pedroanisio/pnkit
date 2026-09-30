#!/usr/bin/env python3
"""check_lock.py — verify a project's vendored pnkit against its lock.

    python3 tools/check_lock.py PROJECT_DIR [--latest]

Checks that PROJECT_DIR/film/vendor/pnkit.lock exists, that every file it lists is present with that SHA-256, that
the copy holds no files the lock does not list (caches aside), and that the copy's __version__ is the lock's
version. --latest also reports whether the library here has a newer version than the vendored one.
Exit status: 0 when the copy matches its lock, 1 otherwise.
"""
import argparse, hashlib, json, os, re, sys

LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def read_version(init_path):
    m = re.search(r'^__version__ = "([^"]+)"', open(init_path, encoding="utf-8").read(), re.M)
    return m.group(1) if m else None


def check(project):
    """-> (lock or None, [problems])"""
    vendor = os.path.join(os.path.abspath(project), "film", "vendor")
    lock_path, dest = os.path.join(vendor, "pnkit.lock"), os.path.join(vendor, "pnkit")
    if not os.path.exists(lock_path):
        return None, [f"no lock: {lock_path} (run tools/sync.py {project})"]
    lock = json.load(open(lock_path, encoding="utf-8"))
    problems = []
    for rel, want in sorted(lock.get("files", {}).items()):
        p = os.path.join(dest, rel)
        if not os.path.exists(p):
            problems.append(f"missing: {rel}")
        elif sha256(p) != want:
            problems.append(f"modified: {rel} (sha256 {sha256(p)[:12]}, lock {want[:12]})")
    if os.path.isdir(dest):
        for root, dirs, names in os.walk(dest):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for n in sorted(names):
                rel = os.path.relpath(os.path.join(root, n), dest).replace(os.sep, "/")
                if rel not in lock.get("files", {}):
                    problems.append(f"not in the lock: {rel}")
    init = os.path.join(dest, "__init__.py")
    if os.path.exists(init) and read_version(init) != lock.get("version"):
        problems.append(f"version: the copy says {read_version(init)}, the lock {lock.get('version')}")
    return lock, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("project")
    ap.add_argument("--latest", action="store_true", help="also compare with the library's current version")
    args = ap.parse_args()
    lock, problems = check(args.project)
    for p in problems:
        print("  " + p)
    if lock is not None:
        state = "OK" if not problems else f"{len(problems)} problem(s)"
        print(f"pnkit {lock.get('version')} (commit {str(lock.get('commit'))[:12]}{', dirty' if lock.get('dirty') else ''}): {state}")
        if args.latest:
            here = read_version(os.path.join(LIB, "pnkit", "__init__.py"))
            print(f"library: {here}" + ("" if here == lock.get("version") else "  (differs from the vendored copy: sync to update)"))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
