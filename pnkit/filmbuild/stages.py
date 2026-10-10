"""pnkit.filmbuild.stages — the stages of film_build, in order. Each one is restartable: it hashes its inputs and its
part of film.json, skips itself when the last run had the same and its outputs are intact, and records what it made.

  snapshot  freeze the inputs (film.json, the one timings file, plan, waivers, scene modules, narrative, sound sources)
            into OUT/build/src; refuse a second timings*.json in the film folder
  voice     none: nothing to do. command: the pronunciation list and its clips, one take per scene by the film's TTS
            command, then the film's timings (written words with the spoken times)
  plan      the plan by itself (stacked plates, slots against the timings) and the timings diff against the last build
  generate  every scene built on CheckedCtx (twice, with two hash seeds, which must agree), the build-time picture
            checks with the waivers, the built shots against the plan
  assemble  one video-only document per scene (captions with the caption text gate when the film has them), the audio
            document and its four stems; the score is regenerated from its script and must match
  render    the segments over film.json's hosts under the lock, the per-segment check on each, sha256 and the host's CPU
            and core count per segment; only segments whose document or engine changed are rendered again
  audio     the audio document and the stems on the hub
  join      lossless join and mux on the hub; OUT/<name>-vN.mp4 (write-once: a new N when the bytes change)
  gates     the film gates on the delivered file, judged, written as OUT/build/gates/*.json and OUT/GATES.md
  sheets    1 s sheets of the film into OUT/sheets/<name>-vN/ (read by a person; the summary only names flagged spans)
  pack      the vpkg (vpkg.json from film.json, SHA256SUMS with host CPUs, GATES.md, REBUILD.md), verified, and a
            rebuild check of N segments and the audio on the hub; filed only when film.json pack.file_to is set
"""
import io, json, math, os, shutil, subprocess, sys, tarfile, time, zipfile

from .. import __version__ as PNKIT_VERSION, files
from . import assemble as asm, gates as G, voice as V
from .config import FilmError
from .remote import Remote, RemoteError, find_runner, q
from .state import Ledger, sha256_file, sha256_json, now, read_json, write_json, read_text, write_text, read_bytes, write_bytes

ORDER = ["snapshot", "voice", "plan", "generate", "assemble", "render", "audio", "join", "gates", "sheets", "pack"]
LIB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))      # the folder that holds pnkit/


class StageFailed(RuntimeError):
    pass


class Build:
    def __init__(self, film, force=False, remote=None, log=None):
        self.f = film
        self.force = force
        self.out = film.out
        self.b = film.build
        os.makedirs(self.b, exist_ok=True)
        self.L = Ledger(film.root, self.out)
        self._remote = remote
        self.log = log or (lambda m: None)

    # ---------------------------------------------------------------- helpers
    def p(self, *parts):
        return os.path.join(self.b, *parts)

    @property
    def remote(self):
        if self._remote is None:
            self._remote = Remote(find_runner(self.f["render"]["runner"], self.f.root))
        return self._remote

    @property
    def rdir(self):
        return self.f["render"]["remote_dir"]

    def fresh(self, stage, inputs, cfg):
        return not self.force and self.L.fresh(stage, self.L.hashes(inputs), cfg)

    def done(self, stage, inputs, cfg, outputs, note, summary=None, t0=None):
        self.L.save(stage, {"stage": stage, "status": "ok", "inputs": self.L.hashes(inputs), "config": sha256_json(cfg),
                            "outputs": {k: v for k, v in self.L.hashes(outputs).items() if v}, "note": note, "summary": summary or {},
                            "finished": now(), "seconds": round(time.time() - t0, 1) if t0 else None, "pnkit": PNKIT_VERSION})
        return note

    def last(self, stage):
        rec = self.L.load(stage)
        return rec.get("note", "") if rec else ""

    def scenes(self):
        return self.f["scenes"]

    def timings(self):
        return read_json(self.p("src", "timings.json"))

    def duration(self):
        return self.timings()["scenes"][-1]["slot_end"]

    def remote_python(self, module_args):
        r = self.f["render"]
        return f'PYTHONPATH="$HOME/{self.rdir}/lib" "$HOME/{r["python"]}" -m {module_args}'

    def locked(self, cmd):
        return f'flock "$HOME/{self.f["render"]["lock"]}" bash -c {q(cmd)}'

    def env(self):
        out = []
        for k, v in sorted(self.f["render"]["env"].items()):
            if not k.replace("_", "").isalnum():
                raise FilmError(f"render.env: bad name {k!r}")
            out.append(f"export {k}={q(v)};")
        return " ".join(out)

    def put_lib(self, host):
        """pnkit itself, as the code that runs the checks on the host (re-sent when it changes)"""
        tar = self.p("pnkit.tar")
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as t:
            for d, dirs, names in os.walk(os.path.join(LIB, "pnkit")):
                dirs[:] = sorted(x for x in dirs if x != "__pycache__")
                for n in sorted(names):
                    full = os.path.join(d, n)
                    info = t.gettarinfo(full, arcname=os.path.relpath(full, LIB))
                    info.mtime = 0; info.uid = info.gid = 0; info.uname = info.gname = ""
                    with open(full, "rb") as fh:
                        t.addfile(info, fh)
        data = buf.getvalue()
        if not os.path.exists(tar) or read_bytes(tar) != data:
            write_bytes(tar, data)
        sha = sha256_file(tar)
        have = self.remote.run(host, f'cat "$HOME/{self.rdir}/lib/.sha" 2>/dev/null || true').strip()
        if have != sha:
            self.remote.run(host, f'mkdir -p "$HOME/{self.rdir}/lib"')
            self.remote.put(host, [tar], f"{self.rdir}/lib/pnkit.tar")
            self.remote.run(host, f'cd "$HOME/{self.rdir}/lib" && rm -rf pnkit && tar xf pnkit.tar && rm pnkit.tar && echo {sha} > .sha')

    # ---------------------------------------------------------------- snapshot
    def snapshot(self):
        f = self.f
        t0 = time.time()
        pic, aud, vc = f["picture"], f["audio"], f["voice"]
        tim = f.path(f["timings"])
        others = []
        for d, dirs, names in os.walk(f.root):
            dirs[:] = [x for x in dirs if os.path.join(d, x) != f.out and x not in ("__pycache__", ".git")]
            for n in names:
                pth = os.path.join(d, n)
                if n.startswith("timings") and n.endswith(".json") and os.path.abspath(pth) != tim:
                    others.append(os.path.relpath(pth, f.root))
        if others:
            raise StageFailed(f"one timings file: {f['timings']} is the source, but {sorted(others)} also exist (rename or delete them)")
        scenes_dir = f.path(pic["scenes_dir"])
        sources = {"film.json": f.file, "timings.json": tim if vc["mode"] == "none" or os.path.exists(tim) else None}
        for k in ("plan", "waivers"):
            if pic.get(k):
                sources[os.path.basename(pic[k])] = f.path(pic[k])
        if vc["mode"] == "command":
            sources["narrative.json"] = f.path(vc["script"])
        for sc in f["scenes"]:
            sources[f"scenes/{sc['module']}.py"] = os.path.join(scenes_dir, sc["module"] + ".py")
        sources.update({os.path.join("sound", os.path.basename(f.path(a))): f.path(a) for a in (aud.get("score_script") or [])[1:2]})
        inputs = [v for v in sources.values() if v]
        for v in inputs:
            if not os.path.exists(v):
                raise StageFailed(f"missing input: {os.path.relpath(v, f.root)}")
        if self.fresh("snapshot", inputs, sources):
            return "cached", self.last("snapshot")
        src = self.p("src")
        if os.path.isdir(src):
            shutil.rmtree(src)
        for rel, pth in sources.items():
            if pth:
                os.makedirs(os.path.dirname(os.path.join(src, rel)), exist_ok=True)
                shutil.copyfile(pth, os.path.join(src, rel))
        if sources["timings.json"]:
            try:
                f.timings()
            except FilmError as e:
                raise StageFailed(str(e))
        rows = {rel: sha256_file(os.path.join(src, rel)) for rel in sorted(sources) if sources[rel]}
        write_json(os.path.join(src, "SNAPSHOT.json"), rows, indent=1)
        outs = [os.path.join(src, r) for r in rows] + [os.path.join(src, "SNAPSHOT.json")]
        return "ran", self.done("snapshot", inputs, sources, outs, f"{len(rows)} files, {len(f['scenes'])} scene modules", t0=t0)

    # ---------------------------------------------------------------- voice
    def voice(self):
        f, t0 = self.f, time.time()
        vc = f["voice"]
        if vc["mode"] == "none":
            return "skipped", "no narration (voice.mode none): the timings are the authored file"
        nar = self.p("src", "narrative.json")
        inputs, cfg = [nar], dict(vc)
        if self.fresh("voice", inputs, cfg):
            return "cached", self.last("voice")
        N = read_json(nar)
        lang, engine = N.get("lang", "pt-br"), vc.get("engine", "kokoro")
        vd = self.p("voice"); os.makedirs(vd, exist_ok=True)
        text = " ".join(ln["text"] for sc in N["scenes"] for ln in sc["lines"])
        pr = V.pronounce_terms(text, lang, vc.get("terms", ()), engine)
        clips = 0
        if vc.get("pronounce"):
            os.makedirs(os.path.join(vd, "pronounce"), exist_ok=True)
            for i, t in enumerate(pr["terms"]):
                wav = os.path.join(vd, "pronounce", f"{i + 1:03d}.wav")
                if not os.path.exists(wav):
                    self._cmd(vc["pronounce"], {"term": t["spoken"], "wav": wav})
                t["clip"] = os.path.relpath(wav, vd); clips += 1
        write_json(os.path.join(vd, "pronounce.json"), pr, indent=1, ensure_ascii=False)
        takes, outs = {}, [os.path.join(vd, "pronounce.json")]
        from .. import vo
        for sc in N["scenes"]:
            spoken = " ".join(vo.speak(ln["text"], lang, engine, numbers=lang.lower().startswith("pt")) for ln in sc["lines"])
            tf, wav, words = (os.path.join(vd, f"{sc['id']}{ext}") for ext in (".txt", ".wav", ".words.json"))
            write_text(tf, spoken)
            self._cmd(vc["tts"], {"scene": sc["id"], "text": tf, "wav": wav, "words": words})
            W = read_json(words)
            takes[sc["n"]] = (W["duration"], [tuple(w) for w in W["words"]])
            outs += [tf, wav, words]
        T = V.build_timings(N, takes, lang, engine, vc["lead"], vc["tail"])
        tim = f.path(f["timings"])
        write_json(tim, T, indent=1, ensure_ascii=False)
        shutil.copyfile(tim, self.p("src", "timings.json"))
        return "ran", self.done("voice", inputs, cfg, outs + [tim], f"{len(pr['terms'])} terms to hear ({clips} clips), "
                                f"{len(takes)} takes, {sum(len(s['lines']) for s in T['scenes'])} sentences", t0=t0)

    def _cmd(self, argv, fill):
        cmd = [a.format(python=sys.executable, **fill) for a in argv]
        r = subprocess.run(cmd, cwd=self.f.root, capture_output=True, text=True)
        if r.returncode:
            raise StageFailed(f"{os.path.basename(cmd[0])} failed (exit {r.returncode}): {(r.stdout + r.stderr)[-300:]}")

    # ---------------------------------------------------------------- plan
    def plan(self):
        from ..pixelart import plan as P
        from .. import timings as TD
        t0 = time.time()
        pic = self.f["picture"]
        tim = self.p("src", "timings.json")
        pf = self.p("src", os.path.basename(pic["plan"])) if pic.get("plan") else None
        inputs, cfg = [tim, pf], {"plan": pic.get("plan")}
        if self.fresh("plan", inputs, cfg):
            return "cached", self.last("plan")
        T = self.timings()
        errs, note = [], []
        if pf:
            plan = P.parse_plan(read_text(pf))
            errs += P.check_plan_only(plan) + P.check_plan_slots(plan, T)
            note.append(f"{len(plan)} planned shots")
        else:
            note.append("no plan file")
        last = os.path.join(self.L.dir, "timings.last.json")
        moved = None
        if os.path.exists(last):
            d = TD.diff(TD.load_sentences(read_json(last)), TD.load_sentences(T))
            moved = {"sentences": len(d["sentences"]), "words": len(d["words"]), "only_a": d["only_a"], "only_b": d["only_b"]}
            write_json(self.p("timings-diff.json"), d, indent=1, ensure_ascii=False)
            note.append(f"timings moved since last build: {moved['sentences']} sentences, {moved['words']} words")
        write_json(self.p("plan-check.json"), {"errors": errs, "timings_moved": moved}, indent=1, ensure_ascii=False)
        if errs:
            raise StageFailed(f"{len(errs)} plan errors (build/plan-check.json): {errs[0]}")
        shutil.copyfile(tim, last)
        return "ran", self.done("plan", inputs, cfg, [self.p("plan-check.json")], "; ".join(note) + ", 0 errors", t0=t0)

    # ---------------------------------------------------------------- generate
    def generate(self):
        from ..pixelart import plan as P
        from ..pixelart.checks import apply_waivers
        t0 = time.time()
        pic = self.f["picture"]
        src = self.p("src")
        inputs = [os.path.join(src, "scenes"), os.path.join(src, "timings.json"), os.path.join(src, "film.json")]
        inputs += [self.p("src", os.path.basename(pic[k])) for k in ("plan", "waivers") if pic.get(k)]
        lib_hash = Ledger(LIB, self.out).hashes([os.path.join(LIB, "pnkit", "pixelart")])
        cfg = {"seeds": pic["determinism_seeds"], "pixelart": sha256_json(lib_hash)}
        if self.fresh("generate", inputs, cfg):
            return "cached", self.last("generate")
        out = self.p("picture")
        runs = []
        for i, seed in enumerate(pic["determinism_seeds"]):
            d = out if i == 0 else self.p(f"picture-seed{seed}")
            env = dict(os.environ, PYTHONHASHSEED=str(seed), PYTHONPATH=LIB + os.pathsep + os.environ.get("PYTHONPATH", ""))
            r = subprocess.run([sys.executable, "-m", "pnkit.filmbuild.generate", src, d], capture_output=True, text=True, env=env, cwd=src)
            if r.returncode:
                raise StageFailed(f"scene build failed (seed {seed}): {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.stdout[-300:]}")
            runs.append(json.loads(r.stdout.strip().splitlines()[-1]))
            if i:
                shutil.rmtree(d)
        if any(x != runs[0] for x in runs[1:]):
            bad = sorted(k for k in runs[0] if any(x.get(k) != runs[0][k] for x in runs[1:]))
            raise StageFailed(f"not deterministic across hash seeds {pic['determinism_seeds']}: {bad}")
        wv = read_json(self.p("src", os.path.basename(pic["waivers"]))) if pic.get("waivers") else []
        found, unused = apply_waivers(read_json(os.path.join(out, "findings.json")), wv, report_unused=True)
        built = [s for sc in self.scenes() for s in read_json(os.path.join(out, f"shots-{sc['n']:02d}.json"))]
        errs, warns = [], []
        if pic.get("plan"):
            errs, warns = P.check_built(built, P.parse_plan(read_text(self.p("src", os.path.basename(pic["plan"])))), self.timings())
        write_json(os.path.join(out, "all-shots.json"), built, ensure_ascii=False)
        rep = {"scene_sha256": runs[0], "seeds": pic["determinism_seeds"], "picture_findings": found, "unused_waivers": unused,
               "plan_errors": errs, "plan_warnings": warns}
        write_json(self.p("generate.json"), rep, indent=1, ensure_ascii=False)
        open_ = [x for x in found if not x["waived"]]
        if errs or open_:
            raise StageFailed(f"{len(errs)} plan errors, {len(open_)} open picture findings (build/generate.json)"
                              + (f": {(errs or [x['check'] + ' ' + x['shot'] for x in open_])[0]}"))
        outs = [os.path.join(out, k) for k in runs[0]] + [os.path.join(out, f"shots-{sc['n']:02d}.json") for sc in self.scenes()] + [self.p("generate.json")]
        return "ran", self.done("generate", inputs, cfg, outs,
                                f"{len(runs[0])} scenes, {len(built)} shots, identical over seeds {pic['determinism_seeds']}; "
                                f"picture findings {len(found)} ({len(found) - len(open_)} waived); plan 0 errors, {len(warns)} warnings", t0=t0)

    # ---------------------------------------------------------------- assemble
    def assemble(self):
        f, t0 = self.f, time.time()
        aud, cap, pic = f["audio"], f["captions"], f["picture"]
        T = self.timings()
        xd = self.p("xml"); ad = os.path.join(xd, "audio")
        os.makedirs(ad, exist_ok=True)
        inputs = [self.p("picture"), self.p("src", "timings.json"), self.p("src", "sound")]
        inputs += [f.path(aud[k]) for k in ("score", "sfx") if aud.get(k)]
        if f["voice"]["mode"] == "command":
            inputs.append(self.p("voice"))
        cfg = {"audio": aud, "captions": cap, "picture": {k: pic[k] for k in ("fps", "unit")}, "title": f["film"]["title"]}
        if self.fresh("assemble", inputs, cfg):
            return "cached", self.last("assemble")
        notes = []
        if aud.get("score_script"):                                   # the score is a product of its script: regenerate and compare
            tmp = self.p("score-check.wav")
            argv = [a if a != aud["score_script"][1] else self.p("src", "sound", os.path.basename(a)) for a in aud["score_script"]]
            self._cmd(argv, {"out": tmp})
            if sha256_file(tmp) != sha256_file(f.path(aud["score"])):
                raise StageFailed(f"the score {aud['score']} is not what its script makes now (regenerate it, or fix the script)")
            os.remove(tmp)
            notes.append("score regenerated bit-identical")
        assets, voices = {}, []
        for k in ("score", "sfx"):
            if aud.get(k):
                shutil.copyfile(f.path(aud[k]), os.path.join(ad, f"{k}.wav"))
                assets[k] = (f"audio/{k}.wav", sha256_file(os.path.join(ad, f"{k}.wav")))
        if f["voice"]["mode"] == "command":
            for sc in T["scenes"]:
                shutil.copyfile(self.p("voice", f"{sc['id']}.wav"), os.path.join(ad, f"vo_{sc['id']}.wav"))
                assets[f"vo_{sc['id']}"] = (f"audio/vo_{sc['id']}.wav", sha256_file(os.path.join(ad, f"vo_{sc['id']}.wav")))
                voices.append((f"vo_{sc['id']}", sc["voice_start"]))
        dur = self.duration()
        unit, fps = pic["unit"], pic["fps"]
        outs, cue_out, cap_findings = [], [], []
        if cap["enabled"]:
            from .. import captions as CP
            approved = " ".join(ln["caption"] for sc in T["scenes"] for ln in sc.get("lines", []))
            words = [tuple(w) for sc in T["scenes"] for ln in sc.get("lines", []) for w in ln["words"]]
            cues = CP.timed(CP.split_cues(words, cap["width"]))
            cap_findings = [str(x) for x in CP.check_text(cues, approved, cap["lang"])]
            write_json(self.p("caption-gate.json"), {"findings": cap_findings}, indent=1, ensure_ascii=False)
            if cap_findings:
                raise StageFailed(f"caption text gate: {len(cap_findings)} findings: {cap_findings[0]}")
            pages = asm.caption_pages(cues, cap["width"], unit)
            cue_out = [{"text": "\n".join(ln), "start": round(a, 3), "end": round(b, 3)} for ln, a, b in pages]
            notes.append(f"{len(pages)} caption pages, text gate 0 findings")
        for sc in T["scenes"]:
            n = sc["n"]
            pg = [(c["text"].split("\n"), c["start"], c["end"]) for c in cue_out if sc["slot_start"] <= c["start"] < sc["slot_end"]]
            x = asm.segment_xml(read_bytes(self.p("picture", f"scene_{n:02d}.xml")), sc, dur, f"seg/s{n:02d}.mp4",
                                f["film"]["title"], pg, unit)
            p_ = os.path.join(xd, f"s{n:02d}.scene.xml"); write_bytes(p_, x); outs.append(p_)
        proj = {"width": 320 * unit, "height": 180 * unit, "fps": fps}
        music, sfx = ("score" if aud.get("score") else None), ("sfx" if aud.get("sfx") else None)
        stems = ["full"] + [k for k, has in (("voice", voices), ("music", music), ("sfx", sfx)) if has]   # an empty mix is invalid (C35)
        for n in os.listdir(xd):
            if n.startswith("stem-") and n.endswith(".scene.xml"):
                os.remove(os.path.join(xd, n))
        for stem in [None] + stems:
            x = asm.audio_xml(proj, dur, assets, voices, music, sfx, aud, stem=stem)
            p_ = os.path.join(xd, "full-audio.scene.xml" if stem is None else f"stem-{stem}.scene.xml"); write_bytes(p_, x); outs.append(p_)
        write_json(os.path.join(xd, "stems.json"), stems); outs.append(os.path.join(xd, "stems.json"))
        if cue_out:
            write_json(os.path.join(xd, "cues.json"), {"cues": cue_out}, indent=1, ensure_ascii=False)
            outs.append(os.path.join(xd, "cues.json"))
        outs += [os.path.join(ad, n) for n in sorted(os.listdir(ad))]
        ml = asm.music_layer(read_bytes(os.path.join(xd, "full-audio.scene.xml")))
        notes.append(f"music layer: {', '.join(ml) or 'NONE'}")
        return "ran", self.done("assemble", inputs, cfg, outs, f"{len(T['scenes'])} segment documents, audio + stems ({', '.join(stems)}); " + "; ".join(notes), t0=t0)

    # ---------------------------------------------------------------- render
    def _seg_key(self, n):
        r = self.f["render"]
        return sha256_json({"xml": sha256_file(self.p("xml", f"s{n:02d}.scene.xml")), "shots": sha256_file(self.p("picture", f"shots-{n:02d}.json")),
                            "engine": r["engine"], "engine_sha256": r["engine_sha256"], "args": r["encode_args"], "env": r["env"]})

    def _assign(self, todo):
        """longest first onto the least-loaded host"""
        T = {s["n"]: s for s in self.timings()["scenes"]}
        load = {h: 0.0 for h in self.f["render"]["hosts"]}
        bins = {h: [] for h in load}
        for n in sorted(todo, key=lambda k: -(T[k]["slot_end"] - T[k]["slot_start"])):
            h = min(load, key=load.get)
            load[h] += T[n]["slot_end"] - T[n]["slot_start"]; bins[h].append(n)
        return {h: sorted(v) for h, v in bins.items() if v}

    def _worker(self, nums):
        r = self.f["render"]
        bg = self.f["picture"]["background"]
        lines = ["#!/usr/bin/env bash", "set -u", f'cd "$HOME/{self.rdir}" || exit 1', "mkdir -p xml/seg logs res", "echo $$ > logs/worker.pid", self.env(),
                 f'export E="$HOME/{r["engine"]}"',
                 'echo "CPU=$(grep -m1 "model name" /proc/cpuinfo | sed "s/^[^:]*: *//")" > res/host.txt',
                 'echo "CORES=$(nproc)" >> res/host.txt', 'echo "ENGINE_SHA256=$(sha256sum "$E" | cut -d" " -f1)" >> res/host.txt',
                 'echo "HOST=$(hostname)" >> res/host.txt']
        args = " ".join(q(a) for a in r["encode_args"])
        for n in nums:
            s = f"s{n:02d}"
            job = (f'rm -f xml/seg/{s}.mp4; "$E" validate xml/{s}.scene.xml > logs/{s}.validate 2>&1 && '
                   f'"$E" encode xml/{s}.scene.xml --output master {args} > logs/{s}.out 2> logs/{s}.err; echo $? > logs/{s}.rc; '
                   f'sha256sum xml/seg/{s}.mp4 > res/{s}.sha256 2>/dev/null; '
                   + self.remote_python(f"pnkit.pixelart.segment xml/seg/{s}.mp4 {n} shots/{s}.json res/{s} --fps {self.f['picture']['fps']}"
                                        + (f" --bg {q(bg)}" if bg else "")) + f" > logs/{s}.check 2>&1")
            lines.append(f'flock "$HOME/{r["lock"]}" bash -c {q(job)}; echo done > logs/{s}.done')
        return "\n".join(lines) + "\n"

    def _attach(self, h, ns):
        """True when a worker launched by an earlier run is still alive on h and was given exactly these documents (the
        stage was interrupted locally, the host kept working): poll it instead of launching a second one. A live worker
        with other documents is an error, not something to queue behind."""
        names = " ".join(f"xml/s{n:02d}.scene.xml shots/s{n:02d}.json" for n in ns)
        out = self.remote.run(h, f'cd "$HOME/{self.rdir}" 2>/dev/null || exit 0; pid=$(cat logs/worker.pid 2>/dev/null); '
                                 f'[ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && echo "ALIVE $pid" && sha256sum {names} 2>/dev/null; true')
        if not out.startswith("ALIVE"):
            return False
        have = {ln.split()[1]: ln.split()[0] for ln in out.splitlines()[1:] if len(ln.split()) == 2}
        for n in ns:
            if (have.get(f"xml/s{n:02d}.scene.xml") != sha256_file(self.p("xml", f"s{n:02d}.scene.xml"))
                    or have.get(f"shots/s{n:02d}.json") != sha256_file(self.p("picture", f"shots-{n:02d}.json"))):
                raise StageFailed(f"render: a worker ({out.split()[1]}) for other documents is still running on {h}; wait for it or stop it")
        return True

    def render(self):
        f, t0 = self.f, time.time()
        r = f["render"]
        nums = [s["n"] for s in self.scenes()]
        inputs = [self.p("xml", f"s{n:02d}.scene.xml") for n in nums] + [self.p("picture", f"shots-{n:02d}.json") for n in nums]
        cfg = {k: r[k] for k in ("hosts", "engine", "engine_sha256", "encode_args", "env")}
        if self.fresh("render", inputs, cfg):
            return "cached", self.last("render")
        rec_path = self.p("render.json")
        segs = read_json(rec_path) if os.path.exists(rec_path) else {}
        todo = [n for n in nums if self.force or segs.get(str(n), {}).get("key") != self._seg_key(n)
                or not os.path.exists(self.p("seg", f"s{n:02d}.mp4")) or sha256_file(self.p("seg", f"s{n:02d}.mp4")) != segs[str(n)]["sha256"]]
        os.makedirs(self.p("seg"), exist_ok=True); os.makedirs(self.p("checks"), exist_ok=True)
        plan = self._assign(todo)
        for h, ns in plan.items():
            if self._attach(h, ns):
                self.log(f"render: {h} already rendering {', '.join(f's{n:02d}' for n in ns)}; attached")
                continue
            self.put_lib(h)
            self.remote.run(h, f'mkdir -p "$HOME/{self.rdir}/xml/seg" "$HOME/{self.rdir}/shots" "$HOME/{self.rdir}/logs" "$HOME/{self.rdir}/res"'
                               f' && cd "$HOME/{self.rdir}" && rm -f ' + " ".join(f"logs/s{n:02d}.done" for n in ns))
            self.remote.put(h, [self.p("xml", f"s{n:02d}.scene.xml") for n in ns], f"{self.rdir}/xml/")
            stage_dir = self.p("shots-up"); os.makedirs(stage_dir, exist_ok=True)
            for n in ns:
                shutil.copyfile(self.p("picture", f"shots-{n:02d}.json"), os.path.join(stage_dir, f"s{n:02d}.json"))
            self.remote.put(h, [os.path.join(stage_dir, f"s{n:02d}.json") for n in ns], f"{self.rdir}/shots/")
            wk = self.p(f"worker-{h}.sh"); write_text(wk, self._worker(ns))
            self.remote.put(h, [wk], f"{self.rdir}/worker.sh")
            self.remote.run(h, f'cd "$HOME/{self.rdir}" && chmod +x worker.sh && (setsid nohup ./worker.sh > logs/worker.log 2>&1 < /dev/null &) ; echo started')
            self.log(f"render: {h} <- {', '.join(f's{n:02d}' for n in ns)}")
        deadline = time.time() + r["timeout_s"]
        pending = {h: set(ns) for h, ns in plan.items()}
        while any(pending.values()):
            for h in list(pending):
                if not pending[h]:
                    continue
                out = self.remote.run(h, f'cd "$HOME/{self.rdir}" && ls logs/ 2>/dev/null | grep "\\.done$" || true', timeout=120)
                got = {int(x[1:3]) for x in out.split() if x.startswith("s") and x.endswith(".done")}
                pending[h] -= got
            if not any(pending.values()):
                break
            if time.time() > deadline:
                raise StageFailed(f"render: timed out after {r['timeout_s']} s, waiting for {dict((h, sorted(v)) for h, v in pending.items() if v)}")
            time.sleep(r["poll_s"])
        cpus = {}
        for h, ns in plan.items():
            tmp = self.p(f"fetch-{h}")
            if os.path.isdir(tmp):
                shutil.rmtree(tmp)
            os.makedirs(tmp)
            self.remote.get(h, f"{self.rdir}/res", tmp)
            host = dict(ln.split("=", 1) for ln in read_text(os.path.join(tmp, "res", "host.txt")).splitlines() if "=" in ln)
            cpus[h] = host
            if r["engine_sha256"] and host.get("ENGINE_SHA256") != r["engine_sha256"]:
                raise StageFailed(f"render: the engine on {h} has sha256 {host.get('ENGINE_SHA256', '?')[:16]}, film.json says {r['engine_sha256'][:16]}")
            for n in ns:
                s = f"s{n:02d}"
                rc = self.remote.run(h, f'cat "$HOME/{self.rdir}/logs/{s}.rc" 2>/dev/null || echo missing').strip()
                if rc != "0":
                    err = self.remote.run(h, f'tail -c 400 "$HOME/{self.rdir}/logs/{s}.err" "$HOME/{self.rdir}/logs/{s}.validate" 2>/dev/null || true')
                    raise StageFailed(f"render {s} on {h}: exit {rc}: {err.strip()[-300:]}")
                self.remote.get(h, f"{self.rdir}/xml/seg/{s}.mp4", self.p("seg", f"{s}.mp4"))
                want = read_text(os.path.join(tmp, "res", f"{s}.sha256")).split()[0]
                got = sha256_file(self.p("seg", f"{s}.mp4"))
                if got != want:
                    raise StageFailed(f"render {s}: fetched sha256 {got[:12]} differs from the host's {want[:12]}")
                cd = self.p("checks", s)
                if os.path.isdir(cd):
                    shutil.rmtree(cd)
                if os.path.isdir(os.path.join(tmp, "res", s)):
                    shutil.copytree(os.path.join(tmp, "res", s), cd)
                chk = read_json(os.path.join(cd, "check.json")) if os.path.exists(os.path.join(cd, "check.json")) else None
                segs[str(n)] = {"scene": n, "host": h, "hostname": host.get("HOST"), "cpu": host.get("CPU"), "cores": host.get("CORES"),
                                "engine_sha256": host.get("ENGINE_SHA256"), "key": self._seg_key(n), "sha256": got,
                                "frames": chk["frames"] if chk else None, "findings": chk["findings"] if chk else ["no check"], "rendered": now()}
            shutil.rmtree(tmp)
        write_json(rec_path, segs, indent=1, sort_keys=True)
        write_text(self.p("SHA256SUMS"), "".join(f"{segs[str(n)]['sha256']}  seg/s{n:02d}.mp4\n" for n in nums))
        used = {(v["cpu"], v["cores"]) for v in segs.values()}
        warn = f"; WARNING hosts differ in CPU/cores {sorted(used)}: a rebuild on one host may not match byte for byte" if len(used) > 1 else ""
        flagged = {f"s{int(k):02d}": v["findings"] for k, v in segs.items() if v["findings"]}
        outs = [self.p("seg", f"s{n:02d}.mp4") for n in nums] + [rec_path, self.p("SHA256SUMS")]
        if flagged:
            self.L.save("render", {"stage": "render", "status": "fail", "note": f"segment checks flagged {flagged}"})
            raise StageFailed(f"segment checks: {flagged} (build/checks/sNN/check.json)")
        return "ran", self.done("render", inputs, cfg, outs, f"{len(todo)} of {len(nums)} segments rendered on {', '.join(plan) or '-'}; "
                                f"checks clean; CPU {sorted(used)}{warn}", summary={"cpus": cpus}, t0=t0)

    # ---------------------------------------------------------------- audio
    def audio(self):
        f, t0 = self.f, time.time()
        r, hub = f["render"], f["render"]["hub"]
        xd = self.p("xml")
        stems = read_json(os.path.join(xd, "stems.json"))
        docs = ["full-audio"] + [f"stem-{k}" for k in stems]
        inputs = [os.path.join(xd, f"{d}.scene.xml") for d in docs] + [os.path.join(xd, "audio")]
        cfg = {k: r[k] for k in ("hub", "engine", "engine_sha256", "env")}
        if self.fresh("audio", inputs, cfg):
            return "cached", self.last("audio")
        ra = f"{self.rdir}/audio"
        self.remote.run(hub, f'rm -rf "$HOME/{ra}" && mkdir -p "$HOME/{ra}/audio"')
        self.remote.put(hub, [os.path.join(xd, f"{d}.scene.xml") for d in docs], f"{ra}/")
        self.remote.put(hub, [os.path.join(xd, "audio", n) for n in sorted(os.listdir(os.path.join(xd, "audio")))], f"{ra}/audio/")
        job = (f'cd "$HOME/{ra}" && {self.env()} E="$HOME/{r["engine"]}"; '
               + "; ".join(f'"$E" encode stem-{s}.scene.xml --output stem --strict --no-upload --hw software > stem-{s}.log 2>&1 || exit 3'
                           for s in stems)
               + '; "$E" encode full-audio.scene.xml --output master --strict --no-upload --hw software > final.log 2>&1 || exit 4; '
               'sha256sum final.m4a ' + " ".join(f"{k}.wav" for k in stems))
        try:
            out = self.remote.run(hub, self.locked(job), timeout=r["timeout_s"])
        except RemoteError as e:
            logs = self.remote.run(hub, f'cd "$HOME/{ra}" && grep -h -m3 -E "error|invalid" *.log 2>/dev/null || true')
            raise StageFailed(f"audio render on {hub}: {e}; {logs.strip()[-300:]}")
        sums = {ln.split()[1]: ln.split()[0] for ln in out.splitlines() if len(ln.split()) == 2}
        self.remote.get(hub, f"{ra}/final.m4a", self.p("final.m4a"))
        if sha256_file(self.p("final.m4a")) != sums.get("final.m4a"):
            raise StageFailed("audio: fetched final.m4a differs from the host's")
        write_json(self.p("audio.json"), {"host": hub, "sha256": sums}, indent=1)
        return "ran", self.done("audio", inputs, cfg, [self.p("final.m4a"), self.p("audio.json")],
                                f"final.m4a and stems {', '.join(stems)} on {hub} (stems stay on the host)", t0=t0)

    # ---------------------------------------------------------------- join
    def film_versions(self):
        """[(N, path)] of OUT/<name>-vN.mp4, sorted"""
        name = self.f["out"]["name"]
        vs = []
        for n in os.listdir(self.out):
            if n.startswith(name + "-v") and n.endswith(".mp4") and n[len(name) + 2:-4].isdigit():
                vs.append((int(n[len(name) + 2:-4]), os.path.join(self.out, n)))
        return sorted(vs)

    def latest_film(self):
        vs = self.film_versions()
        return vs[-1][1] if vs else None

    def join(self):
        f, t0 = self.f, time.time()
        r, hub = f["render"], f["render"]["hub"]
        nums = [s["n"] for s in self.scenes()]
        inputs = [self.p("seg", f"s{n:02d}.mp4") for n in nums] + [self.p("final.m4a")]
        cfg = {"hub": hub}
        if self.fresh("join", inputs, cfg):
            return "cached", self.last("join")
        segs = read_json(self.p("render.json"))
        rj = f"{self.rdir}/join"
        self.remote.run(hub, f'rm -rf "$HOME/{rj}" && mkdir -p "$HOME/{rj}/seg"')
        self.remote.put(hub, [self.p("seg", f"s{n:02d}.mp4") for n in nums], f"{rj}/seg/")
        write_text(self.p("concat.txt"), "".join(f"file seg/s{n:02d}.mp4\n" for n in nums))
        self.remote.put(hub, [self.p("concat.txt")], f"{rj}/concat.txt")
        job = (f'cd "$HOME/{rj}" && sha256sum seg/*.mp4 && ffmpeg -v error -y -f concat -safe 0 -i concat.txt -i "$HOME/{self.rdir}/audio/final.m4a" '
               '-c copy -map 0:v -map 1:a -movflags +faststart film.mp4 && sha256sum film.mp4')
        out = self.remote.run(hub, self.locked(job), timeout=r["timeout_s"])
        sums = {ln.split()[1]: ln.split()[0] for ln in out.splitlines() if len(ln.split()) == 2}
        for n in nums:
            if sums.get(f"seg/s{n:02d}.mp4") != segs[str(n)]["sha256"]:
                raise StageFailed(f"join: segment s{n:02d} on {hub} is not the rendered one")
        tmp = self.p("film.mp4")
        self.remote.get(hub, f"{rj}/film.mp4", tmp)
        sha = sha256_file(tmp)
        if sha != sums.get("film.mp4"):
            raise StageFailed("join: fetched film differs from the host's")
        prev = self.latest_film()
        if prev and sha256_file(prev) == sha:
            dest, made = prev, "same bytes as"
        else:
            vs = self.film_versions()
            dest = os.path.join(self.out, f"{f['out']['name']}-v{vs[-1][0] + 1 if vs else 1}.mp4")
            try:
                with open(dest, "xb") as o, open(tmp, "rb") as i:          # write-once: a full render is never replaced
                    shutil.copyfileobj(i, o)
            except FileExistsError:
                raise files.WriteOnceError(dest)
            made = "new"
        os.remove(tmp)
        write_json(self.p("join.json"), {"film": os.path.relpath(dest, self.out), "sha256": sha, "hub": hub}, indent=1)
        return "ran", self.done("join", inputs, cfg, [dest, self.p("join.json")], f"{made} {os.path.relpath(dest, f.root)} (sha256 {sha[:16]})", t0=t0)

    # ---------------------------------------------------------------- gates
    def gates(self):
        f, t0 = self.f, time.time()
        r, hub, pic = f["render"], f["render"]["hub"], f["picture"]
        J = read_json(self.p("join.json"))
        film_path = os.path.join(self.out, J["film"])
        inputs = [film_path, self.p("render.json"), self.p("generate.json"), self.p("xml", "full-audio.scene.xml")]
        cfg = {"gates": f["gates"], "hub": hub}
        if self.fresh("gates", inputs, cfg):
            return "cached", self.last("gates")
        segs = read_json(self.p("render.json"))
        nums = [s["n"] for s in self.scenes()]
        gd = self.p("gates"); os.makedirs(gd, exist_ok=True)
        write_json(os.path.join(gd, "segments.json"), [{"scene": n, "path": f"../join/seg/s{n:02d}.mp4", "frames": segs[str(n)]["frames"]} for n in nums])
        rg = f"{self.rdir}/gates"
        self.put_lib(hub)
        self.remote.run(hub, f'rm -rf "$HOME/{rg}" && mkdir -p "$HOME/{rg}"')
        up = [os.path.join(gd, "segments.json"), self.p("picture", "all-shots.json"), self.p("src", "timings.json")]
        self.remote.put(hub, up, f"{rg}/")
        voice = f["voice"]["mode"] == "command"
        extra = (f' --full "$HOME/{self.rdir}/audio/full.wav" --voice "$HOME/{self.rdir}/audio/voice.wav" --timings timings.json' if voice else "")
        job = (f'cd "$HOME/{rg}" && ' + self.remote_python(f'pnkit.filmbuild.jobs film-gates "$HOME/{self.rdir}/join/film.mp4" all-shots.json segments.json '
                                                             f'film.json --expected {self.duration()} --fps {pic["fps"]}{extra}'))
        try:
            self.remote.run(hub, self.locked(job), timeout=r["timeout_s"])
        except RemoteError as e:
            raise StageFailed(f"gates job on {hub}: {e}")
        self.remote.get(hub, f"{rg}/film.json", os.path.join(gd, "film.json"))
        m = read_json(os.path.join(gd, "film.json"))
        gen = read_json(self.p("generate.json"))
        ml = asm.music_layer(read_bytes(self.p("xml", "full-audio.scene.xml")))
        capf = read_json(self.p("caption-gate.json"))["findings"] if f["captions"]["enabled"] else None
        rows = G.judge(m, f["gates"], segments={f"s{int(k):02d}": v["findings"] for k, v in segs.items()},
                       picture=gen["picture_findings"], music=ml, captions=capf, voice=voice)
        write_json(os.path.join(gd, "gates.json"), rows, indent=1, ensure_ascii=False)
        md = G.gates_md(f["film"], rows, os.path.relpath(film_path, f.root), J["sha256"],
                        [("film measures", "build/gates/film.json"), ("judged rows", "build/gates/gates.json"),
                         ("segment checks", "build/checks/sNN/check.json"), ("render records (host, CPU, cores, sha256)", "build/render.json"),
                         ("build-time picture findings and plan check", "build/generate.json")], now()[:10])
        write_text(os.path.join(self.out, "GATES.md"), md)
        bad = [x["gate"] for x in rows if not x["ok"]]
        note = f"{len(rows) - len(bad)}/{len(rows)} pass; I {m['loudness']['I']} LUFS, TP {m['loudness']['true_peak']} dBTP, black {len(m['black'])}, " \
               f"first-frame {len(m['first_frames'])}, joins {len(m['joins'])}" + (f"; FAIL: {', '.join(bad)}" if bad else "")
        if bad:
            self.L.save("gates", {"stage": "gates", "status": "fail", "note": note})
            raise StageFailed(note + " (out/GATES.md)")
        return "ran", self.done("gates", inputs, cfg, [os.path.join(gd, "film.json"), os.path.join(gd, "gates.json"), os.path.join(self.out, "GATES.md")], note, t0=t0)

    # ---------------------------------------------------------------- sheets
    def sheets(self):
        f, t0 = self.f, time.time()
        hub = f["render"]["hub"]
        J = read_json(self.p("join.json"))
        film_path = os.path.join(self.out, J["film"])
        inputs, cfg = [film_path], {"hub": hub}
        if self.fresh("sheets", inputs, cfg):
            return "cached", self.last("sheets")
        sd = os.path.join(self.out, "sheets", os.path.splitext(J["film"])[0])
        rs = f"{self.rdir}/sheets"
        self.put_lib(hub)
        job = (f'rm -rf "$HOME/{rs}" && mkdir -p "$HOME/{rs}" && cd "$HOME/{rs}" && '
               + self.remote_python(f'pnkit.filmbuild.jobs sheets "$HOME/{self.rdir}/join/film.mp4" out') + ' && tar cf sheets.tar -C out .')
        self.remote.run(hub, self.locked(job), timeout=f["render"]["timeout_s"])
        os.makedirs(sd, exist_ok=True)
        self.remote.get(hub, f"{rs}/sheets.tar", os.path.join(sd, "sheets.tar"))
        with tarfile.open(os.path.join(sd, "sheets.tar")) as t:
            t.extractall(sd, filter="data")
        os.remove(os.path.join(sd, "sheets.tar"))
        pngs = sorted(x for x in os.listdir(sd) if x.endswith(".png"))
        segs = read_json(self.p("render.json"))
        T = {s["n"]: s for s in self.timings()["scenes"]}
        flagged = [f"s{int(k):02d} {T[int(k)]['slot_start']}-{T[int(k)]['slot_end']} s" for k, v in segs.items() if v["findings"]]
        return "ran", self.done("sheets", inputs, cfg, [os.path.join(sd, x) for x in pngs],
                                f"{len(pngs)} sheets in {os.path.relpath(sd, f.root)}/ (to read: {', '.join(flagged) or 'whole film, nothing flagged'})", t0=t0)

    # ---------------------------------------------------------------- pack
    def pack(self):
        from . import pack as PK
        return PK.pack(self)


def run(build, stages, log=print):
    """run stages in order; stop at the first failure. -> rows [(stage, result, seconds, note)]"""
    rows = []
    for s in stages:
        t0 = time.time()
        try:
            status, note = getattr(build, s)()
        except (StageFailed, FilmError, RemoteError) as e:
            rows.append((s, "FAIL", round(time.time() - t0, 1), str(e)))
            break
        rows.append((s, status, round(time.time() - t0, 1), note))
    return rows


def table(rows):
    w = max(len(r[0]) for r in rows) if rows else 5
    out = [f"{'stage':<{w}}  {'result':<7}  {'s':>6}  note", f"{'-' * w}  -------  ------  ----"]
    for s, st, sec, note in rows:
        out.append(f"{s:<{w}}  {st:<7}  {sec:>6}  {note}")
    return "\n".join(out)
