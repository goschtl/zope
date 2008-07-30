from zope.interface import Interface, Attribute
from zope import schema

class ILayoutAssignment(Interface):
    """A layout assignment."""
    
    name = Attribute(
        """Layout name.""")
    
    provider_map = Attribute(
        """Mapping from region names to content providers.""")

class ILayout(Interface):
    """A layout is a template with region definitions."""
    
    regions = Attribute(
        """Regions that are defined in this layout.""")

    template = Attribute(
        """Template path.""")
    
    resource_directory = Attribute(
        """Browser resource directory name.""")

class IRegion(Interface):
    """Represents a region definition for a template."""

    name = schema.TextLine(
        title=u"Name of region.",
        required=True)
    
    title = schema.TextLine(
        title=u"Title",
        required=False)

    xpath = schema.TextLine(
        title=u"Xpath expression for this region",
        required=True)
