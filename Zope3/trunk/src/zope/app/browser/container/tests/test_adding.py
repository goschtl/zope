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

$Id: test_adding.py,v 1.8 2003/08/16 00:42:42 srichter Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.app import zapi
from zope.app.browser.absoluteurl import AbsoluteURL
from zope.app.browser.container.adding import Adding
from zope.app.context import ContextWrapper
from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.container import IAdding, IContainer, IZopeContainer
from zope.app.interfaces.event import IObjectAddedEvent, IObjectModifiedEvent
from zope.app.interfaces.exceptions import UserError
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter
from zope.component.view import provideView
from zope.component.factory import provideFactory
from zope.component.interfaces import IFactory
from zope.component.exceptions import ComponentLookupError
from zope.context import getWrapperContainer, getWrapperData
from zope.context import \
     getWrapperContainer, getWrapperData, getInnerWrapperData
from zope.interface import implements, Interface
from zope.publisher.browser import TestRequest, BrowserView
from zope.publisher.interfaces.browser import IBrowserPresentation

class Root:
    implements(IContainmentRoot)

class Container(dict):

    implements(IZopeContainer)

    def setObject(self, name, obj):
        self[name] = obj
        return name


class CreationView(BrowserView):

    def action(self):
        return 'been there, done that'


class Factory:

    implements(IFactory)

    def getInterfaces(self):
        return ()

    def __call__(self):
        return 'some_content'


class AbsoluteURL(BrowserView):

    def __str__(self):
        if IContainmentRoot.isImplementedBy(self.context):
            return ''
        name = getInnerWrapperData(self.context)['name']
        url = str(zapi.getView(
            zapi.getParent(self.context), 'absolute_url', self.request))
        url += '/' + name
        return url


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def test(self):
        container = Container()
        # ensure container provides IZopeContainer
        container = ContextWrapper(container, None)
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
        self.assertEqual(result, o)
        self.assertEqual(getWrapperData(result)["name"], "foo")

    def testNoNameGiven(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        provideView(IAdding, "Thing", IBrowserPresentation, CreationView)

        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=')
        self.assertEqual(adding.contentName, '')

    def testAction(self):
        provideFactory('foo', Factory())
        container = Container()
        adding = Adding(container, TestRequest())
        adding.nextURL = lambda: '.'
        adding.namesAccepted = lambda: True

        # typical add - id is provided by user
        adding.action(type_name='foo', id='bar')
        self.assert_('bar' in container)

        # missing type_name
        self.assertRaises(UserError, adding.action, id='bar')

        # missing id
        self.assertRaises(UserError, adding.action, type_name='foo')

        # bad type_name
        self.assertRaises(ComponentLookupError, adding.action, 
            type_name='***', id='bar')

        # alternative add - id is provided internally instead of from user
        adding.namesAccepted = lambda: False
        adding.contentName = 'baz'
        adding.action(type_name='foo')
        self.assert_('baz' in container)

        # alternative add w/missing contentName
        adding.contentName = None
        self.assertRaises(ValueError, adding.action, type_name='foo')
        

    def test_action(self):
        container = Container()
        # ensure container provides IZopeContainer
        container = ContextWrapper(container, Root(), name="container")
        request = TestRequest()
        adding = Adding(container, request)
        adding = ContextWrapper(adding, container, name="+")
        provideView(IAdding, "Thing", IBrowserPresentation, CreationView)
        provideView(Interface, "absolute_url", IBrowserPresentation,
                    AbsoluteURL)
        self.assertRaises(UserError, adding.action, '', 'foo')
        self.assertRaises(UserError, adding.action, 'Unknown', '')
        adding.action('Thing', 'foo')
        self.assertEqual(adding.request.response._headers['location'],
                         '/container/+/Thing=foo')
        adding.action('Thing/screen1', 'foo')
        self.assertEqual(adding.request.response._headers['location'],
                         '/container/+/Thing/screen1=foo')


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
