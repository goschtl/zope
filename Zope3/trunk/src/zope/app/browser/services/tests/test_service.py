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
"""Unit tests for service adding and configuration views.

$Id: test_service.py,v 1.2 2003/04/30 23:37:57 faassen Exp $
"""

import unittest
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.component.view import provideView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.tests.placelesssetup import PlacelessSetup

class IFoo(Interface):
    pass

class Foo:
    __implements__ = IFoo
    def __init__(self, url='some_url'):
        self.url = url

class TestComponentAdding(PlacelessSetup, unittest.TestCase):

    def test_nextURL(self):
        from zope.app.browser.services.service import ComponentAdding

        class AU:
            def __init__(self, context, request):
                self.context = context
            def __str__(self):
                return self.context.url
            __call__ = __str__
        provideView(IFoo, 'absolute_url', IBrowserPresentation, AU)
        provideView(IFoo, 'addConfiguration.html', IBrowserPresentation, AU)

        context = Foo('foo_url')
        request = TestRequest()
        view = ComponentAdding(context, request)
        view.added_object = None
        self.assertEquals(view.nextURL(), 'foo_url/@@contents.html')

        view.added_object = Foo('bar_url')
        self.assertEquals(view.nextURL(), 'bar_url/@@addConfiguration.html')


# XXX: add tests for other methods and classes


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestComponentAdding))
    return suite


if __name__ == '__main__':
    unittest.main()
