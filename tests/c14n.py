"""C14N 2.0 comparison helpers for the golden tests (standard library only).

`c14n(xml)` is the canonical form with comments (xml.etree.ElementTree.canonicalize): what the golden tests compare.
`c14n_numeric(xml)` first rewrites every attribute value that is a plain decimal number to its shortest positional
form ("855.0" -> "855", "0.50" -> "0.5"), because the scene SDK writes an xs:double that way and cannot write
"855.0" (see CHANGELOG 1.0.0). Nothing else is changed: names, order of children, text, comments and every other
attribute value must still agree exactly."""
import re
import xml.etree.ElementTree as ET
from decimal import Decimal

_NUM = re.compile(r"-?\d+\.\d+")


def c14n(xml):
    if isinstance(xml, (bytes, bytearray)):
        xml = xml.decode("utf-8")
    return ET.canonicalize(xml, with_comments=True)


def _plain(v):
    d = Decimal(v)
    if d == 0:
        return "0"
    return format(d.normalize(), "f")


def c14n_numeric(xml):
    if isinstance(xml, (bytes, bytearray)):
        xml = xml.decode("utf-8")
    root = ET.XML(xml, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    for el in root.iter():
        if isinstance(el.tag, str):
            for k, v in list(el.attrib.items()):
                if _NUM.fullmatch(v):
                    el.set(k, _plain(v))
    return ET.canonicalize(ET.tostring(root, encoding="unicode"), with_comments=True)


def wrap(fragment):
    """a fragment of sibling elements as one document, for comparing what a component returns"""
    return f"<r>{fragment}</r>"
