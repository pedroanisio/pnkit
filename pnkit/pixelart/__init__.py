"""pnkit.pixelart — the picture framework of an integer-grid pixel-art film, extracted from Lula 3.0.0 (2026-10-07).

A film draws on a 320 x 180 logical grid, 6 output pixels per cell (1920 x 1080), and writes scene-render 1.1 XML.
Modules (the art and figure modules keep their Lula names, so a Lula scene module ports by changing its imports only):

  geometry      Geometry: cells on the grid, rect/poly/ellipse/line, outline, scale, paths() (merged runs per colour)
  scene_art, story_art, chapter_art, full_art   the palette P, the pixel FONT and lettering(), primitives and props
  figures_v2, figures_v3_pose, figures_v3_cast, figures_v3_extra   figures (kinds, poses: idle, walk, talk, sit, back)
  ctx           Ctx: one build; scenes, shots, zoom, plates and boxes, signs, actors, crowds, steam, dust, tint;
                set_timings / timings / slot; PlanError
  sets          shared sets (bairro, house_exterior, house_interior, school_street, table_room, ...), each 320 x 180
                or wider for a pan, deterministic (sets._snap sorts its palette)
  checks        CheckedCtx: the build-time picture checks run on unchanged scene modules (view outside the set,
                figure cut mid-body, plate line breaks), waivers
  plan          the plan check: built shots against the plan (SHOTS-<ver>.md rows) and the timings
  frames        checks on rendered frames: flat or empty field, plate visible in the frame

Usage (a scene module):

    from pnkit.pixelart.ctx import Ctx, Geometry, P, r
    from pnkit.pixelart import sets

    def build(ctx):
        ctx.begin_scene(1)
        s = ctx.shot('s01a_street', 0.0, 4.0, bg=sets.school_street())
        ctx.plate('1958', 'TL', 0.5, 3.5)
"""
