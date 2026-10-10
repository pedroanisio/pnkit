from pnkit.pixelart.ctx import Geometry, r, slot


def build(ctx):
    ctx.begin_scene(1)
    a, b = slot(1)
    bg = Geometry(); r(bg, 0, 0, 320, 120, 'blue2'); r(bg, 0, 120, 320, 60, 'green')
    ctx.shot('s01a_ceu', a, b, bg=bg)
    ctx.plate('Teste · 1958', 'TL', 0.5, 2.0)
