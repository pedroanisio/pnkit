"""mesh: tapered-tube geometry and its OBJ-import direction convention."""
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit.mesh import Mesh, tapered_tube, bake_bone


class Tube(unittest.TestCase):
    def test_straight_tube_has_one_ring_per_point(self):
        m = Mesh()
        m.tube([(0, 0, 0), (0, 1, 0), (0, 2, 0)], [1.0, 0.8, 0.5], sides=8)
        self.assertEqual(len(m.v), 3 * 8)
        self.assertEqual(len(m.n), 3 * 8)

    def test_tapered_tube_direction(self):
        """down (the default): grows toward -y in OBJ space, which the engine's fixed OBJ import
        (scene = (100x, -100y, -100z)) turns into +y in scene space — away from the root, the way a
        thigh descends from the hip. up=True is the opposite, for a bone that climbs toward the root's
        head end (pnkit.figure's torso) — see this module's docstring for why that distinction is explicit."""
        down = tapered_tube(0.4, 0.1, 0.05, segs=4)
        up = tapered_tube(0.4, 0.1, 0.05, segs=4, up=True)
        ys_down = [v[1] for v in down.v]
        ys_up = [v[1] for v in up.v]
        self.assertAlmostEqual(min(ys_down), -0.4, places=6)
        self.assertAlmostEqual(max(ys_down), 0.0, places=6)
        self.assertAlmostEqual(min(ys_up), 0.0, places=6)
        self.assertAlmostEqual(max(ys_up), 0.4, places=6)

    def test_tapered_tube_radius_at_ends(self):
        import math
        m = tapered_tube(1.0, 0.2, 0.05, segs=10, bulge=0.0)
        # first ring (y=0) at r0, last ring (y=-length) at r1 — radius is the vertex's distance from the
        # tube's own axis (x, z), since bulge=0 leaves no deviation from the base taper
        r_first = math.hypot(m.v[0][0], m.v[0][2])
        r_last = math.hypot(m.v[-1][0], m.v[-1][2])
        self.assertAlmostEqual(r_first, 0.2, places=4)
        self.assertAlmostEqual(r_last, 0.05, places=4)

    def test_bake_bone_writes_and_caches(self):
        with tempfile.TemporaryDirectory() as d:
            name1 = bake_bone(d, "b1", 0.3, 0.1, 0.08, seed=1)
            path = os.path.join(d, f"{name1}.obj")
            self.assertTrue(os.path.exists(path))
            mtime = os.path.getmtime(path)
            name2 = bake_bone(d, "b1", 0.3, 0.1, 0.08, seed=1)   # same (out_dir, name): cached, not rewritten
            self.assertEqual(name1, name2)
            self.assertEqual(os.path.getmtime(path), mtime)


if __name__ == "__main__":
    unittest.main()
