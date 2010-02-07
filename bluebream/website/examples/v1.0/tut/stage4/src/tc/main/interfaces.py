from zope.interface import Interface
from zope.container.interfaces import IContainer
from zope.schema import TextLine
from zope.schema import Text

class ICollector(IContainer):
    """The main application container"""

    name = TextLine(
        title=u"Name",
        description=u"Name of application container",
        default=u"",
        required=True)

    description = Text(
        title=u"Description",
        description=u"Description of application container",
        default=u"",
        required=False)


class ITicket(Interface):
    """Ticket - the main content object"""

    number = TextLine(
        title=u"Number",
        description=u"Ticket number",
        default=u"",
        required=True)

    summary = TextLine(
        title=u"Summary",
        description=u"Ticket summary",
        default=u"",
        required=True)
