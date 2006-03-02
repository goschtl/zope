

import zope.event
from zope.publisher.interfaces import IRequest
from zope.publisher.base import BaseRequest
from zope.app.publication.zopepublication import ZopePublication

from mailgateway.event import MailReceivedEvent


class SMTPRequest(BaseRequest):

    __implements__ = (IRequest,)

    def traverse(self, object):
        return object

class SMTPPublication(ZopePublication):
    
    def callObject(self, request, object):
        mail = request.get('mail')
        mail_event = MailReceivedEvent(mail)
        zope.event.notify(mail_event)
        if len(mail_event.received_by) == 0:
            # XXX doesn't help ... because it doesn't bounce
            raise Exception, "No mailbox found"

