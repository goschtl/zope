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
"""ZWiki Tests

$Id$
"""
import unittest

from zope.event import subscribers
from zope.interface import classImplements, implements 
from zope.app.testing import ztapi
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.mail.interfaces import IMailDelivery

from zwiki.interfaces import IWikiPage, IWiki, IMailSubscriptions
from zwiki.interfaces import IWikiPageEditEvent
from zwiki.wikipage import WikiPage
from zwiki.wikipage import MailSubscriptions, WikiMailer, mailer
from zwiki.wiki import Wiki

SubscriberKey = 'http://www.zope.org/zwiki#1.0/MailSubscriptions/emails'

mail_result=[]

class MailSubscriptionTest(PlacelessSetup):

    def getTestObject(self):
        raise NotImplementedError

    def setUp(self):
        PlacelessSetup.setUp(self)
        # This needs to be done, since the IAttributeAnnotable interface
        # is usually set in the ZCML
        classImplements(WikiPage, IAttributeAnnotatable)
        classImplements(Wiki, IAttributeAnnotatable)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                       AttributeAnnotations)
        self._sub = MailSubscriptions(self.getTestObject())

    def test_Interface(self):
        self.failUnless(IMailSubscriptions.providedBy(self._sub))

    def test_getSubscriptions(self):
        self.assertEqual((), self._sub.getSubscriptions())
        self._sub.context.__annotations__[SubscriberKey] = ('foo@bar.com',)
        self.assertEqual(('foo@bar.com',), self._sub.getSubscriptions())

    def test_addSubscriptions(self):
        self._sub.addSubscriptions(('foo@bar.com',))
        self.assertEqual(('foo@bar.com',),
                         self._sub.context.__annotations__[SubscriberKey])
        self._sub.addSubscriptions(('blah@bar.com',))
        self.assertEqual(('foo@bar.com', 'blah@bar.com'),
                         self._sub.context.__annotations__[SubscriberKey])
        self._sub.addSubscriptions(('blah@bar.com',))
        self.assertEqual(('foo@bar.com', 'blah@bar.com'),
                         self._sub.context.__annotations__[SubscriberKey])
        self._sub.addSubscriptions(('blah@bar.com', 'doh@bar.com'))
        self.assertEqual(('foo@bar.com', 'blah@bar.com', 'doh@bar.com'),
                         self._sub.context.__annotations__[SubscriberKey])

    def test_removeSubscriptions(self):
        self._sub.context.__annotations__[SubscriberKey] = (
            'foo@bar.com', 'blah@bar.com', 'doh@bar.com')
        self._sub.removeSubscriptions(('foo@bar.com',))
        self.assertEqual(('blah@bar.com', 'doh@bar.com'),
                         self._sub.context.__annotations__[SubscriberKey])
        self._sub.removeSubscriptions(('foo@bar.com',))
        self.assertEqual(('blah@bar.com', 'doh@bar.com'),
                         self._sub.context.__annotations__[SubscriberKey])
        self._sub.removeSubscriptions(('blah@bar.com', 'doh@bar.com'))
        self.assertEqual((),
                         self._sub.context.__annotations__[SubscriberKey])
        

class WikiPageMailSubscriptionTest(MailSubscriptionTest, unittest.TestCase):

    def getTestObject(self):
        return WikiPage()

class WikiMailSubscriptionTest(MailSubscriptionTest, unittest.TestCase):

    def getTestObject(self):
        return Wiki()



class MailDeliveryStub(object):
  
    implements(IMailDelivery)

    def send(self, fromaddr, toaddrs, message):
        mail_result.append((fromaddr, toaddrs, message))


class WikiMailerTest(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        # This needs to be done, since the IAttributeAnnotable interface
        # is usually set in the ZCML
        classImplements(WikiPage, IAttributeAnnotatable)
        classImplements(Wiki, IAttributeAnnotatable)
        ztapi.provideAdapter(IWikiPage, IMailSubscriptions,
                       MailSubscriptions)
        ztapi.provideAdapter(IWiki, IMailSubscriptions,
                       MailSubscriptions)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                       AttributeAnnotations)
        delivery = MailDeliveryStub()
        ztapi.provideUtility(IMailDelivery, delivery,
                             name='wiki-delivery')
        subscribers.append(mailer)

    def tearDown(self):
        mail_result=[]
        subscribers.remove(mailer)

    def test_getAllSubscribers(self):
        wiki = Wiki()
        wiki_sub = MailSubscriptions(wiki)
        wiki_sub.context.__annotations__[SubscriberKey] = ('foo@bar.com',)
        page = WikiPage()
        page_sub = MailSubscriptions(page)
        page_sub.context.__annotations__[SubscriberKey] = ('blah@bar.com',)
        wiki['page1'] = page
        # get the item again so it'll be wrapped in ContainedProxy
        page = wiki['page1']
        self.assertEqual(('blah@bar.com', 'foo@bar.com'),
                         mailer.getAllSubscribers(page))

    def test_notify(self):
        wiki = Wiki()
        wiki_sub = MailSubscriptions(wiki)
        wiki_sub.context.__annotations__[SubscriberKey] = ('foo@bar.com',)
        page = WikiPage()
        page_sub = MailSubscriptions(page)
        page_sub.context.__annotations__[SubscriberKey] = ('blah@bar.com',)
        wiki['page1'] = page
        page.source = 'Hello World!'
        self.assertEqual('wiki@zope3.org', 
                         mail_result[-1][0])
        self.assertEqual(('blah@bar.com', 'foo@bar.com'), mail_result[-1][1])
        self.assertEqual(
            u'''Subject: Modified: page1\n\n\n\n??changed:\n'''
            u'''-\n'''
            u'''+Hello World!\n''',
            mail_result[-1][2])
        page.source = 'Hello New World!'
        self.assertEqual('wiki@zope3.org', 
                         mail_result[-1][0])
        self.assertEqual(('blah@bar.com', 'foo@bar.com'), mail_result[-1][1])
        self.assertEqual(
            u'''Subject: Modified: page1\n\n\n\n??changed:\n'''
            u'''-Hello World!\n'''
            u'''+Hello New World!\n''',
            mail_result[-1][2])
  


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WikiMailSubscriptionTest),
        unittest.makeSuite(WikiPageMailSubscriptionTest),
        unittest.makeSuite(WikiMailerTest),
        ))

if __name__ == '__main__':
    unittest.main()
