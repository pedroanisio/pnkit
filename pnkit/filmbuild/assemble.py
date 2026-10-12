"""pnkit.filmbuild.assemble — the documents the engine renders, from the picture build and the timings.

  segment_xml   one video-only document per scene: the scene's composition (and symbols) from its scene_NN.xml, the
                caption pages of its sentences, an output that renders only the scene's slot [slot_start, slot_end).
                Inner windows that start with their shot open 0.1 ms early (Lula assemble_v3: a segment rendered from
                an offset can otherwise drop a plate or figure for its first frame).
  audio_xml     the full-film audio document: voice tracks (role voiceover), one wordless music layer (role music,
                ducked under the voices), effects, linear master normalisation; output m4a.
  stems_xml     the same mix without normalisation, as full / voice / music / sfx WAVs for the voice-margin gate.
  caption_pages pixel caption pages in the band (rows 147-179) from timed cues: at most two lines, <= 288 columns.
"""
from .. import sdk
from ..sdk import S

BAND_TOP, LINE_ROWS_2, LINE_ROW_1, MAXW = 147, (152, 162), 157, 288


def _fmt(v):
    if isinstance(v, bool):
        return str(v).lower()
    if isinstance(v, float):
        return repr(round(v, 6))
    return str(v)


def E(p, tag, **kw):
    """a new <tag> under `p` (an SDK element) with the attributes given (None skipped); the SDK refuses a misplaced
    element or a bad value here"""
    el = sdk.new(p, tag)
    for k, v in kw.items():
        if v is not None:
            sdk.set_exact(el, k, v, _fmt)
    p.add(el)
    return el


def _tostring(root):
    sdk.indent(root, " ")
    return S.to_bytes(root)


def _read(doc):
    return S.read(doc.encode("utf-8") if isinstance(doc, str) else doc)


def _early_windows(comp):
    def walk(g):
        for e in g.find_all("group"):
            if e.start is not None:
                st = float(e.start)
                if gs < st <= gs + 0.0151:
                    st = gs
                e.start = round(st - 0.0001, 6)
            walk(e)
    for g in comp.find_all("group"):
        if not g.name or g.start is None:
            continue
        gs = float(g.start)
        walk(g)


def caption_pages(cues, width, unit=6):
    """cue (words, start, end) list -> [(lines, start, end)] with lines laid out by pnkit.captions.two_lines; raises
    ValueError when a line is wider than the band (288 logical columns)"""
    from .. import captions
    from ..pixelart.ctx import text_width
    out = []
    for c, a, b in cues:
        text = " ".join(w[0] for w in c)
        lines = [ln.upper() for ln in captions.two_lines(text, width)]
        for ln in lines:
            if text_width(ln) > MAXW:
                raise ValueError(f"caption line {ln!r} is {text_width(ln)} columns wide, the band holds {MAXW}")
        out.append((lines, a, b))
    return out


def _caption_groups(comp, pages, unit, scene_id):
    from ..pixelart.ctx import Geometry, r, lettering, W, H
    k = {"n": 0}

    def gid(kind):
        k["n"] += 1
        return f"cap_{scene_id}_{kind}{k['n']}"

    def draw(q, x, y, **attrs):
        g = E(comp, "group", id=gid("g"), x=round(x) * unit, y=round(y) * unit, **attrs)
        for col, path in q.paths(unit).items():
            E(g, "shape", id=gid("p"), shape="path", width=W * unit, height=H * unit, fill=col, path=path)
        return g
    if not pages:
        return
    a0, b0 = min(p[1] for p in pages), max(p[2] for p in pages)
    band = Geometry(); r(band, 0, BAND_TOP, W, H - BAND_TOP, "black")
    draw(band, 0, 0, start=a0, end=b0)
    for lines, a, b in pages:
        rows = LINE_ROWS_2 if len(lines) == 2 else (LINE_ROW_1,)
        for ln, y in zip(lines, rows):
            q, w = lettering(ln, "ivory")
            draw(q, round(160 - w / 2), y, start=a, end=b)


def segment_xml(scene_xml, slot, duration, out_path, title="", pages=None, unit=6):
    """bytes of the video-only document of one scene. slot: the scene's timings record (n, id, slot_start, slot_end)."""
    src = _read(scene_xml)
    root = S.Scene(version=src.version or "1.1")
    proj = src.find("project").copy()
    sdk.set_exact(proj, "duration", float(duration), _fmt)
    root.add(proj)
    meta = E(root, "metadata")
    E(meta, "meta", name="title", value=f"{title} {slot.get('id', '')}".strip())
    E(root, "output", id="master", path=out_path, codec="h264", crf=15, preset="fast", audio=False, faststart=False,
      start=float(slot["slot_start"]), end=float(slot["slot_end"]))
    sy = src.find("symbols")
    if sy is not None:
        root.add(sy.copy())
    comp = src.find("composition").copy()
    root.add(comp)
    _early_windows(comp)
    if pages:
        _caption_groups(comp, pages, unit, slot.get("id", f"s{slot['n']:02d}"))
    return _tostring(root)


def audio_xml(project, duration, assets, voices, music, sfx, mix, out_path="final.m4a", stem=None):
    """bytes of the full-film audio document (or of one stem when stem is 'full', 'voice', 'music' or 'sfx').
    project: {width, height, fps}; assets: {id: (src, sha256)}; voices: [(asset id, start)]; music, sfx: asset ids or
    None; mix: film.json audio settings."""
    root = S.Scene(version="1.1")
    E(root, "project", width=project["width"], height=project["height"], fps=project["fps"], duration=float(duration),
      seed=1, background="#000000", quality="final")
    if stem is None:
        E(root, "output", id="master", path=out_path, codec="audio-only", container="m4a", audioCodec="aac", audioBitrate=192000)
    else:
        E(root, "output", id="stem", path=f"{stem}.wav", codec="audio-only", container="wav")
    A = E(root, "assets")
    for aid in sorted(assets):
        src, sha = assets[aid]
        E(A, "audio", id=aid, src=src, sha256=sha)
    C = E(root, "composition")
    E(C, "group", id="audio_only_placeholder", x=0, y=0)
    m = E(root, "audioMix", sampleRate=48000, channels=2)
    ids = []
    keep = {"full": ("voiceover", "music", "effects"), "voice": ("voiceover",), "music": ("music",), "sfx": ("effects",)}.get(stem)
    for k, (aid, start) in enumerate(voices):
        tid = f"voice_{k + 1:02d}"
        if keep is None or "voiceover" in keep:
            E(m, "audioTrack", id=tid, asset=aid, start=round(float(start), 3), role="voiceover", fadeIn=.006, fadeOut=.015)
        elif stem == "music":                                         # silent, but the music still ducks under it
            E(m, "audioTrack", id=tid, asset=aid, start=round(float(start), 3), role="voiceover", gain=-120)
        else:
            continue
        ids.append(tid)
    duck = dict(duckUnder=" ".join(ids), duckAmount=mix["music_duck"], duckAttack=mix["duck_attack"], duckRelease=mix["duck_release"]) if ids else {}
    if music and (keep is None or "music" in keep):
        E(m, "audioTrack", id="music", asset=music, start=0, role="music", gain=mix["music_gain"], fadeIn=.1, fadeOut=1.5, **duck)
    if sfx and (keep is None or "effects" in keep):
        E(m, "audioTrack", id="effects", asset=sfx, start=0, role="effects", gain=mix["sfx_gain"], fadeIn=.05, fadeOut=.5)
    if stem is None:
        E(m, "master", normalize="integrated", loudness=mix["normalize"], truePeak=mix["true_peak"], limiter=True)
    else:
        E(m, "master", normalize="none", limiter=False)
    return _tostring(root)


def music_layer(audio_doc):
    """S2 §2.1 'check the role, not just the file': the ids of role=music tracks with an asset in an audio document"""
    mix = _read(audio_doc).find("audioMix")
    return [t.id for t in (mix.find_all("audioTrack") if mix is not None else []) if t.role == "music" and t.asset]
