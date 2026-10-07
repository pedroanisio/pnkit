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
import argparse, json, sys

THRESHOLD = 0.15


def load_sentences(data):
    """the simple format, from either shape; ValueError when it is neither"""
    if isinstance(data, dict) and isinstance(data.get("scenes"), list):
        out = []
        for sc in data["scenes"]:
            for ln in sc["lines"]:
                ws, end = ln["words"], ln["end"]
                words = [[w[0], w[1], ws[i + 1][1] if i + 1 < len(ws) else end] for i, w in enumerate(ws)]
                out.append({"sentence": f"{sc.get('n', sc.get('id'))}.{ln['line']}", "text": ln.get("caption", ""), "words": words})
        return out
    if isinstance(data, list):
        for item in data:
            if not (isinstance(item, dict) and "sentence" in item and isinstance(item.get("words"), list)):
                raise ValueError(f"not a sentence item (need 'sentence' and 'words'): {json.dumps(item, ensure_ascii=False)[:80]}")
            for w in item["words"]:
                if not (isinstance(w, (list, tuple)) and len(w) == 3):
                    raise ValueError(f"sentence {item['sentence']!r}: a word must be [word, start, end], got {w!r}")
        return data
    raise ValueError("unknown timings format: expected a list of sentences or an object with 'scenes'")


def _span(words):
    return (min(w[1] for w in words), max(w[2] for w in words)) if words else (0.0, 0.0)


def diff(a, b, threshold=THRESHOLD):
    """-> {"sentences": [...], "words": [...], "only_a": [ids], "only_b": [ids], "moved": bool} for two lists in the simple
    format. Deltas are B minus A, in seconds."""
    A, B = {s["sentence"]: s for s in a}, {s["sentence"]: s for s in b}
    sents, words = [], []
    for sid in A:
        if sid not in B:
            continue
        x, y = A[sid], B[sid]
        (xs, xe), (ys, ye) = _span(x["words"]), _span(y["words"])
        item = {"sentence": sid, "text": x.get("text", ""), "start_a": xs, "start_b": ys, "end_a": xe, "end_b": ye,
                "start_delta": round(ys - xs, 3), "end_delta": round(ye - xe, 3)}
        same = [w[0] for w in x["words"]] == [w[0] for w in y["words"]]
        if not same:
            item["words_changed"] = f"{len(x['words'])} -> {len(y['words'])} words" if len(x["words"]) != len(y["words"]) else "word text differs"
            sents.append(item)
            continue
        if abs(item["start_delta"]) > threshold + 1e-9 or abs(item["end_delta"]) > threshold + 1e-9:
            sents.append(item)
        for i, (p, q) in enumerate(zip(x["words"], y["words"])):
            ds, de = round(q[1] - p[1], 3), round(q[2] - p[2], 3)
            if abs(ds) > threshold + 1e-9 or abs(de) > threshold + 1e-9:
                words.append({"sentence": sid, "index": i, "word": p[0], "start_a": p[1], "start_b": q[1], "end_a": p[2], "end_b": q[2],
                              "start_delta": ds, "end_delta": de})
    only_a, only_b = [s for s in A if s not in B], [s for s in B if s not in A]
    return {"threshold": threshold, "sentences": sents, "words": words, "only_a": only_a, "only_b": only_b,
            "moved": bool(sents or words or only_a or only_b)}


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
