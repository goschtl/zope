##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""Mail Support

$Id: mail.py,v 1.3 2003/08/28 05:22:30 srichter Exp $
"""
from zope.interface import implements

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotations
from zope.app.event.interfaces import IObjectCreatedEvent, IObjectModifiedEvent
from zope.app.mail.interfaces import IMailDelivery

from interfaces import IBug, IBugTracker, IMailSubscriptions

SubscriberKey = 'bugtracker.MailSubsriptions.emails'

class MailSubscriptions:
    """An adapter for IBugTracker and IBug to provide an
    interface for collecting E-mails for sending out change notices."""

    implements(IMailSubscriptions)

    def __init__(self, context):
        self.context = self.__parent__ = context
        self._annotations = IAnnotations(context)
        if not self._annotations.get(SubscriberKey):
            self._annotations[SubscriberKey] = ()

    def getSubscriptions(self):
        "See bugtracker.interfaces.IMailSubscriptions"
        return self._annotations[SubscriberKey]
        
    def addSubscriptions(self, emails):
        "See bugtracker.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            if email not in subscribers:
                subscribers.append(email.strip())
        self._annotations[SubscriberKey] = tuple(subscribers)
                
    def removeSubscriptions(self, emails):
        "See bugtracker.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            if email in subscribers:
                subscribers.remove(email)
        self._annotations[SubscriberKey] = tuple(subscribers)


class Mailer:
    """Class to handle all outgoing mail."""

    def __call__(self, event):
        if IBug.providedBy(event.object):
            if IObjectCreatedEvent.providedBy(event):
                self.handleAdded(event.object)
            elif IObjectModifiedEvent.providedBy(event):
                self.handleModified(event.object)

    def handleAdded(self, object):
        subject = 'Added: %s (%s)' %(object.title, zapi.name(object))
        emails = self.getAllSubscribers(object)
        body = object.description
        self.mail(emails, subject, body)        

    def handleModified(self, object):
        subject = 'Modified: %s (%s)' %(object.title, zapi.name(object))
        emails = self.getAllSubscribers(object)
        body = object.description
        self.mail(emails, subject, body)

    def handleRemoved(self, object):
        subject = 'Removed: %s (%s)' %(object.title, zapi.name(object))
        emails = self.getAllSubscribers(object)
        body = object.description
        self.mail(emails, subject, body)

    def getAllSubscribers(self, object):
        """Retrieves all email subscribers for this message and all above."""
        emails = ()
        obj = object
        while IBug.providedBy(obj) or IBugTracker.providedBy(obj):
            emails += tuple(IMailSubscriptions(obj).getSubscriptions())
            obj = zapi.getParent(obj)
        return emails

    def mail(self, toaddrs, subject, body):
        """Mail out the change message."""
        if not toaddrs:
            return
        msg = 'Subject: %s\n\n\n%s' %(subject, body)
        mail_utility = zapi.getUtility(IMailDelivery, 'bug-mailer')
        mail_utility.send('bugtracker@zope3.org' , toaddrs, msg)
