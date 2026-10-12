"""C14N 2.0 comparison helpers for the golden tests (standard library only).

`c14n(xml)` is the canonical form with comments (xml.etree.ElementTree.canonicalize): what the golden tests compare, with
no further normalisation. (Until 1.0.0 shipped there was a `c14n_numeric` that rewrote plain decimals; with sr-core 1.8.0
the SDK writes the number text pnkit hands it, so nothing needs it.)"""
import xml.etree.ElementTree as ET


def c14n(xml):
    if isinstance(xml, (bytes, bytearray)):
        xml = xml.decode("utf-8")
    return ET.canonicalize(xml, with_comments=True)


def wrap(fragment):
    """a fragment of sibling elements as one document, for comparing what a component returns"""
    return f"<r>{fragment}</r>"
