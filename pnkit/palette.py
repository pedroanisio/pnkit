"""pnkit.palette — the brand kit's colour tokens as hex strings, for XML written outside the kit's styles.

The source of truth is the kit (palsnotes-brand.xml, <styles><token>). These constants mirror it so helpers can
default to brand colours; `check(kit_path)` compares them with a kit file and `tokens(kit_path)` reads any kit.
In the kit's own components prefer var(--pn-...) references, which follow the kit when it changes.
"""
import re

__all__ = ["INK", "RAISED", "CREAM", "MUTED", "ORANGE", "RULE", "COOL", "TOKENS", "tokens", "check"]

INK = "#16181D"        # pn-ink: the field
RAISED = "#22252C"     # pn-ink-raised: panels (orange is never type on it: 4.27:1)
CREAM = "#F2EBDD"      # pn-cream: type and line work
MUTED = "#B8B1A4"      # pn-cream-muted: secondary type (8.34:1 on ink)
ORANGE = "#E8581C"     # pn-orange: the accent (4.94:1 on ink)
RULE = "#3A3E47"       # pn-rule: grid lines, axes, dividers; never type (1.66:1)
COOL = "#5FA8D3"       # pn-data-3: the third data series

TOKENS = {"INK": "pn-ink", "RAISED": "pn-ink-raised", "CREAM": "pn-cream", "MUTED": "pn-cream-muted",
          "ORANGE": "pn-orange", "RULE": "pn-rule", "COOL": "pn-data-3"}


def tokens(kit_path):
    """{token name: value} from a kit file, with var(--x) references resolved"""
    src = open(kit_path, encoding="utf-8").read()
    raw = dict(re.findall(r'<token name="([^"]+)" value="([^"]+)"', src))

    def res(v, depth=0):
        m = re.fullmatch(r"var\(--([\w-]+)\)", v)
        return res(raw[m.group(1)], depth + 1) if m and depth < 8 and m.group(1) in raw else v
    return {k: res(v) for k, v in raw.items()}


def check(kit_path):
    """[(constant, ours, the kit's)] for every constant that differs from the kit (empty when they agree)"""
    t = tokens(kit_path)
    here = globals()
    return [(k, here[k], t.get(name)) for k, name in TOKENS.items() if (t.get(name) or "").upper() != here[k].upper()]
