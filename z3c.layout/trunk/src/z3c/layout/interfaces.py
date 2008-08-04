from zope.interface import Interface, Attribute
from zope.configuration import fields
from zope import schema

class IRegion(Interface):
    """Represents a region definition for a template."""

    name = schema.TextLine(
        title=u"Name of region.",
        required=True)
    
    xpath = schema.TextLine(
        title=u"X-path expression for this region",
        required=True)

    title = schema.TextLine(
        title=u"Title",
        required=False)

    mode = schema.Choice(
        (u"replace", u"append", u"prepend", u"before", u"after"),
        default=u"replace",
        required=False)
    
    provider = schema.TextLine(
        title=u"Content provider",
        description=u"Name of the content provider component to render this region.",
        required=False)

class ILayout(Interface):
    """A layout is a template with region definitions."""

    name = schema.TextLine(
        title=u"Title")
    
    template = fields.Path(
        title=u"Template")

    regions = schema.Set(
        title=u"Regions that are defined in this layout.",
        value_type=schema.Object(schema=IRegion),
        required=False)

    def parse():
        """Parse template using lxml's HTML parser class. Transforms
        are applied before the tree is returned."""

class IContentProviderFactory(Interface):
    def __call__(context, request, view):
        """Return content provider."""
