"""pnkit.filmbuild.remote — the render hosts, reached through one runner script with the interface of vmrun.sh:

    RUNNER HOST run 'command'        RUNNER HOST put LOCAL... REMOTE        RUNNER HOST get REMOTE LOCAL

The runner comes from film.json render.runner (a path; a relative one is looked up from the film's folder and its
parents, then from the working directory and its parents) or from the environment, PNKIT_VM_RUNNER, which wins.
Remote paths are relative to the host's $HOME. Commands are run without a local shell; the remote command is one
argument. Only the last 400 characters of a failing command's output are shown, and nothing else is printed.
"""
import os, shlex, subprocess


class RemoteError(RuntimeError):
    pass


def find_runner(spec, start):
    spec = os.environ.get("PNKIT_VM_RUNNER") or spec
    if not spec:
        raise RemoteError("no runner: set render.runner in film.json or PNKIT_VM_RUNNER")
    if os.path.isabs(spec):
        return spec
    for base in (start, os.getcwd()):
        d = os.path.abspath(base)
        while True:
            cand = os.path.join(d, spec)
            if os.path.exists(cand):
                return cand
            up = os.path.dirname(d)
            if up == d:
                break
            d = up
    raise RemoteError(f"runner {spec!r} not found from {start} or the working directory")


def q(s):
    """shell-quote a remote word"""
    return shlex.quote(str(s))


class Remote:
    def __init__(self, runner):
        self.runner = runner
        self.calls = 0

    def _call(self, argv, timeout):
        self.calls += 1
        try:
            p = subprocess.run([self.runner] + argv, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise RemoteError(f"{argv[0]} {argv[1]}: timed out after {timeout} s")
        if p.returncode:
            tail = (p.stdout + p.stderr)[-400:]
            raise RemoteError(f"{argv[0]} {argv[1]} failed (exit {p.returncode}): {tail}")
        return p.stdout

    def run(self, host, cmd, timeout=1800):
        return self._call([host, "run", cmd], timeout)

    def put(self, host, srcs, dst, timeout=3600):
        return self._call([host, "put"] + list(srcs) + [dst], timeout)

    def get(self, host, src, dst, timeout=3600):
        return self._call([host, "get", src, dst], timeout)
