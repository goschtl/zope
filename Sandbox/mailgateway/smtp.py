##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""SMTP server factories

$Id$
"""

import email

from twisted.internet import defer
from twisted.mail import smtp

from zope.publisher.publish import publish
from zope.app.twisted.server import ServerType 

from mailgateway.request import SMTPRequest, SMTPPublication

class ZopeMessageDelivery:
    __implements__ = (smtp.IMessageDelivery,)
    
    def __init__(self, db):
        self.db = db

    def receivedHeader(self, helo, origin, recipients):
        return "Received: from %s by Zope SMTP server" % origin
    
    def validateFrom(self, helo, origin):
        # All addresses are accepted
        return origin
    
    def validateTo(self, user):
        # Only messages directed to the "console" user are accepted.
        # XXX check for the targetted user here ...

        # XXX Make ConsoleMessage a deferred?
        return lambda: ZopeMessage(self.db)

class ZopeMessage:
    __implements__ = (smtp.IMessage,)
    
    def __init__(self, db):
        self.db = db
        self.lines = []
    
    def lineReceived(self, line):
        self.lines.append(line)
    
    def eomReceived(self):
        mail = email.message_from_string("\n".join(self.lines))
        self.lines = []
        publication = SMTPPublication(self.db)
        request = SMTPRequest(None, {'mail':mail})
        request.setPublication(publication)
        publish(request)
        return defer.succeed(None)
    
    def connectionLost(self):
        # There was an error, throw away the stored lines
        self.lines = None

class ZopeSMTPFactory(smtp.SMTPFactory):

    def __init__(self, db, *a, **kw):
        smtp.SMTPFactory.__init__(self, *a, **kw)
        self.delivery = ZopeMessageDelivery(db)
    
    def buildProtocol(self, addr):
        p = smtp.SMTPFactory.buildProtocol(self, addr)
        p.delivery = self.delivery
        return p

def createSMTPFactory(db):
    return ZopeSMTPFactory(db)

smtp_servertype = ServerType(createSMTPFactory, 8025)
