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


def breaks(cues, width):
    """[(last word before the break, first word after it)] for every cue break inside a sentence and every line break"""
    out = []
    for k, c in enumerate(cues):
        ls = C.two_lines(" ".join(w[0] for w in c), width, start=k == 0 or cues[k - 1][-1][0].endswith((".", "?", "!")))
        if len(ls) == 2:
            out.append((ls[0].split()[-1], ls[1].split()[0]))
        if k + 1 < len(cues) and not c[-1][0].endswith((".", "?", "!")):
            out.append((c[-1][0], cues[k + 1][0][0]))
    return out


class WeakWords(unittest.TestCase):
    """fault (b): no line or cue ends on what / your / there / because / our / where (found on v019, v024, v028)"""
    LINES = ("Here is exactly what the doctors were told.",
             "Before the test, your chance was one in a hundred.",
             "The question is what it has actually learned: the wing or the flow.",
             "A clock higher up, where gravity is weaker, runs fast.",
             "It works on paper, and there the matter rested for years.",
             "Nobody saw the error because the numbers on the screen looked right.",
             "That is the reason our maps agree with the ground under them.",
             "It is the place where you are standing when the signal arrives.")

    def test_the_list_has_them(self):
        for w in ("what how where who because there per our your their his her my but then after before so").split():
            self.assertIn(w, C.WEAK)

    def test_no_line_ends_on_one(self):
        for t in self.LINES:
            ls = C.two_lines(t, C.LINE)
            self.assertEqual(len(ls), 2, t)
            self.assertNotIn(ls[0].split()[-1].lower().strip(",."), C.WEAK, ls)
            self.assertLessEqual(max(len(x) for x in ls), C.LINE)

    def test_no_cue_or_line_ends_on_one(self):
        for width in (C.LINE, C.SHORT_LINE):
            words = speak(" ".join(self.LINES))
            cues = C.split_cues(words, width)
            self.assertEqual([w for c in cues for w in c], words)
            for a, b in breaks(cues, width):
                self.assertNotIn(a.lower().strip(",."), C.WEAK, (a, b))

    def test_a_weak_break_when_there_is_no_other(self):
        ls = C.two_lines("of the of the of the of the of the of the of the", 26)
        self.assertEqual(len(ls), 2); self.assertEqual(" ".join(ls).split(), ["of", "the"] * 7)


class NumbersAndNames(unittest.TestCase):
    """fault (c): no break inside a number or a name"""
    def test_runs(self):
        def stuck(text, start=True):
            t = text.split(); return {(t[i - 1], t[i]) for i in C.no_break(t, frozenset(), start)}
        self.assertEqual(stuck("from about one in ten to nearly half"), {("one", "in"), ("in", "ten")})
        self.assertEqual(stuck("one person in ten thousand of those"), {("ten", "thousand"), ("thousand", "of")})
        self.assertEqual(stuck("it was right three times in ten at best"), {("three", "times"), ("times", "in"), ("in", "ten")})
        self.assertEqual(stuck("eight out of every ten cases"), {("eight", "out")})
        self.assertEqual(stuck("about seventy-five per cent of them"), {("seventy-five", "per"), ("per", "cent"), ("cent", "of")})
        self.assertEqual(stuck("it took 20 000 hours, in 1982, to finish"), {("20", "000")})
        self.assertEqual(stuck("Apollo 12 left a seismometer"), {("Apollo", "12")})
        self.assertEqual(stuck("the crew of Apollo 12 and of New Horizons left"), {("Apollo", "12"), ("New", "Horizons")})
        self.assertEqual(stuck("Then Newton saw it"), set())               # a sentence's first word alone is no name
        self.assertEqual(stuck("Then Newton saw it", start=False), {("Then", "Newton")})
        self.assertEqual(stuck("It fell. Then Newton saw it, and I Think so"), set())

    def test_is_number(self):
        for t in ("one", "twenty", "ninety-five", "thousand,", "1982,", "3.8", "95%", "12", "half", "cent"):
            self.assertTrue(C.is_number(t), t)
        for t in ("person", "kilometres", "once", "tend", "a", "Apollo"):
            self.assertFalse(C.is_number(t), t)

    def test_two_lines_keep_them_whole(self):
        for text, whole in (("Correct answers went from about one in ten to nearly half.", "one in ten"),
                            ("The disease strikes one person in ten thousand every year.", "ten thousand"),
                            ("About thirty of them, twenty thousand kilometres over your head.", "twenty thousand"),
                            ("The doctors got it right three times in ten at best.", "three times in ten"),
                            ("In November 1969 the crew of Apollo 12 left a seismometer.", "Apollo 12"),
                            ("Nine years later the probe New Horizons flew past Pluto.", "New Horizons")):
            ls = C.two_lines(text, C.LINE)
            self.assertEqual(len(ls), 2, text); self.assertEqual(" ".join(ls), text)
            self.assertTrue(any(whole in x for x in ls), ls)

    def test_cues_keep_them_whole(self):
        text = ("In 1982 a researcher put the question to a hundred doctors and about one in ten of them got it right. "
                "The disease strikes one person in ten thousand of those who are tested in any one year. "
                "There are about thirty of them, some twenty thousand kilometres over your head. "
                "When the crew of Apollo 12 sent the lander into the Moon it rang for nearly an hour, "
                "and the doctors were right three times in ten at best.")
        for width in (C.LINE, C.SHORT_LINE):
            words = speak(text); cues = C.split_cues(words, width)
            self.assertEqual([w for c in cues for w in c], words)
            got = breaks(cues, width)
            for pair in (("one", "in"), ("in", "ten"), ("ten", "thousand"), ("twenty", "thousand"), ("Apollo", "12"),
                         ("three", "times"), ("times", "in"), ("a", "hundred")):
                self.assertNotIn(pair, got)
            for c in cues:
                ls = lines_of(c, width)
                self.assertLessEqual(len(ls), 2); self.assertLessEqual(max(len(x) for x in ls), width)


class OneBreak(unittest.TestCase):
    """fault (d): a cue is shown with the line break it was accepted with"""
    def test_two_lines_is_line_break(self):
        for text in (TEXT[:70], "Correct answers went from about one in ten to nearly half.", "short", "x" * 50):
            L = C.line_break(text.split(" "), C.LINE)
            self.assertEqual(C.two_lines(text, C.LINE), L[0] if L else [text])

    def test_fits_means_two_lines(self):
        self.assertIsNone(C.line_break(("word " * 17).split(), C.LINE))          # 84 characters: three lines
        self.assertIsNone(C.line_break(["a" * 30, "b" * 30, "c" * 20], C.LINE))   # 82, but no break gives two lines
        self.assertEqual(C.line_break(["a" * 30, "b" * 30], C.LINE), (["a" * 30, "b" * 30], True))
        lines, legal = C.line_break(["a" * 30, "of", "b" * 40], C.LINE)          # the only break is after "of"
        self.assertEqual((lines, legal), (["a" * 30 + " of", "b" * 40], False))

    def test_every_cue_fits_as_shown(self):
        for width in (C.LINE, C.SHORT_LINE):
            for c in C.split_cues(speak(TEXT), width):
                self.assertIsNotNone(C.line_break([w[0] for w in c], width))


class MinimumShow(unittest.TestCase):
    """fault (a): no cue under MIN_SHOW s on screen ("No." was shown for 0.43 s on v028)"""
    def test_extends_into_the_pause(self):
        words = speak("Is that the chance you are ill?") + speak("No.", t0=4.0) + speak("Before the test it was one in a hundred.", t0=6.0)
        cues = C.split_cues(words)
        self.assertEqual([w[0] for w in cues[1]], ["No."])
        (c, a, b), nxt = C.timed(cues)[1], C.timed(cues)[2]
        self.assertGreaterEqual(b - a, C.MIN_SHOW - 1e-9)
        self.assertLessEqual(a, 4.0); self.assertGreaterEqual(a, 4.0 - 0.3)      # not shown long before it is said
        self.assertLessEqual(b, nxt[1])

    def test_joins_a_neighbour_when_there_is_no_pause(self):
        words = speak("Is that the chance you are ill?", sentence_gap=0.5) + speak("No.", t0=3.3, sentence_gap=0.04)
        words += speak("Before the test, your chance was one in a hundred.", t0=words[-1][2] + 0.04)
        self.assertLess(words[-10][2] - words[-10][1] + 0.04, C.MIN_SHOW)        # "No." and the gap after it
        cues = C.split_cues(words)
        self.assertEqual([w for c in cues for w in c], words)
        texts = [" ".join(w[0] for w in c) for c in cues]
        self.assertIn("No. Before the test, your chance was one in a hundred.", texts)
        for c, a, b in C.timed(cues):
            self.assertGreaterEqual(b - a, C.MIN_SHOW - 1e-9)
            self.assertLessEqual(len(" ".join(w[0] for w in c)) / (b - a), C.MAX_CPS)
        ls = lines_of(cues[-1], C.LINE)
        self.assertLessEqual(max(len(x) for x in ls), C.LINE); self.assertNotIn(ls[0].split()[-1].lower(), C.WEAK)

    def test_one_word_units_everywhere(self):
        words = speak("No. Yes. Why? It works that out by listening to clocks. Up. There they gain forty-five. Net.",
                      sentence_gap=0.1)
        for width in (C.LINE, C.SHORT_LINE):
            cues = C.split_cues(words, width)
            self.assertEqual([w for c in cues for w in c], words)
            tl = C.timed(cues)
            for (c, a, b), nxt in zip(tl, tl[1:] + [(None, 1e9, 1e9)]):
                self.assertGreaterEqual(b - a, C.MIN_SHOW - 1e-9, " ".join(w[0] for w in c))
                self.assertLessEqual(b, nxt[1] + 1e-9)
                self.assertLessEqual(len(lines_of(c, width)), 2)

    def test_min_show_is_a_parameter(self):
        words = speak("No.") + speak("Before the test it was one in a hundred.", t0=0.6)
        self.assertEqual(len(C.split_cues(words, min_show=0.0)), 2)
        self.assertEqual(len(C.split_cues(words)), 1)


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
