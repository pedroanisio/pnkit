"""pnkit.pixelart.plan — the picture plan check (from Lula work/art3/v3/check_plan.py), as functions on data.

The plan is a Markdown file (SHOTS-<version>.md) with one table row per shot, in the Lula format:

    | `s01a_rua`<br>0.00-3.00 s ... | set | cast | props<br>SIGN “PADARIA” @ shop, x 120-170, y 40-48 |
      “São Paulo · 1958” TL over sky; reserved x 6-110, y 6-27 (1 line); 0.50-2.50 s | action |

Built shots are the `shots_json()` records of a pnkit.pixelart.ctx.Ctx build. Timings are {"scenes": [{"n",
"slot_start", "slot_end", "plate_read_s" (optional)}]}.

  check_plan_only(plan)            plates stacked in one slot (windows overlap by more than a frame)
  check_plan_slots(plan, timings)  every scene's shots tile its slot from the timings, no gap or overlap
  check_built(built, plan, timings) -> (errors, warnings): shots as planned (names, times +-0.01 s), signs (rect +-1),
                                   plates (slot, window +-0.06 s, lines, reserved rect), rows (plates and signs <= 146,
                                   soles <= 145), plate over sign, read time (0.3 s per token; scene sum >= plate_read_s)
"""
import re
import unicodedata

FRAME = 1 / 24
ROW_LIMIT, SOLE_LIMIT = 146, 145


def norm(t):
    return unicodedata.normalize('NFC', t).casefold().replace(' / ', ' ').strip()


def parse_plan(text):
    """{shot name: {name, scene, start, end, signs [{text, rect}], plates [{text, slot, rect, lines, window}]}}"""
    shots = {}
    for ln in text.splitlines():
        m = re.match(r'^\| `(s\d\d[a-z]\d?_[a-z0-9_]+)`<br>([\d.]+)-([\d.]+) s', ln)
        if not m:
            continue
        cols = [c.replace('\\|', '|') for c in re.split(r'(?<!\\)\|', ln)]     # an escaped \| inside a cell is text
        props, plates = cols[4], cols[5]
        signs = [dict(text=t, rect=[int(a), int(b), int(c), int(d)])
                 for t, a, c, b, d in re.findall(r'SIGN “([^”]+)” @[^;]*?x (\d+)-(\d+), y (\d+)-(\d+)', props)]
        pl = [dict(text=t, slot=sl, rect=[int(a), int(b), int(c), int(d)], lines=int(n), window=[float(w0), float(w1)])
              for t, sl, a, c, b, d, n, w0, w1 in
              re.findall(r'“([^”]+)” (TL|TR)[^“”]*?; reserved x (\d+)-(\d+), y (\d+)-(\d+) \((\d+) lines?\); ([\d.]+)-([\d.]+) s', plates)]
        shots[m.group(1)] = dict(name=m.group(1), scene=int(m.group(1)[1:3]), start=float(m.group(2)), end=float(m.group(3)),
                                 signs=signs, plates=pl)
    return shots


def _overlap(r1, r2):
    return r1[0] < r2[2] and r2[0] < r1[2] and r1[1] < r2[3] and r2[1] < r1[3]


def stack_errors(items, label):
    """items: one dict per distinct plate of a scene (text, slot, rect, start, end); plates stacked in one slot"""
    out = []
    for i, x in enumerate(items):
        for y in items[i + 1:]:
            if x['slot'] != y['slot']:
                continue
            ov = min(x['end'], y['end']) - max(x['start'], y['start'])
            if ov <= FRAME + 1e-6:
                continue
            if x['slot'] == 'box' and not _overlap(x['rect'], y['rect']):
                continue
            a, b = sorted((x, y), key=lambda q: q['start'])
            out.append(f'{label}: plates overlap in slot {x["slot"]}: {a["text"]!r} [{a["start"]:.2f}, {a["end"]:.2f}) and '
                       f'{b["text"]!r} [{b["start"]:.2f}, {b["end"]:.2f}) share {ov:.2f} s'
                       + (f' (shots {a["shots"]} / {b["shots"]})' if 'shots' in a else ''))
    return out


def plan_plates(plan, sc):
    """distinct plates of scene sc in the plan (a carried-over plate is listed in several rows with one window)"""
    seen = {}
    for p in sorted((p for p in plan.values() if p['scene'] == sc), key=lambda p: p['start']):
        for q in p['plates']:
            k = (norm(q['text']), q['window'][0], q['window'][1])
            if k in seen:
                seen[k]['shots'].append(p['name'])
            else:
                seen[k] = dict(text=q['text'], slot=q['slot'], rect=q['rect'], start=q['window'][0], end=q['window'][1], shots=[p['name']])
    return list(seen.values())


def check_plan_only(plan, scenes=None):
    scs = sorted({p['scene'] for p in plan.values()}) if scenes is None else list(scenes)
    return [e for sc in scs for e in stack_errors(plan_plates(plan, sc), f'plan scene {sc:02d}')]


def check_plan_slots(plan, timings):
    """each scene's planned shots start at its slot_start, end at its slot_end and leave no gap or overlap"""
    err = []
    tim = {s['n']: s for s in timings['scenes']}
    for sc in sorted({p['scene'] for p in plan.values()}):
        ps = sorted((p for p in plan.values() if p['scene'] == sc), key=lambda p: p['start'])
        if sc not in tim:
            err.append(f'scene {sc:02d}: in the plan, not in the timings'); continue
        s0, s1 = tim[sc]['slot_start'], tim[sc]['slot_end']
        if abs(ps[0]['start'] - s0) > .01 or abs(ps[-1]['end'] - s1) > .01:
            err.append(f'scene {sc:02d}: plan spans {ps[0]["start"]}-{ps[-1]["end"]}, slot is {s0}-{s1}')
        for x, y in zip(ps, ps[1:]):
            if abs(x['end'] - y['start']) > .01:
                err.append(f'scene {sc:02d}: plan gap or overlap between {x["name"]} and {y["name"]}')
    for n in sorted(set(tim) - {p['scene'] for p in plan.values()}):
        err.append(f'scene {n:02d}: in the timings, no shot in the plan')
    return err


def check_built(built, plan, timings, scenes=None):
    """(errors, warnings) of built shots (Ctx.shots_json records) against the plan and the timings"""
    err, warn = [], []
    tim = {s['n']: s for s in timings['scenes']}
    scenes = sorted({b['scene'] for b in built}) if scenes is None else list(scenes)
    for sc in scenes:
        bs = sorted((b for b in built if b['scene'] == sc), key=lambda b: b['start'])
        ps = [p for p in plan.values() if p['scene'] == sc]
        if not bs:
            err.append(f'scene {sc:02d}: no built shots'); continue
        if {b['name'] for b in bs} != {p['name'] for p in ps}:
            err.append(f'scene {sc:02d}: shots differ: only built {sorted({b["name"] for b in bs} - {p["name"] for p in ps})}, '
                       f'only plan {sorted({p["name"] for p in ps} - {b["name"] for b in bs})}')
        if sc in tim:
            s0, s1 = tim[sc]['slot_start'], tim[sc]['slot_end']
            if abs(bs[0]['start'] - s0) > .01 or abs(bs[-1]['end'] - s1) > .01:
                err.append(f'scene {sc:02d}: spans {bs[0]["start"]}-{bs[-1]["end"]}, slot is {s0}-{s1}')
        else:
            err.append(f'scene {sc:02d}: not in the timings')
        for x, y in zip(bs, bs[1:]):
            if abs(x['end'] - y['start']) > 1e-6:
                err.append(f'scene {sc:02d}: gap or overlap between {x["name"]} and {y["name"]}')
        for b in bs:
            p = plan.get(b['name'])
            if p is None:
                continue
            if abs(b['start'] - p['start']) > .01 or abs(b['end'] - p['end']) > .01:
                err.append(f'{b["name"]}: time {b["start"]:.3f}-{b["end"]:.3f}, plan {p["start"]}-{p["end"]}')
            bsg = {norm(s['text']): s for s in b['signs']}
            for s in p['signs']:
                g = bsg.get(norm(s['text']))
                if g is None:
                    err.append(f'{b["name"]}: sign {s["text"]!r} missing'); continue
                if any(abs(u - v) > 1 for u, v in zip(g['rect'], s['rect'])):
                    err.append(f'{b["name"]}: sign {s["text"]!r} rect {g["rect"]}, plan {s["rect"]}')
            for t in bsg:
                if t not in {norm(s['text']) for s in p['signs']}:
                    warn.append(f'{b["name"]}: sign {t!r} is not in the plan for this shot')
            for pp in p['plates']:
                found = [q for o in bs for q in o['plates'] if norm(q['text']) == norm(pp['text']) and q['start'] < pp['window'][1] and pp['window'][0] < q['end']]
                if not found:
                    err.append(f'{b["name"]}: plate {pp["text"]!r} missing'); continue
                if pp['window'][0] >= b['start'] - 1e-6 and pp['window'][0] < b['end'] - 1e-6:       # judged where it starts
                    w0 = min(q['start'] for q in found); w1 = max(q['end'] for q in found)
                    nxt = [o for o in ps if o['start'] >= b['end'] - 1e-6]
                    last = min(nxt, key=lambda o: o['start'])['end'] if nxt else b['end']    # a plate may carry over one cut
                    want1 = min(pp['window'][1], last)
                    if want1 < pp['window'][1] - 1e-6:
                        warn.append(f'{b["name"]}: plan window of plate {pp["text"]!r} ends {pp["window"][1]}, after the shot that follows its first shot ({last:.2f}); clipped')
                    if abs(w0 - pp['window'][0]) > .06 or abs(w1 - want1) > .06:
                        err.append(f'{b["name"]}: plate {pp["text"]!r} window {w0:.2f}-{w1:.2f}, plan {pp["window"]}')
                    q = found[0]
                    if q['slot'] != pp['slot']:
                        err.append(f'{b["name"]}: plate {pp["text"]!r} slot {q["slot"]}, plan {pp["slot"]}')
                    if q.get('lines') != pp['lines']:
                        err.append(f'{b["name"]}: plate {pp["text"]!r} has {q.get("lines")} lines, plan {pp["lines"]}')
                    r_, pr = q['rect'], pp['rect']
                    if abs(r_[1] - pr[1]) > 1 or r_[3] - 1 > pr[3] + 1:
                        err.append(f'{b["name"]}: plate {pp["text"]!r} rect {r_}, plan reserved {pr}')
                    if pp['slot'] == 'TL' and r_[2] > pr[2] + 1 or pp['slot'] == 'TR' and r_[0] < pr[0] - 1:
                        warn.append(f'{b["name"]}: plate {pp["text"]!r} is wider than the plan\'s reserved x {pr[0]}-{pr[2]} (card {r_[0]}-{r_[2]})')
        merged = {}
        pl = {}
        for b in bs:
            for q in b['plates']:
                k = norm(q['text']); w = merged.setdefault(k, [q['start'], q['end'], q['text']])
                w[0] = min(w[0], q['start']); w[1] = max(w[1], q['end'])
                if q['rect'][3] - 1 > ROW_LIMIT:
                    err.append(f'{b["name"]}: plate {q["text"]!r} ends at row {q["rect"][3] - 1}')
                k2 = (k, tuple(q.get('full', ())) or None)
                d = pl.setdefault(k2, dict(text=q['text'], slot=q['slot'], rect=q['rect'], start=q['start'], end=q['end'], shots=[]))
                d['start'] = min(d['start'], q['start']); d['end'] = max(d['end'], q['end']); d['shots'].append(b['name'])
        err += stack_errors(list(pl.values()), f'scene {sc:02d}')
        wsum = 0.0
        for w0, w1, t in merged.values():
            tok = len(t.replace(' / ', ' ').split())
            wsum += w1 - w0
            if w1 - w0 + 1e-6 < .3 * tok:
                err.append(f'scene {sc:02d}: plate {t!r} window {w1 - w0:.2f} s < 0.3 s x {tok} tokens')
        need = tim.get(sc, {}).get('plate_read_s', 0) or 0
        if wsum + 1e-6 < need:
            err.append(f'scene {sc:02d}: plate windows sum {wsum:.2f} s < plate_read_s {need}')
        for b in bs:
            for s in b['signs']:
                if s['rect'][3] - 1 > ROW_LIMIT:
                    err.append(f'{b["name"]}: sign {s["text"]!r} below row {ROW_LIMIT}')
            for f in b['figures']:
                if f['rect'][3] - 1 > SOLE_LIMIT:
                    err.append(f'{b["name"]}: {f["kind"]} soles at row {f["rect"][3] - 1}')
            for q in b['plates']:
                for o in bs:
                    if o['start'] < q['end'] and q['start'] < o['end']:
                        for s in o['signs']:
                            if _overlap(q['rect'], s['rect']):
                                err.append(f'{b["name"]}: plate {q["text"]!r} overlaps sign {s["text"]!r} of {o["name"]}')
    return err, warn
