from zope.interface import Interface
from zope.schema import Text, TextLine, Field

from zope.app.container.constraints import containers, contains
from zope.app.container.interfaces import IContained, IContainer

class IComment(Interface):
    """Comment for Ticket"""

    body = Text(
        title=u"Additional Comment",
        description=u"Body of the Comment.",
        default=u"",
        required=True)

class ITicket(IContainer):
    """A ticket object."""

    summary = TextLine(
        title=u"Summary",
        description=u"Short summary",
        default=u"",
        required=True)
  
    description = Text(
        title=u"Description",
        description=u"Full description",
        default=u"",
        required=False)

    contains('.IComment')

class ICollector(IContainer):
    """Collector the base object. It can only
    contains ITicket objects."""

    contains('.ITicket')
  
    description = Text(
        title=u"Description",
        description=u"A description of the collector.",
        default=u"",
        required=False)


class ITicketContained(IContained):
    """Interface that specifies the type of objects that can contain
    tickets.  So a ticket can only contain in a collector."""

    containers(ICollector)

class ICommentContained(IContained):
    """Interface that specifies the type of objects that can contain
    comments.  So a comment can only contain in a ticket."""

    containers(ITicket)
