##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_editconfiguration.py,v 1.4 2003/06/05 12:41:54 stevea Exp $
"""
__metaclass__ = type

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.browser.services.configuration import EditConfiguration
from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.event import IObjectRemovedEvent
from zope.app.interfaces.services.configuration import Active
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component.adapter import provideAdapter
from zope.component.view import provideView
from zope.interface import Interface, implements
from zope.publisher.browser import BrowserView
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.context import ContextWrapper

class Container(dict):
    implements(IContainer, IContainmentRoot)

class I(Interface):
    pass

class C:
    implements(I)
    status = Active


class Test(PlacefulSetup, TestCase):

    def test_remove_objects(self):
        c1 = C()
        c2 = C()
        c7 = C()
        d = Container({'1': c1, '2': c2, '7': c7})
        d = ContextWrapper(d, None)
        view = EditConfiguration(d, TestRequest())
        view.remove_objects(['2', '7'])
        self.assertEqual(d, {'1': c1})

        self.failUnless(
            getEvents(IObjectRemovedEvent,
                      filter = lambda event: event.object == c2),
            )
        self.failUnless(
            getEvents(IObjectRemovedEvent,
                      filter = lambda event: event.object == c7)
            )
        self.failUnless(
            getEvents(IObjectModifiedEvent,
                      filter = lambda event: event.object == d)
            )

    def test_configInfo(self):

        class V(BrowserView):
            def setPrefix(self, p):
                self._prefix = p

        provideView(I, 'ItemEdit', IBrowserPresentation, V)

        c1 = C()
        c2 = C()
        c7 = C()
        d = Container({'1': c1, '2': c2, '7': c7})

        view = EditConfiguration(d, TestRequest())

        info = view.configInfo()
        self.assertEqual(len(info), 3)
        self.assertEqual(info[0]['name'], '1')
        self.assertEqual(info[1]['name'], '2')
        self.assertEqual(info[2]['name'], '7')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
