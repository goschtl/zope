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

$Id: testAdding.py,v 1.5 2002/11/18 13:40:38 stevea Exp $
"""

from unittest import TestCase, main, makeSuite

from Zope.App.OFS.Container.Views.Browser.Adding import Adding
from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalViewService import provideView
from Zope.Proxy.ContextWrapper \
     import getWrapperObject, getWrapperContainer, getWrapperData
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.Event.tests.PlacelessSetup import getEvents
from Zope.Event.IObjectEvent import IObjectAddedEvent, IObjectModifiedEvent

class Container:
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



