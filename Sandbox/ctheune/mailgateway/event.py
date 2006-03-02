
from zope.interface import implements
from mailgateway.interfaces import IMailReceivedEvent

class MailReceivedEvent(object):

    implements(IMailReceivedEvent)

    def __init__(self, mail):
        self.mail = mail
        self.received_by = []
