"""captions: cue rules (<= 2 x 42 characters, <= 17 characters/s, sentence and pause units, weak-word breaks),
display timing, Short cues in output time."""
import os, re, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit import captions as C


def speak(text, t0=0.0, per_char=0.068, word_gap=0.06, sentence_gap=0.55):
    """[(word, start, end)] at a natural pace (~14 characters/s), with a pause after each sentence"""
    out, t = [], t0
    for w in text.split():
        d = 0.08 + per_char * len(w)
        out.append((w, round(t, 3), round(t + d, 3)))
        t += d + (sentence_gap if w.endswith((".", "?", "!")) else word_gap)
    return out


TEXT = ("Jev does not write. It takes a state and a set of typed questions, and it returns a decision for each of "
        "them with a probability attached. Because every answer is fixed in advance, the model can never drift off "
        "the list of allowed options, and the program that reads the result never has to parse free text. That is "
        "why it can be fast, cheap and predictable at the same time, at least according to the company that makes it.")


def lines_of(cue, width):
    return C.two_lines(" ".join(w[0] for w in cue), width)


class CueRules(unittest.TestCase):
    def setUp(self):
        self.words = speak(TEXT)
        self.cues = C.split_cues(self.words, C.LINE)

    def test_every_word_once_in_order(self):
        self.assertEqual([w for c in self.cues for w in c], self.words)

    def test_at_most_two_lines_of_42(self):
        for c in self.cues:
            ls = lines_of(c, C.LINE)
            self.assertLessEqual(len(ls), 2, ls)
            for line in ls:
                self.assertLessEqual(len(line), C.LINE, line)

    def test_readable_rate(self):
        for c, a, b in C.timed(self.cues):
            text = " ".join(w[0] for w in c)
            self.assertLessEqual(len(text) / (b - a), C.MAX_CPS, text)

    def test_cues_do_not_span_sentences(self):
        for c in self.cues:
            for w in c[:-1]:
                self.assertFalse(w[0].endswith((".", "?", "!")), " ".join(x[0] for x in c))

    def test_no_break_after_a_weak_word(self):
        for c in self.cues:
            if c[-1][0].endswith((".", "?", "!")):
                continue                                      # a sentence may end on any word
            self.assertNotIn(c[-1][0].lower().strip(",."), C.WEAK, " ".join(w[0] for w in c))

    def test_no_line_ends_on_a_weak_word(self):
        for c in self.cues:
            ls = lines_of(c, C.LINE)
            if len(ls) == 2:
                self.assertNotIn(ls[0].split()[-1].lower(), C.WEAK, ls)

    def test_pause_ends_a_unit(self):
        words = speak("one two three four") + speak("five six seven eight", t0=10.0)
        units = C.split_units(words)
        self.assertEqual([len(u) for u in units], [4, 4])

    def test_windows_are_ordered_and_disjoint(self):
        tl = C.timed(self.cues)
        for (c0, a0, b0), (c1, a1, b1) in zip(tl, tl[1:]):
            self.assertLess(a0, b0)
            self.assertLessEqual(b0, a1 + 1e-9)
        # every cue covers its own speech
        for c, a, b in tl:
            self.assertLessEqual(a, c[0][1]); self.assertGreaterEqual(b, c[-1][2])

    def test_weak_words_extend_per_episode(self):
        w = speak("Send it to queue A or queue B when the refund is urgent and the customer is a VIP.")
        weak = C.WEAK | {"queue"}
        for c in C.split_cues(w, C.SHORT_LINE, weak=weak):
            self.assertNotEqual(c[-1][0].lower(), "queue")

    def test_stats(self):
        n, over, worst, longest = C.stats(self.words)
        self.assertEqual(n, len(self.cues)); self.assertEqual(over, 0)
        self.assertLessEqual(worst, C.MAX_CPS); self.assertLessEqual(longest, C.LINE)


class Xml(unittest.TestCase):
    def test_sidecar(self):
        x = C.sidecar(speak(TEXT))
        self.assertTrue(x.startswith('  <captions>\n    <captionTrack id="subs-en" language="en" kind="subtitles"'))
        self.assertEqual(x.count("<word "), len(TEXT.split()))
        self.assertIn("&#10;", x)             # two-line cues keep their break

    def test_escaping(self):
        x = C.cue_xml([[("\"odds\"", 0.0, 0.5), ("&", 0.6, 0.8)]])
        self.assertIn('text="&quot;odds&quot;"', x); self.assertIn('text="&amp;"', x)

    def test_short_cues_output_time_and_cover(self):
        words = speak(TEXT, t0=100.0)
        spans = [(100.0, 104.0, 0.0), (106.0, 112.0, 4.0)]
        x = C.short_cues(words, spans, not_before=0.9)
        starts = [float(s) for s in re.findall(r'<cue start="([\d.]+)"', x)]
        self.assertGreaterEqual(starts[0], 0.9)
        kept = [w for w in words if any(a <= w[1] and w[2] <= b for a, b, _ in spans)]
        self.assertEqual(x.count("<word "), len(kept))
        for s in re.findall(r'<word start="([\d.]+)"', x):
            self.assertLess(float(s), 10.0)      # mapped into output time
        self.assertNotIn("&#10;", x)          # a burned track lays out its own lines


if __name__ == "__main__":
    unittest.main()
