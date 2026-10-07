"""vo.speak_map and captions.written_words: captions in the WRITTEN form ("12,4%") timed by the SPOKEN words, from a
token-level written -> spoken map (not by guessing). Fixtures are sentences of the Lula 3.0.0 film (p3/CHANGES.md)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit import vo, captions

WRITTEN = "o desemprego médio cai de 12,4% para 6,7%, entre 2003 e 2010."
SPOKEN = "o desemprego médio cai de doze vírgula quatro por cento para seis vírgula sete por cento, entre dois mil e três e dois mil e dez."


def timed(spoken, step=0.2, t0=1.0):
    return [(w, round(t0 + i * step, 3), round(t0 + i * step + 0.15, 3)) for i, w in enumerate(spoken.split())]


class Numbers(unittest.TestCase):
    def test_cardinals(self):
        for n, s in [(0, "zero"), (3, "três"), (12, "doze"), (21, "vinte e um"), (100, "cem"), (101, "cento e um"), (103, "cento e três"),
                     (200, "duzentos"), (1000, "mil"), (1500, "mil e quinhentos"), (1234, "mil duzentos e trinta e quatro"),
                     (1933, "mil novecentos e trinta e três"), (2003, "dois mil e três"), (2010, "dois mil e dez"),
                     (2025, "dois mil e vinte e cinco"), (5772, "cinco mil setecentos e setenta e dois"),
                     (103000000, "cento e três milhões"), (1000000, "um milhão"), (2500000, "dois milhões e quinhentos mil"),
                     (1000000000, "um bilhão")]:
            self.assertEqual(vo.pt_cardinal(n), s, n)

    def test_expand(self):
        self.assertEqual(vo.pt_number("12,4%"), "doze vírgula quatro por cento")
        self.assertEqual(vo.pt_number("6,7"), "seis vírgula sete")
        self.assertEqual(vo.pt_number("5,06"), "cinco vírgula zero seis")      # a leading zero is read digit by digit
        self.assertEqual(vo.pt_number("38,1%"), "trinta e oito vírgula um por cento")
        self.assertEqual(vo.pt_number("5.772"), "cinco mil setecentos e setenta e dois")
        self.assertEqual(vo.pt_number("54%"), "cinquenta e quatro por cento")


class SpeakMap(unittest.TestCase):
    def test_numbers_off_by_default_and_unchanged(self):
        self.assertEqual(vo.speak(WRITTEN, "pt-br"), WRITTEN)
        self.assertEqual(vo.speak("a greve do ABC", "pt-br", "kokoro"), "a greve do ABC")

    def test_speak_numbers(self):
        self.assertEqual(vo.speak(WRITTEN, "pt-br", "elevenlabs", numbers=True), SPOKEN)

    def test_map_tokens(self):
        m = vo.speak_map(WRITTEN, "pt-br", "elevenlabs", numbers=True)
        self.assertEqual(m.spoken, SPOKEN)
        self.assertEqual([t.written for t in m.tokens], WRITTEN.split())
        by = {t.written: t.spoken for t in m.tokens}
        self.assertEqual(by["12,4%"], "doze vírgula quatro por cento")
        self.assertEqual(by["6,7%,"], "seis vírgula sete por cento,")
        self.assertEqual(by["2003"], "dois mil e três")
        self.assertEqual(by["2010."], "dois mil e dez.")
        self.assertEqual(" ".join(t.spoken for t in m.tokens), SPOKEN)

    def test_map_matches_speak_for_every_entry(self):
        for lang in ("en", "pt-br"):
            for e in vo.entries(lang):
                for engine in ("kokoro", "elevenlabs", "chatterbox", "piper"):
                    text = f"antes {e['written']} depois, fim"
                    self.assertEqual(vo.speak_map(text, lang, engine).spoken, vo.speak(text, lang, engine), (lang, e["written"], engine))

    def test_multiword_entry_is_one_token(self):
        m = vo.speak_map("o Dia D chegou", "pt-br", "kokoro")
        self.assertEqual([(t.written, t.spoken) for t in m.tokens], [("o", "o"), ("Dia D", "Dia Dê"), ("chegou", "chegou")])

    def test_acronyms_elevenlabs(self):
        m = vo.speak_map("Nas greves do ABC, o PT e a CPI.", "pt-br", "elevenlabs")
        self.assertEqual(m.spoken, "Nas greves do á bê cê, o pê tê e a cê pê í.")
        self.assertEqual(m.tokens[3].spoken, "á bê cê,")

    def test_other_engine_unchanged(self):
        self.assertEqual(vo.speak("o PIB e o ABC", "pt-br", "kokoro"), "o PIB e o ABC")

    def test_numbers_other_language_refused(self):
        with self.assertRaises(ValueError):
            vo.speak("12,4%", "en", numbers=True)


class WrittenWords(unittest.TestCase):
    def test_lula_sentence(self):
        out = captions.written_words(timed(SPOKEN), WRITTEN, "pt-br", engine="elevenlabs")
        self.assertEqual([w for w, _, _ in out], WRITTEN.split())
        sp = timed(SPOKEN)
        i = SPOKEN.split().index("doze")
        w, s, e = out[5]
        self.assertEqual(w, "12,4%")
        self.assertEqual((s, e), (sp[i][1], sp[i + 4][2]))            # first spoken word's start, last one's end
        w, s, e = out[-1]
        self.assertEqual((w, e), ("2010.", sp[-1][2]))
        for a, b in zip(out, out[1:]):
            self.assertLessEqual(a[1], b[1])

    def test_lexicon_respelling(self):
        spoken = "Nas greves do á bê cê, a disputa continua."
        out = captions.written_words(timed(spoken), "Nas greves do ABC, a disputa continua.", "pt-br", engine="elevenlabs")
        self.assertEqual([w for w, _, _ in out], "Nas greves do ABC, a disputa continua.".split())
        sp = timed(spoken)
        self.assertEqual(out[3][1:], (sp[3][1], sp[5][2]))

    def test_aligned_words_may_carry_other_punctuation_and_case(self):
        sp = timed(SPOKEN.replace(",", "").replace(".", "").upper())
        out = captions.written_words(sp, WRITTEN, "pt-br", engine="elevenlabs")
        self.assertEqual(len(out), len(WRITTEN.split()))

    def test_misaligned_raises_naming_token(self):
        bad = SPOKEN.replace("seis vírgula sete", "seis vírgula oito")
        with self.assertRaises(captions.CaptionAlignError) as cm:
            captions.written_words(timed(bad), WRITTEN, "pt-br", engine="elevenlabs")
        self.assertEqual(cm.exception.token, "6,7%,")
        self.assertIn("6,7%,", str(cm.exception))

    def test_extra_and_missing_spoken_words(self):
        with self.assertRaises(captions.CaptionAlignError) as cm:
            captions.written_words(timed(SPOKEN + " extra"), WRITTEN, "pt-br", engine="elevenlabs")
        self.assertIn("extra", str(cm.exception))
        with self.assertRaises(captions.CaptionAlignError) as cm:
            captions.written_words(timed(SPOKEN)[:-2], WRITTEN, "pt-br", engine="elevenlabs")
        self.assertEqual(cm.exception.token, "2010.")

    def test_stale_text_fails_loudly(self):
        # the caption text cut a clause the voice still says (or vice versa): no silent guess
        with self.assertRaises(captions.CaptionAlignError):
            captions.written_words(timed(SPOKEN), WRITTEN.replace("entre 2003 e 2010.", "em 2010."), "pt-br", engine="elevenlabs")

    def test_feeds_split_cues(self):
        out = captions.written_words(timed(SPOKEN), WRITTEN, "pt-br", engine="elevenlabs")
        text = " ".join(" ".join(w for w, _, _ in c) for c in captions.split_cues(out))
        self.assertEqual(text, WRITTEN)
        self.assertNotIn("vírgula", text)


if __name__ == "__main__":
    unittest.main()
