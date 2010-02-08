from zope.interface import implements
from tc.main.interfaces import ITicket
from tc.main.interfaces import ITicketContained
from zope.location.contained import Contained


class Ticket(Contained):

    implements(ITicket, ITicketContained)

    number = u""
    summary = u""
