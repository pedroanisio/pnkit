"""pnkit.sdk — the one place where pnkit meets `sr_core.scene`, the Python scene SDK (sr-core >= 1.7.0).

Every pnkit component that writes scene XML builds `sr_core.scene` elements through this module: the SDK enforces
the element's parent, its attributes, enumeration values and the order of a document's sections when the element
is made, and `check()` reports the rest. Nothing in pnkit writes angle brackets by hand any more.

What a component returns
------------------------
`Xml`, a `str` that holds the XML text of what was built, and keeps the SDK elements it was made of in `.elements`
(`.element` when there is exactly one). Callers that used the XML string keep working unchanged (`str()`, `"\\n".join`,
f-strings, `+`, `in`, `ET.fromstring`), and code that wants the element reads `.element`. The text is a snapshot
taken when the component returned; the elements are what pnkit hands on, so a component that receives an `Xml`
adds its element, not a re-parsed copy.

What a component accepts
------------------------
`adopt(parent, *items)` takes SDK elements, `Xml`, and plain XML strings (the old `extra=` and `content=`
arguments, strings a project wrote itself). A string is parsed against the parent's type, so an element or an
attribute the parent does not allow raises `SchemaValueError` / `AttributeError` there, not in a render.

Numbers
-------
pnkit writes floats to three decimals without trailing zeros (`pnkit.xml.f`). `put()` hands the SDK the value that
form reads back as (an int when it is whole, else a float), so the SDK writes the same digits. An attribute
whose type is xs:string (`fps`, a key's `value`) gets the text. A text given for a numeric attribute is kept as given
where the type is a decimal, and read as a number where it is an xs:double (the SDK writes a double in its shortest
form: `855.0` is written `855`, it cannot be written otherwise).
"""
import keyword
import re
import xml.etree.ElementTree as ET

from sr_core import scene as S
from sr_core.scene import SchemaValueError

from ._num import f

__all__ = ["Xml", "BuildError", "num", "put", "new", "adopt", "parse_fragment", "parse_sections", "parse_num", "xml_of", "frag", "text_of", "ws", "add",
           "attrs_of", "errors", "S", "SchemaValueError"]

MIN_SDK = "1.7.0"


class BuildError(ValueError):
    """a document that `check()` reports level-1 errors for; `.findings` holds every finding"""

    def __init__(self, findings, what="document"):
        self.findings = list(findings)
        errs = [x for x in self.findings if x.severity == "error"]
        shown = "; ".join(f"{x.code} {x.path}: {x.message}" for x in errs[:5])
        super().__init__(f"{what} has {len(errs)} error(s): {shown}" + (" ..." if len(errs) > 5 else ""))


def _esc_text(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\r", "&#13;")


def text_of(node):
    """the XML text of one node (an element, or the white space between elements), as the SDK writes it"""
    if isinstance(node, S.Text):
        return _esc_text(node.text)
    return S.to_bytes(node).decode("utf-8").split("\n", 1)[1].rstrip("\n")


def ws(el, text="\n"):
    """append white space among the children of `el`, as the formatting of a string would have it. The SDK keeps these
    text nodes in `el.nodes` and writes them back; they carry no meaning for the engine."""
    el.nodes.append(S.Text(text))


class Xml(str):
    """XML text that carries the SDK nodes it was built from: `.nodes` (elements and the white space between them),
    `.elements`, and `.element` when there is exactly one (see the module docstring)"""
    nodes = ()

    def __new__(cls, text, nodes=()):
        self = super().__new__(cls, text)
        self.nodes = tuple(nodes)
        return self

    @property
    def elements(self):
        return tuple(n for n in self.nodes if isinstance(n, S.Element))

    @property
    def element(self):
        els = self.elements
        if len(els) != 1:
            raise ValueError(f"{len(els)} elements, not one")
        return els[0]

    @classmethod
    def from_nodes(cls, nodes):
        """the Xml of a list of nodes as it stands"""
        nodes = list(nodes)
        return cls("".join(text_of(n) for n in nodes), nodes)

    @classmethod
    def of(cls, *items, sep="\n"):
        """the Xml of elements (or Xml, or text nodes), written one after another with `sep` between the items"""
        nodes = []
        for it in items:
            if it is None:
                continue
            if nodes and sep:
                nodes.append(S.Text(sep))
            nodes.extend(it.nodes if isinstance(it, Xml) else (it,))
        return cls("".join(text_of(n) for n in nodes), nodes)


def xml_of(item, parent):
    """`item` as an `Xml`: an `Xml` as it is; an element wrapped; a string parsed against `parent` (white space kept)"""
    if isinstance(item, Xml):
        return item
    if isinstance(item, S.Element):
        return Xml.of(item)
    return Xml.from_nodes(parse_fragment(parent, str(item)))


def frag(elements, sep="\n"):
    """an `Xml` for several sibling elements"""
    return Xml.of(*elements, sep=sep)


# ------------------------------------------------------------------------------------------------ values

_WHOLE = re.compile(r"-?\d+")
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")
_learned = {}                       # (class, attribute) -> True when the attribute takes text, not a number


def parse_num(s, default=None):
    """the int or float that the text of a number reads as (`"2"` -> 2, `"0.3"` -> 0.3), else `default`"""
    if _WHOLE.fullmatch(s):
        return int(s)
    try:
        return float(s)
    except ValueError:
        return default


def num(x):
    """x as the int or float whose SDK form is pnkit's form (`pnkit.xml.f`): 0.1 + 0.2 -> 0.3, 2.0 -> 2"""
    return parse_num(f(x), x)


def _py(name):
    return name + "_" if keyword.iskeyword(name) else name


def put(el, name, value):
    """set one attribute from a Python value. None leaves it unset. Numbers are given in pnkit's form; the SDK
    refuses what the schema does not allow (SchemaValueError), and an attribute the element does not declare
    (AttributeError)."""
    if value is None:
        return
    py = _py(name)
    if isinstance(value, bool):
        try:
            setattr(el, py, value)
        except SchemaValueError as err:
            try:
                setattr(el, py, "true" if value else "false")
            except SchemaValueError:
                raise err from None
        return
    if isinstance(value, (int, float)):
        key = (type(el), py)
        err = None
        if not _learned.get(key):
            try:
                setattr(el, py, num(value))
                return
            except SchemaValueError as e:
                err = e
        try:
            setattr(el, py, f(value))
            _learned[key] = True
        except SchemaValueError:
            if err is not None:
                raise err from None
            raise
        return
    if isinstance(value, str):
        try:
            setattr(el, py, value)
        except SchemaValueError as err:
            if not _NUMBER.fullmatch(value):
                raise
            try:
                setattr(el, py, num(float(value)) if "." in value else int(value))
            except SchemaValueError:
                raise err from None
        return
    setattr(el, py, value)


def attrs_of(text):
    """{name: value} of an attribute string such as ' tags="hud" x="5"' (the old `attrs=` arguments)"""
    if not text or not text.strip():
        return {}
    try:
        return dict(ET.XML(f"<x {text.strip()}/>").attrib)
    except ET.ParseError as err:
        raise ValueError(f"not a list of attributes: {text!r} ({err})") from None


def new(parent, name, *children, **attrs):
    """a detached `<name>` element of the class the schema gives it under `parent` (an element or its class),
    with `attrs` set in the order given (None skipped) and `children` adopted. Raises if `parent` does not allow
    `<name>`."""
    cls = _class(parent, name)
    el = cls()
    if name != el.xml_name and name in cls._element_names:
        el._name = name          # an alias (<thumbnail> for <poster>): the SDK's public API cannot choose it, see README
    for k, v in attrs.items():
        put(el, k, v)
    if children:
        adopt(el, *children)
    return el


def _class(parent, name):
    ptype = getattr(parent, "_xsd_type", None)
    cls = S.ELEMENT_CLASSES.get((ptype, name)) if ptype else None
    if cls is None:
        pname = getattr(parent, "xml_name", None) if not isinstance(parent, type) else None
        raise SchemaValueError(f"<{name}> is not allowed in <{pname or getattr(parent, '__name__', parent)}>",
                               path=getattr(parent, "xml_path", None) if not isinstance(parent, type) else None)
    return cls


# ------------------------------------------------------------------------------------------------ parsing strings

def _space(text):
    return [S.Text(text)] if text and not text.strip() else []


def _build(parent, node):
    cls = _class(parent, node.tag)
    el = cls()
    if node.tag != el.xml_name and node.tag in cls._element_names:
        el._name = node.tag
    for k, v in node.attrib.items():
        put(el, k, v)
    children = list(node)
    if not children:
        if node.text:
            el.content = node.text
        return el
    if node.text and node.text.strip():
        raise SchemaValueError(f"text among the children of <{node.tag}>", path=el.xml_path)
    el.nodes.extend(_space(node.text))
    for child in children:
        add(el, _build(el, child))
        if child.tail and child.tail.strip():
            raise SchemaValueError(f"text after <{child.tag}> in <{node.tag}>", path=el.xml_path)
        el.nodes.extend(_space(child.tail))
    return el


def parse_fragment(parent, text):
    """the nodes of an XML string (sibling elements and the white space between them; comments are dropped) as
    detached SDK elements typed by `parent`. A name `parent` does not allow, or a value the schema refuses, raises."""
    try:
        root = ET.XML(f"<w>{text}</w>")
    except ET.ParseError as err:
        raise ValueError(f"not well-formed XML: {err}: {text[:120]!r}") from None
    if root.text and root.text.strip():
        raise SchemaValueError("text outside any element", path=getattr(parent, "xml_path", None))
    out = _space(root.text)
    for child in root:
        out.append(_build(parent, child))
        if child.tail and child.tail.strip():
            raise SchemaValueError(f"text after <{child.tag}>", path=getattr(parent, "xml_path", None))
        out.extend(_space(child.tail))
    return out


def parse_sections(text):
    """the top-level sections (children of <scene>) in an XML string, as detached elements"""
    return [n for n in parse_fragment(S.Scene, text) if isinstance(n, S.Element)]


def add(parent, child):
    """`parent.add(child)` that leaves white space where the caller put it: the child goes after the white space
    already among the children. (The SDK puts a new element straight after the previous element and copies that
    element's indentation, which is right for a document that is indented, and wrong for a string whose newlines
    the caller placed.) An element that the content model orders in the middle goes where the model puts it."""
    nodes = parent.nodes
    j = len(nodes) - 1
    while j >= 0 and isinstance(nodes[j], S.Text):
        j -= 1
    trailing = nodes[j + 1:]
    del nodes[j + 1:]
    k = j
    while k >= 1 and isinstance(nodes[k - 1], S.Text):
        k -= 1
    prev = nodes[k:j] if j >= 1 else []
    del nodes[k:j]
    try:
        parent.add(child)
    finally:
        if nodes and nodes[-1] is child:
            nodes.pop()
            nodes[k:k] = prev
            nodes.extend(trailing)
            nodes.append(child)
        else:
            nodes[k:k] = prev
            nodes.extend(trailing)
    return child


def adopt(parent, *items):
    """add `items` to `parent`, in order: SDK elements, `Xml`, XML strings, or lists of these; None and "" are
    skipped. An element that already has a parent is copied. The white space inside a string or an `Xml` is kept."""
    for it in items:
        if it is None:
            continue
        if isinstance(it, Xml):
            nodes = it.nodes
            if not nodes and it.strip():
                nodes = parse_fragment(parent, str(it))
        elif isinstance(it, S.Element):
            nodes = (it,)
        elif isinstance(it, str):
            nodes = parse_fragment(parent, it) if it else ()
        elif isinstance(it, (list, tuple)):
            adopt(parent, *it)
            continue
        else:
            raise TypeError(f"cannot add {type(it).__name__} to <{parent.xml_name}>")
        for n in nodes:
            if isinstance(n, S.Text):
                parent.nodes.append(S.Text(n.text))
            else:
                add(parent, n.copy() if n.owner is not None else n)


def errors(findings):
    """the error-severity findings of a `check()` result"""
    return [x for x in findings if x.severity == "error"]
