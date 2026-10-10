"""pnkit.timings — the word-timings file of a film: load either shape and diff two versions (moved sentences and
words). The core of tools/timings_diff.py, moved here so film_build can call it.

Simple format: [{"sentence": "16.2", "text": "...", "words": [["Um", 10.0, 10.3], ...]}]; the Lula timings-v2.json shape
{"scenes": [{"n", "lines": [{"line", "caption", "words": [[word, start], ...], "end"}]}]} is adapted (a word ends where
the next starts, the last at the line's end)."""
import json

THRESHOLD = 0.15


def load_sentences(data):
    """the simple format, from either shape; ValueError when it is neither"""
    if isinstance(data, dict) and isinstance(data.get("scenes"), list):
        out = []
        for sc in data["scenes"]:
            for ln in sc.get("lines", []):
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


