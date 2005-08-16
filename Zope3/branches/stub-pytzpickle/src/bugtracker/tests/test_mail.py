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
"""Bug Tracker Mail Subscription and Mailer Tests

$Id: test_mail.py,v 1.1 2003/07/24 18:08:38 srichter Exp $
"""
import unittest

from zope.component.tests.placelesssetup import PlacelessSetup
from zope.interface import classImplements, implements

from zope.app.testing import ztapi
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.traversing.interfaces import IPhysicallyLocatable

from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.location.interfaces import ILocation
from zope.app.location.traversing import LocationPhysicallyLocatable
from zope.app.mail.interfaces import IMailDelivery

from bugtracker.bug import Bug
from bugtracker.interfaces import IBug, IBugTracker, IMailSubscriptions
from bugtracker.mail import MailSubscriptions, SubscriberKey, Mailer
from bugtracker.tracker import BugTracker

mail_result = [] 

class MailDeliveryStub(object):
    implements(IMailDelivery)

    def send(self, fromaddr, toaddrs, message):
        mail_result.append((fromaddr, toaddrs, message))


class MailSubscriptionTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        # This needs to be done, since the IAttributeAnnotable interface
        # is usually set in the ZCML
        classImplements(Bug, IAttributeAnnotatable)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        self._sub = MailSubscriptions(Bug())

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


class MailerTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        # This needs to be done, since the IAttributeAnnotable interface
        # is usually set in the ZCML
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             LocationPhysicallyLocatable)
        classImplements(BugTracker, IAttributeAnnotatable)
        classImplements(Bug, IAttributeAnnotatable)
        ztapi.provideAdapter(IBugTracker, IMailSubscriptions, MailSubscriptions)
        ztapi.provideAdapter(IBug, IMailSubscriptions, MailSubscriptions)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        ztapi.provideAdapter(IAttributeAnnotatable, IWriteZopeDublinCore,
                             ZDCAnnotatableAdapter)
        ztapi.provideUtility(IMailDelivery, MailDeliveryStub(), 'bug-mailer')

    def test_getAllSubscribers(self):
        tracker = BugTracker()
        tracker.__parent__ = object()
        tracker.__name__ = 'tracker'
        tracker_sub = MailSubscriptions(tracker)
        tracker_sub.context.__annotations__[SubscriberKey] = ('foo@bar.com',)
        bug = Bug()
        bug_sub = MailSubscriptions(bug)
        bug_sub.context.__annotations__[SubscriberKey] = ('blah@bar.com',)
        tracker['1'] = bug
        self.assertEqual(('blah@bar.com', 'foo@bar.com'),
                         Mailer().getAllSubscribers(bug))

    def test_call(self):
        bug = Bug()
        bug.__parent__ = object()
        bug.__name__ = 'bug'
        bug.title = u'Hello'
        bug.description = u'Hello World!'
        bug_sub = MailSubscriptions(bug)
        bug_sub.context.__annotations__[SubscriberKey] = ('foo@bar.com',)
        event = ObjectModifiedEvent(bug)
        Mailer()(event)
        self.assertEqual('bugtracker@zope3.org', mail_result[0][0])
        self.assertEqual(('foo@bar.com', ), mail_result[0][1])
        self.assertEqual('Subject: Modified: Hello (bug)\n\n\nHello World!',
                         mail_result[0][2])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MailSubscriptionTest),
        unittest.makeSuite(MailerTest),
        ))

if __name__ == '__main__':
    unittest.main()
