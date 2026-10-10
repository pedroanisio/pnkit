"""pnkit.pixelart.segment: the per-segment render check (from Lula p3/check_scene_v3.py), its measures on synthetic
grey frames (numpy) and the plan geometry rules."""
import os, sys, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from pnkit.pixelart import segment

try:
    import numpy as np
    HAVE_NP = True
except ImportError:
    HAVE_NP = False


@unittest.skipUnless(HAVE_NP, "numpy not installed")
class Measures(unittest.TestCase):
    def moving(self, n, h=27, w=48, seed=1):
        rng = np.random.default_rng(seed)
        return rng.integers(0, 255, size=(n, h, w)).astype(np.int16)

    def test_static_span_is_measured(self):
        x = self.moving(24 * 12)
        x[24:24 * 10] = x[24]                            # 9 s held still
        d = segment.frame_diffs(x)
        spans = segment.near_static_spans(d, fps=24, t0=100.0)
        self.assertEqual(len(spans), 1)
        self.assertAlmostEqual(spans[0]['seconds'], 9.0, delta=0.1)
        self.assertAlmostEqual(spans[0]['from_s'], 101.04, delta=0.05)

    def test_black_frames_are_counted(self):
        x = self.moving(48); x[10:13] = 0
        self.assertEqual(segment.black_or_flat(x), 3)

    def test_first_frame_missing_figure_is_found(self):
        x = np.full((48, 27, 48), 100, np.int16)
        for k in range(48):
            x[k, :, k % 48] = 140                         # slow motion everywhere
        x[12:, 2:8, 2:8] = 250                           # a figure appears one frame after the shot starts at frame 11
        bad = segment.first_frame_defects(x, starts=[11], names=['s01b_x'], t0=0.0, fps=24, picture_rows=27)
        self.assertEqual([b['shot'] for b in bad], ['s01b_x'])
        x[11, 2:8, 2:8] = 250
        self.assertEqual(segment.first_frame_defects(x, starts=[11], names=['s01b_x'], t0=0.0, fps=24, picture_rows=27), [])

    def test_jumps_outside_shot_starts(self):
        x = np.zeros((48, 27, 48), np.int16); x[30:] = 200
        d = segment.frame_diffs(x)
        self.assertEqual(len(segment.jumps(d, starts=[0], t0=0.0, fps=24)), 1)
        self.assertEqual(segment.jumps(d, starts=[0, 30], t0=0.0, fps=24), [])

    def test_dhash_differs_for_different_pictures(self):
        a = np.tile(np.arange(9, dtype=np.int16), (8, 1)); b = a[:, ::-1]
        self.assertNotEqual(segment.dhash(a), segment.dhash(b))
        self.assertEqual(len(segment.dhash(a)), 16)


class Geometry(unittest.TestCase):
    def test_plate_over_figure_and_low_soles(self):
        shots = [dict(name='s01a_x', plates=[dict(text='P', rect=[6, 6, 110, 27], start=0, end=2)], signs=[dict(text='S', rect=[50, 10, 90, 20])],
                      figures=[dict(kind='boy', rect=[100, 20, 120, 147], start=1, end=3)])]
        kinds = sorted(p[0] for p in segment.geometry_problems(shots))
        self.assertEqual(kinds, ['figure sole below row 145', 'plate over figure', 'plate over sign'])


if __name__ == "__main__":
    unittest.main()
