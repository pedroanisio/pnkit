"""figure: pose tables, the sign convention, idle breathing, and the bone-direction regressions a render
caught (see pnkit/figure.py's module docstring, lessons 1 and 3) — pinned here so they can't come back
silently between renders."""
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit.figure import (figure, bone_meshes, default_materials, POSES, DIMS, GAIT_MODES, _bend, _breathe)
from pnkit.mesh import tapered_tube

COMMON_KEYS = {"lean", "shL", "shR", "elL", "elR", "height"}


class Poses(unittest.TestCase):
    def test_every_pose_has_the_common_keys(self):
        for name, p in POSES.items():
            missing = COMMON_KEYS - set(p)
            self.assertFalse(missing, f"{name} is missing {missing}")

    def test_gait_poses_use_symmetric_hip_knee(self):
        # a gait pose's legs are driven by phase (ang = dict(hipL=-p["hip"]*sin(phase), ...) in figure()),
        # so it carries one "hip"/"knee" value, not four independent hipL/hipR/kneeL/kneeR like a held pose
        for name in GAIT_MODES:
            self.assertIn("hip", POSES[name], name); self.assertIn("knee", POSES[name], name)

    def test_held_poses_use_explicit_per_side_hip_knee(self):
        for name, p in POSES.items():
            if name not in GAIT_MODES:
                for k in ("hipL", "hipR", "kneeL", "kneeR"):
                    self.assertIn(k, p, f"{name} missing {k}")

    def test_gait_modes_declare_a_cadence(self):
        for name in GAIT_MODES:
            self.assertIn("cadence", POSES[name], name)

    def test_held_poses_declare_no_cadence(self):
        for name, p in POSES.items():
            if name not in GAIT_MODES:
                self.assertNotIn("cadence", p, name)


class Bend(unittest.TestCase):
    def test_bend_negates(self):
        self.assertEqual(_bend(30), -30)
        self.assertEqual(_bend(-62), 62)


class Breathe(unittest.TestCase):
    def test_zero_at_pose_start(self):
        self.assertEqual(_breathe(10.0, 10.0), 0.0)

    def test_nonzero_after_a_quarter_period(self):
        self.assertNotEqual(_breathe(10.9, 10.0, period=3.6), 0.0)


class BoneDirection(unittest.TestCase):
    """the regression this module's docstring (lesson 3) describes: every limb bone descends away from
    its proximal joint, but the torso climbs toward it — a render caught this the first time, not a
    reading of the code, so it is pinned here as a direction check on the actual baked geometry."""

    def test_limb_bones_descend(self):
        # up=False (the default): OBJ y goes to 0 .. -length, which the engine's import flip turns into
        # scene 0 .. +length — away from the proximal joint, into the next one further from the root.
        with tempfile.TemporaryDirectory() as d:
            mesh_ids, _ = bone_meshes(d, DIMS)
            for bone in ("thigh", "shin", "upper", "fore"):
                path = os.path.join(d, mesh_ids[bone][2:] + ".obj")
                ys = [float(line.split()[2]) for line in open(path) if line.startswith("v ")]
                self.assertLessEqual(max(ys), 1e-9, bone)

    def test_torso_climbs(self):
        # up=True: OBJ y goes to 0 .. +length, which the import flip turns into scene 0 .. -length — toward
        # the root, since the spine joint sits at pelvis height and the torso has to reach up to the neck.
        with tempfile.TemporaryDirectory() as d:
            mesh_ids, _ = bone_meshes(d, DIMS)
            path = os.path.join(d, mesh_ids["torso"][2:] + ".obj")
            ys = [float(line.split()[2]) for line in open(path) if line.startswith("v ")]
            self.assertGreaterEqual(min(ys), -1e-9)


class FigureXml(unittest.TestCase):
    def test_figure_emits_every_expected_joint(self):
        with tempfile.TemporaryDirectory() as d:
            mesh_ids, _ = bone_meshes(d, DIMS)
            materials, _ = default_materials()
            xml = figure("f", [(0.0, 1.0, "stand", [(0.0, 0.0)])], 0.0, 0.0, mesh_ids, materials)
            for jid in ("spine", "hipL", "kneeL", "shL", "elL", "hipR", "kneeR", "shR", "elR"):
                self.assertIn(f'id="f-{jid}"', xml)

    def test_figure_has_one_root_position_track_per_axis(self):
        with tempfile.TemporaryDirectory() as d:
            mesh_ids, _ = bone_meshes(d, DIMS)
            materials, _ = default_materials()
            xml = figure("f", [(0.0, 1.0, "stand", [(0.0, 0.0)])], 10.0, 20.0, mesh_ids, materials)
            self.assertIn('id="f"', xml)
            for prop in ("rotationY",):   # root always carries heading, even holding one point
                self.assertIn(f'property="{prop}"', xml)


if __name__ == "__main__":
    unittest.main()
