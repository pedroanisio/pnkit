"""pnkit.filmbuild.pack — the film's package (a .vpkg.zip in the scene-video-package 1.1 layout, as the Lula 3.0.0
package), verified, then checked by rebuilding part of it.

  OUT/pack/<id>-<version>/           the tree: vpkg.json, README.md, project/ (film.json, src/ snapshot, xml/ documents and
                                     audio, SHA256SUMS, render.json with the host CPU of each segment, GATES.md, REBUILD.md,
                                     film-meta.json, join.py). The film and segment media are not packed; their sha256 are.
  OUT/<id>-<version>.vpkg.zip        deterministic (sorted names, fixed dates); write-once: a different package under an
                                     existing version is refused (bump film.version)
  verify                             every member read back and compared with MANIFEST (sha256 per file)
  rebuild check                      the first pack.rebuild_segments segments and the audio rendered again on the hub FROM
                                     THE PACKAGE'S documents, compared by sha256 (and by PSNR at three frames when not
                                     identical): the package's claim is "byte-identical" or "within X dB", never assumed
  filing                             only when pack.file_to is set: the zip and its .sha256 copied there, write-once
"""
import hashlib, json, math, os, shutil, time, zipfile

from .. import __version__ as PNKIT_VERSION
from .remote import RemoteError
from .state import sha256_file, now

FIXED = (2026, 1, 1, 0, 0, 0)
EXCLUDE_DIRS = {"__pycache__", "seg"}


def _md(title, body, date):
    return ("---\ndisclaimer:\n  notice: >-\n    No information within this document should be taken for granted.\n"
            "    Any statement or premise not backed by a real logical definition\n    or verifiable reference may be invalid, erroneous, or a hallucination.\n"
            f'  generated_by: "pnkit {PNKIT_VERSION} film_build (pack stage)"\n  date: "{date}"\n---\n\n# {title}\n\n{body}\n')


def manifest(f, segs, nums, film_name, film_sha, audio_sha):
    r = f["render"]
    args = r["encode_args"]
    steps = [{"id": f"render-s{n:02d}", "kind": "render", "description": f"Render segment {n:02d} (video only).",
              "render": {"scene": f"xml/s{n:02d}.scene.xml", "output": "master", "args": {"rs": args}}, "outputs": [f"xml/seg/s{n:02d}.mp4"]}
             for n in nums]
    steps.append({"id": "render-audio", "kind": "render", "description": "Render the film's audio (m4a).",
                  "render": {"scene": "xml/full-audio.scene.xml", "output": "master", "args": {"rs": ["--strict", "--no-upload", "--hw", "software"]}},
                  "outputs": ["xml/final.m4a"]})
    steps.append({"id": "join", "kind": "mux", "needs": [s["id"] for s in steps], "run": ["python3", "join.py"],
                  "description": "Join the segments without recoding, mux the audio, compare with SHA256SUMS.", "inputs": ["SHA256SUMS"],
                  "outputs": [f"output/{film_name}"]})
    cpus = sorted({(v["cpu"], v["cores"]) for v in segs.values()})
    fm = f["film"]
    return {
        "$schema": "urn:scene-render:vpkg:1", "format": "scene-video-package", "formatVersion": "1.1",
        "package": {"id": fm["id"], "version": fm["version"], "title": fm["title"], "description": fm.get("description", fm["title"]),
                    "languages": [fm.get("lang", "pt-BR")]},
        "scenes": [{"path": "xml/full-audio.scene.xml", "role": "primary", "targets": ["rs"], "note": "The film's audio render (mix and normalisation)."}]
        + [{"path": f"xml/s{n:02d}.scene.xml", "role": "variant", "targets": ["rs"], "note": f"Video-only segment {n:02d}."} for n in nums],
        "include": ["/README.md", "/project/**"],
        "exclude": ["__pycache__/", "*.log", "*.tmp", "/project/xml/seg/", "/project/output/"],
        "requirements": {"tools": [{"name": "python", "version": ">=3.10", "for": ["mux"]}, {"name": "ffmpeg", "for": ["mux"]}], "python": [],
                         "notes": [f"rs-scene-render {r.get('engine_version') or '(version not recorded)'}, binary sha256 {r.get('engine_sha256') or '(not recorded)'}; "
                                   f"rendered with {' '.join(args)}; env {json.dumps(r['env'])}.",
                                   f"Rendered on {', '.join(f'{c} ({k} cores)' for c, k in cpus)}: see project/render.json for the host of each segment.",
                                   f"The film is not in the package; its sha256 is {film_sha} ({film_name}). Audio final.m4a sha256 {audio_sha}."]},
        "engines": [{"id": "rs", "impl": "rs-scene-render", "version": r.get("engine_version") or "unknown", "tested": "full"}],
        "pipeline": {"steps": steps, "deliverables": [{"path": f"output/{film_name}", "role": "master", "step": "join"}]},
        "editorial": {"native_visuals_only": True, "generative_images": False, "pixel_art_logical_grid": [320, 180],
                      "built_by": f"pnkit {PNKIT_VERSION} film_build"},
    }


def _tree(b):
    f = b.f
    J = json.load(open(b.p("join.json")))
    segs = json.load(open(b.p("render.json")))
    nums = [s["n"] for s in f["scenes"]]
    film_name = J["film"]
    pk = os.path.join(b.out, "pack", f"{f.id}-{f.version}")
    if os.path.isdir(pk):
        shutil.rmtree(pk)
    pj = os.path.join(pk, "project")
    shutil.copytree(b.p("src"), os.path.join(pj, "src"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(b.p("xml"), os.path.join(pj, "xml"), ignore=shutil.ignore_patterns("__pycache__", "seg"))
    shutil.copyfile(f.file, os.path.join(pj, "film.json"))
    shutil.copyfile(os.path.join(b.out, "GATES.md"), os.path.join(pj, "GATES.md"))
    shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pack_join.py"), os.path.join(pj, "join.py"))
    audio_sha = sha256_file(b.p("final.m4a"))
    sums = [f"{segs[str(n)]['sha256']}  xml/seg/s{n:02d}.mp4" for n in nums] + [f"{audio_sha}  xml/final.m4a", f"{J['sha256']}  output/{film_name}"]
    open(os.path.join(pj, "SHA256SUMS"), "w").write("\n".join(sums) + "\n")
    json.dump({k: {x: v[x] for x in ("scene", "host", "hostname", "cpu", "cores", "engine_sha256", "sha256", "frames", "rendered")} for k, v in segs.items()},
              open(os.path.join(pj, "render.json"), "w"), indent=1, sort_keys=True)
    json.dump({"segments": [f"xml/seg/s{n:02d}.mp4" for n in nums], "audio": "xml/final.m4a", "film_name": film_name, "film_sha256": J["sha256"]},
              open(os.path.join(pj, "film-meta.json"), "w"), indent=1)
    json.dump(manifest(f, segs, nums, film_name, J["sha256"], audio_sha), open(os.path.join(pk, "vpkg.json"), "w"), indent=1, ensure_ascii=False)
    return pk, pj, segs, nums, J


def _zip(pk, dest):
    names = []
    for d, dirs, fs in os.walk(pk):
        dirs[:] = sorted(x for x in dirs if x not in EXCLUDE_DIRS)
        names += [os.path.relpath(os.path.join(d, n), pk).replace(os.sep, "/") for n in sorted(fs)]
    man = {n: sha256_file(os.path.join(pk, n)) for n in sorted(names)}
    import io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in sorted(names):
            zi = zipfile.ZipInfo(n, FIXED); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
            z.writestr(zi, open(os.path.join(pk, n), "rb").read())
        zi = zipfile.ZipInfo("MANIFEST.sha256", FIXED); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
        z.writestr(zi, "".join(f"{v}  {k}\n" for k, v in man.items()))
    data = buf.getvalue()
    if os.path.exists(dest):
        if open(dest, "rb").read() != data:
            raise FileExistsError(dest)
        return False, len(man)
    with open(dest, "xb") as o:
        o.write(data)
    return True, len(man)


def verify(zpath):
    """-> number of members checked; raises ValueError on a mismatch"""
    with zipfile.ZipFile(zpath) as z:
        if z.testzip() is not None:
            raise ValueError("zip CRC error")
        man = {ln.split("  ", 1)[1]: ln.split("  ", 1)[0] for ln in z.read("MANIFEST.sha256").decode().splitlines() if ln}
        for n, want in man.items():
            if hashlib.sha256(z.read(n)).hexdigest() != want:
                raise ValueError(f"{n}: sha256 differs from MANIFEST")
        extra = set(z.namelist()) - set(man) - {"MANIFEST.sha256"}
        if extra:
            raise ValueError(f"members not in MANIFEST: {sorted(extra)}")
    return len(man)


def rebuild_check(b, pj, segs, nums, n_seg):
    """render n_seg segments and the audio from the package's documents on the hub; compare"""
    from .stages import StageFailed
    f = b.f
    r, hub = f["render"], f["render"]["hub"]
    rr = f"{b.rdir}/rebuild"
    pick = nums[:max(0, n_seg)]
    b.remote.run(hub, f'rm -rf "$HOME/{rr}" && mkdir -p "$HOME/{rr}/xml/audio"')
    b.remote.put(hub, [os.path.join(pj, "xml", f"s{n:02d}.scene.xml") for n in pick] + [os.path.join(pj, "xml", "full-audio.scene.xml")], f"{rr}/xml/")
    ad = os.path.join(pj, "xml", "audio")
    b.remote.put(hub, [os.path.join(ad, x) for x in sorted(os.listdir(ad))], f"{rr}/xml/audio/")
    args = " ".join(f"'{a}'" for a in r["encode_args"])
    job = (f'cd "$HOME/{rr}/xml" && {b.env()} E="$HOME/{r["engine"]}"; '
           + "".join(f'"$E" encode s{n:02d}.scene.xml --output master {args} > s{n:02d}.log 2>&1 || exit 3; ' for n in pick)
           + '"$E" encode full-audio.scene.xml --output master --strict --no-upload --hw software > final.log 2>&1 || exit 4; '
           + "sha256sum " + " ".join(f"seg/s{n:02d}.mp4" for n in pick) + " final.m4a; "
           + 'echo "CPU=$(grep -m1 "model name" /proc/cpuinfo | sed "s/^[^:]*: *//") CORES=$(nproc)"')
    try:
        out = b.remote.run(hub, b.locked(job), timeout=r["timeout_s"])
    except RemoteError as e:
        raise StageFailed(f"rebuild check on {hub}: {e}")
    got = {ln.split()[1]: ln.split()[0] for ln in out.splitlines() if len(ln.split()) == 2 and len(ln.split()[0]) == 64}
    rows = []
    for n in pick:
        same = got.get(f"seg/s{n:02d}.mp4") == segs[str(n)]["sha256"]
        row = {"segment": f"s{n:02d}", "identical": same, "built_on": segs[str(n)]["host"], "rebuilt_on": hub}
        if not same:
            frames = segs[str(n)]["frames"] or 1
            idx = ",".join(str(i) for i in sorted({0, frames // 2, frames - 1}))
            b.remote.run(hub, f'mkdir -p "$HOME/{rr}/orig"')
            b.remote.put(hub, [b.p("seg", f"s{n:02d}.mp4")], f"{rr}/orig/")
            ps = json.loads(b.remote.run(hub, b.locked(f'cd "$HOME/{rr}" && ' + b.remote_python(f"pnkit.filmbuild.jobs psnr orig/s{n:02d}.mp4 xml/seg/s{n:02d}.mp4 {idx}"))).strip().splitlines()[-1])
            row["psnr_db"] = ps
        rows.append(row)
    audio_same = got.get("final.m4a") == sha256_file(b.p("final.m4a"))
    host = [ln for ln in out.splitlines() if ln.startswith("CPU=")]
    return {"segments": rows, "audio_identical": audio_same, "host": host[0] if host else None, "checked": now()}


def pack(b):
    from .stages import StageFailed
    f, t0 = b.f, time.time()
    J = json.load(open(b.p("join.json")))
    inputs = [os.path.join(b.out, J["film"]), b.p("render.json"), b.p("xml"), b.p("src"), os.path.join(b.out, "GATES.md"), b.p("final.m4a")]
    cfg = {"pack": f["pack"], "film": f["film"], "pnkit": PNKIT_VERSION}
    if b.fresh("pack", inputs, cfg):
        return "cached", b.last("pack")
    pk, pj, segs, nums, J = _tree(b)
    zpath = os.path.join(b.out, f"{f.id}-{f.version}.vpkg.zip")
    reb = rebuild_check(b, pj, segs, nums, f["pack"]["rebuild_segments"])
    worst = [x["psnr_db"] for x in reb["segments"] if not x["identical"]]
    if not worst and reb["audio_identical"]:
        claim = f"byte-identical: {len(reb['segments'])} segment(s) and the audio re-rendered from the package's documents on {reb['segments'][0]['rebuilt_on'] if reb['segments'] else f['render']['hub']} matched"
    else:
        lows = [p["psnr_db"] for w in worst for p in w if p["psnr_db"] != "inf"]
        claim = (f"NOT byte-identical: {len(worst)} of {len(reb['segments'])} segments differ (lowest PSNR {min(lows) if lows else 'inf'} dB)"
                 + ("" if reb["audio_identical"] else "; the audio differs"))
    json.dump(dict(reb, claim=claim), open(os.path.join(pj, "rebuild.json"), "w"), indent=1)
    date = now()[:10]
    cpus = sorted({(v["cpu"], v["cores"]) for v in segs.values()})
    open(os.path.join(pj, "REBUILD.md"), "w", encoding="utf-8").write(_md(
        f"Rebuilding {f['film']['title']} {f.version}",
        "Written for: whoever rebuilds this film from the package.\n\n"
        f"**Claim, measured {date}:** {claim} (`rebuild.json`).\n\n"
        "## Steps\n\n"
        f"1. Engine: rs-scene-render {f['render'].get('engine_version') or ''} with sha256 `{f['render'].get('engine_sha256') or 'not recorded'}`; "
        f"environment {json.dumps(f['render']['env'])}.\n"
        f"2. Render each `xml/sNN.scene.xml` (output `master`, args `{' '.join(f['render']['encode_args'])}`) and `xml/full-audio.scene.xml`.\n"
        "3. `python3 join.py`: joins without recoding, muxes the audio and compares every file with `SHA256SUMS`.\n\n"
        "## What can differ\n\n"
        f"The segments were rendered on {', '.join(f'{c} ({k} cores)' for c, k in cpus)} (`render.json` names the host of each). "
        "A software H.264 encoder whose thread count follows the core count writes different bytes on a host with another core count "
        "(Lula 3.0.0, 2026-10-09; engine v0.2.1 pins the encoder threads). Rebuild on a host of the same CPU and core count, "
        "or expect 'within X dB', not byte-identical.\n\n"
        "## Regenerate the documents\n\n"
        "`src/` is the snapshot film_build built from: `film.json`, `timings.json`, the scene modules and the plan. "
        f"With pnkit {PNKIT_VERSION} on the path, `python3 tools/film_build.py project/film.json snapshot generate assemble` rebuilds `xml/`.", date))
    open(os.path.join(pk, "README.md"), "w", encoding="utf-8").write(_md(
        f"{f['film']['title']} {f.version}",
        f"{f['film'].get('description', '')}\n\nPackage made by pnkit {PNKIT_VERSION} film_build on {date}. "
        f"Film `{J['film']}`, sha256 `{J['sha256']}`. Gates: `project/GATES.md`. Rebuild: `project/REBUILD.md` ({claim}).", date))
    try:
        new, members = _zip(pk, zpath)
    except FileExistsError:
        raise StageFailed(f"{os.path.relpath(zpath, f.root)} exists with other content: a package version is not rewritten (bump film.version)")
    n = verify(zpath)
    zsha = sha256_file(zpath)
    open(zpath + ".sha256", "w").write(f"{zsha}  {os.path.basename(zpath)}\n")
    filed = ""
    if f["pack"].get("file_to"):
        dest_dir = f.path(f["pack"]["file_to"])
        dest = os.path.join(dest_dir, os.path.basename(zpath))
        if os.path.exists(dest) and sha256_file(dest) != zsha:
            raise StageFailed(f"filing: {dest} exists with other content")
        if not os.path.exists(dest):
            shutil.copyfile(zpath, dest)
            open(dest + ".sha256", "w").write(f"{zsha}  {os.path.basename(zpath)}\n")
        filed = f"; filed in {os.path.relpath(dest_dir, f.root)}"
    note = f"{os.path.relpath(zpath, f.root)} ({n} files verified, sha256 {zsha[:16]}); rebuild {claim}{filed}"
    return "ran", b.done("pack", inputs, cfg, [zpath, zpath + ".sha256"], note, summary={"rebuild": reb}, t0=t0)
