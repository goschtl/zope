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
"""Unit tests for service adding and registration views.

$Id: test_service.py,v 1.3 2003/09/24 20:43:10 fdrake Exp $
"""

import unittest
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.component.view import provideView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.tests.placelesssetup import PlacelessSetup, setUp, tearDown
from zope.testing.doctestunit import DocTestSuite

class IFoo(Interface):
    pass

class Foo:
    implements(IFoo)
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
        provideView(IFoo, 'registration.html', IBrowserPresentation, AU)

        context = Foo('foo_url')
        request = TestRequest()
        view = ComponentAdding(context, request)
        view.added_object = None
        self.assertEquals(view.nextURL(), 'foo_url/@@contents.html')

        view.added_object = Foo('bar_url')
        self.assertEquals(view.nextURL(), 'bar_url/@@registration.html')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestComponentAdding))
    suite.addTest(DocTestSuite('zope.app.browser.services.service',
                               setUp=setUp, tearDown=tearDown))
    return suite


if __name__ == '__main__':
    unittest.main()
