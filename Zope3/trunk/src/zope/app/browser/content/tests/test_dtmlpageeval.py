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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""DTML Page Evaluation Tests

$Id: test_dtmlpageeval.py,v 1.7 2003/09/21 17:30:33 jim Exp $
"""
from unittest import TestCase, main, makeSuite
from zope.app.browser.content.dtmlpageeval import DTMLPageEval
from zope.app.container.contained import contained
class Test(TestCase):

    def test(self):

        class Template:
            def render(self, request, **kw):
                self.called = request, kw
                request.response.setHeader('content-type', self.content_type)
                return 42

            content_type = 'text/x-test'

        class Folder: name='zope'
        folder = Folder()

        class Request(object):

            def _getResponse(self):
                return self

            response = property(_getResponse)

            def setHeader(self, name, value):
                setattr(self, name, value)

        request = Request()
        template = contained(Template(), folder, 'foo')

        view = DTMLPageEval()
        # Do manually, since directive adds BrowserView as base class
        view.context = template
        view.request = request
        self.assertEqual(view.index(request), 42)
        self.assertEqual(template.called, (request, {}))
        self.assertEqual(getattr(request, 'content-type'), 'text/x-test')

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
