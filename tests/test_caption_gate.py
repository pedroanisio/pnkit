"""captions.check_text and tools/caption_gate.py: the cues' text must equal the approved written text."""
import importlib.util, json, os, subprocess, sys, tempfile, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from pnkit import captions

APPROVED = ("Nas seis regiões metropolitanas acompanhadas pelo IBGE, o desemprego médio cai de 12,4% para 6,7%, entre 2003 e 2010. "
            "O salário mínimo acumula cerca de 54% de ganho acima da inflação. Para muitas famílias, trabalhar passa a render mais.")
GOOD = ["Nas seis regiões metropolitanas\nacompanhadas pelo IBGE,", "o desemprego médio cai de 12,4% para 6,7%,", "entre 2003 e 2010.",
        "O salário mínimo acumula cerca de 54%\nde ganho acima da inflação.", "Para muitas famílias,\ntrabalhar passa a render mais."]


class CheckText(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(captions.check_text(GOOD, APPROVED, "pt-br"), [])

    def test_whitespace_and_line_breaks_only(self):
        self.assertEqual(captions.check_text(["  Um   dois\ntrês ", "quatro"], "Um dois três quatro", "pt-br"), [])

    def test_spelled_out_numbers(self):
        cues = list(GOOD); cues[1] = "o desemprego médio cai de DOZE VÍRGULA QUATRO para seis vírgula sete por cento,"
        fs = captions.check_text(cues, APPROVED, "pt-br")
        kinds = {f.kind for f in fs}
        self.assertIn("spelled-out", kinds); self.assertIn("text", kinds)
        sp = [f for f in fs if f.kind == "spelled-out"]
        self.assertTrue(all(f.cue == 1 for f in sp))
        self.assertTrue(any("vírgula" in f.detail.lower() for f in sp))
        self.assertTrue(any("por cento" in f.detail.lower() for f in sp))

    def test_number_words_where_approved_has_digits(self):
        cues = list(GOOD); cues[2] = "entre dois mil e três e dois mil e dez."
        fs = captions.check_text(cues, APPROVED, "pt-br")
        self.assertTrue(any(f.kind == "spelled-out" and f.cue == 2 and "2003" in f.detail for f in fs), fs)

    def test_number_words_not_flagged_when_approved_has_words(self):
        self.assertEqual(captions.check_text(["Cinco vírgula seis por cento."], "Cinco vírgula seis por cento.", "pt-br"), [])
        self.assertEqual(captions.check_text(["um ex-presidente"], "um ex-presidente com 3 filhos".replace(" com 3 filhos", ""), "pt-br"), [])

    def test_stale_clause_kept(self):
        cues = list(GOOD); cues[4] = "Para muitas famílias,\ntrabalhar passa a render mais, e a renda cai."
        fs = captions.check_text(cues, APPROVED, "pt-br")
        self.assertEqual([f.kind for f in fs if f.kind == "text"], ["text"])
        self.assertIn("e a renda cai", fs[0].detail)

    def test_clause_missing(self):
        fs = captions.check_text(GOOD[:2] + GOOD[3:], APPROVED, "pt-br")
        self.assertTrue(any("entre 2003 e 2010." in f.detail for f in fs if f.kind == "text"))

    def test_cue_shapes(self):
        words = [[("Um", 0, 1), ("dois", 1, 2)], [("três", 2, 3)]]
        self.assertEqual(captions.check_text(words, "Um dois três", "en"), [])
        timed = [([("Um", 0, 1)], 0.0, 1.0), ([("dois", 1, 2)], 1.0, 2.0)]
        self.assertEqual(captions.check_text(timed, "Um dois", "en"), [])
        self.assertEqual(captions.check_text([{"text": "Um dois"}], "Um dois", "en"), [])

    def test_english_has_no_spelled_out_rule(self):
        self.assertEqual(captions.check_text(["five point six per cent"], "five point six per cent", "en"), [])


class Tool(unittest.TestCase):
    def run_gate(self, cues_name, cues_body, approved, *extra):
        with tempfile.TemporaryDirectory() as d:
            c, a = os.path.join(d, cues_name), os.path.join(d, "approved.txt")
            for path, body in ((c, cues_body), (a, approved)):
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(body)
            return subprocess.run([sys.executable, os.path.join(LIB, "tools", "caption_gate.py"), c, "--approved", a, "--lang", "pt-br", *extra],
                                  capture_output=True, text=True)

    def test_json_pass_and_fail(self):
        r = self.run_gate("cues.json", json.dumps(GOOD), APPROVED)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        bad = list(GOOD); bad[2] = "entre dois mil e três e dois mil e dez."
        r = self.run_gate("cues.json", json.dumps([{"text": t, "start": 0, "end": 1} for t in bad]), APPROVED)
        self.assertEqual(r.returncode, 1)
        self.assertIn("spelled-out", r.stdout)

    def test_vtt(self):
        vtt = "WEBVTT\n\n" + "\n".join(f"{i+1}\n00:00:0{i}.000 --> 00:00:0{i}.900\n{t}\n" for i, t in enumerate(GOOD))
        self.assertEqual(self.run_gate("c.vtt", vtt, APPROVED).returncode, 0)
        self.assertEqual(self.run_gate("c.vtt", vtt.replace("IBGE", "IBG"), APPROVED).returncode, 1)

    def test_scene_xml(self):
        body = "<scene><captions><captionTrack id='t'>" + "".join(
            f'<cue start="{i}.000" end="{i}.900" text="{t.replace(chr(10), "&#10;")}"/>' for i, t in enumerate(GOOD)) + "</captionTrack></captions></scene>"
        self.assertEqual(self.run_gate("film.scene.xml", body, APPROVED).returncode, 0)
        self.assertEqual(self.run_gate("film.scene.xml", body.replace("54%", "54"), APPROVED).returncode, 1)


if __name__ == "__main__":
    unittest.main()
