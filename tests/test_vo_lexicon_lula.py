"""The pt-br / elevenlabs entries approved by the owner's ear on 2026-10-07 (lula-filme p3/CHANGES.md)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit import vo

SRC = "lula-filme p3/CHANGES.md, owner approval 2026-10-07"
APPROVED = {"ABC": "á bê cê", "PT": "pê tê", "FHC": "éfe agá cê", "IBGE": "í bê gê é", "STJ": "ésse tê jota", "PF": "pê éfe",
            "CPI": "cê pê í", "PIB": "píbi", "ONU": "ônu", "SUS": "sus"}


class Lula(unittest.TestCase):
    def el(self):
        return {e["written"]: e for e in vo.entries("pt-br") if e["engine"] == "elevenlabs"}

    def test_respellings(self):
        el = self.el()
        for w, s in APPROVED.items():
            self.assertEqual(el[w]["spoken"], s)
            self.assertEqual(el[w]["source"], SRC)
            self.assertTrue(el[w]["why"])
            self.assertEqual(vo.speak(f"do {w},", "pt-br", "elevenlabs"), f"do {s},")

    def test_oas_tse_tested_as_written(self):
        el = self.el()
        for w, tried in (("OAS", "ó á ésse"), ("TSE", "tê essi é")):
            self.assertEqual(el[w]["spoken"], w)
            self.assertIn(tried, el[w]["why"])
            self.assertEqual(vo.speak(f"a {w} decide", "pt-br", "elevenlabs"), f"a {w} decide")
            self.assertEqual([h for h in vo.hazards(f"a {w} decide", "pt-br") if h.kind == "acronym"], [])

    def test_other_engines_untouched(self):
        for w in APPROVED:
            self.assertEqual(vo.speak(w, "pt-br", "kokoro"), w)

    def test_whisper_rule(self):
        rs = [r for r in vo.rules("pt-br") if "Whisper cannot verify letter names" in r["rule"]]
        self.assertEqual(len(rs), 1)
        self.assertTrue(rs[0]["source"] and rs[0]["example"])


if __name__ == "__main__":
    unittest.main()
