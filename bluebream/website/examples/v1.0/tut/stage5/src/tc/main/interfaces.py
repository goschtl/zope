from zope.interface import Interface
from zope.container.interfaces import IContainer
from zope.container.interfaces import IContained
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.constraints import ItemTypePrecondition

from zope.schema import TextLine
from zope.schema import Text
from zope.schema import Field


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

    def __setitem__(name, object):
        """Add an ICollector object."""

    __setitem__.precondition = ItemTypePrecondition(ITicket)


class ITicketContained(IContained):
    """Interface that specifies the type of objects that can contain
    tickets.  So a ticket can only contain in a collector."""

    __parent__ = Field(
        constraint = ContainerTypesConstraint(ICollector))
