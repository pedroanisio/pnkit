#!/usr/bin/env python3
"""instance_clock.py — flag an <instance> with no `start` whose symbol picks its frame from the clock.

    python3 tools/instance_clock.py SCENE [SCENE ...]      exit status 1 when a finding is printed

The scene format gives an instance its own clock: local time = (t - start) * speed + clipIn. With no `start` the
clock is the film's absolute time, so a symbol whose `condition` reads `time` (a walk or crowd cycle choosing
frame floor(time * rate) % n) shows an arbitrary frame at the first frame of a shot, a pop whenever the shot's
start times the rate is not a whole number. Lula 3.0.0 found this only by rendering and comparing frame 1 with
frame 2 (scenes 14, 15, 23, 26, 29). The pattern is plain in the XML, so it is found here without a render.

Independent of pnkit (standard library only). Namespaces are ignored. Imported by tools/gate.py.
"""
import re
import sys
import xml.etree.ElementTree as ET

_TIME = re.compile(r"\btime\b")


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def lint(path):
    """one finding string per offending instance in the scene at `path`; [] when clean"""
    root = ET.parse(path).getroot()
    reads_time = {}
    for sym in root.iter():
        if _local(sym.tag) == "symbol" and sym.get("id") is not None:
            reads_time[sym.get("id")] = any(_TIME.search(el.get("condition") or "") for el in sym.iter())
    return [f"{path}: instance {ins.get('id')} (symbol {ins.get('symbol')}) has no start but its symbol reads the clock "
            f"in a condition; its first frame is on the absolute clock"
            for ins in root.iter() if _local(ins.tag) == "instance" and ins.get("start") is None
            and reads_time.get(ins.get("symbol"))]


def main(argv=None):
    findings = [f for p in (sys.argv[1:] if argv is None else argv) for f in lint(p)]
    print("\n".join(findings) or "clean")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
