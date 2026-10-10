#!/usr/bin/env python3
"""film_build — build a film from one film.json in restartable stages (pnkit.filmbuild; see its docstrings).

    python3 tools/film_build.py FILM.json [STAGE ...] [--force] [--from STAGE] [--to STAGE]

Stages: snapshot voice plan generate assemble render audio join gates sheets pack. Prints one summary table; exit 0
when every stage asked for passed, 1 on a failed stage, 2 when film.json cannot be read."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit.filmbuild.cli import main   # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
