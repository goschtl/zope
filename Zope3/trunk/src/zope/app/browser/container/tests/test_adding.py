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

$Id: test_adding.py,v 1.11 2003/09/21 17:30:25 jim Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.app import zapi
from zope.app.browser.absoluteurl import AbsoluteURL
from zope.app.browser.container.adding import Adding
from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.container import IAdding
from zope.app.interfaces.container import IObjectAddedEvent
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.exceptions import UserError
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.view import provideView
from zope.component.factory import provideFactory
from zope.component.interfaces import IFactory
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements, Interface, directlyProvides
from zope.publisher.browser import TestRequest, BrowserView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.container.contained import contained
import zope.security.checker
from zope.exceptions import ForbiddenAttribute
from zope.app.interfaces.container import IWriteContainer
from zope.app.interfaces.container import IContainerNamesContainer

class Root:
    implements(IContainmentRoot)

class Container(dict):
    implements(IWriteContainer)

class CreationView(BrowserView):

    def action(self):
        return 'been there, done that'


class Content:
    pass

class Factory:

    implements(IFactory)

    def getInterfaces(self):
        return ()

    def __call__(self):
        return Content()


class AbsoluteURL(BrowserView):

    def __str__(self):
        if IContainmentRoot.isImplementedBy(self.context):
            return ''
        name = self.context.__name__
        url = str(zapi.getView(
            zapi.getParent(self.context), 'absolute_url', self.request))
        url += '/' + name
        return url


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)

    def test(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        provideView(IAdding, "Thing", IBrowserPresentation, CreationView)
        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=foo')
        self.assertEqual(view.action(), 'been there, done that')
        self.assertEqual(adding.contentName, 'foo')

        o = object()
        result = adding.add(o)

        # Check the state of the container and result
        self.assertEqual(container["foo"], o)
        self.assertEqual(result, o)

    def testNoNameGiven(self):
        container = Container()
        request = TestRequest()
        adding = Adding(container, request)
        provideView(IAdding, "Thing", IBrowserPresentation, CreationView)

        self.assertEqual(adding.contentName, None)
        view = adding.publishTraverse(request, 'Thing=')
        self.assertEqual(adding.contentName, '')

    def testAction(self):
        # make a private factory
        provideFactory('fooprivate', Factory())

        factory = Factory()
        factory.__Security_checker__ = zope.security.checker.NamesChecker(
            ['__call__'])
        provideFactory('foo', factory)

        container = Container()
        adding = Adding(container, TestRequest())
        adding.nextURL = lambda: '.'
        adding.namesAccepted = lambda: True

        # we can't use a private factory:
        self.assertRaises(ForbiddenAttribute, 
                          adding.action, type_name='fooprivate', id='bar')

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
        # Note: Passing is None as object name might be okay, if the container
        #       is able to hand out ids itself. Let's not require a content
        #       name to be specified!
        # For the container, (or really, the chooser, to choose, we have to
        # marke the container as a ContainerNamesContainer
        directlyProvides(container, IContainerNamesContainer)
        adding.contentName = None
        adding.action(type_name='foo')
        self.assert_('Content' in container)
        

    def test_action(self):
        container = Container()
        container = contained(container, Root(), "container")
        request = TestRequest()
        adding = Adding(container, request)
        adding.__name__ = '+'
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
