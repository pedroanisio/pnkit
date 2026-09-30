"""xml, text and draw helpers: formatting, ids, fades, the 36 px label floor, text-asset caching, pills."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pnkit
from pnkit.xml import f, esc, Ids, opacity, keys, path_d, hash01
from pnkit import text, draw


class Xml(unittest.TestCase):
    def test_f(self):
        self.assertEqual([f(3), f(3.0), f(0.1 + 0.2), f(-0.0001), f(2.50), f(True), f("x")], ["3", "3", "0.3", "0", "2.5", "True", "x"])

    def test_esc(self):
        self.assertEqual(esc('a & "b" <c>'), "a &amp; &quot;b&quot; &lt;c&gt;")

    def test_ids(self):
        ids = Ids()
        self.assertEqual([ids.uid("p"), ids.uid("p"), ids.uid("p"), ids.uid("q")], ["p", "p-2", "p-3", "q"])
        self.assertIn("p-2", ids)

    def test_opacity_window(self):
        x = opacity(2, 2.02)                              # widened to 0.1 s, fades share it
        self.assertIn('<key time="2" value="0"', x); self.assertIn('<key time="2.1" value="0"/>', x)
        self.assertIn('<key time="2.05" value="1"/>', x)
        self.assertEqual(opacity(1, 5, 0.5, 0.5, peak=0.6).count('value="0.6"'), 2)

    def test_keys(self):
        self.assertEqual(keys("x", [(0.12345, 1.5), (1, "a,b", "linear")]),
                         '<animate property="x"><key time="0.123" value="1.5" interpolation="sine-in-out"/>'
                         '<key time="1" value="a,b" interpolation="linear"/></animate>')

    def test_path_and_hash(self):
        self.assertEqual(path_d([(0, 0), (10.04, 5.06)], True), "M0 0 L10 5.1 Z")
        v = [hash01(i, 3) for i in range(200)]
        self.assertTrue(all(0 <= x < 1 for x in v)); self.assertEqual(v, [hash01(i, 3) for i in range(200)])


class Text(unittest.TestCase):
    def setUp(self):
        self.doc = pnkit.Doc(styles={"text": "s-text", "caps": "s-caps", "num": "s-num", "head": "s-head", "note": "s-note", "big": "s-big"})

    def test_label_floor_is_36px(self):
        text.label(self.doc, "small", 100, 100, 0, 3, size=20)
        self.assertIn('size="36"', self.doc.assets[-1])
        text.label(self.doc, "key", 100, 100, 0, 3, size=54)
        self.assertIn('size="54"', self.doc.assets[-1])
        self.assertEqual(text.MIN_INFO_PX, 36)

    def test_assets_are_shared(self):
        a = text.text_asset(self.doc, "SAME", 40, style="caps")
        b = text.text_asset(self.doc, "SAME", 40, style="caps")
        self.assertEqual(a, b); self.assertEqual(len(self.doc.assets), 1)
        self.assertIn('style="s-caps"', self.doc.assets[0]); self.assertIn('color="#F2EBDD"', self.doc.assets[0])

    def test_label_anchor(self):
        x = text.label(self.doc, "LEFT", 200, 300, 1, 4, anchor="left")
        self.assertIn('anchorX="0"', x); self.assertIn('align="start"', self.doc.assets[-1])

    def test_spans(self):
        text.text_asset(self.doc, "A B", 40, spans=[("A ", None, None), ("B", "accent", "#E8581C")])
        self.assertIn('<span>A </span><span role="accent" color="#E8581C">B</span>', self.doc.assets[-1])


class Draw(unittest.TestCase):
    def test_draw_uses_the_frame(self):
        doc = pnkit.Doc(1080, 1920)
        x = draw.draw(doc, "M0 0 L10 10", 1, 3)
        self.assertIn('width="1080" height="1920"', x); self.assertIn('trimEnd="0"', x)
        self.assertIn('trimEnd="1"', draw.draw(doc, "M0 0 L1 1", 1, 3, dur=0))

    def test_pill(self):
        doc = pnkit.Doc()
        x = draw.pill(doc, 500, 400, "QUEUE C", 1, 4)
        self.assertTrue(x.startswith('<group id="pill" x="500" y="400"'))
        self.assertIn('<shape id="pill-b" shape="rect"', x); self.assertIn('<layer id="pill-t" asset="t"', x)
        self.assertIn('fill="#E8581C"', x)

    def test_rect_anchor_and_shapes(self):
        doc = pnkit.Doc()
        self.assertIn('anchorX="50" anchorY="20"', draw.rect(doc, 0, 0, 100, 40, "#000", 0, 1))
        self.assertIn('anchorX="0" anchorY="0"', draw.rect(doc, 0, 0, 100, 40, "#000", 0, 1, anchor="top-left"))
        self.assertIn('width="20" height="20"', draw.disc(doc, 5, 5, 10, "#fff", 0, 1))
        self.assertTrue(draw.round_rect_d(0, 0, 100, 50, 10).startswith("M10 0 L90 0 A10 10 0 0 1 100 10"))
        self.assertTrue(draw.arrow_d(0, 0, 100, 0).startswith("M0 0 L100 0 M"))
        g = draw.group(doc, ["<a/>", "", None, "<b/>"], a=0, b=2)
        self.assertEqual(g.count("\n"), 3)

    def test_bind(self):
        doc = pnkit.Doc()
        K = pnkit.bind(doc)
        K.label("X", 0, 0, 0, 1)
        self.assertEqual(len(doc.assets), 1)
        self.assertIs(K.doc, doc)


if __name__ == "__main__":
    unittest.main()
