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

$Id: wikipage.py,v 1.1 2004/02/27 11:06:58 philikon Exp $
"""
import smtplib
from persistent import Persistent

from zope.interface import implements
from zope.component import getAdapter
from zope.app.traversing import getParent, getName

from zope.app.interfaces.index.text import ISearchableText
from zope.app.interfaces.file import IReadFile, IWriteFile
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.event import ISubscriber
from zope.app.interfaces.event import IObjectAddedEvent, IObjectModifiedEvent
from zope.app.interfaces.event import IObjectRemovedEvent, IObjectMovedEvent

from zope.app.wiki.interfaces import IWiki, IWikiPage
from zope.app.wiki.interfaces import IWikiPageHierarchy, IMailSubscriptions

__metaclass__ = type

HierarchyKey = 'http://www.zope.org/zwiki#1.0/PageHierarchy/parents'
SubscriberKey = 'http://www.zope.org/zwiki#1.0/MailSubscriptions/emails'


class WikiPage(Persistent):
    __doc__ = IWikiPage.__doc__

    implements(IWikiPage)

    # See zope.app.wiki.interfaces.IWikiPage
    source = u''
    
    # See zope.app.wiki.interfaces.IWikiPage
    type = u'reStructured Text (reST)'

    def __init__(self):
        self.__comments = 1

    def append(self, source):
        "See zope.app.wiki.interfaces.IWikiPage"
        self.source += source

    def comment(self, comment):
        "See zope.app.wiki.interfaces.IWikiPage"
        self.__comments += 1
        self.append(comment)

    def getCommentCounter(self):
        "See zope.app.wiki.interfaces.IWikiPage"
        return self.__comments
        

class WikiPageHierarchyAdapter:
    __doc__ = IWikiPageHierarchy.__doc__

    implements(IWikiPageHierarchy)
    __used_for__ = IWikiPage

    def __init__(self, context):
        self.context = context
        self._annotations = getAdapter(context, IAnnotations)
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
        wiki = getParent(self.context)
        name = self.getParents()[0]
        hier = getAdapter(wiki[name], IWikiPageHierarchy)
        return hier.path() + [self.context]

    def findChildren(self, recursive=True):
        "See zope.app.wiki.interfaces.IWikiPageHierarchy"
        wiki = getParent(self.context)
        contextName = getName(self.context)
        children = []
        for pageName in wiki:
            hier = getAdapter(wiki[pageName], IWikiPageHierarchy)
            if contextName in hier.getParents():
                if recursive:
                    subs = hier.findChildren()
                else:
                    subs = ()
                children.append((wiki[pageName], subs))
        return tuple(children)


# Adapters for file-system style access

class WikiPageReadFile:
    """Adapter for letting a Wiki Page look like a regular readable file."""

    implements(IReadFile)
    __used_for__ = IWikiPage

    def __init__(self, context):
        self.context = context

    def read(self):
        """See zope.app.interfaces.file.IReadFile"""
        return self.context.source

    def size(self):
        """See zope.app.interfaces.file.IReadFile"""
        return len(self.context.source)


class WikiPageWriteFile:
    """Adapter for letting a Wiki Page look like a regular writable file."""

    implements(IWriteFile)
    __used_for__ = IWikiPage
    
    def __init__(self, context):
        self.context = context

    def write(self, data):
        """See zope.app.interfaces.file.IWriteFile"""
        self.context.source = unicode(data)


# Adapter for ISearchableText

class SearchableText:
    """This adapter provides an API that allows the Wiki Pages to be indexed
    by the Text Index.""" 

    implements(ISearchableText)
    __used_for__ = IWikiPage

    def __init__(self, page):
        self.page = page

    def getSearchableText(self):
        return [unicode(self.page.source)]


# Component to fullfill mail subscriptions

class MailSubscriptions:
    """An adapter for WikiPages to provide an interface for collecting E-mails
    for sending out change notices."""

    implements(IMailSubscriptions)
    __used_for__ = IWikiPage, IWiki

    def __init__(self, context):
        self.context = context
        self._annotations = getAdapter(context, IAnnotations)
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
        """See zope.app.interfaces.event.ISubscriber"""
        if IWikiPage.isImplementedBy(event.object):
            if IObjectAddedEvent.isImplementedBy(event):
                self.handleAdded(event.object)

            elif IObjectModifiedEvent.isImplementedBy(event):
                self.handleModified(event.object)

            elif IObjectRemovedEvent.isImplementedBy(event):
                self.handleRemoved(event.object)

    def handleAdded(self, object):
        subject = 'Added: '+getName(object)
        emails = self.getAllSubscribers(object)
        body = object.source
        self.mail(emails, subject, body)        

    def handleModified(self, object):
        # XXX: Should have some nice diff code here.
        # from diff import textdiff
        subject = 'Modified: '+getName(object)
        emails = self.getAllSubscribers(object)
        body = object.source
        self.mail(emails, subject, body)

    def handleRemoved(self, object):
        subject = 'Removed: '+getName(object)
        emails = self.getAllSubscribers(object)
        body = subject
        self.mail(emails, subject, body)

    def getAllSubscribers(self, object):
        """Retrieves all email subscribers by looking into the local Wiki Page
           and into the Wiki for the global subscriptions."""
        emails = tuple(getAdapter(object,
                                  IMailSubscriptions).getSubscriptions())
        emails += tuple(getAdapter(getParent(object),
                                   IMailSubscriptions).getSubscriptions())
        return emails

    def mail(self, emails, subject, body):
        """Mail out the Wiki change message."""
        if not emails:
            return
        msg = 'Subject: %s\n\n\n%s' %(subject, body)
        server = smtplib.SMTP(self.host, self.port)
        server.set_debuglevel(0)
        server.sendmail('wiki@zope3.org', emails, msg)
        server.quit()

# Create a global mailer object.
mailer = WikiMailer()
