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
"""Message Implementation

An implementation of the Message using BTreeContainers as base.

$Id: message.py,v 1.1 2003/06/07 11:24:48 srichter Exp $
"""
from zope.i18n import MessageIDFactory
from zope.interface import implements

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotations
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.event.interfaces import IObjectModifiedEvent
from zope.app.mail.interfaces import IMailDelivery
from zope.app.size.interfaces import ISized

from book.messageboard.interfaces import IMessage
from book.messageboard.interfaces import IMessageContained, IMessageContainer
from book.messageboard.interfaces import IMailSubscriptions
from book.messageboard.interfaces import IPlainText

_ = MessageIDFactory('messageboard')


class Message(BTreeContainer):
    """A simple implementation of a message.

    Make sure that the ``Message`` implements the ``IMessage`` interface:

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IMessage, Message)
    True

    Here is an example of changing the title and description of the message:

    >>> message = Message()
    >>> message.title
    u''
    >>> message.body
    u''
    >>> message.title = u'Message Title'
    >>> message.body = u'Message Body'
    >>> message.title
    u'Message Title'
    >>> message.body
    u'Message Body'
    """
    implements(IMessage, IMessageContained, IMessageContainer)

    # See book.messageboard.interfaces.IMessage
    title = u''

    # See book.messageboard.interfaces.IMessage
    body = u''

  
class MessageSized(object):

    implements(ISized)
    __used_for__ = IMessage

    def __init__(self, message):
        self._message = message

    def sizeForSorting(self):
        """See ISized

        Create the adapter first.

        >>> size = MessageSized(Message())

        Here are some examples of the expected output.

        >>> size.sizeForSorting()
        ('item', 0)
        >>> size._message['msg1'] = Message()
        >>> size.sizeForSorting()
        ('item', 1)
        >>> size._message['att1'] = object()
        >>> size.sizeForSorting()
        ('item', 2)
        """
        return ('item', len(self._message))

    def sizeForDisplay(self):
        """See ISized

        Creater the adapter first.

        >>> size = MessageSized(Message())

        Here are some examples of the expected output.

        >>> str = size.sizeForDisplay()
        >>> str
        u'${messages} replies, ${attachments} attachments'
        >>> 'msgs: %(messages)s, atts: %(attachments)s' %str.mapping
        'msgs: 0, atts: 0'
        >>> size._message['msg1'] = Message()
        >>> str = size.sizeForDisplay()
        >>> str
        u'1 reply, ${attachments} attachments'
        >>> 'msgs: %(messages)s, atts: %(attachments)s' %str.mapping
        'msgs: 1, atts: 0'
        >>> size._message['att1'] = object()
        >>> str = size.sizeForDisplay()
        >>> str
        u'1 reply, 1 attachment'
        >>> 'msgs: %(messages)s, atts: %(attachments)s' %str.mapping
        'msgs: 1, atts: 1'
        >>> size._message['msg2'] =  Message()
        >>> str = size.sizeForDisplay()
        >>> str
        u'${messages} replies, 1 attachment'
        >>> 'msgs: %(messages)s, atts: %(attachments)s' %str.mapping
        'msgs: 2, atts: 1'
        >>> size._message['att2'] = object()
        >>> str = size.sizeForDisplay()
        >>> str
        u'${messages} replies, ${attachments} attachments'
        >>> 'msgs: %(messages)s, atts: %(attachments)s' %str.mapping
        'msgs: 2, atts: 2'
        """
        messages = 0
        for obj in self._message.values():
            if IMessage.providedBy(obj):
                messages += 1

        attachments = len(self._message)-messages

        if messages == 1 and attachments == 1: 
            size = _('1 reply, 1 attachment')
        elif messages == 1 and attachments != 1:
            size = _('1 reply, ${attachments} attachments')
        elif messages != 1 and attachments == 1:
            size = _('${messages} replies, 1 attachment')
        else: 
            size = _('${messages} replies, ${attachments} attachments')
  
        size.mapping = {'messages': `messages`, 'attachments': `attachments`}

        return size


SubscriberKey='http://www.zope.org/messageboard#1.0/MailSubscriptions/emails'


class MailSubscriptions:
    """Message Mail Subscriptions.

    Verify the interface implementation

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IMailSubscriptions, MailSubscriptions)
    True

    Create asubscription instance of a message

    >>> msg = Message()
    >>> sub = MailSubscriptions(msg)

    Verify that we have initially no subscriptions and then add some.

    >>> sub.getSubscriptions()
    ()
    >>> sub.addSubscriptions(('foo@bar.com',))
    >>> sub.getSubscriptions()
    ('foo@bar.com',)
    >>> sub.addSubscriptions(('blah@bar.com',))
    >>> sub.getSubscriptions()
    ('foo@bar.com', 'blah@bar.com')
    >>> sub.addSubscriptions(('doh@bar.com',))
    >>> sub.getSubscriptions()
    ('foo@bar.com', 'blah@bar.com', 'doh@bar.com')

    Now let's also check that we can remove entries.

    >>> sub.removeSubscriptions(('foo@bar.com',))
    >>> sub.getSubscriptions()
    ('blah@bar.com', 'doh@bar.com')

    When we construct a new mail subscription adapter instance, the values
    should still be there.

    >>> sub1 = MailSubscriptions(msg)
    >>> sub1.getSubscriptions()
    ('blah@bar.com', 'doh@bar.com')
    """
    implements(IMailSubscriptions)
    __used_for__ = IMessage

    def __init__(self, context):
        self.context = self.__parent__ = context
        self._annotations = IAnnotations(context)
        if not self._annotations.get(SubscriberKey):
            self._annotations[SubscriberKey] = ()

    def getSubscriptions(self):
        "See book.messageboard.interfaces.IMailSubscriptions"
        return self._annotations[SubscriberKey]
        
    def addSubscriptions(self, emails):
        "See book.messageboard.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            if email not in subscribers:
                subscribers.append(email.strip())
        self._annotations[SubscriberKey] = tuple(subscribers)
                
    def removeSubscriptions(self, emails):
        "See book.messageboard.interfaces.IMailSubscriptions"
        subscribers = list(self._annotations[SubscriberKey])
        for email in emails:
            if email in subscribers:
                subscribers.remove(email)
        self._annotations[SubscriberKey] = tuple(subscribers)


class MessageMailer:
    """Class to handle all outgoing mail."""
  
    def __call__(self, event):
        r"""Called by the event system.

        Here is a demonstration on how the notification process and mail
        sending works.

        Before we can test this method, we have to create a mail delivery
        object for testing.

        >>> mail_result = [] 

        >>> from zope.interface import implements
        >>> from zope.app.mail.interfaces import IMailDelivery
        
        >>> class MailDeliveryStub(object):
        ...     implements(IMailDelivery)
        ... 
        ...     def send(self, fromaddr, toaddrs, message):
        ...         mail_result.append((fromaddr, toaddrs, message))

        >>> from zope.app.tests import ztapi
        >>> ztapi.provideUtility(IMailDelivery, MailDeliveryStub(),
        ...                      name='msgboard-delivery')

        Create a message.

        >>> from zope.interface import directlyProvides
        >>> from zope.app.traversing.interfaces import IContainmentRoot

        >>> msg = Message()
        >>> directlyProvides(msg, IContainmentRoot)
        >>> msg.__name__ = 'msg'
        >>> msg.__parent__ = None
        >>> msg.title = 'Hello'
        >>> msg.body = 'Hello World!'

        Add a subscription to message.

        >>> msg_sub = MailSubscriptions(msg)
        >>> msg_sub.context.__annotations__[SubscriberKey] = ('foo@bar.com',)

        Now, create an event and send it to the message mailer object.

        >>> from zope.app.event.objectevent import ObjectModifiedEvent
        >>> event = ObjectModifiedEvent(msg)
        >>> mailer(event)

        >>> from pprint import pprint
        >>> pprint(mail_result)
        [('mailer@messageboard.org',
          ('foo@bar.com',),
          'Subject: Modified: msg\n\n\nHello World!')]
        """
        if IMessage.providedBy(event.object):
            if IObjectAddedEvent.providedBy(event):
                self.handleAdded(event.object)
            elif IObjectModifiedEvent.providedBy(event):
                self.handleModified(event.object)
            elif IObjectRemovedEvent.providedBy(event):
                self.handleRemoved(event.object)
  
    def handleAdded(self, object):
        subject = 'Added: '+zapi.getName(object)
        emails = self.getAllSubscribers(object)
        body = object.body
        self.mail(emails, subject, body)        
  
    def handleModified(self, object):
        subject = 'Modified: '+zapi.getName(object)
        emails = self.getAllSubscribers(object)
        body = object.body
        self.mail(emails, subject, body)
  
    def handleRemoved(self, object):
        subject = 'Removed: '+zapi.getName(object)
        emails = self.getAllSubscribers(object)
        body = subject
        self.mail(emails, subject, body)
  
    def getAllSubscribers(self, object):
        """Retrieves all email subscribers.

        Here a small demonstration of retrieving all subscribers.

        >>> from zope.interface import directlyProvides
        >>> from zope.app.traversing.interfaces import IContainmentRoot

        Create a parent message as it would be located in the message
        board. Also add a subscriber to the message.

        >>> msg1 = Message()
        >>> directlyProvides(msg1, IContainmentRoot)
        >>> msg1.__name__ = 'msg1'
        >>> msg1.__parent__ = None
        >>> msg1_sub = MailSubscriptions(msg1)
        >>> msg1_sub.context.__annotations__[SubscriberKey] = ('foo@bar.com',)

        Create a reply to the first message and also give it a subscriber.
       
        >>> msg2 = Message()
        >>> msg2_sub = MailSubscriptions(msg2)
        >>> msg2_sub.context.__annotations__[SubscriberKey] = ('blah@bar.com',)
        >>> msg1['msg2'] = msg2

        When asking for all subscriptions of message 2, we should get the
        subscriber from message 1 as well.

        >>> mailer.getAllSubscribers(msg2)
        ('blah@bar.com', 'foo@bar.com')
        """
        emails = ()
        msg = object
        while IMessage.providedBy(msg):
            emails += tuple(IMailSubscriptions(msg).getSubscriptions())
            msg = zapi.getParent(msg)
        return emails
  
    def mail(self, toaddrs, subject, body):
        """Mail out the Message Board change message."""
        if not toaddrs:
            return
        msg = 'Subject: %s\n\n\n%s' %(subject, body)
        mail_utility = zapi.getUtility(IMailDelivery, 'msgboard-delivery')
        mail_utility.send('mailer@messageboard.org' , toaddrs, msg)
  
mailer = MessageMailer()


class PlainText:

    implements(IPlainText)

    def __init__(self, context):
        self.context = context

    def getText(self):
        return 'Title: %s\n\n%s' %(self.context.title, 
                                   self.context.body)

    def setText(self, text):
        if text.startswith('Title: '):
            title, text = text.split('\n', 1)
            self.context.title = title[7:]

        self.context.body = text.strip()
