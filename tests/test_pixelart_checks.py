"""pnkit.pixelart.checks and pnkit.pixelart.frames: the four picture checks that would have caught the Lula 3.0.0
defects (PICTURE-REVIEW.md section 2), at build time on the unchanged scene code (CheckedCtx) and on rendered frames.

  zoom view outside the set   11a: zoom(2, 276, 76) on a 320-column set, 36 columns of flat background
  figure cut at the waist     11a: crop at row 30 of a 51-row woman, nothing covering the cut
  plate line breaks           09:  "2003: 12,4% → 2010:" / "6,7%"
  flat dark field             11a's first frame: 22 % of the picture the project's background colour"""
import os, sys, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from pnkit.pixelart import checks, frames
from pnkit.pixelart.ctx import Geometry, r, P, PlanError

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def set_320():
    q = Geometry(); r(q, 0, 0, 320, 180, 'wood1'); return q


def one_shot(ctx, draw):
    ctx.begin_scene(1)
    s = ctx.shot('s01a_test', 0.0, 3.0, bg=set_320())
    draw(ctx, s)
    ctx.finish()
    return ctx.findings


class ZoomView(unittest.TestCase):
    def test_lula_11a_zoom_is_found(self):
        f = one_shot(checks.CheckedCtx(), lambda c, s: c.zoom(2, 276, 76, parent=s, start=0.0, end=3.0).__enter__())
        self.assertEqual([x['check'] for x in f], ['zoom-window-outside-set'])
        self.assertIn('36 columns', f[0]['detail'])

    def test_the_fixed_zoom_is_clean(self):
        self.assertEqual(one_shot(checks.CheckedCtx(), lambda c, s: c.zoom(2, 240, 76, parent=s, start=0.0, end=3.0).__enter__()), [])

    def test_a_wider_set_for_a_pan_counts_as_set(self):
        def draw(c, s):
            c.cur['set_w'] = 400
            c.zoom(2, 276, 76, parent=s).__enter__()
        self.assertEqual(one_shot(checks.CheckedCtx(), draw), [])


class FigureCut(unittest.TestCase):
    def crop_at(self, frac, cover=False):
        def draw(c, s):
            q = c.sprite_frame('mother', 'idle', 0.0, False, .5)
            ys = [y for _, y in q.cells]
            h = max(ys) - min(ys) + 1
            crop = round(h * frac)
            c.actor(s, 'mother', 'idle', 150, 60, 0.0, 3.0, crop=crop)
            if cover:
                t = Geometry(); r(t, 140, 60 + crop - 3, 50, 8, 'wood0')
                c.G(s, t)
        return one_shot(checks.CheckedCtx(), draw)

    def test_waist_crop_in_mid_air_is_found(self):
        f = self.crop_at(0.59)
        self.assertEqual([x['check'] for x in f], ['figure-cut-mid-body'])

    def test_waist_crop_behind_a_table_is_allowed(self):
        self.assertEqual(self.crop_at(0.59, cover=True), [])

    def test_head_and_shoulders_and_feet_crops_are_allowed(self):
        self.assertEqual(self.crop_at(0.30), [])
        self.assertEqual(self.crop_at(0.90), [])


class PlateBreaks(unittest.TestCase):
    def test_label_parted_from_value_is_found(self):
        f = one_shot(checks.CheckedCtx(), lambda c, s: c.box(s, (6, 6, 150, 40), 0.0, 3.0, lines=('2003: 12,4% → 2010:', '6,7%')))
        self.assertEqual([x['check'] for x in f], ['plate-line-break'])

    def test_a_whole_line_per_value_is_clean(self):
        f = one_shot(checks.CheckedCtx(), lambda c, s: c.box(s, (6, 6, 150, 40), 0.0, 3.0, lines=('2003: 12,4%', '2010: 6,7%')))
        self.assertEqual(f, [])

    def test_wrapped_plate_text_is_judged_on_its_wrap(self):
        f = one_shot(checks.CheckedCtx(), lambda c, s: c.plate('Curitiba · 2018', 'TL', 0.5, 2.5))
        self.assertEqual(f, [])


class Waivers(unittest.TestCase):
    def test_waiver_needs_a_reason_and_marks_the_finding(self):
        found = [dict(check='plate-line-break', shot='s01a_test', scene=1, detail='x')]
        out = checks.apply_waivers(found, [dict(check='plate-line-break', shot='s01a_test', reason='label and value by design')])
        self.assertTrue(out[0]['waived'])
        with self.assertRaises(ValueError):
            checks.apply_waivers(found, [dict(check='plate-line-break', shot='s01a_test', reason='')])

    def test_unused_waiver_is_reported(self):
        out, unused = checks.apply_waivers([], [dict(check='zoom-window-outside-set', shot='s09a', reason='r')], report_unused=True)
        self.assertEqual(out, []); self.assertEqual(len(unused), 1)


class BuildRules(unittest.TestCase):
    def test_plate_below_the_picture_area_still_raises(self):
        with self.assertRaises(PlanError):
            one_shot(checks.CheckedCtx(), lambda c, s: c.box(s, (6, 120, 150, 160), 0.0, 3.0, lines=('x',)))


@unittest.skipUnless(HAVE_PIL, "Pillow not installed")
class FlatField(unittest.TestCase):
    BG = (11, 16, 32)

    def frame(self, empty_cols=0, flat=False):
        im = Image.new('RGB', (1920, 1080), (90, 120, 60) if flat else (0, 0, 0))
        if not flat:
            px = im.load()
            for y in range(0, 1080, 6):                     # a busy picture: a checker of two colours per cell
                for x in range(0, 1920, 6):
                    c = (200, 100, 50) if (x // 6 + y // 6) % 2 else (40, 140, 90)
                    for dy in (3,):
                        px[x + 3, y + dy] = c
        if empty_cols:
            im.paste(self.BG, (1920 - empty_cols * 6, 0, 1920, 1080))
        return im

    def test_lula_11a_strip_of_background_is_found(self):
        r_ = frames.flat_field(self.frame(empty_cols=36), self.BG)
        self.assertIn('empty-background', r_['flags'])

    def test_one_colour_field_is_found(self):
        self.assertIn('flat-field', frames.flat_field(self.frame(flat=True), self.BG)['flags'])

    def test_busy_picture_is_clean(self):
        self.assertEqual(frames.flat_field(self.frame(), self.BG)['flags'], [])

    def test_frame_off_the_grid_raises(self):
        with self.assertRaises(ValueError):
            frames.flat_field(Image.new('RGB', (1000, 1000)), self.BG)

    def test_plate_visible_in_frame(self):
        im = Image.new('RGB', (1920, 1080), (0, 0, 0))
        rect = (6, 6, 110, 27)
        x0, y0, x1, y1 = (v * 6 for v in rect)
        im.paste(frames.hex_rgb(P['wood0']), (x0, y0, x1, y1)); im.paste(frames.hex_rgb(P['blue0']), (x0 + 6, y0 + 6, x1 - 6, y1 - 6))
        ok = frames.plate_visible(im, rect, unit=6, fill=P['blue0'], border=P['wood0'])
        self.assertTrue(ok['visible'], ok)
        self.assertFalse(frames.plate_visible(Image.new('RGB', (1920, 1080)), rect, unit=6, fill=P['blue0'], border=P['wood0'])['visible'])


if __name__ == "__main__":
    unittest.main()


class SignBoard(unittest.TestCase):
    def test_plate_over_the_school_board_is_refused_when_the_board_is_the_sign(self):
        from pnkit.pixelart import sets
        def draw(c, s):
            c.sign('ESCOLA', sets.ESCOLA_STREET_BOARD)
            c.plate('Golden · 2026', 'TL', 0.5, 2.5)
        with self.assertRaisesRegex(PlanError, 'overlaps sign'):
            one_shot(checks.CheckedCtx(), draw)

    def test_the_board_constant_matches_the_set(self):
        from pnkit.pixelart import sets
        g = sets.school_street('wide', 'morning', signs=True)
        x0, y0, x1, y1 = sets.ESCOLA_STREET_BOARD
        board = g.cells[(x0, y0)]
        self.assertTrue(all(g.cells.get((x, y)) == board for x in (x0, x1 - 1) for y in (y0, y1 - 1)))
        self.assertNotEqual(g.cells.get((x0 - 1, y0)), board); self.assertNotEqual(g.cells.get((x0, y1)), board)
