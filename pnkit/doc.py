"""pnkit.doc — the document under construction: its frame, its id set, and the registries that become sections.

A project makes one Doc per scene document and passes it to every helper that registers something (text assets,
paints, ids). The lists are plain lists, so a project may alias them (ASSETS = DOC.assets) and append to them
directly; nothing in pnkit keeps state outside a Doc.

The Doc also builds the document: `build()` makes an `sr_core.scene.Scene` from the project frame, the sections a
project hands it and the registries, and refuses a document `check()` reports level-1 errors for.
"""
from . import sdk
from .sdk import S
from .xml import Ids

__all__ = ["Doc", "DEFAULT_STYLES"]

# text roles -> the kit's text styles. Projects usually map the roles to their own styles based on pn-base.
DEFAULT_STYLES = {"text": "pn-body", "caps": "pn-label", "num": "pn-data", "head": "pn-heading", "note": "pn-body",
                  "big": "pn-display"}


class Doc:
    """width, height: the frame. styles: {role: textStyle id} used by text_asset/label/pill.

    Registries (in the order a scene usually writes them): assets (<assets> children), paints (<paints>),
    materials (<materials>), fields (<physics> force fields and constraints), bodies (ids of elements that carry
    rigid bodies; the physics block is written only when there are bodies or fields)."""

    def __init__(self, width=1920, height=1080, styles=None):
        self.width, self.height = width, height
        self.styles = dict(DEFAULT_STYLES if styles is None else styles)
        self.ids = Ids()
        self.assets, self.paints, self.materials, self.fields, self.bodies = [], [], [], [], []
        self.texts = {}            # text_asset cache: identical text assets are made once
        self.scene = None          # the Scene of the last build()

    def uid(self, base):
        return self.ids.uid(base)

    @property
    def cx(self):
        return self.width / 2

    @property
    def cy(self):
        return self.height / 2

    # ------------------------------------------------------------------------------------------ the document
    def section(self, name):
        """the registry `name` ("assets", "paints", "materials") as one section element, as `Xml` ("" when empty)"""
        items = getattr(self, name)
        if not items:
            return sdk.Xml("")
        el = sdk.new(S.Scene, name)
        sdk.ws(el)
        for i, it in enumerate(items):
            if i:
                sdk.ws(el)
            sdk.adopt(el, sdk.xml_of(it, type(el)))
        sdk.ws(el)
        return sdk.Xml.of(S.Text("  "), el, sep="")

    def build(self, project, composition, *parts, version="auto", check=True, physics=None, **sections):
        """the document as an `sr_core.scene.Scene` (also kept in `self.scene`).

        project: the <project> attributes ({"fps": 30, "duration": 40.0, "seed": 1}); width and height default to the frame.
        composition: the <composition> element, or XML text of it. parts: further sections, each a complete element
        (an `Xml` or text, e.g. the sections of `Brand.prologue`). sections: the same by name, for the registries
        ("assets", "paints", "materials", "physics") which are otherwise made from the Doc's lists; a registry that is
        empty and not given is left out. physics: keyword arguments of `physics.block` (cache_path ...) when the
        document has bodies or fields. The SDK refuses a misplaced element or a bad value here; with check=True
        a level-1 error raises `sdk.BuildError`."""
        from . import physics as phys
        scene = S.Scene(version=version)
        proj = dict(width=self.width, height=self.height)
        proj.update(project or {})
        sdk.add(scene, sdk.new(scene, "project", **proj))
        given = {k: v for k, v in sections.items() if v}
        for name in ("assets", "paints", "materials"):
            if name not in given:
                given[name] = self.section(name)
        if "physics" not in given:
            given["physics"] = phys.block(self.bodies, self.fields, **(physics or {}))
        for part in list(parts) + list(given.values()) + [composition]:
            if not part:
                continue
            for el in sdk.xml_of(part, S.Scene).elements:
                sdk.add(scene, el.copy() if el.owner is not None else el)
        self.scene = scene
        if check:
            found = sdk.errors(self.check(scene))
            if found:
                raise sdk.BuildError(self.check(scene), "document")
        return scene

    def check(self, scene=None, **kw):
        """`sr_core.scene.check` of the built document (level 1; schema=True adds level 2): the list of findings"""
        scene = scene or self.scene
        if scene is None:
            raise RuntimeError("Doc.check: nothing built yet, call build() first")
        return S.check(scene, **kw)

    def to_bytes(self, layout="preserve"):
        """the built document as UTF-8 XML with a declaration"""
        if self.scene is None:
            raise RuntimeError("Doc.to_bytes: nothing built yet, call build() first")
        return S.to_bytes(self.scene, layout=layout)

    def write(self, path, layout="preserve"):
        """check and write the built document; raises `sdk.BuildError` (and writes nothing) on level-1 errors"""
        findings = self.check()
        if sdk.errors(findings):
            raise sdk.BuildError(findings, path)
        with open(path, "wb") as fh:
            fh.write(self.to_bytes(layout))
        return path
