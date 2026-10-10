#!/usr/bin/env python3
"""fake scene-render for the film_build tests: validate passes; encode writes, for the asked output, bytes derived from
the document (so a changed document gives a changed file and the same document the same file)."""
import hashlib, os, sys
import xml.etree.ElementTree as ET

cmd, doc = sys.argv[1], sys.argv[2]
root0 = ET.parse(doc).getroot()
mix0 = root0.find("audioMix")
if mix0 is not None and not mix0.findall("audioTrack"):                # as the engine: error[C35]
    print("error[C35]: audioMix needs at least one audioTrack.", file=sys.stderr); sys.exit(1)
if cmd == "validate":
    sys.exit(0)
if cmd == "encode":
    want = sys.argv[sys.argv.index("--output") + 1]
    data = open(doc, "rb").read()
    root = ET.fromstring(data)
    if os.environ.get("FAKE_ENGINE_FAIL") and os.path.basename(doc).startswith(os.environ["FAKE_ENGINE_FAIL"]):
        print("error: fake failure", file=sys.stderr); sys.exit(1)
    for o in root.findall("output"):
        if o.get("id") == want:
            out = os.path.join(os.path.dirname(os.path.abspath(doc)), o.get("path"))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "wb").write(b"FAKE" + hashlib.sha256(data + want.encode()).digest() * 8)
            sys.exit(0)
    sys.exit(f"no output {want}")
sys.exit(2)
