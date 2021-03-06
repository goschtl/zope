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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
$Id$
"""

from unittest import TestCase, main, makeSuite
from zope.testing.cleanup import CleanUp # Base class w registry cleanup
from zope.app.container.contained import contained
from zope.app.zptpage.browser.zptpage import ZPTPageEval

class Test(CleanUp, TestCase):

    def testTemplateRendering(self):

        class Template:
            def render(self, request, **kw):
                self.called = request, kw
                return 42

            content_type = 'text/x-test'

        class Folder:
            name='zope'
        folder = Folder()

        class Request(object):
            def _getResponse(self):
                return self

            response = property(_getResponse)

            def setHeader(self, name, value):
                setattr(self, name, value)

        request = Request()
        template = contained(Template(), folder)

        view = ZPTPageEval()
        # Do manually, since directive adds BrowserView as base class
        view.context = template
        view.request = request
        self.assertEqual(view.index(), 42)
        self.assertEqual(template.called, (request, {}))
        self.assertEqual(getattr(request, 'content-type'), 'text/x-test')

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
