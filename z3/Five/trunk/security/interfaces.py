from zope.interface import Interface
from zope.schema import TextLine, Text

class IPermission(Interface):
    """A permission object."""

    id = TextLine(
        title=u"Id",
        description=u"Id as which this permission will be known and used.",
        readonly=True,
        required=True)

    title = TextLine(
        title=u"Title",
        description=u"Provides a title for the permission.",
        required=True)

    description = Text(
        title=u"Description",
        description=u"Provides a description for the permission.",
        required=False)
