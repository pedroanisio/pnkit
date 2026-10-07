"""pnkit.pixel: build-time checks for integer-grid pixel-art films (ported from the Lula 3.0.0 picture checks, 2026-10-07)."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit import pixel


class ViewOutside(unittest.TestCase):
    LULA = dict(set_w=320, set_h=180, grid_w=320, grid_h=180, anchor=(160, 73))

    def test_window_geometry_matches_the_group_placement(self):
        v = pixel.view_outside(zoom=2, cx=160, cy=73, **self.LULA)
        self.assertEqual((v.x0, v.y0, v.x1, v.y1), (80.0, 36.5, 240.0, 126.5))
        self.assertFalse(v.outside)

    def test_lula_11a_zoom_276_is_22_percent_outside(self):
        v = pixel.view_outside(zoom=2, cx=276, cy=76, **self.LULA)
        self.assertEqual((v.x0, v.x1), (196.0, 356.0))
        self.assertEqual(v.cols, 36.0); self.assertEqual(v.rows, 0.0)
        self.assertTrue(v.outside)
        self.assertAlmostEqual(v.fraction, 0.225, places=3)
        self.assertIn("36 columns", v.describe())

    def test_lula_11a_fixed_zoom_240_is_clean(self):
        v = pixel.view_outside(zoom=2, cx=240, cy=76, **self.LULA)
        self.assertFalse(v.outside); self.assertEqual(v.fraction, 0.0)

    def test_a_wider_set_allows_the_pan(self):
        v = pixel.view_outside(set_w=620, set_h=180, grid_w=320, grid_h=180, zoom=2, cx=500, cy=76, anchor=(160, 73))
        self.assertFalse(v.outside)

    def test_default_anchor_is_the_grid_centre(self):
        v = pixel.view_outside(320, 180, 320, 180, 1, 160, 90)
        self.assertEqual((v.x0, v.y0, v.x1, v.y1), (0.0, 0.0, 320.0, 180.0))

    def test_rows_outside_and_corner_fraction(self):
        v = pixel.view_outside(320, 180, 320, 180, 1, 160, 120)      # 30 rows below the set
        self.assertEqual(v.rows, 30.0); self.assertAlmostEqual(v.fraction, 30 / 180)

    def test_bad_arguments(self):
        with self.assertRaises(ValueError): pixel.view_outside(320, 180, 320, 180, 0, 0, 0)
        with self.assertRaises(ValueError): pixel.view_outside(0, 180, 320, 180, 1, 0, 0)


class FigureCut(unittest.TestCase):
    def test_lula_11a_torso_cut_in_mid_air(self):
        r = pixel.figure_cut(51, 30)                    # 59 % of a 51-row woman
        self.assertIsNotNone(r); self.assertIn("59%", r)

    def test_covered_cut_is_allowed(self):
        self.assertIsNone(pixel.figure_cut(51, 30, occluded=True))

    def test_head_and_shoulders_and_feet_crops_are_allowed(self):
        self.assertIsNone(pixel.figure_cut(51, 14)); self.assertIsNone(pixel.figure_cut(51, 47))

    def test_boundaries_are_exclusive(self):
        self.assertIsNone(pixel.figure_cut(100, 35)); self.assertIsNone(pixel.figure_cut(100, 85))
        self.assertIsNotNone(pixel.figure_cut(100, 36)); self.assertIsNotNone(pixel.figure_cut(100, 84))

    def test_bad_height(self):
        with self.assertRaises(ValueError): pixel.figure_cut(0, 3)


class PlateLineBreaks(unittest.TestCase):
    def test_lula_09_plate(self):
        r = pixel.plate_line_breaks(["2003: 12,4% → 2010:", "6,7%"])
        self.assertTrue(r); self.assertIn("line 1", r[0])

    def test_colon_arrow_and_orphan_value(self):
        self.assertTrue(pixel.plate_line_breaks(["Salário mínimo:", "+53,67% real"]))
        self.assertTrue(pixel.plate_line_breaks(["2003: 12,4%", "→"]))
        self.assertTrue(pixel.plate_line_breaks(["a ->", "b"]))
        self.assertTrue(pixel.plate_line_breaks(["Mais de 600 mil mortes", "6,7%"]))

    def test_good_breaks(self):
        self.assertEqual(pixel.plate_line_breaks(["2003: 12,4%", "→ 2010: 6,7%"]), [])
        self.assertEqual(pixel.plate_line_breaks(["1989 · Primeira candidatura", "presidencial"]), [])
        self.assertEqual(pixel.plate_line_breaks(["6,7%"]), [])          # a one-line plate is not an orphan
        self.assertEqual(pixel.plate_line_breaks([]), [])


class ScaleGrid(unittest.TestCase):
    def test_integers_keep_the_grid(self):
        for s in (1, 2, 3, 6, 2.0, 6.0000000001): self.assertIsNone(pixel.scale_off_grid(s), s)

    def test_fractions_and_non_positive_break_it(self):
        for s in (1.5, 0.5, 2.25, 0, -2): self.assertIsNotNone(pixel.scale_off_grid(s), s)

    def test_not_a_number(self):
        self.assertIsNotNone(pixel.scale_off_grid(float("nan")))
        self.assertIsNotNone(pixel.scale_off_grid("2"))


if __name__ == "__main__":
    unittest.main()
