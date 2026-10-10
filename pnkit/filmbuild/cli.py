"""pnkit.filmbuild.cli — the film_build command line. One table on stdout; exit 0 when every stage asked for passed."""
import argparse, sys

from .config import Film, FilmError
from .stages import ORDER, Build, run, table


def main(argv=None, remote=None):
    ap = argparse.ArgumentParser(prog="film_build", description="Build a film from film.json in restartable, hash-recorded stages.")
    ap.add_argument("film", help="the film.json")
    ap.add_argument("stages", nargs="*", help=f"stages to run (default: all, in order): {' '.join(ORDER)}")
    ap.add_argument("--from", dest="start", choices=ORDER, help="run from this stage to the end (or to --to)")
    ap.add_argument("--to", dest="stop", choices=ORDER, help="run up to and including this stage")
    ap.add_argument("--force", action="store_true", help="rerun the stages even when their inputs did not change")
    a = ap.parse_args(argv)
    bad = [s for s in a.stages if s not in ORDER]
    if bad:
        ap.error(f"unknown stage(s) {bad}; stages: {' '.join(ORDER)}")
    if a.stages:
        stages = [s for s in ORDER if s in a.stages]
    else:
        i = ORDER.index(a.start) if a.start else 0
        j = ORDER.index(a.stop) + 1 if a.stop else len(ORDER)
        stages = ORDER[i:j]
    try:
        film = Film(a.film)
    except FilmError as e:
        print(f"film_build: {e}", file=sys.stderr)
        return 2
    b = Build(film, force=a.force, remote=remote)
    rows = run(b, stages)
    print(f"film_build {film.id} {film.version}")
    print(table(rows))
    return 0 if rows and all(r[1] != "FAIL" for r in rows) and len(rows) == len(stages) else 1


if __name__ == "__main__":
    sys.exit(main())
