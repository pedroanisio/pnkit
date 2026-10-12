"""pnkit._num — pnkit's number and text formatting for scene attributes (no dependencies).

Kept apart from pnkit.xml so that pnkit.sdk can use it and pnkit.xml can build on pnkit.sdk."""

__all__ = ["f", "esc"]


def f(x):
    """a number as the scene format writes it: ints as they are, floats to 3 decimals without trailing zeros
    (-0 is written 0); anything else through str()"""
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return str(x)
    if isinstance(x, float):
        s = f"{x:.3f}".rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return str(x)


def esc(s):
    """escape text for an XML attribute value in double quotes"""
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
