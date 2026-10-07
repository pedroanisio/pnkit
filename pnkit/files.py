"""pnkit.files — approved files are write-once.

An owner-approved file (a narration, a score excerpt, a gate record) must never be overwritten by a re-run: the
approval belongs to those exact bytes. Lula's approved score excerpt was once replaced by a re-run of the tool that
made it. Tools that write such a file use these helpers instead of open(path, "w"):

    files.write_once("score/excerpt.wav", data)       # FileExistsError (WriteOnceError) if the path exists
    path = files.next_free("score/excerpt.wav")       # score/excerpt-v2.wav (or the path itself when it is free)
    path = files.write_next("score/excerpt.wav", data)  # write_once to the first free path; returns it

The check and the create are one operation (open mode "x"), so two processes cannot both win the same path. A
symbolic link, even a dangling one, counts as existing. Standard library only.
"""
import os

__all__ = ["WriteOnceError", "write_once", "next_free", "write_next"]


class WriteOnceError(FileExistsError):
    """the path already exists and approved files are never overwritten"""


def _bytes(data, encoding):
    return data.encode(encoding) if isinstance(data, str) else bytes(data)


def write_once(path, data, encoding="utf-8"):
    """Write data (bytes, or str in `encoding`) to path; raise WriteOnceError if anything is there. Returns path."""
    path = os.fspath(path)
    if os.path.lexists(path):
        raise WriteOnceError(f"{path} exists: an approved file is never overwritten; write the new one beside it "
                             f"(files.next_free / files.write_next)")
    payload = _bytes(data, encoding)
    try:
        with open(path, "xb") as fh:
            fh.write(payload)
    except FileExistsError as e:
        raise WriteOnceError(f"{path} exists: an approved file is never overwritten") from e
    return path


def next_free(path, suffix="-v"):
    """The path itself when nothing is there; else the first of stem+suffix+N+ext for N = 2, 3, ... that is free
    (excerpt.wav -> excerpt-v2.wav -> excerpt-v3.wav). It only looks: use write_next to claim the name."""
    path = os.fspath(path)
    if not os.path.lexists(path):
        return path
    stem, ext = os.path.splitext(path)
    n = 2
    while os.path.lexists(f"{stem}{suffix}{n}{ext}"):
        n += 1
    return f"{stem}{suffix}{n}{ext}"


def write_next(path, data, suffix="-v", encoding="utf-8"):
    """write_once to next_free(path), retrying if another process takes the name first. Returns the path written."""
    while True:
        target = next_free(path, suffix)
        try:
            return write_once(target, data, encoding)
        except WriteOnceError:
            continue
