##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Wiki implementation

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent

from zope.interface import implements
from zope.event import notify
from zope.schema.vocabulary import getVocabularyRegistry

from zope.app import zapi
from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import Contained
from zope.app.filerepresentation.interfaces import IReadFile
from zope.app.filerepresentation.interfaces import IWriteFile
from zope.app.filerepresentation.interfaces import IReadDirectory
from zope.app.filerepresentation.interfaces import IWriteDirectory
from zope.app.annotation.interfaces import IAnnotations
from zope.app.event.objectevent import ObjectEvent
from zope.app.container.interfaces import \
     IObjectAddedEvent, IObjectRemovedEvent
from zope.app.mail.interfaces import IMailDelivery

from zwiki.interfaces import IWiki, IWikiPage
from zwiki.interfaces import IWikiContained, IWikiPageContained
from zwiki.interfaces import IWikiPageHierarchy, IMailSubscriptions
from zwiki.interfaces import IWikiPageEditEvent
from zwiki.diff import textdiff

HierarchyKey = 'http://www.zope.org/zwiki#1.0/PageHierarchy/parents'
SubscriberKey = 'http://www.zope.org/zwiki#1.0/MailSubscriptions/emails'


class WikiPage(BTreeContainer, Contained):
    """A persistent Wiki Page implementation."""

    implements(IWikiPage, IWikiContained)

    def __init__(self, source=u''):
        super(WikiPage, self).__init__()
        self._source = source

    def _getSource(self):
        return self._source

    def _setSource(self, source):
        old_source = self._source 
        self._source = source
        notify(WikiPageEditEvent(self, old_source))

    # See zwiki.interfaces.IWikiPage
    source = property(_getSource, _setSource)

    # See zwiki.interfaces.IWikiPage
    type = u'zope.source.rest'


class WikiPageHierarchyAdapter(object):
    __doc__ = IWikiPageHierarchy.__doc__

    implements(IWikiPageHierarchy)
    __used_for__ = IWikiPage

    def __init__(self, context):
        self.context = context
        self._annotations = IAnnotations(context)
        if not self._annotations.get(HierarchyKey):
            self._annotations[HierarchyKey] = ()

    def reparent(self, parents):
        "See zwiki.interfaces.IWikiPageHierarchy"
        self.setParents(parents)

    def setParents(self, parents):
        res = []
        for p in parents:
            if p != zapi.name(self.context):
                #don't store myself as a parent
                res.append(p)
        self._annotations[HierarchyKey] = tuple(res)

    def getParents(self):
        return self._annotations[HierarchyKey]

    parents = property(getParents, setParents)

    def path(self):
        "See zwiki.interfaces.IWikiPageHierarchy"
        if not self.getParents():
            return [self.context]
        wiki = zapi.getParent(self.context)
        name = self.getParents()[0]
        hier = IWikiPageHierarchy(wiki[name])
        return hier.path() + [self.context]

    def findChildren(self, recursive=True):
        "See zwiki.interfaces.IWikiPageHierarchy"
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



# Adapters for file-system style access

class Directory(object):
    r"""Adapter to provide a file-system rendition of wiki pages

    Usage:

      >>> page = WikiPage()
      >>> page.source = 'This is the FrontPage.'

      >>> from comment import Comment
      >>> comment = Comment()
      >>> comment.title = u'C1'
      >>> comment.source = u'Comment 1'
      >>> page[u'comment1'] = comment

      >>> dir = Directory(page)
      >>> IReadDirectory.providedBy(dir)
      True
      >>> IWriteDirectory.providedBy(dir)
      True

      >>> dir.keys()
      [u'comment1', u'content.txt']
      >>> len(dir)
      2

      >>> content = dir.get('content.txt')
      >>> content.__class__ == ContentFile
      True
      >>> comment = dir.get('comment1')
      >>> comment.__class__ == Comment
      True

      >>> del dir[u'content.txt']
      >>> dir.keys()
      [u'comment1', u'content.txt']
      >>> del dir[u'comment1']
      >>> dir.keys()
      [u'content.txt']
    """

    content_file = u'content.txt'
    implements(IReadDirectory, IWriteDirectory)
    __used_for__ = IWikiPage

    def __init__(self, context):
        self.context = context

    def keys(self):
        return list(self.context.keys()) + [self.content_file]

    def get(self, key, default=None):
        if key == self.content_file: 
            return ContentFile(self.context)
        return self.context.get(key, default)

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, key):
        v = self.get(key, self)
        if v is self:
            raise KeyError, key
        return v

    def values(self):
        return map(self.get, self.keys())

    def __len__(self):
        return len(self.context)+1

    def items(self):
        get = self.get
        return [(key, get(key)) for key in self.keys()]

    def __contains__(self, key):
        return self.get(key) is not None

    def __setitem__(self, name, object):
        if name == self.content_file:
            pass
        else:
            self.context.__setitem__(name, object)

    def __delitem__(self, name):
        if name == self.content_file:
            pass
        else:
            self.context.__delitem__(name)


class ContentFile:
    r"""Adapter for letting a Wiki Page look like a regular file.

    Usage:

      >>> page = WikiPage()
      >>> page.source = 'This is the FrontPage.'

      >>> file = ContentFile(page)
      >>> IReadFile.providedBy(file)
      True
      >>> IWriteFile.providedBy(file)
      True

      >>> file.read()
      u'Source Type: zope.source.rest\n\nThis is the FrontPage.'
      >>> file.size()
      53

      >>> file.write('Type: zope.source.stx\n\nThis is the FrontPage 2.')
      >>> file.context.type
      u'zope.source.stx'
      >>> file.context.source
      u'This is the FrontPage 2.'

    Sometimes the user might not have entered a valid type; let's ignore the
    assignment then.

      >>> file.write('Type: zope.source.foo\n\nThis is the FrontPage 3.')
      >>> file.context.type
      u'zope.source.stx'
      >>> file.context.source
      u'This is the FrontPage 3.'

    Or the type was ommitted altogether.

      >>> file.write('This is the FrontPage 4.')
      >>> file.context.type
      u'zope.source.stx'
      >>> file.context.source
      u'This is the FrontPage 4.'
    """

    implements(IReadFile, IWriteFile)
    __used_for__ = IWikiPage

    def __init__(self, context):
        self.context = context

    def read(self):
        """See zope.app.filerepresentation.interfaces.IReadFile"""
        text = u'Source Type: %s\n\n' %self.context.type
        text += self.context.source 
        return text

    def size(self):
        """See zope.app.filerepresentation.interfaces.IReadFile"""
        return len(self.read())

    def write(self, data):
        """See zope.app.filerepresentation.interfaces.IWriteFile"""
        if data.startswith('Type: '):
            type, data = data.split('\n\n', 1)
            type = type[6:]
            vocab = getVocabularyRegistry().get(self.context, 'SourceTypes')
            if type in [term.value for term in vocab]:
                self.context.type = unicode(type)
                
        self.context.source = unicode(data)


# An edit event containing the source before the update

class WikiPageEditEvent(ObjectEvent):
    implements(IWikiPageEditEvent)

    oldSource = u''

    def __init__(self, object, old_source):
        super(WikiPageEditEvent, self).__init__(object)
        self.oldSource = old_source

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
        "See zwiki.interfaces.IMailSubscriptions"
        return self._annotations[SubscriberKey]
        
    def addSubscriptions(self, emails):
        "See zwiki.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            if email not in subscribers:
                subscribers.append(email.strip())
        self._annotations[SubscriberKey] = tuple(subscribers)
                
    def removeSubscriptions(self, emails):
        "See zwiki.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            if email in subscribers:
                subscribers.remove(email)
        self._annotations[SubscriberKey] = tuple(subscribers)
                


class WikiMailer:
    """Class to handle all outgoing mail."""

    def __call__(self, event):
        if IWikiPage.providedBy(event.object):
            if IObjectAddedEvent.providedBy(event):
                self.handleAdded(event.object)

            elif IWikiPageEditEvent.providedBy(event):
                self.handleModified(event)

            elif IObjectRemovedEvent.providedBy(event):
                self.handleRemoved(event.object)

    def handleAdded(self, object):
        subject = 'Added: '+zapi.name(object)
        emails = self.getAllSubscribers(object)
        body = object.source
        self.mail(emails, subject, body)        

    def handleModified(self, event):
        object = event.object
        if zapi.name(object) is not None:
            subject = 'Modified: '+zapi.name(object)
            emails = self.getAllSubscribers(object)
            body = textdiff(event.oldSource, object.source)
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
