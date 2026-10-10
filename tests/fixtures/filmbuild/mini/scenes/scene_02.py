import os
from pnkit.pixelart.ctx import Geometry, r, slot

ZOOM_X = int(os.environ.get("MINI_ZOOM_X", "160"))


def build(ctx):
    ctx.begin_scene(2)
    a, b = slot(2)
    bg = Geometry(); r(bg, 0, 0, 320, 100, 'blue2'); r(bg, 0, 100, 320, 80, 'steel1')
    s = ctx.shot('s02a_rua', a, b, bg=bg)
    with ctx.zoom(2, ZOOM_X, 90, parent=s, start=a, end=b) as z:
        ctx.walk(z, 'father', 100, 60, a, b, 150)
