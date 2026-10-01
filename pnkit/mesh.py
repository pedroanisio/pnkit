"""pnkit.mesh — baked OBJ meshes for geometry no native primitive covers: tapered tubes along a 3D
polyline (limb bones, branches, cables, roots — anything that narrows along its length).

The engine's `capsule` primitive is a single uniform radius; a hand or a thigh drawn from one looks like
a mannequin's rod. A tapered tube is a real mesh instead, baked once to `assets/*.obj` and referenced by
`<object3D primitive="mesh" mesh="...">`, so the cost is a one-time bake plus a normal mesh draw — not a
per-frame cost, and not a change to how its parent object3D is animated (it still rotates on its own
keyframes exactly as a primitive would). Pure standard library (plain 3-tuples, no numpy): baking is a
one-off, offline step, not a per-frame one, so there is nothing here that needs it.

OBJ convention (RS-ENGINE-PRODUCTION-GUIDE, confirmed against film/world.py and film/trees.py in v014):
Y-up, metres; the scene imports a mesh as (100*X, -100*Y, -100*Z) — 1 OBJ metre = 100 scene units and OBJ
+Y (up) becomes scene -Y. `tapered_tube` bakes *down* OBJ -Y (0 to -L), which after that flip lands at
scene +Y (0 to +100*L): the direction a bone descends from a proximal joint (y=0) to its distal one
(y=+length in scene units, this module's convention — "down" the limb, not "up" out of the ground, which
is what a tree wants and why trees.py's own trunk grows the other way). Caught empirically: baking +Y first
produced bones pointing away from their child joint, not into it — a render is how that showed up, not a
reading of this docstring, so if bones ever look inverted again, check this sign before anything else.
"""
import math, os, random

SIDES = 10


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _scale(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _norm(a): return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
def _unit(a, eps=1e-9):
    n = _norm(a) + eps
    return (a[0] / n, a[1] / n, a[2] / n)


class Mesh:
    """a triangle soup built from tapered tubes; write() emits it as OBJ (Y-up metres, per this module's
    docstring). Shared by anything that bakes tube geometry (limb bones, branches, cables)."""

    def __init__(self):
        self.v, self.n, self.f = [], [], []

    def tube(self, pts, radii, sides=SIDES, cap_ends=False):
        """a tapered tube through pts (N x 3, metres) with per-point radii (N, metres). Open-ended unless
        cap_ends: a limb bone's ends sit inside a joint sphere and never need a cap; a free-standing tube does."""
        pts = [tuple(p) for p in pts]; base = len(self.v)
        for i, (p, r) in enumerate(zip(pts, radii)):
            d = _unit(_sub(pts[min(i + 1, len(pts) - 1)], pts[max(i - 1, 0)]))
            a = (1.0, 0, 0) if abs(d[0]) < 0.9 else (0, 0, 1.0)
            u = _unit(_cross(d, a)); w = _cross(d, u)
            for k in range(sides):
                t = 2 * math.pi * k / sides
                nrm = _add(_scale(u, math.cos(t)), _scale(w, math.sin(t)))
                self.v.append(_add(p, _scale(nrm, r))); self.n.append(nrm)
        for i in range(len(pts) - 1):
            for k in range(sides):
                a = base + i * sides + k; b = base + i * sides + (k + 1) % sides
                self.f.append((a, a + sides, b)); self.f.append((b, a + sides, b + sides))
        if cap_ends:
            self._cap(base, radii[0] > 0, pts[0], _sub(pts[1], pts[0]), sides, inward=True)
            self._cap(len(self.v) - sides, radii[-1] > 0, pts[-1], _sub(pts[-1], pts[-2]), sides, inward=False)

    def _cap(self, ring0, nonzero, center, axis, sides, inward):
        if not nonzero:
            return
        ci = len(self.v); self.v.append(center); self.n.append(_scale(_unit(axis), -1))
        for k in range(sides):
            a, b = ring0 + k, ring0 + (k + 1) % sides
            self.f.append((ci, b, a) if inward else (ci, a, b))

    def write(self, path, header="baked by pnkit.mesh"):
        with open(path, "w") as fh:
            fh.write(f"# {header}\n")
            fh.write("".join(f"v {x:.4f} {y:.4f} {z:.4f}\n" for x, y, z in self.v))
            fh.write("".join(f"vn {x:.4f} {y:.4f} {z:.4f}\n" for x, y, z in self.n))
            fh.write("".join(f"f {a + 1}//{a + 1} {b + 1}//{b + 1} {c + 1}//{c + 1}\n" for a, b, c in self.f))


def rot_towards(d, axis_angle, spin):
    """a direction tilted by axis_angle from d, spun by spin around it (branching, bending)"""
    d = _unit(tuple(d))
    a = (1.0, 0, 0) if abs(d[0]) < 0.9 else (0, 0, 1.0)
    u = _unit(_cross(d, a)); w = _cross(d, u)
    side = _add(_scale(u, math.cos(spin)), _scale(w, math.sin(spin)))
    return _add(_scale(d, math.cos(axis_angle)), _scale(side, math.sin(axis_angle)))


def tapered_tube(length, r0, r1, sides=SIDES, segs=6, bulge=0.0, seed=None, up=False):
    """a straight tube in OBJ space from y=0 to y=-length (metres, or +length if `up`) — see this module's
    docstring for the sign — radius r0 at the base tapering to r1 at the tip. After the engine's OBJ import,
    with up=False it spans scene y=0 to y=+length*100: a bone descending from a proximal joint to a distal
    one further from the root (most limb bones — a thigh from hip to knee, an upper arm from shoulder to
    elbow). up=True spans scene y=0 to y=-length*100 instead, for a bone that climbs *toward* the root's
    head end from a joint that sits at or below it — this rig's one example is the torso: the spine joint
    sits at pelvis height (so the hip joints, children of the same root, line up with it), and the torso
    climbs from there up to the neck, the opposite way a leg or arm bone points. Caught empirically — see
    this module's docstring. bulge (0..~0.3): an outward swell around the midpoint (muscle, not a cone) as
    a fraction of max(r0, r1); a tiny per-tube seeded wobble (bulge/20) keeps a chain of identical bones
    from reading as extruded plastic. Returns a Mesh; cap_ends is left to the caller (a bone sitting inside
    a joint sphere wants open ends, buried in the sphere — see this module's docstring)."""
    rng = random.Random(seed) if seed is not None else None
    sign = 1 if up else -1
    pts = [(0, sign * length * i / segs, 0) for i in range(segs + 1)]
    radii = []
    for i in range(segs + 1):
        u = i / segs
        base = r0 + (r1 - r0) * u
        swell = bulge * max(r0, r1) * math.sin(math.pi * u) if bulge else 0.0
        jitter = rng.gauss(0, bulge * max(r0, r1) * 0.05) if rng is not None else 0.0
        radii.append(max(0.1 * min(r0, r1), base + swell + jitter))
    m = Mesh(); m.tube(pts, radii, sides=sides, cap_ends=False)
    return m


_BAKED = {}


def bake_bone(out_dir, name, length, r0, r1, sides=SIDES, bulge=0.12, seed=None, up=False):
    """bake (or reuse, if this exact (out_dir, name) was already baked in this process) a tapered tube to
    out_dir/name.obj; returns the file's basename (without .obj) for use as a <mesh src="out_dir/<name>.obj">.
    Callers that need many bones of the same shape (a crowd of otherwise-identical figures) share one file —
    call with the same `name` for the same shape, so the cache (keyed on out_dir + name) catches the reuse.
    `up`: see tapered_tube's docstring — get this wrong and the bone points away from its joint, not into it."""
    key = (out_dir, name)
    if key in _BAKED:
        return _BAKED[key]
    os.makedirs(out_dir, exist_ok=True)
    m = tapered_tube(length, r0, r1, sides=sides, bulge=bulge, seed=seed, up=up)
    path = os.path.join(out_dir, f"{name}.obj")
    m.write(path, header=f"pnkit.mesh.bake_bone: length={length:.3f} r0={r0:.3f} r1={r1:.3f}")
    _BAKED[key] = name
    return name
