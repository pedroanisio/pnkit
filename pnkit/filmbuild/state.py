"""pnkit.filmbuild.state — what each stage last did, so a stage reruns only when its inputs changed.

Each stage writes OUT/state/<stage>.json when it finishes: {stage, status, inputs {path: sha256}, config sha256,
outputs {path: sha256}, summary, started, finished, seconds}. A stage is fresh when its record says ok, the inputs and
the config hash the same, and every output still exists with its recorded hash. Paths in records are relative to the
film folder. Records are measurements, overwritten on each run; the films (OUT/<name>-vN.mp4) are write-once.
"""
import datetime, hashlib, json, os


def sha256_file(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(block), b""):
            h.update(b)
    return h.hexdigest()


def sha256_json(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Ledger:
    def __init__(self, root, out):
        self.root = root
        self.dir = os.path.join(out, "state")
        os.makedirs(self.dir, exist_ok=True)

    def rel(self, p):
        return os.path.relpath(os.path.abspath(p), self.root).replace(os.sep, "/")

    def hashes(self, paths):
        """{relative path: sha256} of files (directories are walked, sorted; __pycache__ skipped)"""
        out = {}
        for p in paths:
            if p is None:
                continue
            if os.path.isdir(p):
                for d, dirs, names in os.walk(p):
                    dirs[:] = sorted(x for x in dirs if x != "__pycache__")
                    for n in sorted(names):
                        q = os.path.join(d, n)
                        out[self.rel(q)] = sha256_file(q)
            elif os.path.exists(p):
                out[self.rel(p)] = sha256_file(p)
            else:
                out[self.rel(p)] = None
        return out

    def path(self, stage):
        return os.path.join(self.dir, f"{stage}.json")

    def load(self, stage):
        try:
            return json.load(open(self.path(stage), encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def save(self, stage, rec):
        tmp = self.path(stage) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1, ensure_ascii=False, sort_keys=True)
        os.replace(tmp, self.path(stage))

    def fresh(self, stage, inputs, config):
        rec = self.load(stage)
        if not rec or rec.get("status") != "ok" or rec.get("inputs") != inputs or rec.get("config") != sha256_json(config):
            return False
        for rel, sha in rec.get("outputs", {}).items():
            p = os.path.join(self.root, rel)
            if not os.path.exists(p) or sha256_file(p) != sha:
                return False
        return True


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj, **kw):
    kw.setdefault("ensure_ascii", False)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, **kw)


def read_text(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def write_bytes(path, data):
    with open(path, "wb") as fh:
        fh.write(data)
