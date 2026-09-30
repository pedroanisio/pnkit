"""camera: safe-rect clamp, verify(), beat references through an injected resolver, hold cues."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pnkit
from pnkit.camera import Cam


def inside(cam, t, rect):
    cx, cy, z = cam.at(t)
    vx0, vx1 = cx - (cam.CX - cam.MX) / z, cx + (cam.CX - cam.MX) / z
    vy0, vy1 = cy - (cam.CY - cam.MY) / z, cy + (cam.CY - cam.MY) / z
    x0, y0, x1, y1 = rect
    return vx0 <= x0 + 1e-6 and x1 <= vx1 + 1e-6 and vy0 <= y0 + 1e-6 and y1 <= vy1 + 1e-6


class Clamp(unittest.TestCase):
    def setUp(self):
        self.doc = pnkit.Doc(1920, 1080)

    def test_push_in_is_limited_by_the_safe_rect(self):
        safe = (400, 300, 1500, 800)
        cam = Cam(self.doc, "t", [(1.0, 960, 540, 1.0), (5.0, 300, 300, 1.8)], 0, 10, safe=[(0, safe)])
        cx, cy, z = cam.clamp(5.0, 300, 300, 1.8)
        self.assertLess(z, 1.8)                                   # zoom capped so the rect's width fits
        self.assertAlmostEqual(z, (1920 - 300) / 1100 / 1.022, places=6)
        self.assertTrue(inside(cam, 9.0, safe))
        self.assertEqual(cam.verify(), [])

    def test_a_rect_wider_than_the_frame_zooms_out(self):
        safe = (0, 0, 1920, 1080)
        cam = Cam(self.doc, "wide", [(0.5, 960, 540, 1.0)], 0, 6, safe=[(0, safe)])
        self.assertLess(cam.keys[-1][3], 1.0)
        self.assertEqual(cam.verify(), [])

    def test_default_safe_rect(self):
        cam = Cam(self.doc, "d", [(0.5, 960, 540, 1.2)], 0, 6)
        self.assertEqual(cam.safe_at(3.0), (150, 150, 1770, 930))
        self.assertEqual(cam.verify(), [])

    def test_changing_safe_rects(self):
        a, b = (200, 200, 1720, 880), (900, 380, 1700, 880)
        cam = Cam(self.doc, "c", [(0.5, 960, 540, 1.0), (6.0, 1330, 630, 1.4), (14.0, 960, 540, 1.0)], 0, 20,
                  safe=[(0, a), (6.0, b), (14.0, a)])
        self.assertEqual(cam.safe_at(7.0), b); self.assertEqual(cam.safe_at(15.0), a)
        self.assertEqual(cam.verify(), [])

    def test_verify_reports_a_breach(self):
        cam = Cam(self.doc, "bad", [(0.5, 960, 540, 1.0)], 0, 8)
        cam.keys = [(k[0], k[1], k[2], 2.5) for k in cam.keys]      # force a push-in past the safe rect
        bad = cam.verify()
        self.assertTrue(bad)
        self.assertEqual(bad[0][0], "bad")
        self.assertGreater(bad[0][2], 6)


class References(unittest.TestCase):
    def setUp(self):
        self.doc = pnkit.Doc()
        self.beats = {"intro": 2.0, "point": 6.5}

    def test_beats_and_offsets(self):
        cam = Cam(self.doc, "r", [("intro", 960, 540, 1.0), (("point", -0.5), 1000, 540, 1.05)], 0, 12, resolve=self.beats.__getitem__)
        self.assertEqual([c[0] for c in cam.cues], [2.0, 6.0])

    def test_reference_without_resolver(self):
        with self.assertRaises(TypeError):
            Cam(self.doc, "r", [("intro", 960, 540, 1.0)], 0, 12)

    def test_hold_stops_the_drift(self):
        cam = Cam(self.doc, "h", [(1.0, 960, 540, 1.0, "hold"), (8.0, 1000, 540, 1.05)], 0, 14)
        k = cam.keys
        self.assertEqual(k[1][1:], k[2][1:])                          # held: same framing until the next move

    def test_open_group(self):
        cam = Cam(self.doc, "act", [(1.0, 960, 540, 1.0)], 0, 5)
        x = cam.open()
        self.assertTrue(x.startswith('<group id="cam2d-act" anchorX="960" anchorY="540" x="960" y="540"><animate property="x">'))
        self.assertTrue(cam.open().startswith('<group id="cam2d-act-2"'))
        self.assertEqual(Cam.CLOSE, "</group>")


if __name__ == "__main__":
    unittest.main()
