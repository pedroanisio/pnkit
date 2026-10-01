"""pnkit.figure — an articulated 3D figure: a joint hierarchy driven by named poses (walk, run, crouch,
kneel-fire, prone, stand), following a ground path at a cadence set by the pose, built from tapered-tube
bones (pnkit.mesh) instead of uniform capsules so it holds up closer to camera.

Generalized from v014 "Bayonet Charge, 2011"'s film/figures.py (a desert-camo rifle soldier); credit and
lessons 1, 2 and 5 below are pals-b2's, from building and shipping that film. Lessons 3 and 4 are from
porting it here — both only showed up on a render, never on a reading of the code, which is why every one
of these is written as "what a render catches", not just "what to remember".

1. Sign convention (pals-b2, v014): the engine's positive rotationX swings a hanging limb's end *forward*
   (+z). v014's pose tables already have this baked in per joint, by empirical tuning, not a clean rule (a
   given table value is not uniformly "the angle" or uniformly "its negation" — whichever sign made that
   joint render right is the one it got). `_bend()` is the one place that negates every value for the
   engine; copy a v014 table's signs as they are, never re-derive them under a tidier scheme — that re-
   derivation is exactly what broke this port the first time. If knees start bending forward on a side-view
   render, check this.
2. Geometry over gait (pals-b2, v014): at mid-distance a rigid-capsule rig reads fine; close up it reads
   as a mannequin. Tapered, slightly-bulged bones (pnkit.mesh.tapered_tube) and joints sized to match their
   bone's end radius matter more than animation detail — spend quality budget there first.
3. A bone's own direction is not implied by its joint's position (found porting this module, not in v014,
   which never had the question — its capsules were centred, with the direction implicit in which end the
   centring put closer to zero). Every limb bone here descends *away* from the root (hip-to-knee, shoulder-
   to-elbow); the torso is the one bone that climbs *toward* it, because the spine joint sits at pelvis
   height — level with the hip joints, which share its root — and has to reach up to the neck from there.
   Get this backward and the torso renders into the legs while the arms, still hanging correctly from a
   shoulder with nothing visibly holding it up, read as if they're reaching for the sky. See pnkit.mesh's
   `tapered_tube(..., up=)`.
4. v014's own pose angles are tuned for a rifle carried across the chest — even "stand" holds both elbows
   bent some 90 degrees combined. Correct for that figure, wrong copied verbatim into a generic default:
   dropped in unmodified, an unarmed figure reads as holding an invisible rifle. This module's own POSES
   are its own, not v014's, sized for empty hands; a caller posing a figure for a carried object should
   pass its own `poses` with bent elbows, as v014 did.
5. Held poses were previously frozen (no change at all between entering a pose and leaving it unless the
   pose had a gait cadence). `_breathe()` adds a slow chest-rise idle cycle to every held pose so a prone or
   kneeling figure doesn't read as a statue in a long shot.

A figure is driven by segments: (t0, t1, mode, path) where mode is a key into `poses` (stand, walk, run,
crouch, kneel-fire, prone by default) and path is the ground track [(x, z), ...] walked at constant speed
over [t0, t1]; between segments the last pose holds. Units: 100 = 1 scene metre, y down (pnkit.mesh's OBJ
bones import correctly under that convention — see its docstring).
"""
import math, os

from .mesh import bake_bone

# ---------------------------------------------------------------------- defaults: dims, poses, materials
DIMS = dict(pelvis_h=95, torso_h=52, thigh=46, shin=46, upper=30, fore=28, hip_w=11, sh_w=21, arm_roll=22,
            r_hip=10.5, r_knee=8.6, r_shoulder=9, r_elbow=6.6, r_ankle=7.0, r_wrist=5.0,
            r_thigh_top=9.5, r_thigh_bot=7.8, r_shin_top=7.6, r_shin_bot=5.8,
            r_upper_top=7.2, r_upper_bot=6.0, r_fore_top=6.0, r_fore_bot=4.6, r_torso=17.0)

# joint angles in degrees, in v014's own table convention (the signs are empirically tuned per joint, not
# a clean rule — _bend() negates the lot uniformly; see this module's docstring, lesson 1 — keep that part).
# The magnitudes below are this module's own, not v014's: v014's soldier carries a rifle across the chest,
# so its "stand" already holds both elbows bent ~90 degrees combined — correct for that figure, wrong as a
# generic default (verified empirically: dropped in unmodified, an unarmed figure reads as holding an
# invisible rifle, elbows jutting out with nothing to explain why). These instead hang the arms naturally;
# a caller posing a figure for a carried object should pass its own `poses` with bent elbows, as v014 did.
# cadence: gait cycles/second; arm_swing/twist: degrees of counter-swing/-twist, added for gait realism.
POSES = {
    "stand":      dict(lean=2, hipL=0, hipR=0, kneeL=0, kneeR=0, shL=-6, shR=-5, elL=-10, elR=-10, height=0),
    "walk":       dict(lean=6, hip=22, knee=25, shL=-8, shR=-8, elL=-18, elR=-18, bob=3, cadence=1.8, height=0,
                        arm_swing=22, twist=8),
    "run":        dict(lean=16, hip=38, knee=65, shL=-14, shR=-14, elL=-55, elR=-55, bob=6, cadence=2.9, height=-4,
                        arm_swing=38, twist=14),
    "crouch":     dict(lean=30, hipL=-70, hipR=-70, kneeL=110, kneeR=110, shL=-30, shR=-30, elL=-70, elR=-70, height=38),
    "kneel-fire": dict(lean=8, hipL=-85, hipR=10, kneeL=90, kneeR=100, shL=-60, shR=-65, elL=-40, elR=-55, height=40),
    "prone":      dict(lean=85, hipL=0, hipR=0, kneeL=10, kneeR=10, shL=-100, shR=-110, elL=-60, elR=-70, height=78),
}
GAIT_MODES = {"walk", "run"}   # poses sampled at `cadence` rather than held


def f(x): return f"{x:.2f}".rstrip("0").rstrip(".")


def _keys(prop, pairs, ease="sine-in-out"):
    if not pairs:
        return ""
    return f'<animate property="{prop}">' + "".join(f'<key time="{f(t)}" value="{f(v)}" interpolation="{ease}"/>' for t, v in pairs) + "</animate>"


def _bend(deg):
    """flexion-positive -> the engine's rotationX. See this module's docstring, lesson 1. One call site:
    if this is ever inlined again instead of called, the next pose edit will silently bend joints backward."""
    return -deg


def _breathe(t, t0, amplitude=1.6, period=3.6):
    """a slow chest-rise cycle for held poses (lesson 3): 0 at the pose's own start, so entering a pose
    never pops, settling into a steady sine after about a quarter period."""
    u = min(1.0, (t - t0) / (period * 0.25))
    return amplitude * u * math.sin(2 * math.pi * (t - t0) / period)


# ---------------------------------------------------------------------- bones: tapered meshes, once per shape
def _bone_mesh(assets_dir, name, length, r0, r1, seed, up=False):
    base = bake_bone(assets_dir, name, length / 100.0, r0 / 100.0, r1 / 100.0, bulge=0.12, seed=seed, up=up)
    return base


def bone_meshes(assets_dir, dims=DIMS, fid="fig"):
    """bake this figure's limb and torso bones (shared across every instance with the same dims — bake
    once, reference many times) and the <mesh> asset lines for them. Returns (mesh_ids, asset_xml).

    Every bone's proximal end (its r0, at the joint nearer the root) sits at that joint's own position with
    no offset; the joint hierarchy's own y-offsets (hip-to-knee, shoulder-to-elbow, spine-to-neck) carry it
    to the next joint. Limb bones grow away from the root (up=False); the torso is the one bone that grows
    toward it (up=True) — the spine joint sits at pelvis height, level with the hip joints on the same root,
    and the torso climbs from there to the neck. See tapered_tube's docstring for why that distinction has
    to be explicit, not inferred."""
    d = dims
    # (length, r0 at the proximal end, r1 at the distal end, up)
    specs = {
        "thigh": (d["thigh"], d["r_thigh_top"], d["r_thigh_bot"], False),
        "shin": (d["shin"], d["r_shin_top"], d["r_shin_bot"], False),
        "upper": (d["upper"], d["r_upper_top"], d["r_upper_bot"], False),
        "fore": (d["fore"], d["r_fore_top"], d["r_fore_bot"], False),
        "torso": (d["torso_h"], d["r_torso"], d["r_torso"] * 0.78, True),      # wide at the waist, narrower at the neck
    }
    ids, assets = {}, []
    for bone, (length, r0, r1, up) in specs.items():
        name = f"bone-{bone}-{round(length)}-{round(r0 * 10)}-{round(r1 * 10)}"
        mesh_id = _bone_mesh(assets_dir, name, length, r0, r1, seed=hash(bone) & 0xFFFF, up=up)
        ids[bone] = f"m-{mesh_id}"
        assets.append(f'<mesh id="m-{mesh_id}" src="assets/{mesh_id}.obj" format="obj"/>')
    return ids, assets


def default_materials():
    """a plain, undyed figure (cream uniform, mid-grey gear) — a starting point, not a uniform.

    Returns (ids, xml): `ids` is {key: material id}, the shape `figure()`'s `materials` parameter takes;
    `xml` is the <material> tags to register once in the document (e.g. `doc.materials.extend(xml)`). Build
    your own look the same way: your own `ids` dict (skin, body, gear, metal) and matching `<material>` tags."""
    xml = [
        '<material id="fig-skin" baseColor="#C89A78" roughness="0.9"/>',
        '<material id="fig-body" baseColor="#D8D2C4" roughness="0.9"/>',
        '<material id="fig-gear" baseColor="#5E5A45" roughness="0.85"/>',
        '<material id="fig-metal" baseColor="#1E1F1E" metallic="0.4" roughness="0.5"/>',
    ]
    ids = {"skin": "fig-skin", "body": "fig-body", "gear": "fig-gear", "metal": "fig-metal"}
    return ids, xml


# ---------------------------------------------------------------------- the rig
def figure(fid, segments, x0, z0, mesh_ids, materials, heading0=0.0, dims=DIMS, poses=None,
           head_accessory=None, chest_accessory=None, extra_y=None):
    """XML of one figure.

    segments: [(t0, t1, mode, path)], mode a key into `poses` (default POSES), path a list of (x, z) walked
        at constant speed over [t0, t1]; between segments the figure holds the previous pose.
    mesh_ids: from bone_meshes() (or your own, same shape) — bake once per document, pass to every instance.
    materials: a {skin, body, gear, metal} dict of material *ids* — the `ids` half of default_materials()'s
        return, or your own; register the matching <material> tags in the document once, not per instance.
    head_accessory, chest_accessory: optional extra XML (a helmet; a carried rifle or tool), appended as
        children of `{fid}-head` / `{fid}-spine` respectively — receive no formatting, write them with that
        parent id (the spine joint sits at the base of the neck, chest height, facing +z).
    extra_y: [(t, dy)] extra vertical offset keys (stepping down into a ditch, a fall).
    """
    poses = POSES if poses is None else poses
    d = dims
    T0 = segments[0][0]; T1 = segments[-1][1]
    times = []
    for (s0, s1, mode, _) in segments:
        p = poses[mode]
        step = 1 / (4 * p["cadence"]) if "cadence" in p else 0.4   # 0.4 s: enough for _breathe to read, lesson 3
        k = 0
        while s0 + k * step < s1 - 1e-6:
            times.append(s0 + k * step); k += 1
        times.append(s1)
    if extra_y:
        times += [t for t, _ in extra_y]
    times = sorted(set(round(x, 4) for x in times if T0 - 1e-6 <= x <= T1 + 1e-6))

    samples = []
    pos, head = (x0, z0), heading0
    for t in times:
        seg = next((s for s in segments if s[0] <= t <= s[1]), None)
        if seg is None:
            seg = max((s for s in segments if s[1] <= t), key=lambda s: s[1])
            mode, u, path = seg[2], 1.0, seg[3]
        else:
            mode, path = seg[2], seg[3]; u = (t - seg[0]) / max(1e-6, seg[1] - seg[0])
        if path and len(path) > 1:
            L = [0.0]
            for a, b in zip(path, path[1:]):
                L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
            s = u * L[-1]; k = max(i for i in range(len(L)) if L[i] <= s + 1e-9); k = min(k, len(path) - 2)
            w = (s - L[k]) / max(1e-6, L[k + 1] - L[k])
            pos = (path[k][0] + w * (path[k + 1][0] - path[k][0]), path[k][1] + w * (path[k + 1][1] - path[k][1]))
            head = math.degrees(math.atan2(path[k + 1][0] - path[k][0], path[k + 1][1] - path[k][1]))
        samples.append((t, mode, pos, head, t - seg[0], seg[0]))

    P = {j: [] for j in ("lean", "hipL", "hipR", "kneeL", "kneeR", "shL", "shR", "elL", "elR", "spin", "y", "x", "z", "yaw")}
    for t, mode, (x, z), head, local, t0 in samples:
        p = poses[mode]
        if "cadence" in p:
            ph = 2 * math.pi * p["cadence"] * local
            s1 = math.sin(ph)
            swing = p.get("arm_swing", 0.0) * s1            # arms counter-swing the opposite-side leg
            ang = dict(hipL=-p["hip"] * s1, hipR=p["hip"] * s1,
                       kneeL=p["knee"] * max(0, math.sin(ph + 1.2)), kneeR=p["knee"] * max(0, -math.sin(ph + 1.2)),
                       shL=p["shL"] - swing, shR=p["shR"] + swing, elL=p["elL"], elR=p["elR"], lean=p["lean"])
            dy = -p["bob"] * abs(math.cos(ph)) + p["height"]
            spin = p.get("twist", 0.0) * s1                 # shoulders counter-rotate the hips (torso twist)
        else:
            ang = {k: p[k] for k in ("hipL", "hipR", "kneeL", "kneeR", "shL", "shR", "elL", "elR", "lean")}
            dy = p["height"] + _breathe(t, t0)
            spin = 0.0
        for k, v in ang.items():
            P[k].append((t, _bend(v)))
        P["spin"].append((t, spin))
        P["y"].append((t, -d["pelvis_h"] + dy)); P["x"].append((t, x)); P["z"].append((t, z)); P["yaw"].append((t, head))

    def _reduce(pairs, tol):
        if len(pairs) < 3:
            return pairs
        out = [pairs[0]]
        for i in range(1, len(pairs) - 1):
            (t0, v0), (t1, v1), (t2, v2) = out[-1], pairs[i], pairs[i + 1]
            if abs(v0 + (v2 - v0) * (t1 - t0) / max(1e-9, t2 - t0) - v1) > tol:
                out.append(pairs[i])
        return out + [pairs[-1]]

    ROOT = {"x": 0.5, "z": 0.5, "y": 0.4, "yaw": 0.3}
    lin = lambda prop, key: (_keys(prop, _reduce(P[key], ROOT[key]), "linear") if key in ROOT
                             else _keys(prop, _reduce(P[key], 0.3), "sine-in-out"))

    o = []
    J = lambda jid, parent, x, y, z, extra="": o.append(
        f'<object3D id="{fid}-{jid}" primitive="sphere" radius="1" x="{f(x)}" y="{f(y)}" z="{f(z)}" parent="{parent}" opacity="0">{extra}</object3D>')
    Ball = lambda bid, parent, x, y, z, r, mat: o.append(
        f'<object3D id="{fid}-{bid}" primitive="sphere" x="{f(x)}" y="{f(y)}" z="{f(z)}" radius="{f(r)}" parent="{parent}" material="{mat}" castShadow="true" receiveShadow="true"/>')
    Bone = lambda bid, parent, mesh_id, mat: o.append(
        f'<object3D id="{fid}-{bid}" primitive="mesh" mesh="{mesh_id}" x="0" y="0" z="0" parent="{parent}" material="{mat}" castShadow="true" receiveShadow="true"/>')
    Foot = lambda bid, parent, y, r, mat: o.append(
        f'<object3D id="{fid}-{bid}" primitive="box" x="0" y="{f(y + r * 0.3)}" z="{f(r * 0.9)}" width="{f(r * 1.3)}" height="{f(r * 1.1)}" depth="{f(r * 2.8)}" '
        f'bevel="{f(r * 0.25)}" parent="{parent}" material="{mat}" castShadow="true" receiveShadow="true"/>')

    skin, body, gear = materials["skin"], materials["body"], materials["gear"]
    o.append(f'<object3D id="{fid}" primitive="sphere" radius="1" x="{f(x0)}" y="{f(-d["pelvis_h"])}" z="{f(z0)}" opacity="0">'
             f'{lin("x", "x")}{lin("z", "z")}{lin("y", "y")}{lin("rotationY", "yaw")}</object3D>')
    J("spine", fid, 0, 0, 0, lin("rotationX", "lean") + lin("rotationY", "spin"))          # lean + torso counter-twist
    Bone("torso", f"{fid}-spine", mesh_ids["torso"], body)
    Ball("neck", f"{fid}-spine", 0, -d["torso_h"], 0, d["r_torso"] * 0.42, skin)
    Ball("head", f"{fid}-spine", 0, -d["torso_h"] - d["r_torso"] * 0.9, 0, d["r_torso"] * 0.6, skin)
    if head_accessory:
        o.append(head_accessory)
    if chest_accessory:
        o.append(chest_accessory)
    for side, sx in (("L", -1), ("R", 1)):
        J(f"hip{side}", fid, sx * d["hip_w"], 0, 0, lin("rotationX", f"hip{side}"))
        Ball(f"hipball{side}", f"{fid}-hip{side}", 0, 0, 0, d["r_hip"], body)
        Bone(f"thigh{side}", f"{fid}-hip{side}", mesh_ids["thigh"], body)
        J(f"knee{side}", f"{fid}-hip{side}", 0, d["thigh"], 0, lin("rotationX", f"knee{side}"))
        Ball(f"kneeball{side}", f"{fid}-knee{side}", 0, 0, 0, d["r_knee"], body)
        Bone(f"shin{side}", f"{fid}-knee{side}", mesh_ids["shin"], body)
        Ball(f"ankle{side}", f"{fid}-knee{side}", 0, d["shin"], 0, d["r_ankle"], gear)
        Foot(f"foot{side}", f"{fid}-knee{side}", d["shin"], d["r_ankle"], gear)
        # the shoulder's own Z-roll, before the animated bend (lesson, found empirically — see this
        # module's docstring on `arm_roll`): without it, shoulder + elbow flexion add up in the same
        # bending plane and a standing arm's ~90 degrees of cumulative bend points it at the camera
        # instead of hanging at the figure's side. Rolling the shoulder first tips that plane so the
        # same two angles compose into a natural hang.
        o.append(f'<object3D id="{fid}-shr{side}" primitive="sphere" radius="1" x="{f(sx * d["sh_w"])}" y="{f(-d["torso_h"] + 6)}" z="0" '
                 f'parent="{fid}-spine" rotation="{f(-sx * d["arm_roll"])}" opacity="0"></object3D>')
        J(f"sh{side}", f"{fid}-shr{side}", 0, 0, 0, lin("rotationX", f"sh{side}"))
        Ball(f"shball{side}", f"{fid}-sh{side}", 0, 0, 0, d["r_shoulder"], body)
        Bone(f"upper{side}", f"{fid}-sh{side}", mesh_ids["upper"], body)
        J(f"el{side}", f"{fid}-sh{side}", 0, d["upper"], 0, lin("rotationX", f"el{side}"))
        Ball(f"elball{side}", f"{fid}-el{side}", 0, 0, 0, d["r_elbow"], body)
        Bone(f"fore{side}", f"{fid}-el{side}", mesh_ids["fore"], body)
        Ball(f"hand{side}", f"{fid}-el{side}", 0, d["fore"], 0, d["r_wrist"], skin)
    return "\n".join(o)
