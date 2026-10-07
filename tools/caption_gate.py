#!/usr/bin/env python3
"""caption_gate.py — the caption text gate: the cues must carry the approved written text, nothing else.

    python3 tools/caption_gate.py CUES --approved TEXT [--lang pt-br] [--json]

CUES is a WebVTT file (.vtt), a scene document (.xml: every <cue text="...">, in document order) or a JSON file (a list
of strings or of {"text": ...}, or {"cues": [...]}). TEXT is the approved written text, a plain UTF-8 file; for a whole
film, all of its sentences in order. The gate (pnkit.captions.check_text) reports:

  text          the cues' joined text differs from the approved text (only whitespace and line breaks are normalised):
                a clause that was cut and is still shown, a stale copy of the text, a respelled word;
  spelled-out   (pt only) a cue spells out "vírgula", "por cento" or a number the approved text writes in digits.

Exit status 0 when there are no findings, 1 when there are, 2 when an input cannot be read."""
import argparse, json, os, re, sys, xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit import captions

_TIME = re.compile(r"\d[\d:.,]*\s*-->\s*\d[\d:.,]*")


def read_vtt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.replace("\r\n", "\n").strip()):
        lines = block.split("\n")
        for i, ln in enumerate(lines):
            if _TIME.match(ln.strip()):
                cues.append("\n".join(lines[i + 1:]))
                break
    return cues


def read_cues(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    ext = os.path.splitext(path)[1].lower()
    if ext == ".vtt":
        return read_vtt(raw)
    if ext == ".json":
        d = json.loads(raw)
        return d["cues"] if isinstance(d, dict) else d
    if ext == ".xml":
        return [el.attrib["text"] for el in ET.fromstring(raw).iter() if el.tag.split("}")[-1] == "cue" and "text" in el.attrib]
    raise ValueError(f"unknown cue file type {ext!r} (use .vtt, .xml or .json)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cues"); ap.add_argument("--approved", required=True); ap.add_argument("--lang", default="pt-br")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        cues = read_cues(a.cues)
        with open(a.approved, encoding="utf-8") as fh:
            approved = fh.read()
    except (OSError, ValueError, KeyError, ET.ParseError) as e:
        print(f"caption_gate: cannot read input: {e}", file=sys.stderr)
        return 2
    findings = captions.check_text(cues, approved, a.lang)
    if a.json:
        print(json.dumps([{"kind": f.kind, "cue": f.cue, "detail": f.detail} for f in findings], ensure_ascii=False, indent=1))
    else:
        for f in findings:
            print(f)
        print(f"caption text gate: {'FAIL' if findings else 'pass'} ({len(cues)} cues, {len(findings)} findings)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
