"""pnkit.physics — the <physics> block and the signature that decides whether a simulation cache still applies.

`scene-render simulate` writes a cache for one document; the project records {"signature", "sha256"} next to it.
The signature covers only what the simulation depends on: every layer or shape that carries a <rigidBody> (with
its animation) and the force fields that can move a body (particle-only fields cannot). When the signature of the
document being built matches, the block points at the cache; otherwise the engine simulates.
"""
import hashlib, json, os, re

__all__ = ["signature", "block"]


def signature(doc_body, fields):
    """SHA-256 over the rigid-body elements of `doc_body` (composition XML) and the non-particle `fields`"""
    parts = re.findall(r"<(?:layer|shape)\b[^>]*>(?:(?!</(?:layer|shape)>).)*?<rigidBody[^>]*/>.*?</(?:layer|shape)>", doc_body, re.S)
    fields = [x for x in fields if 'affects="particles"' not in x]      # particle-only fields cannot move a body
    return hashlib.sha256(("\n".join(parts) + "\n".join(fields)).encode()).hexdigest()


def block(bodies, fields, sig=None, cache_path=None, meta_path=None, cache_ref=None, gravity_y=-9.80665, ppm=200):
    """the <physics> block ("" when there are no bodies and no fields). cache_path/meta_path: the cache file and its
    JSON record on disk; cache_ref: the cache's path as the document names it (relative to the document)."""
    if not bodies and not fields:
        return ""
    cache = ""
    if sig and cache_path and meta_path and os.path.exists(cache_path) and os.path.exists(meta_path):
        meta = json.load(open(meta_path))
        if meta.get("signature") == sig:
            cache = f' cache="{cache_ref}" cacheSha256="{meta["sha256"]}"'
    return (f'  <physics gravityY="{gravity_y}" pixelsPerMeter="{ppm}" bounds="none"{cache}>\n'
            + "\n".join("    " + x for x in fields) + "\n  </physics>")
