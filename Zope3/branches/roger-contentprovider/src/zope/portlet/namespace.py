##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Portlet namespace implementation

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component import getMultiAdapter
from zope.interface import implements

from zope.app.traversing.interfaces import ITraversable
from zope.app.traversing.interfaces import TraversalError
from zope.app.zapi import getPath

from zope.portlet.interfaces import IPortletManager



class portlet(object):
    """
    Placeless setup:

        >>> import zope.component
        >>> from zope.app.testing import placelesssetup, ztapi
        >>> from zope.app.testing import setup
        >>> placelesssetup.setUp()
        >>> setup.setUpTraversal()
        
    Setup a view for test the traversable ``++portlet++`` namesapce:

        >>> from zope.publisher.browser import TestRequest
        >>> from zope.app.publisher.browser import BrowserView
        >>> from zope.interface import Interface
      
        >>> class TestContext(object):
        ...     implements(Interface)

    Setup the view on the context:

        >>> testRequest = TestRequest()
        >>> testContext = TestContext()

    Setup a view:

        >>> from zope.portlet.interfaces import IPortlet
        >>> class MyView(BrowserView):
        ...     implements(IPortlet)
        ...
        >>> view = MyView(testContext, testRequest)

    Setup PortletManager::

        >>> from zope.portlet.interfaces import IPortletManager
        >>> class DummyPortletManager(object):
        ...     implements(IPortletManager)
        ...     def __init__(self, context, request, view):
        ...         pass

    Try to traverse ``++portlet++`` namespace on te view the view:

        >>> from zope.publisher.browser import IBrowserRequest
        >>> from zope.app.testing.ztapi import provideAdapter
        >>> provideAdapter(Interface, IPortletManager, DummyPortletManager, name='foo', with=(IBrowserRequest, IPortlet))

    Test setup:

        >>> Interface.providedBy(testContext)
        True
        >>> IBrowserRequest.providedBy(testRequest)
        True
        >>> IPortlet.providedBy(view)
        True

    Test namespace:

        >>> traverser = portlet(view, testRequest)
        >>> portletManager = traverser.traverse('foo', None)
        >>> IPortletManager.providedBy(portletManager)
        True

        >>> placelesssetup.tearDown()
    """

    implements(ITraversable)

    def __init__(self, context, request):
        self.context = context.context
        self.request = request
        self.view = context

    def traverse(self, name, ignored):
        """Get portlet manager or portlet."""

        objs = (self.context, self.request, self.view)
        return getMultiAdapter(objs, IPortletManager, name=name)
