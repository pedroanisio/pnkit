"""brand (prologue, palette against the kit, components) and shorts (spans, segments, overlay, build)."""
import os, re, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pnkit
from pnkit import brand, palette, shorts

KIT = os.environ.get("PNKIT_KIT") or os.path.expanduser("~/videos/docs/palsnotes-brand.xml")


@unittest.skipUnless(os.path.exists(KIT), f"no brand kit at {KIT} (set PNKIT_KIT)")
class Kit(unittest.TestCase):
    def test_palette_matches_the_kit(self):
        self.assertEqual(palette.check(KIT), [])

    def test_prologue_sets_defaults_only(self):
        p = brand.prologue(KIT, {"pn-title": "A & B", "pn-kicker": "SCIENCE"})
        self.assertIn('<param id="pn-title" type="string" default="A &amp; B"', p["parameters"])
        self.assertIn('default="SCIENCE"', p["parameters"])
        for k in ("styles", "layouts", "safeAreas", "symbols"):
            self.assertTrue(p[k].lstrip().startswith(f"<{k}") and p[k].endswith(f"</{k}>"), k)
        self.assertTrue(p["font"].startswith('<font id="pn-archivo"'))
        self.assertTrue(any('id="pn-t-title"' in t for t in p["texts"]))
        self.assertIn("flashCheck", p["accessibility"])

    def test_unknown_parameter(self):
        with self.assertRaises(KeyError):
            brand.prologue(KIT, {"pn-nope": "x"})

    def test_extend(self):
        p = brand.prologue(KIT, {})
        s = brand.extend(p["styles"], "styles", '    <textStyle id="x" basedOn="pn-base"/>\n')
        self.assertTrue(s.endswith('<textStyle id="x" basedOn="pn-base"/>\n  </styles>'))


class Components(unittest.TestCase):
    def setUp(self):
        self.doc = pnkit.Doc()
        self.b = brand.Brand(self.doc)

    def test_placed_above_the_finish(self):
        self.assertEqual(self.b.title_card(1, 5, "KICKER", "Title", emblem=[("M0 0 L10 10", "#F2EBDD", 5)]), "")
        self.b.chapter_card(10, 13, "01", "A chapter")
        self.b.lower_third(20, 25, "Name", "Role")
        self.b.source_line(20, 25, "Source: x")
        self.b.end_card(30, 40, ["Credits"])
        self.assertEqual(len(self.b.overlays), 5)
        self.assertEqual(self.doc.assets, [])                         # brand texts are kept apart
        self.assertEqual(len(self.b.assets), 2 + 2 + 2 + 1 + 2)
        for a in self.b.assets:
            self.assertIn(' color="', a)                             # explicit colour on every brand text

    def test_kit_positions(self):
        x = self.b.lower_third_xml(0, 5, "N", "R")
        self.assertIn('x="192" y="680" width="900" height="152"', x)
        self.assertRegex(self.b.source_line_xml(0, 5, "S"), r'^<layer id="sl" asset="bt(-\d+)?" x="192" y="108">')
        self.assertIn('y="1016"', self.b.notch(0, 5))

    def test_fade_fits(self):
        x = brand.fade(1.0, 1.2)                                     # pushed out so in and out both fit
        self.assertIn('<key time="1.7" value="0"/>', x)


class Shorts(unittest.TestCase):
    BEATS = [("a.one", 1.0, 4.0), ("a.two", 5.5, 9.0), ("b.three", 10.5, 14.0)]

    def test_span_times(self):
        self.assertEqual(shorts.span_times(self.BEATS, "a.two", "a.two"), (4.78, 9.45))
        with self.assertRaises(AssertionError):
            shorts.span_times([("x", 1.0, 4.0), ("y", 4.3, 8.0)], "y", "y")    # would start inside x

    def test_segments(self):
        lines, maps, T = shorts.segments([(10.0, 20.0), (30.0, 35.0), (50.0, 52.6)])
        self.assertEqual(maps, [(10.0, 20.0, 0.0), (30.0, 35.0, 10.0), (50.0, 52.6, 15.0)])
        self.assertAlmostEqual(T, 17.6)
        self.assertIn('duration="0.3"', lines[0]); self.assertNotIn("transition", lines[-1])

    def test_overlay_and_build(self):
        doc = pnkit.Doc()
        calls = []

        def subject(x, y, s, gid):
            calls.append((x, y, s, gid)); return f'<group id="{doc.uid(gid)}"/>'

        out, sym, lay = shorts.build(doc, [("s1", "slug", [("a.two", "a.two")], ("A ", "B", ""))],
                                     lambda spans: [(4.78, 9.45), (20.0, 22.6)], lambda maps: '      <cue start="0.900" end="2.000" text="x"></cue>',
                                     lambda sid, T, head: shorts.overlay(doc, sid, T, head, subject, ("THE ", "TITLE")), "cap", "cap-on")
        self.assertEqual([c[3] for c in calls], ["s1-cv-card", "s1-hk-card"])
        self.assertIn('<symbol id="ov-s1" width="1080" height="1920" duration="7.27">', sym)
        self.assertIn('layout="short-9x16" overlay="ov-s1" burnCaptions="cap-s1"', out)
        self.assertIn('reframe="fit"', lay)
        self.assertEqual(len(doc.paints), 2)
        self.assertEqual(len(doc.assets), 4)                          # running headline, hook kicker, title, call to action
        self.assertIn(">TITLE</span>", doc.assets[2])


if __name__ == "__main__":
    unittest.main()
