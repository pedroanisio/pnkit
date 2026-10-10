"""pnkit.pixelart.plan: the plan check (from Lula work/art3/v3/check_plan.py), as functions on data."""
import os, sys, unittest
LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LIB)
from pnkit.pixelart import plan

ROWS = """\
| `s01a_rua`<br>0.00-3.00 s (3.00 s)<br>f0-f72 | STREET | boy | no props<br>SIGN “PADARIA” @ shop, x 120-170, y 40-48 | “São Paulo · 1958” TL over sky; reserved x 6-110, y 6-27 (1 line); 0.50-2.50 s | +0.4 walk |
| `s01b_casa`<br>3.00-5.00 s (2.00 s)<br>f72-f120 | HOUSE | mother | no signs | none | hold |
| `s02a_mesa`<br>5.00-10.00 s (5.00 s)<br>f120-f240 | TABLE | family | no signs | “Hoje” TR; reserved x 210-314, y 6-27 (1 line); 5.50-7.00 s<br>“Amanhã” TR; reserved x 210-314, y 6-27 (1 line); 6.50-9.00 s | hold |
"""
TIMINGS = {"scenes": [{"n": 1, "slot_start": 0.0, "slot_end": 5.0, "plate_read_s": 1.0},
                      {"n": 2, "slot_start": 5.0, "slot_end": 10.0}]}


def built():
    return [
        dict(name='s01a_rua', scene=1, start=0.0, end=3.0, signs=[dict(text='PADARIA', rect=[120, 40, 170, 48])],
             plates=[dict(text='São Paulo · 1958', slot='TL', rect=[6, 6, 110, 27], start=0.5, end=2.5, lines=1)], figures=[], notes=[]),
        dict(name='s01b_casa', scene=1, start=3.0, end=5.0, signs=[], plates=[], figures=[], notes=[]),
    ]


class Parse(unittest.TestCase):
    def test_rows_signs_and_plates(self):
        p = plan.parse_plan(ROWS)
        self.assertEqual(sorted(p), ['s01a_rua', 's01b_casa', 's02a_mesa'])
        a = p['s01a_rua']
        self.assertEqual((a['start'], a['end'], a['scene']), (0.0, 3.0, 1))
        self.assertEqual(a['signs'], [dict(text='PADARIA', rect=[120, 40, 170, 48])])
        self.assertEqual(a['plates'][0]['window'], [0.5, 2.5]); self.assertEqual(a['plates'][0]['rect'], [6, 6, 110, 27])


class PlanOnly(unittest.TestCase):
    def test_stacked_plates_in_one_slot(self):
        errs = plan.check_plan_only(plan.parse_plan(ROWS))
        self.assertEqual(len(errs), 1); self.assertIn('plates overlap in slot TR', errs[0])

    def test_plan_against_timings_slots(self):
        errs = plan.check_plan_slots(plan.parse_plan(ROWS), TIMINGS)
        self.assertEqual(errs, [])
        bad = {"scenes": [{"n": 1, "slot_start": 0.0, "slot_end": 4.0}, {"n": 2, "slot_start": 4.0, "slot_end": 10.0}]}
        self.assertTrue(any('scene 01' in e for e in plan.check_plan_slots(plan.parse_plan(ROWS), bad)))


class Built(unittest.TestCase):
    def test_built_scene_matches(self):
        errs, warns = plan.check_built(built(), plan.parse_plan(ROWS), TIMINGS, scenes=[1])
        self.assertEqual(errs, [], errs)

    def test_time_off_and_plate_missing(self):
        b = built(); b[0]['end'] = 3.2; b[1]['start'] = 3.2; b[0]['plates'] = []
        errs, _ = plan.check_built(b, plan.parse_plan(ROWS), TIMINGS, scenes=[1])
        self.assertTrue(any('time 0.000-3.200' in e for e in errs), errs)
        self.assertTrue(any("plate 'São Paulo · 1958' missing" in e for e in errs), errs)

    def test_missing_shot_and_low_sole(self):
        b = built()[:1]; b[0]['figures'] = [dict(kind='boy', rect=[10, 100, 30, 150], start=0, end=3)]
        errs, _ = plan.check_built(b, plan.parse_plan(ROWS), TIMINGS, scenes=[1])
        self.assertTrue(any('shots differ' in e for e in errs))
        self.assertTrue(any('soles at row 149' in e for e in errs))

    def test_plate_read_time(self):
        b = built(); b[0]['plates'][0]['end'] = 0.9
        errs, _ = plan.check_built(b, plan.parse_plan(ROWS.replace('0.50-2.50 s', '0.50-0.90 s')), TIMINGS, scenes=[1])
        self.assertTrue(any('plate_read_s' in e for e in errs), errs)
        self.assertTrue(any('0.3 s x 4 tokens' in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main()
