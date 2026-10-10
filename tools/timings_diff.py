#!/usr/bin/env python3
"""timings_diff.py — diff two word-timings files: which sentences and words moved by more than a threshold.

    python3 tools/timings_diff.py A.json B.json [--threshold 0.15] [--json]

Input format (simple, documented): a JSON list, one item per sentence, times in seconds on one clock:

    [{"sentence": "16.2", "text": "Um ex-presidente entra.", "words": [["Um", 10.0, 10.3], ["ex-presidente", 10.3, 11.0]]}]

Also accepted: the Lula film's timings-v2.json shape, {"scenes": [{"id", "n", "lines": [{"line", "caption", "words":
[[word, start], ...], "start", "end"}]}]}. It is adapted to the simple format: the sentence id is "<scene n>.<line>",
a word ends where the next one starts and the last word ends at the line's end (so a word's end moved there is the
next word's start moved: the file carries no word ends).

Sentences are matched by id, words by position inside a matched sentence with the same words. A sentence or word is
reported when its start or its end differs by more than the threshold (default 0.15 s). A sentence whose words differ
in number or text is reported as changed, without a word list. Exit status 1 when anything is reported, else 0 (like
diff); 2 when an input cannot be read."""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit.timings import THRESHOLD, load_sentences, diff   # noqa: E402  (the library holds the diff)


def render(r):
    lines = [f"threshold {r['threshold']} s: {len(r['sentences'])} sentences, {len(r['words'])} words moved"]
    for s in r["sentences"]:
        note = s.get("words_changed") or f"start {s['start_delta']:+.3f}, end {s['end_delta']:+.3f}"
        lines.append(f"  sentence {s['sentence']}: {note}  {s['text'][:60]!r}")
    for w in r["words"]:
        lines.append(f"    {w['sentence']}#{w['index']} {w['word']!r}: start {w['start_delta']:+.3f} ({w['start_a']:.3f} -> {w['start_b']:.3f}), "
                     f"end {w['end_delta']:+.3f} ({w['end_a']:.3f} -> {w['end_b']:.3f})")
    for k, label in (("only_a", "only in A"), ("only_b", "only in B")):
        if r[k]:
            lines.append(f"  {label}: {', '.join(r[k])}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--threshold", type=float, default=THRESHOLD, help="seconds (default 0.15)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        sa, sb = [load_sentences(json.load(open(p, encoding="utf-8"))) for p in (a.a, a.b)]
    except (OSError, ValueError, KeyError) as e:
        print(f"timings_diff: cannot read input: {e}", file=sys.stderr)
        return 2
    r = diff(sa, sb, a.threshold)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else render(r))
    return 1 if r["moved"] else 0


if __name__ == "__main__":
    sys.exit(main())
