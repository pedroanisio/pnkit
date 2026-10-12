"""The SDK path (pnkit 1.0): components build `sr_core.scene` elements; the SDK refuses what the schema refuses at
construction; a Doc builds a Scene whose level-1 check is clean; the scene round-trips through `sr_core.scene.read`."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnkit
from pnkit import sdk, text, draw, xml, camera, brand, shorts, captions, physics, figure, audio
from pnkit.sdk import Xml, S, SchemaValueError
from c14n import c14n, c14n_numeric, wrap

KIT = os.environ.get("PNKIT_KIT") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "palsnotes-brand.xml")
STYLES = {"text": "pn-body", "caps": "pn-label", "num": "pn-data", "head": "pn-heading", "note": "pn-body", "big": "pn-display"}


class Values(unittest.TestCase):
    def test_numbers_keep_pnkit_form(self):
        self.assertEqual([sdk.num(0.1 + 0.2), sdk.num(5.0), sdk.num(-0.0001), sdk.num(2.5), sdk.num(7)], [0.3, 5, 0, 2.5, 7])
        el = sdk.new(S.Composition, "layer", id="a", asset="x", x=0.1 + 0.2, y=5.0, anchorX=1 / 3)
        self.assertEqual(str(Xml.of(el)), '<layer id="a" asset="x" x="0.3" y="5" anchorX="0.333"/>')

    def test_text_attributes_take_the_text(self):
        p = sdk.new(S.Scene, "project", width=1920, height=1080, fps=30, duration=4.0, seed=1)   # fps is xs:string
        self.assertEqual(str(Xml.of(p)), '<project width="1920" height="1080" fps="30" duration="4" seed="1"/>')

    def test_a_bad_value_raises_at_construction(self):
        with self.assertRaises(SchemaValueError):
            sdk.new(S.Group, "shape", id="s", shape="circle")                       # the enumeration says ellipse
        with self.assertRaises(SchemaValueError):
            sdk.new(S.Group, "layer", id="l", asset="x", opacity=1.5)               # unit interval

    def test_a_bad_parent_raises(self):
        with self.assertRaises(SchemaValueError):
            sdk.new(S.Group, "key", time=1)                                         # <key> belongs in <animate>

    def test_an_undeclared_attribute_raises(self):
        with self.assertRaises(AttributeError):
            sdk.new(S.Group, "shape", id="s", shape="rect", strokeDash="4 2")       # the schema's name is `dash`

    def test_xml_is_a_str_that_carries_its_elements(self):
        x = xml.opacity(1, 4)
        self.assertIsInstance(x, str); self.assertIsInstance(x, Xml)
        self.assertIsInstance(x.element, S.Animate)
        self.assertTrue(x.startswith('<animate property="opacity">'))
        self.assertEqual("\n".join([x, x]).count("<animate"), 2)                     # old callers join strings

    def test_strings_are_parsed_against_the_parent(self):
        g = sdk.new(S.Composition, "group", id="g")
        sdk.adopt(g, '<shape id="s1" shape="rect" width="10" height="10"/>', "", None)
        self.assertEqual([e.xml_name for e in g.elements()], ["shape"])
        with self.assertRaises(SchemaValueError):
            sdk.adopt(g, "<a/>")                                                    # not a scene element
        with self.assertRaises(ValueError):
            sdk.adopt(g, "<shape")                                                  # not well-formed


class Components(unittest.TestCase):
    def setUp(self):
        self.doc = pnkit.Doc(styles=STYLES)

    def test_label_returns_a_layer_element(self):
        x = text.label(self.doc, "Hello", 100, 100, 0, 3)
        self.assertIsInstance(x.element, S.Layer)
        self.assertEqual(self.doc.assets[-1].element.xml_name, "text")

    def test_label_refuses_a_foreign_child_in_extra(self):
        with self.assertRaises(SchemaValueError):
            text.label(self.doc, "Hello", 100, 100, 0, 3, extra='<key time="1" value="0"/>')

    def test_label_refuses_an_unknown_attribute(self):
        with self.assertRaises(AttributeError):
            text.label(self.doc, "Hello", 100, 100, 0, 3, attrs=' bogus="1"')

    def test_group_refuses_an_unknown_element(self):
        with self.assertRaises(SchemaValueError):
            draw.group(self.doc, ["<a/>"])

    def test_group_takes_elements_and_strings(self):
        r = draw.rect(self.doc, 1, 2, 3, 4, "#112233", 0, 1)
        g = draw.group(self.doc, [r, "", None, '<shape id="own" shape="rect" width="1" height="1"/>'], a=0, b=2)
        self.assertEqual([e.xml_name for e in g.element.elements()], ["animate", "shape", "shape"])

    def test_a_three_digit_colour_is_refused(self):
        with self.assertRaises(SchemaValueError):
            draw.rect(self.doc, 0, 0, 10, 10, "#fff", 0, 1)

    def test_camera_group(self):
        cam = camera.Cam(self.doc, "act", [(1.0, 960, 540, 1.0)], 0, 8)
        g = cam.group(draw.disc(self.doc, 5, 5, 10, "#FFFFFF", 0, 1))
        self.assertEqual(g.element.xml_name, "group")
        self.assertTrue(cam.open().startswith("<group "))
        self.assertEqual(camera.Cam.CLOSE, "</group>")

    def test_a_bad_audio_asset_is_refused(self):
        c = audio.Cues(extra={"x": {"kind": "file", "path": "a.wav", "gain": 0.2}})
        self.assertEqual(c.assets(30.0), [])
        c.sfx(2.0, "x")
        self.assertIn('<audio id="sfx-x" src="a.wav"/>', c.assets(30.0))

    def test_a_quote_in_a_prompt_is_escaped(self):
        c = audio.Cues(extra={"q": {"kind": "audioforge", "model": "m/x", "prompt": 'a "quiet" <room>', "gain": 0.2}})
        c.sfx(2.0, "q")
        self.assertIn("a &quot;quiet&quot; &lt;room>", c.assets(30.0)[0])           # well-formed; 0.8.0 wrote it raw


class Build(unittest.TestCase):
    """a Doc builds a Scene; check() is clean; a level-1 error stops the build; a round trip through `read` is C14N-equal"""

    def build(self, check=True):
        doc = pnkit.Doc()
        pro = brand.prologue(KIT, {})
        doc.assets.append(pro["font"]); doc.assets.extend(pro["texts"])
        lab = text.label(doc, "Hello", 960, 540, 0, 3)
        dot = draw.disc(doc, 100, 100, 20, "#FFFFFF", 0, 3)
        comp = sdk.new(S.Scene, "composition", lab, dot)
        scene = doc.build({"fps": 30, "duration": 4.0, "seed": 1}, comp, pro["parameters"], pro["styles"], pro["layouts"],
                          pro["safeAreas"], pro["symbols"], check=check)
        return doc, scene

    def test_check_is_clean(self):
        doc, scene = self.build()
        self.assertEqual(doc.check(), [])
        self.assertIs(doc.scene, scene)
        self.assertEqual([e.xml_name for e in scene.elements()][:2], ["project", "parameters"])

    def test_check_level_two_is_clean_too(self):
        try:
            import lxml  # noqa: F401
        except ImportError:
            self.skipTest("level 2 needs lxml")
        doc, _ = self.build()
        self.assertEqual(doc.check(schema=True), [])

    def test_a_level_1_error_stops_the_build(self):
        doc = pnkit.Doc()
        comp = sdk.new(S.Scene, "composition", sdk.new(S.Composition, "layer", id="a", asset="nope", x=1))
        with self.assertRaises(sdk.BuildError) as cm:
            doc.build({"fps": 30, "duration": 4, "seed": 1}, comp)
        self.assertIn("nope", str(cm.exception))
        self.assertTrue(cm.exception.findings)

    def test_write_refuses_an_unchecked_bad_document(self):
        import tempfile
        doc = pnkit.Doc()
        comp = sdk.new(S.Scene, "composition", sdk.new(S.Composition, "layer", id="a", asset="nope", x=1))
        doc.build({"fps": 30, "duration": 4, "seed": 1}, comp, check=False)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(sdk.BuildError):
                doc.write(os.path.join(d, "x.xml"))
            self.assertEqual(os.listdir(d), [])

    def test_round_trip_through_read(self):
        import tempfile
        doc, _ = self.build()
        with tempfile.TemporaryDirectory() as d:
            path = doc.write(os.path.join(d, "x.xml"))
            back = S.read(path)
            self.assertEqual(S.check(back), [])
            self.assertEqual(c14n(S.to_bytes(back).decode()), c14n(doc.to_bytes().decode()))

    def test_an_element_in_the_wrong_place_raises_at_construction(self):
        with self.assertRaises((SchemaValueError, AttributeError, ValueError, TypeError)):
            sdk.new(S.Scene, "layer", id="x")


class Golden(unittest.TestCase):
    """pnkit 0.8.0's component output (tests/golden/components-0.8.0.json) against this version's, C14N 2.0 with comments"""

    @classmethod
    def setUpClass(cls):
        import json
        here = os.path.dirname(os.path.abspath(__file__))
        cls.old = json.load(open(os.path.join(here, "golden", "components-0.8.0.json"), encoding="utf-8"))
        sys.path.insert(0, os.path.join(here, "golden"))
        import components_corpus
        cls.new = components_corpus.corpus(KIT)

    def test_same_entries(self):
        self.assertEqual(sorted(self.new), sorted(self.old))

    # entries that carry an xs:double the old code wrote as "1.000": the SDK writes the shortest form ("1"), so these
    # compare with c14n_numeric (attribute values -?\d+\.\d+ in shortest form on both sides); every other entry is strict.
    NUMERIC = {"captions.cue_xml", "captions.cue_xml.width", "captions.sidecar", "captions.sidecar.opts", "captions.short_cues",
               "shorts.output", "shorts.build.outputs",
               "assemble.segment", "assemble.segment.pages", "assemble.audio", "assemble.audio.bare", "assemble.audio.stem-full",
               "assemble.audio.stem-voice", "assemble.audio.stem-music", "assemble.audio.stem-sfx"}

    def test_every_entry_is_c14n_equal(self):
        bad = []
        for k in sorted(self.old):
            if k.endswith(".ids"):
                if self.old[k] != self.new[k]:
                    bad.append(k)
            elif k in self.NUMERIC:
                if c14n_numeric(wrap(self.old[k])) != c14n_numeric(wrap(self.new[k])):
                    bad.append(k)
            elif c14n(wrap(self.old[k])) != c14n(wrap(self.new[k])):
                bad.append(k)
        self.assertEqual(bad, [])

    def test_the_numeric_allow_list_is_needed(self):
        """an entry leaves the allow-list as soon as it is strictly equal"""
        for k in self.NUMERIC:
            self.assertNotEqual(c14n(wrap(self.old[k])), c14n(wrap(self.new[k])), k)

    def test_every_assembled_document_checks_clean_and_round_trips(self):
        """the documents the engine renders: level 1 clean, and `read` then `to_bytes` is C14N-equal"""
        docs = [k for k in self.new if k.startswith("assemble.") and k != "assemble.music_layer"]
        self.assertEqual(len(docs), 8)
        for k in docs:
            scene = S.read(self.new[k].encode("utf-8"))
            self.assertEqual([x for x in S.check(scene) if x.severity == "error"], [], k)
            self.assertEqual(c14n(S.to_bytes(scene).decode("utf-8")), c14n(self.new[k]), k)

    def test_strings_keep_the_old_attribute_order(self):
        """byte identity of the fragments, except where the SDK escapes less (a '>' in an attribute) or more"""
        same = [k for k in self.old if self.old[k] == self.new[k]]
        self.assertGreater(len(same), len(self.old) * 0.6, sorted(set(self.old) - set(same)))


if __name__ == "__main__":
    unittest.main()
