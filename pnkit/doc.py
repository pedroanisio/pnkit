"""pnkit.doc — the document under construction: its frame, its id set, and the registries that become sections.

A project makes one Doc per scene document and passes it to every helper that registers something (text assets,
paints, ids). The lists are plain lists, so a project may alias them (ASSETS = DOC.assets) and append to them
directly; nothing in pnkit keeps state outside a Doc.
"""
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

    def uid(self, base):
        return self.ids.uid(base)

    @property
    def cx(self):
        return self.width / 2

    @property
    def cy(self):
        return self.height / 2
