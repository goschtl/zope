from zope.interface import implements
from tc.main.interfaces import ITicket


class Ticket(object):

    implements(ITicket)

    number = u""
    summary = u""
