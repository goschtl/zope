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
"""ZWiki Tests

$Id: test_wikimail.py,v 1.1 2003/12/16 10:05:56 nmurthy Exp $
"""
import unittest

from zope.interface import classImplements 
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.interfaces.annotation import IAnnotations, IAttributeAnnotatable
from zope.app.interfaces.event import ISubscriber
from zope.app.attributeannotations import AttributeAnnotations

from zope.products.zwiki.interfaces import IWikiPage, IWiki, IMailSubscriptions
from zope.products.zwiki.wikipage import WikiPage
from zope.products.zwiki.wikipage import MailSubscriptions, WikiMailer, mailer
from zope.products.zwiki.wiki import Wiki

SubscriberKey = 'http://www.zope.org/zwiki#1.0/MailSubscriptions/emails'


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
        self.failUnless(IMailSubscriptions.isImplementedBy(self._sub))

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


class WikiMailerTest(PlacefulSetup, unittest.TestCase):

    # Note: There are several other methods in this class, but they require
    #       mail to be sent out. One way to still write tests for these would
    #       be to implement a dummy smtplib.SMTP class...not now though. ;)

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

    def test_Interface(self):
        self.failUnless(ISubscriber.isImplementedBy(mailer))

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

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(WikiMailSubscriptionTest),
        unittest.makeSuite(WikiPageMailSubscriptionTest),
        unittest.makeSuite(WikiMailerTest),
        ))

if __name__ == '__main__':
    unittest.main()
