##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Wiki implementation

$Id$
"""
import smtplib
from persistent import Persistent

from zope.interface import implements

from zope.app import zapi
from zope.app.container.btree import BTreeContainer
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app.filerepresentation.interfaces import IReadFile, IWriteFile
from zope.app.annotation.interfaces import IAnnotations
from zope.app.event.interfaces import ISubscriber, IObjectModifiedEvent
from zope.app.container.interfaces import \
     IObjectAddedEvent, IObjectRemovedEvent, IObjectMovedEvent
from zope.app.mail.interfaces import IMailDelivery

from zope.app.wiki.interfaces import IWiki, IWikiPage, IComment
from zope.app.wiki.interfaces import IWikiContained, IWikiPageContained
from zope.app.wiki.interfaces import IWikiPageHierarchy, IMailSubscriptions

__metaclass__ = type

HierarchyKey = 'http://www.zope.org/zwiki#1.0/PageHierarchy/parents'
SubscriberKey = 'http://www.zope.org/zwiki#1.0/MailSubscriptions/emails'


class WikiPage(BTreeContainer):
    """A persistent Wiki Page implementation."""

    implements(IWikiPage, IWikiContained)

    # See zope.app.container.interfaces.IContained
    __parent__ = __name__ = None

    # See zope.app.wiki.interfaces.IWikiPage
    source = u''
    
    # See zope.app.wiki.interfaces.IWikiPage
    type = u'zope.source.rest'


class WikiPageHierarchyAdapter:
    __doc__ = IWikiPageHierarchy.__doc__

    implements(IWikiPageHierarchy)
    __used_for__ = IWikiPage

    def __init__(self, context):
        self.context = context
        self._annotations = IAnnotations(context)
        if not self._annotations.get(HierarchyKey):
            self._annotations[HierarchyKey] = ()

    def reparent(self, parents):
        "See zope.app.wiki.interfaces.IWikiPageHierarchy"
        self.setParents(parents)

    def setParents(self, parents):
        self._annotations[HierarchyKey] = tuple(parents)

    def getParents(self):
        return self._annotations[HierarchyKey]

    parents = property(getParents, setParents)

    def path(self):
        "See zope.app.wiki.interfaces.IWikiPageHierarchy"
        # XXX: Allow for multpile parents
        if not self.getParents():
            return [self.context]
        wiki = zapi.getParent(self.context)
        name = self.getParents()[0]
        hier = IWikiPageHierarchy(wiki[name])
        return hier.path() + [self.context]

    def findChildren(self, recursive=True):
        "See zope.app.wiki.interfaces.IWikiPageHierarchy"
        wiki = zapi.getParent(self.context)
        contextName = zapi.name(self.context)
        children = []
        for pageName in wiki:
            hier = IWikiPageHierarchy(wiki[pageName])
            if contextName in hier.getParents():
                if recursive:
                    subs = hier.findChildren()
                else:
                    subs = ()
                children.append((wiki[pageName], subs))
        return tuple(children)


# Simple comments implementation

class Comment(Persistent):
    """A simple persistent comment implementation."""
    implements(IComment, IWikiPageContained)
    
    # See zope.app.container.interfaces.IContained
    __parent__ = __name__ = None

    # See zope.app.wiki.interfaces.IComment
    source = u''
    
    # See zope.app.wiki.interfaces.IComment
    type = u'zope.source.rest'


    # See zope.app.wiki.interfaces.IComment
    def _getTitle(self):
        dc = ICMFDublinCore(self)
        return dc.title

    def _setTitle(self, title):
        dc = ICMFDublinCore(self)
        dc.title = title

    title = property(_getTitle, _setTitle)


# Adapters for file-system style access

class WikiPageReadFile:
    """Adapter for letting a Wiki Page look like a regular readable file."""

    implements(IReadFile)
    __used_for__ = IWikiPage

    def __init__(self, context):
        self.context = context

    def read(self):
        """See zope.app.filerepresentation.interfaces.IReadFile"""
        return self.context.source

    def size(self):
        """See zope.app.filerepresentation.interfaces.IReadFile"""
        return len(self.context.source)


class WikiPageWriteFile:
    """Adapter for letting a Wiki Page look like a regular writable file."""

    implements(IWriteFile)
    __used_for__ = IWikiPage
    
    def __init__(self, context):
        self.context = context

    def write(self, data):
        """See zope.app.filerepresentation.interfaces.IWriteFile"""
        self.context.source = unicode(data)


# Component to fullfill mail subscriptions

class MailSubscriptions:
    """An adapter for WikiPages to provide an interface for collecting E-mails
    for sending out change notices."""

    implements(IMailSubscriptions)
    __used_for__ = IWikiPage, IWiki

    def __init__(self, context):
        self.context = context
        self._annotations = IAnnotations(context)
        if not self._annotations.get(SubscriberKey):
            self._annotations[SubscriberKey] = ()

    def getSubscriptions(self):
        "See zope.app.wiki.interfaces.IMailSubscriptions"
        return self._annotations[SubscriberKey]
        
    def addSubscriptions(self, emails):
        "See zope.app.wiki.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            # XXX: Make sure these are actually E-mail addresses.
            if email not in subscribers:
                subscribers.append(email.strip())
        self._annotations[SubscriberKey] = tuple(subscribers)
                
    def removeSubscriptions(self, emails):
        "See zope.app.wiki.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            if email in subscribers:
                subscribers.remove(email)
        self._annotations[SubscriberKey] = tuple(subscribers)
                


class WikiMailer:
    """Class to handle all outgoing mail."""

    implements(ISubscriber)

    def __init__(self, host="localhost", port="25"):
        """Initialize the the object.""" 
        self.host = host
        self.port = port

    def notify(self, event):
        """See zope.app.event.interfaces.ISubscriber"""
        if IWikiPage.providedBy(event.object):
            if IObjectAddedEvent.providedBy(event):
                self.handleAdded(event.object)

            elif IObjectModifiedEvent.providedBy(event):
                self.handleModified(event.object)

            elif IObjectRemovedEvent.providedBy(event):
                self.handleRemoved(event.object)

    def handleAdded(self, object):
        subject = 'Added: '+zapi.name(object)
        emails = self.getAllSubscribers(object)
        body = object.source
        self.mail(emails, subject, body)        

    def handleModified(self, object):
        # XXX: Should have some nice diff code here.
        # from diff import textdiff
        subject = 'Modified: '+zapi.name(object)
        emails = self.getAllSubscribers(object)
        body = object.source
        self.mail(emails, subject, body)

    def handleRemoved(self, object):
        subject = 'Removed: '+zapi.name(object)
        emails = self.getAllSubscribers(object)
        body = subject
        self.mail(emails, subject, body)

    def getAllSubscribers(self, object):
        """Retrieves all email subscribers by looking into the local Wiki Page
           and into the Wiki for the global subscriptions."""
        emails = tuple(IMailSubscriptions(object).getSubscriptions())
        emails += tuple(IMailSubscriptions(zapi.getParent(object)
                                           ).getSubscriptions())
        return emails

    def mail(self, emails, subject, body):
        """Mail out the Wiki change message."""
        if not emails:
            return
        msg = 'Subject: %s\n\n\n%s' %(subject, body)
        mail_delivery = zapi.getUtility(IMailDelivery,
                                       'wiki-delivery')
        mail_delivery.send('wiki@zope3.org' , emails, msg)

# Create a global mailer object.
mailer = WikiMailer()
