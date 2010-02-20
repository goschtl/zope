from zope.container.interfaces import IContainer
from zope.schema import TextLine
from zope.schema import Text

class ISampleApplication(IContainer):
    """The main application container"""

    name = TextLine(
        title=u"Name",
        description=u"Name of application",
        default=u"",
        required=True)

    description = Text(
        title=u"Description",
        description=u"Description about the application",
        default=u"",
        required=False)
