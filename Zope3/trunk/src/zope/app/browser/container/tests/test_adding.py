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
"""Adding implementation tests

$Id: test_adding.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.component.adapter import provideAdapter
from zope.app.browser.container.adding import Adding
from zope.app.interfaces.container import IAdding
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.view import provideView
from zope.proxy.context \
     import getWrapperObject, getWrapperContainer, getWrapperData
from zope.publisher.browser import TestRequest
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.event import IObjectAddedEvent, IObjectModifiedEvent

from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.container import IContainer
from zope.app.container.zopecontainer import ZopeContainerAdapter



class Container:

    __implements__ = IContainer

    def __init__(self):
        self._data = {}

    def setObject(self, name, obj):
        self._data[name] = obj
        return name

    def __getitem__(self, name):
        return self._data[name]

class CreationView(BrowserView):

    def action(self):
        return 'been there, done that'

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)

    def test(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        provideView(IAdding, "Thing", IBrowserPresentation, CreationView)
        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=foo')
        self.assertEqual(view.action(), 'been there, done that')
        self.assertEqual(adding.contentName, 'foo')

        # Make sure we don't have any events yet:
        self.failIf(getEvents(IObjectModifiedEvent))
        self.failIf(getEvents(IObjectAddedEvent))

        o = Container() # any old instance will do
        result = adding.add(o)

        # Make sure the right events were generated:
        self.failUnless(
            getEvents(IObjectAddedEvent,
                      filter =
                      lambda event:
                      event.object == o)
            )
        self.failUnless(
            getEvents(IObjectModifiedEvent,
                      filter =
                      lambda event:
                      event.object == container)
            )

        # Check the state of the container and result
        self.assertEqual(container["foo"], o)
        self.assertEqual(getWrapperContainer(result), container)
        self.assertEqual(getWrapperObject(result), o)
        self.assertEqual(getWrapperData(result)["name"], "foo")

    def testNoNameGiven(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        provideView(IAdding, "Thing", IBrowserPresentation, CreationView)

        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=')
        self.assertEqual(adding.contentName, '')


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
