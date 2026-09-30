"""vo_probe.py — how does the narration engine read these lines? Kokoro synthesises each line, Whisper large-v3 hears it
back, and internal pauses over 0.25 s are listed. Use it to test a term before adding it to pnkit/data/vo_lexicon.json
(compare the bare written form with a respelling in one run).

    ~/.venvs/voice/bin/python tools/vo_probe.py --lang en "Trained with RLHF." "Trained with R L H F."
    ~/.venvs/voice/bin/python tools/vo_probe.py --lang pt-br --voice pf_dora lines.txt      # one line per row

Needs kokoro-onnx and faster-whisper (the voice venv). The model and voices come from KOKORO_MODEL and KOKORO_VOICES,
else ~/.cache/kokoro. Default voices are the channel's (guide §5): en af_heart, pt-br pf_dora. Runs Whisper on the GPU
when CUDA loads, else on the CPU.
"""
import argparse, ctypes, glob, os, sys, tempfile

VOICE = {"en": "af_heart", "pt": "pf_dora"}
KOKORO_LANG = {"en": "en-us", "pt": "pt-br"}


def _preload_cuda():
    """faster-whisper dlopens libcublas by name; the pip wheels put it where the loader does not look"""
    try:
        import nvidia
    except ImportError:
        return
    for base in nvidia.__path__:
        for so in sorted(glob.glob(os.path.join(base, "*", "lib", "lib*.so.*"))):
            if any(k in so for k in ("cublas", "cudnn", "cudart")):
                try:
                    ctypes.CDLL(so, mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("lines", nargs="+", help="lines to read, or a text file with one line per row")
    ap.add_argument("--lang", default="en"); ap.add_argument("--voice"); ap.add_argument("--speed", type=float, default=1.0)
    a = ap.parse_args()
    base = a.lang.lower().split("-")[0]
    voice = a.voice or VOICE.get(base, "af_heart")
    lines = []
    for x in a.lines:
        lines += [l.strip() for l in open(x, encoding="utf-8") if l.strip() and not l.startswith("#")] if os.path.isfile(x) else [x]
    import numpy as np, soundfile as sf
    from kokoro_onnx import Kokoro
    from faster_whisper import WhisperModel
    k = os.path.expanduser("~/.cache/kokoro")
    tts = Kokoro(os.environ.get("KOKORO_MODEL", os.path.join(k, "kokoro-v1.0.onnx")), os.environ.get("KOKORO_VOICES", os.path.join(k, "voices-v1.0.bin")))
    _preload_cuda()
    try:
        asr = WhisperModel("large-v3", device="cuda", compute_type="float16")
    except Exception:
        asr = WhisperModel("large-v3", device="cpu", compute_type="int8")
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    for text in lines:
        y, sr = tts.create(text, voice=voice, speed=a.speed, lang=KOKORO_LANG.get(base, a.lang))
        y = np.asarray(y, np.float32)
        idx = np.where(np.abs(y) > 0.02 * np.max(np.abs(y)))[0]
        gaps = [round(g / sr, 2) for g in np.diff(idx) if g > 0.25 * sr] if len(idx) else []
        sf.write(tmp, y, sr)
        segs, _ = asr.transcribe(tmp, language=base, beam_size=5)
        heard = " ".join(s.text for s in segs).strip()
        print(f"{text}\n    heard: {heard}\n    {len(y) / sr:.2f} s" + (f", pauses {gaps} s" if gaps else ""), flush=True)
    os.unlink(tmp)


if __name__ == "__main__":
    sys.exit(main())
