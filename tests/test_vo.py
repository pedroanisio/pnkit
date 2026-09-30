"""vo: the narration dictionary loads, every item is well formed, speak applies whole-token respellings, and hazards
catches what v013 missed (the "A.I." split) without flagging v013's final spoken lines."""
import json, os, re, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit import vo

# v013's final spoken lines (a sample): what went to Kokoro after the fix
V013 = [
    "On September fifteenth, twenty twenty-six, a San Francisco startup released an AI model that does not write a single word.",
    "In twenty twenty-four, Almeida left and founded TypeSafe AI with a question: if models already converse better than people, why has so little work been automated?",
    "In a benchmark the company quotes, L L Ms took three to three hundred and twenty-nine seconds.",
    "Chatbots were trained with R L H F, reinforcement learning from human feedback, which rewards the answers people prefer.",
    "An independent study, published on archive, tested Jev on more than ten thousand cases of alignment failures.",
    "In TypeSafe's own four-workflow test, Jev scores sixty-seven point eight percent: tied with G P T five point six Terra, and behind Sol and Opus five.",
    "And the name Jev latest points to versions that change. Today it is one point thirteen point zero.",
    "Jev works best alongside an LLM.",
]


class Data(unittest.TestCase):
    def test_languages_and_fields(self):
        lex = vo.lexicon()
        langs = [k for k in lex if not k.startswith("_")]
        self.assertIn("en", langs); self.assertIn("pt-br", langs)
        for lang in langs:
            for e in lex[lang]["entries"]:
                self.assertTrue({"written", "spoken", "engine", "why", "source"} <= set(e), (lang, e))
                self.assertIn(e["engine"], ("any", "kokoro", "chatterbox", "piper"), (lang, e))
            for r in lex[lang]["rules"]:
                self.assertTrue({"rule", "example", "source"} <= set(r), (lang, r))
            for a in lex[lang]["asr_aliases"]:
                self.assertTrue({"heard", "means", "source"} <= set(a), (lang, a))

    def test_no_duplicate_written_forms(self):
        for lang in (k for k in vo.lexicon() if not k.startswith("_")):
            seen = [(e["written"], e["engine"]) for e in vo.entries(lang)]
            self.assertEqual(len(seen), len(set(seen)), lang)

    def test_spoken_forms_are_hazard_free(self):
        """a respelling must not itself be something hazards() flags"""
        for lang in (k for k in vo.lexicon() if not k.startswith("_")):
            for e in vo.entries(lang):
                hs = [h for h in vo.hazards(e["spoken"], lang) if h.kind in ("split", "digits", "symbol", "dash", "ellipsis")]
                self.assertEqual(hs, [], (lang, e["written"], [str(h) for h in hs]))

    def test_language_fallback(self):
        self.assertEqual(vo.entries("EN-US"), vo.entries("en"))
        self.assertEqual(vo.rules("pt"), vo.rules("pt-br"))
        with self.assertRaises(KeyError):
            vo.entries("xx")


class Speak(unittest.TestCase):
    def test_respellings(self):
        self.assertEqual(vo.speak("released an A.I. model", "en"), "released an AI model")
        self.assertEqual(vo.speak("published on arXiv, e.g. this one", "en"), "published on archive, for example this one")

    def test_whole_tokens_only(self):
        self.assertEqual(vo.speak("arXivist", "en"), "arXivist")          # not inside a longer word
        self.assertEqual(vo.speak("RLHF and LLMs", "en"), "RLHF and LLMs")  # read correctly as written: left alone

    def test_engine_filter(self):
        chatter = vo.speak("A.I.", "en", engine="chatterbox")
        self.assertEqual(chatter, "AI")                                    # engine "any" applies to every engine


class Hazards(unittest.TestCase):
    def kinds(self, text, lang="en", **kw):
        return sorted({h.kind for h in vo.hazards(text, lang, **kw)})

    def test_the_v013_miss(self):
        hs = vo.hazards("a San Francisco startup released an A.I. model", "en")
        self.assertEqual([(h.kind, h.match) for h in hs], [("split", "A.I.")])

    def test_v013_final_lines_are_clean(self):
        for line in V013:
            self.assertEqual([str(h) for h in vo.hazards(line, "en")], [], line)

    def test_splits(self):
        self.assertIn("split", self.kinds("Dr. Smith agreed."))
        self.assertIn("split", self.kinds("George W. Bush agreed."))
        self.assertNotIn("split", self.kinds("It went viral on X. Then it stopped."))
        self.assertNotIn("split", self.kinds("They call it Just G R P O. It works."))
        self.assertIn("split", self.kinds("O Sr. Almeida chegou.", "pt-br"))

    def test_digits_and_symbols(self):
        self.assertEqual(self.kinds("It scores 67.8% on the test."), ["digits", "symbol"])
        self.assertEqual(self.kinds("Version 1.13.0."), ["digits"])

    def test_acronyms(self):
        self.assertEqual(self.kinds("Built on SREP."), ["acronym"])
        self.assertEqual(self.kinds("Built on SREP.", known_acronyms=["SREP"]), [])
        self.assertEqual(self.kinds("Trained with RLHF by NVIDIA."), [])      # tested, in the dictionary

    def test_dashes_ellipses_letters(self):
        self.assertIn("dash", self.kinds("the Harvard–Smithsonian Center"))
        self.assertIn("ellipsis", self.kinds("Então... vai tudo pro cofrinho.", "pt-br"))
        self.assertNotIn("ellipsis", self.kinds("And then..."))
        self.assertIn("letter", self.kinds("It sends it to queue A or queue B."))
        self.assertIn("letter", self.kinds("Era o Dia D na Normandia.", "pt-br"))
        self.assertNotIn("letter", self.kinds("I think so. A study says otherwise."))

    def test_long_sentence(self):
        self.assertIn("long", self.kinds(" ".join(["word"] * 45) + "."))


class AsrNormalise(unittest.TestCase):
    def test_both_sides_compare_equal(self):
        self.assertEqual(vo.asr_normalise("An A.I. model on arXiv", "en"), vo.asr_normalise("an AI model on archive", "en"))


if __name__ == "__main__":
    unittest.main()
