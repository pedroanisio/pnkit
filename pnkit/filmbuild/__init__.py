"""pnkit.filmbuild — film_build: one film.json, restartable stages that record the hashes of their inputs.

    python3 tools/film_build.py FILM.json [STAGE ...] [--force] [--from STAGE] [--to STAGE]

Stages, in order: snapshot, voice, plan, generate, assemble, render, audio, join, gates, sheets, pack (see stages.py).
Heavy work (renders, encodes, ffmpeg measures, sheets) runs only on the render hosts named in film.json, through the
runner, under the lock; locally film_build builds XML, hashes files and copies. It prints one summary table.
"""
